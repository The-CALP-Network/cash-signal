#!/usr/bin/env python3
"""Build index.html (the Cash Signal dashboard) by injecting data/*.json into build/template.html.
Run from anywhere: python3 -I build/build.py
Output: index.html at the repo root, which GitHub Pages serves.
"""
import json
import os
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(HERE), "data")
TEMPLATE = os.path.join(HERE, "template.html")
OUT = os.path.join(os.path.dirname(HERE), "index.html")
TOKEN = "__CASH_SIGNAL_OBJECT__"
# Regional representatives' notes, written by the Power Automate flow from the SharePoint list
# (see sharepoint/README.md). Overlaid on each country's rep_notes at build time; never merged
# into data/<country>.json, so the human layer stays separate from the researched layer.
REP_NOTES = os.path.join(DATA_DIR, "rep", "rep_notes.json")
# Cost-efficiency aggregates (country x modality), written by a script kept outside the repo.
# Only the aggregate file is committed; the agency-level dataset never is.
EFFICIENCY = os.path.join(DATA_DIR, "efficiency", "efficiency.json")
EFF_SOURCE_ID = "eff1"
# CALP's composite estimate of CVA per country (country totals only), written by a script kept
# outside the repo from the volumes survey, the CVA tracking pipeline and WFP's CASHboard.
ESTIMATE = os.path.join(DATA_DIR, "cva_estimate", "cva_estimate.json")
# Every source considered for cash volumes, with whether it is used: shown on the Method tab.
VOLUMES_SOURCES = os.path.join(DATA_DIR, "method", "volumes_sources.json")
REP_FIELDS = ("key_messages", "barriers", "cwg_maturity", "leadership_buy_in",
              "calp_priority", "reviewed_by", "reviewed_date")


def strip_comments(o):
    if isinstance(o, dict):
        return {k: strip_comments(v) for k, v in o.items() if not k.startswith("_")}
    if isinstance(o, list):
        return [strip_comments(x) for x in o]
    return o


def load_rep_notes():
    """{country id: rep_notes dict} from the SharePoint export, or {} if the file is absent."""
    if not os.path.exists(REP_NOTES):
        return {}
    with open(REP_NOTES, encoding="utf-8") as f:
        rows = json.load(f)
    if isinstance(rows, dict):
        rows = rows.get("rows", [])
    out = {}
    for r in rows:
        cid = (r.get("id") or "").strip().lower()
        if not cid:
            continue
        n = {k: (r.get(k) or "").strip() for k in REP_FIELDS}
        # a review needs a date: fall back to the row's last modification
        if n["reviewed_by"] and not n["reviewed_date"]:
            n["reviewed_date"] = (r.get("modified") or "")[:10]
        n["list_modified"] = (r.get("modified") or "")[:10]
        n["list_editor"] = r.get("editor") or ""
        out[cid] = n
    return out


def load_efficiency():
    """Aggregated cost-efficiency figures written by the private aggregation script, or {}."""
    if not os.path.exists(EFFICIENCY):
        return {}
    with open(EFFICIENCY, encoding="utf-8") as f:
        return json.load(f)


def apply_efficiency(c, eff):
    """Overlay the aggregate onto a country's cost_efficiency cells. Cells the dataset
    cannot fill keep whatever the researched layer recorded."""
    cells = ((eff.get("countries") or {}).get(c.get("iso3")) or {}).get("cost_efficiency") or {}
    filled = 0
    for key, d in cells.items():
        if d.get("available") in ("yes", "partial") and d.get("value") is not None:
            c.setdefault("cost_efficiency", {})[key] = dict(d, source_ids=[EFF_SOURCE_ID])
            filled += 1
    if filled:
        src = eff.get("source") or {}
        c.setdefault("sources", []).append({
            "id": EFF_SOURCE_ID,
            "title": src.get("title") or "CALP cost-efficiency dataset",
            "publisher": "CALP",
            "url": "",
            "date": src.get("dataset_date", ""),
            "accessed": eff.get("generated", ""),
        })
    return filled


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def usd_m(v):
    return "US$%sM" % format(round(v / 1e6), ",")


def apply_estimate(c, est):
    """Add CALP's composite CVA estimate as one cash_volumes cell. Country totals only."""
    e = (est.get("countries") or {}).get(c.get("iso3"))
    if not e or not e.get("headline_usd"):
        return 0
    year = est.get("year")
    labels = {x["id"]: x["label"] for x in e.get("candidates", [])}
    note = "Largest eligible figure for %s: %s." % (year, labels.get(e.get("headline_candidate"), "composite"))
    if e.get("fts_identified_usd"):
        note += " FTS shows %s for the same year." % usd_m(e["fts_identified_usd"])
    if e.get("transfer_value_usd"):
        note += " About %s of it is transfer value." % usd_m(e["transfer_value_usd"])
    if e.get("flags"):
        note += " " + " ".join(e["flags"])
    ids = [s["id"] for s in est.get("sources", [])]
    c.setdefault("cash_volumes", {})["calp_estimate_usd"] = {
        "value": e["headline_usd"], "available": "partial", "as_of": est.get("generated", ""),
        "source_ids": ids, "note": note, "period": str(year), "source_type": "CALP composite",
        "fts_identified_usd": e.get("fts_identified_usd"), "uplift_vs_fts": e.get("uplift_vs_fts"),
    }
    have = {s.get("id") for s in c.get("sources", [])}
    c.setdefault("sources", []).extend(s for s in est.get("sources", []) if s["id"] not in have)
    return 1


def main():
    rep = load_rep_notes()
    eff = load_efficiency()
    est = load_json(ESTIMATE)
    eff_cells = est_cells = 0
    countries = []
    for name in sorted(os.listdir(DATA_DIR)):
        if name.endswith(".json"):
            with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
                c = strip_comments(json.load(f))
            if c.get("id") in rep:
                c["rep_notes"] = dict(c.get("rep_notes") or {}, **rep[c["id"]])
            eff_cells += apply_efficiency(c, eff)
            est_cells += apply_estimate(c, est)
            countries.append(c)
    countries.sort(key=lambda c: c["name"])
    # "generated" is the data-collection date shown on the page: the latest last_researched across countries
    generated = max(c.get("last_researched", "") for c in countries) or datetime.date.today().isoformat()
    obj = {"generated": generated, "built": datetime.date.today().isoformat(), "countries": countries,
           "volumes_sources": load_json(VOLUMES_SOURCES)}
    js = json.dumps(obj, ensure_ascii=False, indent=1)
    # keep the data safe inside a <script> element
    js = (js.replace("</", "<\\/").replace("<!--", "<\\!--")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))
    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    if TOKEN not in html:
        raise SystemExit("placeholder %s missing from template" % TOKEN)
    html = html.replace(TOKEN, "const CASH_SIGNAL = " + js + ";")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s (%d countries, %.0f KB; rep notes for %d; %d cost-efficiency cells; %d CVA estimates; %d volume sources)"
          % (OUT, len(countries), len(html) / 1024, len(rep), eff_cells, est_cells,
             len((obj["volumes_sources"] or {}).get("sources", []))))


if __name__ == "__main__":
    main()
