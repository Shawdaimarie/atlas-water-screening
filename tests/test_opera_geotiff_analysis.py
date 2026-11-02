import csv
import json
from pathlib import Path

import pytest

rasterio = pytest.importorskip("rasterio")
import numpy as np
from rasterio.transform import from_origin

from scripts.analyze_opera_geotiffs import _metrics, analyze


def _polygon(x0, y0, x1, y1):
    return {"type": "Polygon", "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]}


def test_real_format_wtr_qa_and_matched_event_baseline_dates(tmp_path):
    aoi = {"type": "Feature", "properties": {}, "geometry": _polygon(0, 0, 120, 120)}
    assets = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"asset_id": "left", "asset_name": "Left asset"}, "geometry": _polygon(1, 1, 59, 119)},
        {"type": "Feature", "properties": {"asset_id": "right", "asset_name": "Right asset"}, "geometry": _polygon(61, 1, 119, 119)},
    ]}
    (tmp_path / "aoi.json").write_text(json.dumps(aoi))
    (tmp_path / "assets.json").write_text(json.dumps(assets))

    rows = []
    for period, dates in (("baseline", ["2025-01-01", "2025-01-07", "2025-01-13"]),
                          ("event", ["2025-02-01", "2025-02-07", "2025-02-13"])):
        for index, acquired in enumerate(dates):
            values = np.zeros((4, 4), dtype="uint8") if period == "baseline" else np.ones((4, 4), dtype="uint8")
            if period == "event" and index == 0:
                values[0, 2], values[1, 2], values[2, 2] = 250, 251, 255
            name = f"{period}-{index}.tif"
            with rasterio.open(tmp_path / name, "w", driver="GTiff", height=4, width=4,
                               count=1, dtype="uint8", crs="EPSG:32631",
                               transform=from_origin(0, 120, 30, 30)) as dst:
                dst.write(values, 1)
            rows.append({"path": name, "acquired_at": acquired,
                         "selection_anchor": "2025-01-07" if period == "baseline" else "2025-02-07",
                         "period": period,
                         "granule_id": name, "product_version": "OPERA_L3_DSWX-S1_V1",
                         "processing_version": "1.0.0", "retrieved_at": "2025-03-01T12:00:00Z"})
    with (tmp_path / "manifest.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

    observation_rows, comparisons = analyze(tmp_path / "manifest.csv", tmp_path / "aoi.json",
                                             tmp_path / "assets.json", aoi_crs="EPSG:32631",
                                             assets_crs="EPSG:32631", min_dates=3)
    by_id = {row["asset_id"]: row for row in comparisons}
    assert by_id["left"]["status"] == "candidate_coverage_pass"
    assert by_id["left"]["matched_dates_per_period"] == 3
    assert by_id["left"]["baseline_mean_water_fraction"] == 0.0
    assert by_id["left"]["event_mean_water_fraction"] == 1.0
    assert by_id["left"]["water_fraction_difference"] == 1.0
    assert by_id["right"]["status"] == "unknown_insufficient_qa_valid_dates"
    assert by_id["right"]["event_qa_valid_dates"] == 2
    assert len(observation_rows) == 12


def test_wtr_class_semantics_and_unknown_class_detection():
    values = np.array([[0, 1, 3, 250, 251, 255, 2]], dtype="uint8")
    selected = np.ones(values.shape, dtype=bool)
    result = _metrics(values, selected)
    assert result["valid_pixels"] == 3
    assert result["water_pixels"] == 2
    assert result["water_fraction_valid"] == pytest.approx(2 / 3)
    assert result["unexpected_classes"] == 1


def test_duplicate_dates_fail_closed(tmp_path):
    aoi = {"type": "Feature", "properties": {}, "geometry": _polygon(0, 0, 60, 60)}
    assets = {"type": "Feature", "properties": {"asset_id": "x"}, "geometry": _polygon(0, 0, 30, 60)}
    (tmp_path / "aoi.json").write_text(json.dumps(aoi))
    (tmp_path / "assets.json").write_text(json.dumps(assets))
    rows = []
    for i in (1, 2):
        name = f"{i}.tif"
        (tmp_path / name).touch()
        rows.append({"path": name, "acquired_at": "2025-01-01", "selection_anchor": "2025-01-01", "period": "baseline",
                     "granule_id": name, "product_version": "OPERA_L3_DSWX-S1_V1",
                     "processing_version": "1.0.0", "retrieved_at": "2025-03-01T12:00:00Z"})
    with (tmp_path / "manifest.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    with pytest.raises(ValueError, match="Duplicate acquisition date"):
        analyze(tmp_path / "manifest.csv", tmp_path / "aoi.json", tmp_path / "assets.json")


def test_non_pinned_product_fails_closed(tmp_path):
    aoi = {"type": "Feature", "properties": {}, "geometry": _polygon(0, 0, 60, 60)}
    assets = {"type": "Feature", "properties": {"asset_id": "x"}, "geometry": _polygon(0, 0, 30, 60)}
    (tmp_path / "aoi.json").write_text(json.dumps(aoi))
    (tmp_path / "assets.json").write_text(json.dumps(assets))
    (tmp_path / "1.tif").touch()
    row = {"path": "1.tif", "acquired_at": "2025-01-01", "selection_anchor": "2025-01-01", "period": "baseline",
           "granule_id": "1", "product_version": "OPERA_L3_DSWX-S1_V2",
           "processing_version": "1.0.0", "retrieved_at": "2025-03-01T12:00:00Z"}
    with (tmp_path / "manifest.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader(); writer.writerow(row)
    with pytest.raises(ValueError, match="Expected pinned product"):
        analyze(tmp_path / "manifest.csv", tmp_path / "aoi.json", tmp_path / "assets.json")
