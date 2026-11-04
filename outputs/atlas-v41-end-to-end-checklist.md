# ATLAS Site v41 release verification

**Date:** 2026-11-03  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Deployment:** `appgdep_6aea707f33d08191b4a92ff861797241` — succeeded  
**Saved version:** `appgprj_6ae8f548d7a48191adbbfe7affb04a94~appgver_6cf19bc40d308191b3bb4f331f58caa2`  
**Site source commit:** `e55e1c2393830c0a863994c5700f41f042fb21a1`  
**Packaged archive SHA-256:** `9139a2d4a780323bc446a6b43313caf3c325672837425dbfa82063368b5d7439`

## Verified

- Sites deployment returned terminal status `succeeded`; control-plane readback confirmed v41 active.
- Access readback confirmed the Site remains owner-only with zero external visitors.
- Saved-version readback matched the exact source commit and deployment ID.
- The deployment package contains `dist/index.html`, the Milton audit JSON and CSV, and Site hosting metadata. Source checks verified five expected UI/asset assertions, valid HTML parsing, and JavaScript syntax in Node 22.
- Retrieved the version's generated screenshot from the Sites artifact at HTTP 200 (JPEG, 140,735 bytes; 1200×750). The image visibly shows the deployed ATLAS page rendered, including the balanced 16-area candidate register and the synthetic-data disclosure. Saved copy: `atlas-site-v41-deployment-capture.jpg` (SHA-256 `1bc9f9f68dae346d9d8f0b9ebdd8148a02322e40513f65695ec948a4ead88fab`). The Milton card is below the captured viewport; its markup and links were source-checked.
- Compared the v40 parent source (`5b0c035d27325ad2d60df6961964773c4c877ccd`) with the exact v41 source checkout: inline application JavaScript is byte-identical (SHA-256 `d1703030814b6a9cfb3a1bdae7872dff15c04d8e3ade4638449035a8e69a051e`, 270,627 bytes). The v41 diff adds the Milton card plus its JSON (12,095 bytes) and CSV (422,720 bytes); all three card/link assertions and both nonempty packaged assets passed. This narrows the change surface and supports reusing the prior v40 interaction evidence for unchanged controls, but does not replace a v41 browser replay.
- Parsed the exact packaged JSON and CSV. JSON contains four scene records. CSV has 4,096 rows (1,024 fixed points × four dates), with 2,845 returned samples, 227 no-sample-returned rows, and 1,024 rows explicitly marked `not_sampled_after_service_error`; class counts reproduce the JSON. Packaged asset SHA-256 values: JSON `2c673de008623707c2b1d8056a35293335d41bc5b1941b8b5930f9216411c6f7`; CSV `121ae49e1f8e0709afb8799a5e32ea675f53eaeeccaa2c247f11eb2d88118e11`. This verifies package data integrity, not browser downloads from production.
- Current source suite in the pinned Python 3.12 container passed **130 tests**. `git diff --check` passed before release packaging.

## Not verified in this pass

- A fresh authenticated browser replay of v41 interactions and direct retrieval/byte inspection of the two downloadable artifacts. An authenticated in-app tab opened but displayed older content: the initial 169/192 draw and no Milton card. This differs from v41's packaged 192/192 matched-quota content and Milton panel. A forced reload timed out and disconnected the browser bridge, so this is an unresolved stale-tab/propagation discrepancy, not proof of the current production route's response. The regular Chrome tab showed a blank page and direct unauthenticated HTTP returned **401**, consistent with owner-only access; this is not a test of the authenticated owner experience. The generated v41 deployment screenshot proves initial page rendering only; it does not verify active controls, the Milton card below the fold, or artifact downloads.
- The interface continues to label the Milton data as an exploratory NASA EGIS sample screen. It is preliminary and unvalidated, not full-area coverage, independent truth, or a validated event comparison. The Oct. 10 sampling request returned an endpoint error; see `atlas-tampa-milton-egis-pixel-sample.md`.
- Score remains **60/100 provisional** and confirmatory eligibility **0/16**. The v41 release adds no score credit.

## Reproduction artifacts

- `atlas-tampa-milton-egis-pixel-sample.md`
- `atlas-tampa-milton-egis-pixel-sample.json`
- `atlas-tampa-milton-egis-pixel-sample.csv`
- `scripts/audit_nasa_egis_milton_samples.py`
- `tests/test_nasa_egis_milton_samples.py`
