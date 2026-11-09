import json

from scripts import audit_gfm_temporal_coverage as audit
from scripts.audit_gfm_temporal_coverage import _load_completed, _period_summary, _target_dates


def test_target_dates_selects_nearest_three_unique_pre_and_post_dates():
    result = _target_dates({
        "pre_event_30d_product_dates": ["2025-01-01", "2025-01-03", "2025-01-03", "2025-01-05"],
        "product_dates_within_reported_event_interval": ["2025-01-06", "2025-01-07"],
        "post_event_30d_product_dates": ["2025-01-10", "2025-01-12", "2025-01-14", "2025-01-15"],
    })
    assert result == {
        "pre_event_30d": ["2025-01-01", "2025-01-03", "2025-01-05"],
        "candidate_event": ["2025-01-06", "2025-01-07"],
        "post_event_30d": ["2025-01-10", "2025-01-12", "2025-01-14"],
    }


def test_target_dates_uses_single_day_interval_as_candidate_event_fallback():
    result = _target_dates({
        "pre_event_30d_product_dates": [],
        "post_event_30d_product_dates": [],
        "reported_start_date": "2025-02-01",
        "reported_end_date": "2025-02-01",
    })
    assert result["candidate_event"] == ["2025-02-01"]


def test_period_summary_requires_three_readable_dates_at_eighty_percent():
    rows = [
        {"target_date": "2025-01-01", "best_coverage_item": {"valid_fraction": 0.8}},
        {"target_date": "2025-01-07", "best_coverage_item": {"valid_fraction": 0.95}},
        {"target_date": "2025-01-13", "best_coverage_item": {"valid_fraction": 0.79}},
        {"target_date": "2025-01-19", "best_coverage_item": None},
    ]
    result = _period_summary(rows)
    assert result["date_slots"] == 4
    assert result["readable_rasters"] == 3
    assert result["rasters_at_or_above_80_percent"] == 2
    assert result["meets_three_date_80_percent_screen"] is False


def test_period_summary_passes_three_date_floor_only_with_three_passing_rasters():
    rows = [
        {"target_date": date, "best_coverage_item": {"valid_fraction": fraction}}
        for date, fraction in [("a", 0.8), ("b", 0.81), ("c", 1.0)]
    ]
    assert _period_summary(rows)["meets_three_date_80_percent_screen"] is True


def test_resume_reuses_area_results_only_when_input_hashes_match(tmp_path):
    output = tmp_path / "audit.json"
    output.write_text(json.dumps({
        "input_sha256": {"register.json": "register-hash", "leads.json": "lead-hash"},
        "areas": [{"city": "Houston"}],
    }))
    expected = {"register.json": "register-hash", "leads.json": "lead-hash"}
    assert list(_load_completed(output, expected)) == ["Houston"]
    assert _load_completed(output, {**expected, "gfm.json": "changed-cache"}) == {}


def test_reused_raster_cache_is_bound_to_same_aoi(monkeypatch):
    city, date = "Houston", "2025-05-19"
    box = [-95.5, 29.6, -95.2, 29.9]
    item = {"id": "pinned-item", "valid_fraction": 0.95}
    cache = {(city, date): {"bbox_wgs84": box, "item": item}}
    result = audit._measure_day(city, box, date, cache)
    assert result["best_coverage_item"] == item
    assert "reused prior audit" in result["status"]

    def fail_if_read(_):
        raise AssertionError("stale AOI cache should trigger a fresh catalog read")

    monkeypatch.setattr(audit, "search_all", fail_if_read)
    try:
        audit._measure_day(city, [-95.4, 29.6, -95.1, 29.9], date, cache)
    except AssertionError as exc:
        assert "fresh catalog read" in str(exc)
    else:
        raise AssertionError("the wrong-AOI cached raster was reused")
