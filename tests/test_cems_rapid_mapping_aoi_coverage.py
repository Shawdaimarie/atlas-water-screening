import json

from shapely.geometry import box

from scripts import audit_cems_rapid_mapping_aoi_coverage as audit_module


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200
        self.headers = {}

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = responses
        self.urls = []

    def get(self, url, timeout):
        self.urls.append(url)
        return FakeResponse(self.responses[url])


def make_area(index, region, bbox):
    return {
        "city": f"Area {index}",
        "region": region,
        "aoi_bbox_wgs84": ",".join(map(str, bbox)),
    }


def test_live_audit_uses_paged_catalog_and_exact_aoi_product_intersections(tmp_path, monkeypatch):
    areas = [make_area(i, "United States", (0, 0, 1, 1)) for i in range(8)]
    areas += [make_area(i + 8, "International", (10, 10, 11, 11)) for i in range(8)]
    # Put the matching WKT only in the first area's fixed box.
    areas[1]["aoi_bbox_wgs84"] = "20,20,21,21"
    register_path = tmp_path / "register.json"
    register_path.write_text(json.dumps({"results": areas}))
    monkeypatch.setattr(audit_module, "CACHE_PATH", tmp_path / "cache")

    first_page = "https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations-info/"
    second_page = first_page + "?offset=10"
    detail_url = audit_module.DETAILS_URL + "?code=EMSR1"
    responses = {
        first_page: {
            "count": 2,
            "next": second_page,
            "results": [{"code": "EMSR1", "category": "Flood"}],
        },
        second_page: {
            "count": 2,
            "next": None,
            "results": [{"code": "EMSR2", "category": "Storm"}],
        },
        detail_url: {
            "results": [{
                "code": "EMSR1",
                "name": "Test flood",
                "eventTime": "2025-01-01T00:00:00",
                "category": "Flood",
                "aois": [{
                    "name": "Test AOI",
                    "number": 1,
                    "extent": box(0.25, 0.25, 0.75, 0.75).wkt,
                    "products": [{
                        "extent": box(0.4, 0.4, 0.6, 0.6).wkt,
                        "images": [{
                            "sensorType": "optical",
                            "sensorName": "TestSat",
                            "acquisitionTime": "2025-01-02T10:00:00",
                            "new": True,
                        }],
                        "layers": [{"format": "cog", "name": "test.tif"}],
                        "version": {"statusCode": "F"},
                        "downloadPath": "https://example.test/product.zip",
                    }],
                }],
            }]},
    }
    session = FakeSession(responses)
    output_path = tmp_path / "audit.json"
    result = audit_module.audit(register_path, output_path, session=session, request_pause_seconds=0)

    assert result["source"]["catalog_count_reported"] == 2
    assert result["source"]["catalog_pages_retrieved"] == 2
    assert result["source"]["flood_activations_screened"] == 1
    assert result["counts"]["areas_with_intersecting_flood_aois"] == 7
    assert result["counts"]["intersecting_flood_aois"] == 7
    assert result["counts"]["intersecting_products"] == 7
    assert all(x["intersecting_products"][0]["imagery"][0]["sensor_name"] == "TestSat" for x in result["matches"])
    assert json.loads(output_path.read_text())["audit_id"] == "atlas-cems-event-discovery-audit"
    assert all("not field truth" in row["interpretation"].casefold() for row in result["matches"])
