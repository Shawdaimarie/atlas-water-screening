from datetime import datetime

from scripts.audit_usgs_gfid_aoi_events import (
    EXPECTED_MD5,
    _excel_date,
    distance_to_bbox_km,
    screen_rows,
)


def test_excel_serial_date_and_bbox_distance_are_parsed_consistently():
    assert _excel_date("45658") == datetime(2025, 1, 1).date()
    assert distance_to_bbox_km(0.5, 0.5, [0, 0, 1, 1]) == 0
    assert 10 < distance_to_bbox_km(1.1, 1.1, [0, 0, 1, 1]) < 20


def test_screen_distinguishes_exact_aoi_event_points_from_nearby_context():
    area = {
        "city": "Fixture City",
        "region": "Fixture",
        "aoi_area_km2": 625,
        "aoi_bbox_wgs84": "0,0,1,1",
    }
    rows = [
        {
            "Date": "2025-01-01",
            "Source": "EM-DAT",
            "Source_ID": "in-box",
            "Lat": "0.5",
            "Lon": "0.5",
            "Country": "Fixtureland",
        },
        {
            "Date": "2025-01-02",
            "Source": "DFO",
            "Source_ID": "near-box",
            "Lat": "1.1",
            "Lon": "1.1",
            "Country": "Fixtureland",
        },
        {
            "Date": "2025-01-03",
            "Source": "HANZE",
            "Source_ID": "far-away",
            "Lat": "2",
            "Lon": "2",
            "Country": "Fixtureland",
        },
    ]

    result = screen_rows(rows, [area], EXPECTED_MD5)
    assert result["counts"]["aggregated_rows_scanned"] == 3
    assert result["counts"]["rows_with_event_date_in_common_window"] == 3
    assert result["counts"]["representative_points_in_all_areas"] == 1
    assert result["counts"]["nearby_representative_points_within_25km_all_areas"] == 2
    screened = result["areas"][0]
    assert screened["events"][0]["source_id"] == "in-box"
    assert screened["nearby_discovery_leads"][0]["representative_point_inside_fixed_aoi"]
    assert screened["nearby_discovery_leads"][1]["source_id"] == "near-box"
    assert not screened["nearby_discovery_leads"][1]["representative_point_inside_fixed_aoi"]
