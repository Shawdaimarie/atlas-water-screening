from shapely import wkb
from shapely.geometry import box

from scripts.audit_groundsource_event_coverage import (
    intersecting_records,
    rank_acquisition_opportunities,
    summarize,
)


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


def test_rank_acquisition_opportunities_counts_common_metadata_windows():
    a = areas()
    a[0]["acquisition_dates"] = [
        "2024-09-01", "2024-09-10", "2024-09-20", "2024-09-30",
        "2024-10-05", "2024-10-15", "2024-11-01",
    ]
    matches = [
        {"city": "A", "region": "United States", "event_id": "near", "start_date": "2024-10-01", "end_date": "2024-10-02", "reported_area_km2": 4.0},
        {"city": "A", "region": "United States", "event_id": "near", "start_date": "2024-10-01", "end_date": "2024-10-02", "reported_area_km2": 4.0},
        {"city": "A", "region": "United States", "event_id": "far", "start_date": "2024-11-20", "end_date": "2024-11-21", "reported_area_km2": 2.0},
    ]
    result = rank_acquisition_opportunities(matches, a, limit=5)
    assert result[0]["candidate_event_count"] == 2
    assert result[0]["events_with_product_date_within_1_day"] == 1
    near = result[0]["top_candidates"][0]
    assert near["event_id"] == "near"
    assert near["nearest_product_date_offset_calendar_days"] == 1
    assert near["pre_event_30d_product_dates"] == ["2024-09-01", "2024-09-10", "2024-09-20", "2024-09-30"]
    assert near["post_event_30d_product_dates"] == ["2024-10-05", "2024-10-15", "2024-11-01"]
    assert near["has_3_pre_event_metadata_dates"] is True
    assert near["has_3_post_event_metadata_dates"] is True
    assert "independent labels pending" in near["screen_status"]
    assert result[1]["candidate_event_count"] == 0


def test_rank_acquisition_opportunities_does_not_call_metadata_dates_timestamps():
    a = areas()
    a[0]["acquisition_dates"] = ["2025-01-02"]
    event = {"city": "A", "region": "United States", "event_id": "same-day", "start_date": "2025-01-02", "end_date": "2025-01-02"}
    result = rank_acquisition_opportunities([event], a)
    assert result[0]["top_candidates"][0]["nearest_product_date_offset_calendar_days"] == 0
    assert result[0]["top_candidates"][0]["has_calendar_date_match_within_1_day"] is True
    # Output schema explicitly limits claims to calendar-day metadata matches.
    assert result[0]["top_candidates"][0]["screen_status"].startswith("discovery lead;")
