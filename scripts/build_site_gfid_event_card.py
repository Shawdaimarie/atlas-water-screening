"""Expose the caveated USGS GFID event screen on the static Site."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs/atlas-usgs-gfid-aoi-event-audit.json"
REPORT_MD = ROOT / "outputs/atlas-usgs-gfid-aoi-event-audit.md"
HTML = ROOT / "dist/index.html"
ASSET = ROOT / "dist/atlas-usgs-gfid-aoi-event-audit.json"
ASSET_MD = ROOT / "dist/atlas-usgs-gfid-aoi-event-audit.md"
START = "<!-- GENERATED USGS GFID AOI EVENT CARD START -->"
END = "<!-- GENERATED USGS GFID AOI EVENT CARD END -->"
ANCHOR = '<article class="reference-card"><h3>Other public reference screens</h3>'


def validate_report(report: dict) -> dict:
    if report.get("status") != "event_context_discovery_only":
        raise ValueError("GFID event screen must remain discovery-only")
    if report.get("counts", {}).get("study_areas") != 16:
        raise ValueError("Expected a complete 8+8, 16-area event screen")
    areas = report.get("areas")
    if not isinstance(areas, list) or len(areas) != 16:
        raise ValueError("Expected exactly 16 area results")
    if any("events" not in area or "nearby_discovery_leads" not in area for area in areas):
        raise ValueError("Every area must retain exact and nearby event results")
    return report["counts"]


def render_card(report: dict) -> str:
    counts = validate_report(report)
    nearby = counts["nearby_representative_points_within_25km_all_areas"]
    exact_areas = counts["areas_with_representative_points_in_aoi"]
    return (
        f"{START}<article class=\"reference-card\"><h3>USGS GFID · geocoded flood-impact events</h3>"
        f"<b>{exact_areas}/16 areas with representative event points in the fixed boxes</b>"
        f"<p>{counts['rows_with_event_date_in_common_window']:,} of "
        f"{counts['aggregated_rows_scanned']:,} source rows have dates in the common window; "
        f"{nearby} representative points fall within 25 km of a box. "
        "A point screen is event context only: no point in a box is not evidence that flooding did not occur, "
        "and the source provides no pixel labels or inundation boundaries.</p>"
        f"<a href=\"{report['source']['data_gov_url']}\" target=\"_blank\" rel=\"noopener\">Open USGS catalog ↗</a> "
        "<a href=\"atlas-usgs-gfid-aoi-event-audit.json\" download=\"atlas-usgs-gfid-aoi-event-audit.json\">Download 16-area screen ↗</a> "
        "<a href=\"atlas-usgs-gfid-aoi-event-audit.md\" target=\"_blank\" rel=\"noopener\">Read interpretation ↗</a>"
        f"</article>{END}"
    )


def update_html(html: str, card: str) -> str:
    start = html.find(START)
    end = html.find(END)
    if start >= 0 or end >= 0:
        if start < 0 or end < start:
            raise ValueError("GFID card markers are incomplete or out of order")
        html = html[:start] + html[end + len(END):]
    if html.count(ANCHOR) != 1:
        raise ValueError("Expected one Other public reference screens card")
    return html.replace(ANCHOR, card + ANCHOR, 1)


def build(
    html_path: Path = HTML,
    report_path: Path = REPORT,
    report_md_path: Path = REPORT_MD,
    asset_path: Path = ASSET,
    asset_md_path: Path = ASSET_MD,
) -> tuple[Path, Path, Path]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    card = render_card(report)
    html_path.write_text(update_html(html_path.read_text(encoding="utf-8"), card), encoding="utf-8")
    shutil.copyfile(report_path, asset_path)
    shutil.copyfile(report_md_path, asset_md_path)
    return html_path, asset_path, asset_md_path


if __name__ == "__main__":
    build()
