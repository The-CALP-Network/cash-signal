#!/usr/bin/env python3
"""Pull cash-related funding figures for every plan in data/*.json from the OCHA FTS public API.

Writes data/fts/<country id>.json. Nothing here is merged into the country records automatically;
merge_v2.py does that so every derived figure keeps its source id, as-of date and caveat.

What is computed per plan (incoming flows only, i.e. money entering the plan; FTS "single" view):
  total_funding            all incoming funding (matches the FTS plan summary)
  mpc_cluster_funding      flows whose destination cluster is Multi-Purpose Cash (single-cluster / destination view)
  ctp_funding              flows whose FTS "method" is "Cash transfer programming (CTP)": the modality tag donors set
  ctp_in_mpc               CTP-tagged flows inside the MPC cluster
  sectoral_cva_funding     CTP-tagged flows outside the MPC cluster = sectoral CVA as FTS can see it
  cva_funding              MPC cluster OR CTP tag (union): the widest defensible "cash" figure
  local_actor shares       destination organisation level "Local and National Non-State Actors" or
                           "National and Sub-National State Actors" (recipient country only): first-level recipients only
  cbpf (internal flows)    the country-based pooled fund's onward grants inside the plan: MPC share and local-actor share

Run: python3 -I build/fts_pull.py            (needs network access to api.hpc.tools)
"""
import json, os, sys, glob, datetime, urllib.request, urllib.parse, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "fts")
API = "https://api.hpc.tools/v1/public/fts/flow"
CTP = "Cash transfer programming (CTP)"
import re
MPC_RE = re.compile(r"multi[\s-]*purpose\s*cash|transferts?\s+d.espèces\s+à\s+usages?\s+multiples|usages multiples", re.I)
LOCAL_LEVELS = {"Local and National Non-State Actors", "National and Sub-National State Actors"}
LOCAL_SUBTYPES = {"Local NGOs/CSOs", "National NGOs/CSOs", "National Governments", "Local Governments", "National Red Cross/Red Crescent Societies", "Red Cross/Red Crescent National Societies"}


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "cash-signal-build"}), timeout=120) as r:
                return json.load(r)
        except Exception as e:  # noqa
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


def flows_for_plan(pid):
    out, page = [], 0
    url = API + "?" + urllib.parse.urlencode({"planId": pid, "limit": 1000})
    d = get(url)
    data = d["data"]
    out.extend(data.get("flows", []))
    nxt = (d.get("meta") or {}).get("nextLink")
    while nxt:
        page += 1
        d = get(nxt)
        out.extend(d["data"].get("flows", []))
        nxt = (d.get("meta") or {}).get("nextLink")
    return out, {k: v for k, v in data.items() if k != "flows"}


def dest(f, t):
    return [o for o in f.get("destinationObjects", []) or [] if o.get("type") == t]


def src(f, t):
    return [o for o in f.get("sourceObjects", []) or [] if o.get("type") == t]


def is_mpc(f, single_only=True):
    """Destination cluster is the plan's multi-purpose cash cluster. single_only matches FTS's
    single-cluster (destination) view; shared flows (one grant split across clusters) are excluded."""
    for o in dest(f, "Cluster"):
        if MPC_RE.search(o.get("name") or "") and (not single_only or o.get("behavior") != "shared"):
            return True
    return False


def is_ctp(f):
    return f.get("method") == CTP


def is_local_dest(f, country_name):
    """True when at least one destination organisation is a local/national actor of the recipient country.
    Governments are counted only when the organisation name contains the country name (donor governments
    also carry the 'National and Sub-National State Actors' level)."""
    for o in dest(f, "Organization"):
        lv, st = set(o.get("organizationLevels") or []), set(o.get("organizationSubTypes") or [])
        if "Local and National Non-State Actors" in lv or st & {"Local NGOs/CSOs", "National NGOs/CSOs"}:
            return True
        if "National and Sub-National State Actors" in lv and country_name and country_name.split()[0].lower() in (o.get("name") or "").lower():
            return True
    return False


def is_cbpf_source(f):
    return any("Country-based UN Pooled Funds" in (o.get("organizationSubTypes") or []) for o in src(f, "Organization"))


