# Copernicus GFM raster-level availability screen

Updated 2026-11-03. This is an archive availability diagnostic over the fixed ATLAS candidate AOIs, not an accuracy assessment. The GFM STAC catalog was queried for all 16 boxes over 2024-09-01 through 2026-11-03; exact per-area item and date counts are in `atlas-gfm-aoi-coverage-screen.json`.

For each area, the first Groundsource candidate event lead was used only to pick one nearby baseline date, one reported-event date, and one nearby post-event date from the existing OPERA metadata-date audit. These event leads are not official confirmations. On each sampled day, all intersecting `ensemble_flood_extent` COGs were opened; the single COG with the largest valid-pixel fraction inside the fixed AOI was retained. Tile/overpass values were not combined. Valid fraction is classifiable (not nodata) pixels divided by AOI pixels. The preregistered 80% valid-pixel floor is shown as a screen only.

| Region | Area | Baseline date (valid %) | Candidate event date (valid %) | Post-event date (valid %) | Event sample ≥80% |
|---|---|---:|---:|---:|:---:|
| United States | Houston | 2025-05-19 (95.0%) | 2025-05-26 (95.2%) | 2025-05-31 (95.0%) | Yes |
| United States | Miami | 2025-08-30 (0.0%) | 2025-09-04 (36.1%) | 2025-09-11 (0.0%) | No |
| United States | Tampa | 2024-10-03 (50.3%) | 2024-10-08 (59.6%) | 2024-10-15 (50.1%) | No |
| United States | New Orleans | 2025-10-12 (0.0%) | 2025-10-13 (0.0%) | 2025-10-19 (79.2%) | No |
| United States | New York City | 2025-02-06 (0.0%) | 2025-02-10 (56.0%) | 2025-02-16 (0.0%) | No |
| United States | Sacramento | 2025-05-07 (63.7%) | 2025-05-08 (no GFM item) | 2025-05-12 (37.5%) | No |
| United States | Atlanta | 2024-10-03 (0.0%) | 2024-10-08 (76.2%) | 2024-10-15 (0.0%) | No |
| United States | St. Louis | 2024-10-30 (84.5%) | 2024-11-05 (20.7%) | 2024-11-11 (84.5%) | No |
| International | Jakarta | 2026-01-25 (0.0%) | 2026-01-26 (80.9%) | 2026-01-30 (81.2%) | Yes |
| International | Singapore | 2025-03-17 (70.5%) | 2025-03-18 (68.6%) | 2025-03-24 (0.0%) | No |
| International | Dubai | 2025-10-22 (no GFM item) | 2025-10-23 (0.0%) | 2025-10-25 (no GFM item) | No |
| International | Mumbai | 2025-09-11 (0.0%) | 2025-09-16 (43.5%) | 2025-09-23 (0.0%) | No |
| International | Bangkok | 2025-09-01 (89.1%) | 2025-09-05 (59.9%) | 2025-09-11 (no GFM item) | No |
| International | Tokyo | 2025-09-09 (0.0%) | 2025-09-10 (no GFM item) | 2025-09-16 (52.1%) | No |
| International | Manila | 2025-09-09 (no GFM item) | 2025-09-10 (0.0%) | 2025-09-12 (no GFM item) | No |
| International | São Paulo | 2025-10-04 (0.0%) | 2025-10-05 (no GFM item) | 2025-10-10 (no GFM item) | No |

## Result and limits

Only **2/16** sampled candidate-event rasters (Houston and Jakarta) meet the 80% AOI-pixel availability floor. Across all 48 target date slots, a same-day GFM item was found and sampled in 39; only 8/48 selected COGs met the 80% floor. No candidate meets confirmatory enrollment: this screen samples only one date per period, Groundsource dates remain unverified discovery leads, three QA-valid observations per baseline and event period are still required, and independent licensed labels, probability sampling, and precision requirements remain absent.

GFM is not independent validation for OPERA DSWx-S1 because both derive from Sentinel-1 SAR. Copernicus describes GFM as a Sentinel-1-based ensemble of three flood-detection algorithms with 20 m pixel sampling and an archive from 2015 onward ([GFM overview](https://global-flood.emergency.copernicus.eu/general-information/about-glofas/), [product specifications](https://european-flood.emergency.copernicus.eu/sites/default/files/AM/AM2022/1-3_GFM_ensemble%20_flood_product_v1.pdf)). The 39 readable sampled COGs report mixed processing versions: 15 v3.1.0, 21 v4.0.0, and 3 v4.1.0. The catalog marks its license as `other` and links [GFM terms of service](https://global-flood.emergency.copernicus.eu/terms-of-service/), so operational reuse needs a separate license/terms review.

The product reports algorithmic observed flood extent, not adjudicated field truth. Raster coverage can be partial even when the STAC item footprint covers an AOI. Therefore catalog dates are not valid observations, and class 1 pixels are not independently verified flood labels. No change to area enrollment or rubric score follows from this diagnostic.

Reproduce the COG screen with Python 3.12 and the project analysis dependencies:

```sh
./.venv/bin/python scripts/audit_gfm_raster_coverage.py
```

Raw area/date catalog query results: `atlas-gfm-aoi-coverage-screen.json`. Raster item identifiers, asset paths, nodata, pixel counts/classes, and processing metadata: `atlas-gfm-raster-coverage-audit.json`.
