# ATLAS v35 deployment and end-to-end replay

**Run date:** 2026-11-03  
**Production:** [ATLAS private Site](https://atlas-water-screening.shawdaimarie.chatgpt.site/)  
**Release:** Site v35 · source SHA `c28c4d06fe9fa8da40c4e1d3850a95df25023404` · deployment `appgdep_6aea1e798c608191bab3f1eb58f9f26d` · result `succeeded`  
**Access check:** Sites readback reports `active`, version 35, owner-only access, and zero external visitors.

## Release and test evidence

| Check | Result | Evidence |
|---|---|---|
| Site publication | Pass | Deployment service returned `succeeded`; active version 35 readback at the existing private URL |
| Published JavaScript syntax | Pass | Inline script extracted from the exact packaged Site source and passed syntax checking |
| Patch whitespace check | Pass | `git diff --check` |
| Full Python suite | Pass | Python 3.12: **92 passed in 2.83s** |
| Event archive audit | Pass, discovery only | 1,597,726 source rows screened, 11,615 intersecting event records across 16 areas; all 16 have date-only discovery candidates whose nearest OPERA metadata dates are within one calendar day and with at least three dates in each 30-day pre/post window |
| Live research card | Pass | Production page visibly reports the 16/16 candidate screen and its date precision, verification, QA, and independent-label caveats |
| Audit JSON endpoint | Pass | Direct live URL renders the complete schema v2 JSON report and its 16 area profiles |
| Audit JSON browser download event | Not verified | Link activation/download automation timed out; endpoint retrieval is verified, but a saved browser download is not claimed |
| Aggregate comparison | Pass | Live values changed from 4 elevated / 7.7% median to 3 / 6.8%, with explicit synthetic-fixture labeling |
| Asset detail | Pass | Selecting Southeast Water Plant updated the detail to 18.9% overlap and 93% valid coverage |
| Candidate profile | Pass | Selecting Mumbai displayed 361 granule metadata hits, 121 dates, the 625 km² footprint, and pending-validation caveats |
| Scenario switch | Pass | Hurricane Ida switched to Baton Rouge, August 2021 event and baseline windows, and Louisiana fixture IDs |
| Evidence export | Pass | Live page displayed its downloaded-success notice with scenario, observation windows, method, and synthetic-data label |
| Study register export | Pass | Live page displayed the 16-area register CSV download-success notice; parsed 8+8 export was previously verified in v34 |
| Reset | Pass | Restored single-observation mode, 4 elevated / 7.7% median, and baseline asset selection |

## Scope and interpretation

Groundsource is news-derived event discovery metadata. OPERA date matching uses calendar dates only, and the audit does not verify exact acquisition timestamps, official event occurrence, valid product pixels, independent reference labels, or comparable sampling. The research result remains 0/16 confirmatory areas. The analysis interface continues to use synthetic fixtures.

The evidence-backed score remains **55/100 provisional**. This release improves discovery and traceability but does not satisfy the missing scientific validation, production API security, recovery, capacity/cost, usability study, cloud deployment, or independent reproduction criteria. The four cloud targets are still preparation only. Apple can support a separate future native app distribution path; it does not host the current browser Site.
