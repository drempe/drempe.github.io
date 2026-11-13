# Hill Country water chemistry dashboard

A static research dashboard for exploring available environmental chemistry records around the Hill Country Field Station in Hays County, Texas.

Open the hosted dashboard at https://drempe.github.io/groundwater-dashboard/.

## Use the dashboard

Choose an analytical channel and a statistic to color sampling locations. Click a location or choose it from the site explorer to inspect the dates, measurements, descriptive statistics, and time series available there. Filters control the records used in summaries. The map includes geology and an approximate groundwater divide with source notes.

Concentrations are reported in micrograms per liter, following the source database's aqueous ppb convention. Analytical channels remain separate. Laboratory controls and non-water materials are excluded from environmental site summaries. A missing measurement is never interpreted as zero. Collection dates and analysis dates are distinguished where the sources allow.

The existing database contains provisional QA/QC dispositions. Those labels address particular laboratory screens and do not establish overall analytical validity or drinking-water suitability. The dashboard explains relevant limitations alongside the data. See `data-audit.md` and `geography-notes.md` for extraction decisions and geographic provenance.

## Source and maintenance

Original thesis and analytical workbooks remain in their existing locations and are read only. The public site contains selected dashboard assets and derived data; it does not include the full thesis draft, original workbooks, or working extraction files.

Run `scripts/recover_run05.py` first, then `scripts/build_data.py` to export chemistry. `scripts/recover_run05.py` repairs a sample-label parsing problem in the January 2025 run using the original workbook and its sample reference sheet. Geographic preparation is documented separately. Rebuilds require the original local source files at the paths expected by those scripts.

The dashboard uses locally bundled Leaflet 1.9.4 under its BSD 2-Clause license. Background tiles require an internet connection and retain their provider attribution. This site has no server-side account system.

## Local preview

Serve this folder with a static HTTP server and open its local address. Opening `index.html` directly may prevent the browser from loading the JSON data files.

Publishing adds only the `groundwater-dashboard/` subdirectory to the existing GitHub Pages repository. Files elsewhere in that repository are preserved.
