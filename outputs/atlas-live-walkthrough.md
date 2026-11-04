# ATLAS live walkthrough

## Current deployment

The private production Site is [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/), **v43**, active with owner-only access. Sign in with the authorized account to view it. The browser Site is hosted on the existing Sites deployment; Apple does not host this web application.

The canonical score is **60/100 provisional**. The study register contains 8 U.S. and 8 international candidate areas, but no area passes the complete independent-reference and sampling gates (**0/16 confirmatory eligible**). The analysis panel uses synthetic fixture values. The matched Sentinel-1 RTC panel measures spatial availability only; it does not validate flood accuracy.

## Guided walkthrough

1. Open the Site and read the visible synthetic-data disclosure. Candidate-area profiles and the synthetic analysis scenario are separate controls; selecting a study candidate does not change the synthetic portfolio.
2. In **16-area evidence and coverage screen**, select **Mumbai**. Review its fixed 625 km² footprint, public management evidence, value-integration question, validation path, source link, and 121 distinct metadata dates. The profile states that OPERA pixel-level QA, event-matched scenes, geometry, and independent labels remain pending. Select **Houston** to compare a U.S. candidate.
3. Expand **Compare 12 accepted sampled dates for all 16 areas**. The table shows three Sentinel-1 RTC VV orbit groups per quarter in each fixed area. The coverage-conditioned matched quota reports **192/192 selected groups**, **16/16 areas**, and **34 additional candidates screened** (23 accepted and 11 below the 80% floor). The card separately reports 169/192 passing groups in the initial random draw and warns that matched selection is conditional, not an archive-wide pass-rate estimate. This is spatial availability only.
4. Expand **Raster-level candidate-date availability · Copernicus GFM**. The 16-area table summarizes 48 baseline/event/post-event date slots: 39 have a matching raster, and 8/39 selected rasters meet the 80% valid-pixel floor. Houston and Jakarta pass on their single candidate-event sample. GFM shares Sentinel-1 lineage with OPERA, so it is not independent flood truth.
5. Review the reference-label cards and shared protocol. The proposed design requires independently sourced event evidence, blinded labels with adjudication, probability sampling, and a predeclared precision target. It plans 385 effective independent reference units per site-period for an overall accuracy/proportion estimate, before design-effect and finite-population adjustments.
6. In **Study setup**, select **Baton Rouge / Hurricane Ida**. Confirm the 2021 event and baseline windows, Louisiana synthetic portfolio, and the synthetic-data disclosure.
7. Switch to **Quality-aware aggregate**. The lead asset changes from 28.6% to 21.4% illustrative overlap. Select **Southeast Water Plant** to see 18.9% overlap, 93% fixture coverage, and 73% uncalibrated fixture confidence. These are demonstration values, not measurements.
8. Select **Export evidence**. The intended success notice confirms the scenario, observation windows, method, and synthetic-data label. This control is part of the previously replayed v40 workflow; it has not been replayed against v41 yet, and the CSV bytes were not inspected in the earlier replay.
9. Select **Reset analysis** to restore the single-observation method and default asset while preserving the selected Baton Rouge/Hurricane Ida scenario.
10. Scroll to **Other public reference screens**. The v41 Tampa / NASA EGIS Milton card reports three successful catalog-date sample calls, per-date return counts, and the Oct. 10 REST error. Use **Open the complete sample audit** or **Download per-point CSV** to inspect the packaged point records. NASA labels the emergency maps preliminary and unvalidated; this panel reports sample-return behavior, not full-AOI water coverage or independent truth. The v41 links and files are present in the deployment package, but live browser retrieval has not yet been replayed.

## Latest production verification

On 2026-11-03, production v40 was reloaded in the authenticated browser. That replay verified the revised 192/192 readiness ledger, all 16 coverage rows, the matched-quota export link, the OPERA-specific pending-QA disclosure, and the synthetic scenario/method/asset/export-notice flow. The live JSON endpoint returned the matched-quota audit with 16 areas, an 8+8 split, 192 selected groups, and the stated interpretation limits. This replay predates v41.

Current v41 production readback confirms the release is active and owner-only, and its generated JPEG screenshot was retrieved successfully (HTTP 200). The capture shows the default synthetic scenario, the explicit synthetic-data disclosure, and the 16-area candidate register. An authenticated tab still displayed older page content (169/192 initial draw, without the v41 Milton panel); forced reload timed out and disconnected the browser bridge. The current v41 runtime response therefore remains unverified until an authenticated reload succeeds. Unauthenticated Chrome receives HTTP 401 under the private access policy. See [v41 deployment checklist](atlas-v41-end-to-end-checklist.md) and [v41 page capture](atlas-site-v41-deployment-capture.jpg).

The hash-locked Python 3.12 Bookworm suite passed **130 tests** for the current worktree. See [v41 deployment checklist](atlas-v41-end-to-end-checklist.md) for release identifiers, package checks, and limitations. These checks verify software and page rendering, not the v41 browser interactions; they do not establish empirical flood accuracy, independent reproduction, or confirmatory study readiness. The score remains **60/100 provisional**.

## Current walkthrough — v42 (2026-11-04)

Version 42 is live and owner-only. The refreshed authenticated in-app browser rendered the full evidence-register link and the latest matched-quota coverage panel. The analyst selected Baton Rouge / Hurricane Ida, selected Dubai from the 16 candidate profiles, toggled to the quality-aware aggregate, inspected the Dubai evidence profile, and downloaded the synthetic scenario CSV. The downloaded CSV contains 12 data rows and explicitly labels every row `synthetic_fixture_no_live_NASA_data`. The deployed JSON endpoint opened and presented the common screening protocol plus all 16 candidate areas. See [the v42 end-to-end checklist](atlas-v42-end-to-end-checklist.md).

These are passed demo/deployment workflows, not flood-validation results. The research frame remains 8 U.S. and 8 international candidates, with **0/16** confirmatory enrollment; the canonical provisional score remains **60/100**. No fresh browser download event was received when the JSON download control was clicked, although the deployed JSON URL itself opened and its contents were read successfully. The primary scenario CSV download completed and was inspected.

## Open evidence and readiness

## Current production walkthrough — v43 (2026-11-04)

Authenticated browser replay on the deployed page passed all 16 candidate profiles and their evidence fields, Baton Rouge/Hurricane Ida selection, quality-aware aggregate update, Southeast Water Plant detail, reset to the single-scene baseline, and completed synthetic CSV export. The live CEMS panel displays 268 activations, 90 floods, and 0/16 fixed-area overlaps. The full hash-locked Python suite passed 138 tests in the current worktree. See [the v43 checklist](atlas-v43-end-to-end-checklist.md) for deployment IDs, archive hash, observed values, and limitations. Analysis values remain synthetic; the evidence register is candidate readiness, with 0/16 confirmatory eligibility and a 60/100 provisional score.

- [v40 deployment and end-to-end checklist](atlas-v40-end-to-end-checklist.md)
- [Canonical scorecard](atlas-scorecard.md)
- [Current worktree revalidation](atlas-current-worktree-revalidation.md)
- [Regional Sentinel-1 coverage comparability screen](atlas-s1rtc-region-comparability-screen.md)
- [Four-cloud release runbook](atlas-cloud-release-runbook.md)
- [Apple distribution readiness](atlas-apple-distribution-readiness.md)

Google Cloud, AWS, Microsoft Azure, and Oracle Cloud deployments remain unverified pending account-specific release inputs. The existing Apple account is designated for possible future Apple-platform app distribution; no native app target or Apple distribution build has been verified. Apple distribution is separate from hosting the current browser Site.
