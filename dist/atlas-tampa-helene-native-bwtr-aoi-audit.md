# Tampa Hurricane Helene · native OPERA BWTR audit

This audit reads the original JPL ARIA-share OPERA DSWx-S1 V1 Binary Water Detection band for the fixed 625 km² Tampa candidate area. It counts native raster pixel centers inside the same frozen WGS84 bounding box for both dates. A padded read window preserves AOI boundary pixels.

| Acquisition date | Valid non-water | Valid water | Invalid/no-data | Water share of valid pixels |
|---|---:|---:|---:|---:|
| 2024-09-14 | 385,407 | 111,909 | 0 | 22.5026% |
| 2024-09-26 | 383,987 | 113,329 | 0 | 22.7881% |

Each scene contains 497,316 AOI pixel centers and passes the preliminary 80% valid-pixel floor. The difference is descriptive only. Two dates do not satisfy the preregistered three-date-per-period floor, and no independent reference labels or uncertainty estimates are available. The product is preliminary and unvalidated; classified water includes permanent and seasonal water, so these values do not establish a flood change or product accuracy.

- [Machine-readable counts and source provenance](atlas-tampa-helene-native-bwtr-aoi-audit.json)
- [Original JPL ARIA-share source directory](https://aria-share.jpl.nasa.gov/20240926-Hurricane_Helene/DSWx/)
- [OPERA DSWx-S1 catalog and class definitions](https://developers.google.com/earth-engine/datasets/catalog/OPERA_DSWX_L3_V1)
