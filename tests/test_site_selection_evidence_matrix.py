import json

import pytest

from scripts.build_site_selection_evidence_matrix import (
    DEFAULT_LEDGER,
    DEFAULT_REGISTER,
    DEFAULT_RTC,
    build_matrix,
    install_site_card,
    render_site_card,
    write_outputs,
)


def test_matrix_preserves_8_plus_8_and_separates_candidate_from_confirmation():
    result = build_matrix()
    summary = result["summary"]

    assert summary["candidate_areas"] == 16
    assert summary["us_candidates"] == 8
    assert summary["international_candidates"] == 8
    assert summary["candidates_with_documented_public_need"] == 16
    assert summary["candidates_with_complete_cmr_metadata_query"] == 16
    assert summary["areas_passing_all_12_rtc_groups"] == 10
    assert summary["rtc_groups_passing_80pct"] == 169
    assert summary["rtc_groups_sampled"] == 192
    assert summary["areas_meeting_matched_rtc_valid_quota"] == 16
    assert summary["matched_rtc_valid_groups_selected"] == 192
    assert summary["supplemental_rtc_groups_screened"] == 34
    assert summary["areas_with_three_groundsource_metadata_opportunities"] == 16
    assert summary["confirmatory_areas_eligible"] == 0
    assert summary["composite_site_score_used"] is False
    assert {row["city"] for row in result["rows"]} == {
        "Houston", "Miami", "Tampa", "New Orleans", "New York City", "Sacramento",
        "Atlanta", "St. Louis", "Jakarta", "Singapore", "Dubai", "Mumbai", "Bangkok",
        "Tokyo", "Manila", "São Paulo",
    }
    assert all(row["cmr_distinct_dates"] > 0 for row in result["rows"])
    assert all(not row["confirmatory_enrollment_eligible"] for row in result["rows"])
    assert all(row["groundsource_top_metadata_opportunities"] == 3 for row in result["rows"])


def test_matrix_records_pinned_input_hashes_and_writes_three_machine_readable_views(tmp_path):
    result = build_matrix()
    assert set(result["source_sha256"]) == {
        str(DEFAULT_REGISTER.relative_to(DEFAULT_REGISTER.parents[1])),
        str(DEFAULT_LEDGER.relative_to(DEFAULT_REGISTER.parents[1])),
        str(DEFAULT_RTC.relative_to(DEFAULT_REGISTER.parents[1])),
        str((DEFAULT_REGISTER.parents[1] / "outputs/atlas-s1rtc-valid-quota-audit.json").relative_to(DEFAULT_REGISTER.parents[1])),
    }
    json_path, csv_path, md_path = tmp_path / "matrix.json", tmp_path / "matrix.csv", tmp_path / "matrix.md"
    write_outputs(result, json_path, csv_path, md_path)
    assert json.loads(json_path.read_text())["summary"] == result["summary"]
    assert len(csv_path.read_text().splitlines()) == 17
    assert "**Confirmatory enrollment:** 0/16" in md_path.read_text()
    assert "not a weighted city ranking" in md_path.read_text()
    assert "192/192 groups" in md_path.read_text()


def test_matrix_fails_closed_when_source_area_frames_disagree(tmp_path):
    register = json.loads(DEFAULT_REGISTER.read_text())
    register["results"].pop()
    altered = tmp_path / "register.json"
    altered.write_text(json.dumps(register))

    with pytest.raises(ValueError, match="same 16-area frame"):
        build_matrix(altered, DEFAULT_LEDGER, DEFAULT_RTC)


def test_site_card_injection_is_explicit_and_idempotent():
    result = build_matrix()
    html = '<section><div class="study-foot">Archive metadata is not a downloaded observation. Details.</div></section>'
    card = render_site_card(result)
    updated = install_site_card(html, card)

    assert "balanced 8+8 frame" in updated
    assert "0/16 pass confirmatory enrollment" in updated
    assert "192/192 groups across 16/16 areas" in updated
    assert 'target="_blank" rel="noopener"' in updated
    assert 'download="atlas-site-selection-evidence-matrix.csv"' in updated
    assert install_site_card(updated, card) == updated
