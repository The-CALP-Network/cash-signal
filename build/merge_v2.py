#!/usr/bin/env python3
"""Merge the v2 additions into the country records.

Inputs
  data/<id>.json       the v1 country record (edited in place, idempotently)
  data/fts/<id>.json   output of fts_pull.py
  data/v2/<id>.json    research fragments (coordination, cwg_reliefweb, cash_volumes, fsps): optional

Adds / refreshes these blocks on each country record:
  coordination, fts_cva, cash_volumes, cwg_reliefweb, fsps, localisation
and these sources: fts1 (FTS API pull) plus every v2s* source from the fragment.
Also fills, only where the v1 cell is empty, overall_funding.sectoral_cash_pct and pooled_funds.mpc_pct /
cbpf_allocations_usd from FTS, flagged partial with an explicit note.

Run: python3 -I build/merge_v2.py
"""
import json, os, glob, datetime, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
NEW_BLOCKS = ["coordination", "fts_cva", "cash_volumes", "cwg_reliefweb", "fsps", "localisation"]


def datum(value=None, available="no", as_of="", sids=None, note="", **extra):
    d = {"value": value, "available": available, "as_of": as_of, "source_ids": sids or [], "note": note}
    d.update(extra)
    return d


def months_between(a, b):
    """Whole months from ISO date a to ISO date b (both YYYY-MM or YYYY-MM-DD)."""
    try:
        ya, ma = int(a[:4]), int(a[5:7]); yb, mb = int(b[:4]), int(b[5:7])
        return (yb - ya) * 12 + (mb - ma)
    except Exception:
        return None


