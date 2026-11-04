# ATLAS v48 production replay

**Date:** 2026-11-04 (America/Chicago)  
**Site:** [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/)  
**Project:** `appgprj_6ae8f548d7a48191adbbfe7affb04a94`  
**Version:** 48; deployment `appgdep_6aeacad4cb2881919b873db5a24e5dfa` succeeded  
**Source:** `dfb4868c4fbe891916f7c66dc690711de156d4cd`  
**Archive SHA-256:** `b92a8ff901e00e11441e2d3d9e6199b65637271e7cb0e810b53143e22089e321`

## Deployed state

Sites readback after publication reports version 48 active at the established URL. Access remains `custom`, with only the owner account `shawdaimarie@gmail.com` allowed and zero external visitors. The archive deploy completed with status `succeeded`.

## Production replay

Authenticated in-app browser checks on the deployed v48 page:

- The page loaded the full balanced candidate register: **16 areas, 8 U.S. and 8 international**.
- The user-selectable candidate profile worked for Jakarta, Singapore, Dubai, and Mumbai. Each profile displayed the common OPERA metadata window, the 12-of-12 conditional 2025 Sentinel-1 RTC availability screen, rationale, public evidence, value question, and scope/validation notes.
- The matched availability panel showed **192/192 selected groups** across **16/16 areas**, after 34 supplemental candidate groups were screened (23 accepted, 11 below the threshold). The page clearly states that the selection is coverage-conditioned availability, not flood classification or independent truth.
- The analyst selected Baton Rouge / Hurricane Ida. The page displayed the 29–30 August 2021 event window, 15–25 August baseline, and synthetic-data disclosure.
- Switching to the quality-aware aggregate updated the method and figures. Selecting Southeast Water Plant displayed 18.9% illustrative overlap, 93% fixture coverage, and 73% uncalibrated fixture confidence.
- Reset returned the analysis to the single-scene baseline and displayed its confirmation.
- The evidence CSV downloaded and parsed as **12 rows**. All rows identify Baton Rouge, Hurricane Ida, the event and baseline windows, aggregate method, and `synthetic_fixture_no_live_NASA_data` provenance.
- The study-area CSV downloaded and parsed as **16 rows** with exactly **8 U.S. and 8 international** entries.
- Keyboard focus was visible with a 3 px outline; buttons, method controls, and the study selector each measured 44 px minimum height. Browser diagnostics returned no console errors.

The visible run is a functioning research walkthrough. Candidate profiles and real source audits are shown separately from the synthetic Houston/Baton Rouge asset-analysis fixture. No NASA granule was loaded for the analysis, and no flood accuracy is claimed.

## Software checks

- Pinned Python 3.12 Bookworm image `python:3.12-bookworm@sha256:a5bab0ff300f91231c2e68bf73a8a8d60762ac39ce1c50eaf6803e4c38a9062b`.
- Installed the development, reference-audit, and audit lock files with `pip install --require-hashes`.
- Full suite: **139 passed in 1.64 s**.
- `git diff --check`: passed.

## Research readiness and score

The release improves visibility and keyboard access and deploys the latest local study and matched-availability panels. These software and availability checks do not establish comparable flood observations or labels. Confirmatory eligibility remains **0/16**; the canonical score remains **60/100 provisional** under the strict 5-or-0 rubric. Real matched OPERA scenes, independent licensed labels, adjudication and precision gates, independent reproduction, the task-based accessibility/usability study, production API authorization, provider-connected deployments, and declared workload/cost evidence remain outstanding. No provider cloud or native Apple release is represented by this Site deployment.
