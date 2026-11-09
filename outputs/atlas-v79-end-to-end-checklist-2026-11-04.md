# ATLAS v79 end-to-end release and walkthrough checklist

**Date:** 2026-11-04 (UTC)  
**Production URL:** [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/)  
**Site version:** 79  
**Source commit:** `c1d40d04d15babf11731b0d82e0923fc6a687ac2`  
**Deployment:** `appgdep_6aeb7b2fc10c81919b50b07a234bfe95` — succeeded  
**Saved version:** `appgprj_6ae8f548d7a48191adbbfe7affb04a94~appgver_a01c72b951dc8191b0f213f0f1183238`

## Release and access verification

- Sites control-plane readback confirms version 79 is active and points to the exact pushed source commit above.
- Access remains custom and owner-only: `shawdaimarie@gmail.com` is the sole allowed viewer; external visitor count is zero.
- The v79 deployment archive contains 45 files, 6,256,640 bytes, and has content hash `sha256:cc09598240c555782d28e0377bb1ed16d724ebea77670bbb8e942d846253833f`.
- The error-only production Worker log query for the 30 minutes following the release returned zero events.

## Browser walkthrough results

| Workflow | Result | Observed result |
|---|---|---|
| Open current production page | Pass | v79 loaded in the authenticated owner browser; synthetic-data notice is visible. |
| Select a research area | Pass | Selecting Jakarta updated its profile and evidence details while preserving the separate synthetic-analysis boundary. |
| Change historical scenario | Pass | Changing Beryl to Ida updated the event to Baton Rouge, Aug. 29–30, 2021, and updated the synthetic scenario label and dates. |
| Change analysis method | Pass | Quality-aware aggregate became selected; Reset returned the method to single-observation baseline. |
| Select asset | Pass | Selecting Southeast Water Plant updated the selected asset detail and illustrative overlap. |
| Export analysis evidence | Pass | The app displayed “Evidence export downloaded with scenario, observation windows, method and synthetic-data label.” |
| Export 8+8 area register | Pass | The app displayed “Study area register downloaded as CSV.” |
| Reset analysis | Pass | The app displayed “Analysis reset to the single-observation baseline.” |
| View HLS availability screen | Pass | The deployed page displays the complete 16-area table, common time window, per-area records/date ranges, and metadata-only caveats. |
| Open full audit report | Pass | The v79 HTML report opens directly from the Site and presents the 16-area table, metrics, limitations, and source links. |
| Validate report/download assets | Pass locally before packaging | The 16-row CSV and compact JSON parsed; full scene JSON and pixel-access report are included; all relative file links in the HTML report resolve to packaged files. A completed browser download receipt for the HLS attachments was not independently observed. |

The HLS screen records 10,978 primary catalog records and 5,655 area/date pairs, with 228–425 catalog dates per area for the shared window `[2024-09-01, 2026-11-03)` UTC. It is metadata availability only. It does not establish valid-pixel coverage, water detections, event confirmation, or independent validation. The live report explicitly describes DSWx-HLS as an optical cross-sensor stream and not a substitute for DSWx-S1.

## Acceptance status

The private browser demonstration and supported synthetic workflows are operating. The software walkthrough is not a real-raster analysis or scientific validation. OPERA target-product pixel retrieval, event/baseline QA coverage, independent labels, local partner/governance review, deployed four-cloud environments, cloud recovery/load tests, and participant usability evidence remain outstanding. The strict score remains **60/100 provisional** and confirmatory eligibility remains **0/16**; v79 earns no score points from metadata discovery alone.

The existing Apple Account is a separate future Apple-platform distribution path. It was not used for this browser Site deployment; no iOS app was built or submitted.
