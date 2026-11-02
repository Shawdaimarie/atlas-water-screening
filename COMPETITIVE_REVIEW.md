# ATLAS Competitive Review and Commercialization Hypotheses

Date: 2026-11-02. Desk research only; no customer interviews, pipeline, willingness-to-pay, market size, contract, or commercial validation is claimed. Review scope is a traceable historical surface-water exposure screen for infrastructure portfolio analysts.

## Alternatives

| Alternative | User/job and strengths | Gaps relative to bounded ATLAS hypothesis | Switching cost / comparison |
|---|---|---|---|
| FEMA Hazus | Public agencies, planners and risk analysts estimate potential physical damage/economic loss using hazard, inventory and damage functions; mature methodology and broad hazards. | Different job: modeled scenario/loss assessment rather than source-observation traceability and per-asset observed-water screening. ATLAS must not imply it improves loss estimates. | Existing GIS workflows, ArcGIS and training. Compare ATLAS only on time to traceable observed exposure evidence for a specific event. |
| USGS Flood Inundation Mapper | Communities and responders inspect modeled inundation maps and historical data at mapped reaches. | Coverage limited to available mapped reaches; models represent scenarios and include uncertainty. ATLAS hypothesis is event-specific observational evidence with explicit missingness. | Familiar public tool; no evidence of migration willingness. |
| Copernicus EMS | Emergency managers obtain on-demand mapping, early warning and exposure products; operational disaster mapping and population/built-up exposure. | Access and activation workflows differ; not established that it meets a specific infrastructure portfolio's routine asset-level traceability need. | Existing institutional access/process; possible alternative is analyst request or GIS workflow. |
| First Street Flood Model | Commercial US flood risk model with probabilistic, nationwide location/infrastructure outputs and bulk data offerings. | Commercial risk-model scope differs from transparent event observation; pricing/terms and input-level audit access need confirmation. | Procurement and data licensing may create switching cost; compare via evaluation dataset and buyer workflow. |

Sources and claim traceability are in EVIDENCE_REGISTER.md. Provider descriptions are not independent performance evidence.

## Defensible hypotheses (unvalidated)

1. Analysts may value a compact asset-level evidence trail showing exact satellite dates, OPERA collection/software version, quality masks, valid coverage and map context alongside exposure ranking.
2. Quality-aware temporal aggregation may reduce false alarms from one noisy observation at the cost of latency and missed short-duration flooding. The direction and magnitude are empirical questions.
3. Portfolio customers may pay for saved analyst time, repeatable audit evidence, and scheduled portfolio refreshes if those benefits exceed data, support, compute and sales costs.
4. Differentiation could come from transparent lineage, missingness-aware ranking, reproducible event replay and low-friction export, rather than exclusive data or a novel sensor/model.

None establishes novelty, moat, demand, or NASA endorsement.

## Benchmark and commercialization experiments

- Utility benchmark: time for an analyst to produce an asset evidence table/report from a selected event using current workflow versus ATLAS; predefine task and measure completion time/error/traceability.
- Technical research benchmark: compare single-observation threshold and quality-aware temporal aggregation on fixed event/asset units, held-out by event and region. Report precision, recall, IoU for labeled inundation, valid-data coverage, calibration only if outputs are probabilistic, and asset ranking metrics (e.g. top-k recall or NDCG) with uncertainty intervals. Fix scoring units, threshold selection, temporal window, spatial blocks and metrics before tuning. Do not treat upstream OPERA product as ground truth.
- Pilot hypothesis: quote by portfolio asset count and refresh frequency, with a fixed scope and explicit analyst review. Measure customer time saved/decision utility, contribution margin after imagery processing/cloud/support, and renewal intent; do not infer demand from a free demo.
- Test alternatives directly: ask qualified buyers what they currently use, procurement/security constraints, required evidence/export, and whether observed exposure fills a costly gap. No interviews have been conducted.

## Revenue pathways as arithmetic scenarios, not forecasts

A possible >USD 1M annual revenue path is 40 customers × USD 25,000 annual contract value = USD 1M annual revenue. Another illustrative mix is 100 customers × USD 10,000 = USD 1M. Both are arithmetic sensitivities only; there is no evidence for customer counts, price acceptance, sales cycle, retention or margin. Track gross margin after data/compute/support, customer acquisition cost, onboarding and renewal. Potential pricing axis: number of portfolio assets × update frequency × service level; validate with paid scoped pilots before projecting.

## Open-source and research contribution

Useful contributions could include issue reports or fixes in OPERA data-access examples, geospatial QA/mask parsing, reproducible event notebooks, and public benchmark protocols with independent labels. Upstream contribution acceptance, GitHub recognition, citations, Hugging Face relevance or Zenodo uptake are not promised. Publication should clearly label ATLAS as independent work and disclaim NASA/university endorsement. Hugging Face is only appropriate if a useful dataset/tool artifact fits its terms; no model is planned.

## Explicitly unavailable evidence

No buyer interviews, contracts, customer usage, willingness-to-pay, verified procurement route, data license clearance for a chosen public asset layer, comparative benchmark results, public endorsement, or market size evidence. No specific company or university was found to endorse ATLAS. Keep commercialization confidence low until measured evidence exists.
