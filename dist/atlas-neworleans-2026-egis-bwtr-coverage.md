# New Orleans · June 2026 NASA EGIS BWTR fixed-area coverage diagnostic

**Run:** 2026-11-04  
**Registered area:** New Orleans, United States; fixed 25 × 25 km candidate box.  
**Event context:** The City of New Orleans reported flash flooding and a continuing flood watch in its June 18, 2026 post-weather update ([City source](https://nola.gov/next/mayors-office/news/articles/june/2026-06-18-city-of-new-orleans-provides-update-post-severe-weather-event/)).  
**Satellite source:** NASA EGIS OPERA DSWx-S1 response service for Louisiana ([ImageServer](https://gis.earthdata.nasa.gov/portal/rest/services/DISASTERS_202606_FLOOD_LA/202610_opera_dswx_s1/ImageServer)).

## Design and result

The item `OPERA_L3_DSWx-S1_T15RYP_20260621T001010Z_20260627T005829Z_S1A_30_v1.0_B02_BWTR` (catalog raster ID 22) has a footprint containing the registered AOI centre. The audit locked that ID and exported the complete fixed box to a 963 × 963, single-band U8 GeoTIFF on an approximately 29.96 m EPSG:3857 output grid. Of 927,369 returned cells, all 927,369 were BWTR class 255 (no data); valid BWTR 0/1 coverage was 0%. An ImageServer `identify` request for the registered area centre also returned `NoData` for raster 22.

This demonstrates why a catalog-footprint intersection is not equivalent to usable pixel coverage. The audit does **not** interpret no-data as dry land or as evidence that flooding did not occur. NASA describes the response maps as preliminary and unvalidated. The catalog item name contains a June 21–27 acquisition interval, not pixel-specific times; the material does not establish event-time-matched observations under the primary 24-hour protocol.

## Interpretation limits

- One quick-response BWTR item and one fixed AOI do not establish temporal sampling adequacy, accuracy, asset exposure, or confirmatory eligibility.
- No independent event-water labels were compared with OPERA.
- The tile is a discovery lead with no valid classified cells inside this registered screen, not a measured flood outcome.
- Confirmatory eligibility remains 0/16; canonical score remains 60/100 provisional.

The machine-readable output records the locked item identity, output-grid dimensions and CRS, full class histogram, raster byte hash, centre-point check, source caveat, and current register hash. Reproduce with `python scripts/audit_nasa_egis_neworleans_bwtr_coverage.py`.
