#!/usr/bin/env python3
"""Pull the WFP market data that is public today, ahead of access to the WFP Data Bridges (DataViz) API.

Two public sources, both published by WFP on HDX:
  1. Market Functionality Index (MFI), dataset 'market-functionality-index-mfi'
     (trader-survey index, 0-10, nine dimensions; the current release covers H1 2026).
  2. WFP food prices, dataset 'wfp-food-prices-for-<country>' (market-level monthly prices;
     the same series the DataViz Economic Explorer and Data Bridges MarketPrices endpoint serve).

Writes data/wfp/<id>.json, one per country. merge_markets.py turns these into the `markets`
block on each country record. When the Data Bridges API key arrives, replace the two fetch_*
functions below with API calls; the output format stays the same.

Run: python3 -I build/wfp_markets_pull.py
"""
import csv, io, json, os, re, statistics, datetime, urllib.request
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "wfp")
HDX = "https://data.humdata.org/api/3/action/package_show?id="
UA = {"User-Agent": "cash-signal-build/1.0"}

# country id -> (ISO3, HDX food-price slug, names the MFI file may use)
COUNTRIES = {
    "afghanistan": ("AFG", "afghanistan", ["Afghanistan"]),
    "chad": ("TCD", "chad", ["Chad"]),
    "drc": ("COD", "democratic-republic-of-the-congo", ["Democratic Republic of the Congo"]),
    "lebanon": ("LBN", "lebanon", ["Lebanon"]),
    "mali": ("MLI", "mali", ["Mali"]),
    "mozambique": ("MOZ", "mozambique", ["Mozambique"]),
    "myanmar": ("MMR", "myanmar", ["Myanmar"]),
    "niger": ("NER", "niger", ["Niger"]),
    "nigeria": ("NGA", "nigeria", ["Nigeria"]),
    "opt": ("PSE", "state-of-palestine", ["Gaza", "State of Palestine", "Palestine", "West Bank"]),
    "somalia": ("SOM", "somalia", ["Somalia"]),
    "southsudan": ("SSD", "south-sudan", ["South Sudan"]),
    "sudan": ("SDN", "sudan", ["Sudan"]),
    "syria": ("SYR", "syrian-arab-republic", ["Syrian Arab Republic", "Syria"]),
    "yemen": ("YEM", "yemen", ["Yemen"]),
}
DIMS = ["Assortment", "Availability", "Price", "Resilience", "Competition", "Infrastructure", "Service", "Quality", "AccessProtection"]
DIM_LABEL = {"AccessProtection": "Access and protection", "Service": "Services", "Resilience": "Supply-chain resilience", "Quality": "Food quality"}
HIGH = {"High Risk", "Very High Risk"}

# The HDX MFI CSV has been through a French-locale spreadsheet: a few scores were turned into dates.
# 7.5 -> "07.mai" (day.month) and 8.75 -> "août.75" (month.year). Both are reversible.
FR_MONTH = {"janv": 1, "févr": 2, "fevr": 2, "mars": 3, "avr": 4, "mai": 5, "juin": 6, "juil": 7,
            "août": 8, "aout": 8, "sept": 9, "oct": 10, "nov": 11, "déc": 12, "dec": 12}


def get(url, timeout=120):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def hdx(slug):
    return json.loads(get(HDX + slug))["result"]


def num(v, fixes):
    v = (v or "").strip()
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        pass
    m = re.match(r"^(\d{1,2})\.([^\d.]+)$", v)          # "07.mai" = day 7, month 5 -> 7.5
    if m and m.group(2).lower() in FR_MONTH:
        fixes.append(v); return int(m.group(1)) + FR_MONTH[m.group(2).lower()] / 10
    m = re.match(r"^([^\d.]+)\.(\d{2})$", v)            # "août.75" = month 8, year 75 -> 8.75
    if m and m.group(1).lower() in FR_MONTH:
        fixes.append(v); return FR_MONTH[m.group(1).lower()] + int(m.group(2)) / 100
    fixes.append(v + " (dropped)")
    return None


