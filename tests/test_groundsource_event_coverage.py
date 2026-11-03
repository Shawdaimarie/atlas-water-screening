from shapely import wkb
from shapely.geometry import box

from scripts.audit_groundsource_event_coverage import intersecting_records, summarize


def areas():
    return [
        {"city": "A", "region": "United States", "aoi_bbox_wgs84": "-96,28,-95,29"},
        {"city": "B", "region": "International", "aoi_bbox_wgs84": "103,1,104,2"},
    ]


def test_exact_geometry_intersections_and_window():
    rows = [
        {"uuid": "a1", "geometry": wkb.dumps(box(-95.5, 28.2, -95.2, 28.4)), "start_date": "2024-09-12", "end_date": "2024-09-13", "area_km2": 4.5},
        {"uuid": "b1", "geometry": wkb.dumps(box(103.2, 1.2, 103.4, 1.4)), "start_date": "2025-01-01", "end_date": "2025-01-01", "area_km2": 1.0},
        {"uuid": "outside", "geometry": wkb.dumps(box(0, 0, 1, 1)), "start_date": "2025-01-01", "end_date": "2025-01-01", "area_km2": 2.0},
        {"uuid": "old", "geometry": wkb.dumps(box(-95.5, 28.2, -95.2, 28.4)), "start_date": "2024-09-11", "end_date": "2024-09-11", "area_km2": 4.5},
    ]
    matches = intersecting_records(rows, areas(), "2024-09-12", "2026-02-03")
    assert [(m["city"], m["event_id"]) for m in matches] == [("A", "a1"), ("B", "b1")]


def test_summary_keeps_empty_areas_and_counts_unique_start_dates():
    a = areas()
    matches = [
        {"city": "A", "event_id": "one", "start_date": "2025-01-01"},
        {"city": "A", "event_id": "two", "start_date": "2025-01-01"},
        {"city": "A", "event_id": "three", "start_date": "2026-02-03"},
    ]
    result = summarize(matches, a)
    assert result[0]["intersecting_event_records"] == 3
    assert result[0]["distinct_event_ids"] == 3
    assert result[0]["distinct_start_dates"] == 2
    assert result[0]["start_date_counts_by_year"] == {"2025": 1, "2026": 1}
    assert result[0]["start_date_range"] == ["2025-01-01", "2026-02-03"]
    assert result[1]["intersecting_event_records"] == 0
    assert result[1]["start_date_range"] is None
