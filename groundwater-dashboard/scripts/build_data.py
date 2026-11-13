"""Reproduce the laboratory WORKING export; this is not the thesis publication dataset.

Uses the normalized SQLite concentrations and explicitly curated workbook
reference joins. Run from this file's location with bundled Python/openpyxl.
"""
from pathlib import Path
import collections
import datetime as dt
import hashlib
import json
import math
import re
import sqlite3
import openpyxl

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
DB = ROOT / 'outputs/water_chemistry_qaqc_database_20260817/water_chemistry_qaqc_database.sqlite'
FIELDS = ['sampleId', 'analyteId', 'value', 'status', 'qrsd', 'blankFlag', 'detectionFlag', 'reportedValue', 'qualifier']
NAMES = dict(zip('Li B Na Mg Al Si P K Ca Ti V Cr Mn Fe Co Ni Cu Zn As Se Rb Sr Zr Mo Ag Cd Sn Sb Cs Ba Tl Pb Bi Th U'.split(),
    ['Lithium','Boron','Sodium','Magnesium','Aluminum','Silicon','Phosphorus','Potassium','Calcium','Titanium','Vanadium','Chromium','Manganese','Iron','Cobalt','Nickel','Copper','Zinc','Arsenic','Selenium','Rubidium','Strontium','Zirconium','Molybdenum','Silver','Cadmium','Tin','Antimony','Cesium','Barium','Thallium','Lead','Bismuth','Thorium','Uranium']))

def clean(x):
    if x is None: return ''
    if isinstance(x, float) and x.is_integer(): x = int(x)
    return re.sub(r'\s+', ' ', str(x)).strip()

def norm(x): return re.sub('[^a-z0-9]', '', clean(x).lower())

def finite(x): return isinstance(x, (int,float)) and not isinstance(x,bool) and math.isfinite(x)

def iso(x):
    if isinstance(x, (dt.datetime,dt.date)):
        return x.date().isoformat() if isinstance(x,dt.datetime) and 1900 <= x.year <= 2030 else x.isoformat() if isinstance(x,dt.date) and 1900 <= x.year <= 2030 else None
    s = clean(x)
    for fmt in ['%Y/%m/%d','%Y-%m-%d','%m/%d/%Y','%m/%d/%y','%m.%d.%y','%m.%d.%Y']:
        try: return dt.datetime.strptime(s,fmt).date().isoformat()
        except ValueError: pass
    return None

def label_date(label):
    s=clean(label)
    for pattern,fmt in [(r'(?<!\d)(20\d{2}/\d{1,2}/\d{1,2})(?!\d)','%Y/%m/%d'),(r'(?<!\d)(20\d{6})(?!\d)','%Y%m%d'),(r'(?<!\d)(\d{1,2}[/.]\d{1,2}[/.](?:20)?\d{2})(?!\d)',None),(r'(?<!\d)(\d{6})(?!\d)','%m%d%y')]:
        for m in re.finditer(pattern,s):
            v=m.group(1)
            if fmt:
                try:
                    d=dt.datetime.strptime(v,fmt).date().isoformat()
                    if '2020' <= d <= '2030': return d
                except ValueError: pass
            else:
                d=iso(v)
                if d: return d
    return None

def stripped_label(label):
    s=clean(label)
    s=re.sub(r'^\d+_', '', s)
    s=s.replace('_',' ')
    s=re.sub(r'(?<!\d)20\d{2}/\d{1,2}/\d{1,2}(?!\d)','',s)
    s=re.sub(r'(?<!\d)20\d{6}(?!\d)','',s)
    s=re.sub(r'(?<!\d)\d{1,2}[/.]\d{1,2}[/.](?:20)?\d{2}(?!\d)','',s)
    # Six-digit geographic/site codes must not be removed just because they
    # resemble MMDDYY. Remove only valid dates in this project's time span.
    def remove_date(m):
        try:
            d=dt.datetime.strptime(m.group(),'%m%d%y').date()
            return '' if 2020 <= d.year <= 2030 else m.group()
        except ValueError:return m.group()
    s=re.sub(r'(?<!\d)\d{6}(?!\d)',remove_date,s)
    s=re.sub(r'(?i)\b(?:rep(?:licate)?|filtered|unfiltered|unfilt|filt|cations|sr iso(?:topes)?|non[- ]acid[- ]clean syringe|acid[- ]clean syringe)\b','',s)
    s=re.sub(r'(?i)\b(?:UF|F)\b','',s)
    s=re.sub(r'(?i)^(?:MS|HC|Mirasol)\s+', '',s)
    return clean(s).strip(' _-')

