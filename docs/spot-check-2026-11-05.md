# Cash Signal data check (15 country files, 5 Nov 2026)

Method: FTS figures re-pulled from api.hpc.tools (plan and flow?groupby=cluster, saved in check/raw/). Survey and web sources opened with curl/pdftotext or WebFetch. No data files edited.

| Country | Field | Value | Verdict | Evidence |
|---|---|---|---|---|
| Afghanistan | plan.requirements_usd | 1,714,181,496 | CONFIRMED | FTS totalRevisedReqs identical |
| Afghanistan | plan.funded_pct | 32.6 | CONFIRMED | 559,667,488 / 1,714,181,496 = 32.65 |
| Afghanistan | modality_preference.cash_pct | 65 | CONFIRMED | HNRP s1: "65 per cent ... preferring cash or a combination of cash and in-kind"; not cash alone, survey unnamed (data note says so) |
| Afghanistan | overall_funding.mpc_funded_pct_of_mpc_req | 182.8 | PLAUSIBLE | 26,883,736 / 14,709,848 matches, but only on FTS report3 (shared flows counted); report2 gives 19.2M = 130.6%. Basis inconsistent, see fix 1 |
| Chad | plan.requirements_usd | 986,069,627 | CONFIRMED | FTS plan 1501 identical |
| Chad | hnrp_requirements.mpc_pct | 0.18 (USD 1,821,169) | CONFIRMED | FTS TEUM cluster requirement 1,821,169 |
| Chad | cwg.leads | Govt/MASSAH, OCHA, Oxfam, Chad Red Cross | CONFIRMED | s4 PDF p.11: transition to MASSAH as permanent lead, supported by OCHA, Oxfam, Chad Red Cross |
| Chad | cash_feasibility | Croix-Rouge du Tchad 2025 | CONFIRMED | Title, author, year match on cash-hub page. Scope is migrants in transit only, not a national study |
| DRC | modality_preference.cash_pct | 70 (vouchers 7, in-kind 59, services 18) | CONFIRMED | REACH AAP factsheet: physical cash 70, in-kind food 59, services 18, vouchers 7. South Kivu and Tanganyika only, 2022 |
| DRC | overall_funding.mpc_funded_pct_of_mpc_req | 47.4 | PLAUSIBLE | 52,385,483 / 110,528,619 matches report3; report2 gives 16,297,373 = 14.7%. Three-fold spread, see fix 1 |
| DRC | cwg.leads | OCHA, GiveDirectly (programmatic), REACH support | CONFIRMED | NORCAP vacancy: programmatic co-chair reports to GiveDirectly; partners GiveDirectly, OCHA, NRC. REACH role not seen |
| DRC | plan.requirements_usd | 2,132,641,156 | CONFIRMED | FTS plan 1509 identical |
| Lebanon | plan.requirements_usd | 1,620,530,000 | CONFIRMED | UNHCR funding update: LRP appeal 1,620.53M |
| Lebanon | plan.funded_pct | 27 | CONFIRMED | Same table: 431.45M received, 27% (39% with carry-over) |
| Lebanon | modality_preference.cash_pct | 75 | CONFIRMED | REACH MSNA 2022 AAP: physical cash 75, in-kind 24, services 14 |
| Lebanon | cwg.leads | UNHCR, WVI, MoSA | CONFIRMED | Aug 2026 minutes list "LCWG Co-chairs": MoSA, UNHCR, WVI |
| Lebanon | overall_funding.mpc_funded_pct_of_mpc_req | 24.5 | CONFIRMED | 32.13+56.71+48.07 = 136.9M over 321.5+134+103.96 = 559.5M. Mixes three appeals and is the whole CWG sector, see fix 5 |
| Mali | hnrp_requirements.mpc_pct | 5.3 | CONFIRMED | FTS TEUM 30,718,088 / 577,866,412 |
| Mali | modality_preference.cash_pct | 90 | UNVERIFIABLE | Cited ReliefWeb HNRP page returned 404 to curl and failed in WebFetch; study not located. Data note already flags it |
| Mali | cash_feasibility | Plan International 2022 | CONFIRMED | Title, author, Aug 2022 fieldwork, 225 traders, 785 FGD all match |
| Mali | market_monitoring | ICSM Dec 2025 | CONFIRMED | Factsheet: 21 markets, 1,140 traders, 33 items, collected 9-19 Dec 2025. CWG minutes: "145 sur 445 marchés" |
| Mozambique | plan.funded_pct | 43.1 | CONFIRMED | 230,057,858 / 534,342,584 = 43.05; both FTS-identical |
| Mozambique | modality_preference.cash_pct | 69 | PLAUSIBLE | Bulletin lists 69 / 65 / 21 under physical cash / in-kind food / infrastructure, but labels and numbers are separated in the PDF text, so pairing is by order. Data note says so |
| Myanmar | hnrp_requirements.mpc_pct | 9.6 | CONFIRMED | FTS 85,428,554 / 889,600,798 |
| Myanmar | overall_funding.mpc_funded_pct_of_mpc_req | 131.8 | PLAUSIBLE | 112,620,297 / 85,428,554 is report3; report2 gives 58,408,549 = 68.4%. Over 100% and basis-dependent, see fix 1 |
| Niger | plan.requirements_usd / mpc_pct | 675,619,589 / 0.2 | CONFIRMED | FTS plan 1513: total identical, TEUM 1,256,000 |
| Niger | cash_feasibility | REACH/MSCWG 2020 | CONFIRMED | Study opened: Tillabéri and Tahoua, 2020. Key informants: 80% (Tillabéri) and 50% (Tahoua) said communities prefer in-kind |
| Nigeria | plan.requirements_usd | 516,399,423 | CONFIRMED | FTS plan 1508 identical; no MPC requirement object exists, as the record says |
| Nigeria | cwg.leads | OCHA, Federal Ministry, CRS (NE) | PLAUSIBLE | s4 is the 2025 HNRP; only the NE co-chair (OCHA and CRS) was seen. National co-lead by the ministry not confirmed. Stale source |
| oPt | plan.requirements_usd | 4,064,305,808 | CONFIRMED | FTS plan 1510 identical |
| oPt | modality_preference.cash_pct | 75 | PLAUSIBLE | Flash Appeal: "75 to 84 per cent ... unrestricted cash". Dashboard shows the lower bound as a point value |
| Somalia | modality_preference.cash_pct | 78 (in-kind 78, other 20) | PLAUSIBLE | MSNA Oct 2025 factsheet text shows "78 78 20" chart values and a select-multiple note; label order not machine-readable |
| Somalia | hnrp_requirements.mpc_pct | 11.4 | CONFIRMED | FTS Multi Purpose Cash 97,000,000 / 852,000,000 |
| Somalia | cwg.leads | WFP, Concern, OCHA | PLAUSIBLE | CALP page names Mary Karanja and Kaitlynn Scott as co-leads; organisations only inferable from email domains (WFP, Concern). OCHA co-chair comes from a Nov 2024 ReliefWeb minute |
| South Sudan | modality_preference.cash_pct | 52 | CONFIRMED | HNRP p.22: "52 per cent ... preferred cash over in-kind", 2025 ISNA |
| South Sudan | cwg.leads | IOM, IRC, Mercy Corps, UNICEF, WFP, Save the Children | PLAUSIBLE | CALP ?p=941 lists IOM coordinator and co-chair, six co-leads as given. The other CALP page names a CashCap coordinator and unnamed co-leads. Undated, conflicting |
| South Sudan | cash_feasibility | REACH Aweil North | CONFIRMED | Factsheet opened. Header says May 2025; record says April 2025 (URL says April). Minor |
| Sudan | overall_funding.mpc_funded_pct_of_mpc_req | 81.0 | PLAUSIBLE | 98,341,936 / 121,347,117 = 81.0 on report2; report3 gives 159.2M = 131%. Requirement 121.3M confirmed on HNRP s3 |
| Sudan | cash_feasibility | 2021 analysis | CONFIRMED | Title and 2021 (from image filename); author not stated, as the record says |
| Syria | modality_preference.cash_pct | 85 | MISMATCH | HNRP: cash-based assistance is the "top priority" for 85% of respondents. That is a priority-need answer, not a modality preference. Record note concedes this but the field is cash_pct |
| Syria | cash_feasibility | CashCap + CWGs 2025 | CONFIRMED | Title, authors, 25 Feb 2025 match |
| Yemen | plan.funded_pct / requirements | 23.4 / 2,162,563,336 | CONFIRMED | FTS plan 1520 identical; 506.1/2162.6 = 23.4 |
| Yemen | market_monitoring | REACH JMMI Feb 2026 | CONFIRMED | Deck: presented to CMWG 7 Apr 2026, data collected first week of month |

