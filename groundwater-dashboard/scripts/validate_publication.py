"""Check the thesis publication gate independently of browser display logic."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/chemistry.json').read_text())
assert d['meta']['publicationBasis']=='thesis-reported-results-only'
fields=d['resultFields']
rows=[dict(zip(fields,r)) if isinstance(r,list) else r for r in d['results']]
assert all(r['status']=='THESIS_REPORTED' for r in rows), 'Working laboratory record in publication'
assert len({a['element'] for a in d['analytes']})==len(d['analytes']), 'Repeated element in public selector'
if d['meta']['publicationStatus']!='ready':
 assert rows==[] and d['samples']==[], 'Unverified measurements published while final source is pending'
 assert 'awaiting' in d['meta']['publicationStatus']
app=(ROOT/'app.js').read_text()
assert "publicationBasis!=='thesis-reported-results-only'" in app
assert "r.status==='THESIS_REPORTED'" in app
assert "quality:'THESIS_REPORTED'" in app
assert 'chemistry-laboratory-working' not in app
html=(ROOT/'index.html').read_text()
assert 'value="all">All reported results' not in html
assert 'value="REVIEW"' not in html and 'value="USE"' not in html
print(json.dumps({'publicationStatus':d['meta']['publicationStatus'],'publishedConcentrations':len(rows),'mappedContextSites':len(d['sites']),'oneSelectorEntryPerElement':True},indent=2))
