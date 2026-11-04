# Hurricane Milton NASA EGIS two-area point-sample screen

**Run:** 2026-11-04  
**Areas:** Miami and Tampa fixed 25 km × 25 km candidate AOIs  
**Source:** NASA EGIS OPERA DSWx-S1 Water Detection ImageServer for Hurricane Milton  
**Status:** exploratory source-access/point-return diagnostic only.

## Matched sampling design

For each fixed AOI, the audit placed the same seeded 1,024 jittered equal-area sample points at each of four catalog dates: 2024-10-03 and 2024-10-08 (pre-landfall), and 2024-10-10 and 2024-10-11 (post-landfall). Every sample request locked to the catalog raster ID. Catalog item geometry was checked against each fixed AOI before requesting point values. The JSON preserves item metadata, footprints, error states, point coordinates, raw classes, and counts; the CSV provides row-level samples.

## Results

| Area | Date | Catalog footprint | Point returns | Returned class counts |
|---|---|---|---:|---|
| Miami | 2024-10-03 | Intersects | 1,024/1,024 | Class 0: 506; class 1: 516; class 3: 2 |
| Miami | 2024-10-08 | Outside fixed AOI | 0/1,024 | Not sampled |
| Miami | 2024-10-10 | Intersects | 0/1,024 | Service returned HTTP/API 400: invalid or missing input parameters |
| Miami | 2024-10-11 | Intersects | 0/1,024 | Service returned HTTP/API 400: invalid or missing input parameters |
| Tampa | 2024-10-03 | Intersects | 797/1,024 | Class 0: 661; class 1: 133; class 3: 3 |
| Tampa | 2024-10-08 | Intersects | 1,024/1,024 | Class 0: 767; class 1: 252; class 3: 5 |
| Tampa | 2024-10-10 | Outside fixed AOI | 0/1,024 | Not sampled |
| Tampa | 2024-10-11 | Intersects | 1,024/1,024 | Class 0: 777; class 1: 246; class 3: 1 |

The 2024-10-10 Miami footprint intersects its fixed box, but NASA's sampling service rejected the point request. The audit records that separately from a non-intersecting footprint and does not convert the service failure into a no-water result. Tampa 2024-10-03 returned fewer points than requested; those missing returns remain missing, not dry.

## Interpretation limits

- NASA describes these rapid-response products as preliminary and unvalidated.
- Catalog-date labels are grouped relative to landfall only; this is not a preregistered event/baseline design, and no change estimate is calculated.
- Point returns are not full-AOI valid-pixel fractions. This audit does not inspect per-asset footprint coverage, independent labels, sampling precision, or accuracy.
- Only 2 of 16 candidate areas had intersecting source coverage for these screened scenes. Neither area passes confirmatory enrollment; the shared ledger remains 0/16.
- The result adds a reproducible raw-data access test but no research-score points.

## Artifacts

- [Machine-readable audit](atlas-milton-egis-multisite-pixel-sample.json)
- [Per-point CSV](atlas-milton-egis-multisite-pixel-sample.csv)
- Reproduce with `python scripts/audit_nasa_egis_milton_multisite.py`.
