# ATLAS live walkthrough

**Live private Site:** https://atlas-water-screening.shawdaimarie.chatgpt.site/\
**Verified published version:** 9\
**Access:** owner-only; sign in with the authorized account.

The deployed page is a research walkthrough using labeled synthetic fixtures. The local OPERA raster analysis scripts are not connected to this page or its API.

## Follow this path in the live page

1. **Explore the screening view.** Open the page and review its research framing and synthetic-data notice. Select the baseline/event method controls and observe the lead fixture asset’s displayed percentages change. The documented author-run check changed the lead asset estimate from 28.6% to 21.4%, elevated count from 4 to 3, and median from 7.7% to 6.8%.
2. **Change the area and event.** Select the Baton Rouge / Hurricane Ida preset. Confirm the area, event label, date windows, map labels, and synthetic asset identifiers update together.
3. **Inspect an asset.** Choose an asset row and review the evidence details. The details should track the selected row and remain marked as synthetic.
4. **Review an international candidate.** Open the study-area register and select Singapore or Mumbai. Review the location rationale, value-integration question, CMR metadata count, and explicit pending-validation status. Metadata counts indicate archive discovery only, not valid observations.
5. **Export the candidate register.** Use “Download area register.” The page should show its CSV download confirmation. The export contains the 8 U.S. and 8 international candidates and their metadata/date evidence.
6. **Export evidence.** Use the evidence export and confirm the download message. These exports document the candidate screen and synthetic walkthrough; they do not contain verified pixel-level results.
7. **Reset.** Use Reset and confirm the method returns to the single-observation baseline. The selected area/event scenario remains in place.

## What has been verified

The latest author-run production replay visited all 16 candidate profiles, switched methods, changed to Baton Rouge/Hurricane Ida, downloaded both CSVs, parsed their contents, and reset to the single-observation baseline. The exact live downloads are [the 16-area register](atlas-live-area-register-v9.csv) and [the Baton Rouge synthetic evidence export](atlas-baton-id-aggregate-fixture-export.csv). The register has 8 U.S. and 8 international records; the evidence export has 12 asset rows and marks every row synthetic. Version 9 deployment status is `succeeded`; Sites readback confirms an active private owner-only publication. The browser walkthrough is a bounded functional check, not independent reproduction or scientific validation.

## Related evidence

- [Deployment and test results](atlas-deployment-test-results.md)
- [Current scorecard](atlas-scorecard.md)
- [Study-area program and selection criteria](atlas-study-area-program.md)
- [Evidence register](atlas-evidence-register.md)
- [Local analysis input template](atlas-study-package-template.json)
- [Four-cloud release preparation](atlas-multicloud-deployment-preparation.md)
