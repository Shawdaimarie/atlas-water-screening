#!/usr/bin/env python3
"""Add the fixed-area New Orleans BWTR missing-data result to the Site."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "dist/index.html"
AUDIT = ROOT / "outputs/atlas-neworleans-2026-egis-bwtr-coverage.json"
REPORT = ROOT / "outputs/atlas-neworleans-2026-egis-bwtr-coverage.md"
ANCHOR = "<!-- GENERATED MULTISITE EGIS SAMPLE CARD END -->"
START = "<!-- GENERATED NEWORLEANS EGIS BWTR CARD START -->"
END = "<!-- GENERATED NEWORLEANS EGIS BWTR CARD END -->"


def build(text: str, audit: dict) -> str:
    start, end = text.find(START), text.find(END)
    if start >= 0 or end >= 0:
        if start < 0 or end < start:
            raise ValueError("New Orleans EGIS card markers are incomplete or out of order")
        text = text[:start] + text[end + len(END):]
    if text.count(ANCHOR) != 1:
        raise ValueError("Expected exactly one multisite EGIS sample card anchor")
    export = audit["export"]
    item_id = audit["source"]["item"]["object_id"]
    card = (
        f'{START}<article class="reference-card"><h3>New Orleans · Louisiana flood BWTR fixed-box export</h3>'
        f'<b>{export["valid_bwtr_fraction"]:.0%} valid BWTR · '
        f'{export["valid_bwtr_pixels"]:,}/{export["pixel_count"]:,} cells</b>'
        '<p>The catalog item contains the registered AOI centre, but locked raster '
        f'{item_id} exported class 255 (no data) across the requested grid; a centre-point query also returned NoData. '
        'Unknown is not dry. NASA marks this response map preliminary and unvalidated. '
        'The June 21–27 item interval lacks pixel-specific times and does not establish the shared primary event-time rule.</p>'
        '<a href="atlas-neworleans-2026-egis-bwtr-coverage.md">Read the coverage record ↗</a> '
        '<a href="atlas-neworleans-2026-egis-bwtr-coverage.json">Open the full raster audit ↗</a> '
        '<a href="https://nola.gov/next/mayors-office/news/articles/june/2026-06-18-city-of-new-orleans-provides-update-post-severe-weather-event/" target="_blank" rel="noopener">Open the City event record ↗</a>'
        f'</article>{END}'
    )
    return text.replace(ANCHOR, ANCHOR + card)


def write() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    HTML.write_text(build(HTML.read_text(encoding="utf-8"), audit), encoding="utf-8")
    shutil.copy2(AUDIT, ROOT / "dist/atlas-neworleans-2026-egis-bwtr-coverage.json")
    shutil.copy2(REPORT, ROOT / "dist/atlas-neworleans-2026-egis-bwtr-coverage.md")


if __name__ == "__main__":
    write()
