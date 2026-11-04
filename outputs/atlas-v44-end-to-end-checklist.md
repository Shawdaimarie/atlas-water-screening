# ATLAS v44 release and walkthrough checklist

**Run date:** 2026-11-04 UTC  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Site version:** v44  
**Deployment:** `appgdep_6aea91ded74c8191a68b51b722cc4512`  
**Source commit:** `de08838d4e03332177008b9cf3b49a981a7c1caa`  
**Archive SHA-256:** `d4eb0d480a709130fd87d3c6c3ce3b923e60a4ed881113e0ea51c5061f7e8c66`  
**Archive files:** 17

## Deployment and access verification

- Sites publication returned `succeeded`; a fresh Sites readback reports v44 active and binds it to the exact source commit, archive hash, and deployment ID above.
- Access remains custom owner-only: `shawdaimarie@gmail.com` is the only listed user; there are no groups or external visitors.
- An unauthenticated production request returned HTTP **401**, consistent with the owner-only policy.
- The source checkout is byte-for-byte aligned with the deployed version before the v44 framework change. The v44 commit contains the updated generated `dist/index.html` and preserves the packaged evidence files.

## What v44 adds

The 16-area selection screen now displays a shared public-value framework applied equally across all 8 U.S. and 8 international candidate areas:

1. Hazard observation: product class, time, valid-pixel fraction, and uncertainty.
2. Asset exposure: dated, sourced footprints and geometry completeness.
3. Service consequence: attributable service criticality, population served, and dependencies, with agency/community review.
4. Distributional equity: representation and missing coverage, using privacy-preserving and locally governed information.
5. Decision usefulness: documented priorities, without an unapproved weighted social-value score.

The page explicitly states that overlap alone does not establish damage, service failure, financial loss, realized benefit, or customer demand. Each area still presents its empirical management/research rationale, value-integration question and dimensions, common archive screen, proposed validation path, and evidence limits.

## Automated and package checks

| Check | Result | Scope |
|---|---|---|
| Full hash-locked Python 3.12 suite | 138 passed in 72.90s before the focused v44 UI addition | Full repository test suite on the pre-v44 worktree; this is author-run, not independent reproduction. |
| Updated study-profile/generator tests | 14 passed in 0.39s after the v44 change | Includes 8+8 profile parity, generator idempotency, the five shared stages, and claim-limit wording. |
| Inline JavaScript syntax | Passed | One embedded script extracted from the packaged v44 page and checked by Node 26.13.0. |
| Static page asset links | 10 checked; 0 missing | Local package contains every referenced JSON/CSV evidence asset. |
| Archive structure | Passed | Contains the static page, configured Sites manifest, and evidence JSON/CSV assets; 17 files. |
| `git diff --check` | Passed | Current worktree and Site source checkout. |

GitHub Actions run `41752413472` passed both the test/container and dependency-security jobs on private PR commit `14b5a1e2734fea5882631123ce5b5c0b647527e4`. That run predates the v44 value-framework addition and is not counted as verification of it.

## Production workflow coverage and limits

The authenticated v43 production replay passed all 16 candidate profiles, the Baton Rouge/Hurricane Ida scenario, method comparison, asset detail, reset, synthetic CSV export, and CEMS card; results are documented in [the v43 walkthrough](atlas-v43-end-to-end-checklist.md). The v44 change is static informational content and does not change those controls. A fresh browser replay of v44 could not be completed in this run because the Codex desktop browser bridge returned `transport closed before response` on reconnect. The page is deployed and available at the production URL above, but the new framework was not visually click-verified in the browser during this release check.

The current analysis remains synthetic. The 16 locations are candidate areas, not confirmed enrolled study sites. Confirmatory eligibility is **0/16**. Current evidence establishes location-specific public research/management need, not ATLAS market demand. Metadata discovery, coverage-conditioned RTC availability, Groundsource event leads, and spatial reference records do not establish comparable event-matched observations, independent labels, flood accuracy, or social benefit.

## Score and open gates

The canonical score remains **60/100 provisional** under the documented 5-point-or-zero rubric. v44 adds research rationale and traceable public-value boundaries but does not earn unsupported product, scientific-validation, scale, usability-study, four-cloud deployment, or independent-reproduction points. A score of 100/100 is not substantiated.

See [canonical scorecard](atlas-scorecard.md), [8+8 study-area program](atlas-study-area-program.md), [current worktree revalidation](atlas-current-worktree-revalidation.md), and [guided live walkthrough](atlas-live-walkthrough.md).
