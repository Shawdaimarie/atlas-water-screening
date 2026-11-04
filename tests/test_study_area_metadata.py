import json
import math
from pathlib import Path

import yaml

from scripts.audit_temporal_overlap import summarize
from scripts.build_site_tampa_egis_card import build as build_tampa_egis_card
from scripts.update_site_study_register import update as update_site_register


ROOT = Path(__file__).resolve().parents[1]
REGISTER = json.loads((ROOT / "data/study_area_register.json").read_text())
AREAS = REGISTER["results"]
PROTOCOL = yaml.safe_load((ROOT / "data/validation_protocol.yaml").read_text())["protocol"]


def test_register_has_eight_candidates_per_region_with_complete_cmr_pages():
    assert len(AREAS) == 16
    assert sum(area["region"] == "United States" for area in AREAS) == 8
    assert sum(area["region"] == "International" for area in AREAS) == 8
    assert all(area["returned_entries_complete"] for area in AREAS)


def test_metadata_date_counts_are_complete_and_90_date_cutoff_is_not_enrollment():
    assert PROTOCOL["discovery_only"]["prior_date_floor"] == 90
    assert PROTOCOL["discovery_only"]["prior_date_floor_is_enrollment_gate"] is False
    assert all(area["unique_acquisition_dates"] >= 90 for area in AREAS)
    assert all(
        area["unique_acquisition_dates"] == len(area["acquisition_dates"])
        for area in AREAS
    )
    assert all(area["acquisition_dates"] == sorted(set(area["acquisition_dates"])) for area in AREAS)


def test_validation_protocol_has_equal_8_plus_8_design_and_no_false_adequacy_claim():
    protocol = PROTOCOL
    discovery = PROTOCOL["discovery_only"]
    assert protocol["study_areas"]["total_candidates"] == 16
    assert protocol["study_areas"]["united_states"] == 8
    assert protocol["study_areas"]["international"] == 8
    assert protocol["state"] == "proposed_not_externally_preregistered"
    assert protocol["version"] == 2
    assert protocol["exploratory_findings_excluded_from_confirmatory"] is True
    assert "exploratory" in protocol["exploratory_history"].casefold()
    assert "externally timestamped" in protocol["confirmatory_freeze_record"]
    assert discovery["feasibility_floors_establish_statistical_adequacy"] is False
    assert PROTOCOL["enrollment"]["current_confirmatory_areas"] == 0
    assert PROTOCOL["reference_labels"]["independent_labelers"] == 2


def test_validation_precision_planning_value_is_reproducible():
    sampling = PROTOCOL["sampling"]
    n0 = math.ceil(
        1.96**2
        * sampling["planning_prevalence"]
        * (1 - sampling["planning_prevalence"])
        / sampling["target_half_width_proportion"] ** 2
    )
    assert n0 == sampling["simple_random_sample_n0"] == 385
    assert sampling["n0_scope"] == "per_area_per_period_overall_accuracy_or_proportion"
    planned = (
        PROTOCOL["study_areas"]["total_candidates"]
        * sampling["planning_periods_per_area"]
        * n0
    )
    assert planned == sampling["planning_area_period_reference_assessments_for_8_plus_8"] == 12320
    assert sampling["paired_locations_may_be_reused_across_periods"] is True
    assert sampling["class_specific_precision_requires_separate_allocation"] is True


def test_metadata_intersection_is_coarse_not_same_day_coverage():
    result = summarize(REGISTER)
    assert result["exact_acquisition_dates_common_to_all_areas"] == 0
    assert result["year_month_periods_with_at_least_one_metadata_acquisition_in_every_area"] == 24
    assert result["year_month_periods_with_any_area_metadata_acquisition"] == 26
    assert "does not test event alignment" in result["limits"]


def test_saved_audit_matches_recomputed_result():
    expected = summarize(REGISTER)
    saved = json.loads((ROOT / "data/temporal_overlap_audit.json").read_text())
    assert saved == expected


