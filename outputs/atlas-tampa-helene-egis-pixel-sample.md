# Tampa Hurricane Helene OPERA pixel-sample audit

**Run:** 2026-11-03 UTC  
**Status:** Exploratory source-access and sampled-coverage check only  
**Scope:** Frozen Tampa AOI, one NASA EGIS OPERA DSWx-S1 Binary Water Detection (BWTR) raster before and one on Hurricane Helene's Florida landfall date.

## Observed results

The public NASA EGIS ImageServer returned raw BWTR class values for all 1,024 deterministic, jittered equal-area points on each pinned layer. The baseline layer (2024-09-14, catalog ID 1) returned 237 water and 787 non-water samples. The landfall-date layer (2024-09-26, catalog ID 3) returned 243 water and 781 non-water samples. All 2,048 returned points were valid classes (0 or 1); no sampled points were missing or masked. These are descriptive sample proportions, not a complete raster summary, a change estimate, or an accuracy metric.

The JSON record preserves the frozen AOI and register hash, service and item identifiers, date checks, sample design and point-file hash, class contract, source caveat, per-point raw values, and run timestamp. The CSV provides the per-point rows. Recreate the audit with `python scripts/audit_nasa_egis_opera_samples.py`; the endpoint uses form-encoded POST for multipoint requests to avoid URL-size limits.

## Full-area export check (2026-11-04)

An exploratory `exportImage` request for the same locked 2024-09-14 item and full registered AOI returned a 945 × 945, three-band `uint8` GeoTIFF. Each of its first two bands contained only values 0 and 255 (208,975 and 684,050 cells); the third contained only 255. The server describes the bands generically as `Band_1`–`Band_3`, and this response did not preserve the raw BWTR classes observed through `getSamples`. Because no published band-to-class mapping was established for this export representation, these values were **not** converted to valid/water/no-data counts and no full-area coverage result is claimed. The locked, stratified raw-class `getSamples` result above remains the applicable evidence. This failed interpretation check reinforces that an image export is not automatically equivalent to the raw product band.

## Method and interpretation limits

- One seeded jittered point was drawn in each of 1,024 equal-area strata over the frozen Tampa WGS84 AOI. Equal-area placement is uniform in longitude and sine(latitude). The same point coordinates were sampled against each layer using nearest-neighbor extraction, approximately 30 m pixels, and a mosaic rule locking the requested raster ID.
- The NASA service description identifies the response maps as **preliminary and unvalidated**. The service does not report the processing version.
- Only one date is available in each period in this paired pilot. This fails the preregistered minimum of three valid acquisition dates per period, so no event-versus-baseline inference or confirmatory eligibility is claimed.
- No independently adjudicated event-floodwater reference labels were assembled for Tampa in this audit. A point sample cannot establish full-AOI pixel validity or validate product accuracy. Spatial dependence and sampling uncertainty were not estimated.

## Artifacts and provenance

- Per-point JSON: `atlas-tampa-helene-egis-pixel-sample.json`
- Per-point CSV: `atlas-tampa-helene-egis-pixel-sample.csv`
- Catalog service: [NASA EGIS Hurricane Helene OPERA DSWx-S1 ImageServer](https://gis.earthdata.nasa.gov/portal/rest/services/DISASTERS_202409_HURRICANE_HELENE/202427_opera_dswx_s1/ImageServer)
- Event timing context: [National Hurricane Center update](https://www.nhc.noaa.gov/archive/2024/al09/al092024.update.09270318.shtml)
- BWTR class definitions: [OPERA DSWx-S1 catalog](https://developers.google.com/earth-engine/datasets/catalog/OPERA_DSWX_L3_V1_S1)

This establishes a reproducible public raw-pixel sampling path for one candidate area. It does not change the confirmatory site count or the project score.
