import json
from urllib.parse import urlsplit

from scripts import audit_s1rtc_pixel_coverage as audit


def item(stamp, orbit, *, platform="sentinel-1a", with_vv=True):
    value = {
        "id": f"item-{stamp}-{orbit}-{platform}",
        "properties": {"datetime": stamp, "platform": platform,
                       "sat:orbit_state": "descending", "sat:absolute_orbit": orbit,
                       "sat:relative_orbit": 42},
        "assets": {"vv": {"href": "https://example.invalid/blob.tif", "file:checksum": "sha256:fixture"}},
        "links": [{"rel": "self", "href": "https://example.invalid/items/fixture"}],
    }
    if not with_vv:
        value["assets"] = {}
    return value


def test_orbit_groups_require_datetime_orbit_platform_and_vv():
    good = item("2025-03-01T00:02:00Z", 100)
    no_band = item("2025-03-02T00:02:00Z", 101, with_vv=False)
    no_orbit = item("2025-03-03T00:02:00Z", None)
    groups = audit._orbit_groups([good, no_band, no_orbit])
    assert list(groups) == ["2025-03-01|sentinel-1a|descending|100"]
    assert groups["2025-03-01|sentinel-1a|descending|100"] == [good]


def test_quarter_selection_is_repeatable_and_uniformly_one_group_per_quarter():
    groups = {}
    for quarter, month in enumerate((2, 5, 8, 11), start=1):
        for day in range(1, 5):
            stamp = f"2025-{month:02d}-{day:02d}T12:00:00Z"
            groups.update(audit._orbit_groups([item(stamp, month * 100 + day)]))
    selected_a = audit.select_quarterly_groups(groups, "Houston")
    selected_b = audit.select_quarterly_groups(groups, "Houston")
    selected_replicate = audit.select_quarterly_groups(groups, "Houston", "ATLAS-S1RTC-quarterly-coverage-replicate-2")
    assert [x["group_id"] for x in selected_a] == [x["group_id"] for x in selected_b]
    assert [x["group_id"] for x in selected_a] != [x["group_id"] for x in selected_replicate]
    assert [x["quarter"] for x in selected_a] == [1, 2, 3, 4]
    assert all(x["candidate_orbit_groups"] == 4 for x in selected_a)
    assert all(len(x["items"]) == 1 for x in selected_a)


def test_asset_token_is_cached_per_storage_container_and_never_stored_in_path(monkeypatch):
    audit._SAS_TOKENS.clear()
    calls = []
    monkeypatch.setattr(audit, "_request_json", lambda url: calls.append(url) or {"token": "se=temporary&sp=rl&sig=secret"})
    href = "https://dataaccount.blob.core.windows.net/rtc-container/path/item.tif"
    signed = audit._sign_asset(href)
    audit._sign_asset("https://dataaccount.blob.core.windows.net/rtc-container/path/second.tif")
    parsed = urlsplit(signed)
    assert len(calls) == 1
    assert calls[0].endswith("/dataaccount/rtc-container")
    assert parsed.path.endswith("/item.tif")
    assert "sig=secret" in parsed.query
    audit._SAS_TOKENS.clear()


def test_run_records_uniform_16_area_pixel_sample_and_limitations(tmp_path, monkeypatch):
    register = json.loads((audit.Path(__file__).parents[1] / "data/study_area_register.json").read_text())
    groups = {}
    for q, month in enumerate((2, 5, 8, 11), start=1):
        groups.update(audit._orbit_groups([item(f"2025-{month:02d}-01T12:00:00Z", q * 100)]))
    monkeypatch.setattr(audit, "_items_for_area", lambda bbox: [x[0] for x in groups.values()])
    monkeypatch.setattr(audit, "_pixel_fraction_for_group", lambda selected, bbox: (0.9, 90, 100))
    output = tmp_path / "coverage.json"
    result = audit.run(audit.Path(__file__).parents[1] / "data/study_area_register.json", output,
                       tmp_path / "checkpoint.json", "test-replicate-seed")
    assert len(result["areas"]) == 16
    assert result["summary"]["us_areas"] == 8
    assert result["summary"]["international_areas"] == 8
    assert result["summary"]["areas_with_all_four_sample_quarters_above_80pct"] == 16
    assert all(len(area["quarter_results"]) == 4 for area in result["areas"])
    assert all(area["quarter_results"][0]["items"][0]["item_url"].startswith("https://example.invalid")
               for area in result["areas"])
    assert "SAS" in result["interpretation_limits"][-1]
    assert result["pixel_coverage_screen"]["sample_seed"] == "test-replicate-seed"
    written = json.loads(output.read_text())
    assert written["summary"] == result["summary"]
