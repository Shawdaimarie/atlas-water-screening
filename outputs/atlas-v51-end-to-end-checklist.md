# ATLAS v51 deployment and end-to-end check

Checked 2026-11-04 America/Chicago.

## Release

- Production Site: `https://atlas-water-screening.shawdaimarie.chatgpt.site/`
- Version: **51**, status active; deployment `appgdep_6aeadaca101c8191b8c49f204278daf8` succeeded.
- Source commit: `80d16ef509410c0968ce86da16219e2ba0effd05`; saved version `appgprj_6ae8f548d7a48191adbbfe7affb04a94~appgver_ea9e4bfed69081919115dbfaefd49723`.
- Packaged release archive SHA-256: `305890f7c9e2a9e67bf7d74fe9419e51e4daf418a9d7afcd9ad4ed94715830ac`; archive listing confirms the four refreshed CSV/JSON assets are present.
- Access readback after deployment: custom owner-only access for `shawdaimarie@gmail.com`; zero external visitors. The existing private audience was preserved.
- Release payload updates four 8+8 study-selection and reference-readiness downloads. The interactive page remains the v50 interface; no API runtime or event-analysis behavior changed.

## Verification

- Full repository test suite with the CI dependency contract (`requirements-dev.lock` and `requirements-reference-audit.lock`, installed with `--require-hashes`) in Python 3.12: **143 passed in 1.25 seconds**.
- Production matrix JSON opened from the deployed Site. It contains 16 candidates (8 U.S. and 8 international), 16 documented public-need contexts, 192 selected RTC groups, and **0 confirmatory-eligible areas**. Jakarta event-area context is shown as 20/21 administrative polygons intersecting the fixed AOI, with explicit limits that this is not a flood location or validation label.
- Production walkthrough replay: changed from Houston/Beryl to Baton Rouge/Ida; selected quality-aware aggregation (elevated assets changed 4 to 3 and median fixture overlap 7.7% to 6.8%); selected Southeast Water Plant and observed its 18.9% synthetic overlap, 93% valid coverage, and 73% uncalibrated fixture confidence.
- Evidence export displayed its success message and labeled the export synthetic. The 8+8 area-register CSV control displayed its download success message.
- Reset returned the method to single observation and restored the 4-asset/7.7% baseline. The selected Baton Rouge/Ida scenario remained available for the live demo.
- `git diff --check` passed before packaging.

## Limits and score

The walkthrough and exported fixture values remain synthetic. The updated candidate matrix improves evidence visibility; it does not establish comparable event observations or independent labels. No registered area is confirmatory-eligible. No cloud-provider staging or production environment was deployed or tested by this release. The canonical rubric score remains **60/100 provisional**; deployment checks do not earn research-validity, capacity, user-study, or independent-reproduction points.
