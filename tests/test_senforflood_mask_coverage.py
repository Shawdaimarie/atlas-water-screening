import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

from scripts.audit_senforflood_mask_coverage import inspect_mask, select_mask_manifest_entries


def test_manifest_excludes_hidden_appledouble_and_non_mask_tiffs():
    rows = [
        {"type": "file", "path": "DFO/Indonesia/E1/flood_mask/000000_flood_mask.tif"},
        {"type": "file", "path": "DFO/Indonesia/E1/flood_mask/._000000_flood_mask.tif"},
        {"type": "file", "path": "DFO/Indonesia/E1/s1_during_flood/000000_S1.tif"},
        {"type": "directory", "path": "DFO/Indonesia/E1/flood_mask"},
    ]
    selected, excluded = select_mask_manifest_entries(rows)
    assert [row["path"] for row in selected] == [rows[0]["path"]]
    assert excluded == 1


def test_mask_screen_counts_only_pixels_inside_the_registered_aoi(tmp_path):
    path = tmp_path / "mask.tif"
    values = np.array([[0, 1], [1, 255]], dtype=np.uint8)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=2,
        width=2,
        count=1,
        dtype="uint8",
        crs="EPSG:4326",
        transform=from_origin(0, 2, 1, 1),
        nodata=255,
    ) as dst:
        dst.write(values, 1)
    row = {"path": "CEMS/EMSR999/flood_mask/000000_flood_mask.tif", "oid": "fixture", "size": 4}
    area = {"key": "United States/Test", "geometry": box(0, 0, 1, 2)}
    result = inspect_mask(row, path, "fixture-sha256", [area])
    match = result["intersections"][0]
    assert match["chip_pixels_inside_aoi"] == 2
    assert match["valid_mask_pixels_inside_aoi"] == 2
    assert match["mask_class_counts_inside_chip_aoi_intersection"] == {"0": 1, "1": 1}
    assert result["source_group"] == "CEMS"
