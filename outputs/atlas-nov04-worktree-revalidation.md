# ATLAS worktree and production revalidation records — 2026-11-04

## Latest revalidation — v61 source and research audit

- Sites control-plane readback confirms private owner-only v61 remains active at the production URL, with deployment `appgdep_6aeb0960487881919cdf41f78877eee8` succeeded from Site source `1bf4d1659270e6516235433259bf3b657361eb6b`. The owner is the only allowed user and external visitor count is zero. The authenticated v61 walkthrough and interaction results are recorded in [`atlas-v61-live-revalidation-2026-11-04.md`](atlas-v61-live-revalidation-2026-11-04.md); this update did not claim a new browser replay.
- A fresh Site-linked source checkout at v61 commit `1bf4d1659270e6516235433259bf3b657361eb6b` matches every one of the **27** current root `dist/` files by SHA-256. No new Site deployment was needed. The existing `.sites-open` checkout was behind the live source and locally edited; the Sites source helper refused to overwrite it. A separate empty checkout was used to read the live source safely. The in-app browser session was listed, but this Mac is locked and CUA reported the browser user unavailable, so no new interaction replay is claimed; the prior authenticated v61 replay remains the latest.
- Re-ran the complete repository suite in digest-pinned Python 3.12 Bookworm with both lock files installed using `--require-hashes`: **172 passed in 1.39 seconds**. Built the current API image from the hash-pinned runtime base; its read-only container passed **11/11** health, 8+8 register, analysis, CSV export, input-limit, host, and CORS checks. `pip-audit` found **no known runtime vulnerabilities**. The 16-area GEOID-Flood screen completed with one historical St. Louis event, 12 tiles, and 12 benchmark-eligible tiles. `git diff --check` passed after the documentation reconciliation.
- Added the exact official Jakarta BPBD 22–26 January 2026 event window to the PetaBencana archive audit. The direct API response returned five area IDs, all last updated 2022-10-07, with the same response hash as separate 2025 and January 2026 requests. This is stale source data, not a flood reference label. A focused regression test covers the event-specific stale-row case; see [`atlas-petabencana-january-2026-event-window.md`](atlas-petabencana-january-2026-event-window.md) and the machine-readable audit.
- The 8+8 candidate frame remains **0/16 confirmatory-eligible**; the PetaBencana result adds no score. The evidence-only canonical score remains **60/100 provisional**.
- Cloud account handoff inputs are still absent. The release-ready validator fails closed with `input file not found: deployment/cloud/owner-inputs.local.yaml`; it creates no provider resources. No GCP, AWS, Azure, or OCI deployment is verified. The existing Apple account remains a separate future Apple-app distribution path; no native app build is verified.
- This local checkout is based on `f8064f83788984260b61f24902802035cc7b14e1` and is dirty; Git cannot fetch over HTTPS in this environment. External release identity is established from Sites control-plane readback and the private GitHub connector, not inferred from the local branch.

The sections below preserve the older v45 revalidation as historical evidence; they do not describe the current deployment.

## Historical v45 source checks (superseded)

- Ran the complete Python 3.12 suite in the digest-pinned `python:3.12-bookworm` image with `requirements-dev.lock` and `requirements-reference-audit.lock` installed using `--require-hashes`: **139 passed in 1.55 seconds**.
- `git diff --check` passed.
- Audited the current static page's local references: **11 static relative references, 0 missing files**. The other 11 static links are external sources. Two dynamic evidence links are populated from the selected area's source records and are not static paths.
- Parsed the generated study-area evidence register: **16 entries, 8 U.S. and 8 international**. The current page contains the common public-value framework, event-discovery evidence links, and readiness-ledger downloads.
- Served the exact root `dist/` package locally; the browser received HTTP 200, rendered all **16** study-area controls, and reported **no JavaScript console errors**. The temporary preview server was stopped after inspection.

## Production boundary

- Sites control-plane readback confirms the private owner-only Site is active at `https://atlas-water-screening.shawdaimarie.chatgpt.site/`, with **v45** current, owner `shawdaimarie@gmail.com`, and zero external visitors.
- Reconciled the existing Site source checkout to the exact v45 remote head `a3718a6043d131fc989e1d172d41a90e839f6cf7`. All **14/14** current root `dist/` files have identical SHA-256 content in that checkout. It retains two additional older Tampa pilot CSV/JSON artifacts that the current page does not link. No newer Site release was needed for the current page package.
- Authenticated v45 browser replay now passed all 16 study profiles, Singapore's official-source caveats, the Baton Rouge/Hurricane Ida scenario, quality-aware method, asset detail, reset, synthetic evidence CSV parsing, 8+8 register CSV parsing, and live matrix/readiness JSON checks. Full results are in `outputs/atlas-v45-end-to-end-checklist.md`. This verifies interface behavior only; the analysis values remain synthetic.

## Research and score

- The candidate frame remains a screening program, not a completed comparative validation study. The evidence-readiness matrix reports **0/16 confirmatory-eligible areas**. Synthetic fixture outputs remain separated from historical observations.
- Canonical score remains **60/100 provisional**. This software revalidation earns no new rubric points. Current gaps include confirmatory real-event observations and independent labels, production API authentication/isolation, capacity/cost evidence, task-based usability/accessibility acceptance, four-provider cloud deployment, and independent reproduction.
- Apple Account direction is recorded separately in `outputs/atlas-apple-distribution-readiness.md`; no native Apple app build or distribution is verified.

## Release handoff

The current deployed page is source-synchronized and fully click-tested at v45. The remaining goal work concerns empirical cross-site validation, production API and cloud deployment, capacity/cost, usability/accessibility acceptance, and independent reproduction. The local environment has no `node` executable for the Sites source workflow helper; Docker is available and was used for the passing test run. No release credential or provider secret was written to disk.
