# ATLAS Scorecard

Updated: 2026-11-02. Scope: privately hosted synthetic walkthrough plus local fixture API. Shared blueprint v1.1 clarification applies: each criterion earns 5 points or 0/pending. Product score is separate from scientific validity, customer validation and readiness for production.

**Current score: 55/100, author-verified and provisional.** No independent reproduction has occurred. The score follows the strict 5-point criterion rule. A deployment does not make synthetic data into a historical observation and does not earn unrelated reliability or scale points.

| Category | Points | Evidence and result |
|---|---:|---|
| Functionality | 15/20 | Three bounded demo criteria pass: supported scenario/area interaction; synthetic method comparison and asset inspection; labeled CSV exports. The 5-point real pinned historical-observation workflow is pending; no real raster or event has been reproduced. |
| Reliability | 5/15 | Identical API analysis requests return identical results (test below). Recovery and restore have no qualifying evidence; the prototype has no persistent analysis store. |
| Security | 15/20 | Private Site access control (5), API input/body/host/CORS boundary checks (5), and hash-locked dependency plus secret scanning (5) pass. Production API authentication/isolation remains pending. |
| Performance | 5/10 | Local fixture API sequential p95 target (<100 ms) passed; the separate throughput/cost criterion remains pending because there is no cost model for deployed raster workloads. |
| Usability | 0/10 | The previous 4-point partial credit is removed to follow the shared rubric's 5-or-0 rule. Focused author accessibility checks do not satisfy the task-study criterion or full accessibility acceptance condition. No screen-reader or task-based user study has been run. |
| Documentation and reproducibility | 15/15 | API/operator documentation, complete evidence provenance, and clean-checkout reproduction pass. The clean checkout was verified by the author; independent reproduction has not occurred. |
| Scalability | 0/10 | No declared-load test or capacity/cost model. |
| **Total** | **55/100** | Author-run evidence; not independently reproduced. |

## Verification record

