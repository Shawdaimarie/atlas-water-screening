# ATLAS worktree and production revalidation — 2026-11-04

## Current source checks

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
