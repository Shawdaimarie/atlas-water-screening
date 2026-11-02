# ATLAS live walkthrough

**Production Site:** [Open ATLAS](https://atlas-water-screening.shawdaimarie.chatgpt.site/)  
**Verified version:** 12  
**Access:** private; sign in with the authorized owner account.  
**Current score:** 55/100 provisional; no 100/100 claim.

The page is an interactive research walkthrough with synthetic analysis fixtures and an evidence-backed 8 U.S. + 8 international candidate register. It does not connect to the local raster-analysis pipeline, the cloud API, or live OPERA water-class data. Candidate archive dates are metadata-discovery evidence only.

## Guided walkthrough

1. Open the production Site and review the synthetic-data and candidate-only notices.
2. In the study-area panel, select **Singapore** or **Mumbai**. Review the location rationale, public source, value-integration question, metadata count, and pending pixel-QA/independent-label status. Try a U.S. candidate such as **Houston** and compare its evidence profile.
3. Use **Download area register**. The CSV contains all 16 candidates, per-area CMR date evidence, AOI bounds, screening dates, rationale, and validation status.
4. In the analysis panel, change the method from the single-scene baseline to **Quality-aware aggregate**. The current synthetic fixture changes the lead overlap estimate from 28.6% to 21.4%, the elevated-fixture count from 4 to 3, and the median from 7.7% to 6.8%.
5. Change the scenario to **Baton Rouge / Hurricane Ida**. Confirm the area, event, time windows, labels, and fixture assets update together. These are illustrative synthetic values.
6. Select an asset row to open its evidence details, then use the evidence export and confirm the success message and synthetic label.
7. Use **Reset** to restore the baseline, then return to a preferred study-area profile.

## Verified live workflows

The latest recorded production replay selected all 16 profiles, switched analysis methods, changed to Baton Rouge/Hurricane Ida, inspected an asset, downloaded both CSV exports, and reset the view. Sites readback confirms the Site is active at version 12, with owner-only access and zero external visitors. These author-run checks demonstrate the walkthrough interactions only; they do not verify real raster coverage, scientific accuracy, a connected production API, or cloud-provider deployment.

For test detail, see [deployment and test results](atlas-deployment-test-results.md). For the current rubric evidence, see the [scorecard](atlas-scorecard.md). For the cloud prerequisites, see the [four-cloud release runbook](atlas-cloud-release-runbook.md).