- Initial local API smoke/test snapshot: `.venv/bin/python -m pytest -q` — **7 passed** on macOS/Python 3.9, project commit `44741a7`. Superseded by the current 31-test suite and the clean-checkout run below; retained as historical evidence.
- Live local API smoke: `/api/health` returned 200 with `live_nasa_ingestion:false`; aggregate analysis returned 200 with 12 synthetic records; CSV export returned 200 with 12 records plus header.
- Browser walkthrough: method switch changed from 28.6% to 21.4% for the lead fixture asset and median changed from 7.7% to 6.8%; asset detail changed on row selection; alternate preset updated area, event, event/baseline dates, map labels and LA fixture IDs; CSV export produced a success toast.
- Hosted Site: version 12 is deployed successfully to the private production URL; Sites readback confirms active owner-only access with zero external visitors. Version 12 includes the evidence profiles and demand disclaimer; full workflow walkthrough history is recorded in `outputs/atlas-deployment-test-results.md`.
- Kubernetes policy and resource-control source passed private GitHub CI on commit `bb0f1f1ccdca0f5c262510fbd0869886fbdfa815` in [run 41551001149](https://github.com/Shawdaimarie/atlas-water-screening/actions/runs/41551001149). This verifies repository checks, not live CNI enforcement or cloud deployment. Independent reviewer reproduction remains pending.
- Additional live E2E pass on 2026-11-02: quality-aware comparison, Baton Rouge/Hurricane Ida scenario, Singapore profile, area-register export, evidence export, single-scene baseline and reset were observed on the authenticated deployed Site. See `outputs/atlas-deployment-test-results.md`. This confirms demo flows only and does not increase the strict criterion score.
- Earlier hash-locked target run — **27 passed in 0.68s** (Python 3.12 environment using `requirements-dev.lock`), including API input boundaries, offline register/intersection checks, synthetic WTR GeoTIFF class/coverage checks, and the 16-area global balance gate. This was followed by the 31-test suite and clean-checkout reproduction recorded below. No study area passed real-data QA.
- Latest read-only ARM64 container smoke — **11/11 checks passed**, including `/api/study-areas` returning 8 U.S. and 8 international candidates, metadata-only status, fixture analysis, CSV, request boundaries, host allowlist, and CORS behavior. Local image tag `atlas-api:goal-2026-11-02`, image ID/digest `sha256:5b23d5c85b0f208fed73a17c62630110273042e33e5323d4bdcba43ebe4ba3f4`. This is not a cloud deployment test.
- Latest live Site v12 E2E replay: all 16 candidate profiles selected successfully; quality-aware method changed synthetic results; Baton Rouge/Hurricane Ida updated the scenario; evidence and register exports showed success; reset restored the single-scene baseline and Houston/Beryl was restored. Site readback confirmed active version 12 and owner-only access. This replay awards no new points because the existing functionality criteria already cover these demo workflows. Candidate profiles do not validate real pixels.
- Current local suite: `.venv/bin/python -m pytest -q` — 40 passed, including static provider-parity, Kubernetes default-deny/network and resource-control checks, offline STAC pagination/date-deduplication, cloud-input readiness/secret-field validation, and all-16-area Earth Engine script/register parity checks. Secret scan passed. These checks do not validate live cloud enforcement or execute Earth Engine.
- Default test-discovery fix: pytest now limits collection to `tests/` so it skips the archived clean checkout under `work/`. The current suite passes **36 tests**, including input preflight tests. No rubric points changed.
- Supplementary SAR coverage audit (2026-11-02): Planetary Computer Sentinel-1 RTC STAC metadata covered all 16 AOIs with 55–442 scene items and 55–280 dates each; no exact date was common to all, although 25/27 represented months had metadata in every area. No raster pixels were inspected and this is the same Sentinel-1 sensor lineage as OPERA, so the result earns no validation or score points. See `outputs/atlas-sentinel1-rtc-coverage-audit.json`.
- Cloud onboarding preflight (2026-11-02): `scripts/validate_cloud_inputs.py --example` fails closed on the blank template with 25 missing/invalid setup requirements; the ignored owner input file is absent. Unit tests cover four-provider IDs, billing/regions/budget, OIDC release flags, and secret-like key rejection. It is a local input check only, not live account validation; no score points.
- Clean-checkout reproduction: fresh detached worktree at commit `73eac66103db64c61f54172ad76fba8157a6b10c`; installed `requirements-dev.lock` with `--require-hashes` in a fresh Python 3.12 ARM64 container (`python:3.12-bookworm@sha256:a5bab0ff300f91231c2e68bf73a8a8d60762ac39ce1c50eaf6803e4c38a9062b`); `python -m pytest -q` — 31 passed in 0.70s. Author-run, not independent.
- Local HTTP security smoke on 2026-11-02: valid synthetic analysis returned 200/12 assets; an unknown `image_url` field returned 422; a 16,385-byte request returned 413 with the 16,384-byte limit disclosed. A separate ASGI test verified the limit without `Content-Length`. This covers the local fixture API only.
- Local API latency benchmark: `.venv/bin/python scripts/benchmark_fixture_api.py` — predeclared target sequential p95 <100 ms; 25 warmups, 500 measured sequential requests. Current hardened API result: median 1.087 ms, p95 3.246 ms. Under 8 workers, 1,000 concurrent requests completed in 1.451 s (689.07 requests/s, p95 21.275 ms). This local synthetic JSON fixture result earns latency only; it excludes raster work, network latency, billed cloud cost, and production capacity. Raw result: `outputs/atlas-performance-benchmark.json`.

## Security verification

The current dependency audit, secret scan, and remote GitHub CI pass for the hash-locked container candidate. Cloud release still requires provider identity and network configuration, deployed authentication/isolation checks, cloud OS image scanning, signed SBOM/provenance, recovery, and capacity tests. See outputs/atlas-security-scan-findings.md.

## Remaining points to earn

Complete held-out real-event data and labels; actual raster ingest and provenance; meaningful recovery/restore evidence; deployed API authorization and isolation review; cloud throughput/cost and declared-load evidence; usability/accessibility checks; independent review. Do not award points until corresponding artifacts and results are attached.


## Expanded study-area verification (2026-11-02)

- The reproducible script `scripts/screen_study_areas.py` queried public CMR metadata for all 16 candidate areas using OPERA DSWx-S1 V1, a common 2024-09-01 through 2026-11-02 UTC window, and nominal 25 × 25 km boxes. The query returned all pages for each area. All 16 met a 90-distinct-date metadata-discovery screen: U.S. 8/8; international 8/8. Distinct dates range from 99 to 403; this is not comparable valid-pixel coverage.
- `scripts/audit_temporal_overlap.py` computes intersections from the saved full per-area date sets: zero exact dates are common to every AOI, while 24 of 26 year-month periods represented have at least one archive metadata date in every AOI. This supports event-relative matched-count design but does not prove event alignment or valid pixels. The version 9 panel discloses this result and the area-register export includes every per-area date.
- The deployed candidate register shows 8 U.S. and 8 international areas, location-specific rationale, a public evidence link, metadata metrics, a value-integration question, and an explicit pending-validation state. It does not present CMR hits as observed flood scenes.
- Enrollment rule documented for later real analyses: at least 3 QA-valid observations in event and baseline windows, each ≥80% unmasked across AOI and each evaluated asset; use the same count and selection rule across enrolled sites. Independent reference labels are still required. These thresholds are preregistered design gates, not achieved results.
- Public agency and World Bank sources demonstrate public management/research need, not ATLAS customer demand, purchase intent, or endorsement.
- Independent-reference discovery update (2026-11-02): Copernicus EMS public catalogs were screened against the 16 fixed AOIs. No coarse AOI-bounds overlap appeared in the current rapid-mapping flood feed; the broader catalog had one approximate Manila-centroid candidate from 2012, which is not a current-window overlap or validation label. The global MODIS flood archive covers 2000–2018 only. No area has independent labels; score remains unchanged. Method and limitations are documented in `outputs/atlas-independent-reference-data-plan.md` and raw API discovery is in `outputs/atlas-cems-event-discovery-audit.json`.
- Point-level reference audit (2026-11-02): inspected 33,141 published GFD/Landsat analyst-validation points across 123 DFO events against all 16 fixed study AOIs. Sacramento is the only AOI with points (8; one event ID); their Landsat assessment is dated 2018-06-26, while the linked flood interval is 2017-02-16 to 2017-03-03. They fail contemporaneous event matching and sampling adequacy. The other 15 AOIs have zero points. No additional score; details are in `outputs/atlas-global-flood-db-validation-audit.json`.


## Focused accessibility review

- Reviewed the live v7 page against selected WCAG 2.1 AA checks for contrast, keyboard access, names/labels, and touch target size.
- Remediated muted secondary text contrast (representative measured ratios now 5.87:1 on white and 5.44:1 on the method card; warning text 5.04:1), added visible focus styling, and set interactive buttons/selects and area choices to a 44 px minimum height.
- Live keyboard check: Tab reached scenario, event, reset, export, register download, then area choices; Enter selected Miami and updated the profile.
- This is a focused author-run review, not a conformance certification. VoiceOver/NVDA, 200% zoom, exhaustive contrast pairs, and task-based usability remain outstanding. Full notes: `outputs/atlas-accessibility-review.md`.


## Real-raster pipeline pilot (2026-11-02)

- Ran the offline analyzer over six public NASA JPL/Caltech ARIA/OPERA DSWx-S1 binary-water response mosaics for the July 2025 Central Texas flood. This is a Kerrville-area technical AOI outside the 16 registered study sites; the accompanying 600 m geometry is a QA test cell, not infrastructure.
- With the preregistered ≥80% valid-pixel and ≥3-date-per-period gates unchanged, only 2/3 dates qualified in baseline and 2/3 in the event period. The system withheld the comparison and returned `unknown_insufficient_qa_valid_dates`.
- NASA labels this response product preliminary and unvalidated. Its processing-software version was not reported by the response page or TIFF tags; the manifest records this uncertainty. No independent reference labels or asset geometry were used.
- This provides a real-input pipeline and fail-closed gate demonstration. It does not satisfy the complete historical observation workflow or any additional rubric criterion. Score remains **55/100 provisional** after clean-checkout reproduction; the added points are documentation/reproducibility only, not scientific validation. Reproduction package: `outputs/atlas-texas-raster-pilot/`.
