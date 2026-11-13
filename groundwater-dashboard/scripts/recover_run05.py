"""Recover January 2025 environmental samples from source workbook columns.

The earlier normalized database read the warning column as the sample name.
This extraction preserves the final dilution-corrected occurrence, explicit
reference-sheet collection dates, censored text, and provisional QC status.
The original workbook is read only.
"""
import json
import math
import re
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'Cations/5. Mirasol Cation Results 1.23.2025.xlsx'
workbook = openpyxl.load_workbook(ROOT / SOURCE, data_only=True)
sheet = workbook['Yale 012325 results']
references = {str(row[0]): row[1:] for row in workbook['Sample # refrence'].values if row[0]}
site_ids = {
    'VY1': 'rcn-bath', 'VY2': 'rcn-w3', 'VY3': 'rcn-w1',
    'VY4': 'rcn-cs1', 'VY5': 'rcn-cs2', 'VY6': 'ps',
    'VY7': 'ec-cp', 'VY8': 'ec-cs', 'VY9': 'ec-head',
    'VY10': 'ec-s1', 'VY11': 'ec-s2', 'VY12': 'ped-ham',
    'VY13': 'ec-head', 'VY15': 'well-5748913',
}
analytes = []
for col in range(10, 59):
    header = sheet.cell(2, col).value
    match = re.fullmatch(r'\s*(\d+)\s*->\s*(\d+)\s+([A-Z][a-z]?)\s*\[\s*(.*?)\s*\]\s*', header)
    assert match, (col, header)
    mass_from, mass_to, element, gas = match.groups()
    gas = 'NG' if gas == 'No Gas' else gas
    channel = f'{mass_from}->{mass_to}{element}[{gas}]'
    aid = re.sub('[^a-z0-9]', '', channel.lower())
    analytes.append({'id': aid, 'label': f'{element} · {channel}', 'element': element, 'unit': 'µg/L', 'channel': channel})

last_rows = {sheet.cell(row, 8).value: row for row in range(89, 105)}
samples, results = [], []
for label, row in last_rows.items():
    if label not in site_ids:
        continue
    reference_label, collection_date = references[label]
    sid = f'r05-{label.lower()}'
    samples.append({
        'id': sid, 'siteId': site_ids[label], 'label': str(reference_label),
        'date': collection_date.date().isoformat(), 'dateBasis': 'workbook reference sheet',
        'analysisDate': '2025-01-23', 'filtration': 'unknown',
        'isReplicate': label == 'VY13', 'sourceFile': SOURCE,
        'sourceSheet': sheet.title, 'sourceRow': row,
        'originalSampleId': label,
        'note': 'Final dilution-corrected occurrence. Run QC requires review; prior database sample-name parsing was incorrect.',
    })
    for col, analyte in enumerate(analytes, 10):
        raw = sheet.cell(row, col).value
        value = raw if isinstance(raw, (int, float)) and math.isfinite(raw) else None
        result = {'sampleId': sid, 'analyteId': analyte['id'], 'value': value,
                  'status': 'REVIEW', 'channel': analyte['channel'], 'qrsd': None,
                  'blankFlag': 'NOT_REVIEWED', 'detectionFlag': 'NO_MDLB'}
        if value is None:
            result.update(reportedValue=str(raw) if raw is not None else '',
                          qualifier='censored' if isinstance(raw, str) and raw.startswith('<') else 'unavailable')
        results.append(result)

payload = {'samples': samples, 'analytes': analytes, 'results': results,
           'notes': ['Recovered 14 environmental sample records from original workbook; VY14 blank excluded. Final VY15 measurement at row 104 retained over row 103 repeat. Censored strings are preserved with null numeric values, never replaced by zero.']}
target = ROOT / 'groundwater-dashboard/data/run05-recovery.json'
target.write_text(json.dumps(payload, separators=(',', ':'), ensure_ascii=False))
print(json.dumps({'samples': len(samples), 'channels': len(analytes), 'results': len(results),
                  'censoredOrUnavailable': sum(r['value'] is None for r in results)}))
