"""Add the audited SpaceNet 8 reference lead to the static ATLAS Site."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs/atlas-spacenet8-louisiana-coverage-audit.json"
HTML = ROOT / "dist/index.html"
ASSET = ROOT / "dist/atlas-spacenet8-louisiana-coverage-audit.json"
START = "<!-- GENERATED SPACENET8 COVERAGE CARD START -->"
END = "<!-- GENERATED SPACENET8 COVERAGE CARD END -->"


def validate_report(report: dict) -> dict:
    summary = report["summary"]
    if summary.get("areas_with_annotation_overlap") != 1:
        raise ValueError("Expected exactly one fixed-AOI overlap for this source screen")
    if summary.get("candidate_areas_with_overlap") != ["New Orleans"]:
        raise ValueError("Unexpected SpaceNet 8 candidate-area overlap")
    result = report["results"]["New Orleans"]
    totals = result["unique_feature_totals"]
    if result.get("annotation_files_intersecting") != 160:
        raise ValueError("Unexpected count of New Orleans intersecting annotation files")
    if totals.get("unique_feature_ids") != 4500 or totals.get("flooded") != 14:
        raise ValueError("Unexpected New Orleans SpaceNet 8 feature totals")
    if totals.get("flood_status_unknown") != 4486 or totals.get("not_flooded") != 0:
        raise ValueError("Null labels must remain unknown, not be interpreted as dry")
    return result


def render_card(report: dict) -> str:
    result = validate_report(report)
    totals = result["unique_feature_totals"]
    return (
        f'{START}<article class="reference-card"><h3>SpaceNet 8 · Hurricane Ida</h3>'
        f'<b>New Orleans · {result["annotation_files_intersecting"]} annotation tiles overlap</b>'
        f'<p>{totals["unique_feature_ids"]:,} unique building/road references intersect the fixed box; '
        f'{totals["flooded"]} have source label <code>flooded=yes</code>. '
        f'{totals["flood_status_unknown"]:,} null flood states remain unknown; the audit does not count them as dry. '
        'Labels were manually interpreted from pre/post high-resolution optical imagery. '
        'Flooded buildings mean water nearby; roads may be labeled for visible water or rubble. '
        'This is a sparse object-level event reference, not a pixel water mask, field truth, or confirmatory validation.</p>'
        '<a href="https://www.spacenet.ai/sn8-challenge/" target="_blank" rel="noopener">Open dataset source ↗</a> '
        '<a href="https://openaccess.thecvf.com/content/CVPR2022W/EarthVision/html/Hansch_SpaceNet_8_-_The_Detection_of_Flooded_Roads_and_Buildings_CVPRW_2022_paper.html" target="_blank" rel="noopener">Read dataset paper ↗</a> '
        '<a href="atlas-spacenet8-louisiana-coverage-audit.json" download="atlas-spacenet8-louisiana-coverage-audit.json">Download AOI audit ↗</a>'
        f'</article>{END}'
    )


def build() -> None:
    report = json.loads(REPORT.read_text())
    card = render_card(report)
    html = HTML.read_text()
    if START in html and END in html:
        before, rest = html.split(START, 1)
        _, after = rest.split(END, 1)
        html = before + card + after
    else:
        anchor = '<article class="reference-card"><h3>Other public reference screens</h3>'
        if html.count(anchor) != 1:
            raise ValueError("Could not locate the reference-card insertion point")
        html = html.replace(anchor, card + anchor, 1)
    HTML.write_text(html)
    shutil.copyfile(REPORT, ASSET)


if __name__ == "__main__":
    build()