def merge(c, fts, frag, today):
    # ---- strip earlier v2 material so the merge is idempotent
    for k in NEW_BLOCKS:
        c.pop(k, None)
    c["sources"] = [s for s in c["sources"] if not (s["id"] in ("fts1", "rw1") or s["id"].startswith("v2s"))]

    # ---- FTS
    s = fts["summary"]
    fts_src = {"id": "fts1", "title": "FTS public API, flows for plan %d (%s)" % (fts["plan_id"], fts["plan_name"]),
               "publisher": "OCHA FTS", "url": fts["fts_page"], "date": fts["pulled"], "accessed": fts["pulled"]}
    c["sources"].append(fts_src)
    asof = s["latest_flow_date"] or fts["pulled"]
    mpc_note = "FTS single-cluster view of the %s cluster; shared-cluster view US$%.1fM. Incoming flows, pledges excluded." % (
        s.get("mpc_cluster_name") or "multi-purpose cash", s["mpc_cluster_funding_shared_view"] / 1e6)
    sect_note = ("Flows whose FTS modality field is 'Cash transfer programming (CTP)' and whose destination cluster is not multi-purpose cash: %d flows. "
                 "The CTP tag is set by the reporting donor or agency and is not applied consistently, so this is a floor, not a measure of sectoral cash."
                 % s["sectoral_cva_flow_count"])
    bycl = s.get("sectoral_cva_by_cluster") or {}
    top = ", ".join("%s US$%.1fM" % (k, v / 1e6) for k, v in list(bycl.items())[:3])
    c["fts_cva"] = {
        "pulled": fts["pulled"], "plan_id": fts["plan_id"], "api_url": fts["api"], "fts_page": fts["fts_page"],
        "total_funding_usd": datum(s["total_funding"], "yes", asof, ["fts1"], "All incoming funding to the plan, pledges excluded. Matches the FTS plan summary."),
        "mpc_usd": datum(s["mpc_cluster_funding"] if s["mpc_cluster_name"] else None, "yes" if s["mpc_cluster_name"] else "no", asof if s["mpc_cluster_name"] else "", ["fts1"],
                         mpc_note if s["mpc_cluster_name"] else "No multi-purpose cash cluster with funding is visible on FTS for this plan (the plan may still carry an MPC requirement), so MPC funding cannot be seen."),
        "ctp_usd": datum(s["ctp_funding"], "yes", asof, ["fts1"], "All flows tagged 'Cash transfer programming (CTP)', inside or outside the MPC cluster."),
        "sectoral_cva_usd": datum(s["sectoral_cva_funding"], "partial", asof, ["fts1"], sect_note + (" Largest: " + top + "." if top else ""), by_cluster=bycl, flow_count=s["sectoral_cva_flow_count"]),
        "cva_usd": datum(s["cva_funding"], "partial", asof, ["fts1"], "Union of the MPC cluster and the CTP tag. Widest defensible FTS cash figure; still a floor because untagged sectoral cash is invisible."),
        "cva_pct_of_total": datum(s["cva_pct_of_total"], "partial", asof, ["fts1"], "cva_usd as a share of total plan funding."),
        "sectoral_cva_pct_of_total": datum(s["sectoral_cva_pct_of_total"], "partial", asof, ["fts1"], "sectoral_cva_usd as a share of total plan funding."),
        "mpc_pct_of_total": datum(s["mpc_pct_of_total"] if s["mpc_cluster_name"] else None, "yes" if s["mpc_cluster_name"] else "no", asof if s["mpc_cluster_name"] else "", ["fts1"], "MPC cluster funding as a share of total plan funding (single-cluster view)."),
        "cbpf_internal": s["cbpf_internal"],
        "caveat": "FTS records funding, not transfers to people, and only to first-level recipients. Sectoral cash depends on a modality tag that reporters apply unevenly."
    }

    # ---- fill empty v1 cells from FTS, flagged partial
    of = c["overall_funding"]["sectoral_cash_pct"]
    if of.get("available") == "no" and s["total_funding"]:
        c["overall_funding"]["sectoral_cash_pct"] = datum(s["sectoral_cva_pct_of_total"], "partial", asof, ["fts1"],
            "FTS proxy: CTP-tagged flows outside the MPC cluster (US$%.1fM) as a share of all plan funding. Vouchers are not separable from cash in this tag. A floor, see Method." % (s["sectoral_cva_funding"] / 1e6), usd=s["sectoral_cva_funding"])
    cb = s["cbpf_internal"]
    pf = c.get("pooled_funds", {})
    if pf.get("cbpf_exists") and cb["flow_count"] >= 10 and cb["total"]:
        if pf["mpc_pct"].get("available") == "no":
            pf["mpc_pct"] = datum(cb["mpc_pct"], "partial", asof, ["fts1"],
                "FTS proxy: the pooled fund's onward grants inside this plan (%d internal flows, US$%.1fM) tagged to the MPC cluster. The fund's own allocation reports may differ." % (cb["flow_count"], cb["total"] / 1e6), usd=cb["mpc"])
        if pf["cbpf_allocations_usd"].get("available") == "no":
            pf["cbpf_allocations_usd"] = datum(cb["total"], "partial", asof, ["fts1"],
                "FTS proxy: sum of the pooled fund's onward grants recorded inside this plan (%d internal flows). Not the fund's full allocation total." % cb["flow_count"])
        if pf["sectoral_cash_pct"].get("available") == "no":
            sect_cb = cb["cva"] - cb["mpc"] if cb["cva"] >= cb["mpc"] else 0
            pf["sectoral_cash_pct"] = datum(round(100.0 * sect_cb / cb["total"], 1), "partial", asof, ["fts1"],
                "FTS proxy: CTP-tagged pooled-fund grants outside the MPC cluster (US$%.1fM) as a share of the fund's grants inside the plan. Floor." % (sect_cb / 1e6), usd=sect_cb)

    # ---- research fragment
    frag = frag or {}
    for src in frag.get("sources", []):
        c["sources"].append(src)
    fr_ids = {x["id"] for x in frag.get("sources", [])}

    def clean_sids(sids):
        return [x for x in (sids or []) if x in fr_ids]

    co = frag.get("coordination") or {}
    c["coordination"] = {"label": co.get("label") or "Unknown", "ocha_plan": co.get("ocha_plan", ""), "unhcr_plan": co.get("unhcr_plan", ""),
                         "note": co.get("note", "") or "Not researched.", "source_ids": clean_sids(co.get("source_ids"))}

    cw = dict(frag.get("cwg_reliefweb") or {})
    # layer the scripted ReliefWeb Response read (data/rw/<id>.json) and curated overrides on top of the fragment
    rw = RW.get(c["id"]) or {}
    rw_sids = []
    if rw.get("exists"):
        cw["page_url"] = rw["page_url"]; cw["page_title"] = rw.get("page_title") or cw.get("page_title", "")
        ld = rw.get("latest_document") or rw.get("latest_item")
        if ld and ld.get("posted"):
            cw["page_last_updated"] = ld["posted"]
            cw["last_update_basis"] = "latest %s posted in the page's ReliefWeb feed: %s" % ((ld.get("format") or "item").lower(), ld.get("title", "")[:90])
        c["sources"].append({"id": "rw1", "title": (rw.get("page_title") or "Cash Working Group page") + " (ReliefWeb Response)", "publisher": "OCHA / ReliefWeb Response", "url": rw["page_url"], "date": rw["checked"], "accessed": rw["checked"]})
        rw_sids = ["rw1"]
    ov = OV.get(c["id"]) or {}
    for k in ("dashboard_url", "dashboard_name", "dashboard_last_updated", "dashboard_period", "co_chairs", "local_cochair", "contacts_basis"):
        if k in ov:
            cw[k] = ov[k]
    last = cw.get("page_last_updated") or ""
    dl = cw.get("dashboard_last_updated") or ""
    m_page = months_between(last, today) if last else None
    m_dash = months_between(dl, today) if dl else None
    chairs = cw.get("co_chairs") or []
    local_types = {"NNGO", "Government", "RCRC"}
    lc = cw.get("local_cochair")
    if lc not in ("yes", "no", "unknown"):
        lc = "yes" if any((x.get("actor_type") in local_types) for x in chairs) else ("no" if chairs else "unknown")
    c["cwg_reliefweb"] = {
        "page_url": cw.get("page_url", ""), "page_title": cw.get("page_title", ""),
        "page_last_updated": last, "last_update_basis": cw.get("last_update_basis", ""),
        "page_fresh_3m": (m_page is not None and m_page <= 3),
        "dashboard_url": cw.get("dashboard_url", ""), "dashboard_name": cw.get("dashboard_name", ""),
        "dashboard_last_updated": dl, "dashboard_period": cw.get("dashboard_period", ""),
        "dashboard_fresh_3m": (m_dash is not None and m_dash <= 3),
        "meeting_minutes_latest": cw.get("meeting_minutes_latest", ""),
        "co_chairs": [{"organisation": x.get("organisation", ""), "actor_type": x.get("actor_type", "Other"), "role": x.get("role", "")} for x in chairs],
        "local_cochair": lc, "contacts_basis": cw.get("contacts_basis", ""),
        "note": cw.get("note", ""), "source_ids": rw_sids + clean_sids(cw.get("source_ids")),
        "checked": today
    }

    cv = frag.get("cash_volumes") or {}

    def vol(key):
        d = cv.get(key) or {}
        av = d.get("available") if d.get("available") in ("yes", "partial", "no") else "no"
        if av != "no" and (d.get("value") in (None, "") or not clean_sids(d.get("source_ids"))):
            av = "no"
        return datum(d.get("value") if av != "no" else None, av, d.get("as_of", "") if av != "no" else "", clean_sids(d.get("source_ids")),
                     d.get("note", "") or ("Not found in CWG dashboards or CVA snapshots searched." if av == "no" else ""),
                     period=d.get("period", ""), source_type=d.get("source_type", ""))
    delivered = vol("cva_delivered_usd"); mpc_del = vol("mpc_delivered_usd"); sect_del = vol("sectoral_cva_delivered_usd")
    # "sectoral CVA, best available": CWG dashboard figure or FTS figure, whichever is higher, with the source named
    fts_sect = s["sectoral_cva_funding"]
    if sect_del["available"] != "no" and sect_del["value"] is not None and sect_del["value"] >= fts_sect:
        best = datum(sect_del["value"], sect_del["available"], sect_del["as_of"], sect_del["source_ids"],
                     "CWG/in-country figure (%s) is higher than FTS-tagged sectoral CVA funding (US$%.1fM). The two measure different things: delivered value vs funding." % (sect_del.get("period") or sect_del.get("source_type") or "dashboard", fts_sect / 1e6), source="in-country dashboard")
    else:
        best = datum(fts_sect, "partial", asof, ["fts1"],
                     ("FTS CTP-tagged sectoral CVA funding; " + ("higher than the in-country figure found (US$%.1fM, %s)." % (sect_del["value"] / 1e6, sect_del.get("period") or "") if sect_del["available"] != "no" and sect_del["value"] is not None else "no in-country sectoral figure found to compare.")), source="FTS")
    c["cash_volumes"] = {
        "mpc_funding_fts_usd": copy.deepcopy(c["fts_cva"]["mpc_usd"]),
        "sectoral_cva_best_usd": best,
        "cva_delivered_usd": delivered,
        "mpc_delivered_usd": mpc_del,
        "sectoral_cva_delivered_usd": sect_del,
        "caveat": "Funding (FTS) and delivered value (CWG dashboards) are different quantities with different periods and coverage. Do not add them, and compare them only with the notes in view."
    }

    fsps = []
    for x in frag.get("fsps") or []:
        if not x.get("name"):
            continue
        fsps.append({"name": x["name"], "type": x.get("type", "other"), "used_by": x.get("used_by") or [], "evidence": x.get("evidence", ""),
                     "website": x.get("website", ""), "logo_url": x.get("logo_url", ""), "logo_source": x.get("logo_source", ""), "source_ids": clean_sids(x.get("source_ids"))})
    c["fsps"] = fsps

    lc_d = datum(lc if lc != "unknown" else None, "yes" if lc in ("yes", "no") else "no", cw.get("page_last_updated") or today if lc != "unknown" else "", rw_sids + clean_sids(cw.get("source_ids")),
                 ("Chairs found: " + "; ".join("%s (%s)" % (x.get("organisation"), x.get("actor_type")) for x in chairs)) if chairs else "No chair or co-chair organisations found on the CWG page or in minutes.")
    c["localisation"] = {
        "framework": "IASC MPC scaling plan, objective 4 (local leadership and co-implementation)",
        "local_cochair": lc_d,
        "cva_to_local_pct": datum(s["local_actor_pct_of_cva"], "partial", asof, ["fts1"],
            "Indicator 4.2 proxy. Share of FTS cash funding (MPC cluster or CTP tag, US$%.1fM) whose first-level recipient is a local or national NGO/CSO or a national government body. FTS does not see sub-grants, so this understates money that reaches local actors through international intermediaries." % (s["cva_funding"] / 1e6), usd=s["local_actor_cva_funding"]),
        "all_funding_to_local_pct": datum(s["local_actor_pct_of_total"], "partial", asof, ["fts1"],
            "Share of all plan funding whose first-level recipient is a local or national actor (US$%.1fM). Same first-level caveat." % (s["local_actor_funding"] / 1e6), usd=s["local_actor_funding"]),
        "cbpf_cva_to_local_pct": datum(cb["local_actor_pct_of_cva"], "partial", asof, ["fts1"],
            "Second-level view: share of the pooled fund's cash grants (US$%.1fM) that went to local or national actors. Pooled-fund grants are the one onward layer FTS records." % (cb["cva"] / 1e6), usd=cb["local_actor_cva"]) if pf.get("cbpf_exists") and cb["flow_count"] >= 10 and cb["cva"] else datum(None, "no", "", [], "No pooled-fund cash grants recorded inside this plan on FTS." if pf.get("cbpf_exists") else "No country-based pooled fund."),
        "cbpf_all_to_local_pct": datum(cb["local_actor_pct"], "partial", asof, ["fts1"],
            "Share of all pooled-fund grants inside the plan (US$%.1fM) to local or national actors." % (cb["total"] / 1e6), usd=cb["local_actor"]) if pf.get("cbpf_exists") and cb["flow_count"] >= 10 and cb["total"] else datum(None, "no", "", [], "No pooled-fund grants recorded inside this plan on FTS." if pf.get("cbpf_exists") else "No country-based pooled fund."),
        "caveat": "FTS sees first-level recipients only; indicator 4.2 as defined (direct donor allocation to local partners) is therefore a floor. Chair roles come from public CWG pages and may be out of date."
    }
    c["last_researched"] = today
    c["researched_by"] = (c.get("researched_by") or "").replace("5 Nov 2026", "5-6 Nov 2026")
    return c