def fetch_mfi():
    pkg = hdx("market-functionality-index-mfi")
    res = [r for r in pkg["resources"] if r["format"].upper() == "CSV"][0]
    raw = get(res["url"]).decode("latin-1")
    rows = list(csv.DictReader(io.StringIO(raw), delimiter=";"))
    meta = {"dataset": "https://data.humdata.org/dataset/market-functionality-index-mfi", "csv": res["url"],
            "dataset_date": pkg.get("dataset_date"), "last_modified": (pkg.get("last_modified") or "")[:10],
            "countries_in_release": sorted({r["CountryName"] for r in rows})}
    return rows, meta


def mfi_country(rows, names):
    fixes = []
    sel = [r for r in rows if r["CountryName"] in names]
    if not sel:
        return None
    for r in sel:
        r["_date"] = datetime.datetime.strptime(r["SurveyDate"], "%d.%m.%Y").date().isoformat()
    latest = {}                                          # latest assessment per market
    for r in sorted(sel, key=lambda r: r["_date"]):
        latest[r["MarketID"]] = r
    mk = list(latest.values())
    scores = [s for s in (num(r["MFIScore"], fixes) for r in mk) if s is not None]
    dims = {}
    for d in DIMS:
        vals = [v for v in (num(r[d], fixes) for r in mk) if v is not None]
        if vals:
            dims[d] = round(statistics.median(vals), 2)
    risk = defaultdict(int)
    for r in mk:
        risk[r["MFIRiskLevel"]] += 1
    adm = defaultdict(list)
    for r in mk:
        s = num(r["MFIScore"], [])
        if s is not None:
            adm[r["Adm1Name"]].append(s)
    by_adm1 = sorted(({"adm1": a, "markets": len(v), "median_score": round(statistics.median(v), 2)} for a, v in adm.items()),
                     key=lambda x: x["median_score"])
    weakest = sorted(dims, key=lambda d: dims[d])[:2]
    return {
        "markets": len(mk), "surveys": len({r["SurveyID"] for r in sel}), "assessments": len(sel),
        "first_date": min(r["_date"] for r in sel), "last_date": max(r["_date"] for r in sel),
        "survey_types": sorted({r["SurveyType"] for r in sel}),
        "median_score": round(statistics.median(scores), 2) if scores else None,
        "high_risk_pct": round(100 * sum(risk[k] for k in HIGH) / len(mk), 1),
        "risk_counts": dict(risk), "dimensions": dims,
        "weakest": [DIM_LABEL.get(d, d) for d in weakest],
        "by_adm1": by_adm1, "excel_fixed_cells": sum(1 for f in fixes if not f.endswith("(dropped)")),
        "excel_dropped_cells": sum(1 for f in fixes if f.endswith("(dropped)")),
    }


def fetch_prices(slug):
    pkg = hdx("wfp-food-prices-for-" + slug)
    res = [r for r in pkg["resources"] if "food_prices" in r["url"]][0]
    raw = get(res["url"], timeout=300).decode("utf-8")
    rdr = csv.DictReader(io.StringIO(raw))
    rows = [r for r in rdr if not r["date"].startswith("#")]
    return rows, {"dataset": "https://data.humdata.org/dataset/wfp-food-prices-for-" + slug, "csv": res["url"],
                  "dataset_date": pkg.get("dataset_date"), "last_modified": (pkg.get("last_modified") or "")[:10]}


def month(s):
    return s[:7]


def shift(ym, k):
    y, m = int(ym[:4]), int(ym[5:7]) + k
    while m < 1: y, m = y - 1, m + 12
    while m > 12: y, m = y + 1, m - 12
    return "%04d-%02d" % (y, m)


