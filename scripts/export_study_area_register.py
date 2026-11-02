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
]


def main():
    areas = json.loads(SOURCE.read_text())["results"]
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for area in areas:
            row = {field: area.get(field, "") for field in FIELDS}
            row["acquisition_dates"] = ";".join(area["acquisition_dates"])
            writer.writerow(row)
    print(f"Wrote {len(areas)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
