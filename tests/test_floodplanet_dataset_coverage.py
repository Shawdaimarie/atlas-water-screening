from pathlib import Path
import json

from scripts.audit_floodplanet_dataset_coverage import area_key, read_areas


def test_floodplanet_screen_uses_the_full_fixed_8_plus_8_register():
    areas = read_areas(Path("data/study_area_register.json"))
    assert len(areas) == 16
    assert sum(area["region"] == "United States" for area in areas) == 8
    assert sum(area["region"] == "International" for area in areas) == 8
    assert area_key(areas[0]) == "United States/Houston"


def test_saved_floodplanet_audit_records_all_items_and_zero_fixed_aoi_overlaps():
    result = json.loads(Path("outputs/atlas-floodplanet-coverage-audit.json").read_text())
    assert result["stac_label_item_count"] == 366
    assert result["successfully_inspected_item_count"] == 366
    assert result["event_group_count"] == 19
    assert result["processing_errors"] == []
    assert result["overlapping_area_count"] == 0
    assert len(result["registered_areas"]) == 16
