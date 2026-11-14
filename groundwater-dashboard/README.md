# Vivian Yale thesis water chemistry atlas

Live page: https://drempe.github.io/groundwater-dashboard/.

## Reconstruction from the raw files

The thesis methods and original laboratory files can be used to reconstruct a dataset. A finished final spreadsheet would help validate that reconstruction, but is not required to begin it. The working reconstruction selects an analytical channel for each element and run, traces source cells, resolves documented per-ion dilution choices, calculates field-blank fractions and corrections, and checks detection limits against the thesis's Table S2.

An initial major-cation reconstruction is retained locally with complete source and decision lineage. It is a working product, not a claim of exact recovery of the author's final dataset. Documented source disagreements remain visible rather than being forced to match the thesis.

The previous separate database's automated USE/REVIEW/10x blank rules do not determine thesis-method eligibility.

## What remains before numerical publication

The thesis uses only samples with absolute charge-balance error at or below 10%, and averages replicate pairs only when both satisfy that criterion. This requires matched sulfate, bicarbonate, chloride and nitrate results in addition to Ca, Mg, Na, K and Sr. Complete matched anion/alkalinity inputs have not been identified in the supplied cation folder. Source ambiguities and several method details also remain under review.

The public dataset therefore still contains zero concentrations and downloads remain disabled. Locations, geology and the approximate groundwater divide are retained as geographic context. The public notice describes the reconstruction status; it does not say that a finished final table is a prerequisite.

## Display and source records

One element appears once in the selector. Isotope, gas mode and selected dilution belong in each measurement's provenance. The thesis's reported blank corrections, exclusions, censoring and sample-level charge balance must be accounted for before any reconstructed result is displayed as eligible.

The working pipeline, evidence manifests, review and candidate data are kept in the local `reconstruction/` folder, excluded from public deployment. `data/chemistry.json` is the separate, currently empty publication dataset. Working exports cannot automatically become public concentrations.

Original thesis and laboratory files remain in their original locations and are read only. The map uses Leaflet 1.9.4 under its BSD 2-Clause license, with provider attribution retained. Local geology polygons and map provenance are documented in `geography-notes.md`. Publication changes only this dashboard directory in the GitHub Pages repository.
