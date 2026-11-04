# WorldFloods v2 footprint screen

**Result: no footprint candidates in the 16 fixed ATLAS study areas.** The reproducible audit parsed all 509 metadata records in the published WorldFloods v2 `metadatas.zip`; no record bounding box intersected any of the 8 U.S. and 8 international 25 × 25 km AOIs.

- Metadata archive SHA-256: `f48d961a1bd52dbcd0aac53e93c144cac1937df68c823cb1d51b7feefc626a00`
- Dataset DOI: [10.5281/zenodo.8153514](https://zenodo.org/records/8153514)
- Published map period: 2016–2023, before the OPERA DSWx-S1 study window used by ATLAS.
- The metadata zip was screened; the 1.2 GB mask archive was not downloaded or inspected.

This is a source-coverage screen, not a finding that floods or other reference data are absent from these cities. The source labels are manually curated from flood maps; their lineage and non-commercial reuse terms would need review before considering a geographic match for validation.

Run `python scripts/audit_worldfloods_v2_coverage.py --metadata-zip <path-to-metadatas.zip>` to reproduce. See [`atlas-worldfloods-v2-aoi-coverage-audit.json`](atlas-worldfloods-v2-aoi-coverage-audit.json) and [`tests/test_worldfloods_v2_coverage.py`](../tests/test_worldfloods_v2_coverage.py).
