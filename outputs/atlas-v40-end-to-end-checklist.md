# ATLAS v40 deployment and end-to-end checklist

**Release date:** 2026-11-03  
**Site:** [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/)  
**Version:** 40  
**Source commit:** `5b0c035d27325ad2d60df6961964773c4c877ccd`  
**Deployment:** `appgdep_6aea4f6bea5481919fb77c51376a4ec0` — succeeded  
**Saved version:** `appgprj_6ae8f548d7a48191adbbfe7affb04a94~appgver_9df852626410819189d9ce7ee0899b0e`  
**Access:** existing owner-only policy preserved; control-plane readback reports one allowed owner and zero external visitors.

## Release change

Updated the readiness card to distinguish the coverage-conditioned **192/192 matched quota** from the earlier **169/192 initial random draw**. It reports 16/16 areas meeting the 12-group screen, and 34 supplemental candidates screened (23 accepted and 11 below the floor). The card states that the matched quota is conditional and must not be treated as an archive-wide pass-rate estimate. Candidate profiles now identify pending pixel QA specifically as **OPERA** QA. Confirmatory enrollment remains 0/16.

## Verification results

- The exact committed Site source was pushed to the bound private Site repository, packaged with `.openai/hosting.json` and the `dist/` site assets, saved as version 40, and deployed successfully.
- Sites control-plane readback reports v40 active at the existing production URL, with owner-only access and no external visitors.
- Authenticated production reload visibly showed the revised readiness card, the 192/192 and 16/16 quota summary, the 16-area results table, the quota audit link, and the OPERA-specific pending-QA text.
- Opened the live matched-quota JSON endpoint. Its report states 16 candidate areas (8 U.S. and 8 international), 192 selected valid groups, 192 target groups, and the screen's interpretation limits.
- Replayed Study setup as Baton Rouge / Hurricane Ida. The live page updated to the August 2021 event window, pre-event reference window, Louisiana portfolio, and synthetic fixture disclosure.
- Switched to **Quality-aware aggregate**. The lead-asset overlap changed to 21.4% synthetic fixture value. Selecting Southeast Water Plant showed 18.9% illustrative overlap, 93% fixture coverage, and 73% uncalibrated confidence.
- Selected **Export evidence**; the visible success notice confirmed the scenario, observation windows, method, and synthetic-data label. The browser automation did not capture a completed download event in this replay, so the exported file bytes were not independently inspected for v40.
- Selected **Reset analysis**. The deployed page returned to single-observation mode and Bayou East Substation (28.6% illustrative overlap) while retaining the Baton Rouge/Hurricane Ida scenario.
- The current worktree's Python 3.12 Bookworm suite passed **127 tests** using the two hash-locked dependency files. See the current revalidation record for environment details and the known host Python limitation.
- `git diff --check` passed for the release changes; only the pre-existing archived CSV line-ending warnings were reported.

## Fresh live replay — 2026-11-03

- Sites control-plane readback again confirmed the active production URL, Site version 40, and the private owner-only audience (one owner, zero external visitors).
- Authenticated browser replay selected Mumbai and displayed its candidate-only profile, 121 distinct metadata dates, the common 625 km² footprint, public need evidence, value-integration question, and explicit pending QA/independent-label caveats.
- Switched the separate synthetic analysis to Baton Rouge / Hurricane Ida. The page updated the event window and portfolio; selecting Quality-aware aggregate changed the fixture ranking and displayed the synthetic-method disclosure.
- Triggered Export evidence. The deployed page showed the success notice naming the scenario, observation windows, method, and synthetic-data label. The browser did not expose a saved file for byte-level inspection, so this confirms the user-visible workflow only.
- The full current-worktree suite passed **128 tests in 2.13s** in Python 3.12 Bookworm after installing `requirements-dev.lock` and `requirements-reference-audit.lock` with `--require-hashes`. The host Python 3.9 attempt cannot collect four spatial-audit modules because Shapely is absent there; it is not the supported pinned test environment.
- The live replay verifies interface controls and evidence disclosures, not real-data results. Analysis remains synthetic, no study area is confirmatorily enrolled, no cloud provider is deployed, and the research score remains **60/100 provisional**.

## Limits and outstanding release gates

The deployed analysis portfolio remains synthetic; it does not retrieve NASA observations. The RTC quota measures finite, non-nodata Sentinel-1 VV spatial coverage and is not OPERA QA, water classification, event/baseline adequacy, independent reference data, or flood-accuracy validation. The 16 candidate areas remain **0/16 confirmatory eligible**, and the canonical score remains **60/100 provisional**.

Google Cloud, AWS, Microsoft Azure, and Oracle Cloud hosting were not deployed by this Site publication. The existing Apple account is a possible Apple Developer distribution identity; the current Site is browser-based, the repository contains no native Apple application target, full Xcode is unavailable on this Mac, and Apple Developer membership/App Store Connect access have not been verified. This Site deployment is not an Apple app release.
