# ATLAS v42 Deployment and Walkthrough Record

Date: 2026-11-04

## Release identity and access

- Site: [ATLAS | Water Exposure Screening](https://atlas-water-screening.shawdaimarie.chatgpt.site/)
- Site version: 42
- Deployment: `appgdep_6aea770b44808191bcc83272f0e6ad53`
- Status: succeeded
- Source commit: `860ea7026d8aff26e5bc45c005392eb77782e392`
- Packaged archive: 1,873,920 bytes, 16 files; SHA-256 `0fe948efa1bffc316c647cb7f12508322d3145ea2fd08958fd47544708a79938`
- Access: custom owner-only policy; owner verified; zero external visitors.
- The deployed Site includes the full JSON companion to the balanced 8+8 register and links it next to the area-register CSV control.

## End-to-end workflow results

| Workflow | Result | Evidence |
|---|---|---|
| Owner opens production Site | Pass | Refreshed authenticated in-app page rendered the current v42 UI. |
| Choose Baton Rouge / Hurricane Ida scenario | Pass | Scenario heading and date window changed to East Baton Rouge Parish, 29–30 August 2021. |
| Select every registered study area | Pass | Clicked all 16 U.S. and international candidate controls in turn; each updated the detail heading and showed all required location-specific fields: public evidence, value dimensions, validation path, scope limit, and primary evidence link (16/16). |
| Select Dubai study candidate | Pass | Detail profile updated to Dubai and displayed its management rationale, cited program facts, value dimensions, validation path, and evidence limit. |
| Switch analysis method | Pass | Quality-aware aggregate control became active; synthetic ranked overlaps changed and provenance described the three-observation fixture. |
| Select an asset detail | Pass | Southeast Water Plant selection updated the detail panel to asset LA-002. |
| Reset analysis | Pass | Reset returned the method to the single-observation baseline and reselected Bayou East Substation. The chosen study scenario remains Baton Rouge / Hurricane Ida. |
| Read full evidence JSON | Pass | Parsed the production endpoint: 16 results, 8 per region, equal nominal 625 km² fields, common OPERA collection/window, date-array counts consistent, and all evidence/value/validation/scope fields populated. |
| Export scenario evidence CSV | Pass | Download completed. File inspection: 12 data rows; includes scenario, event/baseline windows, method, exposure, coverage, fixture confidence, and synthetic data-status fields. |
| Local validation suite | Pass | Hash-locked Python 3.12 Bookworm run: 136 tests passed in 2.26 seconds. Added area test verifies all WGS84 boxes compute to 623.596–623.601 km² with spherical-area approximation, within 1% of nominal 625 km² and 0.005 km² spread. |
| Patch whitespace validation | Pass | `git diff --check` passed. |

The direct click on the JSON download link did not produce a browser download event in this session. The target URL was independently opened in a second browser tab and its JSON content was verified; the primary scenario CSV download completed normally.

## Research and product limits

The site presents a 16-area candidate frame (8 U.S., 8 international) with equal nominal 625 km² areas, a shared OPERA DSWx-S1 metadata window, and area-specific empirical public evidence and research rationale. These are candidate locations only: **0/16** meet the independent-reference and sampling gates for confirmatory enrollment. The scenario portfolio and all computed exposure/ranking values in the walkthrough are synthetic; the page makes that boundary explicit. Deployment and UI tests do not convert synthetic values into validated observations.

The canonical author-verified provisional score remains **60/100**. A 100/100 score is not supported by the current evidence: scientific enrollment, independent reproduction, user study/accessibility acceptance, declared-load/cost evidence, and verified Google Cloud, AWS, Azure, and Oracle Cloud deployments remain incomplete. The current Site is a private browser application; no native Apple app target or Apple distribution build was verified.

## User walkthrough

Open the production link above. Choose Baton Rouge and Hurricane Ida in the left setup controls. In the expanded research program, choose Dubai (or Jakarta, Singapore, or Mumbai) to inspect its evidence and value profile. Scroll to “Compare screening methods” and toggle “Single observation” and “Quality-aware aggregate.” Select an asset to inspect its detail. Use “Export evidence” for the synthetic scenario CSV, and “Download full evidence JSON” beside “Download area register” for the research-area register.

The authenticated browser was left visible on the active ATLAS page with Baton Rouge / Hurricane Ida and Dubai selected. The saved version's screenshot endpoint returned HTTP 200 with a 1200×750 JPEG (140,104 bytes); the capture shows v42's full-evidence JSON link and candidate register. The interactive session screenshot also showed Dubai selected. The saved screenshot shows the default Houston/Beryl profile and does not include below-fold controls.

![ATLAS v42 deployed Site capture](/Users/shawdaimarie/Documents/Codex/2026-11-02/atlas/outputs/atlas-site-v42-deployment-capture.jpg)
