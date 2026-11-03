from datetime import date

import numpy as np
from shapely.geometry import box

from scripts.audit_gfd_event_extent_coverage import (
    select_latest_mapped_overlaps,
    summarize_aoi_bands,
)


def test_latest_mapped_polygon_is_selected_without_using_raster_result():
    areas = [
        {
            "region": "United States",
            "city": "Example",
            "aoi_bbox_wgs84": "0,0,2,2",
        }
    ]
    events = [
        {"id": 1, "Began": date(2010, 1, 1), "Ended": date(2010, 1, 2),
         "Country": "Example", "geometry": box(1, 1, 3, 3)},
        {"id": 2, "Began": date(2015, 1, 1), "Ended": date(2015, 1, 2),
         "Country": "Example", "geometry": box(1, 1, 3, 3)},
        {"id": 3, "Began": date(2020, 1, 1), "Ended": date(2020, 1, 2),
         "Country": "Example", "geometry": box(1, 1, 3, 3)},
    ]
    objects = {
        1: {"name": "DFO_1.zip", "size": "10"},
        2: {"name": "DFO_2.zip", "size": "20"},
    }

    selected = select_latest_mapped_overlaps(events, objects, areas)

    event = selected["United States/Example"]
    assert event["event_id"] == 2
    assert event["event_start"] == "2015-01-01"
    assert event["event_end"] == "2015-01-02"
    assert event["gfd_object"]["size_bytes"] == 20


def test_aoi_pixel_summary_uses_only_flooded_band_valid_0_or_1():
    mask = np.array([[True, True, True, False]])
    bands = {
        "flooded": np.array([[0.0, 1.0, np.nan, 1.0]]),
        "duration": np.array([[0.0, 2.0, np.nan, 3.0]]),
        "clear_perc": np.array([[0.9, 0.8, np.nan, 1.0]]),
        "jrc_perm_water": np.array([[0.0, 0.0, np.nan, 0.0]]),
    }

    summary = summarize_aoi_bands(bands, mask)

    assert summary["aoi_raster_pixels"] == 3
    assert summary["flood_classified_pixels"] == 2
    assert summary["mapped_water_pixels_including_permanent"] == 1
    assert summary["event_flood_candidate_pixels"] == 1
    assert summary["nonwater_pixels"] == 1
    assert summary["gfd_missing_pixels"] == 1
    assert summary["clear_perc_ge_80pct_pixels"] == 2
    assert summary["duration_valid_event_flood_candidate_pixels"] == 1
