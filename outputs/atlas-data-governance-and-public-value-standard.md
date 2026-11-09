# ATLAS data governance and public-value standard

**Version:** 1.0 · **Prepared:** 2026-11-04 · **Applies to:** all 16 candidate study areas

## Purpose and status

This standard makes data rights, public value, privacy, equity, and local accountability explicit alongside raster QA and statistical validity. It is a proposed research control, not evidence of community approval, agency endorsement, customer demand, or delivered benefit. Governance, local benefit review, and consultation are currently pending in all 16 candidate areas.

## Principles and how ATLAS applies them

- **FAIR stewardship:** document stable identifiers, descriptive metadata, access conditions, interoperable formats, provenance, licensing, and reuse limits. FAIR makes research artifacts easier to find and reuse; it does not make restricted data open or override local rules. See the [FAIR principles](https://force11.org/info/the-fair-data-principles/) and their peer-reviewed formulation in [Wilkinson et al. (2016)](https://doi.org/10.1038/sdata.2016.18).
- **CARE when Indigenous data are involved:** recognize Collective Benefit, Authority to Control, Responsibility, and Ethics for data about or relating to Indigenous Peoples, lands, and knowledge. Identify the relevant Indigenous governance body and apply locally defined protocols; do not treat CARE as a substitute for those protocols or as a blanket label for every dataset. See the [Global Indigenous Data Alliance's CARE principles](https://www.gida-global.org/care-principles-copy) and [Carroll et al. (2020)](https://doi.org/10.5334/dsj-2020-042).
- **Official-statistics integrity:** use professional source-quality review, appropriate methods, confidentiality, and privacy when using official statistical data. Review the source's quality, timeliness, cost, and respondent burden; retain any legal or statistical disclosure controls. See the [UN Fundamental Principles of Official Statistics](https://unstats.un.org/unsd/goodprac/bpaboutpr.asp?RecId=6).
- **Public-value accountability:** name the decision and intended beneficiaries, report foreseeable harms and limitations, and return useful outputs to relevant public or community partners. Do not claim that the analysis changes outcomes until that effect is independently measured.

## Mandatory dataset review

Before any non-satellite dataset enters an area's analysis, its record must include:

1. Custodian, persistent identifier or stable URL, version, retrieval timestamp, and checksum when permitted.
2. License, terms of use, permitted purposes, attribution, onward-sharing limits, retention, and deletion rules.
3. Spatial and temporal resolution, coordinate reference system, coverage, missingness, known bias, and transformation history.
4. Intended public decision, intended beneficiaries, foreseeable misuse or harm, and a plan for reporting results back.
5. Privacy and minimization assessment. Use aggregates; exclude direct identifiers; set disclosure suppression rules before joining datasets; do not re-identify people or households.
6. Local governance determination. If data concern Indigenous Peoples, lands, or knowledge, identify the appropriate authority, follow applicable Indigenous data-governance protocols, and obtain required permissions before access or reuse. If the applicability or authority is unclear, do not use the affected data until reviewed.
7. Equity review of population and geographic coverage, missingness, and groups that are not represented. Do not use vulnerability variables to score individuals or determine service priority without locally reviewed purpose and evidence.

## Reporting contract

Keep these quantities separate in every output:

- **Observed hazard:** sensor/product class, acquisition time, valid-pixel coverage, uncertainty, and known product limits.
- **Asset exposure:** geometric overlap and data completeness, not damage or service failure.
- **Service consequence:** criticality and population served only from attributable, licensed, appropriately governed evidence.
- **Distributional context:** aggregated coverage and missingness, with disclosure control and local review.
- **Decision value:** the documented decision, responsible authority, and whether the evidence changed a decision. No combined priority score without stakeholder-approved weights and sensitivity analysis.

No layer of management need, population vulnerability, critical infrastructure, or technology-hub status is a proxy for ATLAS demand, flood truth, damage, or social benefit. Public investment values and modeled hazards remain context unless their spatial and temporal fit to the fixed AOI is verified.

## Acceptance states

| State | Meaning | Permitted use |
|---|---|---|
| `pending` | Custodian, rights, local governance, privacy, or public-value review is incomplete. | Candidate-screening metadata only; do not use the unreviewed dataset in analysis or publish derived sensitive results. |
| `approved_with_conditions` | Reviewer recorded the authority, allowed purpose, safeguards, and limits. | Use only within documented conditions; preserve them in downstream exports. |
| `approved` | Rights, governance, privacy, quality, and intended use are documented and reviewed. | Use for the documented analysis and release scope. |
| `rejected_or_withdrawn` | Use is not authorized, is not fit for purpose, or permission was withdrawn. | Do not ingest; remove local copies and derived outputs according to the record. |

**Current 8+8 status:** all 16 candidate areas remain `pending` for local governance and benefit review. The status is intentionally conservative and does not assert that a particular community or authority has been identified, consulted, or has endorsed ATLAS. No governance gate is counted as passed until its evidence is recorded.

