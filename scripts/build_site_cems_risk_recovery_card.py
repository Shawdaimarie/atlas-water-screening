#!/usr/bin/env python3
"""Publish the Risk & Recovery catalog screen into the private ATLAS Site."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "outputs/atlas-cems-risk-recovery-aoi-audit.json"
SITE_PATH = ROOT / "dist/index.html"
SITE_AUDIT_PATH = ROOT / "dist/atlas-cems-risk-recovery-aoi-audit.json"
START = "<!-- GENERATED CEMS RISK RECOVERY CARD START -->"
END = "<!-- GENERATED CEMS RISK RECOVERY CARD END -->"
ANCHOR = "<!-- GENERATED CEMS RAPID MAPPING CARD END -->"


def render_card(audit: dict) -> str:
    source, counts = audit["source"], audit["counts"]
    if audit["study_frame"].get("area_count") != 16 or source.get("activation_count") < 1:
        raise ValueError("Audit must describe the current 16-area frame and a nonempty catalog")
    return (
        f"{START}<article class=\"reference-card\"><h3>Copernicus EMS Risk &amp; Recovery · AOI screen</h3>"
        f"<b>{source['activation_count']} public activations · {source['flood_activation_count']} floods · "
        f"{counts['areas_with_any_intersection']}/16 AOI intersections</b>"
        "<p>The separate preparedness and recovery catalog was screened using each published product AOI geometry. "
        "No product AOI intersects an ATLAS box. This catalog screen does not show that flooding did not occur, "
        "and products are not treated as field truth or independent labels.</p>"
        f"<a href=\"{source['documentation_url']}\" target=\"_blank\" rel=\"noopener\">Open official API guide ↗</a> "
        "<a href=\"atlas-cems-risk-recovery-aoi-audit.json\" download=\"atlas-cems-risk-recovery-aoi-audit.json\">"
        "Download exact AOI audit ↧</a>"
        f"<span class=\"sr-only\">{counts['product_aoi_intersections']} published product AOIs intersect; "
        f"{counts['intersecting_flood_product_aois']} are flood-category products.</span></article>{END}"
    )


def build(audit_path: Path = AUDIT_PATH, site_path: Path = SITE_PATH,
          site_audit_path: Path = SITE_AUDIT_PATH) -> str:
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    html = site_path.read_text(encoding="utf-8")
    card = render_card(audit)
    if START in html or END in html:
        if html.count(START) != 1 or html.count(END) != 1:
            raise ValueError("Risk & Recovery card markers must occur exactly once as a pair")
        before, rest = html.split(START, 1)
        _, after = rest.split(END, 1)
        html = before + card + after
    else:
        if html.count(ANCHOR) != 1:
            raise ValueError("Could not locate the existing Rapid Mapping card")
        html = html.replace(ANCHOR, ANCHOR + card, 1)
    site_path.write_text(html, encoding="utf-8")
    site_audit_path.write_bytes(audit_path.read_bytes())
    return html


if __name__ == "__main__":
    build()
    print(f"Updated {SITE_PATH} and {SITE_AUDIT_PATH}")