ALIASES = {
 'ECCP':('ec-cp','Elder Creek convergence pool'), 'ECCS':('ec-cs','Elder Creek convergence stream'),
 'ECHEAD':('ec-head','Elder Creek head'), 'ECH':('ec-head','Elder Creek head'),
 'ECS1':('ec-s1','Elder Creek Spring 1'), 'ES1':('ec-s1','Elder Creek Spring 1'),
 'ECS2':('ec-s2','Elder Creek Spring 2'), 'ES2':('ec-s2','Elder Creek Spring 2'),
 'ELDERSPR2':('ec-s2','Elder Creek Spring 2'), 'ELDERSPR1':('ec-s1','Elder Creek Spring 1'),
 'ELDERSPRING2':('ec-s2','Elder Creek Spring 2'), 'ELDERSPRING1':('ec-s1','Elder Creek Spring 1'),
 'ELDERCREEKHEAD':('ec-head','Elder Creek head'),
 'ELDERCREEKCONVERGENCESTREAM':('ec-cs','Elder Creek convergence stream'),
 'ELDERCREEKCONVERGENCEPOOL':('ec-cp','Elder Creek convergence pool'),
 'PS':('ps','Pig Spring'), 'PIGSPRING':('ps','Pig Spring'),
 'RCNBATH':('rcn-bath','Roy Creek North Bath'),
 'RCNW1':('rcn-w1','Roy Creek North Waterfall 1'),
 'RCNW2':('rcn-w2','Roy Creek North Waterfall 2'),
 'RCNW3':('rcn-w3','Roy Creek North Waterfall 3'),
 'RCNWATER3':('rcn-w3','Roy Creek North Waterfall 3'),
 'RCNCS1':('rcn-cs1','Roy Creek North Comma Spring 1'),
 'RCNCS2':('rcn-cs2','Roy Creek North Comma Spring 2'),
 'RCNNWW':('rcn-nww','Roy Creek North NWW'),
 'RCSROAD':('rcs-road','Roy Creek South Road'),
 'RCSRESURGE':('rcs-resurgence','Roy Creek South Resurgence 1'),
 'RCSRESURGENCE':('rcs-resurgence','Roy Creek South Resurgence 1'),
 'RCSRESURGENCE1':('rcs-resurgence','Roy Creek South Resurgence 1'),
 'RCSTOP':('rcs-top','Roy Creek South Top'),
 'RCSTB':('rcs-tb','Roy Creek South TB'),
 'RCSLDS':('rcs-lds','Roy Creek South LDS'), 'LDS':('rcs-lds','Roy Creek South LDS'),
 'PEDLT':('ped-lt','Pedernales at LT'),
 'PEDHAM':('ped-ham','Pedernales at Hamilton'), 'PEDATHAM':('ped-ham','Pedernales at Hamilton'),
 'PEDHAMUNFILTERED':('ped-ham','Pedernales at Hamilton'),
 'PED':('ped-unknown','Pedernales location unspecified'),
 'FARMWELL':('farm-well','Mirasol Farm Well'),
 'ACKEREN':('van-ackeren','Van Ackeren well'), 'VANACKEREN':('van-ackeren','Van Ackeren well'),
 'DHSU':('deadmans-hole-upper','Deadmans Hole upper'),
 'DEADMANSHOLEUPPER':('deadmans-hole-upper','Deadmans Hole upper'),
 'DHP':('deadmans-hole-pool','Deadmans Hole pool'),
 'DEADMANSHOLE':('deadmans-hole-pool','Deadmans Hole pool'),
}

