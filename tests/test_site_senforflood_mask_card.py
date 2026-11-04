import json
from pathlib import Path

import pytest

from scripts.build_site_senforflood_mask_card import render_card, update_html, validate_report


ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads((ROOT / "outputs/atlas-senforflood-mask-coverage-audit.json").read_text())
ANCHOR = '<article class="reference-card"><h3>Other public reference screens</h3>'


def test_senforflood_card_reports_zero_overlap_without_claiming_no_flood():
    card = render_card(REPORT)
    assert "0 / 16 fixed study areas intersected" in card
    assert "not independent ground truth" in card
    assert "not a complete-corpus or no-flood finding" in card
    assert "atlas-senforflood-mask-coverage-audit.json" in card


def test_senforflood_card_insertion_is_idempotent():
    html = f"<main>{ANCHOR}<article>other</article></main>"
    once = update_html(html, render_card(REPORT))
    twice = update_html(once, render_card(REPORT))
    assert twice == once


def test_senforflood_card_fails_closed_on_incomplete_or_changed_report():
    bad = {**REPORT, "summary": {**REPORT["summary"], "international_areas": 7}}
    with pytest.raises(ValueError, match=r"complete 8\+8"):
        validate_report(bad)
    overlap = {**REPORT, "summary": {**REPORT["summary"], "areas_with_any_mask_chip_intersection": 1}}
    with pytest.raises(ValueError, match="zero-overlap"):
        validate_report(overlap)