def test_site_evidence_register_is_complete_and_idempotent():
    site_html = (ROOT / "dist/index.html").read_text()
    updated = update_site_register(site_html, AREAS)
    assert updated == site_html
    embedded = updated.split("const studyAreas=", 1)[1].split(";let selectedStudyArea=", 1)[0]
    profiles = json.loads(embedded)
    assert len(profiles) == 16
    assert sum(area["region"] == "United States" for area in profiles) == 8
    assert sum(area["region"] == "International" for area in profiles) == 8
    assert all(area["empirical_evidence"] and area["validation_path"] for area in profiles)
    assert updated.count("Demand distinction:") == 1
    assert updated.count("GENERATED PUBLIC VALUE CHAIN START") == 1
    assert updated.count("GENERATED PUBLIC VALUE CHAIN END") == 1
    value_chain = updated.split("GENERATED PUBLIC VALUE CHAIN START", 1)[1].split("GENERATED PUBLIC VALUE CHAIN END", 1)[0]
    for stage in ("Hazard observation", "Asset exposure", "Service consequence", "Distributional equity", "Decision usefulness"):
        assert value_chain.count(stage) == 1
    assert "Water overlap alone does not establish damage" in value_chain
    assert "stakeholder-approved weights and sensitivity analysis" in value_chain


def test_singapore_priority_profile_uses_current_official_context_and_excludes_test_series():
    evidence = json.loads((ROOT / "data/study_area_evidence.json").read_text())
    singapore = next(row for row in evidence["records"] if row["city"] == "Singapore")
    assert "36 flood-prone locations" in singapore["empirical_evidence"]
    assert singapore["secondary_evidence_url"] == (
        "https://www.pub.gov.sg/-/media/PUB/PDF/Flood-Management/"
        "List-of-Flood-Prone-Areas-as-at-Apr-2025.pdf"
    )
    assert "no event-specific extent geometry" in singapore["validation_path"]
    assert "not an independent event label" in singapore["scope_limit"]
    site_html = update_site_register((ROOT / "dist/index.html").read_text(), AREAS)
    embedded = site_html.split("const studyAreas=", 1)[1].split(";let selectedStudyArea=", 1)[0]
    profiles = json.loads(embedded)
    singapore_profile = next(row for row in profiles if row["city"] == "Singapore")
    assert singapore_profile["secondary_evidence_url"] == singapore["secondary_evidence_url"]
    assert "data.gov.sg" not in site_html
    evidence_register = json.loads((ROOT / "outputs/atlas-study-area-evidence-register.json").read_text())
    singapore_export = next(row for row in evidence_register["results"] if row["city"] == "Singapore")
    assert singapore_export["secondary_evidence_url"] == singapore["secondary_evidence_url"]


def test_site_discloses_independent_reference_coverage_gaps():
    site_html = (ROOT / "dist/index.html").read_text()
    assert 'aria-labelledby="referenceAuditTitle"' in site_html
    assert "Reference-label coverage is not yet comparable" in site_html
    assert "1 sparse Houston chip" in site_html
    assert "0 of 16 AOIs overlap" in site_html
    assert "8 Sacramento points assessed in 2018 for a 2017 flood" in site_html
    assert "no current area passes the independent-label gate" in site_html
    assert 'href="https://registry.opendata.aws/c2smsfloods/"' in site_html
    assert 'href="https://zenodo.org/records/23426661"' in site_html
    assert site_html.count('<article class="reference-card">') == 8
    assert "Copernicus EMS Rapid Mapping · live AOI screen" in site_html
    assert "268 activations · 90 floods · 0/16 fixed-area AOI overlaps" in site_html
    assert 'href="atlas-cems-event-discovery-audit.json" download=' in site_html
    assert "16-area evidence-readiness ledger" in site_html
    assert "Download 16-area JSON" in site_html
    assert "SpaceNet 8 · Hurricane Ida" in site_html
    assert "4,500 unique building/road references intersect the fixed box" in site_html
    assert "14 have source label" in site_html
    assert "4,486 null flood states remain unknown" in site_html
    assert 'href="atlas-spacenet8-louisiana-coverage-audit.json"' in site_html
    assert "12 benchmark-filtered tiles · St. Louis event EMSR203 (2017)" in site_html
    assert "all 12 records are in the benchmark training split" in site_html
    assert "not held-out validation" in site_html
    assert 'href="https://huggingface.co/datasets/links-ads/geoid-flood"' in site_html
    assert "Tampa · NASA EGIS OPERA BWTR sample" in site_html
    assert "237/1,024 on 2024-09-14 and 243/1,024 on 2024-09-26" in site_html
    assert "preliminary and unvalidated" in site_html
    assert "no independent labels were compared" in site_html


