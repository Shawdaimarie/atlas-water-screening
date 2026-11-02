# ATLAS candidate study-area program

Prepared 2026-11-02. This is an evidence-based candidate register and archive discovery screen, not a claim that 16 sites have completed observation validation.

## Selection principles

1. **Research fit:** urban surface-water exposure intersects critical infrastructure, flood-management decisions, or integrated water planning. Technology-hub status helps diversify operating contexts; it is not itself evidence of hydrologic need.
2. **Verifiable need:** prioritize official plans, funded flood programs, hydrologic observations, and peer-reviewed or public-sector research. These establish public research/management need, not ATLAS customer demand.
3. **Comparable discoverability:** screen the same NASA OPERA DSWx-S1 V1 collection and temporal window in equal nominal 25 × 25 km city-center boxes (~625 km²). CMR granule counts are metadata-discovery counts, not observations passing QA.
4. **Study enrollment gate:** at least 90 distinct acquisition dates in the metadata screen. All 16 pass this discovery gate. Final enrollment additionally requires readable product layers, valid-data coverage, scene-level QA, event/baseline match, assets with auditable geometry, and independent labels.
5. **Balanced design:** use a common analytical footprint and definitions; for each event and baseline period at least 3 QA-valid acquisition dates in each event and baseline period, each with at least 80% unmasked pixels across the AOI and asset footprint; if more qualify, select the same count per area, require a predeclared valid-pixel fraction, report missingness, and do not impute. If a site fails, defer it or replace it before analysis. Product-class signals are not ground truth.
6. **Value integration:** report observed water overlap separately from consequence. Add service criticality, population served, vulnerable communities, and local management priorities only where licensed, attributable datasets and community/agency review support them; do not turn exposure into damage or financial-loss claims.

## Candidate coverage

Common window: 2024-09-01T00:00:00Z to 2026-11-02T23:59:59Z. Collection: OPERA_L3_DSWX-S1_V1. The number of distinct acquisition dates ranges from 99 to 403 (median 165). The reproducible date-set intersection audit found **zero exact acquisition dates common to all 16 areas**; all 16 have at least one archive metadata date in **24 of the 26 year-month periods** represented across the candidates. This supports event-relative sampling with matched counts, not same-date comparisons. Equal AOI size and a discovery threshold do not establish equal usable-pixel coverage. At least 3 QA-valid scenes per event and baseline, with ≥80% unmasked pixels per AOI and asset footprint, must still be audited for each enrolled site; select the same number across sites and report exclusions. Raw date sets and the audit are in `data/study_area_register.json` and `outputs/atlas-temporal-overlap-audit.json`; reproduce with `python3 scripts/screen_study_areas.py` then `python3 scripts/audit_temporal_overlap.py`.

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
