# Tampa Hurricane Milton NASA EGIS WTR sample screen

**Run:** 2026-11-04T05:39:01.107949+00:00  
**Status:** Exploratory point-sample availability screen only  
**AOI:** Frozen Tampa 25 × 25 km candidate box; no geometry changes  
**Samples:** 1,024 same-point, equal-area strata per catalog date at approximately 30 m nearest-neighbor resolution

## Results

| NASA catalog date | Phase | Catalog item | Sample return | Returned WTR classes | Endpoint result |
|---|---|---|---:|---|---|
| 2024-10-03 | pre-landfall | 2 | 797/1024 (77.8%) | 0: 661, 1: 133, 3: 3 | sampled |
| 2024-10-08 | pre-landfall | 3 | 1024/1024 (100.0%) | 0: 767, 1: 252, 3: 5 | sampled |
| 2024-10-10 | post-landfall | 4 | 0/1024 (0.0%) | none | not sampled; item footprint misses fixed AOI |
| 2024-10-11 | post-landfall | 5 | 1024/1024 (100.0%) | 0: 777, 1: 246, 3: 1 | sampled |

On 2024-10-03, 797/1,024 requested points returned (77.8%); the other 227 returned no sample. The 2024-10-08 and 2024-10-11 requests returned all 1,024 points. The 2024-10-10 catalog item exists, but its published footprint bounding box does not intersect the frozen Tampa AOI; its 1,024 locations are retained as outside-footprint and no raster sample request is made.

The returned values were raw WTR codes, not a binary flood label. In the three sampled dates, code 0 (not water), code 1 (open water), and code 3 (low-backscattering non-water) were observed. The complete class mapping is in the JSON artifact and NASA product specification.

## Method and limits

A seeded jittered equal-area 32 × 32 grid was placed over the frozen Tampa AOI; the same 1,024 coordinates were considered for each date. Catalog item footprints were queried in WGS84 and their bounding boxes screened against the frozen AOI before sampling. Intersecting-item requests locked the NASA catalog raster ID and used nearest-neighbor sampling. The CSV retains a row for every point/date, including missing samples and dates outside the published item footprint. The JSON stores item IDs and dates, catalog footprint bounds, service description, AOI/register hash, class definitions, and per-date counts.

NASA describes these emergency response maps as **preliminary and unvalidated**. This sample-return fraction is not full-AOI valid-pixel coverage; the samples are not independent labels because they are OPERA outputs; and the pre-/post-landfall maps do not establish comparable baseline/event periods. The Oct. 10 catalog item footprint misses Tampa, and the available acquisitions do not meet the three-date-per-period feasibility screen. No candidate is confirmatorily enrolled and no score credit is added.

## Source records

- [NASA EGIS Milton DSWx overview](https://gis.earthdata.nasa.gov/portal/home/item.html?id=d20858f42cae4c6b8b4438e847266442)
- [NASA EGIS ImageServer metadata](https://gis.earthdata.nasa.gov/portal/rest/services/DISASTERS_202410_HURRICANE_MILTON/2428_opera_dswx_hls/ImageServer?f=json)
- [NASA OPERA DSWx-S1 product specification](https://www.earthdata.nasa.gov/s3fs-public/2023-12/ProductSpec_DSWX_S1.pdf)
- Reproduce with `python scripts/audit_nasa_egis_milton_samples.py`.
- Machine-readable audit: `atlas-tampa-milton-egis-pixel-sample.json`; per-point records: `atlas-tampa-milton-egis-pixel-sample.csv`.
