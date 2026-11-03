import json
from pathlib import Path

from scripts.audit_sen1floods11_coverage import boxes_intersect


ROOT = Path(__file__).resolve().parents[1]


def test_sen1floods11_bbox_intersection_requires_positive_area():
    aoi = [-96.0, 29.0, -95.0, 30.0]
    assert boxes_intersect([-95.5, 29.5, -95.4, 29.6], aoi)
    assert not boxes_intersect([-95.0, 29.2, -94.9, 29.3], aoi)
    assert not boxes_intersect([-96.2, 30.1, -96.1, 30.2], aoi)


def test_sen1floods11_saved_audit_covers_all_label_items_and_all_areas():
    report = json.loads((ROOT / "outputs/atlas-sen1floods11-label-footprint-audit.json").read_text())
    assert report["source"]["catalog_objects_listed"] == 447
    assert report["source"]["hand_labeled_chip_items"] == 446
    assert len(report["catalog_items"]) == 446
    assert report["summary"] == {
        "areas": 16,
        "us_areas": 8,
        "international_areas": 8,
        "areas_with_label_chip_overlap": 0,
        "label_chip_footprint_overlaps": 0,
    }
    assert all(area["hand_labeled_chip_footprints_intersecting"] == 0 for area in report["areas"])
