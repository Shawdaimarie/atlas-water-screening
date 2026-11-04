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
    assert ledger["summary"]["rtc_matched_quota_groups_selected"] == 192
    assert ledger["summary"]["rtc_matched_quota_target_groups"] == 192
    assert ledger["summary"]["rtc_matched_quota_areas"] == 16
    assert ledger["summary"]["rtc_matched_quota_supplemental_groups_screened"] == 34
    new_orleans = next(x for x in ledger["areas"] if x["city"] == "New Orleans")
    assert new_orleans["spacenet8_flooded_yes_objects"] == 14
    assert new_orleans["spacenet8_unknown_flood_status_objects"] == 4486
    assert new_orleans["spacenet8_unique_object_references"] == 4500
    mumbai = next(x for x in ledger["areas"] if x["city"] == "Mumbai")
    assert mumbai["nrsc_official_map_documents"] == 2
    assert mumbai["nrsc_official_use_marked"] is True
    assert mumbai["nrsc_fixed_aoi_overlap_verified"] is False
    assert mumbai["nrsc_reuse_license_verified"] is False
    assert ledger["summary"]["areas_with_unverified_official_map_leads"] == 1
    assert ledger["summary"]["nrsc_official_map_documents"] == 2
    assert ledger["summary"]["cities_with_nonspatial_administrative_event_leads"] == 1
    assert ledger["summary"]["jakarta_incident_source_rows"] == 260
    jakarta = ledger["city_specific_nonspatial_leads"][0]
    assert jakarta["city"] == "Jakarta"
    assert jakarta["coordinate_or_geometry_field_present"] is False
    assert jakarta["explicit_reuse_license_verified"] is False
    assert jakarta["confirmatory_enrollment_eligible"] is False


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
    assert "192/192 selected RTC groups meet the matched 80% quota" in html
    assert "initial random availability draw passed 169/192" in html
    assert "not an archive-wide pass-rate estimate" in html
    assert "Mumbai’s two NRSC maps" in html
    assert "unverified overlap and reuse terms" in html
    assert "Jakarta also has a 2024 BPBD administrative incident extract" in html
    assert "atlas-jakarta-incident-data-audit.json" in html
    assert "Event acquisition opportunities" in html
    assert "do not establish an exact 24-hour match" in html
    assert "atlas-groundsource-event-coverage-audit.json" in html
    assert 'target="_blank" rel="noopener">Open event/date opportunity JSON' in html
    assert 'download="atlas-groundsource-event-coverage-audit.json">Download event/date opportunity JSON' in html


def test_groundsource_opportunities_remain_discovery_only_and_include_each_area():
    ledger = build_ledger()
    assert ledger["summary"]["areas_with_three_groundsource_top_metadata_opportunities"] == 16
    assert len(ledger["areas"]) == 16
    for row in ledger["areas"]:
        assert row["groundsource_top_leads_with_near_date_and_3_pre_post_metadata"] == 3
        assert len(row["groundsource_top_metadata_opportunity_leads"]) <= 3
    assert ledger["summary"]["confirmatory_areas_eligible"] == 0


def test_generated_reference_ledger_matches_current_source_snapshot():
    root = Path(__file__).resolve().parents[1]
    expected = build_ledger()
    on_disk = json.loads((root / "outputs/atlas-reference-readiness-ledger.json").read_text())
    assert on_disk == expected
    assert (root / "dist/atlas-reference-readiness-ledger.json").read_bytes() == (root / "outputs/atlas-reference-readiness-ledger.json").read_bytes()
    assert (root / "dist/atlas-reference-readiness-ledger.csv").exists()
    assert (root / "dist/atlas-jakarta-incident-data-audit.json").read_bytes() == (root / "outputs/atlas-jakarta-incident-data-audit.json").read_bytes()
    assert (root / "dist/atlas-groundsource-event-coverage-audit.json").read_bytes() == (root / "outputs/atlas-groundsource-event-coverage-audit.json").read_bytes()
    assert "GENERATED REFERENCE READINESS LEDGER START" in (root / "dist/index.html").read_text()
