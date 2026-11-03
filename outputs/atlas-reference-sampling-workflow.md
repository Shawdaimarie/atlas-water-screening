# ATLAS independent reference sampling workflow

Updated 2026-11-03. This is a reproducible frame preparation step for the proposed 16-area study. It does not create reference labels or enroll any candidate area.

## Run

Populate the study package using `outputs/atlas-study-package-template.json`. Each of the 16 registered areas must provide an `event_sampling_raster` and `baseline_sampling_raster`, plus its fixed AOI, assets, and acquisition manifest. Sampling rasters must be single-band OPERA DSWx-S1 V1 BWTR on the frozen 30 m projected grid, with valid classes 0 (non-water) and 1 (water); nodata and product-invalid classes are excluded by mask/value checks. The command transforms each supplied AOI to the raster CRS and stops if a valid sampling pixel center falls outside that AOI; it hashes both AOI and raster inputs.

Run in the project's hash-locked Python 3.12 environment:

```sh
python scripts/build_reference_sample_frames.py \
  --study-package input_data/study-package.json \
  --output-dir work/reference-sample-frame \
  --target-n 385 \
  --seed 20261103
```

The command requires all 16 registered areas and both periods. It stops on missing/out-of-package files, non-projected grids, non-30 m grids, valid pixels outside the fixed AOI, invalid study-area balance, or missing period rasters. It writes `reference_sample_frame.csv` and `reference_sample_frame_summary.json`.

## Sampling and output fields

For each area-period, valid map pixels form two strata: mapped water and mapped non-water. A deterministic seed derived from the run seed, area, and period selects a simple random sample without replacement within each stratum. Allocation is proportional to the valid class populations, with at least one unit per nonempty class where the target allows it. Each selected unit records its pixel row/column and center coordinates, CRS, stratum population, sample count, inclusion probability, and inverse-probability design weight. The summary stores source-raster, AOI, and package hashes, class totals, seed, and target.

Interpretation and adjudication columns are intentionally blank. Independent labelers must assess the units against licensed, temporally suitable reference material while blinded to the OPERA map. Preserve reference source, date, license, both initial labels, and adjudication according to `outputs/atlas-preregistered-validation-protocol.md`.

## Limits and current status

The default 385 is an unadjusted planning target for one overall proportion at 95% confidence and ±5 percentage points. It is not a guarantee of effective sample size: the spatial-block pilot must estimate design effect and adjust the target before confirmatory use. If a stratum population is below its allocation, all available units are selected and the frame records the finite population. The script does not calculate accuracy, spatial independence, event eligibility, or valid-reference coverage.

No complete set of real, QA-verified event and baseline BWTR rasters is currently available for the 16 fixed areas. The workflow has been tested on synthetic GeoTIFF fixtures only. Four fixture tests and the full pinned Python 3.12 suite pass (100 tests). Therefore no production frame was drawn, independent labels remain unavailable at comparable coverage, confirmatory eligibility remains **0/16**, and the canonical score remains **55/100 provisional**.
