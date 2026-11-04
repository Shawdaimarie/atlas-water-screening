#!/usr/bin/env python3
"""Add the caveated Tampa NASA EGIS sample summary to the Site evidence panel."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "dist/index.html"
START = "<!-- GENERATED TAMPA EGIS SAMPLE CARD START -->"
END = "<!-- GENERATED TAMPA EGIS SAMPLE CARD END -->"
ANCHOR = '<article class="reference-card"><h3>Other public reference screens</h3>'
CARD = f'''{START}<article class="reference-card"><h3>Tampa · NASA EGIS OPERA BWTR sample</h3><b>2 dates · 1,024 returned raw-pixel samples per date</b><p>Sampled water class: 237/1,024 on 2024-09-14 and 243/1,024 on 2024-09-26. These are point counts, not full-area water fractions. NASA marks the response maps preliminary and unvalidated. One date per period fails the three-date feasibility floor; no independent labels were compared. This does not validate Tampa or ATLAS.</p><a href="{"https://gis.earthdata.nasa.gov/portal/rest/services/DISASTERS_202409_HURRICANE_HELENE/202427_opera_dswx_s1/ImageServer?f=pjson"}" target="_blank" rel="noopener">Open NASA EGIS source catalog ↗</a></article>{END}'''


def build(text: str | None = None) -> str:
    text = HTML.read_text(encoding="utf-8") if text is None else text
    start = text.find(START)
    end = text.find(END)
    if start >= 0 or end >= 0:
        if start < 0 or end < start:
            raise ValueError("Tampa EGIS card markers are incomplete or out of order")
        text = text[:start] + text[end + len(END):]
    if text.count(ANCHOR) != 1:
        raise ValueError("Expected one reference-card insertion point")
    return text.replace(ANCHOR, CARD + ANCHOR)


if __name__ == "__main__":
    HTML.write_text(build(), encoding="utf-8")
