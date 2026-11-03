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
    "validation_path", "scope_limit", "secondary_evidence_url",
]


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
        record["need_evidence_type"] = e["evidence_type"]
        record["empirical_evidence"] = e["empirical_evidence"]
        record["value_dimensions"] = "; ".join(e["value_dimensions"])
        record["validation_path"] = e["validation_path"]
        record["scope_limit"] = e["scope_limit"]
        record["secondary_evidence_url"] = e.get("secondary_evidence_url", "")
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
    prior_schemas = [
        "const cols=" + "[" + ",".join("'" + field + "'" for field in schema_fields) + "];const rows=[cols,...studyAreas.map(a=>cols.map(k=>a[k]))];"
        for schema_fields in (old_fields, FIELDS[:-6], FIELDS)
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
    new_source = ('<a class="study-source" href="${a.evidence_url}" target="_blank" rel="noopener">Open primary evidence ↗</a>'
                  '${a.secondary_evidence_url?` <a class="study-source" href="${a.secondary_evidence_url}" target="_blank" rel="noopener">Open supporting evidence ↗</a>`:""}')
    if html.count(new_source) == 0 and html.count(old_source) == 1:
        html = html.replace(old_source, new_source, 1)
    elif html.count(new_source) != 1:
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
