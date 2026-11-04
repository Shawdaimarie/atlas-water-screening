# ATLAS v34 deployment and end-to-end replay

**Run date:** 2026-11-03  
**Production:** [ATLAS private Site](https://atlas-water-screening.shawdaimarie.chatgpt.site/)  
**Release:** Site v34 · source commit `f6acd59c4c5610591be5d25eb1ba030cbfdfbd94` · deployment `appgdep_6aea1b56af2c81919494c9300621a370` · result `succeeded`  
**Access check:** control plane reports `active`, custom owner-only access, zero external visitors, and latest version 34.

## Test record

| Check | Result | Evidence |
|---|---|---|
| Published source JavaScript syntax | Pass | `node --check` on extracted inline script from the exact packaged `dist/index.html` |
| Patch whitespace check | Pass | `git diff --check` |
| Full regression suite | Pass | Python 3.12 environment: `89 passed in 1.38s` |
| Keyboard method selection | Pass | Space toggled `aria-pressed`; single scene showed 4 elevated / 7.7% median, aggregate showed 3 / 6.8% |
| Keyboard asset selection | Pass | Selecting Southeast Water Plant updated selected state and detail to 18.9% overlap, 93% valid coverage, 73% illustrative uncalibrated confidence |
| Reset workflow | Pass | Restored single-scene method, 4 elevated, 7.7% median and Bayou East Substation selection |
| Candidate profile | Pass | Mumbai displayed 361 metadata hits, 121 dates, a consistent 625 km² footprint, public evidence and 12/12 sampled 2025 RTC groups above the 80% spatial screen; status remains candidate-only |
| Event workflow | Pass | Hurricane Ida switched the demonstration to Baton Rouge and 2021 event/baseline windows |
| Evidence export | Pass | Browser downloaded 12-row CSV; parsed columns include area, event/window, method, overlap, coverage, confidence and `data_status` |
| Study register export | Pass | Browser downloaded 16-row CSV; parsed split is 8 United States + 8 International |

All analysis values in the deployed workflow remain synthetic fixtures; the candidate metadata, sampled valid-pixel proportions, and reference leads do not constitute flood classification or independent validation. The 0/16 confirmatory-enrollment gate remains unmet.

## Accessibility and scope limits

The v34 replay verifies keyboard operation and the browser accessibility tree’s selected-state and live-detail announcements for the method and asset controls. It does not establish screen-reader acceptance across assistive technologies or a task-based usability study. Per the existing strict rubric, Usability remains 0/10 until both required evidence conditions are met; total remains **55/100 provisional**, not 100/100.

The live web Site is hosted by the current Sites service. An Apple Account can support a future Apple Developer/TestFlight/App Store release after a native app target exists; it does not host this browser Site or create Google Cloud, AWS, Azure, or Oracle Cloud accounts. Those provider deployments remain unverified.
