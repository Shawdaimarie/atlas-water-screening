import json
from pathlib import Path

from scripts.build_reference_readiness_ledger import build_ledger, render_card


def test_reference_readiness_ledger_balances_all_areas_and_preserves_unknowns():
    ledger = build_ledger()
    assert len(ledger["areas"]) == 16
    assert ledger["summary"]["us_areas"] == 8
    assert ledger["summary"]["international_areas"] == 8
    assert ledger["summary"]["confirmatory_areas_eligible"] == 0
    assert ledger["summary"]["rtc_groups_passing_80pct"] == 169
    assert ledger["summary"]["rtc_groups_sampled"] == 192
    assert ledger["summary"]["rtc_unique_area_orbit_groups"] == 192
    assert ledger["summary"]["rtc_duplicate_selections"] == 0
    assert ledger["summary"]["areas_passing_all_12_rtc_samples"] == 10
    new_orleans = next(x for x in ledger["areas"] if x["city"] == "New Orleans")
    assert new_orleans["spacenet8_flooded_yes_objects"] == 14
    assert new_orleans["spacenet8_unknown_flood_status_objects"] == 4486
    assert new_orleans["spacenet8_unique_object_references"] == 4500


def test_reference_ledger_hashes_the_register_that_defines_its_area_rows():
    ledger = build_ledger()
    root = Path(__file__).resolve().parents[1]
    import hashlib

    expected = hashlib.sha256((root / "data/study_area_register.json").read_bytes()).hexdigest()
    assert ledger["input_sha256"]["data/study_area_register.json"] == expected


def test_reference_ledger_card_reports_limits_and_both_downloads():
    html = render_card(build_ledger())
    assert "0/16 confirmatory sites eligible" in html
    assert "atlas-reference-readiness-ledger.json" in html
    assert "atlas-reference-readiness-ledger.csv" in html
    assert "do not establish comparable flood labels" in html
    assert "169/192 distinct RTC groups" in html


def test_generated_reference_ledger_matches_current_source_snapshot():
    root = Path(__file__).resolve().parents[1]
    expected = build_ledger()
    on_disk = json.loads((root / "outputs/atlas-reference-readiness-ledger.json").read_text())
    assert on_disk == expected
    assert (root / "dist/atlas-reference-readiness-ledger.json").read_bytes() == (root / "outputs/atlas-reference-readiness-ledger.json").read_bytes()
    assert (root / "dist/atlas-reference-readiness-ledger.csv").exists()
    assert "GENERATED REFERENCE READINESS LEDGER START" in (root / "dist/index.html").read_text()
