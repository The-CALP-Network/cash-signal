# Cash Signal

CALP Network's "dashboard of dashboards": cash-related indicators for 15 humanitarian responses, one tab per country, with a by-theme pivot. Single-file HTML, no build server, hosted on GitHub Pages.

**Purpose.** Help CALP prioritise its efforts at country level and strengthen analysis and messaging on each response. "Not available" is treated as a finding.

## Layout

```
index.html            the dashboard (generated: do not edit by hand)
data/<country>.json   one record per country; every figure carries a source id
data/fts/<id>.json    scripted FTS pull per plan (build/fts_pull.py)
data/rw/<id>.json     scripted read of each CWG page on ReliefWeb Response (build/rw_cwg_pull.py)
data/rw/overrides.json curated chairs and dashboards read from the CWG pages' contacts tabs (organisations and roles only)
data/v2/<id>.json     research fragments: coordination, CWG pulse, delivered volumes, FSPs (AI-collected)
build/template.html   page markup, styles and rendering code
build/build.py        injects data/*.json into the template -> index.html
build/fts_pull.py     pulls every flow per plan from the FTS API and computes the cash figures
build/rw_cwg_pull.py  reads the CWG pages on ReliefWeb Response
build/merge_v2.py     merges fts/, rw/ and v2/ into data/<country>.json (idempotent)
build/archive/        earlier templates (v1 sidebar … v5 pre-search)
schema/schema.json    the country record format
schema/validate.py    checks a country file (run before every rebuild)
docs/                 research brief, spot-check reports, and the HNRP 2026 modality-preference review (xlsx)
```

## What is on the page (v2, 6 Nov 2026)

- **Country search** and a draggable, scrollable tab strip with arrows. Press `/` to focus the search.
- **At a glance**: plan requirements, MPC share and funding, preference for cash, sectoral and total CVA funded (FTS), CVA delivered (in-country), and the coordination label (OCHA / UNHCR / both / neither).
- Indicator groups: modality preference, cost efficiency, plan requirements, overall funding, OCHA pooled funds, systems, **cash volumes**, **local leadership** (IASC MPC scaling plan objective 4, indicators 4.1 and 4.2).
- **CWG pulse (trial)**: what the group's public page shows: last update, dashboard currency (within 3 months or not), minutes, chair organisations by actor type.
- **Financial service providers** named in public sources, with hot-linked logos where the provider publishes one.
- **Caveat callouts** on every visual that rests on uneven data, and a full **Method** tab: sources, indicator definitions, known data-quality issues (computed from the data), update process, change log.

## Updating the data

1. Edit `data/<country>.json`. Every datum is `{value, available: yes|partial|no, as_of, source_ids, note}`; `source_ids` point at entries in that file's `sources[]`. Leave `value` null and set `available: "no"` when nothing was found: say in `note` what was looked for.
2. FTS figures: `python3 -I build/fts_pull.py` then `python3 -I build/merge_v2.py`. CWG pages: `python3 -I build/rw_cwg_pull.py`, edit `data/rw/overrides.json` if chairs or dashboards changed, then merge. The merge only fills v1 cells that are still empty and refreshes the v2 blocks.
3. Regional representatives fill the `rep_notes` block (key messages, barriers, CWG maturity, leadership buy-in, CALP priority, reviewed_by, reviewed_date). Once `reviewed_by` is set the country shows as Reviewed.
4. Validate and rebuild:

```
python3 -I schema/validate.py data/sudan.json
python3 -I build/build.py
```

5. Commit `data/` and `index.html` together.

The "Data collected" date on the page is the latest `last_researched` across the country files.

## Hosting on GitHub Pages

Settings → Pages → Source: *Deploy from a branch*, branch `main`, folder `/ (root)`. `index.html` is served at the repo's Pages URL. `.nojekyll` is present so Pages serves the file as-is. External requests: the Roboto font from Google Fonts, and provider logos hot-linked from the providers' own sites (never stored here).

## Method, in brief

Data was collected on 5–6 November 2026 by AI agents from public sources (FTS API, 2026 HNRPs, CWG pages, REACH, WFP, CBPF reports, agency press releases), then spot-checked independently (`docs/spot-check-2026-11-05.md`, `docs/spot-check-2026-11-06.md`). FTS figures are pulled by script and reproducible: MPC uses the single-cluster (destination) view; sectoral CVA uses the "Cash transfer programming (CTP)" modality tag outside the MPC cluster and is a floor; local-actor shares use first-level recipients only. AI country summaries are drafts awaiting review by CALP regional representatives. The Method tab on the page has the full version.
