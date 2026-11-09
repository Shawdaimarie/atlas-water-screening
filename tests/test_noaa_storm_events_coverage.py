from scripts.audit_noaa_storm_events_coverage import flood_event_type, point_in_bbox


def test_bbox_uses_longitude_latitude_order_and_includes_boundary():
    bbox = (-95.5, 29.6, -95.2, 29.9)
    assert point_in_bbox(-95.5, 29.6, bbox)
    assert point_in_bbox(-95.35, 29.75, bbox)
    assert not point_in_bbox(29.75, -95.35, bbox)
    assert not point_in_bbox(-95.51, 29.75, bbox)


def test_event_type_screen_includes_flood_variants_only():
    assert flood_event_type("Flood")
    assert flood_event_type("Flash Flood")
    assert flood_event_type("Coastal Flood")
    assert not flood_event_type("Heavy Rain")
    assert not flood_event_type("Thunderstorm Wind")
