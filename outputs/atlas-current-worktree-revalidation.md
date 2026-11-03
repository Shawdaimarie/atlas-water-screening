# ATLAS current-worktree revalidation

**Run date:** 2026-11-03  
**Purpose:** revalidate the current source and release evidence against the active ATLAS goal. This is a local verification record, not a claim of independent reproduction or a new production deployment.

## Source and test state

- Git base commit: `f8064f83788984260b61f24902802035cc7b14e1` (`Record verified ATLAS v21 walkthrough`). The worktree was dirty with 60 modified, deleted, or untracked paths during the run; the test result applies to that exact then-current worktree.
- Reproduction command: `docker run --rm -v "$PWD:/work" -w /work python:3.12-bookworm@sha256:a5bab0ff300f91231c2e68bf73a8a8d60762ac39ce1c50eaf6803e4c38a9062b sh -lc 'python -m pip install --disable-pip-version-check --require-hashes -r requirements-dev.lock -r requirements-reference-audit.lock && python -m pytest -q'`.
- Result: **96 passed in 18.09s** using both hash-locked dependency files and the digest-pinned Python 3.12 Bookworm environment.
- Environment note: `.venv/bin/python -m pytest -q` uses Python 3.9 and could not collect four spatial-audit modules because Shapely is missing from that local environment. The pinned Python 3.12 run collected and passed the full suite; no application test failure was reported in the Python 3.9 run.
- Current local `dist/index.html` inline script: extracted and parsed successfully with Node.js **22.23.4** (`node --check`). `git diff --check` passed. This syntax check does not establish that this local file is identical to the deployed v37 archive.

## Production state checked

- Sites control-plane readback reports the ATLAS Site as **active**, current live URL `https://atlas-water-screening.shawdaimarie.chatgpt.site`, latest version **37**, custom owner-only access, and zero external visitors.
- The latest saved version points to source commit `2a74d35d2451e311e4f6eec723fe453092bedbb9`; its deployment ID is `appgdep_6aea23764d64819198aa4c9d99def75b`.
- The v37 production criteria card and 16-row JSON matrix endpoint were verified in the authenticated browser in the release run. A follow-up live replay selected Mumbai, changed the separate synthetic scenario to Baton Rouge/Hurricane Ida, switched to quality-aware aggregate, and selected Southeast Water Plant for its detail panel.
- **Evidence export** produced a browser-saved CSV; parsing confirmed 12 rows, all labeled `synthetic_fixture_no_live_NASA_data`, for Baton Rouge/Hurricane Ida and the aggregate method. The **8+8 evidence matrix CSV** also produced a saved file; parsing confirmed 16 rows, 8 U.S. and 8 international, with 0 confirmatory-eligible areas.
- The browser was left on the live Site with Mumbai selected and its candidate profile visible. This replay verifies the deployed walkthrough and file exports only; the values remain synthetic. No cross-provider E2E is claimed.

## Cloud release readiness

- The ignored owner handoff file `deployment/cloud/owner-inputs.local.yaml` is absent. The digest-pinned Python 3.12 `--release-ready` preflight exits with `FAIL: input file not found` and requests the owner to copy the example and fill non-secret account identifiers and approved choices.
- No provider credentials or account identifiers are available in the project, and no GCP, AWS, Azure, or OCI resources were created or tested. This is consistent with account onboarding still being in progress; account creation alone does not pass the deployment gate.

## Research and rubric limits

The candidate register contains 8 U.S. and 8 international locations with explicit area-level rationale and common screening rules. It does not establish balanced event/baseline observations or independent labels: the current matrix reports **0/16 confirmatory-eligible areas**, and the deployed analysis remains synthetic. The auxiliary RTC screen is an availability diagnostic, not water classification or event validation. No four-cloud provider has a verified deployment, and no Apple app target/build has been verified. The canonical score is now **60/100 provisional** after the separately documented local artifact recovery drill; this revalidation adds no points.

## Follow-up verification (2026-11-03)

