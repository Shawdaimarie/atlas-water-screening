# ATLAS v53 production walkthrough and release check

**Date:** 2026-11-04  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Site version:** 53  
**Source commit:** `9aeb51500c0c3d9c330b7d95f18560260aa44ddb`  
**Deployment:** `appgdep_6aeade16fc7481918dbebe524ee86c6b` — succeeded  
**Audience:** owner-only; `shawdaimarie@gmail.com`; zero external visitors.

## Production replay results

The deployed page was opened in the authenticated in-app browser. The following interactions ran against v53 and were checked from the rendered accessibility tree and visible page:

| Workflow | Result | Evidence observed |
|---|---|---|
| Select all registered study-area profiles | **16/16 passed** | Each U.S. and international selection updated the profile heading and rendered rationale, public evidence, value-integration question, and shared validation path. |
| Switch event | **Passed** | Hurricane Ida changed the event details and date window. |
| Switch study area | **Passed** | Baton Rouge changed the scenario label and portfolio heading. |
| Combine selected area and event | **Passed** | Baton Rouge + Hurricane Ida displayed together in the event card and portfolio title. |
| Change comparison method | **Passed** | Quality-aware aggregate became selected and the corresponding method text appeared. |
| Inspect an asset | **Passed** | Southeast Water Plant became selected and its detail panel appeared. |
| Export evidence | **Passed** | Export control fired and the page showed a success notice naming scenario, observation windows, method, and the synthetic-data label. A prior v51 production replay parsed the downloaded fixture CSV; current source-level regression checks assert required export-provenance fields. |
| Reset analysis | **Passed** | Reset notice appeared and method returned to single-observation baseline. Scenario selectors remained independently set to Baton Rouge and Ida. |
| Keyboard area selection | **Passed** | Space selected Miami, updated its profile, and retained focus on Miami after rerender. |

## Automated and source checks

- Hash-locked Python 3.12 project suite: **145 passed**; a fresh documentation-state recheck completed in **1.17 seconds**.
- Node 22 syntax check of the deployed inline script: passed.
- `git diff --check`: passed.
- Sites control-plane readback: active version 53, succeeded deployment, custom owner-only access.

## Scientific and release limits

This verifies production interface behavior and the private Sites release path. The analysis portfolio, map, observations, and exposure values are synthetic fixture data; no NASA granule is loaded in the scenario. The candidate selector is independent of the Houston/Baton Rouge analysis scenario. The evidence ledger remains **0/16 confirmatory-eligible**. This replay does not demonstrate an operational raster API, production cloud infrastructure, scientific accuracy, customer demand, deployment to Apple, Google Cloud, AWS, Azure, or Oracle.

Canonical score remains **60/100 provisional**. See `SCORECARD.md`, `outputs/atlas-v53-accessibility-audit.md`, and `outputs/atlas-reference-readiness-ledger.csv`.