def site_identity(label, run):
    s=stripped_label(label); n=norm(s).upper()
    if n in ALIASES: return ALIASES[n]
    m=re.search(r'(?<!\d)(574\d{4})(?!\d)',s)
    if m: return 'well-'+m.group(1),'State water site '+m.group(1)
    # Coded vials are unique to their run and must never become geographic sites.
    if re.fullmatch(r'(?:VY|DBP|AJ|SL|DA|JS|HFC)\s*\d+',s,re.I):
        return 'unresolved-'+run.lower()+'-'+norm(s), s+' (site unresolved)'
    slug=re.sub('[^a-z0-9]+','-',s.lower()).strip('-') or 'unknown'
    return slug,s or 'Unknown site'

def is_qc(label, sample_name=''):
    s=(clean(label)+' '+clean(sample_name)).replace('_',' ')
    return bool(re.search(r'(?i)\b(?:blank|DI|CCB\d*|QC\d*|NIST|check|method analysis|L[1-9])\b|CPS RSD|ISTD Recovery|^Sample(?: |$)|^MS REP(?: |$)',s))

def fil(value):
    s=clean(value).lower()
    if re.search(r'\b(?:uf|unfiltered|unfilt)\b',s):return 'unfiltered'
    if re.search(r'\b(?:f|filtered|filt)\b',s):return 'filtered'
    return 'unknown'

