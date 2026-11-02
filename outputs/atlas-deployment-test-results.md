# ATLAS deployment and verification results

**Run date:** 2026-11-02\
**Production Site:** [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/) (private owner-only access)\
**Current published Site version:** 12
**Current source commit deployed:** `af1c7a315447588f6893279605f5c7b7ddbaa240`
**Version provenance:** Sites readback matched version 12 to this source commit and deployment `appgdep_6ae9164a45bc81919f19e1af0750b143`; archive hash `sha256:077b62bb99cdc3503f970af4878bac95bc0bdf9666e36b0492ac7a7946173844`.

## Result summary

The private static Site is deployed (version 12) and the study-area candidate register is visible and interactive. Its downloadable CSV contains the complete per-area acquisition-date sets, AOI bounds, collection, and query window. The current product remains a synthetic research walkthrough. The register is an archive metadata discovery screen; its scenes have not been downloaded or pixel-QA audited for the 16 enrolled candidates. Therefore the project is **not 100/100** and the study areas are not yet fully validated.

## Checks completed

| Check | Result | Evidence |
|---|---|---|
| Production publish | Pass | Sites returned `succeeded` for version 10; subsequent Site readback confirmed version 10, active status, private/custom access, and zero external visitors. |
| Access policy | Pass | Sites readback reports a custom allowlist containing only the owner. |
| U.S./international register | Pass | Live page contains 8 U.S. and 8 international candidate areas. |
| Candidate profile interaction | Pass | Selected Mumbai; rationale, value-integration question, 361 metadata hits, and 121 acquisition dates appeared. |
| Candidate register export | Pass | “Download area register” produced the visible “Study area register downloaded as CSV” success message. |
| Method comparison | Pass | Aggregate view changed the lead synthetic asset from 28.6% to 21.4%, elevated count from 4 to 3, and median from 7.7% to 6.8%; UI labels the result experimental/synthetic. |
| Area/event workflow | Pass | Switching to Baton Rouge changed to Hurricane Ida, event and baseline dates, map labels, and LA fixture IDs. |
| Asset detail | Pass | Selecting Southeast Water Plant updated detail values and asset ID. |
| Synthetic evidence export | Pass | Export button showed its success message with synthetic-data labeling and selected method. |
| Reset workflow | Pass | Reset restored the single-scene baseline values and method labels. |
| API and metadata unit tests | Pass | Current suite `.venv/bin/python -m pytest -q`: 14 passed in 0.98s; includes API fixtures, request-boundary checks, and offline study-area date-set checks. |
| API HTTP smoke | Pass | Live local API: health and area listing returned 200; single, aggregate, alternate-area analysis returned 200 with 12 records; CSV returned 200 with 12 records and a header. Health explicitly reports `live_nasa_ingestion:false`. |
| Static/document checks | Pass | HTML parser accepted the deployed source; structural checks confirmed exactly one study-area panel and 16 records with 8 per region. |
| Focused accessibility checks | Pass with documented limits | Updated muted-text colors measure 5.87:1 on white, 5.44:1 on the method card, and 5.04:1 for warning text. Keyboard Tab/Enter selected Miami and updated its profile. Touch targets and focus styling were improved; VoiceOver/NVDA and zoom review remain open. See `atlas-accessibility-review.md`. |
| CMR metadata screen | Pass for discovery only | Reproducible query returned complete result pages for 16 equal nominal 625 km² AOIs using the common DSWx-S1 V1 window. All exceeded the 90-date metadata screen; distinct acquisition dates ranged from 99 to 403. |
| Temporal overlap audit | Pass for metadata only | Exact `time_start` date intersection is empty across all 16 AOIs. Every AOI has at least one metadata date in 24 of 26 year-month periods represented across the candidates. Reproducible from saved date sets. No claim of same-day or equal pixel-valid coverage. |
| Full-date register export | Pass for metadata only | Version 10 retains all 3,047 per-area dates; the export includes AOI coordinates/bounds, collection, time window, counts, dates, rationale, value-integration question, source, completeness and pending-validation status. Production click was confirmed by a success message; the same date values are independently present and count-checked in local CSV/JSON artifacts. |
| Fixture API request-boundary checks | Pass locally | Over HTTP: valid analysis 200/12 rows; unexpected `image_url` field 422; 16,385-byte payload 413 with 16,384-byte limit. Unit test also exercises a streamed over-limit body without `Content-Length`. This local API is not deployed or connected to the Site. |

