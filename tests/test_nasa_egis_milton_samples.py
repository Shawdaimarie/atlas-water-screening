import json
from datetime import datetime, timezone

from scripts.audit_nasa_egis_milton_samples import SERVICE_URL, SCENES, run


def test_run_preserves_scene_sample_counts_and_service_error(tmp_path):
    register = tmp_path / "register.json"
    register.write_text(json.dumps({"results": [{
        "city": "Tampa", "region": "United States",
        "aoi_bbox_wgs84": "-82.584317,27.838311,-82.330083,28.062889",
    }]}))

    def fake_fetch(url, params):
        if url == SERVICE_URL:
            return {"description": "Preliminary and unvalidated response maps; October 3, 2024 and October 11, 2024; 30 meters"}
        if url.endswith("/query"):
            scene = next(item for item in SCENES if item["raster_id"] == int(params["objectIds"]))
            when = datetime.fromisoformat(scene["date"]).replace(tzinfo=timezone.utc)
            return {"features": [{"attributes": {
                "objectid": scene["raster_id"], "name": scene["name"],
                "date": when.timestamp() * 1000, "productname": "WTR mosaic", "category": 1,
            }}]}
        rule = json.loads(params["mosaicRule"])
        raster_id = rule["lockRasterIds"][0]
        if raster_id == 4:
            return {"error": {"code": 400, "message": "Invalid or missing input parameters."}}
        points = json.loads(params["geometry"])["points"]
        return {"samples": [
            {"locationId": i, "rasterId": raster_id, "resolution": 30,
             "value": [0, 1, 3, 7][i % 4]}
            for i, _ in enumerate(points)
        ]}

    report, rows = run(fake_fetch, register)
    assert [scene["samples_returned"] for scene in report["scenes"]] == [1024, 1024, 0, 1024]
    assert [scene["sampling_status"] for scene in report["scenes"]] == [
        "sampled", "sampled", "service_error", "sampled"
    ]
    assert report["scenes"][0]["class_counts"] == {"0": 256, "1": 256, "3": 256, "7": 256}
    assert report["scenes"][2]["sampling_error"]["code"] == 400
    assert sum(row["sample_status"] == "not_sampled_after_service_error" for row in rows) == 1024


def test_run_rejects_unlocked_raster_sample(tmp_path):
    register = tmp_path / "register.json"
    register.write_text(json.dumps({"results": [{
        "city": "Tampa", "region": "United States",
        "aoi_bbox_wgs84": "-82.584317,27.838311,-82.330083,28.062889",
    }]}))
    sample_seen = False

    def fake_fetch(url, params):
        nonlocal sample_seen
        if url == SERVICE_URL:
            return {"description": "Preliminary and unvalidated response maps; October 3, 2024 and October 11, 2024; 30 meters"}
        if url.endswith("/query"):
            scene = next(item for item in SCENES if item["raster_id"] == int(params["objectIds"]))
            when = datetime.fromisoformat(scene["date"]).replace(tzinfo=timezone.utc)
            return {"features": [{"attributes": {
                "objectid": scene["raster_id"], "name": scene["name"],
                "date": when.timestamp() * 1000, "productname": "WTR mosaic", "category": 1,
            }}]}
        rule = json.loads(params["mosaicRule"])
        raster_id = rule["lockRasterIds"][0]
        if not sample_seen:
            sample_seen = True
            points = json.loads(params["geometry"])["points"]
            return {"samples": [{"locationId": 0, "rasterId": raster_id + 1,
                                  "resolution": 30, "value": 1}]}
        return {"error": {"code": 400, "message": "stop fixture"}}

    import pytest
    with pytest.raises(ValueError, match="unlocked raster"):
        run(fake_fetch, register)
