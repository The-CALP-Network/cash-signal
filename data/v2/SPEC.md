# Cash Signal v2 research fragment — one JSON file per country at data/v2/<id>.json

Rules
- Every fact must come from a page you actually opened (WebFetch) or a search result snippet; cite it in `sources[]` and reference the id in `source_ids`.
- Source ids are prefixed `v2s` (v2s1, v2s2 ...) so they do not collide with the existing s1.. ids.
- "Not found" is a finding: set `available: "no"` / `"unknown"` and say in `note` what you looked for and where.
- Never record people's names or email addresses. Organisations and roles only.
- Dates ISO (YYYY-MM-DD, or YYYY-MM if that is all the page gives). `accessed` is today's date.
- Logos: record a URL only (never download). Only from Wikimedia Commons, the provider's own brand/press page, or the provider's site favicon/logo. If none, leave `logo_url` "".
- Keep notes to one or two sentences. Plain JSON, no comments, must parse.

Schema
{
  "id": "<country id>",
  "coordination": {
    "label": "OCHA | UNHCR | OCHA + UNHCR | Neither",
    "ocha_plan": "name of the OCHA-coordinated plan (HNRP/HRP/Flash Appeal) covering 2026, or 'none'",
    "unhcr_plan": "name of any UNHCR-led plan with an in-country chapter for 2026 (country RRP, regional RRP chapter, 3RP), or 'none'",
    "note": "one line, e.g. 'HNRP (OCHA) plus Sudan regional RRP chapter (UNHCR)'",
    "source_ids": []
  },
  "cwg_reliefweb": {
    "page_url": "the Cash Working Group page on response.reliefweb.int (or equivalent hub such as data.unhcr.org / humanitarianresponse) — '' if none",
    "page_title": "",
    "page_last_updated": "date of the most recent item (document, event, dashboard, update) visible on that page, YYYY-MM-DD, or ''",
    "last_update_basis": "what that date is: e.g. 'latest document posted', 'page footer updated stamp', 'latest meeting minutes'",
    "dashboard_url": "in-country CVA / CWG dashboard (Power BI, Tableau, 4W, HDX) — '' if none",
    "dashboard_name": "",
    "dashboard_last_updated": "YYYY-MM-DD or ''",
    "dashboard_period": "period the dashboard data covers, e.g. 'Jan-Jun 2025'",
    "meeting_minutes_latest": "date of the latest meeting minutes found, or ''",
    "co_chairs": [
      {"organisation": "", "actor_type": "UN | INGO | NNGO | Government | RCRC | Consortium | Other", "role": "chair | co-chair | co-lead | coordinator | IM lead"}
    ],
    "local_cochair": "yes | no | unknown   (yes only if a national/local NGO, national government body or national RCRC society holds a chair/co-chair/co-lead role)",
    "contacts_basis": "where the chair/co-chair information came from (page contacts block, ToR, minutes, HNRP)",
    "note": "",
    "source_ids": []
  },
  "cash_volumes": {
    "cva_delivered_usd":          {"value": null, "available": "yes | partial | no", "as_of": "", "period": "", "source_ids": [], "note": "", "source_type": "CWG dashboard | OCHA CVA snapshot | cluster report | other"},
    "mpc_delivered_usd":          {"value": null, "available": "yes | partial | no", "as_of": "", "period": "", "source_ids": [], "note": "", "source_type": ""},
    "sectoral_cva_delivered_usd": {"value": null, "available": "yes | partial | no", "as_of": "", "period": "", "source_ids": [], "note": "", "source_type": ""}
  },
  "fsps": [
    {"name": "", "type": "bank | mobile money | money transfer operator | fintech / e-wallet | post office | hawala | card / prepaid | other",
     "used_by": ["organisations named as using it, e.g. WFP, UNHCR, CWG members"],
     "evidence": "one line: what the source says",
     "website": "", "logo_url": "", "logo_source": "Wikimedia Commons | provider brand page | provider site | ''",
     "source_ids": []}
  ],
  "sources": [
    {"id": "v2s1", "title": "", "publisher": "", "url": "https://...", "date": "YYYY-MM-DD or YYYY-MM or YYYY", "accessed": "2026-11-06"}
  ]
}

Where to look
- CWG page: https://response.reliefweb.int/<country>/<cash-working-group slug> (try the country hub home first: https://response.reliefweb.int/<country>). Lebanon's CWG lives on data.unhcr.org; Myanmar's on themimu.info; Syria's may be on humanitarianaction.info or response.reliefweb.int/syria.
- Volumes: CWG dashboards and 'CVA snapshot' / 'CVA overview' infographics on reliefweb.int (search 'reliefweb <country> cash and voucher assistance dashboard 2025', '<country> CWG 4W 2025'); OCHA regional CVA overviews; HNRP 2026 CVA section may report 2025 delivered amounts.
- FSPs: CWG FSP mapping / FSP assessment documents, WFP and UNHCR country pages and press releases, CaLP case studies, mobile money operator announcements, HNRP CVA section. Record each FSP once with every organisation seen using it.
- Coordination: humanitarianaction.info plan page (OCHA); data.unhcr.org / reporting.unhcr.org for RRP chapters.
