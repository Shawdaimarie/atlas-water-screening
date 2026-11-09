import datetime as dt

from scripts.audit_opera_hls_egis_coverage import epoch_ms, query_area, render_markdown


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append((url, params, timeout))
        return FakeResponse(self.pages.pop(0))


def test_epoch_ms_assumes_utc_and_respects_offsets():
    assert epoch_ms("2026-01-01") == 1767225600000
    assert epoch_ms("2026-01-01T01:00:00+01:00") == 1767225600000


def test_query_area_pages_primary_scenes_and_groups_by_utc_date():
    session = FakeSession([
        {
            "features": [
                {"attributes": {"datetime": 1767225600000, "name": "A", "cloud_coverage": 20,
                                "spacecraft_name": "Landsat-8", "tileid": "T1"}},
                {"attributes": {"datetime": 1767225600000, "name": "B", "cloud_coverage": 30,
                                "spacecraft_name": "Sentinel-2A", "tileid": "T2"}},
            ],
            "exceededTransferLimit": True,
        },
        {
            "features": [
                {"attributes": {"datetime": 1767312000000, "name": "C", "cloud_coverage": None,
                                "spacecraft_name": "Landsat-9", "tileid": "T3"}},
            ],
            "exceededTransferLimit": False,
        },
    ])
    area = {
        "region": "International",
        "city": "Test City",
        "aoi_bbox_wgs84": "100.0,-1.0,101.0,0.0",
    }

    result = query_area(session, area, "2026-01-01", "2026-02-01", page_size=2)

    assert result["primary_scene_records"] == 3
    assert result["distinct_acquisition_dates"] == 2
    assert result["acquisitions"][0]["scene_records"] == 2
    assert result["acquisitions"][0]["spacecraft"] == ["Landsat-8", "Sentinel-2A"]
    assert result["acquisitions"][0]["tile_ids"] == ["T1", "T2"]
    assert result["acquisitions"][0]["scene_cloud_coverage_percent_min"] == 20
    assert result["acquisitions"][0]["scene_cloud_coverage_percent_max"] == 30
    assert result["acquisitions"][1]["scene_cloud_coverage_percent_min"] is None
    assert session.calls[0][1]["resultOffset"] == 0
    assert session.calls[1][1]["resultOffset"] == 2
    assert session.calls[0][1]["where"] == "category=1"
    assert session.calls[0][1]["returnGeometry"] == "false"
    assert session.calls[0][1]["time"] == f"{epoch_ms('2026-01-01')},{epoch_ms('2026-02-01')}"


def test_markdown_keeps_cross_sensor_and_metadata_limits_visible(tmp_path):
    audit = {
        "generated_at_utc": "2026-11-04T00:00:00+00:00",
        "query": {"start_date_utc_inclusive": "2024-09-01", "end_date_utc_exclusive": "2026-11-03"},
        "areas_succeeded": 1,
        "areas_with_at_least_90_metadata_dates": 1,
        "total_scene_records": 1,
        "total_area_date_pairs": 1,
        "areas": [{"region": "United States", "city": "Example", "primary_scene_records": 1,
                   "distinct_acquisition_dates": 1, "first_acquisition_date": "2026-01-01",
                   "last_acquisition_date": "2026-01-01"}],
        "interpretation_limits": [
            "Metadata only.",
            "Cross-sensor comparison, not independent field truth.",
        ],
    }
    markdown = render_markdown(audit, tmp_path / "audit.json")
    assert "metadata dates" in markdown
    assert "not independent field truth" in markdown
    assert "No score points" in markdown

