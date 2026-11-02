# ATLAS real-raster QA pilot: Central Texas, July 2025

**Result:** the analyzer processed six publicly available NASA JPL/Caltech ARIA/OPERA DSWx-S1 binary-water mosaic GeoTIFFs. The fixed 25 km Kerrville-area AOI passed the 80% valid-pixel threshold on two of three baseline dates and two of three event-period dates. The preregistered requirement is three dates in each period, so the system correctly emitted no event/baseline comparison.

This is a technical pipeline test only. Kerrville is not one of the 16 registered city candidates. The 600 m test geometry is not an infrastructure asset. The public NASA response page labels the mosaics preliminary and unvalidated, with no warranty; these files do not establish independent flood truth or an operational result.

## Inputs and provenance

The official [NASA Earthdata ImageServer description](https://gis.earthdata.nasa.gov/portal/rest/services/DISASTERS_202507_FLOOD_TX/202507_opera_dswx_hls/ImageServer) identifies the Central Texas July 4, 2025 response, documents BWTR classes and 30 m posting, lists the six acquisition dates, links to the public files, and states that the response maps are preliminary and unvalidated. The [NASA ARIA-Share directory](https://aria-share.jpl.nasa.gov/20250704_Texas_Floods/DSWx-S1/) supplied the TIFFs.

The response mosaics contain binary water values rather than complete original product science layers. The software version used to create the mosaics was not present in the page or TIFF tags; the manifest says `not_reported_in_aria_share_mosaic_metadata`. It is not inferred or fabricated. The run manifest records a SHA-256 for every input, geometry, manifest, script, and output.

## Results by acquisition date

| Period | Date | AOI valid fraction | QA result |
|---|---|---:|---|
| Baseline | 2025-06-17 | 0.999922 | passes |
| Baseline | 2025-06-19 | 0.000000 | no coverage |
| Baseline | 2025-06-22 | 1.000000 | passes |
| Event | 2025-07-01 | 0.000000 | no coverage |
| Event | 2025-07-04 | 1.000000 | passes |
| Event | 2025-07-11 | 0.999929 | passes |

Both periods have 2 qualifying dates, below the required 3. The pipeline returned `unknown_insufficient_qa_valid_dates`, with no matched dates or water-fraction delta. This confirms that the quality gate rejects incomplete coverage.

## Reproduce

From the project root, with `requirements-analysis.txt` installed:

```sh
python scripts/analyze_opera_geotiffs.py \
  --manifest outputs/atlas-texas-raster-pilot/manifest.csv \
  --aoi outputs/atlas-texas-raster-pilot/aoi.geojson \
  --assets outputs/atlas-texas-raster-pilot/assets.geojson \
  --output-dir outputs/atlas-texas-raster-pilot/analysis
```

This reproduction reuses the attached rasters; the original public URLs and file hashes are in `summary.json` and `analysis/run_manifest.json`.

## Files

- `manifest.csv`, `aoi.geojson`, `assets.geojson`: input definitions.
- `rasters/*.tif`: original public NASA response mosaics.
- `analysis/observation_qa.csv`: per-date AOI and technical-cell QA results.
- `analysis/asset_event_baseline_comparison.csv`: coverage gate outcome; no comparison emitted.
- `analysis/run_manifest.json` and `summary.json`: provenance, hashes, settings, and summary.
