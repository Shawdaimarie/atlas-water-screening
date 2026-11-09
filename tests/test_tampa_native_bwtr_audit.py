import json
from pathlib import Path

import numpy as np
from rasterio.windows import Window

from scripts.audit_tampa_helene_raw_bwtr import _covering_window, _summarize_classes


ROOT = Path(__file__).resolve().parents[1]


def test_covering_window_encloses_fractional_bounds_and_margin():
    bounds = Window(10.25, 20.5, 3.25, 4.1)

    result = _covering_window(bounds, width=100, height=100)

    assert result.col_off == 9
    assert result.row_off == 19
    assert result.col_off <= bounds.col_off
    assert result.row_off <= bounds.row_off
    assert result.col_off + result.width >= bounds.col_off + bounds.width
    assert result.row_off + result.height >= bounds.row_off + bounds.height


def test_covering_window_clips_padding_to_raster_edges():
    result = _covering_window(Window(0.1, 0.2, 2.1, 2.2), width=10, height=10)

    assert result == Window(0, 0, 4, 4)


def test_class_summary_separates_valid_invalid_and_unexpected_classes():
    summary = _summarize_classes(np.array([0, 1, 1, 0, 250, 251, 255, 7], dtype=np.uint8))

    assert summary["aoi_pixel_count"] == 8
    assert summary["class_counts"] == {"0": 2, "1": 2, "7": 1, "250": 1, "251": 1, "255": 1}
    assert summary["valid_pixel_count"] == 4
    assert summary["invalid_pixel_count"] == 3
    assert summary["unexpected_class_counts"] == {"7": 1}
    assert summary["valid_fraction"] == 0.5
    assert summary["water_fraction_of_valid_pixels"] == 0.5
    assert not summary["passes_80_percent_valid_pixel_floor"]


def test_v70_site_bundle_matches_native_audit_artifact():
    audit = json.loads((ROOT / "dist/atlas-tampa-helene-native-bwtr-aoi-audit.json").read_text())
    page = (ROOT / "dist/index.html").read_text()

    assert len(audit["scenes"]) == 2
    assert all(scene["aoi_sampling"]["aoi_pixel_count"] == 497_316 for scene in audit["scenes"])
    assert all(scene["aoi_sampling"]["valid_fraction"] == 1.0 for scene in audit["scenes"])
    assert "Tampa · native OPERA BWTR pixels" in page
    assert "497,316 fixed-AOI pixels" in page
    assert "atlas-tampa-helene-native-bwtr-aoi-audit.json" in page
    assert (ROOT / "dist/atlas-tampa-helene-native-bwtr-aoi-audit.md").is_file()
