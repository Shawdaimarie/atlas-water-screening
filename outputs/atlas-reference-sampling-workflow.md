# ATLAS independent reference sampling workflow

Updated 2026-11-03. This is a reproducible frame preparation step for the proposed 16-area study. It does not create reference labels or enroll any candidate area.

## NASA OPERA raster access prerequisite

The project has a common 16-area CMR metadata screen, but a CMR hit is not a retrieved scene. NASA PO.DAAC lists the OPERA DSWx-S1 V1 Earthdata Cloud distribution as controlled access. Metadata search can be performed without signing in; raster download or stream access requires a NASA Earthdata Login. The official `earthaccess` client supports interactive login and temporary cloud credentials. When retrieval is authorized, use interactive authentication with credential persistence disabled; keep the session in the user-controlled terminal, and write downloaded rasters only to an external data directory excluded from Git. Never copy passwords, bearer tokens, temporary S3 credentials, or `.netrc` files into ATLAS source, logs, Site assets, or project outputs. See [PO.DAAC OPERA DSWx-S1 V1](https://podaac.jpl.nasa.gov/dataset/OPERA_L3_DSWX-S1_V1), the [AWS Open Data access note](https://registry.opendata.aws/nasa-operal3dswx-s1/), and [`earthaccess` authentication guidance](https://earthaccess.readthedocs.io/en/stable/user/explanation/authenticate/).

Before counting data as an observation, resolve the exact granule ID, collection version, acquisition interval, MGRS tile, and class/confidence GeoTIFF paths; record the source checksum and retrieval time. Then run full-AOI mask/coverage checks and preserve per-asset footprint coverage. Reuse the identical event/baseline eligibility rules in all 16 areas. A successful Earthdata login or object download alone does not qualify an area for confirmatory analysis.

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

## Independent label review gate

Use `outputs/atlas-reference-labels-template.csv` for one row per labeler and sampled unit. Each unit needs two distinct primary labelers; both must be blinded to OPERA. Use the protocol's five label values. Record an ISO-8601 acquisition timestamp with timezone, sensor, resolution, source lineage, independence status and rationale, license, and HTTPS source link. For disagreement, include a third row with role `adjudicator` and the resolved class. Reuse one source ID only when its metadata is identical across rows. Do not declare an OPERA-derived or same-acquisition Sentinel-1 product `independent_primary` without a documented independent evidence basis.

Run the declared review-quality checks after the labels are assembled:

```sh
python scripts/validate_reference_labels.py \
  --sample-frame work/reference-sample-frame/reference_sample_frame.csv \
  --labels input_data/reference_labels.csv \
  --output-dir work/reference-label-qc
```

The validator writes a per-unit QC CSV and a hash-linked JSON summary. Incomplete, unblinded, sensitivity-only, or unknown-lineage records remain marked unready. A passing source declaration does not prove accuracy, licensing, event-time proximity, or complete sample precision; a second scientific review must still check those conditions against the source. This step never establishes confirmatory site enrollment.

No complete set of real, QA-verified event and baseline BWTR rasters is currently available for the 16 fixed areas. The existing real-raster analyzer has only been run on an out-of-frame Central Texas pilot and a two-date NASA EGIS point-sample screen for Tampa; neither is a complete fixed-AOI event/baseline run. The sampling and label review workflows have been tested only with synthetic fixtures. NASA granule downloads still require an Earthdata Login, and no credentials should be placed in the repository. Therefore no production frame or label QC run exists, independent labels remain unavailable at comparable coverage, confirmatory eligibility remains **0/16**, and the canonical score remains **60/100 provisional**.
