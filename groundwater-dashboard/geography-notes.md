# Geographic sources and limitations

The dashboard maps 25 chemistry site labels: 19 approximate local labels from the supplied thesis Figure 2B and six locations matched exactly by identifier/name to the published Hunt (2023) Table 2 coordinates. Three Deadmans labels use one shared group centroid because the source figure does not distinguish their sublocations. Unresolved labels remain in the chemistry table and are not assigned invented coordinates.

## Published bedrock geology

Source: Brian Hunt, Hydrogeologic Data: Hamilton Pool and Reimers Ranch Source Water Protection Study in Western Travis County, Texas, Texas Data Repository, DOI [10.18738/T8/SF0BXT](https://doi.org/10.18738/T8/SF0BXT), version 7.1 metadata accessed 2026-11-13. Repository metadata identifies CC0 1.0. The Phase 2 report is the 2023 report cited by the thesis.

The original `Geology_bedrock_units_2023` layer was read from the published `HamiltonPool_geologicmap.lpkx` in `Geology_v3_2023.tar`, repository file ID 296411. It contains 161 polygons in EPSG:26914. The browser layer removes height ordinates, simplifies polygons by 3 m in the native coordinate system with topology preservation, transforms to WGS84, and rounds coordinates to six decimals. Two source polygons contained self intersecting rings; a standard make_valid operation repairs their geometry before simplification. No new geologic contacts were interpreted. A source unit string `Kgrl\` is displayed as `Kgrl`; a null unit is labeled unclassified. These are surface bedrock units, not determinations of well completion intervals.

Colors are chosen for legibility and resemble the source legend. The layer is local GeoJSON, so no remote geology service is required. It does not extrapolate outside the original map footprint.

## Approximate local site coordinates

The supplied thesis has no machine readable coordinate table. Its embedded Figure 2 image is 955 × 1053 pixels. Five well symbols in panel B were matched to locations listed in Hunt (2023), Table 2, printed pp.85–87: Farm Well 5747607, Johanson1 5747313, Johanson2 5747314, Buddy RV 5747316, and Hegemier5747602. A least squares affine transform from image pixels to longitude/latitude gives control residuals of 0.9–21.8 m. Residuals only measure the fit to these controls and do not establish the accuracy of the map or sampling coordinates.

Named local markers were manually digitized from Figure 2B. The dashboard uses a conservative 150 m display tolerance for these locations. This is an analyst chosen tolerance, not a statistical confidence interval. EC CS and CP share one source marker. EC S1 and Head are very close and their assignment is approximate. The three Deadmans labels share a group centroid with a 300 m display tolerance. None is presented as a field GPS measurement.

The native embedded figure has differing horizontal and vertical scale after placement/resizing. The affine fit uses independently matched wells rather than assuming isotropic image pixels or relying on its scale bar alone.

## Groundwater divide

The approximate divide line is manually traced from thesis Figure 2A, which explicitly attributes its divide and geology to Hunt (2023b). The line was registered to panel B using common well symbols and transformed with the panel B affine fit. The dashboard therefore shows a **digitized approximation**, not the original GIS divide. A 300 m display tolerance is used for communication; it is neither a measured uncertainty nor a hydrologic model result. The source report calls the divide approximate. Its position may change with water levels and pumping.

The trace has not been recomputed from concentrations and should not be read as a current hydraulic boundary. Hunt report Figure53 independently corroborates the presence and broad path of the Middle Trinity groundwater divide, but is not substituted for the thesis line.

## Intentionally unmapped labels

RCN W2/NWW are not explicitly labeled on Figure2B. Individual Pedernales symbols cannot be assigned safely to Hamilton/LT/unspecified laboratory labels. The chemistry identifier5747318 conflicts with a reported Edge Spring site in Hunt Table2; it remains unresolved. Other regional laboratory labels lack defensible matching coordinates in the available files. No aliases were inferred solely to make additional points appear.

## Reproduction

`geo_build.py` records controls, marker pixels, line vertices, transformations and provenance, and generates `data/geography.json` plus `data/geology.geojson`. It needs numpy, pyogrio, pyproj and shapely. Downloaded public archives and temporary libraries are working files, excluded from deployment. The original thesis and chemistry files were not edited.
