# ATLAS Site v50 end-to-end checklist

Updated: 2026-11-04

## Release identity and deployment

- Product: private ATLAS browser Site: <https://atlas-water-screening.shawdaimarie.chatgpt.site/>.
- Site version: **50**; deployment `appgdep_6aead729d1008191a02eed2dffbf574e` returned `succeeded`.
- Source commit: `9e8fbbe7f85f314c764a6cea01569d73bdcaf14a`.
- Local deployment archive SHA-256: `c201f9606f5047eafa874c03d362d1a29a0ecabf18f1c46046232c3b9b8dd0ef`.
- Sites archive readback: SHA-256 `d1fd67d5d205ce916cdffdccb6fe9e15b6991da10e1bc68a8ed82391d46da799`, 17 files.
- Sites control-plane readback: Site active at v50, custom owner-only access, owner `shawdaimarie@gmail.com`, zero external visitors.
- The release adds the official Jakarta event-area context to the selection card and deploys the linked audit JSON. `dist/index.html` SHA-256 is `100a0d3daa7c945edaeb26f6249563d39e3b256ecbd3aeb261a9ad67cd300f83`; Jakarta JSON SHA-256 is `17cb9980daa44e772df9b3ffe42631d956ffc657c919030b9d1df5c542d020eb`.

## Verification

- Full current-worktree Python 3.12 suite using digest-pinned Bookworm and hash-locked dependency files: **143 passed in 1.42s**. `git diff --check` passed. This tested the source candidate that produced the v50 site files.
- Static package check against the Site-linked source: inline JavaScript syntax valid; 14 static local file references checked and 0 missing.
- Authenticated production replay after deployment showed the updated card: BPBD reported 90 inundated RT and 10 roads, and 20/21 named affected kelurahan administrative polygons positively overlap the fixed Jakarta box. The note explicitly says this does not locate water within the AOI, provide pixel labels, or pass QA.
- Clicked the Jakarta profile: the location-specific rationale, evidence, integration question, comparability path, and pending validation limits rendered. All 16 profiles had the same four content checks in the v49 replay; v50's code change only updates the evidence card and audit JSON.
- Opened the linked production Jakarta JSON endpoint in the authenticated browser. It parsed and showed the reported interval, source URLs, boundary-service checksum, 20 positive-area intersections, and `confirmatory_enrollment_eligible=false` / `score_credit=0`.
- Ran the analysis controls in production: Hurricane Ida selected Baton Rouge and updated the event window; quality-aware aggregation changed the illustrative elevated count from 4 to 3 and median overlap from 7.7% to 6.8%; selecting Southeast Water Plant displayed 18.9% fixture overlap, 93% valid coverage, and 73% uncalibrated fixture confidence. Export Evidence and Download Area Register displayed their success messages. Reset returned to the single-observation baseline; the walkthrough state was then restored.
- The live page is left open on the Jakarta event-context card, with Baton Rouge / Hurricane Ida, quality-aware aggregate, and Southeast Water Plant selected for the guided demo. The figures remain explicitly synthetic.

## Interpretation and remaining gates

- The 20/21 Jakarta result is administrative event context, not flood extent inside the AOI, a label set, or product validation. See [BPBD/admin-boundary audit](atlas-jakarta-bpbd-jan2026-aoi-context.md) and [8+8 matrix](atlas-site-selection-evidence-matrix.md).
- The canonical score remains **60/100 provisional**; confirmatory eligibility remains **0/16**. No score points come from the evidence-card release. The research objective is not complete at 100/100.
- Google Cloud, AWS, Azure, and Oracle Cloud deployments remain unverified. The selected Apple Account is noted for an Apple distribution path, but this Site is browser-hosted; a native iOS target, full Xcode, and Apple Developer Program/App Store Connect access are unverified.
- The v50 release updates the Sites-linked source branch. The separate local GitHub checkout remains an older, divergent worktree and should be reconciled before claiming the whole development repository is synchronized.
