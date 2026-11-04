# ATLAS next release preparation

**Prepared:** 2026-11-03  
**Current production:** Site v36, active and owner-only  
**State:** published and browser-checked

## Change prepared

The 16-area readiness card now provides two distinct controls for the Groundsource event/date audit: an “Open … JSON” link that opens the report in a new tab, and a separate “Download … JSON” link. The existing download link had correct same-origin HTML but its browser download event did not complete in the prior replay; direct authenticated endpoint viewing worked. Separate controls make those outcomes explicit and preserve the saved-file option.

## Verification

- Regression assertion covers both the open-in-new-tab link (`target="_blank"`, `rel="noopener"`) and the separate download link.
- Full hash-locked Python 3.12 suite: **92 passed in 1.45s**.
- `scripts/build_reference_readiness_ledger.py` regenerated the 16-area ledger assets and `dist/index.html`.
- `git diff --check` passed.

## Publication and live verification

- Site v36 deployment `appgdep_6aea2118b6988191ba84354f60b9a61e` succeeded from source commit `fc94165e833e8d9fd51ba23febc4ca96a2cced5e`.
- Sites readback reports v36 active, private owner-only access, and zero external visitors.
- Production page shows separate open and download controls. Clicking the open control opened the audit JSON in a new tab. The browser did not report a saved-file event for the download control, so file download remains unverified.
- Live workflow replay on v36 also selected Mumbai (candidate-only; 361 metadata hits and 121 dates), switched to Hurricane Ida/Baton Rouge, changed from the single-observation fixture (4 elevated / 7.7% median) to quality-aware aggregation (3 / 6.8%), and triggered the evidence-export success notice. The interface identifies all analysis values as synthetic.
- The full Python 3.12 suite passed **92 tests in 1.45s**; `git diff --check` passed.

This verifies publication and the new open-link behavior. It does not verify the browser's download save event, cloud deployment, scientific validation, or raise the canonical score above **55/100 provisional**.
