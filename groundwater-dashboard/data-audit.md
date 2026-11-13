# Chemistry export audit

Export date: 2026-11-13. Source database SHA256: `7c3df7a907b8577fd4dca404adb451aa80adbd66bf4d72682974600d6fbf2729`.

## Scope

982 environmental analytical records at 270 normalized site identities; 51,116 reported analyte/channel results (50,975 numeric and 141 censored/unavailable), 144 channel-specific analytes, 35 elements.
847 records have a defensible collection date (2013-04-21 to 2026-06-10); 135 remain unknown. Date filters must not silently use analysis dates.

## Decisions

Descriptive summaries of analytical records within the selected channel, QA state, filtration, date and replicate filters. Multiple aliquots and reruns are retained; n is not a count of independent field visits.

Mass transition and gas mode remain separate. NG and No Gas spellings are harmonized; legacy #1/#2/#3 mode labels retain their original identity.

USE, REVIEW and EXCLUDE_PENDING_REVIEW are provisional inherited blank-screen dispositions, not validated water-safety classifications. No validated run-specific LLOQ; negative reported values are retained.

Collection dates recovered from explicit sample labels or source workbook reference/dilution tables. Missing, ambiguous or future-relative-to-analysis dates stay unknown; analysis dates are separate.

Obvious laboratory standards, NIST reference waters, continuing calibration checks, DI/process blanks, method experiments, solid samples and malformed instrument-warning records are excluded from environmental summaries.
SQLite RUN05 has invalid sample-column parsing. Its database records are excluded. Recovery from the original final corrected block is included only when data/run05-recovery.json is present.
Workbook identities are joined by exact vial/data-file identifier and validated against meaningful existing site labels. Ambiguous site/date joins stay unresolved. No future collection date is silently corrected.
RUN14 For_Spreadsheet repeats VY10 in its SampleName column and is one number behind the analytical sheet thereafter. Physical reference-row order (row minus one) matches the original analytical sample sequence; this corrected key is still checked against each source site label.
Legacy alias RCT and RCN TB remain distinct from RCS Top/TB because the supplied labels alone do not establish equivalence. Ped LT, Ped at Hamilton and unspecified Ped remain separate. RCN W2 is retained separately.
Numeric state water identifiers do not establish that a site is a well. Unclassified regional and unresolved coded sites are labeled accordingly. Apparent numeric-label typos such as 5741314 and 8748505 are preserved as written and must not be geolocated by guessing a correction.

## Counts

QA states: {'EXCLUDE_PENDING_REVIEW': 9591, 'REVIEW': 27929, 'USE': 13596}
Excluded source sample records: {'additional laboratory QC or malformed row': 294, 'blank or non-water in database': 435, 'RUN05 invalid database normalization': 38, 'QC recovered from reference sheet': 28, 'rock or soil leachate recovered from workbook': 103}
Export JSON size: 4,495,401 bytes.

## Unresolved date and identity joins

- RUN02_20240726 AJ45: collection date 2025-05-18 is later than analysis 2024-07-26; left unknown.
- RUN06_20250410 VY42: collection date 2025-08-24 is later than analysis 2025-04-10; left unknown.
- RUN07_20250516 HFC33: dilution table says 2025-03-25 but For_spreadsheet says 2025-04-10; left unknown.
- RUN07_20250516 HFC34: dilution table says 2025-03-25 but For_spreadsheet says 2025-04-10; left unknown.
