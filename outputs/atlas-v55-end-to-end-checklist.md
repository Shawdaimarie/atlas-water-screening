# ATLAS v55 production research-evidence release

**Date:** 2026-11-04  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Site version:** 55  
**Source commit:** `0a71b8a6be98a8980906ab2b4a08e0634e2fffbe`  
**Deployment:** `appgdep_6aeae665e2dc8191ba1288491e6959b2` — succeeded  
**Audience:** owner-only; `shawdaimarie@gmail.com`; zero external visitors.

## Research update

- Added the New Orleans June 2026 NASA EGIS OPERA DSWx-S1 BWTR item audit to the reference evidence panel.
- The exact catalog item footprint contains the registered New Orleans AOI centre. A raster locked to item 22 was exported over the fixed box at approximately 30 m on an EPSG:3857 grid.
- The returned 963 × 963 TIFF contains 927,369 cells, all class 255 (no data); valid BWTR 0/1 fraction is 0%. A centre-point identify request independently returned `NoData` for the same locked raster.
- The result shows catalog-footprint coverage cannot substitute for pixel coverage. It is not interpreted as dry land. NASA marks the rapid-response product preliminary and unvalidated; the interval in the item name does not establish per-pixel event-time matching. No accuracy or event-change estimate was calculated.

## Verification

| Check | Result | Evidence |
|---|---|---|
| Full project test suite | **153 passed** | `.venv/bin/python -m pytest -q`; 1 existing LibreSSL/urllib3 environment warning. |
| Live EGIS retrieval | **Completed** | Export metadata and GeoTIFF were read; all class counts, 30 m approximate grid, CRS, and SHA-256 are in `outputs/atlas-neworleans-2026-egis-bwtr-coverage.json`. |
| Production deployment | **Passed** | Sites reported the owner-private v55 deployment succeeded at the existing URL. |
| Production evidence card | **Passed** | Reloaded authenticated production tab and confirmed the New Orleans card's 0/927,369 coverage statement and record, JSON, and City event links. Screenshot captured with the three evidence cards in view. |
| Access policy | **Passed** | Sites readback immediately before publishing confirmed custom owner-only access and zero external visitors; deployment operation preserved the existing policy. |

## Research and score limits

The project remains a 16-candidate evidence-development program. This one response product is not suitable as independent truth and its no-data result does not validate or disprove flooding. Confirmatory eligibility remains **0/16**, and the canonical score remains **60/100 provisional**. The web Site uses synthetic values in its demo analysis and is still not an Apple app or a deployment to Google Cloud, AWS, Azure, or Oracle Cloud.

Artifacts: `outputs/atlas-neworleans-2026-egis-bwtr-coverage.json`, `outputs/atlas-neworleans-2026-egis-bwtr-coverage.md`, and `outputs/atlas-v54-end-to-end-checklist.md`.
