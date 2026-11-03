from scripts.audit_c2s_flood_dataset import area_geometry, parse_label_key


def test_parse_c2s_s1_label_key():
    event, scene, date = parse_label_key(
        "c2smsfloods/chips/4567c2a2-b5f3-4a88-90ba-119bfb3eee9e/s1/"
        "S1B_IW_GRDH_1SDV_20170830T122203_20170830T122232_007169_00CA2C_"
        "E7BF_08192-01536/LabelWater.tif"
    )
    assert event == "4567c2a2-b5f3-4a88-90ba-119bfb3eee9e"
    assert scene.endswith("08192-01536")
    assert date == "2017-08-30"


def test_area_geometry_uses_registered_aoi_bounds():
    polygon = area_geometry({"aoi_bbox_wgs84": "-96,29,-95,30"})
    assert polygon == {
        "type": "Polygon",
        "coordinates": [[[-96, 29], [-95, 29], [-95, 30], [-96, 30], [-96, 29]]],
    }