def test_tampa_egis_site_card_build_is_idempotent_and_caveated():
    site_html = (ROOT / "dist/index.html").read_text()
    updated = build_tampa_egis_card(site_html)
    assert build_tampa_egis_card(updated) == updated
    assert updated.count("GENERATED TAMPA EGIS SAMPLE CARD START") == 1
    assert "not full-area water fractions" in updated
    assert "fails the three-date feasibility floor" in updated


def test_site_protocol_panel_matches_proposed_validation_contract():
    site_html = (ROOT / "dist/index.html").read_text()
    assert 'aria-labelledby="protocolTitle"' in site_html
    assert "Shared validation protocol" in site_html
    assert "Proposed design—not externally preregistered" in site_html
    assert "three valid scenes and 80% scene validity are feasibility checks only" in site_html
    assert "Confirmatory enrollment: 0 / 16" in site_html
    assert "385 effective independent reference units per site-period" in site_html
    assert "12,320 area-period reference assessments" in site_html
    assert "Class-specific accuracy requires separate sample allocation" in site_html
    assert "Invalid masks and no-data are missing, never dry" in site_html
    assert "the 3-date/80% thresholds as final criteria" not in site_html
    assert "Final enrollment requires 3 QA-valid scenes in each event and baseline period" not in site_html
    assert 'href="https://github.com/Shawdaimarie/atlas-water-screening/blob/main/outputs/atlas-preregistered-validation-protocol.md"' in site_html


def test_s1rtc_real_pixel_coverage_audit_is_balanced_and_clearly_limited():
    audit = json.loads((ROOT / "outputs/atlas-s1rtc-pixel-coverage-audit.json").read_text())
    assert audit["summary"] == {
        "areas": 16, "us_areas": 8, "international_areas": 8,
        "areas_with_all_four_sample_quarters_above_80pct": 12,
        "quarterly_samples_above_80pct": 56,
    }
    assert audit["pixel_coverage_screen"]["band"] == "VV"
    assert audit["pixel_coverage_screen"]["nominal_spacing_m"] == 10
    assert "not a water classification" in audit["interpretation_limits"][1]
    assert all(len(area["quarter_results"]) == 4 for area in audit["areas"])
    assert all(q["valid_fraction"] is None or 0 <= q["valid_fraction"] <= 1
               for area in audit["areas"] for q in area["quarter_results"])
    assert all("SAS" not in json.dumps(q) and "sig=" not in json.dumps(q)
               for area in audit["areas"] for q in area["quarter_results"])


