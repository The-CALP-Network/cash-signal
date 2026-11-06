#!/usr/bin/env python3
"""Read each cash working group's public page on ReliefWeb Response and record what is visible:
latest posted items, dashboards (iframes), contact organisations and roles (never names or emails), events.

Writes data/rw/<id>.json. merge_v2.py prefers these over the research fragments when both exist.
Run: python3 -I build/rw_cwg_pull.py   (needs network access to response.reliefweb.int)
"""
import json, os, re, html, datetime, urllib.request, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "rw")
PAGES = {
    "afghanistan": "https://response.reliefweb.int/afghanistan/cash-voucher-working-group",
    "chad": "https://response.reliefweb.int/chad/cash-working-group",
    "drc": "https://response.reliefweb.int/democratic-republic-congo/cash-working-group",
    "mali": "https://response.reliefweb.int/mali/groupe-de-travail-cash",
    "mozambique": "https://response.reliefweb.int/mozambique/mozambique-cash-and-voucher-working-group",
    "niger": "https://response.reliefweb.int/niger/cash-working-group",
    "nigeria": "https://response.reliefweb.int/nigeria/cash-working-group",
    "opt": "https://response.reliefweb.int/palestine/palestine-cash-working-group",
    "somalia": "https://response.reliefweb.int/somalia/somalia-cash-working-group",
    "southsudan": "https://response.reliefweb.int/south-sudan/south-sudan-cash-working-group",
    "sudan": "https://response.reliefweb.int/sudan/cash-working-group",
    "syria": "https://response.reliefweb.int/syria/cash-working-group",
    "yemen": "https://response.reliefweb.int/yemen/cash-and-market",
}
MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
MONTHS.update({"janv": 1, "févr": 2, "fev": 2, "mars": 3, "avr": 4, "mai": 5, "juin": 6, "juil": 7, "août": 8, "aout": 8, "sept": 9, "déc": 12, "dec": 12})


def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (cash-signal build)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa
        return 0, ""


def text(s):
    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def iso(d):
    m = re.match(r"(\d{1,2})\s+([A-Za-zéû]+)\.?\s+(\d{4})", d.strip())
    if not m:
        return ""
    mon = MONTHS.get(m.group(2)[:4].lower()) or MONTHS.get(m.group(2)[:3].lower())
    return "%s-%02d-%02d" % (m.group(3), mon, int(m.group(1))) if mon else ""


def river(s):
    items = []
    for art in re.findall(r"<article class=\"hri-river__result\".*?</article>", s, flags=re.S):
        t = re.search(r"<h3 class=\"title\">\s*<a href=\"([^\"]+)\"[^>]*>(.*?)</a>", art, flags=re.S)
        f = re.search(r"<dd class=\"format[^\"]*\">(.*?)</dd>", art, flags=re.S)
        src = re.search(r"<dd class=\"source\">(.*?)</dd>", art, flags=re.S)
        d = re.search(r"<dd class=\"date posted\">(.*?)</dd>", art, flags=re.S)
        items.append({"title": text(t.group(2)) if t else "", "url": t.group(1) if t else "", "format": text(f.group(1)) if f else "",
                      "source": text(src.group(1)) if src else "", "posted": iso(text(d.group(1))) if d else ""})
    return items


def documents(s):
    """Documents the page lists directly (not the ReliefWeb river): title + any date in the block."""
    out = []
    for blk in re.findall(r"<(?:article|div) class=\"[^\"]*(?:node--type-document|rw-document|document)[^\"]*\".*?</(?:article|div)>", s, flags=re.S)[:40]:
        tt = re.search(r"<(?:h3|h4|a)[^>]*>(.*?)</(?:h3|h4|a)>", blk, flags=re.S)
        dd = re.search(r"(\d{1,2}\s+[A-Za-zéû]+\.?\s+\d{4})", text(blk))
        if tt:
            out.append({"title": text(tt.group(1))[:120], "date": iso(dd.group(1)) if dd else ""})
    return out