def summarise(flows, country_name):
    # pledges are not funding (FTS excludes them from fundingTotal)
    inc = [f for f in flows if f.get("boundary") == "incoming" and f.get("status") != "pledge"]
    internal = [f for f in flows if f.get("boundary") == "internal" and f.get("status") != "pledge"]
    mpc_shared = [f for f in inc if is_mpc(f, single_only=False)]
    amt = lambda L: int(sum(f.get("amountUSD") or 0 for f in L))  # noqa
    total = amt(inc)
    mpc = [f for f in inc if is_mpc(f)]
    ctp = [f for f in inc if is_ctp(f)]
    ctp_mpc = [f for f in ctp if is_mpc(f)]
    sect = [f for f in ctp if not is_mpc(f)]
    cva = [f for f in inc if is_mpc(f) or is_ctp(f)]
    local_all = [f for f in inc if is_local_dest(f, country_name)]
    local_cva = [f for f in cva if is_local_dest(f, country_name)]
    latest = max((f.get("date") or "")[:10] for f in inc) if inc else ""
    # sectoral CVA by cluster
    bycl = {}
    for f in sect:
        for o in dest(f, "Cluster"):
            bycl[o.get("name")] = bycl.get(o.get("name"), 0) + (f.get("amountUSD") or 0)
    # CBPF onward grants (internal flows whose source is the country-based pooled fund)
    cb = [f for f in internal if is_cbpf_source(f)]
    cb_total = amt(cb)
    cb_mpc = amt([f for f in cb if is_mpc(f)])
    cb_ctp = amt([f for f in cb if is_ctp(f)])
    cb_cva = amt([f for f in cb if is_mpc(f) or is_ctp(f)])
    cb_local = amt([f for f in cb if is_local_dest(f, country_name)])
    cb_local_cva = amt([f for f in cb if (is_mpc(f) or is_ctp(f)) and is_local_dest(f, country_name)])
    pct = lambda a, b: round(100.0 * a / b, 1) if b else None  # noqa
    return {
        "total_funding": total,
        "flow_count_incoming": len(inc),
        "latest_flow_date": latest,
        "mpc_cluster_funding": amt(mpc),
        "mpc_cluster_funding_shared_view": amt(mpc_shared),
        "mpc_cluster_name": next((o.get("name") for f in mpc_shared for o in dest(f, "Cluster") if MPC_RE.search(o.get("name") or "")), None),
        "ctp_funding": amt(ctp),
        "ctp_in_mpc": amt(ctp_mpc),
        "sectoral_cva_funding": amt(sect),
        "sectoral_cva_by_cluster": {k: int(v) for k, v in sorted(bycl.items(), key=lambda x: -x[1])},
        "sectoral_cva_flow_count": len(sect),
        "cva_funding": amt(cva),
        "cva_pct_of_total": pct(amt(cva), total),
        "sectoral_cva_pct_of_total": pct(amt(sect), total),
        "mpc_pct_of_total": pct(amt(mpc), total),
        "local_actor_funding": amt(local_all),
        "local_actor_pct_of_total": pct(amt(local_all), total),
        "local_actor_cva_funding": amt(local_cva),
        "local_actor_pct_of_cva": pct(amt(local_cva), amt(cva)),
        "cbpf_internal": {
            "flow_count": len(cb), "total": cb_total, "mpc": cb_mpc, "ctp": cb_ctp, "cva": cb_cva,
            "mpc_pct": pct(cb_mpc, cb_total), "cva_pct": pct(cb_cva, cb_total),
            "local_actor": cb_local, "local_actor_pct": pct(cb_local, cb_total),
            "local_actor_cva": cb_local_cva, "local_actor_pct_of_cva": pct(cb_local_cva, cb_cva)
        }
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    today = datetime.date.today().isoformat()
    only = sys.argv[1:]
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        c = json.load(open(p, encoding="utf-8"))
        if only and c["id"] not in only:
            continue
        pid = c.get("plan", {}).get("fts_plan_id")
        if not pid:
            print(c["id"], "no fts_plan_id; skipped"); continue
        flows, meta = flows_for_plan(pid)
        s = summarise(flows, c["name"])
        rec = {"id": c["id"], "plan_id": pid, "plan_name": c["plan"]["name"], "pulled": today,
               "api": API + "?planId=%d" % pid, "fts_page": "https://fts.unocha.org/plans/%d/summary" % pid,
               "meta": meta, "summary": s}
        with open(os.path.join(OUT, c["id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1, ensure_ascii=False)
        print("%-12s plan %d  total %7.1fM  MPC %6.1fM  CTP %6.1fM  sectoral-CVA %5.1fM (%d flows)  local %4.1f%% of total, %4.1f%% of CVA  CBPF-internal %d flows MPC %s%%" % (
            c["id"], pid, s["total_funding"] / 1e6, s["mpc_cluster_funding"] / 1e6, s["ctp_funding"] / 1e6, s["sectoral_cva_funding"] / 1e6,
            s["sectoral_cva_flow_count"], s["local_actor_pct_of_total"] or 0, s["local_actor_pct_of_cva"] or 0, s["cbpf_internal"]["flow_count"], s["cbpf_internal"]["mpc_pct"]))


if __name__ == "__main__":
    main()
