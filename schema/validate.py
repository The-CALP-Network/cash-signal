#!/usr/bin/env python3
"""Validate a Cash Signal country JSON against the schema's structure and rules."""
import json, sys, re

AVAIL = {"yes", "partial", "no"}
TOP = ["id","name","iso3","calp_region","last_researched","researched_by","plan","plan_2027",
       "modality_preference","cost_efficiency","hnrp_requirements","overall_funding","pooled_funds",
       "cash_feasibility","market_monitoring","cwg","ai_summary","rep_notes","sources"]
DATUM_GROUPS = {
  "plan": ["people_in_need","people_targeted","requirements_usd","funded_usd","funded_pct"],
  "modality_preference": ["cash_pct","vouchers_pct","in_kind_pct","other_pct"],
  "cost_efficiency": ["mpc","sectoral_cash","vouchers","in_kind_food"],
  "hnrp_requirements": ["mpc_pct","sectoral_cash_pct","vouchers_pct","total_cva_pct"],
  "overall_funding": ["mpc_pct","mpc_funded_pct_of_mpc_req","sectoral_cash_pct","vouchers_pct"],
  "pooled_funds": ["cbpf_allocations_usd","mpc_pct","sectoral_cash_pct","vouchers_pct"],
}
errs = []
def err(m): errs.append(m)

path = sys.argv[1]
try:
    d = json.load(open(path))
except Exception as e:
    print("INVALID JSON:", e); sys.exit(1)

for k in TOP:
    if k not in d: err(f"missing top-level key: {k}")
src_ids = {s.get("id") for s in d.get("sources", [])}
for s in d.get("sources", []):
    if not re.match(r"^https?://", s.get("url","")): err(f"source {s.get('id')} has no http URL")
    for k in ("id","title","url","accessed"):
        if not s.get(k): err(f"source {s.get('id')} missing {k}")

def check_datum(label, x):
    if not isinstance(x, dict): err(f"{label}: not an object"); return
    av = x.get("available")
    if av not in AVAIL: err(f"{label}: available must be yes|partial|no (got {av!r})")
    if av == "no" and x.get("value") not in (None, ""): err(f"{label}: available=no but value set")
    if av in ("yes","partial"):
        if x.get("value") in (None, ""): err(f"{label}: available={av} but value empty")
        if not x.get("source_ids"): err(f"{label}: available={av} but no source_ids")
        if not x.get("as_of"): err(f"{label}: available={av} but as_of empty")
    for sid in x.get("source_ids", []):
        if sid not in src_ids: err(f"{label}: unknown source id {sid}")
    v = x.get("value")
    if label.endswith("_pct") and isinstance(v,(int,float)) and not (0 <= v <= 100):
        err(f"{label}: percentage out of 0-100 ({v})")

for grp, keys in DATUM_GROUPS.items():
    g = d.get(grp, {})
    for k in keys:
        if k not in g: err(f"{grp}.{k} missing")
        else: check_datum(f"{grp}.{k}", g[k])

for blk in ("cash_feasibility","market_monitoring","cwg","plan_2027"):
    for sid in d.get(blk, {}).get("source_ids", []):
        if sid not in src_ids: err(f"{blk}: unknown source id {sid}")
if d.get("cash_feasibility",{}).get("exists") not in {"yes","no","unknown"}: err("cash_feasibility.exists must be yes|no|unknown")
if d.get("market_monitoring",{}).get("functional") not in {"yes","partial","no","unknown"}: err("market_monitoring.functional must be yes|partial|no|unknown")
if d.get("cwg",{}).get("exists") not in {"yes","no","unknown"}: err("cwg.exists must be yes|no|unknown")
if d.get("plan",{}).get("type") not in {"HNRP","HRP","Flash Appeal","RRP","Other","None"}: err("plan.type invalid")
if d.get("plan",{}).get("status") not in {"published","draft","not yet published","none"}: err("plan.status invalid")

ai = d.get("ai_summary", {})
n = len(ai.get("narrative","").split())
if not (90 <= n <= 220): err(f"ai_summary.narrative should be 120-180 words (got {n})")
if not ai.get("headline"): err("ai_summary.headline empty")
if not isinstance(ai.get("barriers"), list) or not ai.get("barriers"): err("ai_summary.barriers empty")
for cite in re.findall(r"\[(s\d+)\]", ai.get("narrative","")):
    if cite not in src_ids: err(f"narrative cites unknown source {cite}")
for k,v in d.get("rep_notes",{}).items():
    if not k.startswith("_") and v: err(f"rep_notes.{k} must be empty")
if "_comment" in d: err("remove top-level _comment")

if errs:
    print(f"{len(errs)} problem(s):"); [print(" -", e) for e in errs]; sys.exit(1)
yes = sum(1 for g,ks in DATUM_GROUPS.items() for k in ks if d[g][k]["available"]=="yes")
tot = sum(len(ks) for ks in DATUM_GROUPS.values())
print(f"OK — {d['name']}: {yes}/{tot} indicators available, {len(src_ids)} sources")
