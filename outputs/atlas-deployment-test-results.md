# ATLAS deployment and verification results

**Run date:** 2026-11-02\
**Production Site:** [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/) (private owner-only access)\
**Current published Site version:** 15
**Current source commit deployed:** `07d6c103d7612d34f0bb6e8e6bd1a7792b6bc2c9`
**Version provenance:** Sites readback matched version 15 to the deployed source commit and deployment `appgdep_6ae954d29ca48191977d5426931aea8e`; deployment status was `succeeded` at the existing private URL.

## Result summary

The private static Site is deployed (version 15) and the study-area candidate register is visible and interactive. Its downloadable CSV contains the complete per-area acquisition-date sets, AOI bounds, collection, and query window. The current product remains a synthetic research walkthrough. The register is an archive metadata discovery screen; its scenes have not been downloaded or pixel-QA audited for the 16 enrolled candidates. Therefore the project is **not 100/100** and the study areas are not yet fully validated.

## Checks completed

| Check | Result | Evidence |
|---|---|---|
| Production publish | Pass | Sites readback on 2026-11-03 confirms active version 15, source `07d6c103d7612d34f0bb6e8e6bd1a7792b6bc2c9`, and successful deployment recorded above. |
| Access policy | Pass | Version 15 Sites readback confirms the existing owner-only custom allowlist contains `shawdaimarie@gmail.com`; zero external visitors. This is Sites account access; Apple Sign In is not configured. |
| U.S./international register | Pass for candidate presentation | Version 12 walkthrough rendered 8 U.S. and 8 international candidate areas and exercised all 16 profiles. They remain metadata-screened candidates, not validated sites. |
| Candidate profile interaction | Pass | Selected Mumbai; rationale, value-integration question, 361 metadata hits, and 121 acquisition dates appeared. |
| Candidate register export | Pass | “Download area register” produced the visible “Study area register downloaded as CSV” success message. |
| Method comparison | Pass | Aggregate view changed the lead synthetic asset from 28.6% to 21.4%, elevated count from 4 to 3, and median from 7.7% to 6.8%; UI labels the result experimental/synthetic. |
| Area/event workflow | Pass | Switching to Baton Rouge changed to Hurricane Ida, event and baseline dates, map labels, and LA fixture IDs. |
| Asset detail | Pass | Selecting Southeast Water Plant updated detail values and asset ID. |
| Synthetic evidence export | Pass | Export button showed its success message with synthetic-data labeling and selected method. |
| Reset workflow | Pass | Reset restored the single-scene baseline values and method labels. |
| API and metadata unit tests (earlier snapshot) | Pass locally | The version-12-era suite had 40 passing tests in 1.33s with one LibreSSL/urllib3 environment warning. See the dated current full-suite result below. |
| API HTTP smoke | Pass locally; not deployed | Local fixture API health, area listing, analysis, CSV, and request-boundary checks passed. Health explicitly reports `live_nasa_ingestion:false`; the API is not connected to the Site. |
| Static/document checks | Pass | HTML parser accepted the deployed source; structural checks confirmed exactly one study-area panel and 16 records with 8 per region. |
| Focused accessibility checks | Pass with documented limits | Updated muted-text colors measure 5.87:1 on white, 5.44:1 on the method card, and 5.04:1 for warning text. Keyboard Tab/Enter selected Miami and updated its profile. Touch targets and focus styling were improved; VoiceOver/NVDA and zoom review remain open. See `atlas-accessibility-review.md`. |
| CMR metadata screen | Pass for discovery only | Reproducible query returned complete result pages for 16 equal nominal 625 km² AOIs using the common DSWx-S1 V1 window. All exceeded the 90-date metadata screen; distinct acquisition dates ranged from 99 to 403. |
| Temporal overlap audit | Pass for metadata only | Exact `time_start` date intersecti