"""Independent consistency checks against the untouched chemistry database."""
import collections
import json
import math
from pathlib import Path
import re
import sqlite3

PROJECT = Path(__file__).resolve().parents[1]
data = json.loads((PROJECT / 'data/chemistry.json').read_text())
samples = {s['id']: s for s in data['samples']}
analytes = {a['id']: a for a in data['analytes']}
sites = {s['id']: s for s in data['sites']}
assert len(samples) == len(data['samples']), 'Duplicate sample identifier'
assert len(analytes) == len(data['analytes']), 'Duplicate analytical channel'
assert len(sites) == len(data['sites']), 'Duplicate site identity'
assert all(s['siteId'] in sites for s in samples.values()), 'Broken site reference'
assert all(not s.get('date') or s['date'] <= s['analysisDate'] for s in samples.values()), 'Collection after analysis'
assert all(not re.search(r'(?i)\b(?:CCB\d*|QC\d*|NIST|blank|check)\b', s['label']) for s in samples.values()), 'Control in environmental data'

db = sqlite3.connect(PROJECT.parent / 'outputs/water_chemistry_qaqc_database_20260817/water_chemistry_qaqc_database.sqlite')
source = {}
for key, channel, value, status in db.execute('select sample_key,channel,concentration_ppb,recommended_use from results'):
    source[(key, re.sub('[^a-z0-9]', '', channel.lower()))] = (value, status)
compared = 0
seen = set()
fields = data['resultFields']
decoded = []
for row in data['results']:
    result = dict(zip(fields, row))
    decoded.append(result)
    sid, aid, value = result['sampleId'], result['analyteId'], result['value']
    assert sid in samples and aid in analytes, 'Broken analytical reference'
    assert value is None or isinstance(value, (int, float)) and math.isfinite(value), 'Invalid numeric result'
    assert (sid, aid) not in seen, 'Duplicate sample and channel'
    seen.add((sid, aid))
    key = samples[sid].get('databaseSampleKey')
    if key:
        expected_value, expected_status = source[(key, aid)]
        assert value == expected_value, (sid, aid, value, expected_value)
        assert result['status'] == expected_status, (sid, aid, 'QA state changed')
        compared += 1

# A source-workbook spot check from the separately recovered January run.
recovered = next(r for r in decoded if r['sampleId'] == 'r05-vy1' and r['analyteId'] == '77ling')
assert recovered['value'] == 5.736
assert samples['r05-vy1']['date'] == '2024-11-15'
assert samples['r05-vy1']['siteId'] == 'rcn-bath'
assert any(r['value'] is None and r.get('qualifier') == 'censored' for r in decoded)

counts = data['meta']['counts']
for name in ['samples', 'analytes', 'sites', 'results']:
    assert counts[name] == len(data[name]), ('Incorrect count', name)

summary = {'samples': len(samples), 'results': len(decoded), 'source_values_and_QA_compared': compared,
           'censored_or_missing': sum(r['value'] is None for r in decoded)}
geo_path = PROJECT / 'data/geography.json'
if geo_path.exists():
    geo = json.loads(geo_path.read_text())
    mapped = [s for s in geo.get('sites', []) if s.get('lat') is not None and s.get('lon') is not None]
    assert all(25 < s['lat'] < 37 and -107 < s['lon'] < -93 for s in mapped), 'Coordinate outside Texas'
    summary['mapped_site_matches'] = sum(s['id'] in sites for s in mapped)
print(json.dumps(summary, indent=2))