## Sweeps without opening sources

- FTS-derived as_of: all 15 files carry a 2026 date on requirements, funded_usd, funded_pct and the two overall_funding MPC fields. No stale dates.
- Arithmetic: funded_pct matches funded_usd/requirements within 1 point in all 15. mpc_pct matches usd/requirements in all files that give usd. No MPC USD exceeds plan requirements. No modality value is outside 0-100.
- Over 100 where it perhaps should not be: Afghanistan 182.8 and Myanmar 131.8 (MPC funded as percent of MPC requirement).
- Source ids: every [sN] in all 15 narratives exists in sources[].
- Narrative citations checked for Mali, Nigeria, Sudan, Somalia:
  - Mali: figures and CWG/ICSM claims are supported. The 90% sentence is attributed to the gDCF analysis with [s7]; s7 would not open, but the sentence already says it is unverified.
  - Nigeria: "$516.4m", "$367.7m", "about 71%", "over a third unassigned" (136.2/367.7 = 37%) and "no 2026 MPC requirement" all check against FTS. The co-leadership sentence cites [s4][s5][s7] but s4 is the 2025 plan. The GTS voucher-versus-cash claim [s6] was not opened.
  - Sudan: $121.3M, 1.0M households, 360,000 SDG, three months all in [s3]. 81% vs 46.9% supported by [s16]. Claims on [s14] (50 of 57 localities, 95%) not opened.
  - Somalia: 78/78 in [s7] fits. WFP and Concern co-lead sentence cites [s9], which names people, not organisations. "No MPC-tagged projects at the pooled fund" [s6] not opened.

