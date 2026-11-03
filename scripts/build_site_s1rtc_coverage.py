#!/usr/bin/env python3
"""Inject the redacted 2025 Sentinel-1 RTC coverage sample into the static Site."""
from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "dist/index.html"
AUDIT = ROOT / "outputs/atlas-s1rtc-pixel-coverage-audit.json"
ASSET = ROOT / "dist/s1rtc-pixel-coverage-audit.json"


PANEL_START = "<!-- GENERATED S1RTC COVERAGE PANEL START -->"
PANEL_END = "<!-- GENERATED S1RTC COVERAGE PANEL END -->"
CSS_START = "/* GENERATED S1RTC COVERAGE CSS START */"
CSS_END = "/* GENERATED S1RTC COVERAGE CSS END */"
DATA_START = "/* GENERATED S1RTC COVERAGE DATA START */"
DATA_END = "/* GENERATED S1RTC COVERAGE DATA END */"
PROFILE_START = "/* GENERATED S1RTC AREA PROFILE START */"
PROFILE_END = "/* GENERATED S1RTC AREA PROFILE END */"
TABLE_START = "/* GENERATED S1RTC TABLE RENDERER START */"
TABLE_END = "/* GENERATED S1RTC TABLE RENDERER END */"


PANEL = f'''{PANEL_START}<section class="rtc-sample" aria-labelledby="rtcSampleTitle"><div class="rtc-head"><div><div class="eyebrow">Real raster availability sample · 2025</div><h3 id="rtcSampleTitle">Sentinel-1 coverage varies across the candidate areas</h3><p>One reproducibly sampled Sentinel-1 RTC orbit group per calendar quarter for each fixed 25 × 25 km area. The screen measures finite, non-nodata VV pixels only.</p></div><a class="rtc-download" href="s1rtc-pixel-coverage-audit.json" download="atlas-s1rtc-pixel-coverage-audit.json">Download full item audit ↗</a></div><div class="rtc-metrics"><span><b>56 / 64</b> sampled dates at or above 80%</span><span><b>12 / 16</b> areas at or above 80% in all four samples</span></div><details class="rtc-details" open><summary>Compare the four sampled dates for all 16 areas</summary><div class="rtc-table-wrap"><table class="rtc-table"><caption>Valid VV pixel coverage of each fixed study area on the deterministically sampled 2025 dates</caption><thead><tr><th scope="col">Study area</th><th scope="col">Q1</th><th scope="col">Q2</th><th scope="col">Q3</th><th scope="col">Q4</th></tr></thead><tbody id="rtcCoverageRows"></tbody></table></div></details><p class="rtc-footnote"><b>Interpretation:</b> 80% is a per-scene spatial coverage feasibility floor. A low sample means that selected orbit group is insufficient; other listed orbit groups require the same QA. This is not a flood classification, OPERA validation, event/baseline sample, ground truth, or confirmation that the 16 areas are comparable. <a href="https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc" target="_blank" rel="noopener">Open collection metadata ↗</a></p></section>{PANEL_END}'''


CSS = f'''{CSS_START}.rtc-sample{{margin:14px 0 12px;padding:13px;background:#f8faf8;border:1px solid #dfe7e1;border-radius:7px}}.rtc-head{{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}}.rtc-head h3{{font-size:13px;margin:4px 0}}.rtc-head p{{font-size:10px;line-height:1.45;color:#596861;margin:4px 0}}.rtc-download{{flex:none;color:#167568;font-size:10px}}.rtc-metrics{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}.rtc-metrics span{{padding:6px 8px;background:#fff;border:1px solid #e0e7e2;border-radius:5px;color:#596861;font-size:9px}}.rtc-metrics b{{color:#1a4f46;font-size:11px}}.rtc-details{{background:#fff;border:1px solid #e3e9e4;border-radius:5px}}.rtc-details summary{{padding:8px 10px;color:#34483f;font-size:10px;font-weight:650;cursor:pointer;min-height:36px}}.rtc-table-wrap{{overflow:auto;max-height:440px}}.rtc-table{{width:100%;border-collapse:collapse;min-width:610px;font-size:9px}}.rtc-table caption{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}.rtc-table th,.rtc-table td{{border-top:1px solid #edf0ed;padding:7px 8px;text-align:left;vertical-align:middle}}.rtc-table thead th{{position:sticky;top:0;background:#f4f7f4;color:#64736c;z-index:1}}.rtc-table tbody th{{min-width:120px;color:#263a32;font-size:9px}}.rtc-table tbody th small{{display:block;color:#77867e;font-weight:450;margin-top:2px}}.rtc-cell{{display:flex;flex-direction:column;gap:3px;white-space:nowrap}}.rtc-cell span{{color:#68776f}}.rtc-pass{{color:#176c5d}}.rtc-review{{color:#9d542c}}.rtc-footnote{{font-size:9px;line-height:1.55;color:#596861;margin:9px 0 0}}.rtc-footnote a{{color:#167568}}.rtc-area-readout{{margin:10px 0;padding:9px;background:#f3f7f4;border:1px solid #dfe7e1;border-radius:5px;font-size:9px;line-height:1.5}}.rtc-area-readout b{{color:#34483f}}@media(max-width:700px){{.rtc-head{{display:block}}.rtc-download{{display:inline-block;margin-top:7px}}}}{CSS_END}'''


