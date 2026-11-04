# ATLAS raster workload performance contract

Status: prospective local workload check; target written before the run.

## Fixed workload

- Dataset: all six SHA-256-pinned preliminary NASA ARIA/OPERA Central Texas BWTR mosaic GeoTIFFs listed in `outputs/atlas-texas-raster-pilot/summary.json`.
- Processing: `scripts/analyze_opera_geotiffs.py` with the fixed 25 km AOI, 600 m technical cell, six-row manifest, 80% valid-pixel rule, and three qualifying dates per baseline and event period.
- Environment: `python:3.12-bookworm@sha256:a5bab0ff300f91231c2e68bf73a8a8d60762ac39ce1c50eaf6803e4c38a9062b`, Linux ARM64, two vCPUs and 2 GiB memory limit, with `requirements-dev.lock` installed using `--require-hashes`.
- Repetitions: three fresh CLI processes, writing to disposable separate output directories. The OS file cache is not cleared. Validate input hashes before all repetitions and verify the same QA gate result after each.

## Targets set before measurement

- Each six-scene single-AOI analysis completes in at most **10 seconds** wall time.
- Peak resident memory stays below **1 GiB** per run.
- At least **6 completed six-scene jobs per minute** are sustained serially over the three measured repetitions.
- All repetitions produce the same per-date QA, insufficient-coverage state, and no-comparison outcome.

This is a bounded local processing regression target for a preliminary response-mosaic pilot outside the 16 registered sites. It is not a deployed-service, production-load, multi-user, or cloud-cost test. No billed compute cost is estimated here; therefore this result alone cannot satisfy the canonical performance or scalability criteria, and it will not change the score.

## Measured result

The three fresh CLI runs passed: maximum wall time **0.302 seconds**, median **0.299 seconds**, peak resident memory **104,964,096 bytes**, and serial rate **200.476 jobs/minute**. The six-row per-date QA CSV and insufficient-coverage comparison CSV had identical hashes across all runs. Each run emitted no comparison because the fixed pilot has only two qualifying dates in each period. Exact input/output hashes and per-run values are in `atlas-raster-performance-benchmark.json`.

Reproduce in the pinned Linux ARM64 container with a two-vCPU, 2 GiB memory limit: install `requirements-dev.lock` using `--require-hashes`, then run `python scripts/benchmark_opera_raster_workload.py`. The measured packages were Rasterio 1.5.2 and NumPy 2.5.4. This local baseline adds no rubric points without an appropriate deployed workload and cost test.
