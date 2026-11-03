import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_earth_engine_audit_uses_all_registered_area_bounds():
    register = json.loads((ROOT / "data/study_area_register.json").read_text())
    source = (ROOT / "scripts/earthengine/atlas_opera_pixel_coverage.js").read_text()
    block = source.split("var rawAreas = [", 1)[1].split("];", 1)[0]
    matches = re.findall(
        r"\['([^']+)','([^']+)',(-?[\d.]+),(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)\]",
        block,
    )
    actual = {
        (region, city, ",".join((west, south, east, north)))
        for region, city, west, south, east, north in matches
    }
    expected = set()
    for area in register["results"]:
        expected.add((area["region"], area["city"], area["aoi_bbox_wgs84"]))
    assert len(matches) == 16
    assert len(expected) == 16
    assert actual == expected


def test_earth_engine_audit_uses_documented_binary_water_validity_gate():
    source = (ROOT / "scripts/earthengine/atlas_opera_pixel_coverage.js").read_text()
    assert "ee.ImageCollection('OPERA/DSWX/L3_V1/S1')" in source
    assert "bwtr.eq(0).or(bwtr.eq(1))" in source
    assert "bwtr.eq(250).or(bwtr.eq(251))" in source
    assert "MIN_VALID_AOI_FRACTION = 0.80" in source
    assert "MIN_DATES_PER_AREA = 90" in source
    assert "Export.table" not in source
