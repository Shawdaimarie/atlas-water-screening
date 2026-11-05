import zipfile
import json

import numpy as np
import pytest
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from rasterio.warp import transform_geom

from scripts.audit_asean_atlas_fixed_aoi import _aoi_polygon, _raster_row, parse_bbox


def test_parse_bbox_requires_a_valid_wgs84_envelope():
    assert parse_bbox("103.7,1.2,103.9,1.4") == (103.7, 1.2, 103.9, 1.4)
    for value in ("103.7,1.2,103.7,1.4", "181,1,182,2", "103.7,1,103.9"):
        with pytest.raises(ValueError):
            parse_bbox(value)


def test_fixed_aoi_screen_excludes_nodata_from_wet_area(tmp_path):
    bbox = (103.7, 1.2, 103.9, 1.4)
    geometry = transform_geom("EPSG:4326", "EPSG:32648", _aoi_polygon(bbox))
    coords = [point for ring in geometry["coordinates"] for point in ring]
    center_x = sum(point[0] for point in coords[:-1]) / (len(coords) - 1)
    center_y = sum(point[1] for point in coords[:-1]) / (len(coords) - 1)
    left = (center_x // 30) * 30
    top = (center_y // 30) * 30 + 30
    values = np.array([[0.0, 0.1], [0.2, np.nan]], dtype="float32")

    with MemoryFile() as memory:
        with memory.open(
            driver="GTiff",
            width=2,
            height=2,
            count=1,
            dtype="float32",
            crs="EPSG:32648",
            transform=from_origin(left, top, 30, 30),
            nodata=np.nan,
        ) as dataset:
            dataset.write(values, 1)
        raster_bytes = memory.read()

    archive = tmp_path / "singapore_flood_atlas.zip"
    inner = (
        "maps/singapore_ssp585_2020_rp10/pluvial/"
        "pluvial_depth_SSP5-8.5_2020_rp10.tif"
    )
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zipped:
        zipped.writestr(inner, raster_bytes)

    row = _raster_row(
        archive,
        "Singapore",
        {
            "city": "Singapore",
            "region": "International",
            "aoi_bbox_wgs84": ",".join(map(str, bbox)),
        },
        "pluvial",
        10,
    )

    assert row["aoi_pixels"] == 4
    assert row["valid_depth_pixels"] == 3
    assert row["valid_pixel_fraction"] == 0.75
    assert row["wet_depth_gt_0_pixels"] == 2
    assert row["wet_depth_ge_0_10_pixels"] == 2
    assert row["wet_area_denominator_pixels"] == 3
    assert row["wet_area_gt_0_km2"] == pytest.approx(0.0018)
    assert "not treated as dry" in row["area_method"]
    assert row["nodata_value"] is None
    json.dumps(row, allow_nan=False)
