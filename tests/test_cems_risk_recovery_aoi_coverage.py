import json

from scripts.audit_cems_risk_recovery_aoi_coverage import audit


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class Session:
    def __init__(self, pages):
        self.pages = pages
        self.headers = {}

    def get(self, url, timeout):
        return Response(self.pages[url])


def test_catalog_geometry_screen_and_pagination(tmp_path):
    register = {"results": []}
    for i in range(16):
        register["results"].append({
            "region": "United States" if i < 8 else "International",
            "city": f"Area {i}",
            "aoi_bbox_wgs84": "0,0,1,1" if i == 0 else f"{i*10},0,{i*10+1},1",
        })
    register_path = tmp_path / "areas.json"
    register_path.write_text(json.dumps(register))
    url1 = "https://riskandrecovery.emergency.copernicus.eu/api/public-activations/"
    url2 = url1 + "?page=2"
    intersecting = {
        "code": "EMSN-test", "name": "Test Flood", "category": "Flood",
        "eventTime": "2025-01-01T00:00:00Z", "actDrmPhase": "Recovery", "closed": True,
        "products": [{"productName": "P01", "analysisName": "Extent",
                      "linkedAois": [{"aoiName": "test", "sqkm": "1",
                                      "extent": "POLYGON ((0.2 0.2, 0.8 0.2, 0.8 0.8, 0.2 0.8, 0.2 0.2))"}]}],
    }
    non_intersecting = {
        "code": "EMSN-away", "name": "Other", "category": "Wildfire",
        "products": [{"linkedAois": [{"extent": "POLYGON ((190 0, 191 0, 191 1, 190 1, 190 0))"}]}],
    }
    session = Session({url1: {"results": [intersecting], "next": url2},
                       url2: {"results": [non_intersecting], "next": None}})
    result = audit(register_path, tmp_path / "out.json", session)
    assert result["source"]["activation_count"] == 2
    assert result["counts"] == {
        "product_aoi_intersections": 1,
        "intersecting_flood_product_aois": 1,
        "areas_with_any_intersection": 1,
        "areas_with_flood_intersection": 1,
    }
    assert result["areas"][0]["flood_activations"] == 1
    assert result["areas"][1]["intersecting_product_aois"] == 0


def test_catalog_audit_requires_canonical_study_frame(tmp_path):
    register_path = tmp_path / "areas.json"
    register_path.write_text(json.dumps({"results": []}))
    try:
        audit(register_path, tmp_path / "out.json", Session({}))
    except ValueError as exc:
        assert "canonical 8 U.S. + 8 international" in str(exc)
    else:
        raise AssertionError("noncanonical frame should be rejected")
