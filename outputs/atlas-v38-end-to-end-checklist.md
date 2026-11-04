# ATLAS v38 deployment and live walkthrough record

**Release date:** 2026-11-03  
**Site:** [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/)  
**Version:** 38  
**Source commit:** `5c42fc8bdcb8238e476ee371932301658b4bce0e`  
**Deployment:** `appgdep_6aea3dd1e3048191b939f7def5a7468e` — succeeded  
**Access:** existing owner-only account policy preserved

## Change

Added a collapsible **Raster-level candidate-date availability · Copernicus GFM** panel to the existing 16-area evidence screen. It shows baseline, candidate-event, and post-event AOI valid-pixel percentages for one Groundsource discovery lead per area, plus the 80% event-date availability result. The page states that GFM uses the same Sentinel-1 lineage as OPERA, is not independent validation, and does not change 0/16 confirmatory enrollment. The machine-readable raster audit is included in the static package.

## Deployment verification

- Sites control-plane readback after publication reported version 38 active at the existing private URL. Deployment tool returned `succeeded` with no failure message.
- In the authenticated live Site, expanded the new panel. The rendered table contained all 16 candidate areas and the same dates/coverage results as the source audit. Its summary stated 39 matching items across 48 sampled date slots, 8 selected rasters at or above 80%, and only Houston/Jakarta passing the single candidate-event sample.
- Opened the live audit JSON link in the authenticated browser. It returned the 16-area report, asset identifiers/URLs, pixel-valid fractions and counts, nodata values, class counts, processing versions, and the non-enrollment limitation.
- Captured the visible deployed panel at `outputs/atlas-v38-gfm-live.jpg`.
- Full Python suite passed **124 tests in 17.17s** in `python:3.12-bookworm@sha256:a5bab0ff300f91231c2e68bf73a8a8d60762ac39ce1c50eaf6803e4c38a9062b` after installing `requirements-dev.lock` and `requirements-reference-audit.lock` with `--require-hashes`.
- Targeted GFM audit logic checks passed for STAC pagination, AOI polygon construction, and output consistency (16 areas, 48 slots, 39 sampled items, 8/39 rasters at or above 80%, 2/16 candidate-event dates at or above 80%). `git diff --check` passed.
- The v38 static package contained `dist/index.html`, `.openai/hosting.json` with the selected Site ID, and `dist/atlas-gfm-raster-coverage-audit.json`. The JSON parsed with 16 areas; the live endpoint was also read in-browser.

## Research and score limits

The GFM screen uses one event-lead date per baseline/event/post-event period. The event leads remain unverified and all areas still lack the required three QA-valid dates per period plus independent licensed reference labels and probability samples. GFM is Sentinel-1-based like OPERA and cannot establish independent accuracy. No area enrolls and the canonical score stays **60/100 provisional**.

The existing method comparison, scenario switch, area profiles, export/reset, and synthetic fixture labeling were verified in the v37 walkthrough. This v38 release did not change those behaviors or turn the fixture analysis into live observations. Google Cloud, AWS, Azure, and Oracle deployments remain unverified; this Site release is hosted only on the existing private Sites deployment.

## Live replay in Chrome (2026-11-03)

- Sites readback before the replay confirmed production v38 active with owner-only access. The live page loaded in the authenticated browser and displayed the 16-area research program, reference-readiness ledger, sampled RTC coverage, and GFM availability section.
- Selected Mumbai in the candidate profile. The visible profile changed to Mumbai and displayed its 625 km² fixed footprint, public management evidence, value-integration question, validation path, and the 12/12 sampled RTC spatial-coverage result. The profile kept candidate-only and customer-demand limitations visible.
- Changed the separate synthetic walkthrough scenario to Baton Rouge/Hurricane Ida. The heading, event/baseline windows, synthetic portfolio, and LA asset identifiers updated. The page explicitly disclosed that values remain illustrative synthetic fixtures and that the selected Mumbai profile is independent of the Houston/Baton Rouge demo scenario.
- Switched from single observation to quality-aware aggregate; the selected fixture asset's overlap changed from 28.6% to 21.4%. Selected Southeast Water Plant; its live detail showed 18.9% synthetic overlap, 93% fixture coverage, and 73% uncalibrated fixture confidence.
- Export evidence showed the success message naming scenario, observation windows, method, and the synthetic-data label. Chrome listed the generated `atlas-baton-ida-aggregate-fixture (3).csv` file as complete (3.3 KB). The download completed; this replay did not independently parse the file contents.
- Reset analysis restored the single-observation method and default Bayou East Substation while preserving the Baton Rouge/Hurricane Ida scenario. This is the observed reset scope.
- Expanded the Copernicus GFM panel. Its 16-row table showed 39 matching items in 48 sampled date slots, with 8 of 39 selected rasters at or above 80% valid pixels and only Houston/Jakarta passing the single candidate-event sample. The GFM raw audit link opened a valid JSON document with its Sentinel-1 independence limitation.
- Returned to the live walkthrough tab and left it open on the Baton Rouge/Ida analysis with Mumbai selected; the GFM panel remains expanded lower on the page. Screenshot of the current v38 live GFM panel is `outputs/atlas-v38-gfm-live.jpg`.
- The replay is functional UI evidence only. Analysis values remain synthetic; candidate-area coverage and GFM outputs do not establish flood accuracy or independent truth. The canonical score remains **60/100 provisional** and confirmatory enrollment remains **0/16**.
