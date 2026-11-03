# ATLAS OPERA pixel audit: owner run guide

**Purpose:** measure actual valid-pixel coverage for every registered study-area acquisition date using the public OPERA DSWx-S1 V1 product. This checks whether archive metadata availability translates into adequately observed AOI pixels. It does not identify flood events or validate water classifications against independent truth.

## Access gate

The source is `OPERA/DSWX/L3_V1/S1`, a NASA/JPL OPERA product at 30 m with 6–12 day nominal revisit. The Earth Engine catalog snapshot on 2026-11-02 lists data through **2026-10-28 UTC**; this audit therefore ends on 2026-10-28, even though the PO.DAAC/CMR register was screened through 2026-11-02. Rerun after that date to extend the common interval.

Earth Engine requires an enabled, registered Google Cloud project and the correct user permissions. The owner must complete Google's access registration and determine whether the project qualifies for noncommercial access or requires a commercial plan. No project was selected or registered by this preparation. Do not use another Google Cloud project merely because it is available.

Official references: [OPERA DSWx-S1 catalog](https://developers.google.com/earth-engine/datasets/catalog/OPERA_DSWX_L3_V1_S1), [PO.DAAC collection record and reprocessing notice](https://podaac.jpl.nasa.gov/dataset/OPERA_L3_DSWX-S1_V1), [Earth Engine access setup](https://developers.google.com/earth-engine/guides/access), and [commercial-use transition guidance](https://developers.google.com/earth-engine/guides/transition_to_commercial).

## Run

1. Sign in to the [Earth Engine Code Editor](https://code.earthengine.google.com/) using the approved Google identity and choose the registered project.
2. Open `scripts/earthengine/atlas_opera_pixel_coverage.js`, paste its contents into a new Code Editor script, and click **Run**.
3. Confirm the map shows all 16 fixed AOI boxes. In the Console, inspect `ATLAS per-area summary` and `ATLAS per-acquisition pixel QA diagnostics`.
4. Save the Console tables or export the `diagnostics` FeatureCollection to Drive only after reviewing the requested fields and destination. The script itself does not create assets or start exports.
5. Record the execution date, selected project ID, script commit, console outputs, any error, and the returned latest acquisition date in the private validation record. Do not record credentials or tokens.

## Measurement rules and interpretation

The script groups all intersecting source images by UTC acquisition date, mosaics same-day tiles, and uses the documented `BWTR_Binary_water` classes. Classes 0 (valid non-water) and 1 (water) count as valid; classes 250 (HAND mask), 251 (layover/shadow), masked pixels, and fill do not. It reports the per-date class histogram so unexpected codes are visible, along with AOI valid-area fraction, water area, source tile count, and product version. It uses each complete registered bounding box and 30 m scale consistently across all sites.

NASA reports that OPERA reprocessed affected acquisitions from 2025-05-20 through 2025-12-09 and recommends replacing any earlier downloaded granules with replacement products. This diagnostic reads the current Earth Engine collection but does not independently verify per-granule replacement status. Save the run date and product-version list; if correction status for an affected date is unclear, exclude it until the current granule is confirmed. For local GeoTIFF analysis, retrieve from the current PO.DAAC listing and retain the granule ID, processing metadata, retrieval time, and SHA-256; do not reuse an unverified cached file.

The metadata screen is 90 distinct dates per area. The 80% per-date AOI coverage flag is a minimum coverage diagnostic, not a complete event-study pass. Enrollment still requires at least three QA-valid dates in both prespecified event and baseline periods, consistent date selection across sites, valid asset coverage, data-quality review, and independent reference labels. Do not infer flood occurrence from a water-class observation or use this sam