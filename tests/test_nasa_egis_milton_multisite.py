import json
from collections import Counter
from datetime import datetime, timezone

from scripts.audit_nasa_egis_milton_multisite import audit
from scripts.build_site_multisite_egis_card import ANCHOR, build
from scripts.audit_nasa_egis_milton_samples import SCENES, SERVICE_URL


def test_multisite_audit_uses_same_seeded_samples_and_keeps_preliminary_limits(tmp_path):
    register = tmp_path / "register.json"
    register.write_text(json.dumps({"results": [
        {"city": "Miami", "region": "United States",
         "aoi_bbox_wgs84": "-80.316481,25.649411,-80.067119,25.873989"},
        {"city": "Tampa", "region": "United States",
         "aoi_bbox_wgs84": "-82.584317,27.838311,-82.330083,28.062889"},
    ]}))
    locked_ids = []

    def fake_fetch(url, params):
        if url == SERVICE_URL:
            return {"description": "NASA preliminary and unvalidated response maps."}
        if url.endswith("/query"):
            scene = next(x for x in SCENES if x["raster_id"] == int(params["objectIds"]))
            extent = (-85.0, 24.0, -80.4, 34.0) if scene["raster_id"] == 3 else (
                -84.0, 24.0, -79.0, 34.0
            )
            ring = [[extent[0], extent[1]], [extent[2], extent[1]],
                    [extent[2], extent[3]], [extent[0], extent[3]],
                    [extent[0], extent[1]]]
            date = datetime.fromisoformat(scene["date"]).replace(tzinfo=timezone.utc)
            return {"features": [{"attributes": {
                "objectid": scene["raster_id"], "name": scene["name"],
                "date": date.timestamp() * 1000,
                "productname": "WTR mosaic", "category": 1,
            }, "geometry": {"rings": [ring]}}]}
        points = json.loads(params["geometry"])["points"]
        raster_id = json.loads(params["mosaicRule"])["lockRasterIds"][0]
        locked_ids.append(raster_id)
        return {"samples": [
            {"locationId": i, "rasterId": raster_id, "resolution": 30,
             "value": [0, 1, 3, 7][i % 4]}
            for i, _ in enumerate(points)
        ]}

    report, rows = audit(fake_fetch, register)
    assert report["summary"]["areas"] == 2
    assert report["summary"]["confirmatory_eligible_areas"] == 0
    assert [a["city"] for a in report["areas"]] == ["Miami", "Tampa"]
    assert [a["scenes_with_any_returned_samples"] for a in report["areas"]] == [3, 4]
    assert Counter(locked_ids) == {2: 8, 3: 4, 4: 8, 5: 8}
    assert len(rows) == 8 * 1024  # Missing-footprint attempts remain explicit rows.
    assert all(a["sample_design"]["points_per_scene"] == 1024 for a in report["areas"])
    assert all(a["scenes"][0]["class_counts"] == {"0": 256, "1": 256, "3": 256, "7": 256}
               for a in report["areas"])
    assert any("preliminary/unvalidated" in limit for limit in report["limits"])


def test_multisite_audit_rejects_missing_fixed_area(tmp_path):
    register = tmp_path / "register.json"
    register.write_text(json.dumps({"results": [
        {"city": "Miami", "region": "United States",
         "aoi_bbox_wgs84": "-80.316481,25.649411,-80.067119,25.873989"},
    ]}))
    import pytest

    with pytest.raises(ValueError, match="exactly one Miami and one Tampa"):
        audit(lambda *_args, **_kwargs: {}, register)


def test_multisite_site_card_keeps_missingness_and_unvalidated_limits():
    report = {
        "areas": [
            {"city": "Miami", "scenes": [
                {"date_utc": "2024-10-03", "sampling_status": "sampled",
                 "samples_returned": 1024, "samples_requested": 1024},
                {"date_utc": "2024-10-10", "sampling_status": "service_error",
                 "samples_returned": 0, "samples_requested": 1024},
            ]},
            {"city": "Tampa", "scenes": [
                {"date_utc": "2024-10-03", "sampling_status": "sampled",
                 "samples_returned": 797, "samples_requested": 1024},
            ]},
        ]
    }
    source = f"<section>{ANCHOR}</section>"
    result = build(source, report)
    assert "Miami and Tampa · Hurricane Milton raw WTR samples" in result
    assert "10-03: 1024/1024 returned; 10-10: service error" in result
    assert "10-03: 797/1024 returned" in result
    assert "not full-AOI coverage" in result
    assert "three-valid-scene event/baseline rule" in result
    assert build(result, report) == result
