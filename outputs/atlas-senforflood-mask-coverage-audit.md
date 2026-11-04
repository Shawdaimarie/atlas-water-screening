# SenForFlood mask coverage screen across the 16 ATLAS study areas

**Run date:** 2026-11-04  
**Result:** source discovery only; no new confirmatory reference labels.

## Scope and reproducibility

The audit read the Hugging Face repository tree at pinned revision `aa33be10fffbd3a82370fdd91327d8545107b43f`, retrieved all **4,023** listed flood-mask GeoTIFFs (**27,681,760 bytes**), verified each retrieved file's listed size, computed SHA-256 for every file, and opened all rasters. It excluded **177** AppleDouble `._` sidecar files. The machine-readable report records the pinned revision, each mask's path and SHA-256, repository OID, size, and the per-area results.

The same fixed WGS84 bounding boxes in the ATLAS 8+8 study-area register were checked against every mask-chip footprint. Raster bounds were transformed to WGS84; actual AOI pixels and mask classes were examined for any intersecting chip. The dataset record identifies version 2 and a CC BY-SA 4.0 license. No mask rasters are copied into this project.

## Findings

- The screen covered **8 U.S. and 8 international areas**.
- **0 of 4,023** mask chips intersected any registered AOI; consequently **0/16 areas** had SenForFlood mask-chip coverage in this repository snapshot.
- The screen adds **0** independently labeled areas and **0** confirmatory enrollments.
- The dataset includes both CEMS and DFO samples. Its documentation describes DFO masks as automatic change-detection outputs; these are not independent truth for ATLAS. CEMS masks are analyst-created, but an analyst-created label still needs event-time, image-lineage, provenance, spatial-adequacy, and license review before it could support an independent reference assessment.

The published dataset description reports 353 flood events, while the Hugging Face repository describes its upload as in progress. This screen therefore states only what was present at the pinned repository revision; it does not claim to have exhausted the full Dataverse dataset. The source dataset and the paper are available from the [Hugging Face dataset repository](https://huggingface.co/datasets/matosak/SenForFlood), its [Harvard Dataverse record](https://doi.org/10.7910/DVN/ZQCODX), and the [ISPRS paper](https://doi.org/10.5194/isprs-archives-XLVIII-M-7-2025-97-2025).

## Interpretation

This negative overlap result is a coverage finding for one pinned repository snapshot. It does not show that floods did not occur in any city, and it does not qualify or disqualify another reference source. SenForFlood masks are not used as independent validation labels here. The existing confirmatory status remains **0/16**, and the canonical score remains **60/100 provisional**.

Reproduce with `python scripts/audit_senforflood_mask_coverage.py`. The downloaded mask cache is local under ignored `work/`; only the checksum and coverage audit is retained in `atlas-senforflood-mask-coverage-audit.json`.
