# Vivian Yale thesis water chemistry atlas

Live page: https://drempe.github.io/groundwater-dashboard/.

## Publication basis

The dashboard is limited to results reported in the thesis and traceable to the final numerical table used for its figures. The separate laboratory working database's automated `USE`, `REVIEW` and `EXCLUDE_PENDING_REVIEW` labels do not establish thesis approval.

The supplied Word draft contains figure images and methodological descriptions, but no embedded sample-level result table. The final numerical reporting table has not yet been identified. Until it is supplied, the public dataset contains **zero concentrations** and downloads are disabled. The map retains 25 geographic site labels, published geology, and the approximate groundwater divide. Those markers do not imply that final chemistry values are loaded.

## Intended data interface

One element appears once in the selector. Instrument isotope, gas mode and dilution choices belong in measurement provenance. Final concentrations must preserve the thesis's selected analyses, blank corrections, exclusions and qualified values. A result cannot become eligible merely because a working database gives it a `USE` flag.

The thesis describes cation blank corrections where the blank contributes 5–20% of a concentration and non-reporting above 20%, as well as selecting reanalysis dilution separately for affected ions. These descriptions do not substitute for the final reported numerical values.

`data/chemistry.json` is the publication dataset. It carries `publicationBasis: thesis-reported-results-only`, a publication status, and only `THESIS_REPORTED` result rows. The browser rejects other publication bases and filters out other result dispositions. The current status is `awaiting-final-thesis-data`.

## Working files

Original thesis and laboratory files remain in their original locations and are read only. Earlier laboratory extraction work is retained locally as a separate working copy, excluded from the public dataset. `scripts/build_data.py` now writes only `data/chemistry-laboratory-working.json`; it cannot overwrite the publication dataset. Its flags are not final thesis QA/QC decisions.

`data-audit.md` describes the publication gate. `geography-notes.md` documents the map sources and positional tolerances. `scripts/validate_publication.py` checks the published dataset's eligibility and empty-state rules.

The map uses Leaflet 1.9.4 under its BSD 2-Clause license. Background maps require an internet connection and retain provider attribution. The geology polygons are stored locally. Publication changes only the `groundwater-dashboard/` directory of the GitHub Pages repository.
