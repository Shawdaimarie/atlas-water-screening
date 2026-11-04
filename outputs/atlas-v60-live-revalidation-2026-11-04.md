# ATLAS v60 live revalidation — 2026-11-04

## Release identity and access

- Sites control-plane readback reports the existing ATLAS project active at `https://atlas-water-screening.shawdaimarie.chatgpt.site`, with latest version **60**.
- Version `appgprj_6ae8f548d7a48191adbbfe7affb04a94~appgver_38a8500036dc819183dd85c60a4d47b9` is sourced from commit `73207c38e528e8e0fd2552d300637c61e8ee8257`; deployment `appgdep_6aeb0154a2588191bb41dd0cb899deb5` reports **succeeded**.
- Access readback reports custom owner-only access for `shawdaimarie@gmail.com`, zero external visitors, and the current user as owner. The audience was not changed.
- The deployed page includes the 16-area candidate evidence and common research-readiness disclosures. Confirmatory eligibility remains **0/16**; synthetic scenario/map/assets/results remain clearly identified as fixtures.

## Keyboard and link verification

On a fresh authenticated production tab:

1. Pressing `Tab` from the initial page state focused “Skip to main content”; it became visible at the top of the page with a 44 px target.
2. Pressing `Enter` changed the URL fragment to `#mainContent`, moved focus to the main landmark, and scrolled that landmark to the top of the viewport.
3. The target is a `<main id="mainContent" tabindex="-1">`, allowing programmatic focus after activation.

The visual inspection also found 37 content links with target heights of at least 24 px in the deployed DOM. This is a focused author-run check, not WCAG conformance certification. Screen-reader acceptance, 200% zoom, exhaustive contrast measurement, and a task-based usability study remain outstanding.

## Local verification

- Full suite: `.venv/bin/python -m pytest -q` — **166 passed** in 1.92 s.
- One existing environment warning: the Python 3.9 virtual environment's urllib3 detected LibreSSL rather than OpenSSL. No test failed.
- Cloud release preflight: `scripts/validate_cloud_inputs.py --example --release-ready` failed closed with **29** missing or invalid account, billing, region, budget, hosting, and federated-identity inputs. No cloud resources were created; `deployment/cloud/owner-inputs.local.yaml` is absent.
- Apple distribution inspection: no `.xcodeproj` or `.xcworkspace` exists, and `xcodebuild -version` reports that this Mac has Command Line Tools rather than full Xcode. The user's existing Apple Account remains the intended Apple distribution account, but Developer Program membership and App Store Connect access are unverified.

## Score and limits

The canonical score remains **60/100 provisional**. The v60 accessibility improvement adds no usability points because the rubric requires both a task-based study and complete accessibility acceptance. Real event/independent-label validation, production API authentication/isolation, deployed cloud releases, capacity/cost evidence, and independent reproduction remain unverified. The current evidence does not support 100/100.

## Source alignment

The Sites release is proven to use source commit `73207c38e528e8e0fd2552d300637c61e8ee8257`. The accessible v60 UI/test delta was merged into canonical GitHub main in PR #8 (merge commit `b731570dbda7021fa18a84fb791b90de04a9ce9d`). The local checkout remains an older base with substantial uncommitted work; this does not imply that the entire worktree is committed or aligned with GitHub.
