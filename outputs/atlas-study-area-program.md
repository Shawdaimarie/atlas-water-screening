# ATLAS candidate study-area program

Prepared 2026-11-02. This is an evidence-based candidate register and archive discovery screen, not a claim that 16 sites have completed observation validation.

## Selection principles

1. **Research fit:** urban surface-water exposure intersects critical infrastructure, flood-management decisions, or integrated water planning. Technology-hub status helps diversify operating contexts; it is not itself evidence of hydrologic need.
2. **Verifiable need:** prioritize official plans, funded flood programs, hydrologic observations, and peer-reviewed or public-sector research. These establish public research/management need, not ATLAS customer demand.
3. **Comparable discoverability:** screen the same NASA OPERA DSWx-S1 V1 collection and temporal window in equal nominal 25 × 25 km city-center boxes (~625 km²). CMR granule counts are metadata-discovery counts, not observations passing QA.
4. **Candidate discovery completeness:** record all pages and distinct dates returned by the same product and date-window query. The prior 90-date cutoff is descriptive only; it is not an enrollment criterion and does not establish observations that pass QA.
5. **Balanced feasibility screen:** use the common analytical footprint and product definitions. The existing ≥80% valid-pixel rule and three dates per period are preliminary feasibility floors only; they are not evidence of statistical sample adequacy. Confirmatory enrollment additionally requires independently referenced event coverage and the area-weighted probability-sample precision gate in `outputs/atlas-preregistered-validation-protocol.md`. If an area fails, defer it or replace it before analysis. Product-class signals are not ground truth.
6. **Value integration:** report observed water overlap separately from consequence. Add service criticality, population served, vulnerable communities, and local management priorities only where licensed, attributable datasets and community/agency review support them; do not turn exposure into damage or financial-loss claims.

## Operational selection criteria and evidence interpretation

All 16 areas were selected as a purposive, stratified set rather than ranked by a single composite score. To retain a candidate, the study team required: (1) urban surface-water flood mechanisms relevant to infrastructure and service decisions; (2) a location-specific public-sector, scientific, or multilateral record showing a current management or research need; (3) an open or obtainable path to independent event references; and (4) discoverable OPERA DSWx-S1 V1 metadata in the same 25 × 25 km city-centre screening footprint and time window. The international set intentionally includes Jakarta, Singapore, Dubai, Mumbai, Bangkok, Tokyo, and Manila as major technology and economic hubs with documented water-management programs; hub status is context, never a substitute for flood evidence.

The evidence register records the evidence class, an attributable empirical fact or program measure, a common value-integration frame, a proposed independent validation path, and a scope limitation for every location. Project cost, pump capacity, sensor count, or target population establishes public management activity or research need; none is evidence of ATLAS buyer demand, purchase intent, endorsement, realized benefit, or reduced flood loss. The available sources do not establish market demand. Customer demand needs separate interviews, procurement records, or other direct market evidence.

## Independent reference-data lead

NASA/JPL's OPERA DSWx-S1 CalVal Database V1 is a candidate source of reference classifications. The anonymous CMR record reports one ZIP granule (~181.6 MB) covering September 2021 and links it to a `podaac-ops-cumulus-protected` object; NASA's data-access documentation requires an Earthdata Login account to download/stream DAAC files. The database's global metadata envelope includes the candidate cities, but no per-city label coverage, provenance, dates, or licensing has been verified. See the [reference-data access audit](atlas-independent-reference-data-plan.md). Treat this as a lead only until the package is retrieved and its reference sources are audited; it adds no validation result.

## High-principle value integration

The analysis follows a five-step public-value chain and keeps each quantity separate:

1. **Hazard observation:** report the source product class, acquisition time, valid-pixel fraction, and uncertainty. The satellite result is an observation of surface-water class, not ground truth.
2. **Asset exposure:** intersect only documented, dated, attributable asset footprints; report overlap and geometry/data completeness. Do not infer damage or service failure from overlap.
3. **Service consequence:** add service criticality, population served, and dependency only from licensed, attributable data and review with the responsible agency or community partner. Treat unknown values as unknown.
4. **Distributional equity:** report who and what is represented in the reference data; assess coverage and missingness by neighborhood and population group only where lawful, privacy-preserving, and locally governed.
5. **Decision usefulness:** compare evidence with documented agency priorities and ask whether it changes an operational or investment decision. Do not create a weighted social-value score without declared stakeholder-approved weights and sensitivity analysis.

Every candidate follows the same screening contract: fixed 625 km² nominal footprint; same product/version/time window; disclose every acquisition date and valid-pixel fraction; retain source/processing provenance; and do not impute missing observations. The ≥80% per-scene floor and three dates per event/baseline period permit only a feasibility screen. Confirmatory site enrollment requires the same number of matched observations across sites, independent event labels, and adequate effective sample size for the predeclared confidence-interval target. No registered area has passed pixel-level QA or the independent-label gate; current cross-area observational coverage is not comparable and no event effect is estimated. See the [preregistered validation protocol](atlas-preregistered-validation-protocol.md).

## Candidate coverage

