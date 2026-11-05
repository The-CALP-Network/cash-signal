# Cash Signal

CALP Network's "dashboard of dashboards": cash-related indicators for 15 humanitarian responses, one tab per country, with a by-theme pivot. Single-file HTML, no build server, hosted on GitHub Pages.

**Purpose.** Help CALP prioritise its efforts at country level and strengthen analysis and messaging on each response. "Not available" is treated as a finding.

## Layout

```
index.html            the dashboard (generated — do not edit by hand)
data/<country>.json   one record per country; every figure carries a source id
build/template.html   page markup, styles and rendering code
build/build.py        injects data/*.json into the template -> index.html
build/archive/        earlier templates (v1 sidebar, v2 themed tabs, v3 country tabs)
schema/schema.json    the country record format
schema/validate.py    checks a country file (run before every rebuild)
docs/                 research brief, method and the independent spot-check report
```

## Updating the data

1. Edit `data/<country>.json`. Every datum is `{value, available: yes|partial|no, as_of, source_ids, note}`; `source_ids` point at entries in that file's `sources[]`. Leave `value` null and set `available: "no"` when nothing was found — say in `note` what was looked for.
2. Regional representatives fill the `rep_notes` block (key messages, barriers, CWG maturity, leadership buy-in, CALP priority, reviewed_by, reviewed_date). Once `reviewed_by` is set the country shows as Reviewed.
3. Validate and rebuild:

```
python3 -I schema/validate.py data/sudan.json
python3 -I build/build.py
```

4. Commit `data/` and `index.html` together.

The "Data collected" date on the page is the latest `last_researched` across the country files.

## Hosting on GitHub Pages

Settings → Pages → Source: *Deploy from a branch*, branch `main`, folder `/ (root)`. `index.html` is served at the repo's Pages URL. `.nojekyll` is present so Pages serves the file as-is. The page's only external request is the Roboto font from Google Fonts.

## Method, in brief

Data was collected on 5 November 2026 by AI agents from public sources (FTS API, 2026 HNRPs, CWG pages, REACH, WFP, CBPF reports), then spot-checked independently (`docs/spot-check-2026-11-05.md`). FTS figures use the single-cluster (destination) view of the "Multipurpose Cash" sector; the shared-cluster alternative is given in each note. AI country summaries are drafts awaiting review by CALP regional representatives.
