import json

import numpy as np
import pytest
import rasterio
from rasterio.io import MemoryFile

from scripts.audit_nasa_egis_neworleans_bwtr_coverage import (
    RASTER_ID,
    RASTER_NAME,
    SERVICE_URL,
    audit,
    projected_grid,
    summarize_tiff,
)
from scripts.build_site_neworleans_egis_card import ANCHOR, build as build_card


def make_tiff(values, grid):
    xmin, ymin, xmax, ymax = grid["bbox_3857"]
    transform = rasterio.transform.from_bounds(
        xmin, ymin, xmax, ymax, grid["width"], grid["height"]
    )
    with MemoryFile() as memory:
        with memory.open(
            driver="GTiff", width=grid["width"], height=grid["height"], count=1,
            dtype="uint8", crs="EPSG:3857", transform=transform,
        ) as dataset:
            dataset.write(np.asarray(values, dtype="uint8").reshape(
                grid["height"], grid["width"]
            ), 1)
        return memory.read()


def test_projected_grid_is_deterministic_and_approximately_30m():
    box = (-90.2, 29.8, -89.9, 30.1)
    first = projected_grid(box)
    assert first == projected_grid(box)
    assert first["width"] > 0 and first["height"] > 0
    assert first["target_resolution_m"] == pytest.approx(29.976, abs=0.001)
    xmin, ymin, xmax, ymax = first["bbox_3857"]
    assert xmin < xmax and ymin < ymax


def test_export_counts_only_bwtr_zero_and_one_as_valid():
    grid = {"bbox_3857": [0, 0, 4, 1], "width": 4, "height": 1}
    summary = summarize_tiff(make_tiff([0, 1, 255, 255], grid), grid)
    assert summary["class_counts"] == {"0": 1, "1": 1, "255": 2}
    assert summary["valid_bwtr_pixels"] == 2
    assert summary["valid_bwtr_fraction"] == 0.5


def test_export_rejects_unrecognized_bwtr_class():
    grid = {"bbox_3857": [0, 0, 3, 1], "width": 3, "height": 1}
    with pytest.raises(ValueError, match="Unrecognized BWTR classes"):
        summarize_tiff(make_tiff([0, 1, 42], grid), grid)


def test_audit_keeps_catalog_intersection_separate_from_valid_pixels(tmp_path):
    register = tmp_path / "register.json"
    register.write_text(json.dumps({"results": [{
        "city": "New Orleans", "region": "United States", "lon": -90.0, "lat": 30.0,
        "aoi_bbox_wgs84": "-90.2,29.8,-89.8,30.2",
    }]}))
    grid = projected_grid((-90.2, 29.8, -89.8, 30.2))
    fake_tiff = make_tiff([255] * (grid["width"] * grid["height"]), grid)

    def fake_json(url, params):
        if url == SERVICE_URL:
            return {"description": "Response maps are preliminary and unvalidated."}
        if url.endswith("/query"):
            return {"features": [{
                "attributes": {"objectid": RASTER_ID, "name": RASTER_NAME,
                               "productname": "Binary Water (BWTR)", "category": 1},
                "geometry": {"rings": [[[-90.5, 29.5], [-89.5, 29.5],
                                          [-89.5, 30.5], [-90.5, 30.5],
                                          [-90.5, 29.5]]]},
            }]}
        if url.endswith("/exportImage"):
            assert json.loads(params["mosaicRule"])["lockRasterIds"] == [RASTER_ID]
            return {"href": "https://gis.earthdata.nasa.gov/fake.tif",
                    "width": int(params["size"].split(",")[0]),
                    "height": int(params["size"].split(",")[1])}
        if url.endswith("/identify"):
            return {"value": "NoData", "catalogItems": {"features": [
                {"attributes": {"objectid": RASTER_ID}},
            ]}}
        raise AssertionError(url)

    report = audit(fake_json, lambda _href: fake_tiff, register)
    assert report["source"]["item"]["aoi_center_inside_catalog_footprint"] is True
    assert report["export"]["valid_bwtr_pixels"] == 0
    assert report["export"]["valid_bwtr_fraction"] == 0
    assert report["centre_point_crosscheck"]["value"] == "NoData"
    assert report["confirmatory_eligible"] is False
    assert "not evidence" in report["interpretation"]


def test_site_card_preserves_no_data_and_event_time_limits():
    report = {
        "source": {"item": {"object_id": 22}},
        "export": {"valid_bwtr_fraction": 0.0, "valid_bwtr_pixels": 0,
                   "pixel_count": 927369},
    }
    result = build_card(f"<section>{ANCHOR}</section>", report)
    assert "New Orleans · Louisiana flood BWTR fixed-box export" in result
    assert "0% valid BWTR · 0/927,369 cells" in result
    assert "Unknown is not dry" in result
    assert "preliminary and unvalidated" in result
    assert "pixel-specific times" in result
    assert build_card(result, report) == result
