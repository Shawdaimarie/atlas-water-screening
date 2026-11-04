import datetime as dt
import json

import pytest

from scripts.audit_nasa_egis_opera_samples import (
    SERVICE_URL,
    _sample_item,
    _summarize,
    _validate_item,
    equal_area_sample_points,
)


def test_equal_area_points_are_reproducible_and_cover_each_stratum():
    bbox = (-82.6, 27.8, -82.3, 28.1)
    first = equal_area_sample_points(bbox, side=4, seed="fixed")
    second = equal_area_sample_points(bbox, side=4, seed="fixed")
    assert first == second
    assert len(first) == 16
    assert {(p["stratum_row"], p["stratum_col"]) for p in first} == {
        (row, col) for row in range(4) for col in range(4)
    }
    assert all(bbox[0] < p["lon"] < bbox[2] and bbox[1] < p["lat"] < bbox[3] for p in first)


def test_catalog_item_rejects_mismatched_date_and_id():
    millis = int(dt.datetime(2024, 9, 14, tzinfo=dt.timezone.utc).timestamp() * 1000)
    attributes = {
        "objectid": 1,
        "name": "20240914_DSWx-S1_BWTR",
        "date": millis,
        "productname": "Binary Water Detection",
    }
    assert _validate_item(attributes, object_id=1, expected_name=attributes["name"],
                          expected_date="2024-09-14")["raster_id"] == 1
    with pytest.raises(ValueError, match="Expected raster id"):
        _validate_item(attributes, object_id=3, expected_name=attributes["name"],
                       expected_date="2024-09-14")


def test_samples_pin_layer_and_preserve_raw_class_values():
    item = {"raster_id": 1, "name": "baseline", "date_utc": "2024-09-14"}
    points = equal_area_sample_points((-82.6, 27.8, -82.3, 28.1), side=2)
    calls = []

    def fake_fetch(url, params):
        calls.append((url, params))
        geometry = json.loads(params["geometry"])
        count = len(geometry["points"])
        return {"samples": [
            {"locationId": index, "rasterId": 1, "value": str(index % 2),
             "resolution": "29.97600242,29.97600242"}
            for index in range(count)
        ]}

    rows = _sample_item(fake_fetch, item, points)
    assert len(rows) == 4
    assert {row["raw_bwtr_class"] for row in rows} == {0, 1}
    assert all(url == f"{SERVICE_URL}/getSamples" for url, _ in calls)
    assert json.loads(calls[0][1]["mosaicRule"])["lockRasterIds"] == [1]
    assert calls[0][1]["interpolation"] == "RSP_NearestNeighbor"
    summary = _summarize(rows, item)
    assert summary["sampled_valid_fraction"] == 1
    assert summary["sampled_water_points"] == 2


def test_samples_reject_unknown_classes_and_foreign_raster_ids():
    item = {"raster_id": 1, "name": "baseline", "date_utc": "2024-09-14"}
    point = equal_area_sample_points((-82.6, 27.8, -82.3, 28.1), side=1)

    def unknown_class(url, params):
        return {"samples": [{"locationId": 0, "rasterId": 1, "value": "42"}]}

    with pytest.raises(ValueError, match="Unexpected BWTR class"):
        _sample_item(unknown_class, item, point)

    def wrong_raster(url, params):
        return {"samples": [{"locationId": 0, "rasterId": 2, "value": "1"}]}

    with pytest.raises(ValueError, match="different raster ID"):
        _sample_item(wrong_raster, item, point)
