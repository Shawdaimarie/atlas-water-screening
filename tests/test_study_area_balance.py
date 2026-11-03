import json
import csv
from pathlib import Path
import sys

import pytest

from scripts.audit_study_area_balance import expected_program, global_balance
from scripts.audit_study_area_balance import main as run_balanced_cli
import rasterio
import numpy as np
from rasterio.transform import from_origin


def _areas():
    register = json.loads((Path(__file__).resolve().parents[1] / "data/study_area_register.json").read_text())
    return [{"city": row["city"], "region": row["region"]} for row in register["results"]]


def _rows(area_index, event_count=3):
    result = []
    for period, dates, anchor in (
        ("baseline", ["2025-01-01", "2025-01-07", "2025-01-13"], "2025-01-07"),
        ("event", ["2025-02-01", "2025-02-07", "2025-02-13"][:event_count], "2025-02-07"),
    ):
        for index, acquired in enumerate(dates):
            result.append({
                "asset_id": f"asset-{area_index}", "asset_name": "Fixture asset",
                "period": period, "acquired_at": acquired, "selection_anchor": anchor,
                "granule_id": f"{area_index}-{period}-{index}", "candidate_observation": True,
                "asset_water_fraction_valid": 0.6 if period == "event" else 0.1,
                "product_version": "OPERA_L3_DSWX-S1_V1", "processing_version": "1.0.0",
                "product_doi": "https://doi.org/10.5067/OPDSWS1-L3V1",
                "source_sha256": f"checksum-{area_index}-{period}-{index}",
                "analysis_code_sha256": "script-checksum",
            })
    return result


def test_full_16_area_balance_uses_one_global_count_and_anchor_rule():
    areas = _areas()
    observations = {a["city"]: _rows(i) for i, a in enumerate(areas)}
    availability, comparisons = global_balance(areas, observations, min_dates=3)
    assert len(availability) == 16
    assert len(comparisons) == 16
    assert {r["global_matched_dates_per_period"] for r in availability} == {3}
    assert all(r["status"] == "globally_balanced_candidate" for r in comparisons)
    assert all(r["water_fraction_difference"] == 0.5 for r in comparisons)
    assert all(len(r["event_selected_dates"].split(";")) == 3 for r in comparisons)


def test_one_undercovered_area_blocks_balanced_claim_for_all_16():
    areas = _areas()
    observations = {a["city"]: _rows(i, event_count=2 if i == 7 else 3) for i, a in enumerate(areas)}
    availability, comparisons = global_balance(areas, observations, min_dates=3)
    assert {r["global_status"] for r in availability} == {"insufficient_global_qa_valid_coverage"}
    assert {r["global_matched_dates_per_period"] for r in availability} == {0}
    assert all(r["water_fraction_difference"] is None for r in comparisons)


def test_rejects_missing_or_misclassified_study_area():
    areas = _areas()[:-1]
    with pytest.raises(ValueError, match="all 16"):
        global_balance(areas, {}, min_dates=3)
    areas = _areas()
    areas[0] = {**areas[0], "region": "International"}
    with pytest.raises(ValueError, match="Region classification mismatch"):
        global_balance(areas, {}, min_dates=3)


@pytest.mark.filterwarnings("ignore:Use @ matmul instead of .*:PendingDeprecationWarning")
def test_16_area_package_cli_writes_balanced_results_and_provenance(tmp_path, monkeypatch):
    area_entries = []
    for index, area in enumerate(_areas()):
        slug = area["city"].lower().replace(" ", "_")
        folder = tmp_path / "input_data" / slug
        folder.mkdir(parents=True)
        aoi = {"type": "Feature", "properties": {}, "geometry": {
            "type": "Polygon", "coordinates": [[[0, 0], [120, 0], [120, 120], [0, 120], [0, 0]]]}}
        assets = {"type": "FeatureCollection", "features": [{"type": "Feature",
            "properties": {"asset_id": f"asset-{index}", "asset_name": "Fixture asset"},
            "geometry": aoi["geometry"]}]}
        (folder / "aoi.json").write_text(json.dumps(aoi))
        (folder / "assets.json").write_text(json.dumps(assets))
        manifest_rows = []
        for period, dates, anchor, value in (
            ("baseline", ["2025-01-01", "2025-01-07", "