RW, OV = {}, {}


def main():
    global RW, OV
    today = datetime.date.today().isoformat()
    rwdir = os.path.join(DATA, "rw")
    if os.path.isdir(rwdir):
        for p in glob.glob(os.path.join(rwdir, "*.json")):
            r = json.load(open(p, encoding="utf-8"))
            if os.path.basename(p) == "overrides.json":
                OV = {k: v for k, v in r.items() if not k.startswith("_")}
            elif r.get("id"):
                RW[r["id"]] = r
    n = 0
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        c = json.load(open(p, encoding="utf-8"))
        fp = os.path.join(DATA, "fts", c["id"] + ".json")
        vp = os.path.join(DATA, "v2", c["id"] + ".json")
        if not os.path.exists(fp):
            print(c["id"], "no FTS file; skipped"); continue
        fts = json.load(open(fp, encoding="utf-8"))
        frag = json.load(open(vp, encoding="utf-8")) if os.path.exists(vp) else None
        c = merge(c, fts, frag, today)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2, ensure_ascii=False); f.write("\n")
        n += 1
        print("%-12s merged  fragment=%s  fsps=%d  cwg_page=%s  coord=%s" % (c["id"], "yes" if frag else "no", len(c["fsps"]), c["cwg_reliefweb"]["page_last_updated"] or "-", c["coordination"]["label"]))
    print("merged", n)


if __name__ == "__main__":
    main()
