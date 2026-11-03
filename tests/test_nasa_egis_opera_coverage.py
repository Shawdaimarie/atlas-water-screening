import datetime as dt
import json

from scripts.audit_nasa_egis_opera_coverage import (
    bbox_intersects,
    catalog_record,
    is_opera_dswx_image_service,
    make_spatial_query,
)


def test_service_filter_requires_opera_dswx_imageserver():
    assert is_opera_dswx_image_service("2428_OPERA_DSWx_S1", "ImageServer")
    assert not is_opera_dswx_image_service("2428_OPERA_DSWx_S1", "MapServer")
    assert not is_opera_dswx_image_service("generic_dswx", "ImageServer")


def test_geographic_extent_coarse_intersection():
    extent = {
        "xmin": -124, "ymin": 24, "xmax": -66, "ymax": 50,
        "spatialReference": {"wkid": 4326},
    }
    assert bbox_intersects(extent, (-96, 28, -95, 30))
    assert not bbox_intersects(extent, (100, 0, 101, 1))
    # Projected extents are left to ArcGIS's exact spatial predicate.
    projected = {**extent, "spatialReference": {"wkid": 3857}}
    assert bbox_intersects(projected, (100, 0, 101, 1))


def test_spatial_query_uses_fixed_wgs84_envelope():
    query = make_spatial_query((-96.0, 28.0, -95.0, 29.0))
    geometry = json.loads(query["geometry"])
    assert geometry == {
        "xmin": -96.0, "ymin": 28.0, "xmax": -95.0, "ymax": 29.0,
        "spatialReference": {"wkid": 4326},
    }
    assert query["spatialRel"] == "esriSpatialRelIntersects"
    assert query["returnGeometry"] == "false"


def test_catalog_date_and_s1_water_classification():
    millis = int(dt.datetime(2024, 10, 3, tzinfo=dt.timezone.utc).timestamp() * 1000)
    water = catalog_record({
        "objectid": 7, "name": "OPERA_DSWx_S1_WTR_20241003", "date": millis,
        "productname": "DSWx-S1 WTR", "groupname": "Milton", "category": "Raster",
    })
    assert water["date_utc"] == "2024-10-03"
    assert water["candidate_sentinel1_water_observation"] is True
    assert water["metadata_only"] is True

    change_map = catalog_record({
        "name": "OPERA_DSWx_S1_ChngMap_20241003", "productname": "Change Map", "date": None,
    })
    assert change_map["candidate_sentinel1_water_observation"] is False

    undated_wtr = catalog_record({"name": "OPERA_DSWx_S1_WTR_item", "date": None})
    assert undated_wtr["date_utc"] is None
    assert undated_wtr["candidate_sentinel1_water_observation"] is True

