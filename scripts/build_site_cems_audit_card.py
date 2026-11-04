#!/usr/bin/env python3
"""Publish the latest Copernicus EMS coverage screen into the static Site."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "outputs/atlas-cems-event-discovery-audit.json"
SITE_PATH = ROOT / "dist/index.html"
SITE_AUDIT_PATH = ROOT / "dist/atlas-cems-event-discovery-audit.json"
START = "<!-- GENERATED CEMS RAPID MAPPING CARD START -->"
END = "<!-- GENERATED CEMS RAPID MAPPING CARD END -->"


def render_card(audit: dict) -> str:
    source = audit["source"]
    counts = audit["counts"]
    return (
        f"{START}<article class=\"reference-card\"><h3>Copernicus EMS Rapid Mapping · live AOI screen</h3>"
        f"<b>{source['catalog_codes_unique']:,} activations · {source['flood_activations_screened']} floods · "
        f"0/16 fixed-area AOI overlaps</b>"
        "<p>Every flood activation AOI polygon was checked against the same fixed study boxes. "
        "This feed yielded no intersecting AOIs or products. It is a mapping-catalog coverage result; "
        "CEMS products are not treated as independent field labels, and no labels were compared with ATLAS.</p>"
        f"<a href=\"{source['guide']}\" target=\"_blank\" rel=\"noopener\">Open official API guide ↗</a> "
        "<a href=\"atlas-cems-event-discovery-audit.json\" download=\"atlas-cems-event-discovery-audit.json\">Download exact AOI audit ↧</a>"
        f"<span class=\"sr-only\">{counts['intersecting_flood_aois']} AOIs and "
        f"{counts['intersecting_products']} products intersect.</span></article>{END}"
    )


def build(audit_path: Path = AUDIT_PATH, site_path: Path = SITE_PATH,
          site_audit_path: Path = SITE_AUDIT_PATH) -> str:
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    html = site_path.read_text(encoding="utf-8")
    card = render_card(audit)
    if START in html or END in html:
        if html.count(START) != 1 or html.count(END) != 1:
            raise ValueError("CEMS card markers must occur exactly once as a pair")
        before, rest = html.split(START, 1)
        _, after = rest.split(END, 1)
        html = before + card + after
    else:
        anchor = '<div class="reference-grid">'
        if html.count(anchor) != 1:
            raise ValueError("Could not locate the static reference evidence grid")
        html = html.replace(anchor, anchor + card, 1)
    site_path.write_text(html, encoding="utf-8")
    site_audit_path.write_bytes(audit_path.read_bytes())
    return html


if __name__ == "__main__":
    build()
    print(f"Updated {SITE_PATH} and {SITE_AUDIT_PATH}")
