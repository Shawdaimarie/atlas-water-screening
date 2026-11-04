import json

from scripts import audit_s1rtc_valid_quota as quota


def _item(month, quarter, orbit):
    day = 1
    group = f"2025-{month:02d}-{day:02d}|sentinel-1a|ascending|{orbit}"
    return group, {
        "id": f"item-{orbit}",
        "properties": {"datetime": f"2025-{month:02d}-{day:02d}T12:00:00Z",
                       "platform": "sentinel-1a", "sat:orbit_state": "ascending",
                       "sat:absolute_orbit": orbit, "sat:relative_orbit": 42},
        "assets": {"vv": {"href": "https://example.invalid/raster.tif",
                           "raster:bands": [{"nodata": -32768, "spatial_resolution": 10}],
                           "file:checksum": f"sha256:{orbit}", "file:size": 100}},
        "links": [{"rel": "self", "href": f"https://example.invalid/items/{orbit}"}],
    }


def _record(group, quarter, fraction):
    date, platform, direction, orbit = group.split("|")
    return {"quarter": quarter, "date": date, "platform": platform,
            "orbit_state": direction, "relative_orbit": 42,
            "absolute_orbit": int(orbit), "valid_fraction": fraction,
            "valid_pixels": int(100 * fraction), "aoi_pixels": 100,
            "items": [{"id": f"item-{orbit}", "asset_checksum": f"sha256:{orbit}"}]}


def _fixture(tmp_path):
    register = json.loads(quota.REGISTER.read_text())
    groups = []
    by_quarter = {}
    for quarter, months in enumerate(((1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)), 1):
        by_quarter[quarter] = []
        for slot, month in enumerate((*months, months[-1], months[-1]), 1):
            orbit = 100 * quarter + slot
            group, item = _item(month, quarter, orbit)
            groups.append(item)
            by_quarter[quarter].append(group)
    input_areas = []
    for area in register["results"]:
        quarters = []
        for quarter in range(1, 5):
            # The first sample passes; the next two fail. The fourth candidate
            # is a pass, and the third candidate is also screened if needed.
            fractions = (0.9, 0.4, 0.5)
            quarters.append({"quarter": quarter, "samples": [
                _record(group, quarter, fraction)
                for group, fraction in zip(by_quarter[quarter][:3], fractions)
            ]})
        input_areas.append({"city": area["city"], "region": area["region"],
                            "quarter_results": quarters})
    register_path = tmp_path / "register.json"
    register_path.write_text(json.dumps(register))
    input_path = tmp_path / "initial.json"
    input_path.write_text(json.dumps({"areas": input_areas}))
    return register, groups, by_quarter, register_path, input_path


def test_matched_quota_keeps_initial_passes_and_screened_replacements(tmp_path, monkeypatch):
    register, groups, by_quarter, register_path, input_path = _fixture(tmp_path)
    fractions = {int(item["properties"]["sat:absolute_orbit"]):
                 (0.95 if int(item["properties"]["sat:absolute_orbit"]) % 100 in {4, 5} else 0.85)
                 for item in groups}
    # One extra available group per quarter lets each stratum reach 3 valid.
    monkeypatch.setattr(quota.source, "_items_for_area", lambda bbox: groups)
    monkeypatch.setattr(quota.source, "_pixel_fraction_for_group",
                        lambda items, bbox: (fractions[int(items[0]["properties"]["sat:absolute_orbit"])], 90, 100))
    output = tmp_path / "quota.json"
    result = quota.run(register_path, input_path, output, tmp_path / "checkpoint.json")

    assert result["summary"]["areas_meeting_12_group_quota"] == 16
    assert result["summary"]["valid_groups_selected"] == 192
    assert result["summary"]["target_valid_groups"] == 192
    assert all(row["all_quarter_quotas_met"] for row in result["areas"])
    assert all(len(q["samples"]) == 3 for row in result["areas"] for q in row["quarter_results"])
    assert all(s["valid_fraction"] >= 0.8 for row in result["areas"]
               for q in row["quarter_results"] for s in q["samples"])
    assert len(json.loads(output.read_text())["areas"]) == 16


def test_matched_quota_reports_candidate_pool_exhaustion(tmp_path, monkeypatch):
    register, groups, by_quarter, register_path, input_path = _fixture(tmp_path)
    # No supplemental candidate clears the threshold.
    monkeypatch.setattr(quota.source, "_items_for_area", lambda bbox: groups)
    monkeypatch.setattr(quota.source, "_pixel_fraction_for_group", lambda items, bbox: (0.2, 20, 100))
    result = quota.run(register_path, input_path, tmp_path / "quota.json", tmp_path / "checkpoint.json")

    assert result["summary"]["areas_meeting_12_group_quota"] == 0
    assert result["summary"]["valid_groups_selected"] == 64
    assert all(q["selected_valid_groups"] == 1 for row in result["areas"] for q in row["quarter_results"])
    assert all(q["supplemental_groups_screened"] == 2 for row in result["areas"] for q in row["quarter_results"])
