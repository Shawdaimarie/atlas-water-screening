# USGS Global Flood Impacts Database fixed-AOI event screen

**Retrieved:** 2026-11-04  **Window:** 2024-09-01 to 2026-11-02

## Result

The USGS GFID aggregated workbook contains 136,642 source rows; 504 rows have a consolidated event date in the common study window. The exact representative-coordinate screen found **0 of 16** points inside the registered AOIs and **0** additional points within 25 km of any AOI.

| Study area | Representative points inside fixed AOI | Nearby points within 25 km |
|---|---:|---:|
| Houston | 0 | 0 |
| Miami | 0 | 0 |
| Tampa | 0 | 0 |
| New Orleans | 0 | 0 |
| New York City | 0 | 0 |
| Sacramento | 0 | 0 |
| Atlanta | 0 | 0 |
| St. Louis | 0 | 0 |
| Jakarta | 0 | 0 |
| Singapore | 0 | 0 |
| Dubai | 0 | 0 |
| Mumbai | 0 | 0 |
| Bangkok | 0 | 0 |
| Tokyo | 0 | 0 |
| Manila | 0 | 0 |
| São Paulo | 0 | 0 |

## Interpretation

This is evidence that this particular geocoded impact database does not provide spatially local event points for these 16 boxes in the screened period. It is not evidence that no floods occurred in or near the areas. GFID event coordinates are representative geocodes, not inundation boundaries; an inside point would still require source-level location precision and event-date review. The database does not provide per-pixel labels, and its impact records do not qualify any site for confirmatory enrollment.

The workbook MD5 matched the checksum in the USGS ScienceBase file metadata: `3ea4849f12f98a58855d06b9f1b9a5bc`. The audit scanned the workbook’s `Aggregated` worksheet and retained source rows without deduplicating possible overlapping records.

## Sources and artifacts

- [USGS GFID catalog page](https://catalog.data.gov/dataset/the-global-flood-impacts-database-gfid)
- [USGS ScienceBase record](https://www.sciencebase.gov/catalog/item/69e7e00db66b0164d0f7302d)
- [Machine-readable audit](atlas-usgs-gfid-aoi-event-audit.json)

Score and confirmatory enrollment remain unchanged: **60/100 provisional** and **0/16 eligible**.
