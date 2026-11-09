import json
import io
import urllib.error

from scripts import audit_opera_earthdata_access as access_audit


def test_build_audit_keeps_access_failures_area_specific(tmp_path, monkeypatch):
    register = tmp_path / "register.json"
    register.write_text(json.dumps({"results": [
        {"region": "United States", "city": "A"},
        {"region": "International", "city": "B"},
    ]}))

    def fake_fetch(area):
        return {"region": area["region"], "city": area["city"],
                "cmr_status": "found", "unauthenticated_head_status": 403,
                "data_downloaded": False}

    monkeypatch.setattr(access_audit, "fetch_area", fake_fetch)
    audit = access_audit.build_audit(register, workers=1)

    assert audit["areas_tested"] == 2
    assert audit["status_counts"] == {"403": 2}
    assert {row["city"] for row in audit["areas"]} == {"A", "B"}
    assert all(row["data_downloaded"] is False for row in audit["areas"])


def test_fetch_area_checks_binary_water_asset_not_multiclass_wtr(monkeypatch):
    asset = "https://archive.podaac.earthdata.nasa.gov/protected/scene_B02_BWTR.tif"
    cmr = {
        "feed": {"entry": [{
            "producer_granule_id": "scene",
            "links": [
                {"href": "https://archive.podaac.earthdata.nasa.gov/protected/scene_B01_WTR.tif"},
                {"href": asset},
            ],
        }]}
    }
    requests = []

    class Response(io.BytesIO):
        status = 200
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.close()

    def fake_urlopen(request, timeout):
        requests.append(request)
        if request.get_method() == "HEAD":
            assert request.full_url == asset
            raise urllib.error.HTTPError(asset, 403, "Forbidden", {}, None)
        return Response(json.dumps(cmr).encode())

    monkeypatch.setattr(access_audit.urllib.request, "urlopen", fake_urlopen)
    row = access_audit.fetch_area({
        "region": "United States", "city": "Test", "first_acquisition_date": "2024-09-01",
        "collection": "OPERA_L3_DSWX-S1_V1", "aoi_bbox_wgs84": "-1,-1,1,1",
    })

    assert row["bwtr_asset_url"] == asset
    assert row["asset_layer"] == "B02_BWTR"
    assert row["unauthenticated_head_status"] == 403
    assert row["data_downloaded"] is False
    assert [request.get_method() for request in requests] == ["GET", "HEAD"]
