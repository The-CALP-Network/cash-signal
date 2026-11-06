#!/usr/bin/env python3
"""Merge data/wfp/<id>.json (from wfp_markets_pull.py) into data/<id>.json as the `markets` block.

Idempotent: replaces the `markets` block and the wfp1/wfp2 sources each run. Leaves every other block alone,
including the v1 `market_monitoring` field (which records joint monitoring systems such as JMMIs).

Run: python3 -I build/merge_markets.py
"""
import json, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")

# What the WFP Data Bridges API should add once the key arrives (endpoint families per the API catalogue).
DATA_BRIDGES_PENDING = [
    "MFI trend across survey rounds, not just the latest public release",
    "MFI by admin area and market, with all nine dimensions",
    "Exchange rates (official and parallel) and their month-on-month change",
    "Minimum expenditure basket cost, where WFP computes one",
    "Price series beyond the HDX extract: weekly prices and wholesale",
]


def datum(value=None, available="no", as_of="", sids=None, note="", **extra):
    d = {"value": value, "available": available, "as_of": as_of, "source_ids": sids or [], "note": note}
    d.update(extra)
    return d


def merge(c, w):
    c["sources"] = [s for s in c["sources"] if s["id"] not in ("wfp1", "wfp2")]
    mfi, ms = w.get("mfi"), w.get("mfi_source") or {}
    pr, ps = w.get("prices"), w.get("prices_source") or {}
    c["sources"].append({"id": "wfp1", "title": "WFP Market Functionality Index (MFI), HDX release " + (ms.get("dataset_date") or ""),
                         "publisher": "WFP via HDX", "url": ms.get("dataset", "https://data.humdata.org/dataset/market-functionality-index-mfi"),
                         "date": ms.get("last_modified", ""), "accessed": w["pulled"]})
    if ps.get("dataset"):
        c["sources"].append({"id": "wfp2", "title": "WFP food prices for %s (market-level monthly series)" % c["name"],
                             "publisher": "WFP via HDX", "url": ps["dataset"], "date": ps.get("last_modified", ""), "accessed": w["pulled"]})
    rel = "the public MFI release (%d countries, %s)" % (len(ms.get("countries_in_release") or []), (ms.get("dataset_date") or "").replace("T00:00:00", "").replace("T23:59:59", ""))
    m = {"pulled": w["pulled"]}

    if mfi:
        span = mfi["first_date"] if mfi["first_date"] == mfi["last_date"] else "%s to %s" % (mfi["first_date"], mfi["last_date"])
        thin = mfi["markets"] < 10
        av = "partial" if thin else "yes"
        m["mfi_score"] = datum(mfi["median_score"], av, mfi["last_date"], ["wfp1"],
                               "Median MFI score (0-10) across %d markets, latest assessment per market, %s. Weakest dimensions: %s.%s"
                               % (mfi["markets"], span, ", ".join(mfi["weakest"]), " Very few markets: indicative only." if thin else ""),
                               markets=mfi["markets"])
        m["mfi_high_risk_pct"] = datum(mfi["high_risk_pct"], av, mfi["last_date"], ["wfp1"],
                                       "Share of assessed markets WFP rates high or very high risk.", markets=mfi["markets"])
        m["mfi_detail"] = {k: mfi[k] for k in ("markets", "surveys", "first_date", "last_date", "survey_types", "risk_counts",
                                               "dimensions", "by_adm1", "excel_fixed_cells")}
    else:
        nf = "Not in %s. WFP may hold MFI rounds that are not public; the Data Bridges API should show them." % rel
        m["mfi_score"] = datum(note=nf)
        m["mfi_high_risk_pct"] = datum(note=nf)
        m["mfi_detail"] = None

    if pr:
        stale = not pr["fresh_3m"]
        ln = pr["latest_month"]
        base = "%d food series (market x commodity) with a retail price in both %s and %s; unweighted median." % (pr["yoy_series"], ln, pr["yoy_base_month"])
        av = "partial" if (stale or pr["yoy_series"] < 30) else "yes"
        m["price_markets"] = datum(pr["markets_latest"], "partial" if stale else "yes", ln, ["wfp2"],
                                   "Markets with a WFP retail food price in %s; %d markets reported at least once in the 12 months to then.%s"
                                   % (ln, pr["markets_12m"], " Latest month is %d months old." % pr["months_since_latest"] if stale else ""))
        m["price_change_yoy_local"] = datum(pr["yoy_local_pct"], av if pr["yoy_local_pct"] is not None else "no", ln, ["wfp2"],
                                         ("Year-on-year change in local currency (%s). " % "/".join(pr["currencies"])) + base
                                         + (" Middle half of series: %s%% to %s%%." % tuple(pr["yoy_local_iqr"]) if pr.get("yoy_local_iqr") else "")
                                         + (" " + "; ".join(pr["flags"]) if pr["flags"] else ""))
        m["price_change_yoy_usd"] = datum(pr["yoy_usd_pct"], av if pr["yoy_usd_pct"] is not None else "no", ln, ["wfp2"],
                                       "Same series in US dollars at WFP's conversion rate (%d series). The gap to the local-currency figure is mostly the exchange rate." % pr["yoy_usd_series"])
        m["prices_detail"] = {k: pr[k] for k in ("latest_month", "months_since_latest", "fresh_3m", "markets_latest", "markets_12m",
                                                 "commodities_latest", "currencies", "yoy_base_month", "yoy_series", "partial_months_after")}
    else:
        for k in ("price_markets", "price_change_yoy_local", "price_change_yoy_usd"):
            m[k] = datum(note="No WFP food-price dataset for this country on HDX.")
        m["prices_detail"] = None

    m["data_bridges"] = {"status": "awaiting API access", "pending": DATA_BRIDGES_PENDING}
    c["markets"] = m
    return c


def main():
    n = 0
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        c = json.load(open(p, encoding="utf-8"))
        wp = os.path.join(DATA, "wfp", c["id"] + ".json")
        if not os.path.exists(wp):
            print(c["id"], "no WFP file; skipped"); continue
        c = merge(c, json.load(open(wp, encoding="utf-8")))
        with open(p, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2, ensure_ascii=False); f.write("\n")
        n += 1
    print("merged markets into", n, "country files")


if __name__ == "__main__":
    main()
