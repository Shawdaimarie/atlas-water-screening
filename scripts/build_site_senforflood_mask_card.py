"""Publish the caveated SenForFlood footprint screen on the ATLAS Site."""
from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs/atlas-senforflood-mask-coverage-audit.json"
REPORT_MD = ROOT / "outputs/atlas-senforflood-mask-coverage-audit.md"
HTML = ROOT / "dist/index.html"
ASSET = ROOT / "dist/atlas-senforflood-mask-coverage-audit.json"
ASSET_MD = ROOT / "dist/atlas-senforflood-mask-coverage-audit.md"
START = "<!-- GENERATED SENFORFLOOD COVERAGE CARD START -->"
END = "<!-- GENERATED SENFORFLOOD COVERAGE CARD END -->"
ANCHOR = '<article class="reference-card"><h3>Other public reference screens</h3>'


def validate_report(report: dict) -> dict:
    if report.get("audit_id") != "atlas_senforflood_mask_coverage":
        raise ValueError("Unexpected SenForFlood report")
    summary = report.get("summary", {})
    if summary.get("registered_areas") != 16 or summary.get("us_areas") != 8 or summary.get("international_areas") != 8:
        raise ValueError("Expected a complete 8+8 audit")
    if summary.get("areas_with_any_mask_chip_intersection") != 0:
        raise ValueError("Current card copy expects the audited zero-overlap result")
    if summary.get("valid_mask_files_inspected", 0) < 1:
        raise ValueError("No valid mask files were inspected")
    if report.get("source", {}).get("dataverse_license", {}).get("name") != "CC BY-SA 4.0":
        raise ValueError("Dataset license must be explicit")
    if not report.get("source", {}).get("huggingface_revision"):
        raise ValueError("A pinned repository revision is required")
    return summary


def render_card(report: dict) -> str:
    summary = validate_report(report)
    return (
        f"{START}<article class=\"reference-card\"><h3>SenForFlood · global mask-chip screen</h3>"
        f"<b>0 / 16 fixed study areas intersected · {summary['valid_mask_files_inspected']:,} mask files screened</b>"
        "<p>The pinned repository snapshot supplied no mask chips within the registered AOIs. Its DFO masks are automatic change-detection outputs, not independent ground truth. CEMS masks are analyst-created, but still need event timing, imagery lineage, and adequacy review. The Hugging Face upload is marked in progress; this is not a complete-corpus or no-flood finding.</p>"
        "<a href=\"https://doi.org/10.5194/isprs-archives-XLVIII-M-7-2025-97-2025\" target=\"_blank\" rel=\"noopener\">Read dataset paper ↗</a> "
        "<a href=\"https://doi.org/10.7910/DVN/ZQCODX\" target=\"_blank\" rel=\"noopener\">Open Dataverse record ↗</a> "
        "<a href=\"atlas-senforflood-mask-coverage-audit.json\" download=\"atlas-senforflood-mask-coverage-audit.json\">Download checksum and coverage audit ↗</a> "
        "<a href=\"atlas-senforflood-mask-coverage-audit.md\" target=\"_blank\" rel=\"noopener\">Read interpretation ↗</a>"
        f"</article>{END}"
    )


def update_html(html: str, card: str) -> str:
    start = html.find(START)
    end = html.find(END)
    if start >= 0 or end >= 0:
        if start < 0 or end < start:
            raise ValueError("SenForFlood card markers are incomplete or out of order")
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
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(report_path, asset_path)
    shutil.copyfile(report_md_path, asset_md_path)
    return html_path, asset_path, asset_md_path


if __name__ == "__main__":
    build()
