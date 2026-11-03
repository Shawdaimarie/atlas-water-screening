# ATLAS — surface-water exposure screening

ATLAS is an independent research prototype. The interactive walkthrough currently uses generated synthetic fixtures; it does not retrieve NASA Earthdata or contain observations from a real event. The Houston and Baton Rouge labels are scenario names only. The map is schematic and not georeferenced.

## Run the walkthrough locally

Open `dist/index.html` in a browser, or serve it with:

```sh
python3 -m http.server 8000 --directory dist
```

The page supports scenario selection, single-observation vs quality-aware aggregate comparison, asset ranking, asset details, and CSV export. It also contains an interactive 16-area candidate evidence register backed by a standardized NASA CMR metadata search and equal-depth profiles of documented public management/research need, value dimensions, validation paths, and evidence limits. Candidate-area metadata is separate from the synthetic event walkthrough; no live raster or real flood values are shown. All exports include a synthetic-fixture marker. Public-sector need is not customer demand; the project has no customer interviews, purchase intent, or procurement evidence.

## Run the local API

Python 3.12+:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn api.main:app --reload --port 8001
```

The API exposes the 16-area metadata-only candidate register and matched public-evidence profiles at `GET /api/study-areas`; analysis endpoints continue to return clearly labeled synthetic fixtures. To check it:

```sh
python -m pytest -q
```

Endpoints: `GET /api/health`, `GET /api/areas` (synthetic fixtures), `GET /api/study-areas` (metadata-only candidates), `POST /api/analyses`, and `POST /api/exports/csv`. This local Starlette API is not connected to the hosted static walkthrough and does not perform raster or NASA ingestion.

## Local OPERA raster analysis

The offline processor `scripts/analyze_opera_geotiffs.py` computes per-observation BWTR QA coverage and asset water fractions from local, operator-supplied GeoTIFFs. It does not log in to NASA, download files, or verify file authenticity. It requires OPERA DSWx-S1 V1's `BWTR_Binary_water` band: 0 is valid non-water, 1 is valid water, and 250/251 plus fill/no-data are missing. The separate multi-class WTR layer has class 3 for inundated vegetation; it is not accepted in the binary band. Unexpected classes fail the observation gate. The processor requires projected metre CRS and nominal 30 m posting. See the NASA [DSWx-S1 product specification](https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_DSWx-S1_Product_Spec_v1.0.0_D-108761_RevA_2024-08-16_.pdf) and [Earth Engine catalog band table](https://developers.google.com/earth-engine/datasets/catalog/OPERA_DSWX_L3_V1_S1).

Install the development environment with `pip install -r requirements-dev.txt`. Provide a single-feature AOI GeoJSON, asset FeatureCollection GeoJSON, and a manifest CSV containing `path,band,acquired_at,selection_anchor,period,granule_id,product_version,processing_version,retrieved_at`; set `band` to `BWTR_Binary_water` for every row. Record the processing version from source product metadata and retrieval time as ISO-8601 with timezone. Paths must remain inside the manifest directory; duplicate acquisition dates must be mosaicked before analysis. Example:

```sh
python scripts/analyze_opera_geotiffs.py \
  --manifest /path/to/site/manifest.csv \
  --aoi /path/to/site/aoi.geojson \
  --assets /path/to/site/assets.geojson \
  --output-dir /path/to/site/analysis-output
```

The default gate is at least 80% valid pixels over the AOI and each asset, and at least three qualifying dates in each predeclared event and baseline period. Selection uses the same count in both periods, choosing observations nearest each predeclared period anchor, then earliest date, then granule ID. Outputs retain source-file SHA-256, selected dates, quality fractions, and an explicit unverified local-input label. The script does not establish independent flood truth, damage, or operational impact.

To re