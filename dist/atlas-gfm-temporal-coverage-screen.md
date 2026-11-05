# ATLAS multi-date GFM raster coverage screen

Updated 2026-11-04. This is a raster-availability diagnostic for the fixed 8+8 candidate frame, not a flood-accuracy assessment or an enrollment decision.

## Method

Three nearest distinct OPERA metadata dates in the 30 days before and after the first Groundsource candidate lead, plus all OPERA metadata dates within the reported lead interval. Dates are candidate sampling windows, not verified flood-event dates.

A selected same-day COG is the intersecting item with the greatest fixed-AOI valid fraction; duplicates are not mosaicked. Each date passes at >=80% non-nodata pixels.

For each selected date, the audit searches the Copernicus GFM STAC collection, reads every intersecting `ensemble_flood_extent` COG, and retains the single item with the highest valid-pixel fraction over the fixed AOI. It does not mosaic duplicate items. Previously measured same-area/date results from the 2026-11-03 GFM audit are reused; new dates are read live. The machine-readable output records the input file SHA-256 values, item IDs, assets, versions, nodata, pixel counts, fractions, and item-level failures.

## Results

| Region | Area | Pre-event dates ≥80% | Candidate-event dates ≥80% | Post-event dates ≥80% | 3 pre + 3 post pass |
|---|---|---:|---:|---:|:---:|
| United States | Houston | 3/3 | 1/1 | 3/3 | Yes |
| United States | Miami | 0/3 | 0/1 | 0/3 | No |
| United States | Tampa | 0/3 | 0/2 | 0/3 | No |
| United States | New Orleans | 0/3 | 0/1 | 0/3 | No |
| United States | New York City | 0/3 | 0/2 | 0/3 | No |
| United States | Sacramento | 0/3 | 0/1 | 0/3 | No |
| United States | Atlanta | 0/3 | 0/1 | 0/3 | No |
| United States | St. Louis | 2/3 | 0/1 | 2/3 | No |
| International | Jakarta | 0/3 | 1/1 | 1/3 | No |
| International | Singapore | 0/3 | 0/1 | 0/3 | No |
| International | Dubai | 0/3 | 0/1 | 0/3 | No |
| International | Mumbai | 0/3 | 0/1 | 0/3 | No |
| International | Bangkok | 1/3 | 0/1 | 1/3 | No |
| International | Tokyo | 0/3 | 0/1 | 0/3 | No |
| International | Manila | 0/3 | 0/1 | 0/3 | No |
| International | São Paulo | 1/3 | 0/1 | 1/3 | No |

Across 114 date slots in all 16 areas, 92 yielded a readable raster and 17/114 selected rasters met the 80% floor. Two areas (Houston and Jakarta) had at least one candidate-event-date raster meeting the floor. Houston alone had all three selected pre-event and all three post-event dates pass. No area is confirmatory-eligible.

## Interpretation and limits

Groundsource records are discovery leads; they do not establish official event occurrence, exact local timing, or flood extent. Pre/post windows are acquisition opportunities around those leads, not verified event/baseline periods. GFM shares Sentinel-1 lineage with OPERA DSWx-S1, so these data are not independent validation truth. A GFM raster passing the spatial-coverage floor does not validate the target product or prove mapped water is floodwater. The single-event-date screen also does not satisfy three observations within a verified event period. Independent licensed labels, adjudication, probability sampling, and the predeclared precision gate remain absent.

Confirmatory eligibility therefore remains **0/16**, and the canonical score remains **60/100 provisional**. This screen is not a replacement for the target OPERA full-AOI QA or independent reference-label workflow.

## Reproduction

Run `python scripts/audit_gfm_temporal_coverage.py` with the project analysis dependencies. It resumes completed areas from the JSON output and records input hashes. The 4 focused regression tests cover date selection and the 80% / three-date screen. Full local suite: **195 passed**.

Machine-readable detail: [`atlas-gfm-temporal-coverage-audit.json`](atlas-gfm-temporal-coverage-audit.json). Existing single-date screen: [`atlas-gfm-raster-coverage-screen.md`](atlas-gfm-raster-coverage-screen.md).
