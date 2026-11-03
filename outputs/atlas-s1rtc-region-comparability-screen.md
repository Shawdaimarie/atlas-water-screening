# Sentinel-1 RTC regional coverage comparability screen

**Purpose:** quantify whether the equal-count 12-group-per-area spatial availability sample has comparable valid-pixel coverage across the fixed 8+8 candidate frame. This is an availability diagnostic, not flood classification, reference truth, or inferential evidence.

## Result

| Stratum | Areas | Groups passing ≥80% valid VV pixels | Areas passing all 12 groups | Areas not passing all 12 |
|---|---:|---:|---:|---:|
| United States | 8 | 78/96 (81.25%) | 3/8 | 5/8 |
| International | 8 | 91/96 (94.79%) | 7/8 | 1/8 |

| **Total** | **16** | **169/192** | **10/16** | **6/16** |

Both strata have three sampled groups per area per quarter across 2025 (12 unique groups per area). In this deterministic sample, 3/8 U.S. sites and 7/8 international sites meet the all-12 spatial screen. The aggregate group pass rates differ by 13.54 percentage points. The sample is not designed to estimate a regional population difference; the imbalance is a diagnostic that current observational completeness is not comparable at the 80% screen.

## Per-area counts

| Stratum | Area | Passing sampled groups | All-12 result |
|---|---|---:|---|
| United States | Houston | 10/12 | Does not pass |
| United States | Miami | 12/12 | Pass |
| United States | Tampa | 6/12 | Does not pass |
| United States | New Orleans | 12/12 | Pass |
| United States | New York City | 9/12 | Does not pass |
| United States | Sacramento | 10/12 | Does not pass |
| United States | Atlanta | 12/12 | Pass |
| United States | St. Louis | 7/12 | Does not pass |
| International | Jakarta | 12/12 | Pass |
| International | Singapore | 12/12 | Pass |
| International | Dubai | 12/12 | Pass |
| International | Mumbai | 12/12 | Pass |
| International | Bangkok | 12/12 | Pass |
| International | Tokyo | 12/12 | Pass |
| International | Manila | 12/12 | Pass |
| International | São Paulo | 7/12 | Does not pass |

## Interpretation and next gate

The source is Sentinel-1 RTC VV at 10 m. A pass means a sufficient fraction of raster pixels is finite and not source-declared nodata. It does not verify OPERA BWTR classes, event attribution, baseline matching, reference-label independence, spatial sampling adequacy, or precision. The source and processed product also share Sentinel-1 lineage, so this audit cannot serve as independent truth.

Keep the 16 AOIs fixed while checking additional predeclared dates and event windows. Before confirmatory use, require the same number of QA-valid event and baseline observations across sites, at least three per period, independent licensed labels, and probability samples that meet the protocol precision target. If a location cannot meet that common support, report the gap and retain its candidate status rather than imputing or silently changing its footprint.

## Supplemental matched spatial-availability quota (2026-11-03)

To evaluate whether the six incomplete areas had other usable dates in the same fixed area-quarter candidate pool, a predeclared deterministic random-without-replacement screen retained passing groups from the initial draw, then screened additional groups only when needed to reach three ≥80%-valid groups per quarter. Rejected initial picks were not re-used. Selection depended only on the finite/non-nodata VV pixel fraction. All 16 areas reached the same quota: **192/192 selected groups** passed, with 12 distinct groups per area and 3 per quarter. The screen examined 34 additional groups: 23 passed and filled the shortfall; 11 failed the threshold. The initial unconditional unique-group draw remains separately preserved at 169/192 groups and 10/16 areas passing all 12.

| Area | Initial passing groups | Additional groups screened (pass/fail) | Final matched quota |
|---|---:|---:|---:|
| Houston | 10/12 | 2 (2/0) | 12/12 |
| Miami | 12/12 | 0 (0/0) | 12/12 |
| Tampa | 6/12 | 9 (6/3) | 12/12 |
| New Orleans | 12/12 | 0 (0/0) | 12/12 |
| New York City | 9/12 | 6 (3/3) | 12/12 |
| Sacramento | 10/12 | 3 (2/1) | 12/12 |
| Atlanta | 12/12 | 0 (0/0) | 12/12 |
| St. Louis | 7/12 | 7 (5/2) | 12/12 |
| Jakarta | 12/12 | 0 (0/0) | 12/12 |
| Singapore | 12/12 | 0 (0/0) | 12/12 |
| Dubai | 12/12 | 0 (0/0) | 12/12 |
| Mumbai | 12/12 | 0 (0/0) | 12/12 |
| Bangkok | 12/12 | 0 (0/0) | 12/12 |
| Tokyo | 12/12 | 0 (0/0) | 12/12 |
| Manila | 12/12 | 0 (0/0) | 12/12 |
| São Paulo | 7/12 | 7 (5/2) | 12/12 |

This resolves the **RTC spatial-coverage quota** for the fixed 2025 sample, not observational comparability for flood research. The accepted RTC groups do not prove OPERA DSWx-S1 scene availability, event/baseline timing, water-class validity, independent reference coverage, or statistical representativeness. The coverage-conditioned quota is not an unconditional estimate of archive-wide usability, and does not change the 0/16 confirmatory enrollment count or canonical score. The full attempt-level record is in [`atlas-s1rtc-valid-quota-audit.json`](atlas-s1rtc-valid-quota-audit.json), generated by [`audit_s1rtc_valid_quota.py`](../scripts/audit_s1rtc_valid_quota.py); the separate initial draw is retained in [`atlas-s1rtc-pixel-coverage-unique-audit.json`](atlas-s1rtc-pixel-coverage-unique-audit.json).

## Reproducibility

Input: [`atlas-s1rtc-pixel-coverage-combined-audit.json`](atlas-s1rtc-pixel-coverage-combined-audit.json). The audit contains 192 unique sampled area/orbit groups (12 per area) and the per-scene pixel-availability flags. The source audit does not establish valid OPERA observation counts.
