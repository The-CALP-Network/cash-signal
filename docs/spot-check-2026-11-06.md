# Cash Signal v2 data check (15 country files, 6 Nov 2026)

Independent check of the new v2 blocks (coordination, fts_cva, cash_volumes, cwg_reliefweb, fsps, localisation). Method: FTS flows re-pulled from api.hpc.tools (flow?planId=N&limit=1000, all flows returned in one page: incoming + internal counts match meta) and recomputed from scratch; ReliefWeb Response pages and /contacts tabs opened with curl (Mozilla UA); cash volume and FSP sources opened with curl or WebFetch; coordination checked by WebSearch/WebFetch. No data files edited. No person names or emails recorded.

FTS recompute rules used: total = incoming, status != pledge; MPC = destination Cluster named Multi-Purpose Cash with behaviour single; sectoral CVA = method "Cash transfer programming (CTP)" and destination not an MPC cluster; CVA = MPC or CTP; local = destination organisation level "Local and National Non-State Actors" or national government of that country.

| Country | Field | Value | Verdict | Evidence |
|---|---|---|---|---|
| Sudan | fts_cva.total_funding_usd | 1,342,958,757 | CONFIRMED | Recomputed 1,342,958,757 over 630 incoming flows; equals FTS meta fundingTotal |
| Sudan | fts_cva.mpc_usd | 98,341,936 | CONFIRMED | Single-behaviour MPC cluster 98,341,936; shared-cluster view 100,089,194 matches the note's "US$100.1M" |
| Sudan | fts_cva.sectoral_cva_usd | 12,800,979 | CONFIRMED | CTP not in MPC = 12,800,979; ctp_usd 105,044,916 and cva_usd 111,142,915 also reproduce |
| Sudan | localisation.cva_to_local_pct | 0.0 | CONFIRMED | 0 of 111.1M CVA goes to a local/national first-level recipient |
| Sudan | localisation.all_funding_to_local_pct | 0.7 (USD 8,916,630) | CONFIRMED | 8,916,630 / 1,342,958,757 = 0.66% |
| Sudan | fts_cva.cbpf_internal | 187 flows, 368,377,246; mpc 51,715,000; ctp 108,424,842; local 4,749,714 | CONFIRMED | Internal flows sourced from pooled funds: 187 flows, all four figures reproduce exactly |
| Myanmar | fts_cva.total_funding_usd | 468,077,276 | CONFIRMED | Recomputed identical; equals FTS fundingTotal |
| Myanmar | fts_cva.mpc_usd | 58,408,549 | CONFIRMED | Single-cluster MPC identical |
| Myanmar | fts_cva.sectoral_cva_usd | 20,678,602 | CONFIRMED | CTP not in MPC identical (CTP total and CVA both 79,087,151) |
| Myanmar | localisation.cva_to_local_pct | 8.5 (USD 6,722,100) | CONFIRMED | 6,722,100 / 79,087,151 = 8.50% |
| Myanmar | localisation.all_funding_to_local_pct | 1.8 (USD 8,388,183) | CONFIRMED | 8,388,183 / 468,077,276 = 1.79% |
| Chad | fts_cva.total_funding_usd | 443,545,769 | CONFIRMED | Identical; equals FTS fundingTotal |
| Chad | fts_cva.mpc_usd | null (no MPC cluster) | CONFIRMED | No MPC destination cluster in any flow; computed 0 |
| Chad | fts_cva.sectoral_cva_usd | 5,287,511 | CONFIRMED | CTP-tagged flows 5,287,511 (also = cva_usd) |
| Chad | localisation.cva_to_local_pct | 0.0 | CONFIRMED | 0 of 5.29M to local/national recipients |
| Chad | localisation.all_funding_to_local_pct | 0.8 (USD 3,360,938) | CONFIRMED | 3,360,938 / 443,545,769 = 0.76% |
| Mozambique | fts_cva.total_funding_usd | 230,201,189 | CONFIRMED | Identical; equals FTS fundingTotal |
| Mozambique | fts_cva.mpc_usd | null (no MPC cluster) | CONFIRMED | No MPC destination cluster; computed 0 |
| Mozambique | fts_cva.sectoral_cva_usd | 7,295,039 | CONFIRMED | CTP-tagged flows identical |
| Mozambique | localisation.cva_to_local_pct | 0.0 | CONFIRMED | 0 of 7.30M |
| Mozambique | localisation.all_funding_to_local_pct | 0.0 | CONFIRMED | No incoming flow to a local/national first-level recipient (internal flows do have 8.6%, not in scope) |
| Somalia | fts_cva.total_funding_usd | 303,480,905 | CONFIRMED | Identical; equals FTS fundingTotal |
| Somalia | fts_cva.mpc_usd | 35,086,246 | CONFIRMED | Single-cluster MPC identical |
| Somalia | fts_cva.sectoral_cva_usd | 27,346,358 | CONFIRMED | CTP not in MPC identical |
| Somalia | localisation.cva_to_local_pct | 0.0 | CONFIRMED | 0 of 62.4M |
| Somalia | localisation.all_funding_to_local_pct | 0.9 (USD 2,810,088) | CONFIRMED | 2,810,088 / 303,480,905 = 0.93% |
| Sudan | cwg_reliefweb.page_last_updated | 2026-11-05 | CONFIRMED | Latest item in the page feed: OCHA analysis "Cash and Services in Sudan for ICCG", posted 5 Nov 2026. Feed is page-wide (also carries non-cash Sudan news), but the 5 Nov item is cash-specific |
| Sudan | cwg_reliefweb.co_chairs | OCHA (non-prog.), CashCap (prog.), WFP (prog.) | CONFIRMED | /contacts lists exactly these three organisations and roles, plus an OCHA cash coordination officer not recorded |
| Sudan | cwg_reliefweb.dashboard_url | Power BI link | CONFIRMED | HTTP 200 text/html (shell page only; does not prove the report loads) |
| Sudan | cwg_reliefweb.note | "response.reliefweb.int/sudan CWG page could not be fetched" | MISMATCH | Page fetches fine (HTTP 200) and the same record cites contents and contacts from it; note is stale and contradicts contacts_basis |
| South Sudan | cwg_reliefweb.page_last_updated | 2026-09-02 | CONFIRMED | Newest item in feed is dated 2 Sep 2026 (others 20 and 22 Jul 2026) |
| South Sudan | cwg_reliefweb.co_chairs | OCHA, IOM, CRS, ADA (trainee seat), CashCap TA | CONFIRMED | /contacts lists these five with these roles |
| South Sudan | cwg_reliefweb.dashboard_url / note | Power BI link; "minutes listed to 25 Sep 2025" | PLAUSIBLE | URL returns HTTP 200 text/html. Note is stale: the page feed now lists minutes of the 29 Jan 2026 meeting |
| Nigeria | cwg_reliefweb.page_last_updated | 2026-10-14 | CONFIRMED | Newest feed item posted 14 Oct 2026 |
| Nigeria | cwg_reliefweb.co_chairs | OCHA (lead), Caritas Germany (NE technical co-lead) | CONFIRMED | /contacts lists exactly these two organisations and roles |
| Nigeria | cwg_reliefweb.dashboard_url | Power BI link | CONFIRMED | HTTP 200 text/html (shell only) |
| Somalia | cwg_reliefweb.page_last_updated | 2026-10-14 | CONFIRMED | Newest feed items posted 14 Oct 2026 |
| Somalia | cwg_reliefweb.co_chairs | WFP (chair) | PLAUSIBLE | /contacts shows only a WFP chair and a WFP IMO, so the record matches the page. The page's own Nov 2024 minutes still mention an OCHA co-chair, so the structure may be incomplete or have changed |
| Somalia | cwg_reliefweb.dashboard_url | Power BI link | CONFIRMED | HTTP 200 text/html (shell only) |
| Sudan | coordination.unhcr_plan | "none (Sudan is not one of the seven asylum countries)" | MISMATCH | The seven-country Regional RRP claim is right (CAR, Chad, Egypt, Ethiopia, Libya, South Sudan, Uganda; UNHCR-led). But a "Sudan Country Refugee Response Plan (CRP) January-December 2026" exists on UNHCR's portal (published 17 Mar 2026), and HNRP part 4 refers to Sudan's 2026 CRRP developed with the Commission for Refugees and 19 partners. Lead agency not stated on pages opened (UNHCR inferred from hosting). Label should not be OCHA only with plan "none" |
| South Sudan | coordination.unhcr_plan | South Sudan CRRP 2026 plus regional RRP chapter | CONFIRMED | UNHCR portal page "South Sudan Country Refugee Response Plan (CRRP) - 2026", published 13 Jan 2026; South Sudan is one of the seven RRP countries. Lead agency not stated on the page, inferred from hosting (record says so) |
| Chad | coordination.unhcr_plan | Sudan Regional RRP 2026 (Chad one of seven) | CONFIRMED | UN News/AllAfrica: appeal by UNHCR with 123 partners for seven countries incl. Chad |
| Nigeria | coordination.unhcr_plan | none | UNVERIFIABLE | No 2026 Nigeria-situation RRP found, but UNHCR's situation page could not be filtered to confirm the absence of a 2026 plan |
| Sudan | cash_volumes.cva_delivered_usd | 50,000,000 (Q1 2025) | CONFIRMED | OCHA Eastern Africa Q1 overview: "Sudan ... $50.0 million", 1 Jan-31 Mar 2025 |
| Somalia | cash_volumes.cva_delivered_usd | 36,300,000 (Q1 2025) | CONFIRMED | Same report: Somalia $36.3 million. Quarterly only, record says so |
| Mozambique | cash_volumes.cva_delivered_usd | 27,900,000 (2025) | CONFIRMED | OCHA overview 31 Dec 2025: 26 partners, US$27.9M, 904,000 people, nine provinces; vouchers 67/19/14 percent; cyclone 12M, conflict 9M, drought 4.5M |
| Yemen | cash_volumes.cva_delivered_usd | 48,570,000 (Jan-Jun 2025) | CONFIRMED | OCHA snapshot: 58 partners, USD 48.57 million, Jan-Jun 2025 |
| Afghanistan | cash_volumes.cva_delivered_usd | 152,700,000 (2025, prelim.) | CONFIRMED | HNRP 2026 CVA overview: CWG partners reached 16.6M people, $152.7M by September 2025, preliminary |
| Niger | cash_volumes.cva_delivered_usd | 31,000,000 (Jan-Dec 2025) | UNVERIFIABLE | Cited hub page (response.reliefweb.int/niger) shows only a "Intervention en transfert monetaire" link and no 17.3bn FCFA or USD 31M text, in either the page=0 or default URL. Figure may sit behind the dashboard |
| Sudan | fsps: Bankak | bank, logo bankofkhartoum.com | PLAUSIBLE | CGAP: Bankak app facilitated 50M+ transactions, surcharges up to 20%; the page does not say it delivers humanitarian cash, the record admits no agency named. Logo HTTP 200 image/png |
| Sudan | fsps: MTN Sudan Fintech | mobile money, used by Mercy Corps | CONFIRMED | ALNAP case study (WebFetch): pilot delivered in Gedaref with MTN Sudan Fintech, SDG 45,800 to 25 displaced households. curl got 404 but WebFetch read it. Logo HTTP 200 image/png |
| Sudan | fsps: Cashi, RedRose | fintech, used by CORE, NIDAA | PLAUSIBLE | CALP article names both as partners for cash distribution in Khartoum; "FSP" role implied not stated. curl returned 403, read via WebFetch. No logo_url |
| Chad | fsps: Moov Money | mobile money, logo moov-africa.td | CONFIRMED | Two articles: 2021 World Bank safety-net payment to 22,000 households, and Jun 2022 emergency transfers to refugees and hosts via PARCA (government/World Bank funded). Note these are government/World Bank programmes, not NGO humanitarian cash. Logo HTTP 200 image/png |
| Myanmar | fsps: Wave Money | mobile money | CONFIRMED | NextBillion: WFP works with Wave Money for e-wallet transfers to 284 households. Article is old (circa 2016-17), no date in the record's evidence |
| Yemen | fsps: YCash | fintech | CONFIRMED | FinDev Gateway: National Cash Transfer Co. (YCash) launched as first licensed humanitarian-transfers company |
| South Sudan | fsps: MTN, Zain | mobile money | PLAUSIBLE | GSMA blog: m-Gurush and Nilepay in partnership with Zain (2019); MTN "recently began" mobile money; blog says mobile money lets development organisations distribute cash assistance. "MoMo" brand not on page. curl 403, read via WebFetch |
| Logos (11 with logo_url) | fsps.logo_url | Hesab, Moov, Express Union, Western Union, Ecobank, Vodacom, OMT, MTN SS, Bank of Khartoum, MTN Sudan | CONFIRMED | All HTTP 200; content-type image/png for Hesab, Moov, Express Union, Bank of Khartoum, MTN Sudan; image/svg+xml for Western Union, Ecobank, Vodacom, OMT, MTN South Sudan |
| South Sudan | fsps.logo_url (Zain) | ss.zain.com .../ZN_LOGO_SILVER-CMYK.png | UNVERIFIABLE | HTTP 429 text/html on two tries (rate limit), so not confirmed either way |

