# ATLAS validation protocol for the 16 candidate study areas

**Protocol state: proposed; not externally preregistered.** Freeze a dated copy in a public or institutionally controlled registry before examining candidate-area OPERA outcomes or reference labels. Any change after that point must be versioned with a dated rationale. No area currently satisfies the confirmatory enrollment gates; this protocol defines the evidence needed to change that status.

## Objectives and inference limits

The study will assess (1) availability of QA-valid satellite observations, (2) classification of surface water, (3) event-period inundation relative to a matched non-event baseline, and (4) overlap of mapped water with licensed, dated infrastructure and service data. These are separate estimands. A product water class is not by itself flood truth; overlap is not damage, service interruption, or monetary loss. Value integration will preserve separate measures for hazard, exposure, service criticality, population served, distributional coverage, and decision usefulness. No composite social-value score will be calculated without locally approved weights and sensitivity analysis.

The 16 sites are purposively selected, eight in the United States and eight internationally. They are not a probability sample of cities, so results support comparisons among enrolled sites only and do not estimate national or global city prevalence. Sites may enter the confirmatory analysis only when they meet the same data, reference, sampling, and precision gates. If fewer than 8+8 qualify, report the enrolled subset as exploratory and do not describe the cross-region comparison as complete.

## Fixed measurement contract

- Use OPERA DSWx-S1 V1 at its documented 30 m grid and the binary water fraction raster (BWTR) for primary surface-water mapping. Interpret BWTR `0` and `1` as valid non-water and water classifications only where the product specification marks the observation valid. HAND-masked `250`, layover/shadow `251`, fill, and other no-data are missing observations, never dry land. Report product version, granule identifiers, acquisition time, processing metadata, grid alignment, mask classes, and valid-pixel fraction for every area/date.
- Use each candidate's fixed 25 × 25 km screening footprint (625 km² nominal), with a frozen equal-area projection/grid and the exact boundary file hash in the analysis manifest. Do not change boundaries after seeing mapped water. Report boundary clipping and pixel counts.
- Distinguish mapped surface water, persistent water, and event-associated inundation. An event inundation label must be supported by independent temporal/reference evidence; subtracting a single baseline classification alone does not establish floodwater.
- Report observation availability (valid area fraction and dates), water-map agreement, event-versus-baseline change, and asset/service overlap as separate results. Missing or ambiguous cells remain missing and are included in coverage accounting.

NASA's OPERA catalog/specification documents the BWTR classes and invalid masks, as well as the product-level validation requirement. That product requirement is not an ATLAS sample-size or AOI coverage rule. See the [OPERA DSWx-S1 Earth Engine catalog](https://developers.google.com/earth-engine/datasets/catalog/OPERA_DSWX_L3_V1_S1) and [OPERA validation plan](https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_Validation_Plan.pdf).

## Candidate discovery and event enrollment

The prior 90-date metadata threshold is discovery bookkeeping only. It is not a site-enrollment, observation-adequacy, or statistical-power criterion. The three-date and 80%-valid-per-scene floors are feasibility checks only; show results below those floors as unavailable, and never describe passing them as statistically adequate.

Before opening candidate-area OPERA water outputs, identify qualifying flood events from independent, dated official event products, gauge/agency records, or independently mapped references. Archive the query, inclusion list, exclusions, event st