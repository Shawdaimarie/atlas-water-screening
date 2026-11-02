# ATLAS Cost Model — Demo Boundaries

Updated: 2026-11-02. This is a cost-collection plan, not a provider quote or spending authorization.

## Current demo

| Component | State | Measured monthly cost |
|---|---|---|
| Private Sites static walkthrough | Deployed, owner-only | Unknown; no billing/usage evidence available |
| FastAPI fixture API | Local process only | No hosted compute charge; this is not a production comparison |
| NASA Earthdata / OPERA granules | Not accessed | No project-specific data transfer or storage measured |
| Postgres/PostGIS/object storage | Not provisioned | None measured |

The USD 50/month project target remains a design target only. Do not report the current demo as a verified <=USD 50 deployment.

## Production estimate inputs still required

- Chosen cloud region, Cloud Run service CPU/memory/minimum instances, request count and duration.
- Job count, raster pixels/bytes processed per job, maximum parallel jobs and retry rate.
- Object-storage bytes, retention, replication and egress; database instance/backup configuration and spatial query load.
- Logs/metrics retention, external imagery transfer, and any licensed asset costs.

Monthly run-rate model after these values are measured:

`service requests + bounded job CPU/memory time + storage + database/backup + egress + observability + licensed data`.

Before deployment, compare at least low/expected/peak workloads using current provider pricing pages, enforce quotas and job bounds, and add actual test run duration/cost evidence. No commitment or spend has been made here.
