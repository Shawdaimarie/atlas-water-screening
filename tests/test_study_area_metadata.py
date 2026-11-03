import json
from pathlib import Path

from scripts.audit_temporal_overlap import summarize
from scripts.update_site_study_register import update as update_site_register


ROOT = Path(__file__).resolve().parents[1]
REGISTER = json.loads((ROOT / "data/study_area_register.json").read_text())
AREAS = REGISTER["results"]


def test_register_has_eight_candidates_per_region_with_complete_cmr_pages():
    assert len(AREAS) == 16
    assert sum(area["region"] == "United States" for area in AREAS) == 8
    assert sum(area["region"] == "International" for area in AREAS) == 8
    assert all(area["returned_entries_complete"] for area in AREAS)


def test_all_candidates_pass_metadata_discovery_gate_and_counts_match_dates():
    assert all(area["unique_acquisition_dates"] >= 90 for area in AREAS)
    assert all(
        area["unique_acquisition_dates"] == len(area["acquisition_dates"])
        for area in AREAS
    )
    assert all(area["acquisition_dates"] == sorted(set(area["acquisition_dates"])) for area in AREAS)


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
