from scripts.audit_jakarta_bpb_event_spatial_context import (
    REPORTED_AFFECTED_AREAS,
    intersecting_reported_areas,
)


def _polygon(xmin, ymin, xmax, ymax):
    return {
        "type": "Polygon",
        "coordinates": [[
            [xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax], [xmin, ymin]
        ]],
    }


def test_bpbd_event_admin_areas_match_fixed_aoi_by_city_and_name():
    aoi = _polygon(0, 0, 10, 10)
    features = [
        {
            "properties": {
                "wadmkk": "JAKARTA BARAT",
                "wadmkd": "KEDAUNG KALI ANGKE",
                "wadmkc": "CENGKARENG",
            },
            "geometry": _polygon(5, 5, 12, 12),
        },
        {
            # Same kelurahan name in a different city must not be conflated.
            "properties": {
                "wadmkk": "JAKARTA SELATAN",
                "wadmkd": "KAPUK",
                "wadmkc": "TEST",
            },
            "geometry": _polygon(1, 1, 2, 2),
        },
        {
            "properties": {
                "wadmkk": "JAKARTA TIMUR",
                "wadmkd": "CAWANG",
                "wadmkc": "TEST",
            },
            # Touching at the AOI boundary is not positive-area overlap.
            "geometry": _polygon(10, 2, 12, 4),
        },
    ]

    result = intersecting_reported_areas(features, aoi)

    assert result["reported_affected_kelurahan_count"] == 21
    assert result["reported_areas_returned_by_aoi_intersection_query_count"] == 2
    assert result["positive_area_intersection_count"] == 1
    hit = result["positive_area_intersections"][0]
    assert hit["administrative_city"] == "JAKARTA BARAT"
    assert hit["kelurahan"] == "KEDAUNG KALI ANGKE"
    assert hit["intersection_area_degrees_squared"] > 0
    assert len(result["not_returned_by_aoi_intersection_query"]) == 19


def test_official_jakarta_affected_area_transcription_is_balanced_and_contains_rawajati():
    assert len(REPORTED_AFFECTED_AREAS) == 21
    assert {area["city"] for area in REPORTED_AFFECTED_AREAS} == {
        "JAKARTA BARAT",
        "JAKARTA SELATAN",
        "JAKARTA TIMUR",
        "JAKARTA UTARA",
    }
    assert {"city": "JAKARTA SELATAN", "kelurahan": "RAWAJATI"} in REPORTED_AFFECTED_AREAS