## Verdict counts

58 rows (the logo row groups 10 URLs): CONFIRMED 48, PLAUSIBLE 5, MISMATCH 2, UNVERIFIABLE 3. All 28 FTS rows reproduced exactly.

## Recommended fixes

1. Sudan coordination: replace "unhcr_plan: none" and the OCHA-only label. A Sudan Country Refugee Response Plan 2026 exists (UNHCR portal, 17 Mar 2026; HNRP part 4 cites it). State that UNHCR leadership is inferred from hosting unless the PDF confirms it.
2. Sudan cwg_reliefweb.note: delete "could not be fetched". The page and contacts tab load and the same record uses them.
3. South Sudan cwg_reliefweb.note: update "minutes listed to 25 Sep 2025"; the page now lists the 29 Jan 2026 minutes.
4. Niger cash_volumes.cva_delivered_usd (USD 31M, 17.3bn FCFA): the cited hub page contains no such text. Either cite the actual 4W PDF/dashboard that shows it, or set available to no.
5. Somalia co_chairs: contacts tab lists only WFP; add a note that earlier minutes show an OCHA co-chair, or re-check, so the localisation "no local co-chair" is not read as a full structure.
6. Chad Moov Money evidence: both articles are government/World Bank social-protection or refugee programmes. Add that qualifier, or find an NGO/UN humanitarian use, before labelling it a humanitarian FSP.
7. Myanmar Wave Money: cite the date of the WFP pilot; the evidence is several years old.
8. Cash volumes with a quarterly period (Sudan, Somalia, Yemen half-year) should not be shown beside annual figures (Mozambique, Afghanistan) without the period label in the UI.
9. Zain logo: re-test later (HTTP 429 may be transient); consider hosting logos locally since several third-party sites throttle or block hotlinking.
10. Dashboard checks only prove the Power BI shell responds with HTTP 200, not that the report loads or is current; keep dashboard_last_updated empty rather than inferring.