def test_live_site_source_exposes_s1rtc_sample_table_and_download():
    site_html = (ROOT / "dist/index.html").read_text()
    assert "Matched valid-pixel coverage quota across 16 candidate areas" in site_html
    assert "192 / 192" in site_html
    assert "16 / 16" in site_html
    assert "34</b> additional groups screened · 23 accepted · 11 below floor" in site_html
    assert "Compare 12 accepted sampled dates" in site_html
    assert "A / B / C" in site_html
    assert "A / B / C / C" not in site_html
    assert 'id="rtcCoverageRows"' in site_html
    assert "renderS1rtcAreaCoverage" in site_html
    assert 'href="s1rtc-pixel-coverage-unique.json"' in site_html
    assert 'href="s1rtc-pixel-coverage-valid-quota.json"' in site_html
    assert 'href="https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc"' in site_html
    combined = json.loads((ROOT / "outputs/atlas-s1rtc-pixel-coverage-combined-audit.json").read_text())
    assert combined["measurement"]["source_declared_nodata_values"] == [-32768]
    assert combined["item_url_template"].endswith("/items/{item_id}")
    assert all("stac_nodata" in sample
               for area in combined["areas"] for quarter in area["quarter_results"]
               for sample in quarter["samples"])
    assert combined["summary"] == {
        "areas": 16, "us_areas": 8, "international_areas": 8,
        "sampling_design": "Three distinct sampled orbit groups per quarter; without replacement within each area and quarter.",
        "selected_groups_per_area": 12, "selected_orbit_groups": 192,
        "unique_orbit_groups": 192, "duplicate_group_selections": 0,
        "selected_groups_above_80pct": 169, "unique_groups_above_80pct": 169,
        "areas_with_all_sampled_groups_above_80pct": 10,
        "retained_prior_unique_groups": 173, "replacement_raster_reads": 19,
    }
    assert all(area["sampled_group_count"] == 12 for area in combined["areas"])
    assert all(len(q["samples"]) == 3 for area in combined["areas"] for q in area["quarter_results"])
    assert (ROOT / "dist/s1rtc-pixel-coverage-unique.json").read_bytes() == (
        ROOT / "outputs/atlas-s1rtc-pixel-coverage-combined-audit.json").read_bytes()
    assert not (ROOT / "dist/s1rtc-pixel-coverage-replicates.json").exists()


def test_site_matched_quota_asset_preserves_all_screening_attempts_and_limits():
    report = json.loads((ROOT / "dist/s1rtc-pixel-coverage-valid-quota.json").read_text())
    assert report["summary"]["valid_groups_selected"] == 192
    assert report["summary"]["areas_meeting_12_group_quota"] == 16
    assert report["summary"]["supplemental_groups_screened"] == 34
    assert len(report["areas"]) == 16
    assert all(area["all_quarter_quotas_met"] for area in report["areas"])
    assert all(len(q["supplemental_attempts"]) == q["supplemental_groups_screened"]
               for area in report["areas"] for q in area["quarter_results"])
    assert any("water classification or flood accuracy" in limit for limit in report["interpretation_limits"])
    assert any("does not provide a regional population estimate" in limit for limit in report["interpretation_limits"])


def test_evidence_export_includes_selected_scenario_and_measurement_provenance():
    site_html = (ROOT / "dist/index.html").read_text()
    handler = site_html.split("$('export').onclick=()=>{", 1)[1].split(";let timer", 1)[0]
    for field in (
        "study_area", "event", "event_window", "baseline_window", "collection",
        "asset_id", "method", "observed_overlap_percent", "valid_coverage_percent",
        "fixture_confidence_percent", "data_status",
    ):
        assert f"'{field}'" in handler
    assert "const eventKey=$('event').value" in handler
    assert "const eventName=eventKey==='ida'?'Hurricane Ida':'Hurricane Beryl'" in handler
    assert "2021-08-29/2021-08-30" in handler
    assert "2021-08-15/2021-08-25" in handler
    assert "2024-07-08/2024-07-10" in handler
    assert "2024-06-24/2024-07-04" in handler
    assert "OPERA DSWx-S1 V1 schema reference; no granule loaded" in handler
    assert "synthetic_fixture_no_live_NASA_data" in handler
    assert "atlas-${area}-${eventKey}-${mode}-fixture.csv" in handler