def prices_country(rows, today):
    cur = today[:7]
    food = [r for r in rows if r["pricetype"] == "Retail" and r["category"] != "non-food"]
    months = sorted({month(r["date"]) for r in food})
    partial = [m for m in months if m >= cur]            # month still running (WFP stamps mid-month)
    complete = [m for m in months if m < cur]
    if not complete:
        return None
    L = complete[-1]; P = shift(L, -12)
    series = defaultdict(dict)                           # (market, commodity, unit, currency) -> {month: (price, usd)}
    for r in food:
        m = month(r["date"])
        if m in (L, P):
            k = (r["market_id"], r["commodity_id"], r["unit"], r["currency"])
            try:
                series[k][m] = (float(r["price"]), float(r["usdprice"]) if r["usdprice"] else None)
            except ValueError:
                pass
    loc, usd = [], []
    for k, v in series.items():
        if L in v and P in v and v[P][0] > 0:
            loc.append(v[L][0] / v[P][0] - 1)
            if v[L][1] and v[P][1]:
                usd.append(v[L][1] / v[P][1] - 1)
    flags = []
    med_loc = statistics.median(loc) if loc else None
    if med_loc is not None and (med_loc < -0.9 or med_loc > 20):
        flags.append("local-currency change outside -90%..+2000%: possible redenomination; local figure withheld")
        med_loc = None
    last12 = [shift(L, -i) for i in range(12)]
    mk_latest = {r["market_id"] for r in food if month(r["date"]) == L}
    mk_12 = {r["market_id"] for r in food if month(r["date"]) in last12}
    comm = {r["commodity"] for r in food if month(r["date"]) == L}
    flag_mix = defaultdict(int)
    for r in food:
        if month(r["date"]) == L:
            flag_mix[r["priceflag"]] += 1
    gap = (int(cur[:4]) - int(L[:4])) * 12 + int(cur[5:7]) - int(L[5:7])
    return {
        "latest_month": L, "partial_months_after": partial, "months_since_latest": gap,
        "fresh_3m": gap <= 3,
        "markets_latest": len(mk_latest), "markets_12m": len(mk_12), "commodities_latest": len(comm),
        "currencies": sorted({r["currency"] for r in food if month(r["date"]) == L}),
        "price_flags": dict(flag_mix),
        "yoy_base_month": P, "yoy_series": len(loc),
        "yoy_local_pct": round(100 * med_loc, 1) if med_loc is not None else None,
        "yoy_local_iqr": [round(100 * q, 1) for q in statistics.quantiles(loc, n=4)[::2]] if len(loc) >= 4 else None,
        "yoy_usd_pct": round(100 * statistics.median(usd), 1) if usd else None,
        "yoy_usd_series": len(usd), "flags": flags,
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    today = datetime.date.today().isoformat()
    mrows, mmeta = fetch_mfi()
    print("MFI release:", mmeta["dataset_date"], "countries:", len(mmeta["countries_in_release"]))
    for cid, (iso3, slug, names) in COUNTRIES.items():
        out = {"id": cid, "iso3": iso3, "pulled": today, "mfi_source": mmeta, "mfi": mfi_country(mrows, names)}
        try:
            prows, pmeta = fetch_prices(slug)
            out["prices_source"], out["prices"] = pmeta, prices_country(prows, today)
        except Exception as e:                           # keep going; a missing price file is a finding
            out["prices_source"], out["prices"] = {"error": str(e)}, None
        with open(os.path.join(OUT, cid + ".json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False); f.write("\n")
        m, p = out["mfi"], out["prices"]
        print("%-11s MFI %-24s prices %s" % (cid,
              ("%d mkts, median %.1f, %.0f%% high" % (m["markets"], m["median_score"], m["high_risk_pct"])) if m else "not assessed",
              ("%s, %d mkts, yoy %s%% local / %s%% USD (%d series)" % (p["latest_month"], p["markets_latest"], p["yoy_local_pct"], p["yoy_usd_pct"], p["yoy_series"])) if p else "none"))


if __name__ == "__main__":
    main()
