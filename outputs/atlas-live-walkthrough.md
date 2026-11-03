# ATLAS live walkthrough

**Production Site:** [Open ATLAS](https://atlas-water-screening.shawdaimarie.chatgpt.site/)

**Current deployed version:** 23 (deployment `appgdep_6ae9f349bbf88191bd90035e54ed546f` succeeded; source commit `2eb8cf562d9a2257dd012b422c1852cfa464e140`)

**Access:** private; sign in with the authorized owner account.

**Current score:** 55/100 provisional; no 100/100 claim.

The page is an interactive research walkthrough with synthetic analysis fixtures and an evidence-backed 8 U.S. + 8 international candidate register. It does not connect to the local raster-analysis pipeline, the cloud API, or live OPERA water-class data. Candidate archive dates are metadata-discovery evidence only.

## Guided walkthrough

1. Open the production Site and review the synthetic-data and candidate-only notices. The reference panel reports the C2S, UFOv2, CEMS, GFD, SpaceNet 8, and normalized 16-area readiness screens; no current candidate passes the independent-label gate.
2. In the study-area panel, select **Singapore** or **Mumbai**. Review the location rationale, public source, value-integration question, metadata count, and pending pixel-QA/independent-label status. Try a U.S. candidate such as **Houston** and compare its evidence profile.
3. Use **Download area register**. The CSV contains all 16 candidates, per-area CMR date evidence, AOI bounds, screening dates, rationale, and validation status.
4. In the analysis panel, change the method from the single-scene baseline to **Quality-aware aggregate**. The current synthetic fixture changes the lead overlap estimate from 28.6% to 21.4%, the elevated-fixture count from 4 to 3, and the median from 7.7% to 6.8%.
5. Change the scenario to **Baton Rouge / Hurricane Ida**. Confirm the area, event, time windows, labels, and fixture assets update together. These are illustrative synthetic values.
6. Select an asset row to open its evidence details, then use the evidence export and confirm the success message and synthetic label.
7. Use **Reset** to restore the baseline, then return to a preferred study-area profile.

8. Review the **Sentinel-1 coverage** panel. Compare draws A, B, and C in each quarter, open the multi-draw JSON download, and note repeated groups and the 80% spatial-data coverage floor. The current screen shows 168/192 selected groups above the threshold and 10/16 areas passing all 12 selections. Treat this as availability only; it does not validate water classification, event coverage, or independent labels. Then review the **Shared validation protocol** below the reference-coverage panel. It explains the common 30 m measurement, independent event evidence, blinded label review, probability sampling, and the 385-unit starting precision calculation. The page labels this as a proposed design and states that 0 of 16 candidate areas currently qualify for confirmatory validation. Use **Open the full proposed protocol** to read the private source document.

## Verified live workflows

Version 23 is the active private production release. Authenticated replay verifies the 16-area ledger card and download links. The production JSON route displays all 16 AOIs and confirms 0 confirmatory sites; the source-derived summary is 168/192 sampled RTC groups passing the 80% availability screen, 10/16 areas passing all 12 sampled groups, and four areas with some spatial reference lead. The hash-locked Python 3.12 suite passes 77 tests. These checks verify the walkthrough and source-coverage reports only; they do not verify flood classification, scientific accuracy, a connected production API, or cloud-provider deployment. Full record: `atlas-deployment-test-results.md`.

The user intends to use an existing Apple account for a future release. ATLAS is currently a private web Site, not an Apple-hosted service or an iOS app. No iOS target or Apple distribution build has been verified; the browser deployment remains the way to observe this walkthrough.

For test detail, see [deployment and test results](atlas-deployment-test-results.md). For the current rubric evidence, see the [scorecard](atlas-scorecard.md). For the cloud prerequisites, see the [four-cloud release runbook](atlas-cloud-release-runbook.md).


The corrected full source snapshot also passed [GitHub Actions run 41578752221](https://github.com/Shawdaimarie/atlas-water-screening/actions/runs/41578752221): 56 tests, the reference footprint screen, container build and image audit, 11/11 HTTP smoke checks, and dependency audit. These are source and local-container checks only.
