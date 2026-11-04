# ATLAS v43 end-to-end walkthrough

**Run date:** 2026-11-04 UTC  
**Environment:** authenticated production Site, owner-only  
**URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Site version:** v43  
**Deployment:** `appgdep_6aea7e613920819193a64e36e62bf28b`  
**Source commit:** `7da85f1044c20e269dcc3eb8a189eafc1ea890f7`

## Deployment verification

- Sites control-plane readback reports v43 active, deployment successful, private/custom owner-only access, and zero external visitors.
- Saved version source commit matches the published Site source. The deployed archive SHA-256 is `028680b2baa75ef0896dde58261cc40cd10a688e8caf64c4c6a1b4983e532bc8`.
- Authenticated Chrome rendered the deployed v43 page and the Copernicus EMS card: 268 unique activations, 90 flood activations, and zero AOI/product intersections across the 16 fixed study areas.
- A fresh unauthenticated `curl -I -L` request returned HTTP **401**, consistent with the owner-only Site policy.

## Production walkthrough results

| Workflow | Result | Observed behavior |
|---|---|---|
| Load the Site | Pass | ATLAS v43 rendered in the authenticated owner session. |
| Review the 8+8 candidate frame | Pass | All 16 profiles are present: 8 U.S. and 8 international. Each selected profile exposes public evidence, value question/dimensions, validation path, evidence limit, and primary evidence link. All 16 were selected in turn and checked. |
| Change demonstration scenario | Pass | Baton Rouge selection changed the historical event to Hurricane Ida, updated the portfolio/event date and displayed a synthetic-fixture notice. |
| Compare methods | Pass | Quality-aware aggregate changed the illustrative median overlap from 7.7% to 6.8%, changed the elevated count from 4 to 3, updated the ranking, and disclosed the experimental three-observation fixture method. |
| Inspect asset detail | Pass | Selecting Southeast Water Plant displayed its LA-002 identity, 18.9% illustrative observed overlap, 93% valid fixture coverage, and uncalibrated confidence. |
| Reset analysis | Pass | Reset restored the single-observation baseline and default asset while retaining the selected Baton Rouge/Hurricane Ida scenario. |
| Export evidence | Pass | Chrome reported a completed 3.2 KB `atlas-baton-ida-single-fixture.csv` download and the page confirmed the scenario, observation windows, method, and synthetic-data label are included. |
| Inspect live CEMS AOI screen | Pass | The card states 268 activations, 90 floods, 0/16 fixed-area overlaps, and links to the official API guide and exact audit download. |

## Automated verification

The full hash-locked Python 3.12 Bookworm suite passed **138 tests in 72.90 seconds** on the current worktree. The run installed `requirements-dev.lock` and `requirements-reference-audit.lock` with `--require-hashes`, then ran `python -m pytest -q`. A fresh `git diff --check` passed after the documentation updates. This is author-run validation of the current worktree, not an independent clean-checkout reproduction.

## Limits and score

The deployed analysis demonstration remains synthetic; its overlap, coverage, and confidence values are not measured historical outcomes. The 8+8 locations are candidate areas with a common proposed protocol, not enrolled confirmatory sites. The latest reference-readiness result remains **0/16 confirmatory-eligible**. Copernicus EMS yielded no intersecting AOIs/products and no independent labels. This Site walkthrough does not verify four-cloud deployment, native Apple distribution, field validation, usability study acceptance, or independent reproduction.

Canonical provisional score remains **60/100** under the published 5-point-per-criterion scorecard. Passing a deployment walkthrough does not substantiate the unmet scientific, scale, usability-study, cloud, or independent-reproduction criteria. A 100/100 claim is not supported by this run.