def contacts(s):
    """Organisation + role pairs from the contacts tab, read from the schema.org markup
    (Person > Organization name, Organization role). Names and emails are discarded."""
    res = []
    for person in re.findall(r"<article class=\"hid-contact\".*?(?=<article class=\"hid-contact\"|</div>\s*</div>\s*</div>\s*</div>)", s, flags=re.S):
        # a text block can hold several people: split on each <p><span itemprop="name">
        for blk in re.split(r"<p><span itemprop=\"name\">", person)[1:]:
            orgs = re.findall(r"<div itemscope itemtype=\"https://schema.org/Organization\">(.*?)</div>", blk, flags=re.S)
            org = role = ""
            for o in orgs:
                v = text(o)
                if not v:
                    continue
                if "itemprop=\"name\"" in o and not org:
                    org = v
                elif not role:
                    role = v
            if org or role:
                res.append({"organisation": org, "role": role})
    if res:
        return res
    # fallback: schema.org markup absent, use text and keep only organisation/role words after a known organisation
    t = text(s)
    for m in re.finditer(r"([A-Z][^@]{3,160}?)\s([A-Za-z0-9._-]+@[A-Za-z0-9.-]+)", t):
        chunk = m.group(1)
        m2 = re.search(r"((?:United Nations|UN |UNHCR|UNICEF|WFP|World Food|OCHA|IOM|FAO|UNDP|UNRWA|CashCap|NORCAP|REACH|IMPACT|Mercy Corps|Save the Children|Oxfam|NRC|Norwegian|Danish|IRC|International Rescue|CRS|Catholic|Concern|Action Against Hunger|ACF|Action Contre|CARE|World Vision|Plan International|ACTED|GiveDirectly|Red Cross|Red Crescent|Croix|Ministry|Minist|Government|Gouvernement|Federal|Consortium|Caritas|Relief International|Islamic Relief|Welthungerhilfe|GOAL|Medair|Tearfund|INTERSOS|COOPI|Première Urgence|Cordaid|Christian Aid|Agency|Organisation|Organization|Foundation|Association|Network|Programme|Fund).*)$", chunk)
        if m2:
            org_role = m2.group(1).strip()
            r = re.search(r"\s(?=(?:CWG|Cash|Co-?chair|Co-?Chair|Co-?lead|Co-?Lead|Chair|Coordinator|Coordinat|Information Management|IM |Officer|Lead|Focal|Technical|Head|Advisor|Adviser|Specialist|Manager|Deputy|Senior|Associate|Assistant|Point focal|Responsable|Chargé|Président|Analyst|Email))", org_role)
            if r:
                res.append({"organisation": org_role[:r.start()].strip(), "role": org_role[r.start():].strip()})
            else:
                res.append({"organisation": org_role, "role": ""})
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    today = datetime.date.today().isoformat()
    only = sys.argv[1:]
    for cid, url in PAGES.items():
        if only and cid not in only:
            continue
        code, s = fetch(url)
        rec = {"id": cid, "page_url": url, "checked": today, "http_status": code}
        if code != 200 or not s:
            rec["exists"] = False
            print("%-12s %s %s" % (cid, code, url)); json.dump(rec, open(os.path.join(OUT, cid + ".json"), "w"), indent=1, ensure_ascii=False); continue
        rec["exists"] = True
        t = re.search(r"<title>(.*?)</title>", s, flags=re.S)
        rec["page_title"] = text(t.group(1)).replace(" | ReliefWeb Response", "") if t else ""
        rec["river"] = river(s)
        rec["documents"] = documents(s)
        ifr = [u for u in re.findall(r"<iframe[^>]+src=\"([^\"]+)\"", s) if "googletagmanager" not in u]
        rec["iframes"] = ifr
        rec["dashboard_links"] = sorted(set(u for u in re.findall(r"href=\"([^\"]+)\"", s) if re.search(r"powerbi|tableau|data\.humdata|dashboard|app\.powerbi|arcgis|lookerstudio|datastudio", u, re.I)))
        # sub-pages
        for sub in ("contacts", "events", "reports"):
            c2, s2 = fetch(url.rstrip("/") + "/" + sub)
            if c2 == 200 and s2:
                if sub == "contacts":
                    rec["contacts"] = contacts(s2)
                elif sub == "events":
                    rec["events"] = [{"title": x["title"], "date": x["posted"]} for x in river(s2)][:10]
                    ev = re.findall(r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})", text(s2))
                    rec["event_dates"] = sorted(set(filter(None, (iso(x) for x in ev))))[-8:]
                else:
                    rec["reports_river"] = river(s2)[:30]
        # latest dates
        allitems = rec["river"] + rec.get("reports_river", [])
        dated = [x for x in allitems if x["posted"]]
        nonnews = [x for x in dated if "news" not in x["format"].lower()]
        latest = max(dated, key=lambda x: x["posted"]) if dated else None
        latest_doc = max(nonnews, key=lambda x: x["posted"]) if nonnews else None
        rec["latest_item"] = latest
        rec["latest_document"] = latest_doc
        docd = [d for d in rec["documents"] if d["date"]]
        rec["latest_listed_document"] = max(docd, key=lambda d: d["date"]) if docd else None
        json.dump(rec, open(os.path.join(OUT, cid + ".json"), "w"), indent=1, ensure_ascii=False)
        print("%-12s 200  river=%d docs=%d iframes=%d dash=%d contacts=%d latest=%s latest_doc=%s" % (
            cid, len(rec["river"]), len(rec["documents"]), len(ifr), len(rec["dashboard_links"]), len(rec.get("contacts", [])),
            latest["posted"] if latest else "-", latest_doc["posted"] if latest_doc else "-"))


if __name__ == "__main__":
    main()
