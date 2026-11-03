from scripts.audit_ufo_dataset_coverage import approximate_area_km2, clip_polygon_to_bbox


def test_clip_polygon_to_bbox_preserves_overlap():
    polygon = [[-2, -2], [2, -2], [2, 2], [-2, 2], [-2, -2]]
    clipped = clip_polygon_to_bbox(polygon, (-1, -1, 1, 1))
    assert len(clipped) == 4
    assert approximate_area_km2(clipped) > 48_000


def test_clip_polygon_to_bbox_returns_empty_for_disjoint_polygon():
    polygon = [[-2, -2], [-1, -2], [-1, -1], [-2, -1], [-2, -2]]
    assert clip_polygon_to_bbox(polygon, (1, 1, 2, 2)) == []
    assert approximate_area_km2([]) == 0
