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

The offline processor `scripts/analyze_opera_geotiffs.py` computes per-observation WTR QA coverage and asset water fractions from local, operator-supplied GeoTIFFs. It does not log in to NASA, download files, or verify file authenticity. OPERA DSWx-S1 V1 WTR classes are parsed as water `{1, 3}`, valid non-water `{0}`, and masked/no-data `{250, 251, 255}`; other classes fail the observation gate. The processor requires projected metre CRS and nominal 30 m posting. See the NASA [DSWx-S1 product specification](https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_DSWx-S1_Product_Spec_v1.0.0_D-108761_RevA_2024-08-16_.pdf).

Install the development environment with `pip install -r requirements-dev.txt`. Provide a single-feature AOI GeoJSON, asset FeatureCollection GeoJSON, and a manifest CSV containing `path,acquired_at,selection_anchor,period,granule_id,product_version,processing_version,retrieved_at`. Record the processing version from source product metadata and retrieval time as ISO-8601 with timezone. Paths must remain inside the manifest directory; duplicate acquisition dates must be mosaicked before analysis. Example:

```sh
python scripts/analyze_opera_geotiffs.py \
  --manifest /path/to/site/manifest.csv \
  --aoi /path/to/site/aoi.geojson \
  --assets /path/to/site/assets.geojson \
  --output-dir /path/to/site/analysis-output
```

The default gate is at least 80% valid pixels over the AOI and each asset, and at least three qualifying dates in each predeclared event and baseline period. Selection uses the same count in both periods, choosing observations nearest each predeclared period anchor, then earliest date, then granule ID. Outputs retain source-file SHA-256, selected dates, quality fractions, and an explicit unverified local-input label. The script does not establish independent flood truth, damage, or operational impact.

To require equal usable-date counts across the complete 16-area program, use `scripts/audit_study_area_balance.py` with a 16-area JSON package. Start from [the study package template](outputs/atlas-study-package-template.json), replace the local paths with authorized raster, AOI, asset, and manifest files, then run:

```sh
python scripts/audit_study_area_balance.py \
  --study-package outputs/atlas-study-package-template.json \
  --output-dir /path/to/balanced-study-output
```

The balance gate checks every registered area and every provided asset; if any area has fewer than 3 qualifying dates in either period, it marks the full study insufficient and emits no cross-area water-fraction comparison. A passing gate only establishes matched data sufficiency. Independent event labels and accuracy evaluation remain necessary.

A separate real-input technical run is packaged at [outputs/atlas-texas-raster-pilot](outputs/atlas-texas-raster-pilot/README.md). It uses six publicly available preliminary NASA ARIA/OPERA response mosaics near Kerrville, outside the 16 registered study areas. The pipeline processed the rasters but withheld the comparison because only two dates per period passed the preregistered 80% valid-pixel rule. NASA labels these response products preliminary and unvalidated; this pilot is not a study result or a validation of any registered candidate.

## Multi-cloud deployment preparation

The API now has a container image and a shared restricted Kubernetes deployment baseline intended for Google Kubernetes Engine, Amazon EKS, Azure Kubernetes Service, and Oracle Kubernetes Engine. Review [the multi-cloud preparation and release gates](outputs/atlas-multicloud-deployment-preparation.md) and the common [release runbook](deployment/cloud/RELEASE_RUNBOOK.md) before provisioning. The machine-readable [provider parity matrix](deployment/cloud/provider-matrix.yaml) defines identical account, OIDC, identity-denial, private-network, artifact, runtime, recovery, and staging E2E gates, with provider-specific evidence mappings. The owner reports that account creation is underway; no account readiness or billing configuration is verified, and no cloud resources have been created. Provider IaC and deploy workflows, identity/network/secret bindings, remote CI, and staging remain pending. The shared local verification workflow and hash-locked runtime, development, and audit dependencies are prepared.

Build the local image with `docker build -t atlas-api:local .`. Do not deploy the fixture API as a real flood-analysis service: all returned analysis values are synthetic.

## Evidence and limits

See `STUDY_AREA_PROGRAM.md`, `EVIDENCE_REGISTER.md`, `TECHNICAL_REVIEW.md`, `COMPETITIVE_REVIEW.md`, and `SPECIFICATION.md`. `scripts/screen_study_areas.py` reproduces the common 25 km × 25 km CMR metadata screen and writes candidate counts; metadata hits are not QA-valid scenes or independent flood labels. OPERA product metadata and schema references do not make the fixture data real. NASA Earthdata credentials were not supplied. Do not interpret observed water as proof of damage, service interruption, structural failure, or financial loss.
