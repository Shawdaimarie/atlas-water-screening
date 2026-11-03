import json

import pytest

from scripts import audit_s1rtc_unique_pixel_coverage as unique


def orbit_item(month, day, orbit):
    stamp = f"2025-{month:02d}-{day:02d}T12:00:00Z"
    group = f"2025-{month:02d}-{day:02d}|sentinel-1a|ascending|{orbit}"
    return group, {
        "id": f"item-{month}-{day}-{orbit}",
        "properties": {"datetime": stamp, "platform": "sentinel-1a",
                       "sat:orbit_state": "ascending", "sat:absolute_orbit": orbit,
                       "sat:relative_orbit": 42},
        "assets": {"vv": {"href": "https://example.invalid/blob.tif",
                           "raster:bands": [{"nodata": -32768, "spatial_resolution": 10}],
                           "file:checksum": f"sha256:{orbit}", "file:size": 100}},
        "links": [{"rel": "self", "href": f"https://example.invalid/items/{orbit}"}],
    }


def record(group_id, quarter):
    day, platform, direction, orbit = group_id.split("|")
    return {"quarter": quarter, "date": day, "platform": platform,
            "orbit_state": direction, "relative_orbit": 42,
            "absolute_orbit": int(orbit), "valid_fraction": .9,
            "valid_pixels": 90, "aoi_pixels": 100,
            "items": [{"id": f"item-{orbit}", "asset_checksum": f"sha256:{orbit}"}]}


def test_quarter_replacement_is_deterministic_and_unique():
    groups = {}
    for month in (1, 2, 3):
        group, item = orbit_item(month, 1, month)
        groups[group] = [item]
    previous = [record("2025-01-01|sentinel-1a|ascending|1", 1) for _ in range(3)]

    first = unique.select_unique_quarter(groups, previous, "Houston", 1)
    second = unique.select_unique_quarter(groups, previous, "Houston", 1)

    assert [slot["group_id"] for slot in first] == [slot["group_id"] for slot in second]
    assert len({slot["group_id"] for slot in first}) == 3
    assert first[0]["origin"] == "prior_draw_1"
    assert [slot["origin"] for slot in first[1:]] == ["duplicate_replacement"] * 2


def test_quarter_replacement_fails_when_three_distinct_groups_do_not_exist():
    group, item = orbit_item(1, 1, 1)
    previous = [record(group, 1)] * 3
    with pytest.raises(ValueError, match="cannot produce 3 unique samples"):
        unique.select_unique_quarter({group: [item]}, previous, "Houston", 1)


def test_full_report_preserves_8_plus_8_and_emits_192_distinct_groups(tmp_path, monkeypatch):
    register_path = unique.REGISTER
    register = json.loads(register_path.read_text())
    candidate_items = []
    groups_by_quarter = {}
    for quarter, months in enumerate(((1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)), start=1):
        groups_by_quarter[quarter] = []
        for day, month in enumerate(months, start=1):
            group, item = orbit_item(month, day, quarter * 100 + month)
            candidate_items.append(item)
            groups_by_quarter[quarter].append(group)

    areas = register["results"]
    reports = []
    input_paths = []
    for _ in range(3):
        rows = []
        for area in areas:
            quarters = []
            for quarter in range(1, 5):
                first_group = groups_by_quarter[quarter][0]
                quarters.append(record(first_group, quarter))
            rows.append({"city": area["city"], "region": area["region"],
                         "quarter_results": quarters})
        reports.append({"source": {"collection": "fixture"}, "period": {"start": "2025-01-01"},
                        "pixel_coverage_screen": {"sample_seed": "fixture"}, "areas": rows})
    for index, report in enumerate(reports):
        path = tmp_path / f"input-{index}.json"
        path.write_text(json.dumps(report))
        input_paths.append(path)

    monkeypatch.setattr(unique.source, "_items_for_area", lambda bbox: candidate_items)
    monkeypatch.setattr(unique.source, "_pixel_fraction_for_group", lambda selected, bbox: (.91, 91, 100))
    output_path = tmp_path / "unique.json"
    result = unique.run(register_path, input_paths, output_path, tmp_path / "checkpoint.json")

    assert result["summary"]["selected_area_orbit_groups"] == 192
    assert result["summary"]["unique_area_orbit_groups"] == 192
    assert result["summary"]["duplicate_selections"] == 0
    assert result["summary"]["retained_prior"] == 64
    assert result["summary"]["replacement_unique_groups"] == 128
    assert result["summary"]["areas_passing_all_12_samples"] == 16
    assert sum(row["region"] == "United States" for row in result["areas"]) == 8
    assert sum(row["region"] == "International" for row in result["areas"]) == 8
    assert len(json.loads(output_path.read_text())["areas"]) == 16
