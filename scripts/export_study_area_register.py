"""Export complete 8+8 candidate-area evidence registers in CSV and JSON."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/study_area_register.json"
EVIDENCE_SOURCE = ROOT / "data/study_area_evidence.json"
OUTPUT = ROOT / "outputs/atlas-study-area-register.csv"
JSON_OUTPUT = ROOT / "outputs/atlas-study-area-evidence-register.json"
FIELDS = [
    "region", "city", "lat", "lon", "aoi_bbox_wgs84", "aoi_area_km2",
    "collection", "temporal_start", "temporal_end", "cmr_granule_hits",
    "unique_acquisition_dates", "acquisition_dates", "first_acquisition_date",
    "last_acquisition_date", "returned_entries_complete", "screening_rationale",
    "value_integration_question", "evidence_url", "status",
    "need_evidence_type", "empirical_evidence", "value_dimensions",
    "validation_path", "scope_limit", "secondary_evidence_url",
    "event_reference_url", "event_reference_date", "event_reference_audit",
]


def build_rows(areas: list[dict], evidence_records: list[dict]) -> list[dict]:
    evidence_by_city = {record["city"]: record for record in evidence_records}
    if len(evidence_by_city) != len(evidence_records) or set(evidence_by_city) != {area["city"] for area in areas}:
        raise ValueError("Evidence profiles must match the candidate areas exactly")
    rows = []
    for area in areas:
        row = dict(area)
        evidence = evidence_by_city[row["city"]]
        row["need_evidence_type"] = evidence["evidence_type"]
        row["empirical_evidence"] = evidence["empirical_evidence"]
        row["value_dimensions"] = "; ".join(evidence["value_dimensions"])
        row["validation_path"] = evidence["validation_path"]
        row["scope_limit"] = evidence["scope_limit"]
        row["secondary_evidence_url"] = evidence.get("secondary_evidence_url", "")
        row["event_reference_url"] = evidence.get("event_reference_url", "")
        row["event_reference_date"] = evidence.get("event_reference_date", "")
        row["event_reference_audit"] = evidence.get("event_reference_audit", "")
        rows.append(row)
    return rows


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE_SOURCE.read_text(encoding="utf-8"))
    areas = source["results"]
    rows = build_rows(areas, evidence["records"])
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            flat = {field: row.get(field, "") for field in FIELDS}
            flat["acquisition_dates"] = ";".join(row["acquisition_dates"])
            writer.writerow(flat)
    payload = {
        "schema_version": 1,
        "screening_protocol": source["screening_protocol"],
        "results": rows,
    }
    JSON_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {OUTPUT} and {JSON_OUTPUT}")


if __name__ == "__main__":
    main()
