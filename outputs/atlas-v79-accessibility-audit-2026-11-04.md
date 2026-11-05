# ATLAS v79 live accessibility review

**Date:** 2026-11-04  
**Environment:** Private production Site v79, owner session  
**URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Scope:** Focused manual keyboard and accessibility-tree review, plus review of the repository's static accessibility checks. This is not a complete WCAG audit or user study.

## Observed results

- The page exposed a named `main` landmark and a “Skip to main content” link in the browser accessibility tree.
- Keyboard traversal reached the skip link, the study-area and historical-event controls, reset and export actions, register and evidence links, and candidate-area checkboxes.
- The browser reported the controls by accessible role/name. A screenshot showed a visible focus outline on “Export evidence.”
- With keyboard focus on the Jakarta checkbox, Space selected Jakarta. The accessible tree changed to the Jakarta evidence profile, including its public rationale, value dimensions, validation path, and limitations. No scenario fixture values were represented as Jakarta results.
- The browser was returned to the Houston profile after the interaction.
- The current visible top-level page fit the inspected 1280 × 720 viewport without horizontal clipping in the captured view. This is a limited visual check, not a measurement of the whole page at other widths or zoom levels.
- Repository checks in `tests/test_site_accessibility.py` cover selected status-text contrast pairs, selected text and map-label contrast, control boundary contrast, a skip link/main landmark, and minimum link/button target styles. These are targeted source assertions, not a complete automated accessibility scan.
- The five targeted checks in `tests/test_site_accessibility.py` passed in the current worktree (`5 passed`).

## Not established

- This review does not establish WCAG 2.1 AA conformance. It did not test 200% browser zoom, all page regions and interactive states, VoiceOver or another screen reader, voice control, reduced motion, high-contrast modes, or full keyboard operation of every disclosure and download.
- No participant task study or assistive-technology acceptance study has been conducted. The Usability rubric remains **0/10**.
- The earlier v76 320 × 844 CSS-pixel responsive check is supporting historical evidence, not a substitute for a v79 full-page responsive and zoom audit.

## Apple account release status

The current deployment is a private web Site. Repository inspection found no `.xcodeproj`, `.xcworkspace`, Swift package, or iOS app target. The existing Apple Account is the intended publisher identity for a future Apple-platform release, but Apple Developer Program/App Store Connect access is unverified and this account does not deploy the current web Site or any of the four cloud environments. No iOS build, signing, TestFlight upload, or device install was performed. See `outputs/atlas-apple-distribution-readiness.md`.

## Disposition

Focused keyboard checks passed for the controls and Jakarta profile interaction described above. Full accessibility acceptance and user testing remain open; no usability points are awarded from this partial review. The current research score remains **60/100 provisional**.
