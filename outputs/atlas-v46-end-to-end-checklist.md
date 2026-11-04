# ATLAS v46 production end-to-end checklist

**Checked:** 2026-11-03 America/Chicago  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Status:** private owner-only Site, v46 active. This record covers the browser walkthrough and its linked exports; synthetic values are not operational flood measurements.

## Release identity

- Sites readback reports the production Site active at v46, with owner-only custom access and zero external visitors.
- Site source commit: `43fed86571ee3c4de6edf921463d6256694aec75`.
- Deployment: `appgdep_6aeac2ead124819198f7c4d02a8dfafe` (succeeded).
- Local package SHA-256: `996e6a0148563dd091366770f55ca48e993c9979f97842ead15ff4ebb76ebbd2`.
- Sites stored archive checksum: `sha256:d279c2e5e26c62c12db8109d561c277750476d99fae1ba5daefc042d0a3927f7`, with 17 packaged files.

## Regression fix

Production replay found that browser Back from a linked JSON page could restore the Baton Rouge/Ida selectors while leaving the analysis heading on Houston/Beryl. The buildless page now synchronizes the displayed scenario from the restored selectors on `pageshow`, including a valid scenario pairing, method, and selected asset. The fix was checked in the local browser preview using the same selectors → live JSON → Back path before publication.

## Production walkthrough and results

1. **Load and access:** the authenticated production page loaded successfully. Sites readback still shows owner-only access; no audience change was made.
2. **All 16 study-area profiles:** Houston, Miami, Tampa, New Orleans, New York City, Sacramento, Atlanta, St. Louis, Jakarta, Singapore, Dubai, Mumbai, Bangkok, Tokyo, Manila, and São Paulo each displayed the candidate-only status, location rationale, public-evidence context, value-integration question, comparable validation path, and evidence limit (**16/16 passed**).
3. **Scenario controls:** selecting Baton Rouge and Hurricane Ida updated the event description, event window (2021-08-29 to 2021-08-30), baseline window (2021-08-15 to 2021-08-25), title, and synthetic portfolio together.
4. **Method and asset:** selecting the quality-aware aggregate changed the displayed median overlap from 7.7% to 6.8% and updated the ranking. Selecting Southeast Water Plant updated the detail panel to LA-002, 18.9% fixture overlap, 93% valid coverage, and 73% uncalibrated fixture confidence.
5. **Live matrix endpoint:** the deployed `atlas-site-selection-evidence-matrix.json` parsed as JSON with 16 rows and `confirmatory_areas_eligible: 0`.
6. **History regression:** after opening that live JSON endpoint and using Back, the page showed Baton Rouge/Ida consistently across selectors, event card, title, event/baseline windows, and evidence provenance. The restored analysis returned to the single-observation baseline, and no stale Houston/Beryl title remained.
7. **Evidence exports:** the post-Back single-mode CSV contained 12 Baton Rouge/Hurricane Ida rows, the matching event window, `single` method, and `synthetic_fixture_no_live_NASA_data` provenance. A second aggregate-mode export contained 12 rows with `aggregate` method and the same scenario and synthetic-data label. Both browser success messages appeared and both CSVs parsed successfully.
8. **8+8 area register:** the production register download contained 16 rows: 8 U.S. and 8 international, equal 625 km² areas, and populated public evidence, validation-path, and scope-limit fields.
9. **Reset:** reset returned the analysis to the single-observation baseline and default asset and displayed its success message. The chosen Baton Rouge/Ida scenario remained intact.
10. **Console:** no browser console errors were recorded during the production replay.

## Research boundary and score

The page continues to disclose that its water map, asset portfolio, and observation values are synthetic fixtures and that no NASA data were retrieved. The area register and metadata/coverage panels support candidate screening only. They do not establish flood classification, independent ground truth, or damage/service consequences. Confirmatory eligibility remains **0/16** and the canonical score remains **60/100 provisional**; this UI fix and walkthrough add no scientific-validity points.

Remaining gates include matched QA-valid OPERA event and baseline observations, independent licensed labels and adjudication, probability-sample precision evidence, four-provider cloud deployments, capacity/cost testing, a task-based accessibility/usability study, and independent reproduction. See [the canonical scorecard](../SCORECARD.md) and [multi-cloud preparation record](atlas-multicloud-deployment-preparation.md).
