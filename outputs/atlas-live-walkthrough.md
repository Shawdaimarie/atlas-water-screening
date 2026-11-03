# ATLAS live walkthrough

**Production Site:** [Open ATLAS](https://atlas-water-screening.shawdaimarie.chatgpt.site/)

**Current deployed version:** 19

**Access:** private; sign in with the authorized owner account.

**Current score:** 55/100 provisional; no 100/100 claim.

The page is an interactive research walkthrough with synthetic analysis fixtures and an evidence-backed 8 U.S. + 8 international candidate register. It does not connect to the local raster-analysis pipeline, the cloud API, or live OPERA water-class data. Candidate archive dates are metadata-discovery evidence only.

## Guided walkthrough

1. Open the production Site and review the synthetic-data and candidate-only notices. The new reference-coverage panel reports the C2S, UFOv2, CEMS, and GFD screening gaps; no current candidate passes the independent-label gate.
2. In the study-area panel, select **Singapore** or **Mumbai**. Review the location rationale, public source, value-integration question, metadata count, and pending pixel-QA/independent-label status. Try a U.S. candidate such as **Houston** and compare its evidence profile.
3. Use **Download area register**. The CSV contains all 16 candidates, per-area CMR date evidence, AOI bounds, screening dates, rationale, and validation status.
4. In the analysis panel, change the method from the single-scene baseline to **Quality-aware aggregate**. The current synthetic fixture changes the lead overlap estimate from 28.6% to 21.4%, the elevated-fixture count from 4 to 3, and the median from 7.7% to 6.8%.
5. Change the scenario to **Baton Rouge / Hurricane Ida**. Confirm the area, event, time windows, labels, and fixture assets update together. These are illustrative synthetic values.
6. Select an asset row to open its evidence details, then use the evidence export and confirm the success message and synthetic label.
7. Use **Reset** to restore the baseline, then return to a preferred study-area profile.

8. Review the **Sentinel-1 coverage** panel. Compare both samples per quarter, open the paired JSON download, and note repeated groups and the 80% spatial-data coverage floor. Then review the **Shared validation protocol** below the reference-coverage panel. It explains the common 30 m measurement, independent event evidence, blinded label review, probability sampling, and the 385-unit starting precision calculation. The page explicitly labels this as a proposed design and states that 0 of 16 candidate areas currently qualify for confirmatory validation. Use **Open the full proposed protocol** to read the private source document.

## Verified live workflows

Version 19 is the active private production release. It retains the shared proposed-validation protocol, 16 candidate profiles and fixed-AOI reference coverage panel, and adds the pinned GEOID-Flood result: 12 St. Louis tiles for 2017, all in the benchmark training split and outside the current analysis window. The deployed card says no raster, mask-alignment, or sensor-independence checks were performed and does not call this held-out validation. Version 17’s interactive replay selected all 16 candidate profiles, switched the synthetic method, changed to Baton Rouge/Hurricane Ida, confirmed both export messages, and reset to the single-scene baseline; version 19’s paired sample panel and live JSON download were verified in the browser; the download reports the STAC nodata value, per-sample identifiers and checksums, and two-draw results across 16 areas. These checks do not verify real raster coverage, scientific accuracy, a connected production API, or cloud-provider deployment. Full record: `atlas-deployment-test-results.md`.

For test detail, see [deployment and test results](atlas-deployment-test-results.md). For the current rubric evidence, see the [scorecard](atlas-scorecard.md). For the cloud prerequisites, see the [four-cloud release runbook](atlas-cloud-release-runbook.md).
