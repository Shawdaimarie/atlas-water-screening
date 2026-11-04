# ATLAS v56 live deployment revalidation

**Date:** 2026-11-04  
**Target:** private owner-only ATLAS Site, `https://atlas-water-screening.shawdaimarie.chatgpt.site/`  
**Deployment:** `appgdep_6aeaebcca5e88191a27437915d99d473`  
**Source:** `184b5ac7309ff69a8e33201087eab214c2890e4d`

## Deployment record cross-check

The Sites deployment record was re-read after the walkthrough. It reports version **56**, publication status **succeeded**, and the expected source commit. Its saved archive contains **22 files**, is **1,556,480 bytes**, and has SHA-256 `a49507f5332972a87559cc8454ffb8d90f57839c9304b582fafaa472939c3742`. Access remains custom/owner-only, with no external visitors. This confirms the walkthrough target and its release artifact; it does not verify a four-cloud deployment.

## Observed workflows

Replayed the deployed page in the authenticated browser and inspected its rendered accessibility tree and screenshot.

| Workflow | Observed result |
|---|---|
| Load the 8+8 evidence register | All 16 candidate areas rendered with their U.S./international grouping, metadata counts, rationale, public evidence, value question, validation path, and explicit pending-validation status. |
| Select Dubai | Dubai profile displayed 1,009 granule metadata hits, 381 distinct dates, a 625 km² nominal footprint, Dubai Municipality Tasreef evidence, a value-integration question, comparable validation path, and explicit limits. |
| Select Mumbai | Mumbai profile displayed 361 granule metadata hits, 121 distinct dates, a 625 km² nominal footprint, Government of India UFRMP evidence, a value-integration question, comparable validation path, and explicit limits. The page identifies these as candidate metadata, not QA-valid observations or customer demand. |
| Switch scenario | Hurricane Beryl changed the synthetic walkthrough to Houston and July 8–10, 2024; the page retained its synthetic-fixture disclosure. |
| Change comparison method | Quality-aware aggregate selection changed the fixture median from 7.7% to 6.8% and the selected lead-asset overlap from 28.6% to 21.4%; the method described three illustrative observations and kept missing pixels unknown. |
| Select an asset | Selecting Southeast Water Plant changed the detail panel to TX-002, 18.9% illustrative overlap, 93% fixture coverage, and 73% uncalibrated fixture confidence. |
| Export evidence | The site displayed “Evidence export downloaded with scenario, observation windows, method and synthetic-data label.” |
| Reset | The analysis returned to the single-observation baseline, 7.7% median fixture overlap, and the default Bayou East Substation detail. |

## Interpretation

The production walkthrough and its tested controls are operational. The tested analysis remains generated synthetic fixture data; this replay does not demonstrate NASA retrieval, validated flood classification, asset exposure in the 16 candidate areas, or the full scientific study. The current worktree full test suite separately passed **157 tests** on macOS/Python 3.9 (one existing urllib3/LibreSSL warning). After the later exact-source audit, the canonical score is **60/100 provisional** after source recovery and passing CI; confirmatory enrollment remains **0/16**.

## Remaining gates

Comparable event/baseline OPERA pixels and independent licensed reference labels across the 8+8 areas; participant usability/accessibility acceptance; ready and deployed Google Cloud, AWS, Azure, and Oracle environments; deployed capacity/cost evidence; and independent reproduction are still outstanding.
