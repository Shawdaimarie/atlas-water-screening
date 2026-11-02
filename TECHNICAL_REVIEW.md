# ATLAS Technical Review

Date: 2026-11-02. Blueprint: shared v1.1 clarification. Status: review complete for a bounded research/demo prototype; production and operational claims are not approved. No neural network training is in scope.

## Decision and bounded scope

Proceed to an implementation-ready specification for a local, single-user, historical-event screening prototype using pinned OPERA DSWx inputs, static/synthetic infrastructure assets, deterministic spatial aggregation, and downloadable provenance report. Start with a Houston-area Texas event/date only after an archive query confirms granule coverage and independent reference data; use a separate non-Texas US event/region as held-out validation. Do not yet promise live ingestion, current-event response, arbitrary uploads, multi-tenant SaaS, damage prediction, financial loss, Singapore/Dubai support, or NISAR-derived DSWx.

## Source and observation handling

NASA Earthdata Login documentation confirms some data-download services require account/application authorization. No credentials were supplied. Initial demo must therefore use a small, legally redistributable sample/granule downloaded through a user-authorized process, or prebuilt public output where license/terms are verified. If access is not available, use clearly labeled synthetic fixtures and report no live ingestion. Do not include secrets or Earthdata credentials in the browser or repository.

For every granule, retain collection short name/version, granule ID, product/software version, source URL, acquisition timestamp, processing timestamp, sensor, spatial posting, CRS/affine transform, bands/layers, mask interpretation, checksum, attribution/license, retrieval timestamp and code/config commit. Preserve source raster and a machine-readable manifest; outputs link asset-level measurements to pixel/class counts and observation IDs. Distinguish observation time from processing and retrieval times.

OPERA DSWx-HLS and DSWx-S1 are complementary, not interchangeable. Product layers, fill values, cloud/snow or layover/shadow masks and confidence semantics must follow the product-version-specific specification. Do not interpret fuzzy score/confidence as a calibrated probability. Set exposed area to unknown when valid coverage is insufficient; never silently count missing or masked pixels as dry.

## Proposed architecture

- React + TypeScript + MapLibre user interface; event/area presets, asset table/map, observation dates, resolution, mask coverage, uncertainty and export.
- Python + FastAPI versioned OpenAPI service, initially modular monolith with bounded asynchronous job interface for raster work.
- Postgres; PostGIS only for vector AOI/asset intersection and metadata queries; COG/raster originals and derived artifacts in object storage for production. Local demo may use filesystem fixtures and SQLite only if explicitly identified as a local substitute.
- GDAL/rasterio/xarray-based geospatial processing with explicit CRS, transform, nodata, resampling and alignment rules. Prefer categorical nearest-neighbor alignment; do not resample water classes with bilinear interpolation.
- Job record states: queued/running/succeeded/failed/cancelled; idempotency key from source IDs, AOI, asset version and configuration. Enforce file size, AOI size, pixel and runtime limits before job execution.
- Export CSV/GeoJSON plus a human-readable PDF/HTML report and JSON provenance manifest. Export summarizes observed water intersection and valid coverage, with uncertainty and caveats; no loss estimate.

Google Cloud Run, Cloud Run Jobs, GitHub Actions and IaC are target choices per blueprint, subject to fresh current documentation, account configuration, price/quotas verification, and deployment authorization before implementation/deployment. The USD 50/month project target is a design ceiling for modeling, not a quote or spending authorization. Avoid continuous GPU; no neural network is planned.

## Threat model and trust boundaries

Assets are user-provided or public input and must be treated as untrusted. Validate type, size, coordinate ranges, geometry validity, raster dimensions, CRS, decompression/zip expansion and URLs; reject arbitrary remote URL fetching to prevent SSRF. Run expensive parsing in bounded jobs, with time/memory limits and no unnecessary network egress. Render properties as text and avoid injecting filenames/metadata into HTML. Use least privilege service identity, managed secrets, HTTPS, rate limits, audit events, and isolated storage prefixes if tenancy is introduced. The first prototype is single-user and must not be represented as tenant-isolated production software. Keep NASA credentials outside app backend unless an explicitly reviewed OAuth flow is later implemented. Audit log integrity is not tamper-proof unless backed by separately controlled immutable storage.

## Failure modes and operations

Expected failures: Earthdata auth/authorization denied, absent granule, archive transient errors, partial tile coverage, corrupt raster, CRS/affine mismatch, unsupported mask/version, empty assets, invalid geometry, cancellation, timeout, object-store failure, and export failure. Return visible reason/status and retain enough job metadata for reproducibility. Retry only idempotent transient retrieval; avoid duplicate jobs. Log structured identifiers, timings, counts and error classes, not secrets or unnecessary personal data. Production requires health checks, backup and restore evidence, rollback procedure, dependency/secret scans, quotas and bounded jobs, and incident notes.

## Required tests before G1

Coordinate transform and axis-order fixtures; projected/geographic CRS and reprojection; missing/no-data never becomes dry; all relevant quality mask classes excluded/reported; categorical alignment preserves class labels; exact boundary-touch/intersection semantics and polygons crossing tile edges; invalid/empty geometry; overlapping pixels not double-counted per asset; area unit conversion; zero valid coverage; deterministic repeat; asset at raster edge; provenance manifest completeness; job retry/idempotency; hostile archive/path/URL and size-limit rejection; export round-trip. No tests run in this review-only turn.

## Reproducibility and evidence study limits

Pin code, product version, input granules/checksums, AOI/asset fixtures and config. A clean-checkout study should reproduce output within documented floating-point/spatial tolerance. Hosted model nondeterminism is not applicable because no model is used. Upstream OPERA outputs are observations/products, not independent validation labels. Prefer independent high-resolution imagery with documented interpretation protocol, agency flood surveys, or georeferenced reports; report label source and positional/date uncertainty. Separate Houston event/time and validation geography/event; use spatial blocks larger than observed autocorrelation range where estimable; do not randomly split neighboring pixels. Predeclare all thresholds/aggregation variants and freeze held-out evaluation before tuning.

## Unresolved release blockers

1. Archive query has not established one Texas event with adequate OPERA coverage plus independent labels.
2. Exact second region/event and label source not selected.
3. Public asset dataset license/redistribution and completeness not audited; default to synthetic assets.
4. Earthdata credentials/application authorization absent; live archive access unverified.
5. Exact selected granule versions, observation and processing times, QA masks, attribution and licenses must be captured before packaging.
6. NISAR availability is not equivalent to mature OPERA DSWx-NI coverage. Keep excluded until collection, maturity, spatial/temporal match, quality, redistribution and integration costs are reviewed.
7. Cloud pricing/account and target <=USD 50/month configuration unverified.