- A later full run on the current worktree passed **121 tests** in the digest-pinned Python 3.12 Bookworm environment with both hash-locked dependency files. `git diff --check` passed; only pre-existing CRLF normalization warnings were emitted for the archived Texas pilot CSVs.
- A fresh authenticated production replay on private Site v37 verified the Houston/Hurricane Beryl start state, switch to Baton Rouge/Hurricane Ida, quality-aware method toggle with ranking update, selection of Mumbai and its candidate-evidence profile, export success confirmation, and reset to the single-observation baseline. Site readback confirms owner-only access and zero external visitors. This verifies interface workflows; analysis values are still synthetic.
- The WorldFloods v2 metadata archive was SHA-256 checked and all 509 record bounding boxes screened against the same 16 fixed AOIs: 0 candidate footprints. The archive period is 2016–2023 and predates the current OPERA DSWx-S1 validation window. This does not imply reference data are absent outside the checked boxes. Machine-readable evidence: `outputs/atlas-worldfloods-v2-aoi-coverage-audit.json`.
- The sampling-frame and label-QC workflows, plus the new source screen, are available in private GitHub PR [#1](https://github.com/Shawdaimarie/atlas-water-screening/pull/1). The latest head CI [run 41698848108](https://github.com/Shawdaimarie/atlas-water-screening/actions/runs/41698848108) passed both test/container and dependency-security jobs. The PR is open and unmerged.
- The recovery drill adds local Reliability evidence. Canonical score is now **60/100 provisional**. Research enrollment is still 0/16; four-cloud deployments, capacity evidence, task-based usability, and independent reproduction remain incomplete.

See [the canonical scorecard](atlas-scorecard.md), [the deployed v37 checklist](atlas-v37-end-to-end-checklist.md), and [deployment and test results](atlas-deployment-test-results.md).

## Sampling workflow follow-up (2026-11-03)

After adding the reference label review-quality gate, the current worktree was rerun in the same digest-pinned Python 3.12 Bookworm environment using both lock files. The full suite passed **108 tests in 1.35s**. The four sampling tests cover deterministic draws, weights, invalid-pixel exclusion, fixed-AOI/grid checks, and 16-area/two-period fixture output. Eight label tests cover blinded double labels, adjudication, incomplete and sensitivity-only records, ID integrity, source metadata and timestamps, and sensitivity-only adjudicator rejection. `git diff --check` passed after the workflow and documentation updates. All new evidence tests use synthetic fixtures; no production frame or independent label QC run exists.

The offline workflow is proposed in private GitHub [PR #1](https://github.com/Shawdaimarie/atlas-water-screening/pull/1), head commit `eaf75da8eef0e019f3810d89f027fc3a1f45cab0`. The latest Actions run [41696378952](https://github.com/Shawdaimarie/atlas-water-screening/actions/runs/41696378952) passed the current repository suite (**94 passed in 2.31s**), reference screen, container build, 11/11 HTTP smoke checks, runtime image audit, and dependency audit. Sites readback during this follow-up confirms production Site **v37** remains active and owner-only. The PR is cleanly mergeable but remains unmerged, and this offline workflow has not been added to the Site UI.

## Latest verification and release-source comparison (2026-11-03 UTC)

- Re-ran the complete current-worktree suite in the digest-pinned Python 3.12 Bookworm container after installing both hash-locked dependency sets: **124 passed in 17.24s**.
- Opened the existing Site source branch read-only at commit `2a74d35d2451e311e4f6eec723fe453092bedbb9`. SHA-256 comparison found all ten files in the local `dist/` directory identical to the source checkout's `dist/` files. Sites control-plane readback reports that commit as active private Site v37. This confirms that the current study-area evidence page and its JSON/CSV assets already match the deployed release; no new Site version was needed for these local source updates.
- Score records are reconciled to **60/100 provisional**: the local hash-verified artifact backup/restore drill supplies one additional Reliability criterion. Confirmatory eligibility remains **0/16**; the 8+8 list is a candidate frame, and values shown in the analysis walkthrough remain synthetic.
- The PetaBencana Jakarta archive audit exercised four dated query windows. The March 2025 and January 2026 requests returned the same five area IDs, all last updated 2022-10-07; the January 2020 positive control returned 520 records with 519 last-updated dates inside its requested window. Three new fixture tests validate this fail-closed date-window classification. The API result is a source-quality finding, not event truth or study eligibility; the complete report is `outputs/atlas-petabencana-archive-screen.json` and its limitations are documented in `outputs/atlas-independent-reference-data-plan.md`.
- `git diff --check` passed after the score/status reconciliation. No deployed page delta resulted from this audit, and the production source/page comparison above remains unchanged.

## Live replay and full-suite rerun (2026-11-03)

- Rechecked the existing authenticated owner-only Site v37. The page remains on the deployed version; the ten `dist/` files match the active Site source branch at commit `2a74d35d2451e311e4f6eec723fe453092bedbb9`, so no new release was required.
- Live interactions changed the synthetic analysis to Baton Rouge/Hurricane Ida and quality-aware aggregation, selected the New Orleans evidence profile, and produced the evidence-export success message. The visible evidence panel reported 4,500 SpaceNet 8 objects, 14 `flooded=yes`, 4,486 unknown, and 0/16 confirmatory-eligible areas. These are source-screen counts and synthetic demo workflows, not a validated comparison.
- The current hash-locked Python 3.12 Bookworm run passed **124 tests in 9.38s** using both dependency lock files; `git diff --check` passed. The canonical score remains **60/100 provisional** and confirmatory eligibility remains **0/16**.

## v38 live audit panel release (2026-11-03)

- Published the raster-level Copernicus GFM availability panel and 16-area audit JSON as private Site v38. Source commit `5c42fc8bdcb8238e476ee371932301658b4bce0e`; deployment `appgdep_6aea3dd1e3048191b939f7def5a7468e` succeeded. Control-plane readback reports version 38 active and preserves the owner-only policy.
- The live panel expanded to 16 rows; the summary reported 39/48 matched date slots, 8/39 selected COGs at or above 80% valid pixels, and 2/16 candidate-event samples passing. The browser link to the packaged raw audit opened successfully and returned 16 area records.
- Full Python 3.12 Bookworm suite using both hash-locked requirements files passed **124 tests in 17.17s**. v38 evidence and limits are recorded in `outputs/atlas-v38-end-to-end-checklist.md`.
- Research enrollment remains 0/16; GFM shares Sentinel-1 lineage with OPERA and does not qualify as independent truth. Score remains 60/100 provisional. Four-cloud deployment, capacity, user study/accessibility acceptance, and independent reproduction remain incomplete.

## Current revalidation (2026-11-03)

- Current worktree base commit is `f8064f83788984260b61f24902802035cc7b14e1`; the worktree had 83 modified, deleted, or untracked paths when rechecked. The result below applies to that local state, not to a clean checkout.
- In digest-pinned Python 3.12 Bookworm with `requirements-dev.lock` and `requirements-reference-audit.lock` installed using `--require-hashes`, the full suite passed **124 tests in 20.07s**. A prior attempt using the Mac's Python 3.9 `.venv` failed collection in four spatial-audit modules because Shapely is missing there; that environment failure is superseded by the complete pinned run, not counted as a product test failure.
- `git diff --check` passed. Sites control-plane readback confirms the deployed private Site remains active at v38 with owner-only access, deployment `appgdep_6aea3dd1e3048191b939f7def5a7468e`, source commit `5c42fc8bdcb8238e476ee371932301658b4bce0e`.
- The evidence ledger still has 16 candidate areas (8 U.S., 8 international), 10/16 passing all 12 sampled Sentinel-1 RTC availability screens, and **0/16** eligible for confirmatory validation. The region screen shows 78/96 sampled groups passing for U.S. versus 91/96 for international locations, so the current availability is not comparable across strata at the 80% screen. Availability, event-discovery metadata, or unverified labels do not meet the independent reference, probability sample, adjudication, and precision gates. The score remains **60/100 provisional**; no score credit is inferred from this revalidation. See [regional comparability screen](atlas-s1rtc-region-comparability-screen.md).

## v40 release revalidation (2026-11-03)

- Production Sites readback reports version **40** active, owner-only, with zero external visitors. Deployment `appgdep_6aea4f6bea5481919fb77c51376a4ec0` succeeded from Site source commit `5b0c035d27325ad2d60df6961964773c4c877ccd`.
- Authenticated live reload verified the revised 192/192 matched RTC quota, all 16 area rows, the supplemental audit link, and the OPERA-specific pending-QA disclosure. The raw quota endpoint reported 16 areas (8+8) and 192/192 selected groups.
- Live interaction replay changed the synthetic scenario to Baton Rouge/Hurricane Ida, switched to quality-aware aggregate, and selected Southeast Water Plant; visible values matched the fixture (18.9% illustrative overlap, 93% coverage, 73% uncalibrated confidence). The export success notice appeared. Download capture timed out, so this v40 replay did not independently verify the downloaded CSV bytes.
- The current worktree full suite passed **127 tests in 2.08s** in `python:3.12-bookworm@sha256:a5bab0ff300f91231c2e68bf73a8a8d60762ac39ce1c50eaf6803e4c38a9062b`, with `requirements-dev.lock` and `requirements-reference-audit.lock` installed using `--require-hashes`.
- Extracted the deployed HTML inline script and `node --check` passed in Node 22. `git diff --check` passed. The packaged Site HTML and local `dist/index.html` share SHA-256 `2cfdfb6fcc7930be249485c708add9e605feb2a0113db13d79041d9290684cfd`.
- The supplemental coverage-conditioned RTC screen now fills a 12-group, three-per-quarter quota in all 16 candidate areas after screening 34 additional groups (23 accepted, 11 below the floor). This does not change the original draw's 169/192 pass result or make matched selection unconditional. It remains spatial data availability, not OPERA validation or independent flood truth. The ledger remains **0/16 confirmatory-eligible** and the score remains **60/100 provisional**.
- Apple distribution is still separate from this browser Site. No native app target exists, full Xcode is unavailable on this Mac, and Apple Developer membership/App Store Connect access remain unverified. No cloud provider deployment is established by v40.

See [v40 end-to-end checklist](atlas-v40-end-to-end-checklist.md) and [live walkthrough](atlas-live-walkthrough.md).


## Cloud/Apple track decoupling and latest validation (2026-11-03)

- Cloud onboarding no longer requires an Apple distribution role. The owner-input example records the selected App Store/TestFlight intent separately, while Apple membership and App Store Connect access remain unverified.
- The digest-pinned Python 3.12 Bookworm suite with both hash-locked dependency files passed **128 tests in 1.73s**. The cloud input validator ran against the example and failed closed with **29** missing or invalid owner/provider requirements, printed field names only, and created no resources. This is expected until account, budget, region, identity, and release choices are supplied.
- The provisional score remains **60/100**; the v40 Site remains active and owner-only. Neither Apple account ownership nor local CI changes verify a native app distribution or any of the four cloud deployments.

## Live Site replay and prospective-protocol clarification (2026-11-03)

- Sites control-plane readback confirms the existing owner-only Site is active at version 40, with zero external visitors and source commit `5b0c035d27325ad2d60df6961964773c4c877ccd`. The version archive and local/source `dist/index.html` hashes match.
- An authenticated browser replay confirmed all 16 area profiles (8 U.S., 8 international), common nominal 625 km² footprint and metadata window, selection criteria, the 192/192 coverage-conditioned RTC table, the separate 169/192 initial random draw, reference-source limitations, zero confirmatory eligibility, the common sample/precision rules, and the synthetic-analysis warning. Clicking “Download area register” displayed the success message. The browser did not expose the downloaded bytes for independent parsing.
- Protocol v2 now explicitly records that prior candidate selection, source screening, RTC draws, Tampa OPERA sampling, and other archive exploration are discovery-only and excluded from future confirmatory inference. It requires an externally timestamped freeze of events, inclusion list, AOIs, sampling plan, metrics, and analysis code before examining selected-event OPERA outcomes or labels. The protocol remains proposed and not externally preregistered.
- The post-change digest-pinned Python 3.12 Bookworm run passed **128 tests in 2.29s** with both lock files installed using `--require-hashes`; `git diff --check` passed. The canonical score remains **60/100 provisional**, and confirmatory enrollment remains **0/16**.
- The deployed Site remains version 40. The protocol v2 local source changes have not been published to the Site-linked repository branch; the live UI already labels the protocol as proposed and not externally preregistered.

## Protocol review-branch synchronization (2026-11-03)

- Published the validated protocol v2 Markdown, YAML contract, and matching freeze assertions to the existing private GitHub PR branch `codex/reference-sampling-frame`. GitHub readback confirms PR #1 remains open and unmerged at head `5975b5a12c9d16e0ddc6296897f526d1cff8e4fa`; the branch contains the explicit exploratory-exclusion rule.
- The GitHub combined-status and PR-workflow queries returned no checks for this new head at the time of verification. The **128-test** result is from the local digest-pinned full suite and must not be represented as CI for the new PR head.
- GitHub default branch and the active Site remain unchanged; the updated protocol is available for review in PR #1 and has not been merged or deployed through the Site.

## Protocol PR CI verification (2026-11-03)

- GitHub PR #1 head `5975b5a12c9d16e0ddc6296897f526d1cff8e4fa` completed Actions run [41723543703](https://github.com/Shawdaimarie/atlas-water-screening/actions/runs/41723543703) successfully. The `tests-and-image` job passed **97 tests in 1.73s**, the 16-area GEOID-Flood footprint screen, container build, **11/11** HTTP smoke checks, and image audit; the `dependency-security` job also succeeded.
- This CI run verifies the PR branch as it exists at that head, including protocol v2 and its assertions. It ran 97 tests; the broader **128-test** result applies only to the current local worktree and should not be conflated with this PR run.
- The PR remains open and unmerged; the default branch and deployed Site v40 remain unchanged. Scientific eligibility is still **0/16** and the score remains **60/100 provisional**.
