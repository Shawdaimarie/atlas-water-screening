import csv
import json
import math
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_full_evidence_register_csv_and_json_are_balanced_and_complete():
    source = json.loads((ROOT / "data/study_area_register.json").read_text())
    evidence = json.loads((ROOT / "data/study_area_evidence.json").read_text())
    exporter = runpy.run_path(str(ROOT / "scripts/export_study_area_register.py"))
    rows = exporter["build_rows"](source["results"], evidence["records"])

    assert len(rows) == 16
    assert [sum(row["region"] == region for row in rows) for region in ("United States", "International")] == [8, 8]
    assert len({row["city"] for row in rows}) == 16
    required = (
        "screening_rationale", "evidence_url", "need_evidence_type", "empirical_evidence",
        "value_integration_question", "value_dimensions", "validation_path", "scope_limit",
    )
    assert all(row.get(field) for row in rows for field in required)
    assert len({row["collection"] for row in rows}) == 1
    assert len({row["temporal_start"] for row in rows}) == 1
    assert len({row["temporal_end"] for row in rows}) == 1
    assert {row["aoi_area_km2"] for row in rows} == {625}
    assert all(len(row["acquisition_dates"]) == row["unique_acquisition_dates"] for row in rows)
    assert all(row["evidence_url"].startswith("https://") for row in rows)


def test_candidate_bounding_boxes_have_comparable_spherical_area():
    source = json.loads((ROOT / "data/study_area_register.json").read_text())
    radius_km = 6371.0088
    areas_km2 = []
    for row in source["results"]:
        west, south, east, north = map(float, row["aoi_bbox_wgs84"].split(","))
        area = radius_km**2 * math.radians(east - west) * (
            math.sin(math.radians(north)) - math.sin(math.radians(south))
        )
        areas_km2.append(area)

    assert len(areas_km2) == 16
    assert max(abs(area - 625) for area in areas_km2) / 625 < 0.01
    assert max(areas_km2) - min(areas_km2) < 0.1


def test_register_export_rejects_missing_or_duplicate_evidence_profiles():
    source = json.loads((ROOT / "data/study_area_register.json").read_text())
    evidence = json.loads((ROOT / "data/study_area_evidence.json").read_text())["records"]
    exporter = runpy.run_path(str(ROOT / "scripts/export_study_area_register.py"))
    with __import__("pytest").raises(ValueError, match="match the candidate areas"):
        exporter["build_rows"](source["results"], evidence[:-1])
    with __import__("pytest").raises(ValueError, match="match the candidate areas"):
        exporter["build_rows"](source["results"], evidence + [evidence[0]])


def test_generated_json_evidence_register_matches_csv_export():
    output = ROOT / "outputs/atlas-study-area-evidence-register.json"
    assert output.is_file()
    payload = json.loads(output.read_text())
    with (ROOT / "outputs/atlas-study-area-register.csv").open(newline="") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(payload["results"]) == len(csv_rows) == 16
    json_by_city = {row["city"]: row for row in payload["results"]}
    csv_by_city = {row["city"]: row for row in csv_rows}
    for city, row in json_by_city.items():
        assert ";".join(row["acquisition_dates"]) == csv_by_city[city]["acquisition_dates"]
        for field in ("empirical_evidence", "value_dimensions", "validation_path", "scope_limit"):
            assert row[field] == csv_by_city[city][field]
