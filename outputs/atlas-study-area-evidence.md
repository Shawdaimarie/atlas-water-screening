# ATLAS — equal-depth study-area evidence

Prepared 2026-11-02.

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
