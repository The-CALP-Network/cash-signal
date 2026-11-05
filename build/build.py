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


def strip_comments(o):
    if isinstance(o, dict):
        return {k: strip_comments(v) for k, v in o.items() if not k.startswith("_")}
    if isinstance(o, list):
        return [strip_comments(x) for x in o]
    return o


def main():
    countries = []
    for name in sorted(os.listdir(DATA_DIR)):
        if name.endswith(".json"):
            with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
                countries.append(strip_comments(json.load(f)))
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
    print("wrote %s (%d countries, %.0f KB)" % (OUT, len(countries), len(html) / 1024))


if __name__ == "__main__":
    main()
