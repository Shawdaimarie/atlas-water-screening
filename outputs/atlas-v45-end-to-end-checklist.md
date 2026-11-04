# ATLAS v45 release and end-to-end checklist

**Checked:** 2026-11-03 America/Chicago (Sites readback timestamps are in UTC)  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Site version:** v45  
**Deployment:** `appgdep_6aeaa307a37c8191ad760a055e109dfd`  
**Source commit:** `a3718a6043d131fc989e1d172d41a90e839f6cf7`  
**Archive SHA-256:** `7338d6ac98da75340468209d10d89b2dbfa3cb0e958279c7e6a6b94fcc649c2e`  
**Packaged files:** 17

## Verified deployment state

- Sites reports v45 as the active version, deployment status `succeeded`, and the production URL above.
- The access policy is custom owner-only: `shawdaimarie@gmail.com` is the sole authorized viewer; no external visitors are listed.
- An unauthenticated HTTP request to the production URL returned **401**, consistent with the owner-only access policy.
- The saved version ties the deployment to source commit `a3718a6043d131fc989e1d172d41a90e839f6cf7` and the 17-file archive hash above.

## v45 study-area evidence update

- The candidate screen remains balanced at **8 U.S. and 8 international areas**, using the same nominal 625 km² footprints, common OPERA metadata query, public-need evidence fields, value-integration questions, validation paths, and explicit scope limitations.
- The Singapore profile now cites the official PUB list of **36 named flood-prone locations** as national management-need context. It does not assert that these locations intersect the fixed ATLAS box, provide event-level inundation geometry, or qualify as validation labels. The data.gov.sg staging page is explicitly excluded. See [Singapore source audit](atlas-singapore-source-audit.md).
- The page links to the complete machine-readable [8+8 evidence register](atlas-study-area-evidence-register.json).
- The matched RTC quota remains a spatial-availability screen only. Confirmatory eligibility is **0/16**; there are no independent event labels sufficient to support the study comparison. The walkthrough's analysis values remain synthetic fixtures.

## Software and package checks

| Check | Result | Scope |
|---|---|---|
| Full hash-locked Python 3.12 suite | **139 passed in 18.16s** | Current worktree; dependencies installed from both lock files with `--require-hashes`. Author-run software checks, not independent reproduction. |
| GitHub Actions on current PR head `26e5a6d0b3d599d4b2c124d3bac205ccab7cb15b` | **139 passed in 3.81s; all jobs succeeded** | Run [41776500087](https://github.com/Shawdaimarie/atlas-water-screening/actions/runs/41776500087) also passed the 16-area GEOID-Flood screen, container build/runtime audit, 11/11 HTTP smoke checks, and dependency-security scan. |
| Local page references | **12 checked; 0 missing** | Relative `href` and `src` references in `dist/index.html`; includes the complete JSON evidence register. |
| `git diff --check` | Passed | Current worktree. |
| Live production response without sign-in | **401** | Confirms private access behavior; does not exercise authenticated UI workflows. |

## Authenticated browser walkthrough — 2026-11-04

The current production page was opened in the authenticated in-app browser and observed as version 45. The full replay passed:

- Selected every candidate-area card. All **16/16** profiles displayed the rationale, public evidence, value-integration question, comparable validation path, scope limit, and candidate-only status.
- Selected Singapore and verified the live profile cites PUB's 36 named flood-prone locations while explaining that the national list is not an event label and has no verified intersection with the frozen AOI.
- Switched the analysis to Baton Rouge / Hurricane Ida, selected **Quality-aware aggregate**, and selected Southeast Water Plant. The asset detail identified it as water exposure only.
- Exported and parsed the live synthetic evidence file: **12 data rows**, method `aggregate`, event `Hurricane Ida`, and `data_status=synthetic_fixture_no_live_NASA_data`.
- Exported and parsed the live study-area register: **16 rows**, 8 United States + 8 International, 25 fields.
- Opened the deployed evidence matrix JSON and parsed its 16-area summary: **0 confirmatory-eligible**, 192/192 groups selected under the matched RTC availability quota, and 169/192 initial groups above the screen. Opened the event-opportunity JSON and the 16-area reference-readiness ledger; the ledger reports 0 eligible areas.
- Used Reset and verified the method returned to Single observation while the selected scenario remained Baton Rouge / Hurricane Ida. Set the page back to Houston / Hurricane Beryl, selected Singapore, and left the live Site visible for the user.

These checks establish deployed UI behavior and export integrity. They do **not** validate the illustrative fixture values, event-date opportunity leads, independent-label adequacy, or flood-classification accuracy. A new production UI replay is no longer pending for v45.

Use the [guided walkthrough](atlas-live-walkthrough.md) to repeat the sequence.

## Readiness and score limits

- The four-cloud `--example --release-ready` preflight reports **29 missing or invalid inputs** and creates no resources. No Google Cloud, AWS, Azure, or Oracle deployment is verified.
- The Apple account is a separate future distribution path. There is no native app target or verified TestFlight/App Store build; Apple does not host the browser Site.
- Canonical rubric score remains **60/100 provisional**. The 8+8 candidate frame, software tests, and deployment do not establish validated flood observations, independent labels, or confirmatory enrollment.
