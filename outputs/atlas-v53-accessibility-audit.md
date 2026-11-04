# ATLAS v53 accessibility and production walkthrough record

Date: 2026-11-04. Site: `https://atlas-water-screening.shawdaimarie.chatgpt.site/` (owner-only). Version: v53. Source commit: `9aeb51500c0c3d9c330b7d95f18560260aa44ddb`. Deployment: `appgdep_6aeade16fc7481918dbebe524ee86c6b`. Status: succeeded.

## Scope and changes

Focused author-run checks covered keyboard interaction and selected WCAG 2.1 AA text contrast pairs on the deployed study-area selector and candidate profile. The earlier production check found that choosing an area caused the selector to rerender and moved keyboard focus to the page root. v52 added focus restoration to the selected study-area control. v53 corrected three text colors identified below 4.5:1: warning pill (4.36:1 to about 5.05:1), profile detail heading text (4.35:1 to about 6.05:1), and small raster-table row labels (3.82:1 to about 5.87:1). The accessible visible focus treatment and minimum interactive control height were already present.

## Verification evidence

- Hash-locked full Python 3.12 suite: **145 passed in 1.46 seconds** (release recheck).
- Node 22 syntax check of the deployed inline script: passed.
- `git diff --check`: passed.
- Production keyboard replay on v53: the existing study controls and area list were keyboard reachable; Space selected Miami, updated the profile from Houston to Miami, and the focused control remained the Miami checkbox after the rerender.
- Production visual replay: the deployed page rendered the candidate-area matrix and the Miami rationale, value-integration question, evidence limits, and validation path. The owner-only browser tab is left open for the walkthrough.
- Deployment operation returned succeeded for v53 at the existing production URL; no audience change was requested or made.

## Limits and score treatment

This is a focused author-run audit, not a full WCAG conformance claim or a task-based usability study. Screen-reader testing (including VoiceOver/NVDA), 200% zoom/reflow, exhaustive contrast coverage, and independent user tasks remain unverified. The accessibility correction does not satisfy the rubric's usability study criterion and adds no points. The score remains **60/100 provisional** and confirmatory eligibility **0/16**; see `SCORECARD.md` for the independent evidence still required. This Site release is browser-hosted and does not constitute an Apple-platform release; the existing Apple Account applies to a future app distribution path.
