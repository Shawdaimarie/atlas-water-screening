"""Embed the complete discovery-date register and export schema into the static Site."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/study_area_register.json"
SITE_HTMLS = [ROOT / ".sites-open/dist/index.html", ROOT / "dist/index.html"]
FIELDS = [
    "region", "city", "lat", "lon", "aoi_bbox_wgs84", "aoi_area_km2",
    "collection", "temporal_start", "temporal_end", "cmr_granule_hits",
    "unique_acquisition_dates", "acquisition_dates", "first_acquisition_date",
    "last_acquisition_date", "returned_entries_complete", "screening_rationale",
    "value_integration_question", "evidence_url", "status",
    "need_evidence_type", "empirical_evidence", "value_dimensions",
    "validation_path", "scope_limit", "secondary_evidence_url", "current_official_hotspot_url",
    "event_reference_url", "event_reference_date", "event_reference_audit",
]
VALUE_CHAIN_START = "<!-- GENERATED PUBLIC VALUE CHAIN START -->"
VALUE_CHAIN_END = "<!-- GENERATED PUBLIC VALUE CHAIN END -->"
VALUE_CHAIN = (
    f"{VALUE_CHAIN_START}<div class=\"study-foot public-value-chain\" role=\"group\" aria-labelledby=\"publicValueTitle\">"
    "<b id=\"publicValueTitle\">Shared public-value framework · apply the same five steps in all 16 areas</b>"
    "<ol><li><b>Hazard observation:</b> report product class, acquisition time, valid-pixel fraction, and uncertainty.</li>"
    "<li><b>Asset exposure:</b> intersect dated, sourced asset footprints and report overlap and geometry completeness.</li>"
    "<li><b>Service consequence:</b> add criticality, population served, and dependencies only from attributable data reviewed with responsible agencies or communities.</li>"
    "<li><b>Distributional equity:</b> report who is represented and where coverage is missing, using privacy-preserving, locally governed data.</li>"
    "<li><b>Decision usefulness:</b> evaluate evidence against documented local priorities; use no weighted social-value score without stakeholder-approved weights and sensitivity analysis.</li></ol>"
    "<p>Keep observation, exposure, consequence, equity, and decision relevance separate. Water overlap alone does not establish damage, service failure, financial loss, realized benefit, or customer demand; unknowns stay unknown.</p>"
    f"</div>{VALUE_CHAIN_END}"
)


def update(html: str, areas: list[dict]) -> str:
    start = html.index("const studyAreas=")
    end = html.index(";let selectedStudyArea=", start)
    embedded = []
    evidence = json.loads((ROOT / "data/study_area_evidence.json").read_text())
    evidence_by_city = {record["city"]: record for record in evidence["records"]}
    if set(evidence_by_city) != {area["city"] for area in areas}:
        raise ValueError("Evidence profiles must match the 16 candidate areas exactly")
    for area in areas:
        record = dict(area)
        record["acquisition_dates"] = ";".join(record["acquisition_dates"])
        e = evidence_by_city[record["city"]]
        if record.get("evidence_url") != e.get("evidence_url"):
            raise ValueError(f"Primary source URL mismatch for {record['city']}")
        if e.get("secondary_evidence_url") == e.get("evidence_url"):
            raise ValueError(f"Primary and secondary source URLs must differ for {record['city']}")
        record["secondary_evidence_url"] = e.get("secondary_evidence_url", "")
        record["current_official_hotspot_url"] = e.get("current_official_hotspot_url", "")
        record["need_evidence_type"] = e["evidence_type"]
        record["empirical_evidence"] = e["empirical_evidence"]
        record["value_dimensions"] = "; ".join(e["value_dimensions"])
        record["validation_path"] = e["validation_path"]
        record["scope_limit"] = e["scope_limit"]
        record["secondary_evidence_url"] = e.get("secondary_evidence_url", "")
        record["event_reference_url"] = e.get("event_reference_url", "")
        record["event_reference_date"] = e.get("event_reference_date", "")
        record["event_reference_audit"] = e.get("event_reference_audit", "")
        embedded.append(record)
    data_literal = json.dumps(embedded, ensure_ascii=False, separators=(",", ":"))
    html = html[:start] + "const studyAreas=" + data_literal + html[end:]

    old_fields = [
        "region", "city", "cmr_granule_hits", "unique_acquisition_dates",
        "first_acquisition_date", "last_acquisition_date", "screening_rationale",
        "value_integration_question", "evidence_url", "status",
    ]
    old_schema = (
        "const cols=[" + ",".join("'" + field + "'" for field in old_fields)
        + "];const rows=[cols,...studyAreas.map(a=>cols.map(k=>a[k]))];"
    )
    new_schema = (
        "const cols=[" + ",".join("'" + field + "'" for field in FIELDS)
        + "];const rows=[cols,...studyAreas.map(a=>cols.map(k=>a[k]))];"
    )
    previous_fields = [field for field in FIELDS if field != "current_official_hotspot_url"]
    prior_schemas = [
        "const cols=" + "[" + ",".join("'" + field + "'" for field in schema_fields) + "];const rows=[cols,...studyAreas.map(a=>cols.map(k=>a[k]))];"
        for schema_fields in (
            old_fields,
            previous_fields[:-3],
            previous_fields[:-6],
            previous_fields,
            FIELDS[:-3],
            FIELDS[:-6],
            FIELDS,
        )
    ]
    schema_to_replace = next((schema for schema in prior_schemas if html.count(schema) == 1), None)
    if schema_to_replace is None:
        raise ValueError("Expected exactly one supported study-register CSV schema")
    html = html.replace(schema_to_replace, new_schema, 1)

    old_detail = '<p><b>Value integration question:</b> ${a.value_integration_question}</p><p><b>Common archive window:</b>'
    new_detail = ('<p><b>Public evidence (${a.need_evidence_type}):</b> ${a.empirical_evidence}</p>'
                  '<p><b>Value integration question:</b> ${a.value_integration_question}</p>'
                  '<p><b>Public value dimensions:</b> ${a.value_dimensions}</p>'
                  '<p><b>Comparable validation path:</b> ${a.validation_path}</p>'
                  '<p><b>Evidence limit:</b> ${a.scope_limit}</p>'
                  '<p><b>Common archive window:</b>')
    if html.count(old_detail) == 1:
        html = html.replace(old_detail, new_detail, 1)
    elif new_detail not in html:
        raise ValueError("Expected an existing or already-updated candidate detail card")
    old_source = '<a class="study-source" href="${a.evidence_url}" target="_blank" rel="noopener">Open primary evidence ↗</a>'
    secondary_source = '${a.secondary_evidence_url?` <a class="study-source" href="${a.secondary_evidence_url}" target="_blank" rel="noopener">Open supporting evidence ↗</a>`:""}'
    current_hotspot_source = '${a.current_official_hotspot_url?` <a class="study-source" href="${a.current_official_hotspot_url}" target="_blank" rel="noopener">Open current PUB hotspot list ↗</a>`:""}'
    primary_source = '<a class="study-source" href="${a.evidence_url}" target="_blank" rel="noopener">Open primary evidence ↗</a>'
    event_sources = ('${a.event_reference_url?` <a class="study-source" href="${a.event_reference_url}" target="_blank" rel="noopener">Open event source ↗</a>`:""}'
                     + '${a.event_reference_audit?` <a class="study-source" href="${a.event_reference_audit}" target="_blank" rel="noopener">Open event audit ↗</a>`:""}')
    previous_source = primary_source + secondary_source + event_sources
    new_source = primary_source + secondary_source + current_hotspot_source + event_sources
    # Older generated pages accidentally appended the supporting link twice.
    html = html.replace(new_source + secondary_source, new_source)
    if html.count(new_source) == 0:
        if html.count(previous_source) == 1:
            html = html.replace(previous_source, new_source, 1)
        elif html.count(old_source) == 1:
            html = html.replace(old_source, new_source, 1)
    if html.count(new_source) != 1:
        raise ValueError("Expected the primary evidence link exactly once")
    public_need_label = '<div class="study-status">Candidate only · metadata screening passed. OPERA pixel-level QA, event-matched scenes, asset geometry, and independent labels remain pending.</div>'
    demand_note = '<p><b>Demand distinction:</b> documented public management need does not establish ATLAS customer demand or purchase intent.</p>'
    public_need_detail = public_need_label + demand_note
    while html.count(public_need_detail + public_need_detail):
        html = html.replace(public_need_detail + public_need_detail, public_need_detail)
    while html.count(demand_note + demand_note):
        html = html.replace(demand_note + demand_note, demand_note)
    if public_need_detail in html:
        pass
    elif public_need_label in html:
        html = html.replace(public_need_label, public_need_detail, 1)
    else:
        raise ValueError("Expected candidate-only disclosure in the study-area detail card")

    if html.count(VALUE_CHAIN_START) == 0:
        matrix_end = "<!-- GENERATED SITE SELECTION MATRIX END -->"
        if html.count(matrix_end) != 1:
            raise ValueError("Expected the generated selection-matrix boundary exactly once")
        html = html.replace(matrix_end, matrix_end + VALUE_CHAIN, 1)
    elif html.count(VALUE_CHAIN_START) != 1 or html.count(VALUE_CHAIN_END) != 1:
        raise ValueError("Expected one complete generated public-value chain")
    return html


def main():
    areas = json.loads(REGISTER.read_text())["results"]
    if len(areas) != 16 or any(len(a["acquisition_dates"]) != a["unique_acquisition_dates"] for a in areas):
        raise ValueError("Expected all 16 candidates with complete matching date sets")
    for path in SITE_HTMLS:
        source = path.read_text()
        path.write_text(update(source, areas))
        print(f"Updated {path}")


if __name__ == "__main__":
    main()