Common window: 2024-09-01T00:00:00Z to 2026-11-02T23:59:59Z. Collection: OPERA_L3_DSWX-S1_V1. The number of distinct acquisition dates ranges from 99 to 403 (median 165). The reproducible date-set intersection audit found **zero exact acquisition dates common to all 16 areas**; all 16 have at least one archive metadata date in **24 of the 26 year-month periods** represented across the candidates. This supports event-relative sampling with matched counts, not same-date comparisons. The 90-date cutoff formerly used in the discovery screen is now explicitly descriptive and does not qualify sites for enrollment. Equal AOI size, metadata counts, and the preliminary 80%/three-scene floor do not establish adequate valid-pixel observations or statistical power. Raw date sets and the audit are in `data/study_area_register.json` and `outputs/atlas-temporal-overlap-audit.json`; reproduce with `python3 scripts/screen_study_areas.py` then `python3 scripts/audit_temporal_overlap.py`.

| Region | Candidate | CMR granule metadata hits | Distinct acquisition dates | Rationale / primary evidence |
|---|---|---:|---:|---|
| United States | Houston | 446 | 126 | Gulf coastal compound rainfall, river, and surge flooding; critical infrastructure exposure is well documented. [source](https://prod-01-asg-toolkit-climate.woc.noaa.gov/action-plan/resilient-houston) |
| United States | Miami | 131 | 112 | Coastal rainfall flooding interacts with groundwater table, high tides, and sea-level rise; NOAA-supported research targets prediction and risk management. [source](https://coastalscience.noaa.gov/news/new-model-enables-rapid-flood-prediction-in-miami-to-support-risk-management/) |
| United States | Tampa | 261 | 106 | USGS documented widespread Milton flooding in its Tampa coverage area, major-stage rivers, and field measurements/gage repairs. [source](https://water.usgs.gov/alerts/item_2024-10-11_20%3A05%3A00.html) |
| United States | New Orleans | 535 | 165 | Low elevation, levees, pumps, and a large catch-basin network create a documented urban rainfall-flood management problem. [source](https://marinedebris.noaa.gov/removal/preventing-pervasive-floating-litter-new-orleans-storm-drains) |
| United States | New York City | 922 | 238 | NOAA-hosted research maps present/future flood adaptation areas; infrastructure and power-system exposure are documented. [source](https://repository.library.noaa.gov/view/noaa/77144) |
| United States | Sacramento | 472 | 258 | The Sacramento region relies on levees along major rivers; USGS maintains streamgages and studies flood processes in California’s Central Valley. [source](https://www.usgs.gov/centers/california-water-science-center/science/science-topics/floods) |
| United States | Atlanta | 241 | 99 | The City’s 2025 comprehensive plan calls for stormwater management and flooding mitigation, including capital and watershed actions. [source](https://www.atlantaga.gov/home/showpublisheddocument/66053/638884420075030000) |
| United States | St. Louis | 232 | 101 | NOAA/NWS river gauge documentation defines flood stages and describes levee/floodwall impacts along the Mississippi. [source](https://water.noaa.gov/gauges/eadm7) |
| International | Jakarta | 779 | 249 | Greater Jakarta faces regular widespread flooding alongside water-supply deficits and water-quality challenges; the World Bank calls for integrated urban water management. [source](https://www.worldbank.org/en/topic/water/publication/pathways-to-integrated-urban-water-management-for-greater-jakarta) |
| International | Singapore | 231 | 163 | PUB documents flash/coastal flood risks, investments in drainage, a national flood-resilience program, and extensive sensor monitoring. [source](https://www.pub.gov.sg/Public/KeyInitiatives/Flood-Resilience) |
| International | Dubai | 1009 | 381 | Dubai Municipality’s AED 30bn Tasreef program expands stormwater collection and drainage; contracts cover critical urban areas. [source](https://www.dm.gov.ae/aed-1-439-billion-contracts-awarded-for-four-tasreef-project-phases/) |
| International | Mumbai | 361 | 121 | India approved an urban flood risk mitigation program that includes Mumbai; city planning and IFLOWS document substantial flood research and warning needs. [source](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2297625&lang=1&reg=3) |
| International | Bangkok | 170 | 127 | World Bank city-region analysis documents interacting upstream runoff, intense local rainfall, and tidal effects. [source](https://documents1.worldbank.org/curated/en/834261468025503285/pdf/508980ESW0v10P1pt1bangkok1report111.pdf) |
| International | Tokyo | 258 | 202 | World Bank work documents Tokyo-region urban flood risk management practice and the need to integrate risk into urban planning and investment. [source](https://www.worldbank.org/en/programs/tokyo-development-learning-center/tdd/tdd_on_urban_flood_management) |
| International | Manila | 1166 | 403 | World Bank-supported Metro Manila Flood Management Project targets 17 cities/municipalities and more than one million people with pump/drainage upgrades. [source](https://www.worldbank.org/ext/en/topic/water/water-for-planet) |
| International | São Paulo | 530 | 196 | World Bank case material documents urban flood exposure, drainage constraints, and the need to combine structural and nonstructural measures. [source](https://documents1.worldbank.org/curated/en/659161468182066104/pdf/709820PUB0EPI0067926B09780821389621.pdf) |

## Area-specific research design

## Repeated Sentinel-1 RTC availability sample (exploratory)

Two separately seeded uniform orbit-group draws were measured using the same 10 m VV finite/non-nodata rule for every AOI and calendar quarter of 2025. Together they cover 128 area/quarter selections, of which 121 are unique area/orbit groups because seven groups were selected in both draws. Of those 121 unique groups, 102 (84.3%) met the 80% spatial-coverage floor. Ten of 16 areas met the floor in all eight selected groups across both draws. The first draw passed 56/64 groups and all quarters in 12/16 areas; the second passed 53/64 and all eight groups in 10/16 areas.

Six areas had at least one selected low-coverage group across the two draws: Houston (9.1% in draw B Q4), Tampa (77.8% in draw B Q1/Q3/Q4), New York City (3.2% in draw B Q3), Sacramento (0.0% in draw B Q2; 60.6% in Q4), St. Louis (26.1% in draw B Q2; 25.6% in draw B Q3), and São Paulo (0.1% in draw B Q3; 0.0% in Q4). These results indicate uneven acquisition-footprint availability for the sampled orbit groups; they do not establish that the remaining groups pass, and selected samples are not event/baseline observations.

Both data draws and the deduplicated 121-group summary are in `outputs/atlas-s1rtc-pixel-coverage-combined-audit.json`; run-specific item provenance is retained in `outputs/atlas-s1rtc-pixel-coverage-audit.json` and `outputs/atlas-s1rtc-pixel-coverage-replicate-2.json`. The replicate uses the same full-year 2025 Planetary Computer Sentinel-1 RTC collection, fixed AOIs, projection/window calculation, 80% floor, nodata checks, and per-area/per-quarter randomization rule with a distinct fixed seed. The report does not infer water, assert OPERA classification accuracy, or treat the 128 selections as independent experiments.

### United States — Houston

Gulf coastal compound rainfall, river, and surge flooding; critical infrastructure exposure is well documented.

**Integration question:** Use as a high-hazard coastal baseline and test how observed-water overlap aligns with infrastructure and watershed planning.

**Standardized archive screen:** 446 granule metadata hits; 126 distinct acquisition dates (2024-09-04–2026-10-24) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://prod-01-asg-toolkit-climate.woc.noaa.gov/action-plan/resilient-houston)

### United States — Miami

Coastal rainfall flooding interacts with groundwater table, high tides, and sea-level rise; NOAA-supported research targets prediction and risk management.

**Integration question:** Test a shallow-groundwater coastal setting and compare satellite water signals with documented local flood evidence.

**Standardized archive screen:** 131 granule metadata hits; 112 distinct acquisition dates (2024-09-04–2026-10-24) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://coastalscience.noaa.gov/news/new-model-enables-rapid-flood-prediction-in-miami-to-support-risk-management/)

### United States — Tampa

USGS documented widespread Milton flooding in its Tampa coverage area, major-stage rivers, and field measurements/gage repairs.

**Integration question:** Test an event with independent hydrologic measurements and coastal/river flood context.

**Standardized archive screen:** 261 granule metadata hits; 106 distinct acquisition dates (2024-09-02–2026-10-24) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://water.usgs.gov/alerts/item_2024-10-11_20%3A05%3A00.html)

### United States — New Orleans

Low elevation, levees, pumps, and a large catch-basin network create a documented urban rainfall-flood management problem.

**Integration question:** Test satellite screening in a pump-dependent, leveed urban drainage environment.

**Standardized archive screen:** 535 granule metadata hits; 165 distinct acquisition dates (2024-09-06–2026-10-27) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://marinedebris.noaa.gov/removal/preventing-pervasive-floating-litter-new-orleans-storm-drains)

### United States — New York City

NOAA-hosted research maps present/future flood adaptation areas; infrastructure and power-system exposure are documented.

**Integration question:** Test dense coastal infrastructure and compare pluvial/coastal water exposure across an urban asset portfolio.

**Standardized archive screen:** 922 granule metadata hits; 238 distinct acquisition dates (2024-09-01–2026-10-24) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://repository.library.noaa.gov/view/noaa/77144)

### United States — Sacramento

The Sacramento region relies on levees along major rivers; USGS maintains streamgages and studies flood processes in California’s Central Valley.

**Integration question:** Add an inland river/levee comparator and assess whether water observations can complement gauge-based context.

**Standardized archive screen:** 472 granule metadata hits; 258 distinct acquisition dates (2024-09-02–2026-10-25) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://www.usgs.gov/centers/california-water-science-center/science/science-topics/floods)

### United States — Atlanta

The City’s 2025 comprehensive plan calls for stormwater management and flooding mitigation, including capital and watershed actions.

**Integration question:** Test an inland urban-runoff case and connect exposure evidence to watershed and public-infrastructure planning.

**Standardized archive screen:** 241 granule metadata hits; 99 distinct acquisition dates (2024-09-02–2026-10-24) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://www.atlantaga.gov/home/showpublisheddocument/66053/638884420075030000)

### United States — St. Louis

NOAA/NWS river gauge documentation defines flood stages and describes levee/floodwall impacts along the Mississippi.

**Integration question:** Test a major-river and levee comparator with official river-stage context.

**Standardized archive screen:** 232 granule metadata hits; 101 distinct acquisition dates (2024-09-06–2026-10-27) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://water.noaa.gov/gauges/eadm7)

### International — Jakarta

Greater Jakarta faces regular widespread flooding alongside water-supply deficits and water-quality challenges; the World Bank calls for integrated urban water management.

**Integration question:** Study cross-jurisdictional water exposure and the integration of flood, water-supply, sanitation, and infrastructure planning.

**Standardized archive screen:** 779 granule metadata hits; 249 distinct acquisition dates (2024-09-01–2026-10-28) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://www.worldbank.org/en/topic/water/publication/pathways-to-integrated-urban-water-management-for-greater-jakarta)

### International — Singapore

PUB documents flash/coastal flood risks, investments in drainage, a national flood-resilience program, and extensive sensor monitoring.

**Integration question:** Test a data-rich, highly urbanized setting where satellite screening can be compared with agency sensors and flood reports.

**Standardized archive screen:** 231 granule metadata hits; 163 distinct acquisition dates (2024-09-06–2026-10-28) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://www.pub.gov.sg/Public/KeyInitiatives/Flood-Resilience)

### International — Dubai

Dubai Municipality’s AED 30bn Tasreef program expands stormwater collection and drainage; contracts cover critical urban areas.

**Integration question:** Test rapid urban growth and major drainage investment, while treating dry-climate extreme rainfall as an event-based case.

**Standardized archive screen:** 1009 granule metadata hits; 381 distinct acquisition dates (2024-09-01–2026-10-27) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://www.dm.gov.ae/aed-1-439-billion-contracts-awarded-for-four-tasreef-project-phases/)

### International — Mumbai

India approved an urban flood risk mitigation program that includes Mumbai; city planning and IFLOWS document substantial flood research and warning needs.

**Integration question:** Test monsoon, coastal, drainage, and asset exposure; join satellite screening to the city’s flood-warning and mitigation evidence.

**Standardized archive screen:** 361 granule metadata hits; 121 distinct acquisition dates (2024-09-02–2026-10-24) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2297625&lang=1&reg=3)

### International — Bangkok

World Bank city-region analysis documents interacting upstream runoff, intense local rainfall, and tidal effects.

**Integration question:** Test a deltaic megacity where river, pluvial, and tidal drivers overlap and require cross-system interpretation.

**Standardized archive screen:** 170 granule metadata hits; 127 distinct acquisition dates (2024-09-06–2026-10-25) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://documents1.worldbank.org/curated/en/834261468025503285/pdf/508980ESW0v10P1pt1bangkok1report111.pdf)

### International — Tokyo

World Bank work documents Tokyo-region urban flood risk management practice and the need to integrate risk into urban planning and investment.

**Integration question:** Test a mature infrastructure context and evaluate water-screening evidence alongside risk-informed planning and engineered controls.

**Standardized archive screen:** 258 granule metadata hits; 202 distinct acquisition dates (2024-09-02–2026-10-25) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://www.worldbank.org/en/programs/tokyo-development-learning-center/tdd/tdd_on_urban_flood_management)

### International — Manila

World Bank-supported Metro Manila Flood Management Project targets 17 cities/municipalities and more than one million people with pump/drainage upgrades.

**Integration question:** Test a high-need urban drainage and pumping portfolio with documented public investment and operations context.

**Standardized archive screen:** 1166 granule metadata hits; 403 distinct acquisition dates (2024-09-01–2026-10-26) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://www.worldbank.org/ext/en/topic/water/water-for-planet)

### International — São Paulo

World Bank case material documents urban flood exposure, drainage constraints, and the need to combine structural and nonstructural measures.

**Integration question:** Test an inland megacity and connect observed-water evidence with drainage, land-use, and asset planning.

**Standardized archive screen:** 530 granule metadata hits; 196 distinct acquisition dates (2024-09-03–2026-10-25) for a 625 km² nominal AOI. **Candidate only:** QA-valid coverage and independent labels are pending. [Evidence source](https://documents1.worldbank.org/curated/en/659161468182066104/pdf/709820PUB0EPI0067926B09780821389621.pdf)

## Reproducibility and limitations

The acquisition-date count is computed by grouping returned CMR granule metadata by `time_start` date for a common product, AOI window, and temporal range. One date may have multiple granules; a metadata hit is not a downloaded raster or an observed flood. The 24 common year-months are a coarse metadata availability check, not equivalent sensor view, scene quality, event relevance or pixel coverage. The bounding boxes approximate equal metric area and can include different urban land proportions, coastlines, and asset populations. Archive access is public for this metadata query; no Earthdata credentials, OPERA pixels, asset registry, or independent validation labels were used.

The production version 9 area-register export includes each AOI bounding box, collection and date window, every CMR acquisition date, date count, evidence URL, rationale, value-integration question, and candidate status. Reproduce it with `scripts/screen_study_areas.py`, `scripts/audit_temporal_overlap.py`, and `scripts/export_study_area_register.py`. These artifacts expose metadata timing differences; they do not establish comparable valid-pixel coverage.

OPERA DSWx-S1 is a 30 m research product. Before analysis, pin the product/spec/software version; obtain granules; decode water, mask, layover/shadow and fill codes; calculate valid-pixel fraction over each fixed asset footprint; document georegistration and geometry uncertainty; select event/baseline dates with a common rule; and compare against independent field, agency, or gauge/mapped observations appropriate to the hazard. Gauges support temporal context but are not spatial flood-extent truth.

## Evidence sources for the common product and design

- NASA [OPERA products and temporal availability](https://www.jpl.nasa.gov/go/opera/products/).
- NASA [OPERA DSWx summary, interpretation and limitations](https://science.data.nasa.gov/disasters/data-gallery/opera-dswx).
- PO.DAAC [OPERA DSWx-S1 V1 collection](https://podaac.jpl.nasa.gov/dataset/OPERA_L3_DSWX-S1_V1).
- JPL [DSWx product suite and non-harmonized sensor products](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/).
- World Bank [urban risk assessment framework](https://www.worldbank.org/en/topic/urbandevelopment/publication/urban-risk-assessments).

## Pixel-QA and 16-area balance implementation

`scripts/analyze_opera_geotiffs.py` now processes operator-supplied local single-band WTR GeoTIFFs. The manifest requires granule ID, acquisition date, predeclared period anchor, event/baseline label, pinned collection version, processing-software version, and timezone-qualified retrieval time. It records the source SHA-256 and analysis-script SHA-256. The script checks the 30 m projected grid, applies WTR V1 classes 0/1/3 and masks 250/251/255, fails unknown classes, and calculates valid and water fractions over the AOI and each supplied asset footprint. It does not fetch data or independently authenticate that the file is an OPERA granule.

`scripts/audit_study_area_balance.py` checks that a run includes every area in the canonical register (exactly 8 U.S. and 8 international), then finds one global matched count across every area and evaluated asset. A single area with fewer than three qualifying observations in either period blocks the comparative output for all areas. When coverage passes, each area uses its predeclared event and baseline anchors, nearest-date selection with deterministic ties, and equal counts across all 16. `outputs/atlas-study-package-template.json` lists the input files needed for such a run.

Unit tests create tiny synthetic GeoTIFFs to exercise class interpretation, masks, coverage gates, reproducible matched-date selection, and the 16-area global failure/pass rules. The tests validate implementation behavior only. No actual OPERA raster was loaded; no study area has passed pixel-QA; no independent flood labels or event comparisons exist. The 80% and three-date gates are preregistered engineering criteria, not empirically validated scientific thresholds. Actual input checksums and per-area results must be reviewed before treating any area as enrolled.

## Exploratory real-raster coverage screen across all 16 areas (2026-11-03)

To replace metadata-only pixel assumptions with a real-data coverage observation, `scripts/audit_s1rtc_pixel_coverage.py` read the public Microsoft Planetary Computer Sentinel-1 RTC collection for the fixed registered AOIs. The audit queried the same full 2025 calendar period for every candidate, drew one orbit group uniformly from the eligible groups in each quarter with the fixed seed `ATLAS-S1RTC-quarterly-coverage-v1`, and measured the fraction of AOI pixels that were finite and not the raster's declared nodata in the 10 m VV band. It read spatial COG windows only. Short-lived read-only storage tokens were kept in process memory and excluded from checkpoints and reports. The collection metadata declares 10 m VV backscatter and CC-BY-4.0 ([collection record](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc)); token acquisition follows the [Planetary Computer data-access documentation](https://planetarycomputer.microsoft.com/docs/concepts/sas/).

All 16 areas received four quarter-stratified samples (64 total). **56/64** sampled orbit groups met the 80% spatial-coverage floor, and **12/16** areas met it in all four sampled quarters. At least one selected sample was below 80% in Tampa (77.9% on 2025-02-12; 77.3% on 2025-08-11), New York City (3.4% on 2025-05-24; 3.1% on 2025-12-02), St. Louis (25.2% on 2025-09-13; 26.0% on 2025-12-30), and São Paulo (0.1% on 2025-01-13; 0.1% on 2025-06-06). Candidate orbit-group counts per quarter and per-item identifiers, checksums, and item links are recorded in `outputs/atlas-s1rtc-pixel-coverage-audit.json` (SHA-256 `8911ed93de7722517537e3b59f5f91dc9ee72ad4ba0364ecf25cc3a6f75a99b6`). These four locations remain candidates; the result means the randomly selected scene groups cannot count toward the final coverage floor, while other discoverable groups recorded by the audit still require full review.

This is a sampled observation-availability diagnostic only. It does not show a flood, classify water, validate OPERA DSWx-S1, establish same-date or same-orbit comparability among cities, test event/baseline adequacy, assess radiometric or geolocation quality, or supply independent labels. It does not change confirmatory enrollment status or earn score points. The finite/non-nodata rule measures spatial file coverage only; no water fraction or event effect is estimated.

Reproduce with Python 3.12 and the locked development/geospatial dependencies; the default resumable checkpoint is under ignored `work/` and contains no signed asset URL:

```sh
docker run --rm -v "$PWD:/workspace" -w /workspace python:3.12-bookworm \
  sh -lc 'python -m pip install --require-hashes -r requirements-dev.lock && python scripts/audit_s1rtc_pixel_coverage.py'
```


## Equal-depth area evidence and validation profiles

These 16 profiles use the same fields and structure. They identify public research or management need and operational validation sources; they do not establish direct customer demand or ATLAS accuracy.

### United States

#### Houston — adopted capital plan

Houston’s FY2026–2030 CIP estimates $1.156 billion for storm-drainage improvements, with about $170 million for Local Drainage Program and Storm Water Action Team projects. The plan describes objective ranking of flood-protection needs and design for 2-year collection-system rainfall while reducing structural-flood risk during 100-year events. [Primary evidence](https://www.houstontx.gov/cip/26cipadopt/e_storm.pdf).

**Fixed screen:** 446 CMR granule metadata hits, 126 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** drainage service continuity, capital-project prioritization, neighborhood-level exposure.

**Comparable validation path:** Overlay only city-published drainage project and channel/detention geodata available for the 25 km study box; compare event-period satellite classifications with city/USGS gauge records and dated official flood reports. Record geometry/date coverage before analysis.

**Scope limit:** CIP allocations are planned estimates, not measured reductions in flood loss; the plan cautions that receiving-system capacity can still cause flooding. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Miami — public-sector research demonstration

NOAA NCCOS reports a rainfall-flood model demonstrated over roughly 1,000 km² of Miami-Dade using rain, gauges, topography, land use, flood infrastructure, and groundwater. For a four-day May 2020 Memorial Day flood period, canal water levels were predicted with about 15 cm average accuracy and the model ran at least 30 times faster than real time. [Primary evidence](https://coastalscience.noaa.gov/news/new-model-enables-rapid-flood-prediction-in-miami-to-support-risk-management/).

**Fixed screen:** 131 CMR granule metadata hits, 112 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** canal and drainage operations, groundwater-sensitive neighborhoods, equitable risk-management prioritization.

**Comparable validation path:** Use documented gauge/canal levels, rainfall timing, and independently mapped event reports for a held-out event; treat the NOAA 2020 experiment as contextual precedent, not as ATLAS ground truth or performance evidence.

**Scope limit:** The NOAA demonstration is county-scale and predates the current candidate window; it does not validate the 625 km² candidate box or ATLAS. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Tampa — event instrumentation

USGS deployed eight wave sensors between Naples and Crystal River to measure Hurricane Milton coastal impacts and added a rapid deployment gauge in St. Petersburg; USGS also documented post-storm flood measurements and gauge repairs along Florida’s Gulf Coast. [Primary evidence](https://www.usgs.gov/news/national-news-release/usgs-deploys-sensors-along-floridas-gulf-coast-measure-impacts-hurricane).

**Fixed screen:** 261 CMR granule metadata hits, 106 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** coastal water level, transport and utility access, recovery prioritization.

**Comparable validation path:** Match any candidate-box OPERA dates to USGS/NWS gauge time series and geolocated high-water marks or official event reports. Keep regional instruments outside the box as context and do not count them as local reference samples.

**Scope limit:** The cited sensors cover a regional coast and do not establish adequate independent labels inside the Tampa candidate box. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### New Orleans — municipal hazard plan and operating context

The City’s hazard-mitigation plan identifies rainfall, ponding, backwater, riverine, coastal, and infrastructure-failure flooding, including combined hazards. It notes low-lying, poorly drained areas and dependence on pumps and levees; the plan documents 69 significant flooding events during 1997–2019. [Primary evidence](https://ready.nola.gov/hazard-mitigation/hazards/flooding/).

**Fixed screen:** 535 CMR granule metadata hits, 165 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** pump-dependent drainage service, road and emergency access, low-lying community exposure.

**Comparable validation path:** Pre-register one dated event and baseline, then compare eligible OPERA pixels with city pump/drainage records, NWS rainfall and river stages, and dated official street-flood reports where spatial precision is sufficient.

**Scope limit:** The city hazard plan is a planning source and historical event count is not a geocoded independent truth set. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### New York City — municipal monitoring and capital program

NYC DEP’s December 2025 report identifies 86 priority drainage areas in its 2024 Stormwater Analysis and reports city monitoring infrastructure including 325 FloodNet sensors and 241 sewer monitors. The report describes a multibillion-dollar capital program; the reported investment commitments are not flood-loss outcomes. [Primary evidence](https://www.nyc.gov/site/dep/news/25-031/mayor-adams-nyc-department-environmental-protection-delivered-historic-progress-climate).

**Fixed screen:** 922 CMR granule metadata hits, 238 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** critical sewer and transport service, neighborhood drainage priorities, public sensor coverage.

**Comparable validation path:** Acquire dated FloodNet and NYC DEP records, independently review their spatial coverage against the 625 km² box, and validate a held-out event against municipal inundation or high-water labels rather than using capital-plan priority zones as truth.

**Scope limit:** The agency’s counts are citywide and do not imply that all sensors or priority areas fall within the candidate AOI. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Sacramento — state flood-risk and levee context

California DWR describes more than 1,600 miles of State and federal levees in the Central Valley and more than 70 overtoppings or breaches since 1983; its flood-risk communication program sends notices to at-risk parcel owners across 17 counties. [Primary evidence](https://water.ca.gov/Programs/Flood-Management/Community-Resources/Flood-Risk).

**Fixed screen:** 472 CMR granule metadata hits, 258 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** levee-protected communities, transport and utility corridor exposure, risk communication.

**Comparable validation path:** Use local Sacramento River/American River gauge and levee incident records, DWR floodplain layers, and event-date reference extents; exclude regional counts from the local denominator.

**Scope limit:** These metrics describe the broader Central Valley program, not the city-center AOI, and the cited page does not provide a local event-label dataset. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Atlanta — municipal watershed planning and event response

Atlanta Watershed Management publishes ten watershed improvement plans that identify infrastructure needs and recommended projects. City emergency communications also document active monitoring of road, drainage, and public-safety conditions during heavy-rain flooding; this is direct management relevance but not a quantified citywide loss series. [Primary evidence](https://atlantawatershed.org/watershedimprovementplans/).

**Fixed screen:** 241 CMR granule metadata hits, 99 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** watershed and drainage investment, road access, neighborhood service equity.

**Comparable validation path:** Map plan project and stormwater geographies in the candidate box; evaluate a predeclared event using NWS rainfall, USGS stream gauges, and dated city incident/closure reports with location-level inclusion rules.

**Scope limit:** Plan coverage and agency response do not establish customer demand, parcel-level impacts, or independent event accuracy. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### St. Louis — official hydrologic record

NWS reports that the Mississippi River at St. Louis crested at 49.58 ft on August 1, 1993, then a record, during the region’s Great Flood. This provides a strong riverine/floodwall stress context for an inland comparator. [Primary evidence](https://www.weather.gov/lsx/1993_flood).

**Fixed screen:** 232 CMR granule metadata hits, 101 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** river and floodwall exposure, regional transport continuity, long-term flood preparedness.

**Comparable validation path:** Use NOAA/NWS gauge records and recent dated event reports for actual validation; retain 1993 as contextual extreme-event history, not as a contemporaneous label for the 2024–2026 screen.

**Scope limit:** The headline evidence is historical and regional; it does not establish recent local flooding or current demand. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

### International

#### Jakarta — municipal flood-response capacity and multilateral research

DKI Jakarta reported 580 stationary pumps across 202 locations and 557 mobile pumps across its five administrative cities in 2024. The World Bank describes Greater Jakarta as a 14-municipality/district, three-province system facing recurring floods alongside water-supply and sanitation challenges, and calls for integrated urban-water management. [Primary evidence](https://www.jakarta.go.id/siaran-pers/4685-SP-HMS-03-2024); [supporting evidence](https://www.worldbank.org/en/topic/water/publication/pathways-to-integrated-urban-water-management-for-greater-jakarta).

**Fixed screen:** 779 CMR granule metadata hits, 249 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** pump and drainage operations, water quality and supply, cross-administration planning.

**Comparable validation path:** Obtain dated BPBD flood-event and pump-operation records, rainfall and river/gate levels, then spatially resolve them to the fixed AOI. Engage local technical partners to review translation, data licensing, and location bias.

**Scope limit:** Pump counts are response-capacity inventory, not utilization or measured effectiveness; Greater Jakarta evidence spans well beyond the selected box. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Singapore — national drainage performance and current risk context

PUB reports that flood-prone area fell from about 3,200 ha in the 1970s to less than 25 ha, a 99% reduction, while also identifying continuing flash-flood and coastal-flood risks and named hotspots. The historical reduction is a national management outcome, not an ATLAS result. [Primary evidence](https://www.pub.gov.sg/Public/KeyInitiatives/Flood-Resilience/About-Floods).

**Fixed screen:** 231 CMR granule metadata hits, 163 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** drainage-service performance, urban transport and facility access, residual-risk hotspot prioritization.

**Comparable validation path:** Use PUB’s dated flood alerts, water-level sensor or rainfall records, and official hotspot polygons for a held-out event; spatially check each source against the common box and retain national statistics only as context.

**Scope limit:** National before/after flood-prone area figures cannot be attributed to the 625 km² screen or to satellite detection. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Dubai — funded infrastructure program (planned targets)

Dubai Municipality reports a Tasreef stormwater program estimated at AED 30 billion, with project targets to raise drainage capacity substantially and manage more than 20 million m³/day by planned 2033 completion; contracts have been awarded across project phases. These are design and delivery targets, not observed service outcomes. [Primary evidence](https://www.dm.gov.ae/dubai-municipality-and-dubai-south-launch-stormwater-tunnel-project-for-sustainable-infrastructure/); [supporting evidence](https://www.dm.gov.ae/aed-1-439-billion-contracts-awarded-for-four-tasreef-project-phases/).

**Fixed screen:** 1009 CMR granule metadata hits, 381 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** stormwater tunnel and network service, critical technology/logistics facilities, capital phasing and residual risk.

**Comparable validation path:** Acquire municipality project alignments, construction status, rainfall, and dated incident/road-closure records; stratify completed and under-construction assets before any exposure analysis.

**Scope limit:** Published capacity values are future program targets and cannot serve as observed flood truth or current system performance. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Mumbai — approved public flood-mitigation program

India’s August 2026 UFRMP Phase I announcement includes Mumbai, with a city allocation of ₹707.71 crore and ₹150 crore reported released at that point. It documents funded implementation need; project completion and measured outcomes remain pending. [Primary evidence](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2297625&lang=1&reg=3).

**Fixed screen:** 361 CMR granule metadata hits, 121 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** drainage and flood-risk reduction, transport and public-service continuity, implementation equity across neighborhoods.

**Comparable validation path:** Use BMC/Maharashtra dated rainfall, drainage works, pump/gauge operations, and geocoded flood incident records; separately identify pre- and post-project dates and verify data translation and spatial resolution.

**Scope limit:** Approval and release establish program activity, not completed works, reduced flooding, or customer demand. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Bangkok — multilateral hydrologic and flood-risk assessment

World Bank urban-flood analysis describes Bangkok risk as the interaction of large upstream runoff, intense local rainfall, and tidal influence, with major flood-control works built following past floods. This makes the city a useful compound-driver comparator. [Primary evidence](https://documents1.worldbank.org/curated/en/834261468025503285/pdf/508980ESW0v10P1pt1bangkok1report111.pdf).

**Fixed screen:** 170 CMR granule metadata hits, 127 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** urban drainage and river operations, commuter and utility access, upstream-to-city coordination.

**Comparable validation path:** Acquire Royal Irrigation Department and Bangkok Metropolitan Administration gauge, rainfall, pump, and event-closure records. Predefine local ground-truth sources and normalize Thai local time/date before matching satellite acquisitions.

**Scope limit:** The source is a planning/assessment report with historical context, not a current independent event label or an evaluation of ATLAS. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Tokyo — metropolitan flood-control inventory and target

Tokyo Metropolitan Government reports 30 operational underground river-storage facilities with about 2.73 million m³ total capacity as of October 2025, and a target of about 3.65 million m³ by 2035. Tokyo also publishes real-time river and flood information. [Primary evidence](https://www.kensetsu.metro.tokyo.lg.jp/river/chusho_seibi/ike); [supporting evidence](https://www.kasen-suibo.metro.tokyo.lg.jp/s/tsim0401g_en.html).

**Fixed screen:** 258 CMR granule metadata hits, 202 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** storage and river-control infrastructure, dense transport and utility service, investment tracking.

**Comparable validation path:** Use Tokyo river/flood telemetry and rainfall with event reports and storage-facility service areas; assess source timestamps, datum and Japanese date/time conventions before event matching.

**Scope limit:** Capacity is metropolitan inventory/target, not proof of local flood absence or a satellite-classification accuracy measure. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### Manila — multilateral program and target population

The World Bank describes the Metro Manila Flood Management Project as covering 17 cities/municipalities and targeting more than one million people through pumping-station, drainage, solid-waste and control-system improvements. [Primary evidence](https://www.worldbank.org/ext/en/topic/water/water-for-planet).

**Fixed screen:** 1166 CMR granule metadata hits, 403 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** pump-station service, drainage and solid-waste interactions, population and neighborhood access.

**Comparable validation path:** Obtain project pump and drainage locations, PAGASA rainfall, city/BWSC incident reports, and independently reviewed event extents. Resolve Metro Manila boundaries against the fixed city-center box and report only in-AOI evidence.

**Scope limit:** Project beneficiaries and footprint are regional targets, not actual affected persons or performance inside the candidate box. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.

#### São Paulo — municipal drainage plan and investment pipeline

São Paulo’s October 2026 drainage-plan release describes 201 interventions, 173 priority works, and a projected R$16.51 billion program through 2049. A separate municipal update reports 389 interventions completed since 2021; plan and commitment totals describe public management activity, not measured flood-loss reduction. [Primary evidence](https://prefeitura.sp.gov.br/web/obras/w/prefeitura-de-s%C3%A3o-paulo-publica-3%C2%AA-edi%C3%A7%C3%A3o-do-plano-diretor-de-drenagem-com-201-interven%C3%A7%C3%B5es-que-visam-a-redu%C3%A7%C3%A3o-de-alagamentos); [supporting evidence](https://prefeitura.sp.gov.br/web/obras/w/obras-refor%C3%A7am-o-combate-a-alagamentos-e-%C3%A1reas-de-risco-em-s%C3%A3o-paulo).

**Fixed screen:** 530 CMR granule metadata hits, 196 distinct dates, 625 km² nominal AOI, 2024-09-01 through 2026-11-02 UTC. **Value dimensions:** stormwater works and maintenance, transport and community service, project priority and equity.

**Comparable validation path:** Join dated municipal flood incident and rainfall records to geocoded interventions; separate completed/active/planned works, and validate a held-out event against independently reviewed high-water or flood-extent data.

**Scope limit:** Municipal project totals are citywide, may span the candidate box unevenly, and are not measured reduction in risk or proof of ATLAS demand. The candidate still has no demonstrated pixel-QA pass or independent-label accuracy result.
