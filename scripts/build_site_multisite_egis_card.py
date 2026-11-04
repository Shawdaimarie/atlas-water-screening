#!/usr/bin/env python3
"""Insert a bounded, fail-closed Miami/Tampa EGIS sampling summary in the Site."""
from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "dist/index.html"
AUDIT = ROOT / "outputs/atlas-milton-egis-multisite-pixel-sample.json"
REPORT = ROOT / "outputs/atlas-milton-egis-multisite-pixel-sample.md"
ANCHOR = "<!-- GENERATED TAMPA EGIS SAMPLE CARD END -->"
START = "<!-- GENERATED MULTISITE EGIS SAMPLE CARD START -->"
END = "<!-- GENERATED MULTISITE EGIS SAMPLE CARD END -->"


def _city_line(area: dict) -> str:
    scenes = []
    for scene in area["scenes"]:
        date = scene["date_utc"][5:]
        status = scene["sampling_status"]
        if status == "sampled":
            result = f"{scene['samples_returned']}/{scene['samples_requested']} returned"
        elif status == "outside_aoi_footprint":
            result = "outside AOI"
        else:
            result = "service error"
        scenes.append(f"{date}: {result}")
    return f"<b>{area['city']}:</b> " + "; ".join(scenes) + "."


def build(text: str, report: dict) -> str:
    start = text.find(START)
    end = text.find(END)
    if start >= 0 or end >= 0:
        if start < 0 or end < start:
            raise ValueError("Multisite EGIS card markers are incomplete or out of order")
        text = text[:start] + text[end + len(END):]
    if text.count(ANCHOR) != 1:
        raise ValueError("Expected one Tampa EGIS card anchor")
    lines = " ".join(_city_line(area) for area in report["areas"])
    card = (
        f'{START}<article class="reference-card"><h3>Miami and Tampa · Hurricane Milton raw WTR samples</h3>'
        f'<b>2 of 16 AOIs · four dates screened with matched points</b>'
        f'<p>{lines} NASA labels the response layers preliminary and unvalidated. '
        'These are catalog-locked point returns, not full-AOI coverage or a water-change estimate. '
        'The source dates do not meet the shared three-valid-scene event/baseline rule, and no independent labels were compared.</p>'
        '<a href="atlas-milton-egis-multisite-pixel-sample.md">Read the sampling record ↗</a> '
        '<a href="atlas-milton-egis-multisite-pixel-sample.json">Open the machine-readable audit ↗</a>'
        f'</article>{END}'
    )
    return text.replace(ANCHOR, card + ANCHOR)


def write() -> None:
    report = json.loads(AUDIT.read_text(encoding="utf-8"))
    text = build(HTML.read_text(encoding="utf-8"), report)
    HTML.write_text(text, encoding="utf-8")
    shutil.copy2(AUDIT, ROOT / "dist/atlas-milton-egis-multisite-pixel-sample.json")
    shutil.copy2(REPORT, ROOT / "dist/atlas-milton-egis-multisite-pixel-sample.md")


if __name__ == "__main__":
    write()
