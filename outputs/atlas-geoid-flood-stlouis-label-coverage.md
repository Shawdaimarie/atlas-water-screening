# GEOID-Flood St. Louis label coverage audit

**Run:** 2026-11-04

Inspected the 12 pinned GEOID-Flood label chips whose catalog footprints intersect the fixed 25 × 25 km St. Louis AOI. Inside the AOI, 4,851,977/6,244,762 10 m pixels have mapped labels (77.70%); 1,392,785 pixels are class 255/outside the mapped label area. Class counts are `{"0": 4507775, "1": 317922, "2": 26280, "255": 1392785}`.

This is EMSR203 (2017-04-28), in the GEOID-Flood **training** split. The result distinguishes label-pixel coverage from catalog tile-footprint coverage. It is historical diagnostic evidence only: it is outside the shared 2024–2026 window, has not been independently adjudicated, and adds no score or enrollment.

The audit pins and verifies the 703,922-byte metadata catalog and 74,137,600-byte label shard by SHA-256, extracts only the 12 relevant TIFFs in memory, and counts classes within the registered AOI geometry. See [machine-readable result](atlas-geoid-flood-stlouis-label-coverage.json).
