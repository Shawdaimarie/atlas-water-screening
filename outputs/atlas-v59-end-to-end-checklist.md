# ATLAS v59 deployment and verification record

**Date:** 2026-11-04  
**Site:** [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/)  
**Audience:** owner-only, unchanged  
**Source commit:** `fa778eded93e614b8be36dbdbf56293afe177560`  
**Version:** `appgprj_6ae8f548d7a48191adbbfe7affb04a94~appgver_76751bfa17108191be66b25f780c2bd7`  
**Deployment:** `appgdep_6aeafebe578c8191858fecbdd9dc31a4`

## Release result

Sites returned `succeeded` for the private production deployment. The archive was built from the pushed source commit, and its `dist` directory contains the 16-area reference-readiness ledger, the new GFID audit JSON and Markdown, and the generated evidence card.

## Verification results

| Check | Result | Evidence |
|---|---|---|
| Full local project suite | **Pass: 165 tests** | `./.venv/bin/python -m pytest -q` |
| Whitespace / patch validation | **Pass** | `git diff --check` |
| GFID audit fixtures | **Pass** | Included in the full suite; 2 focused tests |
| Ledger and Site-card checks | **Pass** | Included in the full suite; 3 focused card tests and ledger consistency checks |
| Static deployment packaging | **Pass** | Site workflow pushed commit `fa778eded93e614b8be36dbdbf56293afe177560` and produced `/tmp/atlas-v59.tar.gz` |
| Production publication | **Pass** | Sites deployment status `succeeded`; private production URL returned |
| Authenticated browser replay | **Not completed** | Browser automation returned `browser.user is unavailable`; native Mac app access reported the Mac locked |
| External AWS / Azure / GCP / OCI deployment | **Not run** | Provider accounts are still being created; no account credentials, projects, or paid cloud resources were used |
| Apple native release | **Not run** | User selected their existing Apple Account. No native target, Xcode, Developer Program membership, or App Store Connect access was verified. |

The full suite emitted one environment warning: the installed urllib3 build detected LibreSSL rather than OpenSSL. It did not fail any test.

## Guided walkthrough

1. Open the private [ATLAS Site](https://atlas-water-screening.shawdaimarie.chatgpt.site/) while signed in as the owner.
2. Review the dashboard and its 8 U.S. and 8 international candidate areas. Choose an area to inspect its rationale, value dimensions, public evidence, and validation path.
3. Scroll to **16-area evidence-readiness ledger**. It reports 0/16 confirmatory-eligible sites and the common observation and reference coverage caveats.
4. Find **USGS GFID independent event-context screen**. Open the JSON link or download the audit to inspect per-area counts and source provenance.
5. Verify the interpretation: 136,642 aggregated source rows were scanned; 504 rows fell in the shared time window; no representative geocodes were found in or within 25 km of the 16 boxes. This says this database supplied no local geocodes in the screen; it does not establish that flooding did not occur.
6. Try the labeled synthetic scenario and method-comparison controls, inspect an asset, export the result, and use Reset. These walkthrough analytics remain synthetic fixture data, not live flood estimates.

## Scientific and score status

The GFID audit is event-context discovery only. It does not include flood extents or per-pixel labels, does not meet the independent-label or confirmatory enrollment gates, and does not change the score. Current author-verified provisional score: **60/100**. Confirmatory study areas: **0/16**. A score of 100/100 is not supported by the current evaluation evidence.

## Reproduction

Run `./.venv/bin/python scripts/audit_usgs_gfid_aoi_events.py --help` for the audit interface. The audit expects the official USGS workbook and verifies its published MD5 before scanning. Rebuild the displayed ledger with `./.venv/bin/python scripts/build_reference_readiness_ledger.py`.

