# ATLAS Deployment and Operations (demo)

## Current deployment

- Hosted walkthrough: [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site)
- Audience: private, owner-only Sites access. The first visit requires ChatGPT sign-in. The owner completed ChatGPT sign-in after the profile-sharing disclosure and the private site loaded in the owner browser. Do not make this site public without separate authorization.
- Deployment type: static walkthrough with client-side synthetic fixture behavior. It does not deploy the Starlette API.
- Local API: `uvicorn api.main:app --host 127.0.0.1 --port 8001`; local only, no persistent records and no external data retrieval.
- Current dataset mode: synthetic fixture. The public-facing UI discloses this and labels all event dates illustrative. No NASA credentials or granules are configured.
- Cost: no deployment price or account usage evidence was available. The USD 50/month project target has not been verified or measured; no spend is authorized by this record.

## Run locally

See `README.md`. The static page runs from `dist/`. The API runs separately from the project root and exposes health, synthetic fixture areas, the metadata-only 16-area study register, synthetic analyses, and CSV export. The UI does not call the API yet.

## Operational limits

There is no queue, database, object storage, user-upload path, tenant data, live ingestion, backup/restore process, alerting, service-level objective or rollback drill. The Site provider manages static hosting; the project has not independently verified its resilience or operating cost. For a demo issue, redeploy the last known good saved Site version through Sites and retest the URL; this rollback path has not been exercised.

## Next deployment gate

Before promoting beyond a private demo: connect the UI to a production-grade API; verify source data access/license/version; establish cost and quotas; implement bounded processing and provenance; complete privacy/access, security, restore, monitoring and rollback checks; then document the actual environment and run G1/G2 evidence.

## Multi-cloud preparation

See `outputs/atlas-multicloud-deployment-preparation.md` and `deployment/cloud/RELEASE_RUNBOOK.md` for the common restricted-container/Kubernetes baseline targeting GKE, EKS, AKS, and OKE. `deployment/cloud/provider-matrix.yaml` captures the equivalent identity, registry, and release controls. No provider account was accessed or provisioned. The Starlette fixture API image is locally smoke-tested and audited only; provider IaC, identity trust setup, registry, ingress, cloud cost, and staging releases remain pending.

The WTR raster analyzer is a separate local research path. It is not part of this API image or the private Sites frontend. Real-data launch still requires Earthdata-authorized granule access, a complete 16-area pixel-QA pass, independently sourced labels, and a cloud runtime sized and priced for raster work.
