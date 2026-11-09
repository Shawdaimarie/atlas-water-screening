# ASEAN modeled flood-hazard screen

Checked 2026-11-04. This supplementary audit tests whether a public modeled flood atlas adds consistent hazard and value context for the ATLAS study areas in Singapore, Jakarta, and Bangkok. It is not a validation dataset.

## Source and scope

The source is the v2 Open Multi-Hazard Flood Atlas, a public Zenodo record under CC BY 4.0. Its 30 m depth rasters represent coastal, fluvial, and pluvial design-event scenarios. The audit screens the present-day `SSP5-8.5_2020` scenario at 10-, 100-, and 1,000-year return periods against the three cities' frozen ATLAS 25 km × 25 km WGS84 boxes. It checks 27 rasters in total.

The archives are pinned by byte length and MD5 in `outputs/atlas-asean-flood-atlas-fixed-aoi-screen.json`. The reproducible implementation is `scripts/audit_asean_atlas_fixed_aoi.py`; the source rasters themselves are not copied into this repository. Raster pixel centers are transformed into the source UTM CRS and selected inside each fixed box. Valid-data fraction is reported separately. Nodata and missing pixels are excluded from wet-area estimates and remain unknown, never assumed dry. Wet-area counts are reported at both depth >0 m and depth ≥0.10 m.

## Results

| City | Hazard | Valid coverage across return periods | Modeled area at ≥0.10 m (km²), RP10 / RP100 / RP1000 |
|---|---|---:|---:|
| Singapore | Coastal | 100% | 0.00 / 0.00 / 0.00 |
| Singapore | Fluvial | 83.8% | 17.00 / 19.79 / 22.96 |
| Singapore | Pluvial | 81.2% | 28.22 / 62.37 / 90.77 |
| Jakarta | Coastal | 100% | 21.88 / 26.92 / 33.97 |
| Jakarta | Fluvial | 49.5% | 40.06 / 66.57 / 91.36 |
| Jakarta | Pluvial | 79.4–79.7% | 179.96 / 234.62 / 271.42 |
| Bangkok | Coastal | 84.4–100% | 3.22 / 1.18 / 1.55 |
| Bangkok | Fluvial | 29.2–31.0% | 15.51 / 25.09 / 42.37 |
| Bangkok | Pluvial | 84.4–100% | 10.13 / 34.26 / 50.01 |

These values are model outputs and area counts over valid raster cells. Bangkok coastal output is non-monotonic across return periods, an issue to check against the source's scenario definitions before interpreting trend. Singapore's modeled coastal values are zero within this particular box; this does not establish absence of coastal risk. The broad boxes and city-level model grids are not parcel exposure measurements.

## Research and value integration

The screen adds a comparable scenario layer for three major technology hubs. It can support descriptive prioritization and value dimensions such as critical-infrastructure exposure, population/service continuity, and the cost of false negatives, provided those layers are sourced and joined independently. It cannot establish local demand on its own, and this screen adds no verified site-level demand measurements. Tie infrastructure and population overlays to dated public inventories before describing them as evidence.

## Limits and score treatment

- The atlas contains modeled design conditions, not dated observed floods or matched event/baseline samples.
- The dataset README's validation claims and accompanying manuscript were not independently reviewed here.
- Spatial coverage is uneven, especially for Bangkok fluvial (about 29–31%) and Jakarta fluvial (49.5%). The summaries must be read with those coverage gaps.
- This is only three of the 16 registered sites. It does not meet all-area comparable observational coverage or independent reference-label requirements.
- No confirmatory area is newly eligible. Score remains **60/100 provisional** and eligibility remains **0/16**.

## Reproduction

Run `python scripts/audit_asean_atlas_fixed_aoi.py --archive-dir <directory-with-pinned-archives>` in the hash-locked Python 3.12 environment. The audit fails if archive bytes, checksum, source license/readme declarations, raster CRS, resolution, or overlap checks fail. Two tests cover WGS84 box validation and nodata exclusion from valid-area denominators.

Sources: [Zenodo v2 record](https://zenodo.org/records/21403070) and [dataset README](https://zenodo.org/records/21403070/files/README.md?download=1). The source attribution and license are also embedded in the JSON artifact.
