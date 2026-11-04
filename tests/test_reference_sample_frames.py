import csv
import json
from pathlib import Path
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from scripts.build_reference_sample_frames import draw_frame
from scripts.build_reference_sample_frames import main as run_frame_cli
from scripts.audit_study_area_balance import expected_program


def _raster(path: Path, values: np.ndarray) -> None:
    with rasterio.open(path, "w", driver="GTiff", height=values.shape[0], width=values.shape[1],
                       count=1, dtype="uint8", crs="EPSG:32610",
                       transform=from_origin(500000, 4500000, 30, 30), nodata=255) as dst:
        dst.write(values.astype("uint8"), 1)


def _aoi(path: Path) -> None:
    geojson = {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[
        [500000, 4499820], [500180, 4499820], [500180, 4500000], [500000, 4500000], [500000, 4499820]
    ]]}}
    path.write_text(json.dumps(geojson))


def test_stratified_frame_is_reproducible_weighted_and_excludes_invalid(tmp_path):
    values = np.array([[0] * 6, [0] * 6, [0] * 6, [0] * 6, [0] * 6, [1, 1, 1, 1, 1, 255]], dtype="uint8")
    path = tmp_path / "event.tif"
    _raster(path, values)
    aoi = tmp_path / "aoi.geojson"
    _aoi(aoi)
    first, summary = draw_frame(path, aoi, aoi_crs="EPSG:32610", city="Houston", region="United States", period="event", target_n=10, seed=123)
    again, _ = draw_frame(path, aoi, aoi_crs="EPSG:32610", city="Houston", region="United States", period="event", target_n=10, seed=123)
    assert first == again
    assert len(first) == 10
    assert summary["strata_population"] == {"mapped_nonwater": 30, "mapped_water": 5}
    assert summary["strata_sample_n"] == {"mapped_nonwater": 8, "mapped_water": 2}
    assert {r["design_weight"] for r in first if r["map_stratum"] == "mapped_nonwater"} == {3.75}
    assert {r["design_weight"] for r in first if r["map_stratum"] == "mapped_water"} == {2.5}
    assert all(r["label_status"] == "pending_independent_interpretation" for r in first)
    assert all(r["reference_labeler_1"] == "" and r["adjudicated_label"] == "" for r in first)


def test_frame_rejects_nonprojected_and_non_30m_rasters(tmp_path):
    geographic = tmp_path / "geographic.tif"
    aoi = tmp_path / "aoi.geojson"
    _aoi(aoi)
    with rasterio.open(geographic, "w", driver="GTiff", height=2, width=2, count=1,
                       dtype="uint8", crs="EPSG:4326", transform=from_origin(0, 1, .001, .001)) as dst:
        dst.write(np.zeros((2, 2), dtype="uint8"), 1)
    with pytest.raises(ValueError, match="projected"):
        draw_frame(geographic, aoi, aoi_crs="EPSG:32610", city="Houston", region="United States", period="event", target_n=2, seed=1)


def test_frame_rejects_valid_pixels_outside_fixed_aoi(tmp_path):
    path = tmp_path / "event.tif"
    _raster(path, np.zeros((6, 6), dtype="uint8"))
    aoi = tmp_path / "partial-aoi.geojson"
    aoi.write_text(json.dumps({"type": "Feature", "properties": {}, "geometry": {
        "type": "Polygon", "coordinates": [[[500000, 4499910], [500180, 4499910],
            [500180, 4500000], [500000, 4500000], [500000, 4499910]]]}}))
    with pytest.raises(ValueError, match="outside the fixed AOI"):
        draw_frame(path, aoi, aoi_crs="EPSG:32610", city="Houston", region="United States",
                   period="event", target_n=4, seed=1)


def test_cli_requires_both_period_rasters_for_all_16(tmp_path, monkeypatch):
    areas = []
    values = np.array([[0, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 255], [0, 0, 0, 1]], dtype="uint8")
    for row in json.loads((Path(__file__).resolve().parents[1] / "data/study_area_register.json").read_text())["results"]:
        slug = row["city"].casefold().replace(" ", "_")
        folder = tmp_path / "input" / slug
        folder.mkdir(parents=True)
        area = {"city": row["city"], "region": row["region"]}
        aoi = folder / "aoi.geojson"
        _aoi(aoi)
        area.update({"aoi": f"input/{slug}/aoi.geojson", "aoi_crs": "EPSG:32610"})
        for period in ("event", "baseline"):
            raster_name = f"{period}.tif"
            _raster(folder / raster_name, values)
            area[f"{period}_sampling_raster"] = f"input/{slug}/{raster_name}"
        areas.append(area)
    package = tmp_path / "package.json"
    package.write_text(json.dumps({"study_areas": areas}))
    out = tmp_path / "frame"
    monkeypatch.setattr(sys, "argv", ["build_reference_sample_frames.py", "--study-package", str(package),
                                       "--output-dir", str(out), "--target-n", "4", "--seed", "123"])
    run_frame_cli()
    with (out / "reference_sample_frame.csv").open() as handle:
        records = list(csv.DictReader(handle))
    summary = json.loads((out / "reference_sample_frame_summary.json").read_text())
    assert len(records) == 128  # 4 units × 16 sites × two periods
    assert len(summary["area_periods"]) == 32
    assert summary["independent_reference_labels_created"] is False
    assert summary["confirmatory_enrollment_established"] is False
    assert {row["city"].casefold() for row in records} == set(expected_program())
