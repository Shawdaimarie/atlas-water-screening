import json
from pathlib import Path

from scripts.build_reference_readiness_ledger import build_ledger, render_card


def test_reference_readiness_ledger_balances_all_areas_and_preserves_unknowns():
    ledger = build_ledger()
    assert len(ledger["areas"]) == 16
    assert ledger["summary"]["us_areas"] == 8
    assert ledger["summary"]["international_areas"] == 8
    assert ledger["summary"]["confirmatory_areas_eligible"] == 0
    st_louis = next(x for x in ledger["areas"] if x["city"] == "St. Louis")
    assert st_louis["geoid_flood_tiles"] == 12
    assert st_louis["geoid_mapped_label_fraction"] == 0.776967480906398
    assert st_louis["geoid_outside_mapped_label_fraction"] == 0.223032519093602
    assert st_louis["confirmatory_enrollment_eligible"] is False
    other_area = next(x for x in ledger["areas"] if x["city"] == "Houston")
    assert other_area["geoid_mapped_label_fraction"] is None
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
    assert ledger["summary"]["areas_with_official_event_admin_area_aoi_context"] == 1
    assert ledger["summary"]["jakarta_bpbd_2026_affected_kelurahan_polygons_intersecting_aoi"] == 20
    assert ledger["summary"]["jakarta_bpbd_2026_reported_affected_kelurahan_count"] == 21
    assert ledger["summary"]["jakarta_incident_source_rows"] == 260
    assert ledger["summary"]["areas_with_nasa_egis_s1_water_catalog_leads"] == 3
    assert ledger["summary"]["nasa_egis_s1_water_catalog_footprint_records"] == 12
    assert ledger["summary"]["usgs_gfid_rows_scanned"] == 136642
    assert ledger["summary"]["usgs_gfid_rows_in_common_window"] == 504
    assert ledger["summary"]["areas_with_usgs_gfid_representative_points_in_aoi"] == 0
    assert ledger["summary"]["usgs_gfid_representative_event_points_within_25km"] == 0
    assert all(x["usgs_gfid_representative_event_points_in_aoi"] == 0 for x in ledger["areas"])
    tampa = next(x for x in ledger["areas"] if x["city"] == "Tampa")
    assert tampa["nasa_egis_s1_water_catalog_dates"] == [
        "2024-09-14", "2024-09-26", "2024-10-03", "2024-10-08", "2024-10-11"
    ]
    miami = next(x for x in ledger["areas"] if x["city"] == "Miami")
    assert miami["nasa_egis_s1_water_catalog_dates"] == ["2024-10-03", "2024-10-10", "2024-10-11"]
    new_orleans = next(x for x in ledger["areas"] if x["city"] == "New Orleans")
    assert new_orleans["nasa_egis_s1_water_catalog_dates"] == []
    assert new_orleans["nasa_egis_s1_water_catalog_footprint_records"] == 2
    time_records = new_orleans["nasa_egis_s1_water_catalog_temporal_records"]
    assert len(time_records) == 2
    assert {x["date_basis"] for x in time_records} == {"granule_name_interval_only"}
    assert {x["granule_name_interval_start_utc"] for x in time_records} == {"2026-06-21T00:10:10Z"}
    assert {x["granule_name_interval_end_utc"] for x in time_records} == {"2026-06-27T00:58:29Z"}
    jakarta = ledger["city_specific_nonspatial_leads"][0]
    assert jakarta["city"] == "Jakarta"
    assert jakarta["coordinate_or_geometry_field_present"] is False
    assert jakarta["explicit_reuse_license_verified"] is False
    assert jakarta["confirmatory_enrollment_eligible"] is False
    event_context = ledger["city_specific_official_event_area_context"][0]
    assert event_context["positive_area_intersections_with_fixed_aoi"] == 20
    assert event_context["reported_affected_kelurahan_count"] == 21
    assert event_context["event_location_within_aoi_verified"] is False
    assert event_context["pixel_labels_or_raster_qa_present"] is False
    jakarta_row = next(x for x in ledger["areas"] if x["city"] == "Jakarta")
    assert jakarta_row["jakarta_bpbd_2026_affected_kelurahan_polygons_intersecting_aoi"] == 20
    assert jakarta_row["confirmatory_enrollment_eligible"] is False


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
    assert "Jakarta official-event context" in html
    assert "20/21 named affected kelurahan boundary polygons" in html
    assert "atlas-jakarta-bpbd-jan2026-aoi-context.json" in html
    assert "atlas-jakarta-incident-data-audit.json" in html
    assert "NASA EGIS same-product discovery" in html
    assert "catalog footprints show OPERA S1-water layers in 3/16 areas" in html
    assert "atlas-nasa-egis-opera-footprint-audit.json" in html
    assert "Historical reference-pixel coverage" in html
    assert "77.70%" in html
    assert "not held-out validation" in html
    assert "atlas-geoid-flood-stlouis-label-coverage.json" in html
    assert "USGS GFID independent event-context screen" in html
    assert "no local point is not evidence that flooding did not occur" in html
    assert "atlas-usgs-gfid-aoi-event-audit.json" in html
    assert "New Orleans has one WTR/BWTR catalog granule" in html
    assert "the service date field is absent" in html
    assert "not counted as multiple acquisition dates" in html
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
    assert (root / "dist/atlas-jakarta-bpbd-jan2026-aoi-context.json").read_bytes() == (root / "outputs/atlas-jakarta-bpbd-jan2026-aoi-context.json").read_bytes()
    assert (root / "dist/atlas-groundsource-event-coverage-audit.json").read_bytes() == (root / "outputs/atlas-groundsource-event-coverage-audit.json").read_bytes()
    assert (root / "dist/atlas-nasa-egis-opera-footprint-audit.json").read_bytes() == (root / "outputs/atlas-nasa-egis-opera-footprint-audit.json").read_bytes()
    assert (root / "dist/atlas-geoid-flood-stlouis-label-coverage.json").read_bytes() == (root / "outputs/atlas-geoid-flood-stlouis-label-coverage.json").read_bytes()
    assert (root / "dist/atlas-usgs-gfid-aoi-event-audit.json").read_bytes() == (root / "outputs/atlas-usgs-gfid-aoi-event-audit.json").read_bytes()
    assert (root / "dist/atlas-usgs-gfid-aoi-event-audit.md").read_bytes() == (root / "outputs/atlas-usgs-gfid-aoi-event-audit.md").read_bytes()
    assert "GENERATED REFERENCE READINESS LEDGER START" in (root / "dist/index.html").read_text()
