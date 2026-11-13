"""Prepare a fail-closed publication dataset until thesis final data are supplied.

Never promotes laboratory USE flags to thesis approval. Original research
workbooks and the normalized laboratory database are read only.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'data/chemistry.json'
current = json.loads(source.read_text())
archive = ROOT / 'data/chemistry-laboratory-working.json'
if current.get('results') and not archive.exists():
    archive.write_text(source.read_text())
geo = json.loads((ROOT / 'data/geography.json').read_text())
meta = {
    'title': 'Vivian Yale thesis water chemistry',
    'generatedAt': '2026-11-13',
    'publicationBasis': 'thesis-reported-results-only',
    'publicationStatus': 'awaiting-final-thesis-data',
    'notes': [
        'The published dashboard includes no raw laboratory concentrations.',
        'The final sample-level table used for the thesis figures has not been identified in the supplied files.',
        'Automated USE, REVIEW and EXCLUDE_PENDING_REVIEW flags from the separate working database are not thesis approval.',
        'Sites and the approximate divide remain visible as geographic context; numerical values and downloads are withheld pending the final thesis data table.'
    ],
    'counts': {'sites': len(geo['sites']), 'samples': 0, 'results': 0, 'analytes': 0},
    'qa': 'Only results traceable to the final thesis reporting table are eligible. No working-database flag is an eligibility substitute.'
}
names = {'Sr': 'Strontium', 'Ca': 'Calcium', 'Mg': 'Magnesium', 'Na': 'Sodium', 'K': 'Potassium'}
payload = {
    'meta': meta,
    'resultFields': ['sampleId', 'analyteId', 'value', 'status', 'qrsd', 'blankFlag', 'detectionFlag', 'reportedValue', 'qualifier'],
    'analytes': [{'id': element, 'element': element, 'label': label, 'unit': 'mg/L', 'channel': 'Thesis-selected reported result'} for element, label in names.items()],
    'sites': [{'id': s['id'], 'label': s['label'], 'type': s.get('type', 'Water sampling site')} for s in geo['sites']],
    'samples': [],
    'results': []
}
source.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
print('Published chemistry dataset contains zero unverified concentrations; geographic context retained.')
