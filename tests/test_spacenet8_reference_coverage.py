import pytest
from shapely.geometry import box

from scripts.audit_spacenet8_reference_coverage import flood_label, parse_bbox, screen_features
from scripts.build_site_spacenet8_reference_card import render_card


def test_spacenet8_screen_counts_intersecting_buildings_and_roads():
    area = box(-91, 29, -90, 30)
    geojson = {
        "features": [
            {
                "properties": {"id": "building-1", "building": "yes", "flooded": "yes"},
                "geometry": {"type": "Point", "coordinates": [-90.5, 29.5]},
            },
            {
                "properties": {"id": "road-1", "highway": "primary", "flooded": False},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-90.7, 29.5], [-89.8, 29.5]],
                },
            },
            {
                "properties": {"id": "outside", "building": "yes", "flooded": True},
                "geometry": {"type": "Point", "coordinates": [-89.5, 29.5]},
            },
            {
                "properties": {"id": "unknown-1", "flooded": None},
                "geometry": {"type": "Point", "coordinates": [-90.5, 29.5]},
            },
        ]
    }

    result = screen_features(geojson, area)

    assert result["features_intersecting"] == 3
    assert result["unique_feature_ids"] == 3
    assert result["flooded"] == 1
    assert result["not_flooded"] == 1
    assert result["flood_status_unknown"] == 1
    assert result["buildings"] == 1
    assert result["roads"] == 1
    assert result["other"] == 1


def test_spacenet8_screen_deduplicates_repeated_feature_id():
    area = box(-91, 29, -90, 30)
    feature = {
        "properties": {"id": "road-1", "highway": "primary", "flooded": False},
        "geometry": {
            "type": "LineString",
            "coordinates": [[-90.7, 29.5], [-90.6, 29.5]],
        },
    }

    result = screen_features({"features": [feature, feature]}, area)

    assert result["features_intersecting"] == 2
    assert result["unique_feature_ids"] == 1
    assert result["roads"] == 1
    assert result["not_flooded"] == 1


def test_spacenet8_bbox_requires_valid_wgs84_order():
    assert parse_bbox("-91,29,-90,30").bounds == (-91, 29, -90, 30)
    with pytest.raises(ValueError):
        parse_bbox("-90,30,-91,29")


def test_spacenet8_flood_flag_keeps_null_as_unknown():
    assert flood_label("yes") is True
    assert flood_label("no") is False
    assert flood_label(None) is None


def test_site_card_requires_unknown_labels_to_remain_unknown():
    report = {
        "summary": {
            "areas_with_annotation_overlap": 1,
            "candidate_areas_with_overlap": ["New Orleans"],
        },
        "results": {
            "New Orleans": {
                "annotation_files_intersecting": 160,
                "unique_feature_totals": {
                    "unique_feature_ids": 4500,
                    "flooded": 14,
                    "flood_status_unknown": 4486,
                    "not_flooded": 0,
                },
            }
        },
    }

    card = render_card(report)

    assert "14 have source label" in card
    assert "4,486 null flood states remain unknown" in card
    assert "pixel water mask" in card
