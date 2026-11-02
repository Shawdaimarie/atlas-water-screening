from scripts.audit_sentinel1_rtc_coverage import query_area


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.bodies = []

    def post(self, url, json, timeout):
        self.bodies.append(json)
        return FakeResponse(next(self.pages))


def test_query_area_follows_stac_pagination_and_deduplicates_dates():
    session = FakeSession(
        [
            {
                "features": [
                    {"properties": {"datetime": "2025-01-02T03:00:00Z"}},
                    {"properties": {"datetime": "2025-01-02T16:00:00Z"}},
                ],
                "links": [{"rel": "next", "body": {"token": "page-2"}}],
            },
            {
                "features": [
                    {"properties": {"datetime": "2025-01-08T03:00:00Z"}}
                ],
                "links": [],
            },
        ]
    )
    area = {
        "region": "International",
        "city": "Singapore",
        "aoi_bbox_wgs84": "103.7,1.2,103.9,1.4",
    }

    result = query_area(
        session,
        area,
        "2024-09-01T00:00:00Z",
        "2026-11-02T23:59:59Z",
    )

    assert result["item_count"] == 3
    assert result["distinct_dates"] == 2
    assert result["dates"] == ["2025-01-02", "2025-01-08"]
    assert result["year_months"] == ["2025-01"]
    assert result["pages_read"] == 2
    assert session.bodies[0]["collections"] == ["sentinel-1-rtc"]
    assert session.bodies[1] == {"token": "page-2"}

