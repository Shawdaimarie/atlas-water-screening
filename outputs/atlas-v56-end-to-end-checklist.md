# ATLAS Site v56 release and verification record

**Date:** 2026-11-04  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Site version:** 56  
**Sites source commit:** `184b5ac7309ff69a8e33201087eab214c2890e4d`  
**Deployment:** `appgdep_6aeaebcca5e88191a27437915d99d473` — `succeeded`  
**Local package SHA-256:** `1cd1722eb25df2f980fbb524f4187eef295ed5670562e7eec3e93dcffc4ac288`

## Change

The evidence-readiness card now shows the actual GEOID-Flood mask coverage measured inside the fixed St. Louis AOI: **77.70% mapped labels** and **22.30% outside mapped labels**. It explains that the 2017 EMSR203 case is in the benchmark's training split, outside the shared 2024–2026 window, and not held-out validation. The other 15 areas retain `null` for GEOID-Flood pixel coverage; catalog tile footprints are not presented as measured valid-label coverage. The card links to the hash-verified St. Louis audit JSON.

## Verified

- Sites control-plane readback reports version 56 active at the production URL, the expected source commit, the successful deployment, custom owner-only access for `shawdaimarie@gmail.com`, and zero external visitors.
- The saved archive contains 24 files. Its `dist/index.html` contains the new coverage disclosure and audit link. Its ledger JSON has all 16 areas; St. Louis records `0.776967480906398` and Houston remains `null` for this source-specific measure.
- Focused readiness-ledger and GEOID label-audit tests: **9 passed**. Full local test suite: **157 passed**, with one existing LibreSSL/urllib3 warning. `git diff --check` passed.
- The full source-audit result, pinned catalog/shard hashes, pixel classes, and limitations are recorded in `atlas-geoid-flood-stlouis-label-coverage.md` and its JSON companion.

## Production browser replay status

Authenticated replay on the published owner-only v56 Site **passed**. The page loaded at the production URL. St. Louis was selected and its evidence profile displayed. The St. Louis audit link opened the live JSON audit. The scenario selector changed from Houston/Beryl to Baton Rouge/Ida and updated the fixture title, dates, and metrics. Quality-aware aggregation changed the synthetic values and method description; selecting Southeast Water Plant updated its detail and asset code. Evidence export produced the success message and downloaded the evidence file with scenario, windows, method, and synthetic-data label. Reset returned to the single-observation baseline. These are UI workflow checks on synthetic analysis fixtures, not scientific validation.

## Walkthrough

1. Open the production URL and sign in as the Site owner.
2. Scroll to **16-area evidence-readiness ledger** and find **Historical reference-pixel coverage**.
3. Confirm the card states 77.70% mapped for St. Louis, labels the event as historical training data, and says no pixel coverage has been measured from GEOID-Flood for the other 15 areas.
4. Open **St. Louis label-coverage audit** and verify the 6,244,762 AOI pixels, class 255 outside-map count, the source hashes, and the training-split/time-window caveat.
5. Use the existing 16-area JSON/CSV controls and confirm St. Louis has a numeric GEOID mapped-label fraction while the other areas preserve null values.

Screenshot: `atlas-v56-live-walkthrough.jpg` (captured from the published page with the Singapore candidate profile visible).

## Research gate and score

The source audit and Site update add **no confirmatory enrollment**. The program remains 8 U.S. and 8 international candidates, **0/16 confirmatory-eligible**. Following the later source-provenance audit, the current canonical score is **60/100 provisional**; exact-source clean-checkout reproducibility is now verified on canonical main at `8014d08be673c3ecc9501d7fcd1a36022e4695e5`. Research-grade matched event/baseline observations and independent labels across all 16 areas, usability acceptance, cloud deployment evidence, and independent reproduction remain outstanding.
