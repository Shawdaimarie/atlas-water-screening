import json
import math
from pathlib import Path

import yaml

from scripts.audit_temporal_overlap import summarize
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
    assert site_html.count('<article class="reference-card">') == 4
    assert "12 benchmark-filtered tiles · St. Louis event EMSR203 (2017)" in site_html
    assert "all 12 records are in the benchmark training split" in site_html
    assert "not held-out validation" in site_html
    assert 'href="https://huggingface.co/datasets/links-ads/geoid-flood"' in site_html


def test_site_protocol_panel_matches_proposed_validation_contract():
    site_html = (ROOT / "dist/index.html").read_text()
    assert 'aria-labelledby="protocolTitle"' in site_html
    assert "Shared validation protocol" in site_html
    assert "Proposed design—not externally preregistered" in site_html
    assert "three valid scenes and 80% scene validity are feasibility checks only" in site_html
    assert "Confirmatory enrollment: 0 / 16" in site_html
    assert "385 independent units" in site_html
    assert "Invalid masks and no-data are missing, never dry" in site_html
    assert "the 3-date/80% thresholds as final criteria" not in site_html
    assert "Final enrollment requires 3 QA-valid scenes in each event and baseline period" not in site_html
    assert 'href="https://github.com/Shawdaimarie/atlas-water-screening/blob/main/outputs/atlas-preregistered-validation-protocol.md"' in site_html
