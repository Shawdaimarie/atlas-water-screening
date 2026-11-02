# ATLAS Architecture Decisions

## ADR-001: Private static walkthrough for the first visible demo

Date: 2026-11-02 · Status: accepted for demo only

**Decision:** Publish a private static HTML/CSS/JavaScript walkthrough with client-side synthetic fixture data. Keep a separate FastAPI fixture API runnable locally. Do not claim the API, Postgres/PostGIS, raster storage, Cloud Run, React/TypeScript or MapLibre is deployed.

**Reason:** A visible end-to-end UI could be delivered using the connected Sites publisher despite the machine lacking the Google Cloud CLI and Node toolchain. The managed Site provides private owner-only access. Real NASA access, credentials, asset licensing, selected granules and independent labels are not available; therefore using fabricated data as live observations would misrepresent results.

**Consequences:** The static UI can demonstrate scenario selection, method comparison, ranking, fixture details and CSV export, but its figures are illustrative only. The FastAPI service is not connected to the UI or deployed. Cost, service limits and production controls are unverified. The original GCP/FastAPI/React/PostGIS/object-storage architecture remains the intended implementation target after dependencies and deployment access are verified.

**Revisit when:** event datasets/labels and NASA authorization are available, and a production API and geospatial processing deployment can be costed and secured.
