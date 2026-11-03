# ATLAS live walkthrough

## Current deployment

The private production Site is [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/), **v40**, active with owner-only access. Sign in with the authorized account to view it. The browser Site is hosted on the existing Sites deployment; Apple does not host this web application.

The canonical score is **60/100 provisional**. The study register contains 8 U.S. and 8 international candidate areas, but no area passes the complete independent-reference and sampling gates (**0/16 confirmatory eligible**). The analysis panel uses synthetic fixture values. The matched Sentinel-1 RTC panel measures spatial availability only; it does not validate flood accuracy.

## Guided walkthrough

1. Open the Site and read the visible synthetic-data disclosure. Candidate-area profiles and the synthetic analysis scenario are separate controls; selecting a study candidate does not change the synthetic portfolio.
2. In **16-area evidence and coverage screen**, select **Mumbai**. Review its fixed 625 km² footprint, public management evidence, value-integration question, validation path, source link, and 121 distinct metadata dates. The profile states that OPERA pixel-level QA, event-matched scenes, geometry, and independent labels remain pending. Select **Houston** to compare a U.S. candidate.
3. Expand **Compare 12 accepted sampled dates for all 16 areas**. The table shows three Sentinel-1 RTC VV orbit groups per quarter in each fixed area. The coverage-conditioned matched quota reports **192/192 selected groups**, **16/16 areas**, and **34 additional candidates screened** (23 accepted and 11 below the 80% floor). The card separately reports 169/192 passing groups in the initial random draw and warns that matched selection is conditional, not an archive-wide pass-rate estimate. This is spatial availability only.
4. Expand **Raster-level candidate-date availability · Copernicus GFM**. The 16-area table summarizes 48 baseline/event/post-event date slots: 39 have a matching raster, and 8/39 selected rasters meet the 80% valid-pixel floor. Houston and Jakarta pass on their single candidate-event sample. GFM shares Sentinel-1 lineage with OPERA, so it is not independent flood truth.
5. Review the reference-label cards and shared protocol. The proposed design requires independently sourced event evidence, blinded labels with adjudication, probability sampling, and a predeclared precision target. It plans 385 effective independent reference units per site-period for an overall accuracy/proportion estimate, before design-effect and finite-population adjustments.
6. In **Study setup**, select **Baton Rouge / Hurricane Ida**. Confirm the 2021 event and baseline windows, Louisiana synthetic portfolio, and the synthetic-data disclosure.
7. Switch to **Quality-aware aggregate**. The lead asset changes from 28.6% to 21.4% illustrative overlap. Select **Southeast Water Plant** to see 18.9% overlap, 93% fixture coverage, and 73% uncalibrated fixture confidence. These are demonstration values, not measurements.
8. Select **Export evidence**. The success notice confirms the scenario, observation windows, method, and synthetic-data label. In the v40 replay the notice appeared; the browser download event did not complete through the automation capture, so this replay did not independently inspect the downloaded file bytes.
9. Select **Reset analysis** to restore the single-observation method and default asset while preserving the selected Baton Rouge/Hurricane Ida scenario.

## Latest live verification

On 2026-11-03, production v40 was reloaded in the authenticated browser. Control-plane readback reports version 40 active and owner-only, with zero external visitors. The live page showed the revised 192/192 readiness ledger, all 16 coverage rows, the matched-quota export link, and the OPERA-specific pending-QA disclosure. The live JSON endpoint returned the matched-quota audit with 16 areas, an 8+8 split, 192 selected groups, and the stated interpretation limits.

The same replay changed the synthetic scenario to Baton Rouge/Hurricane Ida, selected the aggregate method, selected Southeast Water Plant, and received the evidence-export success notice. Reset then restored single-observation mode and Bayou East Substation while retaining the scenario. The browser is left open at the matched-coverage results so the table and quota can be inspected directly.

The hash-locked Python 3.12 Bookworm suite passed **127 tests** for the current worktree. See [v40 deployment and end-to-end checklist](atlas-v40-end-to-end-checklist.md) for the release identifiers and evidence. These checks verify software and UI behavior; they do not establish empirical flood accuracy, independent reproduction, or confirmatory study readiness. The score remains **60/100 provisional**.

## Open evidence and readiness

- [v40 deployment and end-to-end checklist](atlas-v40-end-to-end-checklist.md)
- [Canonical scorecard](atlas-scorecard.md)
- [Current worktree revalidation](atlas-current-worktree-revalidation.md)
- [Regional Sentinel-1 coverage comparability screen](atlas-s1rtc-region-comparability-screen.md)
- [Four-cloud release runbook](atlas-cloud-release-runbook.md)
- [Apple distribution readiness](atlas-apple-distribution-readiness.md)

Google Cloud, AWS, Microsoft Azure, and Oracle Cloud deployments remain unverified pending account-specific release inputs. The existing Apple account is designated for possible future Apple-platform app distribution; no native app target or Apple distribution build has been verified. Apple distribution is separate from hosting the current browser Site.