PROFILE_RENDERER = f'''{PROFILE_START}function renderS1rtcAreaCoverage(city){{const row=s1rtcCoverageData.find(x=>x.city===city);if(!row)return'';return`<div class="rtc-area-readout"><b>2025 sampled VV coverage:</b> ${{row.sampled_quarter_pixel_passes}} of 4 quarter samples met the 80% spatial screen.<br>${{row.quarter_results.map(q=>`Q${{q.quarter}} · ${{q.date||'no eligible orbit group'}} · ${{q.valid_fraction===null?'not sampled':(q.valid_fraction*100).toFixed(1)+'% valid'}}`).join(' &nbsp; | &nbsp;')}}</div>`}}{PROFILE_END}'''


TABLE_RENDERER = f'''{TABLE_START}function renderS1rtcCoverageTable(){{const body=$('rtcCoverageRows');if(!body)return;body.innerHTML=s1rtcCoverageData.map(a=>`<tr><th scope="row">${{a.city}}<small>${{a.region}}</small></th>${{a.quarter_results.map(q=>{{const fraction=q.valid_fraction;const cls=fraction!==null&&fraction>=0.8?'rtc-pass':'rtc-review';return`<td><div class="rtc-cell"><span>${{q.date||'No sample'}}</span><b class="${{cls}}">${{fraction===null?'—':(fraction*100).toFixed(1)+'% valid'}}</b></div></td>`}}).join('')}}</tr>`).join('')}}renderS1rtcCoverageTable();{TABLE_END}'''


def replace_marked(text: str, start: str, end: str, replacement: str, *, before: str | None = None) -> str:
    if start in text and end in text:
        left = text.index(start)
        right = text.index(end, left) + len(end)
        return text[:left] + replacement + text[right:]
    if before is None or before not in text:
        raise ValueError(f"Could not find Site insertion point for {start}")
    return text.replace(before, replacement + before, 1)


def build() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("summary", {}).get("areas") != 16 or len(audit.get("areas", [])) != 16:
        raise ValueError("Coverage audit must contain the complete 8+8 area set")
    if audit.get("summary", {}).get("quarterly_samples_above_80pct") != 56:
        raise ValueError("Unexpected coverage audit sample result; review before building the Site")
    data = [{key: area[key] for key in ("region", "city", "sampled_quarter_pixel_passes", "all_four_quarters_meet_pixel_screen", "quarter_results")}
            for area in audit["areas"]]
    data_js = f"{DATA_START}const s1rtcCoverageData={json.dumps(data, ensure_ascii=False, separators=(',', ':'))};{DATA_END}"
    html = HTML.read_text()
    html = replace_marked(html, CSS_START, CSS_END, CSS, before=".reference-grid{display:grid")
    html = replace_marked(html, DATA_START, DATA_END, data_js, before="const assets=[")
    profile_anchor = "let selectedStudyArea=studyAreas[0];"
    html = replace_marked(html, PROFILE_START, PROFILE_END, PROFILE_RENDERER, before=profile_anchor)
    if html.index(PROFILE_START) < html.index(profile_anchor):
        profile_left = html.index(PROFILE_START)
        profile_right = html.index(PROFILE_END, profile_left) + len(PROFILE_END)
        profile_code = html[profile_left:profile_right]
        html = html[:profile_left] + html[profile_right:]
        profile_anchor_end = html.index(profile_anchor) + len(profile_anchor)
        html = html[:profile_anchor_end] + profile_code + html[profile_anchor_end:]
    anchor = '<p><b>Common archive window:</b> ${a.temporal_start.slice(0,10)} to ${a.temporal_end.slice(0,10)} · ${a.first_acquisition_date}–${a.last_acquisition_date} found.</p><a class="study-source"'
    if "${renderS1rtcAreaCoverage(a.city)}" not in html:
        if anchor not in html:
            raise ValueError("Could not locate the study area profile insertion point")
        html = html.replace(anchor, anchor.replace("</p><a", "</p>${renderS1rtcAreaCoverage(a.city)}<a"), 1)
    html = replace_marked(html, PANEL_START, PANEL_END, PANEL, before='<div class="reference-grid">')
    html = replace_marked(html, TABLE_START, TABLE_END, TABLE_RENDERER, before="drawStudyAreas();")
    HTML.write_text(html)
    shutil.copyfile(AUDIT, ASSET)


if __name__ == "__main__":
    build()
