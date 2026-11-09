"""Package and link the complete 8+8 JSON evidence register in a static Site."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_SOURCE = ROOT / "outputs/atlas-study-area-evidence-register.json"
CSV_SOURCE = ROOT / "outputs/atlas-study-area-register.csv"
BUTTON = '<button type="button" class="btn" id="downloadStudyRegister">↓ &nbsp;Download area register</button>'
LINK = '<a class="btn" href="atlas-study-area-evidence-register.json" download="atlas-study-area-evidence-register.json">↓ &nbsp;Download full evidence JSON</a>'
ACTION_GROUP = '<div class="study-register-actions">' + BUTTON + LINK + "</div>"


def update_html(html: str) -> str:
    button_count = html.count(BUTTON)
    action_group_count = html.count(ACTION_GROUP)
    if button_count == 1 and action_group_count == 0:
        return html.replace(BUTTON, ACTION_GROUP, 1)
    if button_count == 1 and action_group_count == 1:
        return html
    raise ValueError("Expected one study-area register button or the complete download group")


def build(site_root: Path, json_source: Path = JSON_SOURCE) -> tuple[Path, Path]:
    dist = site_root / "dist"
    html_path = dist / "index.html"
    json_path = dist / "atlas-study-area-evidence-register.json"
    csv_path = dist / "atlas-study-area-register.csv"
    html_path.write_text(update_html(html_path.read_text(encoding="utf-8")), encoding="utf-8")
    shutil.copyfile(json_source, json_path)
    shutil.copyfile(CSV_SOURCE, csv_path)
    return html_path, json_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-root", type=Path, default=ROOT)
    parser.add_argument("--json-source", type=Path, default=JSON_SOURCE)
    args = parser.parse_args()
    html, data = build(args.site_root, args.json_source)
    print(f"Linked complete evidence-register download in {html} and packaged {data} plus {args.site_root / 'dist/atlas-study-area-register.csv'}")


if __name__ == "__main__":
    main()
