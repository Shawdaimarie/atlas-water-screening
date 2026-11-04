# ATLAS v37 end-to-end release checklist

**Run date:** 2026-11-03  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Audience:** private owner-only Site  
**Result:** deployed successfully; new criteria card and JSON route verified in production

## Release provenance

- Site version: **37**.
- Source commit: `2a74d35d2451e311e4f6eec723fe453092bedbb9`.
- Deployment: `appgdep_6aea23764d64819198aa4c9d99def75b`; Sites returned `succeeded`.
- Post-deploy Sites readback: active Site, latest version 37, custom access, zero external visitors, one allowed owner.
- The v37 page adds a visible evidence-based selection summary and links to a generated 16-area JSON/CSV matrix. The publication uses the existing private audience.

## Selection matrix verification

- The builder reconciles the study-area register, pinned reference-readiness ledger, and unique RTC sample audit by exact region/city keys; it fails closed if any source has a different area frame.
- All 16 candidate areas are present: 8 U.S. and 8 international. All use the common 625 km² nominal AOI and OPERA DSWx-S1 V1 metadata window.
- It reports the current evidence as: 16/16 have a recorded public-need rationale and complete CMR metadata query; 169/192 separate RTC samples meet the 80% finite/non-nodata VV floor, with 10/16 areas passing all 12; 0/16 are eligible for confirmatory enrollment.
- The report does not use a composite city-value score. It distinguishes candidate discovery from confirmatory eligibility and describes CMR, Groundsource, RTC, and reference-lead limits.
- Input SHA-256 values are included in `outputs/atlas-site-selection-evidence-matrix.json`.

## Automated verification

- New focused matrix tests: **4 passed**.
- Full hash-locked Python 3.12 suite: **96 passed in 1.41s**.
- Published inline JavaScript: `node --check` passed using the verified Node.js 26.13.0 local toolchain.
- `git diff --check`: passed.

## Production browser verification

- Opened v37 and verified that the visible selection criteria card reports the 8+8 frame, equal-area rule, common collection/window, 169/192 availability diagnostic, 10/16 full RTC screen, and 0/16 confirmatory eligibility.
- Followed **Open full selection and readiness matrix**; the production JSON endpoint displayed all six criteria and all 16 area rows. Its source hashes and summary matched the local generated artifact.
- The **Download 8+8 evidence matrix CSV** link was exercised in the authenticated production browser and produced a saved file. Parsing confirmed 16 rows, exactly 8 U.S. and 8 international areas, all 16 candidate names, and 0 confirmatory-eligible areas. The JSON content was also opened and inspected in the live browser.
- Prior v35/v36 release records contain the core walkthrough replay for area profiles, Hurricane Ida/Baton Rouge scenario, synthetic method comparison, asset details, export notice, and Reset. v37 changes selection transparency and adds matrix links; those prior interaction results do not imply live raster processing.

## Follow-up production replay (2026-11-03)

- Selected Mumbai in the 16-area profile list. The live profile displayed 361 CMR granule metadata hits, 121 distinct dates, the 625 km² nominal area, public flood-management evidence, value-integration question, and the explicit pending QA/independent-label status.
- Changed the separate synthetic analysis scenario to Baton Rouge / Hurricane Ida and changed the method to **Quality-aware aggregate**. The UI showed 3 elevated assets and 6.8% median fixture overlap; selecting Southeast Water Plant displayed 18.9% fixture overlap, 93% fixture coverage, and an uncalibrated confidence value. The analysis remains labeled synthetic and is not linked to the Mumbai candidate profile.
- **Export evidence** produced a browser-saved CSV. Parsing found 12 rows, all for Baton Rouge / Hurricane Ida, method `aggregate`, and `synthetic_fixture_no_live_NASA_data`.
- Downloaded and parsed the 8+8 matrix CSV in the same live replay: 16 rows with an 8/8 region split and 0/16 confirmatory eligibility. These successful save events replace the earlier v37-run limitation above.
- **Reset analysis** restored the single-observation method; the scenario controls stayed on Baton Rouge/Hurricane Ida. I then explicitly restored the Houston/Beryl starting scenario. Mumbai stayed selected in the separate candidate register throughout.
- The browser was left open on the live Site with Mumbai selected and the candidate-profile section visible. No score points are added: the scenario values are synthetic and the matrix reports no confirmatory area.

## Research and score limits

The matrix strengthens explicit, evidence-based selection and makes area differences reviewable. It does **not** establish market demand, real OPERA water classification, balanced event/baseline observations, independent labels, or a completed cross-city comparison. Confirmatory enrollment remains 0/16. No rubric points are added; canonical score remains **55/100 provisional**. Four-cloud hosting, Apple app distribution, capacity, accessibility/user-study, and independent-reproduction gates remain open.