## Fix before showing anyone

1. MPC funding basis is inconsistent. Afghanistan, DRC, Myanmar, Syria and Yemen use FTS report3 (includes shared-cluster flows); South Sudan, Sudan, oPt and Lebanon use report2 (single-cluster only). The two views differ a lot, so country comparisons are not like-for-like. Same-basis (report2) values from the pulled data:

   | Country | report2 funded (USD) | report2 % of MPC req | Dashboard now |
   |---|---|---|---|
   | Afghanistan | 19,204,278 | 130.6 | 182.8 |
   | DRC | 16,297,373 | 14.7 | 47.4 |
   | Myanmar | 58,408,549 | 68.4 | 131.8 |
   | Syria | 36,642,452 | 20.0 | 38.8 |
   | Yemen | 35,723,129 | 29.8 | 32.1 |
   | Sudan | 98,341,936 | 81.0 | 81.0 |
   | South Sudan | 15,724,265 | 46.9 | 46.9 |
   | oPt | 46,413,981 | 7.8 | 7.8 |

   Pick one basis (report2 is the conservative one) and apply it everywhere, or show both. The overall_funding.mpc_pct share needs the same treatment. Source for all: https://api.hpc.tools/v1/public/fts/flow?planId=<id>&groupby=cluster. Afghanistan stays above 100 even on report2, so show "over 100%, not meaningful" rather than 182.8.
2. Syria modality_preference.cash_pct = 85: move out of modality preference, or relabel as "cash is top priority need (85%)". Do not plot it beside survey modality shares.
3. Mali modality_preference.cash_pct = 90: unverified. Hide it or badge it "unverified, relayed" until the HNRP or CWG study is opened.
4. oPt cash_pct = 75: display as "75-84%" (Flash Appeal 2026), not 75.
5. Lebanon mpc_funded_pct_of_mpc_req = 24.5 blends LRP, Flash Appeal and Addendum CWG sector lines, while plan.funded_pct (27) and requirements are LRP-only. On the LRP alone the CWG sector is 32.13M / 321.5M = 10%. Label the basis on the card or use the LRP-only figure (UNHCR funding update, data.unhcr.org/en/documents/download/124737).
6. Nigeria cwg.leads: sourced from the 2025 HNRP. Mark as dated. Somalia and South Sudan leads: undated CALP pages, names without organisations (Somalia) or conflicting (South Sudan); show with "unconfirmed".
7. Sudan: the 2026 HNRP page s3 says "over 90 per cent of affected households identifying cash as the most dignified" form of support, and consultations ranked cash top. The record has no cash_pct. Optional to add, as a consultation figure, not survey modality share.
8. Chad cash_feasibility is a migrants-in-transit study, not national; South Sudan feasibility date is May 2025 per the document header. Mozambique 69/65/21 label pairing rests on order only.

## Counts (rows in table: 43)

CONFIRMED 31, PLAUSIBLE 10, MISMATCH 1, UNVERIFIABLE 1.
