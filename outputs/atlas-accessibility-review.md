# ATLAS focused accessibility review

**Date:** 2026-11-02\
**Reviewed:** private deployed version 7\
**Scope:** focused WCAG 2.1 AA checks for the interactive candidate-area panel and primary walkthrough controls. This is an author-run review, not a conformance certification.

## Findings and changes

| Check | Finding | Change / result |
|---|---|---|
| Text contrast (1.4.3) | Muted labels on white measured 3.06–4.13:1 in representative checks, below 4.5:1 for normal text. | Darkened secondary labels. Post-change representative ratios: 5.87:1 on white; 5.44:1 on light method panel; 5.04:1 warning text on its background. |
| Keyboard operation (2.1.1) | Needed live verification of the new study-area controls. | Tab reached scenario, event, reset, evidence export, register export, then the area choices. Enter selected Miami and updated the profile. |
| Focus visibility (2.4.7) | New controls needed a reliable focus treatment. | Added a visible 3 px outline for area choices, buttons, method tabs, and selects. |
| Target size (2.5.5) | Candidate list buttons were under the 44 px target. | Set study-area choices, primary buttons, tabs, and selects to a 44 px minimum height. |
| Names and labels (1.3.1, 4.1.2) | Candidate choices and details needed clear programmatic context. | Area-choice container has an accessible label; each choice exposes its selected state; details use a polite live region; scenario selectors retain explicit labels; map has descriptive alternative text. |

## Limits

Screen-reader operation with VoiceOver/NVDA, 200% zoom, exhaustive color-pair review, and task-based usability testing were not completed. These gaps keep this score partial.
