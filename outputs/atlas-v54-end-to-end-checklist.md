# ATLAS v54 production update and release check

**Date:** 2026-11-04  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Site version:** 54  
**Source commit:** `3ef7ab802765ff4bce24789928a51d77fba8f084`  
**Deployment:** `appgdep_6aeae302a7348191813b1980390d32de` — succeeded  
**Audience:** owner-only; `shawdaimarie@gmail.com`; zero external visitors.

## Release changes

- Added the bounded Miami/Tampa Hurricane Milton OPERA EGIS point-sample audit and its machine-readable JSON and sampling record to the evidence panel.
- Clearly labels the sample as preliminary/unvalidated, point returns rather than full-AOI coverage, and insufficient for water-change estimation or confirmatory validation.
- The user confirmed the existing Apple Account is intended for a future Apple app distribution path. The current product is still a private web Site; no Apple credentials were requested or stored.

## Verification

| Check | Result | Evidence |
|---|---|---|
| Full project test suite | **148 passed** | `.venv/bin/python -m pytest -q`; 1 existing LibreSSL/urllib3 environment warning. |
| Sites deployment | **Passed** | Sites returned production status `succeeded`, version 54, and the private production URL. |
| Live update present | **Passed** | Reloaded authenticated production page; the Miami and Tampa Milton card rendered with per-date point counts, the unvalidated-data qualification, and both record links. |
| Study-area selector walkthrough | **Passed** | Selected Singapore; the evidence profile, PUB source rationale, value-integration question, and validation path rendered. The screenshot was captured with Singapore selected. |
| Owner-only policy | **Passed** | Sites access readback showed custom access restricted to the owner; zero external visitors. |

## Research and product limits

This is a web release, not an Apple app release. The Apple Account is the chosen account for a future app signing/distribution workflow, but the repository still has no iOS app target and the full Xcode/Developer Program/App Store Connect gates remain unverified. The 16-area project remains exploratory with **0/16 confirmatory-eligible areas**. The Milton audit has incomplete/service-error and outside-footprint dates, uses point sampling, and has no independent label comparison. It does not validate flood classification or change the canonical score.

The canonical score remains **60/100 provisional**. See `SCORECARD.md`, `outputs/atlas-v53-accessibility-audit.md`, `outputs/atlas-milton-egis-multisite-pixel-sample.md`, and `outputs/atlas-apple-distribution-readiness.md`.
