"""Export a flat, reviewable CSV from the standardized CMR screen."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/study_area_register.json"
OUTPUT = ROOT / "outputs/atlas-study-area-register.csv"
FIELDS = [
    "region", "city", "lat", "lon", "aoi_bbox_wgs84", "aoi_area_km2",
    "collection", "temporal_start", "temporal_end", "cmr_granule_hits",
    "unique_acquisition_dates", "acquisition_dates", "first_acquisition_date",
    "last_acquisition_date", "returned_entries_complete", "screening_rationale",
    "value_integration_question", "evidence_url", "status",
    "need_evidence_type", "empirical_evidence", "value_dimensions",
    "validation_path", "scope_limit", "secondary_evidence_url",
]


def main():
    areas = json.loads(SOURCE.read_text())["results"]
    evidence = json.loads((SOURCE.parent / "study_area_evidence.json").read_text())
    evidence_by_city = {record["city"]: record for record in evidence["records"]}
    if set(evidence_by_city) != {area["city"] for area in areas}:
        raise ValueError("Evidence profiles must match the 16 candidate areas exactly")
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for area in areas:
            row = {field: area.get(field, "") for field in FIELDS}
            row["acquisition_dates"] = ";".join(area["acquisition_dates"])
            e = evidence_by_city[area["city"]]
            row["need_evidence_type"] = e["evidence_type"]
            row["empirical_evidence"] = e["empirical_evidence"]
            row["value_dimensions"] = "; ".join(e["value_dimensions"])
            row["validation_path"] = e["validation_path"]
            row["scope_limit"] = e["scope_limit"]
            row["secondary_evidence_url"] = e.get("secondary_evidence_url", "")
            writer.writerow(row)
    print(f"Wrote {len(areas)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