## Research design and limitations

- Area selection uses official/public evidence for flood-management relevance, infrastructure exposure, and integrated water planning. Evidence supports public research and management need; it does not establish ATLAS buyer demand, endorsement, or purchase intent.
- CMR hits and acquisition dates are discovery metadata. They do not show that pixels are usable, that an event was observed, or that an AOI has adequate valid coverage.
- The documented study enrollment rule requires at least three QA-valid observations in each event and baseline period, each with at least 80% unmasked pixels over the AOI and each asset footprint. Sites must use matched sample counts and the same selection rule. Independent field or authoritative reference labels remain required.
- Main map, event overlap, asset portfolio, coverage, and confidence values are generated synthetic fixtures. The local FastAPI fixture service is not deployed or connected to the static Site. A separate six-raster Texas pipeline pilot failed the predeclared three-valid-date minimum in each period and emitted no comparison; it does not validate any enrolled site or establish a historical flood result.

## Open requirements before a 100/100 claim

Real pinned OPERA raster ingest and provenance; event-specific QA coverage for each enrolled site; independent reference labels and a held-out event; asset geometries with reviewed licensing; deployed/connected geospatial API; recovery/restore evidence; deployed-API authorization and dependency/secret checks; cloud throughput/cost benchmark; accessibility/usability review; declared-load/capacity evidence; and independent reproduction. The strict current rubric score is 55/100, provisional and author-verified, as shown in `SCORECARD.md`.

## Guided walkthrough

