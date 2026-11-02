# ATLAS Scoped Specification (pre-implementation)

Blueprint: shared v1.1 clarification. Status: this specification describes the intended bounded study; a synthetic demonstration was implemented and privately deployed, while research implementation gates remain open.

## Product statement

ATLAS is a research/demo workflow for screening infrastructure assets against observed surface-water extent in a selected historical event. It reports observed spatial overlap and data quality/coverage with traceable source evidence. It does not determine damage, service disruption, structural failure, loss, or causality.

## Initial study design

- Texas case: Houston/Harris County area as candidate only; select event/date only after OPERA archive query confirms coverage and a defensible independent label source. Prefer a documented event/time with enough acquisitions to compare a single scene and temporal aggregation.
- Held-out validation: a distinct US region and event, selected before parameter tuning based on equivalent data and independent label availability. No random neighboring-pixel split.
- Singapore/Dubai: later coverage assessment only; no supported coverage claim.
- Asset data: start with explicitly synthetic points/lines/polygons. Replace with a small public dataset only after license, attribution, redistribution, update date and completeness review.
- Observations: OPERA DSWx-S1 or HLS selected according to event conditions and collection coverage, pinned to exact V1 collection/product and software version. Do not combine sources without a declared harmonization protocol. NISAR and DSWx-NI excluded from initial scope.

## Workflow and outputs

1. Choose a documented event and supported area preset.
2. Load supplied synthetic/public assets and disclose source/version/license.
3. Query or replay approved observation granules; show acquisition/processing/retrieval dates, resolution, sensor, source product, quality masks and valid coverage.
4. Establish baseline from documented pre-event observations appropriate to the area/season; document window and selection. Compare a single-observation threshold baseline with predeclared quality-aware temporal aggregations.
5. Calculate per-asset observed overlap fraction/area and valid pixel coverage; rank only with disclosed score and uncertainty/missingness. Preserve an unknown state for inadequate data.
6. Inspect map, source evidence and per-asset values.
7. Export CSV/GeoJSON and a report/manifest containing versions, timestamps, units, methodology, limitations, source attribution/license and checksums.

## Research protocol before tuning

Primary unit: asset-event observation. Pixel-level inundation classification evaluated separately from asset-level ranking. Candidate classification metrics: precision, recall, IoU and valid-data coverage; Brier score/reliability only if output is interpreted as probability and appropriately calibrated. Ranking metric: preselected NDCG@k or top-k recall, compared to held-out event/region; select one primary ranking metric before tuning. Record uncertainty intervals with spatial/event block resampling where feasible. Freeze test regions/events. Choose spatial blocks using empirical autocorrelation analysis or conservative geographic units; no random pixel split. Use labels independent of OPERA (e.g. agency field/flood delineation or independently interpreted finer-resolution imagery) and record label date, resolution, positional error and adjudication protocol. If no independent labels exist, do not make accuracy/improvement claims; publish feasibility/coverage only.

Temporal aggregation variants, thresholds, minimum valid observations and missing-data treatment must be preregistered in a dated protocol before inspecting held-out outcomes. Main comparison: single best-matched observation threshold vs quality-filtered temporal summary over a fixed event window, measured on identical assets and labels. No result can be assumed superior.

## Data and provenance schema

Observation: product short name/collection version, granule ID, product/software version, sensor, acquisition timestamp, processing timestamp, retrieved timestamp, spatial posting, CRS, transform, layer names, mask definition, source URL, license/attribution, checksum, file size. Asset: stable local ID, geometry type/CRS, source and version/license or synthetic flag. Analysis: code revision, config hash, AOI, date window, baseline definition, threshold, QA policy, alignment method, execution environment, job timings and outputs. Report uncertainty and valid-data ratio per asset.

## Project-specific acceptance rubric

The shared 100-point scorecard is adopted with criteria pending. Before implementation begins, write a measurable test condition and artifact for each item below. Each sub-item earns 5 or 0/pending; author-only evidence is provisional until clean CI or independent reproduction.

- Functionality 20: historical event reproduced; asset evidence inspected; supported area changed; traceable export completed.
- Reliability 15: failed job recovers visibly; repeated request is idempotent; backup/restore or local artifact recovery is demonstrated.
- Security 20: server-side access control appropriate to declared deployment; input/SSRF/resource-limit attacks rejected; tenant isolation only if multi-tenant scope exists; dependency/secret scans clean with findings handled.
- Performance 10: predeclared raster job latency and throughput/cost target met on fixed dataset and environment.
- Usability 10: task completion study with defined task/sample and accessibility checks; report actual sample and failures.
- Documentation/reproducibility 15: clean-checkout reproduction; API/operator docs; complete evidence provenance.
- Scalability 10: declared workload/load test and capacity/cost model within stated bounds.

Current score: 45/100, author-verified and provisional. See SCORECARD.md for per-item evidence, exact test command, environment and outstanding criteria. The deployed demo uses synthetic fixtures; no score implies scientific validity or commercial confidence.

## Release criteria and gaps

G0 complete only when both reviews, evidence register, bounded scope and rubric are committed. G1 requires local vertical slice and required tests from TECHNICAL_REVIEW. G2 requires held-out evaluation and independent reproduction. Cloud deployment remains gated on current docs, cost/account verification and authorization. No release claim of global coverage, operational response, asset damage, loss estimation, validated temporal superiority, customer demand or institutional endorsement.
