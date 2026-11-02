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
]


def update(html: str, areas: list[dict]) -> str:
    start = html.index("const studyAreas=")
    end = html.index(";let selectedStudyArea=", start)
    embedded = []
    for area in areas:
        record = dict(area)
        record["acquisition_dates"] = ";".join(record["acquisition_dates"])
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
    if html.count(old_schema) != 1:
        raise ValueError("Expected to find the existing study-register CSV schema exactly once")
    return html.replace(old_schema, new_schema, 1)


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