1. Open the private [deployed ATLAS site](https://atlas-water-screening.shawdaimarie.chatgpt.site/).
2. In “16-area evidence and coverage screen,” select Jakarta, Dubai, Singapore, or Mumbai; inspect the linked evidence and explicitly pending-validation message.
3. Choose “Download area register” to get the complete CSV.
4. Scroll to “Compare screening methods,” select “Quality-aware aggregate,” then inspect the asset ranking and the synthetic-data notice.
5. Select a ranking row to inspect asset detail; switch the study scenario to see the alternate illustrative event; use “Reset analysis” to restore the baseline.

## Additional live walkthrough verification

**Run date:** 2026-11-02. Browser: Codex in-app browser, authenticated owner session, live production URL above. This was a second author-run pass; it is not an independent reproduction.

| Live action | Observed result |
|---|---|
| Open production page | Dashboard and all 16 study-area options rendered. Houston/Beryl is explicitly labeled synthetic; the candidate panel states pixel QA, event-matched scenes, asset geometry and independent labels remain pending. |
| Change method to quality-aware aggregate | Lead fixture overlap changed 28.6% → 21.4%; elevated assets changed 4 → 3; median changed 7.7% → 6.8%. UI labels it experimental and synthetic. |
| Change event to Hurricane Ida | Scenario changed to Baton Rouge; event and baseline dates updated to August 2021; asset IDs changed to LA; UI displayed a synthetic-data notice. |
| Exercise every study-area profile | All 16 candidate controls changed the visible profile and retained the candidate-only limitation. |
| Local test rerun | `.venv/bin/python -m pytest -q` — 14 passed in 0.98s on macOS/Python 3.9 venv, including four offline register/intersection checks; author-run, not independent. |
| Select Singapore | Profile showed 231 granule metadata hits, 163 distinct acquisition dates and a nominal 625 km² footprint. Primary PUB evidence, rationale and value-integration question were visible. Candidate-only limitations remained visible. |
| Download area register | Success message: “Study area register downloaded as CSV.” |
| Download evidence export | Success message: “Evidence export downloaded with synthetic-data label and method.” |
| Switch to single-scene baseline and reset | Baseline values returned (4 elevated assets; median 7.7%); reset success message appeared. |

The production page is left open to the Singapore profile in the authenticated browser for review. The current live state is still a demo view; it does not represent validated Singapore observations.

### Version 8 production regression

Version 8 deployed successfully from source commit `b8d2cd78fd7d03ff47d9a7280102dae6b9f5dc0b`. Version 9 deployed successfully from source commit `a4a65d06764aed5259fd860c4411f7e03feb644e`; Sites readback confirmed active status and unchanged owner-only access. The v9 browser run passed all 16 profile selections and the expanded register export confirmation; the page was left open to Singapore. Version 8's method/event/evidence-export/reset checks remain applicable because version 9 changed only embedded study metadata and CSV columns.

## Rubric clarification

The shared blueprint v1.1 clarification requires each rubric item to earn 5 points or 0/pending. Applying that rule consistently, the previous 41/100 total included partial credit for usability and documentation. A local fixture-API latency benchmark passed its predeclared p95 target, and bounded local API adversarial checks passed. The earlier strict criterion score was **45/100 provisional**: 15 functionality + 5 reliability + 10 security + 5 performance + 0 usability + 10 documentation/reproducibility + 0 scalability. See `SCORECARD.md` for criterion definitions and the evidence behind each award.

## Local performance benchmark

- Command: `.venv/bin/python scripts/benchmark_fixture_api.py`; API served by local Uvicorn at `127.0.0.1:8017`.
- Predeclared latency acceptance: sequential analysis-response p95 under 100 ms for the synthetic 12-asset JSON fixture after 25 warmups and 500 requests.
- Result: pass; median 1.087 ms, p95 3.246 ms. A separate 1,000-request, 8-worker run completed in 1.451 s (689.07 requests/second, p95 21.275 ms).
- This is a local synthetic API measurement. It does not establish raster processing performance, cloud latency, cost, production capacity, or a scale score. Raw result: `atlas-performance-benchmark.json`.

## Comparable-coverage artifacts

- Requery the common metadata screen: `python3 scripts/screen_study_areas.py`.
- Recompute temporal intersections: `python3 scripts/audit_temporal_overlap.py`.
- Rebuild the full-date CSV: `python3 scripts/export_study_area_register.py`.
- Test all saved counts/intersections offline: `.venv/bin/python -m pytest -q`.
- The exact per-area CMR dates are in `atlas-study-area-register.json` and CSV; the cross-area audit is in `atlas-temporal-overlap-audit.json`. This is archive metadata evidence only, not observational QA.

## Current live version 12 walkthrough verification

**Run date:** 2026-11-02. **Production version:** 12. **Deployment:** `appgdep_6ae9164a45bc81919f19e1af0750b143` (`succeeded`). **Deployed source:** `af1c7a315447588f6893279605f5c7b7ddbaa240`. Browser check used the authenticated owner session on the live production Site; this is author-run, not independent.

| Live action | Result |
|---|---|
| Load and inspect the version 12 Site | Pass. Houston/Beryl dashboard and all 16 candidate choices rendered. The UI explicitly labels analysis inputs synthetic and candidate areas metadata-only with pixel QA and independent labels pending. |
| Select each candidate profile | Pass, 16/16. Each U.S. and international profile became selected and showed its matching city heading; the final panel retained pending-validation and demand-limit disclosures. |
| Select Singapore | Pass. Profile displayed PUB rationale, value-integration question, 231 metadata hits, 163 distinct dates, and the 625 km² nominal box. |
| Change analysis method | Pass. Quality-aware aggregate changed the lead synthetic overlap from 28.6% to 21.4%, elevated fixture count from 4 to 3, and median from 7.7% to 6.8%; the interface disclosed the result was experimental and synthetic. |
| Change scenario to Baton Rouge / Hurricane Ida | Pass. Selected area/event, event and baseline windows, scenario heading, schematic map label and fixture portfolio changed together. |
| Export evidence | Pass. UI reported “Evidence export downloaded with synthetic-data label and method.” |
| Export candidate register | Pass. UI reported “Study area register downloaded as CSV.” The retained local register is separately count-checked at 16 rows (8 U.S., 8 international). |
| Reset and restore the starting walkthrough | Pass. Reset returned the method to the single-scene baseline (median 7.7%, 4 elevated fixtures); the scenario selectors were then restored to Houston/Beryl. |
| Verify publication/access | Pass. Sites readback reports active version 12, successful production deployment, custom owner-only allowlist for `shawdaimarie@gmail.com`, and zero external visitors. |
| Latest source CI | Pass. [GitHub Actions run 41544931776](https://github.com/Shawdaimarie/atlas-water-screening/actions/runs/41544931776) succeeded on commit `58acb5a6ccd86c49d8091901faa5f361f36255c0`. |

The authenticated browser is left open on the live Site with the Houston/Beryl synthetic analysis visible and the São Paulo candidate profile selected. These checks demonstrate the deployed walkthrough and its exports; they do not demonstrate cloud-hosted API behavior, real water observations, candidate-area pixel QA, or independent labels. No additional rubric points are awarded by this replay; the score remains 55/100 provisional.



## Latest verification refresh

- On 2026-11-02, Sites readback confirmed production deployment `appgdep_6ae8feb057fc819198db222b7d3f638c` is `succeeded`, URL is the private ATLAS production URL, Site is active at version 9, and access remains custom owner-only.
- The local test suite was rerun after the latest source changes: 14 passed in 0.98s. The latest local benchmark is captured in `atlas-performance-benchmark.json`; values above reflect that run.

## Current checkout verification refresh (2026-11-02)

- Read-only Sites state: active production Site version 12, custom allowlist with one allowed viewer (the owner), zero external visitors.
- After the GFD/Landsat point-coverage audit was added, `.venv/bin/python scripts/audit_gfd_validation_coverage.py` regenerated the pinned-source report with 33,141 points, 123 events, and matches in 1/16 AOIs; that Sacramento match is temporally unsuitable and under-sampled.
- The first default pytest run recursively collected duplicate modules from `work/atlas-clean-checkout/` and failed during collection. Added `pytest.ini` with `testpaths = tests` to keep the archived reproduction out of current test discovery. The current suite passes 36 tests in 0.70s, including the STAC audit and cloud-input preflight tests.
- The four-provider preflight command against the blank example failed closed with 25 missing/invalid setup requirements and reported that no resources were created. The owner-only local handoff file does not exist, so no provider account readiness, billing, region, Apple-account role, or budget choice is verified.
- Remote CI passed on the current source, audit, and cloud-preflight commit `84089a48a53fc17e3c800605726d5cab5c519e00` in [run 41548693104](https://github.com/Shawdaimarie/atlas-water-screening/actions/runs/41548693104).
- The browser control could not reattach to the existing in-app tab during this refresh, so no new screenshot-based UI assertion was made. The prior v9 production E2E run and each check above remain author-run evidence; a new full UI replay and an independent reproduction are still pending.


## Local OPERA analysis preparation (2026-11-02)

- Added `scripts/analyze_opera_geotiffs.py` for operator-supplied local DSWx-S1 V1 WTR GeoTIFFs. It records granule ID, product and processing versions, timezone-qualified retrieval time, source SHA-256, and analysis-code SHA-256; tests cover WTR classes, unknown codes, 80% AOI/asset valid-pixel gates, minimum observations, and event/baseline matching. The tests use synthetic GeoTIFFs only.
- Added `scripts/audit_study_area_balance.py` to require the full canonical 8 U.S./8 international register and find a single qualifying date count across all areas and assets. A single under-covered area prevents comparative output for the cohort. Its tests exercise both the balanced case and a single-area failure.
- Current local suite: `.venv/bin/python -m pytest -q` — **23 passed in 0.82s** with no warnings after pinning the affine dependency. An earlier fresh source-copy with a new virtual environment passed 23 tests in 14.72s, before the runtime dependency updates below. It is not evidence for the current dependency set; no independent reproduction or clean Git checkout has been tested.
- This does not change the production deployment: the analyzer is local only, no real raster has been downloaded, no actual area passed the pixel gate, and the existing Site still displays synthetic walkthrough values. Independent flood labels remain unavailable.


## Dependency and image refresh (2026-11-02)

- Updated runtime requirements to FastAPI 0.128.8 and Pydantic 2.12.5 and removed the unused Uvicorn `standard` extra.
- After the changes, `.venv/bin/python -m pytest -q` passed **23 tests in 1.06s**, `pip check` reported no broken requirements, and `git diff --check` passed.
- Rebuilt the ARM64 API candidate image; image-list digest is `sha256:4296d8ea2c7e3ef08acef4e3492dd2e8ce492ad1152fd65c09201ccf4207580f`. This candidate has not been smoke-tested after the dependency refresh.
- `pip-audit==2.9.0` reports known Starlette/AnyIO advisories in requirements and additional pip advisories in the image base. The audit is a release failure, not a pass. See `atlas-security-scan-findings.md`.
- Added a shared PR/push workflow with tests, image build, and a blocking dependency audit. It has no cloud credentials and does not deploy.


## Hash-locked API candidate verification (2026-11-02)

- Installed requirements-dev.lock with --require-hashes in a disposable Debian Python 3.12 x86_64 container (libexpat1 supplied for the Rasterio wheel).
- Full suite: **26 passed in 6.82s** with no warnings.
- pip-audit on the installed environment: **No known vulnerabilities found**. A separate audit of the built ARM64 image also found no known vulnerabilities.
- detect-secrets baseline scan reported **0 potential findings**; its hook passed over all tracked and new nonignored project files.
- Built ARM64 API image: digest **sha256:01bbdadffc2edd20903237ad975ce783887b985af7f2a4eed7e5346c5e03c67c**.
- Ran scripts/smoke_container.py against that image with a read-only root filesystem: **10/10 passed** (health, areas, aggregate analysis, CSV, invalid-field rejection, request-size rejection, malformed JSON rejection, host allowlist, allowed CORS preflight, denied CORS preflight).
- These checks exercise a local candidate container, not a provider-hosted environment. The GitHub workflow is prepared but has not run remotely; no cloud deployment has occurred.


## Multi-cloud preparation validation (2026-11-02)

- Parsed `deployment/cloud/provider-matrix.yaml` and checked the exact four-provider set (Google Cloud, AWS, Microsoft Azure, Oracle Cloud), common security/release gates, and the prohibition on static cloud credentials.
- Confirmed the published runbook and provider-matrix copies in `outputs/` match their maintained deployment source files.
- `git diff --check` passed; the detect-secrets hook passed across tracked and new nonignored files with the existing zero-finding baseline.
- This validates preparation artifacts only. There are no cloud resources, provider credentials, account-specific deployment workflows, or hosted cloud E2E results to report.


## Study-area API and current-checkout rerun (2026-11-02)

- Added `GET /api/study-areas` to expose the canonical 16 candidate locations, including region, evidence link, selection rationale, integration question, common archive window, and metadata screen counts. Each record explicitly says analysis is not ready; response labels the dataset metadata-only and says QA-valid pixels and independent flood labels are unproven.
- The Docker image now includes the canonical study-area JSON. The API validates on startup that the register contains exactly 8 U.S. and 8 international areas.
- Fresh target test run from the current checkout: **27 passed in 0.72s**, installed from `requirements-dev.lock` with `--require-hashes` in Python 3.12.
- Fresh container build: ARM64 tag `atlas-api:goal-2026-11-02`, digest `sha256:5b23d5c85b0f208fed73a17c62630110273042e33e5323d4bdcba43ebe4ba3f4`.
- The first smoke attempt found the runner could hit the container before startup. The API was healthy on immediate follow-up; the smoke runner was fixed to wait for health up to a bounded timeout. Rerun against the read-only image passed **11/11** checks, including 8+8 candidate counts.
- This improves local API coverage, not scientific validation or cloud deployment. No real OPERA raster was downloaded, and no candidate passed scene QA.


## Deployment control-plane readiness check (2026-11-02)

- Read-only GitHub owner-repository inventory and focused repository searches found no ATLAS project repository. The local checkout has no configured Git remote; `gh`, GCP, AWS, Azure, OCI, Terraform, and Helm CLIs are unavailable in this environment. No cloud management connector is present for the four requested providers.
- Sites readback confirms the existing private static walkthrough is active at version 9. This Site does not include the API runtime.
- A private GitHub repository form is staged with the proposed name `atlas-water-screening`, but it has not been submitted and no files have been transmitted. User authorization is pending for the exact repository creation/source upload needed to run remote CI.
- No cloud accounts were accessed or provisioned. Account signup, billing acceptance, and any legal terms remain in the account owner's hands.


## Live Site v9 walkthrough refresh (2026-11-02)

- Opened the authenticated private production Site and selected each of the 16 candidates. Each selection rendered its matching city/region detail, metadata counts, rationale, value-integration question, and primary evidence link; U.S. 8/8 and international 8/8 were present.
- Switched from single-observation to quality-aware aggregate: Houston's lead synthetic asset changed from 28.6% to 21.4% and the displayed median from 7.7% to 6.8%. The interface continued to identify the values as synthetic.
- Changed the scenario to Baton Rouge / Hurricane Ida. The event window and baseline updated to the scenario dates, asset IDs changed to the LA prefix, and the UI disclosed synthetic data.
- Downloaded the area register and parsed the result: 16 records, 8 U.S., 8 international. Saved the exact production download as `outputs/atlas-live-area-register-v9.csv`.
- Downloaded the evidence export and parsed the result: 12 assets, `aggregate` method, and `synthetic_fixture_no_live_NASA_data` on every row. Saved it as `outputs/atlas-baton-id-aggregate-fixture-export.csv`.
- Reset returned the analysis method to the single-observation baseline. The Site reports that the reset is to the baseline; selected scenario remains Baton Rouge / Hurricane Ida.
- This is author-run browser E2E evidence for the deployed synthetic walkthrough and candidate register. It does not demonstrate NASA ingestion, pixel QA, event truth, API connectivity, or cloud deployment; it does not change the score.


## Four-provider preparation update (2026-11-02)

- Expanded the machine-readable provider matrix and release runbook for GKE, EKS, AKS, and OKE. Common release requirements now include constrained OIDC allow/deny tests, separated staging/production and publish/deploy identities, private endpoints/ingress, signed digest/SBOM/provenance verification, registry image scans, restricted pod policy, managed secrets/KMS, audit logs, budgets, restore, rollback, and matched staging E2E results.
- Added provider-specific evidence outputs for Google Artifact Analysis, AWS ECR enhanced scanning, Azure Defender for Containers and Notary Project signatures, and OCI Vulnerability Scanning. OCI registry publishing remains a separate unproven identity gate.
- Owner reports new provider accounts are being created under `shawdaimarie@gmail.com`; account signup, billing, MFA, region choices, and IDs were not accessed or verified. No credential or payment information was requested/stored, and no paid cloud resources were created.
- Matrix validation: parsed YAML; exact provider set was `google_cloud`, `aws`, `microsoft_azure`, and `oracle_cloud`; required common gates and at least five provider evidence items per provider were present.
- `outputs/atlas-cloud-release-runbook.md` and `outputs/atlas-provider-parity-matrix.yaml` byte-match their maintained source files.
- Current checkout test rerun: **27 passed in 0.80s**. `git diff --check` passed. These are preparation/documentation checks plus local tests; no remote cloud deployment or provider-hosted workflow was run, so no 100/100 score is claimed.


## Real-input raster QA pilot (2026-11-02)

- Retrieved six public NASA JPL/Caltech ARIA/OPERA DSWx-S1 BWTR mosaics for the July 4, 2025 Central Texas flood response. Each file downloaded successfully and is packaged under `outputs/atlas-texas-raster-pilot/rasters/`; `summary.json` and `analysis/run_manifest.json` record source and SHA-256 checksums.
- Ran `scripts/analyze_opera_geotiffs.py` with a 25 km Kerrville-area AOI and one 600 m technical QA cell (explicitly not a real asset). All six GeoTIFFs were parsed, projected, and evaluated against the same ≥80% valid-pixel rule.
- Baseline QA: 2025-06-17 0.999922 (pass), 2025-06-19 0.000000 (no AOI coverage), 2025-06-22 1.000000 (pass). Event QA: 2025-07-01 0.000000 (no AOI coverage), 2025-07-04 1.000000 (pass), 2025-07-11 0.999929 (pass).
- Only 2/3 dates passed in each period. The predeclared minimum remains 3; the result was `unknown_insufficient_qa_valid_dates`, with no selected matched dates and no water-fraction comparison. This is a successful fail-closed QA demonstration, not a passing event analysis.
- NASA's response maps are preliminary/unvalidated; processing software version is absent from published page and TIFF tags; no independent labels or real infrastructure polygons were supplied. Kerrville is outside the selected 16 areas, so none of the enrolled locations is considered real-data validated by this pilot.
- Verified the package's six TIFF byte lengths and SHA-256 values against `summary.json`; reproduced the analysis from the packaged manifest and geometries. This pilot does not change the scorecard.
- Final current-checkout verification after updating the pilot and cloud documents: **27 passed in 0.68s**; provider matrix parsed with the exact four targets; runbook/matrix and scorecard review copies match their sources; six-raster input hashes and the insufficient-coverage result validated; `git diff --check` passed.
- Read-only Sites control-plane recheck on 2026-11-02: ATLAS remains active at version 9 on the private URL; configured access remains owner-only with no external visitor grants. This verifies publication/access state, not the separate local API or a cloud-hosted runtime.


## Multi-cloud onboarding refresh and live selector check (2026-11-02)

- Updated the four-provider release runbook and machine-readable matrix to track account setup as owner-reported and unverified, with no credentials retained and no infrastructure provisioned. Resource creation remains gated on owner-confirmed billing, MFA/recovery, regions, data residency, budget alerts, and environment boundaries.
- Tightened parity requirements so digest, signature, SBOM, and provenance must survive registry transfer and be enforced at admission for GKE, EKS, AKS, and OKE. Provider scan enablement and evidence must be demonstrated in the actual account.
- The version 9 live walkthrough showed the candidate profile and synthetic analysis as separate content but did not state that boundary explicitly. Version 10 adds a visible notice explaining that profile selection does not change the synthetic Houston/Baton Rouge map, asset portfolio, or values.
- Cloud identity, registry transfer, staging, rollback, and real raster workflows remain untested because no cloud environment is configured.


### Verification refresh (2026-11-02)

- `.venv/bin/python -m pytest -q`: **27 passed in 0.84s**.
- Read-only Docker smoke against the current local candidate: **11/11 passed** (health, area lists, 8+8 study-area register, synthetic aggregate, CSV export, invalid field, payload limit, malformed JSON, host allowlist, allowed CORS, denied CORS).
- Ruby YAML parser accepted `deployment/cloud/provider-matrix.yaml`; it contains the four requested providers and 18 shared required checks. `git diff --check` passed.
- These local checks do not test cloud IAM, registry scanning, signature preservation, Kubernetes admission, staging, recovery, or production.


## Private Site version 10 release and regression (2026-11-02)

- Published version 10 successfully from source commit `807abdea007ccd694f920b769ef9c644b7dc3947`; Sites readback confirmed active status, private/custom access, zero external visitors, and the exact source commit. Deployment ID: `appgdep_6ae910bcef608191bb2063553a735c4e`; archive hash: `sha256:53b7799645e9acbfa4c2ccc373b99ef7f11d27cb9a088da57e5f443426bd4d3c`.
- The added disclosure distinguishes the 16 candidate evidence profiles from the independent synthetic scenario demonstration; it preserves the fact that research-area selection does not load geospatial observations or switch the scenario’s asset fixtures.
- Live v10 checks passed: selected Jakarta and confirmed its profile/rationale/source; changed method and observed the expected synthetic aggregate ranking; selected Hurricane Ida and observed Baton Rouge dates, schematic label, and `LA-` asset IDs; downloaded the area register and evidence export (both success messages); reset and observed the single-scene baseline (4 elevated assets; median 7.7%).
- Browser page was left open to the private v10 walkthrough with Jakarta selected and Baton Rouge/Hurricane Ida active. The dashboard and profile are visibly synthetic; this validates only the walkthrough, not scientific analysis.
- Synchronized the published source’s `dist/index.html` back to the current workspace. Python tests are unchanged from the latest 27-pass run; this static-copy change does not affect the API or its test suite.
- At this version 10 release milestone, the score was **50/100 provisional**. No cloud-provider environment or scientific validation gate passed from that Site release.


## Current multi-cloud preparation rerun (2026-11-02)

- Parsed `deployment/cloud/provider-matrix.yaml` and verified the four targets (GKE, EKS, AKS, OKE), OIDC-only release contract, immutable digest promotion, production approval gate, and provider-specific identity/evidence requirements.
- Current checkout suite: `.venv/bin/python -m pytest -q` — **27 passed in 0.80s**.
- Ran the current `atlas-api:goal-2026-11-02` container locally with a read-only root filesystem, dropped capabilities, no-new-privileges, and bounded CPU/memory. `scripts/smoke_container.py` passed **11/11** HTTP checks.
- Local checks passed; no cloud account sign-in, remote GitHub CI, cloud resources, or provider-hosted test was available. Owner reports account creation is in progress under `shawdaimarie@gmail.com`; account IDs, MFA, billing, regions, and budgets remain unverified.


## Latest live deployment and CI verification (2026-11-02)

This status supersedes the earlier version 10/11 entries below; those are retained as release history.

- The private Sites deployment is active at **version 12**, from source commit `af1c7a315447588f6893279605f5c7b7ddbaa240`. Deployment `appgdep_6ae9164a45bc81919f19e1af0750b143` succeeded. Access readback remains custom owner-only (`shawdaimarie@gmail.com`) with zero external visitors.
- Live browser review of the current page confirmed the Houston/Beryl synthetic scenario, exposure summary, evidence export control, and 16-area candidate register. Candidate records disclose that pixel QA and independent labels remain pending. The Site remains separate from the API.
- The current local suite passes: `.venv/bin/python -m pytest -q` — **31 passed**, including three checks for provider-parity policy, the nonsecret owner-input template, and restricted Kubernetes manifests. Secret scan and `git diff --check` passed.
- Private GitHub CI passed on commit `ad459345be5450117a1611c360b158a11a0f6a59`: [run 41544022836](https://github.com/Shawdaimarie/atlas-water-screening/actions/runs/41544022836). The run passed the 31-test suite, container build, container HTTP smoke, and dependency audit, including the new provider-policy and Kubernetes manifest checks. An earlier run exposed missing `study_area_evidence.json` in the Docker build context; `.dockerignore` and Dockerfile were corrected before the successful run.
- The live Site only demonstrates the synthetic walkthrough and candidate evidence profiles. The API is not connected to the Site or deployed to a cloud provider. No Google Cloud, AWS, Azure, or OCI staging or production environment has passed deployment checks.
- Current documented score is **55/100 provisional** under the canonical rubric. CI and Site deployment do not establish real-scene pixel validity, independent ground truth, operational demand, or cross-provider deployment.

## OPERA pixel-audit preparation refresh (2026-11-02)

- Official catalog review confirmed Earth Engine exposes `OPERA/DSWX/L3_V1/S1` with the documented 30 m `BWTR_Binary_water` classes (0 valid non-water, 1 water, 250 HAND-masked, 251 layover/shadow-masked); the public catalog snapshot was current through 2026-10-28 UTC. ATLAS's existing CMR metadata screen runs through 2026-11-02, so the planned pixel diagnostic deliberately uses the shorter common catalog window.
- Added `scripts/earthengine/atlas_opera_pixel_coverage.js` and `outputs/atlas-earth-engine-pixel-audit-guide.md`. The script covers the 16 registered boxes, mosaics same-day tiles, reports per-date valid-pixel area, water area, known invalid area, class histogram and source metadata, and flags dates below 80% AOI validity. It only prints results; no Earth Engine task, export, project registration, or billing action was performed.
- Owner execution requires a selected Google Cloud project with Earth Engine API access and approved commercial/noncommercial registration. No suitable project or eligibility was verified; therefore there are still no pixel-coverage results, and the diagnostic earns no score points yet.
- Added offline checks that compare the script's 16 locations/bounds against the canonical JSON register and assert the documented validity/coverage gates. Current local suite: `.venv/bin/python -m pytest -q` — **38 passed in 0.99s**, with one environment warning that urllib3 is running against LibreSSL. `git diff --check` passed.
- This prepares actual pixel QA but does not satisfy any event-level, data-quality, or independent-label validation requirement until an owner-run Earth Engine result is reviewed. Score remains **55/100 provisional**.


## Clean-checkout reproduction (2026-11-02)

- Created a fresh detached Git worktree at commit `73eac66103db64c61f54172ad76fba8157a6b10c`.
- In a new Python 3.12 ARM64 container (`python:3.12-bookworm@sha256:a5bab0ff300f91231c2e68bf73a8a8d60762ac39ce1c50eaf6803e4c38a9062b`), installed all locked development dependencies with `python -m pip install --require-hashes -r requirements-dev.lock`.
- Ran `python -m pytest -q`: **31 passed in 0.70s**. This was author-run from a clean checkout; an independent reviewer reproduction remains pending.
- The failed first attempt in the separate `python:3.12-slim-bookworm` image lacked `libexpat.so.1`, required by the optional Rasterio package. The successful reproducibility result used the standard Bookworm Python image; this does not change the runtime API image or establish any real-area scientific result.
- The canonical score rises from 50 to **55/100** only because the documented clean-checkout reproduction item is now evidenced. Cloud, usability, capacity, held-out-event, and independent-label criteria remain pending.
