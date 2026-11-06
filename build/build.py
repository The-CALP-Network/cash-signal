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


def main():
    rep = load_rep_notes()
    countries = []
    for name in sorted(os.listdir(DATA_DIR)):
        if name.endswith(".json"):
            with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
                c = strip_comments(json.load(f))
            if c.get("id") in rep:
                c["rep_notes"] = dict(c.get("rep_notes") or {}, **rep[c["id"]])
            countries.append(c)
    countries.sort(key=lambda c: c["name"])
    # "generated" is the data-collection date shown on the page: the latest last_researched across countries
    generated = max(c.get("last_researched", "") for c in countries) or datetime.date.today().isoformat()
    obj = {"generated": generated, "built": datetime.date.today().isoformat(), "countries": countries}
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
    print("wrote %s (%d countries, %.0f KB; rep notes for %d)" % (OUT, len(countries), len(html) / 1024, len(rep)))


if __name__ == "__main__":
    main()