def export():
    c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
    runs={r['run_id']:dict(r) for r in c.execute('select * from runs')}
    references=collections.defaultdict(lambda:collections.defaultdict(list))
    label_refs=collections.defaultdict(lambda:collections.defaultdict(list))
    nonwater=collections.defaultdict(set)
    books={}
    def book(run):
        if run not in books:books[run]=openpyxl.load_workbook(ROOT/runs[run]['source_file'],read_only=True,data_only=True)
        return books[run]
    def add(run,key,label,date,sheet,row,filtering=None):
        if not clean(label):return
        ref=dict(label=clean(label),date=iso(date),source=f'{sheet}!{row}',filtration=fil(filtering))
        if key:references[run][norm(key)].append(ref)
        label_refs[run][norm(label)].append(ref)
    def vertical(run,sheet,keycol,sitecol,datecol,start=2,end=500,prefix='',filcol=None):
        for rownum,row in enumerate(book(run)[sheet].iter_rows(min_row=start,max_row=end,max_col=max(keycol or 0,sitecol,datecol or 0,filcol or 0),values_only=True),start):
            val=lambda col:row[col-1] if col else None
            key=val(keycol)
            if prefix and finite(key):key=prefix+str(int(key))
            add(run,key,val(sitecol),val(datecol),sheet,rownum,val(filcol))
    def horizontal(run,sheet,keyrow,siterow,daterow,prefix='',filterrow=None):
        rows=list(book(run)[sheet].iter_rows(min_row=1,max_row=max(keyrow or 0,siterow,daterow or 0,filterrow or 0),max_col=200,values_only=True))
        for i,label in enumerate(rows[siterow-1][1:],1):
            key=rows[keyrow-1][i] if keyrow else None
            if prefix and finite(key):key=prefix+str(int(key))
            add(run,key,label,rows[daterow-1][i] if daterow else None,sheet,f'column {i+1}',rows[filterrow-1][i] if filterrow else None)
    vertical('RUN03_20241028','Dilutions',1,2,3,start=2,end=90,prefix='VY')
    vertical('RUN06_20250410','Yale dilutions',1,3,4,start=22,end=63)
    vertical('RUN07_20250516','For_spreadsheet',None,1,2,end=6)
    vertical('RUN07_20250516','HFC&VY dilutions',5,6,7,start=2,end=35,prefix='HFC')
    for sn in ['Mirasol Dilutions',"Austin's Colony",'Boggy Ck Fernando']:
        if sn=='Mirasol Dilutions':vertical('RUN08_20250630',sn,2,5,None,start=8,end=83,filcol=6)
        else:vertical('RUN08_20250630',sn,1,2,None,start=7,end=90,filcol=3)
    vertical('RUN09_20250821','Sample IDs',2,5,None,start=8,end=53)
    vertical('RUN09_20250821','For_spreadsheet',1,2,3,start=2,end=31)
    vertical('RUN10_20250904','yale dilutions',1,2,3,start=8,end=102,prefix='VY',filcol=5)
    vertical('RUN11_20251006','Pasteintospreadsheet',4,6,5,start=2,end=90)
    vertical('RUN13_20251209','For_spreadsheet',1,2,3,start=2,end=43)
    # RUN14 reference SampleName column duplicates VY10 and is one behind the
    # analytical source thereafter. Its physical sequence matches source site
    # labels; use row index and still require geographic identity agreement.
    for rownum,row in enumerate(book('RUN14_20251218')['For_Spreadsheet'].iter_rows(min_row=2,max_row=52,max_col=3,values_only=True),2):
        add('RUN14_20251218','VY'+str(rownum-1),row[0],row[1],'For_Spreadsheet',rownum)
    vertical('RUN15_20260207','Mirasol_simple',1,2,3,start=2,end=31)
    vertical('RUN15_20260207','Libbing dil',6,7,8,start=2,end=11,prefix='SL',filcol=9)
    horizontal('RUN17_20260528','Dilutions',10,11,13)
    vertical('RUN18_20260626','Yale dilutions',1,2,3,start=2,end=23,prefix='VY')
    horizontal('RUN19_20260701','Full Dilution info',4,5,6,prefix='VY',filterrow=7)
    vertical('RUN20_20260803','HCFS samples',None,1,2,start=2,end=20)
    for run,sheet,keycol,matrixcol in [
        ('RUN08_20250630','Mirasol Dilutions',2,3),
        ('RUN09_20250821','Sample IDs',2,3),
        ('RUN09_20250821','User Dilutions',4,5)]:
        for row in book(run)[sheet].iter_rows(max_row=100,max_col=max(keycol,matrixcol),values_only=True):
            if re.search(r'(?i)leachate|rock|soil',clean(row[matrixcol-1])):
                nonwater[run].add(norm(row[keycol-1]))
    samples=[]; keymap={}; excluded=collections.Counter(); site_table={}; issues=[]
    for raw in c.execute('select * from samples order by run_id,source_row,sample_key'):
        s=dict(raw);run=s['run_id'];label=s['sample_label'];name=s['sample_name']
        if run=='RUN05_20250123':excluded['RUN05 invalid database normalization']+=1;continue
        if not s['is_water_primary'] or s['is_blank']:excluded['blank or non-water in database']+=1;continue
        if is_qc(label,name):excluded['additional laboratory QC or malformed row']+=1;continue
        if norm(name) in nonwater[run]:excluded['rock or soil leachate recovered from workbook']+=1;continue
        # In first run the source label stores date/misc info; true site is in sample_name.
        if run=='RUN01_20240122':label=re.sub(r'^\d+_', '',name)
        current_id,current_label=site_identity(label,run)
        refs=references[run].get(norm(name),[]) or references[run].get(norm(s['data_file']),[])
        if run=='RUN14_20251218':
            refs=[r for r in refs if site_identity(r['label'],run)[0]==current_id]
        if not refs:refs=label_refs[run].get(norm(label),[])
        # Prefer exact geographic agreement whenever the database has a real label.
        unresolved=current_id.startswith('unresolved-')
        if not unresolved:
            agree=[r for r in refs if site_identity(r['label'],run)[0]==current_id]
            if agree:refs=agree
            elif refs:
                issues.append(f'{run} {name}: reference identity disagrees with label {label}; ignored reference join.')
                refs=[]
        ref_sites={site_identity(r['label'],run)[0] for r in refs}
        if len(ref_sites)==1 and refs and unresolved:
            label=refs[0]['label'];current_id,current_label=site_identity(label,run)
        if is_qc(label,name):excluded['QC recovered from reference sheet']+=1;continue
        # Original dilution sheets explicitly identify L25-coded samples as
        # rock/gypsum/soil leachates, although the SQLite matrix flags missed them.
        if re.match(r'(?i)^L25',label):excluded['rock or soil leachate recovered from workbook']+=1;continue
        date=label_date(label);basis='label' if date else 'unknown';date_source=None
        dates={r['date'] for r in refs if r['date']}
        if len(dates)==1 and len(ref_sites)==1:
            date=next(iter(dates));basis='workbook';date_source=refs[0]['source']
        if run=='RUN07_20250516' and norm(name) in ['hfc33','hfc34']:
            issues.append(f'{run} {name}: dilution table says 2025-03-25 but For_spreadsheet says 2025-04-10; left unknown.')
            date=None;basis='unknown';date_source=None
        if run=='RUN01_20240122':
            raw_date=clean(s['sample_label'])
            if raw_date.isdigit() and len(raw_date)==5:
                date=(dt.datetime(1899,12,30)+dt.timedelta(days=int(raw_date))).date().isoformat();basis='workbook';date_source='analytical Misc Info Excel date serial'
        analysis=runs[run]['analysis_date']
        if date and date>analysis:
            issues.append(f'{run} {name}: collection date {date} is later than analysis {analysis}; left unknown.')
            date=None;basis='unknown';date_source=None
        filtration=fil(label)
        if filtration=='unknown' and refs:
            fs={r['filtration'] for r in refs if r['filtration']!='unknown'}
            if len(fs)==1:filtration=next(iter(fs))
        if filtration=='unknown':filtration=s['filtration'] or 'unknown'
        sid='s'+str(len(samples)+1)
        obj=dict(id=sid,siteId=current_id,label=label,originalLabel=s['sample_label'],sampleCode=name,date=date,dateBasis=basis,dateSource=date_source,
                 analysisDate=analysis,filtration=filtration,isReplicate=bool(re.search(r'(?i)\brep(?:licate)?\b',label)),
                 sourceFile=s['source_file'],sourceSheet=s['source_sheet'],sourceRow=s['source_row'],runId=run,databaseSampleKey=s['sample_key'])
        samples.append(obj);keymap[s['sample_key']]=sid
        if current_id not in site_table:
            region='Mirasol study area' if current_id.startswith(('ec-','rcn-','rcs-','ped-','deadmans-')) or current_id in ['ps','farm-well'] else 'Regional / unresolved'
            typ='Unclassified water record'
            if current_id.startswith('well-'):typ='Groundwater site'
            elif 'well' in current_id or current_id=='van-ackeren':typ='Well'
            elif re.search(r'(?i)spring',current_label):typ='Spring'
            elif region=='Mirasol study area':typ='Surface water / spring'
            site_table[current_id]=dict(id=current_id,label=current_label,type=typ,region=region)
    analytes={};results=[]
    for r in c.execute('select * from results order by run_id,sample_key,channel_key'):
        if r['sample_key'] not in keymap:continue
        channel=r['channel'];aid=norm(channel)
        if aid not in analytes:
            analytes[aid]=dict(id=aid,label=NAMES.get(r['element'],r['element'])+' · '+channel,element=r['element'],unit='µg/L',channel=channel)
        results.append([keymap[r['sample_key']],aid,r['concentration_ppb'],r['recommended_use'],r['qrsd_used_pct'],r['blank_flag'],r['detection_flag']])
    recovery=PROJECT/'data/run05-recovery.json'
    if recovery.exists():
        rec=json.loads(recovery.read_text())
        for a in rec['analytes']:analytes[a['id']]=a
        for s in rec['samples']:
            s['siteId'],sl=site_identity(s.get('label',''), 'RUN05_20250123')
            samples.append(s)
            if s['siteId'] not in site_table:site_table[s['siteId']]=dict(id=s['siteId'],label=sl,type='Groundwater site' if s['siteId'].startswith('well') else 'Surface water / spring',region='Mirasol study area')
        for r in rec['results']:results.append([r.get(f) for f in FIELDS])
    for w in books.values():w.close()
    counts=dict(sites=len(site_table),samples=len(samples),results=len(results),numericResults=sum(finite(r[2]) for r in results),qualifiedResults=sum(not finite(r[2]) for r in results),analytes=len(analytes),elements=len({a['element'] for a in analytes.values()}),datedSamples=sum(bool(s.get('date')) for s in samples),unknownDateSamples=sum(not s.get('date') for s in samples))
    meta=dict(title='Mirasol water chemistry',generatedAt='2026-11-13',sourceDatabase=DB.name,sourceDatabaseSha256=hashlib.sha256(DB.read_bytes()).hexdigest(),counts=counts,
        units='µg/L; source reports ppb for water. No conversion of solid matrices.',
        statistics='Descriptive summaries of analytical records within the selected channel, QA state, filtration, date and replicate filters. Multiple aliquots and reruns are retained; n is not a count of independent field visits.',
        dates='Collection dates recovered from explicit sample labels or source workbook reference/dilution tables. Missing, ambiguous or future-relative-to-analysis dates stay unknown; analysis dates are separate.',
        channels='Mass transition and gas mode remain separate. NG and No Gas spellings are harmonized; legacy #1/#2/#3 mode labels retain their original identity.',
        qa='USE, REVIEW and EXCLUDE_PENDING_REVIEW are provisional inherited blank-screen dispositions, not validated water-safety classifications. No validated run-specific LLOQ; negative reported values are retained.',
        exclusions=dict(excluded),run05Recovered=recovery.exists(),notes=['No anion, pH, electrical conductivity, alkalinity, microbial or organic contaminant datasets were provided in the normalized database.','Coordinates and groundwater divide are approximate where digitized from the thesis; unmapped sites retain chemistry without invented coordinates.'])
    data=dict(meta=meta,resultFields=FIELDS,analytes=sorted(analytes.values(),key=lambda a:a['label']),sites=sorted(site_table.values(),key=lambda s:s['label']),samples=samples,results=results)
    out=PROJECT/'data/chemistry-laboratory-working.json';out.write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False,allow_nan=False))
    status=collections.Counter(r[3] for r in results)
    dates=sorted(s['date'] for s in samples if s.get('date'))
    audit=['# Chemistry export audit','',f'Export date: 2026-11-13. Source database SHA256: `{meta["sourceDatabaseSha256"]}`.','',
       '## Scope','',f'{len(samples):,} environmental analytical records at {len(site_table)} normalized site identities; {len(results):,} reported analyte/channel results ({counts["numericResults"]:,} numeric and {counts["qualifiedResults"]} censored/unavailable), {len(analytes)} channel-specific analytes, {counts["elements"]} elements.',
       f'{counts["datedSamples"]} records have a defensible collection date ({dates[0]} to {dates[-1]}); {counts["unknownDateSamples"]} remain unknown. Date filters must not silently use analysis dates.',
       '', '## Decisions','',meta['statistics'],'',meta['channels'],'',meta['qa'],'',meta['dates'],'',
       'Obvious laboratory standards, NIST reference waters, continuing calibration checks, DI/process blanks, method experiments, solid samples and malformed instrument-warning records are excluded from environmental summaries.',
       'SQLite RUN05 has invalid sample-column parsing. Its database records are excluded. Recovery from the original final corrected block is included only when data/run05-recovery.json is present.',
       'Workbook identities are joined by exact vial/data-file identifier and validated against meaningful existing site labels. Ambiguous site/date joins stay unresolved. No future collection date is silently corrected.',
       'RUN14 For_Spreadsheet repeats VY10 in its SampleName column and is one number behind the analytical sheet thereafter. Physical reference-row order (row minus one) matches the original analytical sample sequence; this corrected key is still checked against each source site label.',
       'Legacy alias RCT and RCN TB remain distinct from RCS Top/TB because the supplied labels alone do not establish equivalence. Ped LT, Ped at Hamilton and unspecified Ped remain separate. RCN W2 is retained separately.',
       'Numeric state water identifiers do not establish that a site is a well. Unclassified regional and unresolved coded sites are labeled accordingly. Apparent numeric-label typos such as 5741314 and 8748505 are preserved as written and must not be geolocated by guessing a correction.',
       '', '## Counts','',f'QA states: {dict(status)}',f'Excluded source sample records: {dict(excluded)}',f'Export JSON size: {out.stat().st_size:,} bytes.',
       '', '## Unresolved date and identity joins','']+['- '+x for x in sorted(set(issues))]
    (PROJECT/'laboratory-data-audit.local.md').write_text('\n'.join(audit)+'\n')
    print(json.dumps({'counts':counts,'qa':dict(status),'excluded':dict(excluded),'sizeBytes':out.stat().st_size,'issues':len(set(issues))},indent=2))

if __name__=='__main__':export()
