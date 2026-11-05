# ATLAS Scoped Specification

Blueprint: shared v1.1 clarification. Status: a private synthetic-data walkthrough is deployed. The 8+8 areas below are evidence-screened candidates; comparable observation and independent-validation gates remain open. The canonical current score is recorded in `SCORECARD.md`.

## Product statement

ATLAS is a research/demo workflow for screening infrastructure assets against observed surface-water extent in a selected historical event. It reports observed spatial overlap and data quality/coverage with traceable source evidence. It does not determine damage, service disruption, structural failure, loss, or causality.

## 8+8 candidate study design

The current purposive, stratified candidate set comprises eight U.S. areas—Houston, Miami, Tampa, New Orleans, New York City, Sacramento, Atlanta, and St. Louis—and eight international areas—Jakarta, Singapore, Dubai, Mumbai, Bangkok, Tokyo, Manila, and São Paulo. The register and `STUDY_AREA_PROGRAM.md` document for each area its empirical public need, research rationale, value-integration question, validation path, and evidence limits. Selection prioritizes verifiable flood-management or research need, urban infrastructure relevance, and discoverable metadata in one common 25 × 25 km footprint; technology-hub status is context, not proof of hydrologic need or customer demand.

All candidates use the same nominal 625 km² footprint, OPERA DSWx-S1 V1 metadata window, quality definitions, measurement units, reporting fields, and enrollment rules. Metadata discovery and auxiliary Sentinel-1 RTC coverage are not observations of inundation. The temporal audit found no acquisition date common to all 16 areas. For any confirmatory cross-area comparison, choose event-relative windows from an independently defined event frame, require QA-valid event and baseline scenes in every enrolled area, select an equal number of qualifying scenes per area, preserve missingness, and withhold the comparison if any area fails. The current feasibility floor of at least three scenes per period with at least 80% valid pixels is not a claim of statistical power; report sensitivity to stricter coverage and achieved sampling precision.

Enrollment additionally requires a spatially representative probability sample of the fixed AOI and evaluated assets, independent and appropriately licensed reference labels, two blinded labelers with adjudication, a frozen protocol before confirmatory outcomes are inspected, and a held-out event/area design. Exclude same-sensor or otherwise dependent sources from independent-truth claims. If labels or usable scenes are missing, report feasibility and data coverage only; do not infer flood accuracy, damage, loss, buyer demand, or operational impact. See `data/validation_protocol.yaml` and `outputs/atlas-independent-reference-data-plan.md`.

Asset data begin as explicitly synthetic fixtures. Any public or partner data require documented geometry/date completeness, license, attribution, redistribution terms, and provenance before analysis. Do not combine observation products or label sources without a declared harmonization and lineage protocol.

## Value integration

Keep the public-value chain distinct and evidence-backed: (1) observed hazard class and quality; (2) asset exposure and geometry completeness; (3) service criticality, population served, and dependencies only when supported by licensed, attributable data and relevant agency/community review; (4) distributional coverage and missingness only where lawful, privacy-preserving, and locally governed; and (5) documented decision usefulness. Unknown values stay unknown. Do not apply stakeholder-weighted composite scores without approved weights and sensitivity analysis. The candidate register records location-specific integration questions and limitations; public investment or management need does not establish ATLAS purchasing demand.

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

Current score: 60/100, author-verified and provisional, as detailed in `SCORECARD.md`. The deployed demo uses synthetic fixtures. No score implies scientific validity, independent reproduction, customer demand, or commercial readiness.

## Release criteria and gaps

G0 requires both reviews, the 8+8 evidence register, bounded scope, and rubric. G1 requires the local vertical slice and tests from `TECHNICAL_REVIEW.md`. G2 requires adequately sampled, held-out event evaluation and independent reproduction. Google Cloud, AWS, Azure, and Oracle deployments require verified owner account/billing/region choices, federated release identity, common security controls, private staging, recovery, workload/cost evidence, and provider-hosted end-to-end checks. Apple app distribution is a separate release target from the private browser Site and cloud backend; it requires a native app target, full Xcode, verified Apple Developer Program/App Store Connect access, signing, and TestFlight/device checks. No release claim of global coverage, operational response, asset damage, loss estimation, validated temporal superiority, customer demand, or institutional endorsement.
