import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
builder = runpy.run_path(str(ROOT / "scripts/build_site_gfid_event_card.py"))


def _report():
    return {
        "status": "event_context_discovery_only",
        "counts": {
            "study_areas": 16,
            "areas_with_representative_points_in_aoi": 0,
            "representative_points_in_all_areas": 0,
            "nearby_representative_points_within_25km_all_areas": 0,
            "rows_with_event_date_in_common_window": 504,
            "aggregated_rows_scanned": 136642,
        },
        "source": {"data_gov_url": "https://catalog.data.gov/gfid"},
        "areas": [
            {"city": f"Area {i}", "events": [], "nearby_discovery_leads": []}
            for i in range(16)
        ],
    }


def test_gfid_site_card_discloses_scope_and_has_source_and_audit_links():
    card = builder["render_card"](_report())
    assert "0/16 areas with representative event points" in card
    assert "504 of 136,642 source rows" in card
    assert "no point in a box is not evidence that flooding did not occur" in card
    assert "https://catalog.data.gov/gfid" in card
    assert "atlas-usgs-gfid-aoi-event-audit.json" in card


def test_gfid_site_card_build_is_repeatable_and_packages_both_audit_formats(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    html = dist / "index.html"
    html.write_text(
        '<section><article class="reference-card"><h3>Other public reference screens</h3>'
        "<p>Existing content</p></article></section>",
        encoding="utf-8",
    )
    report = tmp_path / "report.json"
    report.write_text(json.dumps(_report()), encoding="utf-8")
    report_md = tmp_path / "report.md"
    report_md.write_text("# GFID screen" + chr(10), encoding="utf-8")
    asset = dist / "audit.json"
    asset_md = dist / "audit.md"

    build = builder["build"]
    build(html, report, report_md, asset, asset_md)
    first = html.read_text(encoding="utf-8")
    build(html, report, report_md, asset, asset_md)
    assert html.read_text(encoding="utf-8") == first
    assert json.loads(asset.read_text(encoding="utf-8"))["status"] == "event_context_discovery_only"
    assert asset_md.read_text(encoding="utf-8") == "# GFID screen" + chr(10)
    assert first.count("GENERATED USGS GFID AOI EVENT CARD START") == 1


def test_gfid_site_card_rejects_incomplete_or_promoted_evidence():
    bad = _report()
    bad["status"] = "confirmatory_validation"
    with pytest.raises(ValueError, match="discovery-only"):
        builder["render_card"](bad)
    bad = _report()
    bad["areas"].pop()
    with pytest.raises(ValueError, match="exactly 16"):
        builder["render_card"](bad)
