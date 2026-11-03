#!/usr/bin/env python3
"""Inject the redacted 2025 Sentinel-1 RTC coverage sample into the static Site."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "dist/index.html"
AUDIT = ROOT / "outputs/atlas-s1rtc-pixel-coverage-audit.json"
UNIQUE_AUDIT = ROOT / "outputs/atlas-s1rtc-pixel-coverage-unique-audit.json"
COMBINED_AUDIT = ROOT / "outputs/atlas-s1rtc-pixel-coverage-combined-audit.json"
ASSET = ROOT / "dist/s1rtc-pixel-coverage-unique.json"
LEGACY_REPLICATE_ASSET = ROOT / "dist/s1rtc-pixel-coverage-replicates.json"


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


PANEL = f'''{PANEL_START}<section class="rtc-sample" aria-labelledby="rtcSampleTitle"><div class="rtc-head"><div><div class="eyebrow">Real raster availability samples · 2025</div><h3 id="rtcSampleTitle">Sentinel-1 coverage varies across the candidate areas</h3><p>Three unique RTC orbit groups per calendar quarter for each fixed 25 × 25 km area. Samples are selected without replacement within each area and quarter. The screen measures finite, non-nodata VV pixels only.</p></div><a class="rtc-download" href="s1rtc-pixel-coverage-unique.json" download="atlas-s1rtc-pixel-coverage-unique.json">Download the unique-group coverage audit ↗</a></div><div class="rtc-metrics"><span><b>169 / 192</b> selected groups at or above 80%</span><span><b>10 / 16</b> areas at or above 80% in all 12 selected groups</span></div><details class="rtc-details" open><summary>Compare 12 unique sampled dates for all 16 areas</summary><div class="rtc-table-wrap"><table class="rtc-table"><caption>Valid VV pixel coverage for three distinct sample groups per quarter and study area</caption><thead><tr><th scope="col">Study area</th><th scope="col">Q1 · A / B / C</th><th scope="col">Q2 · A / B / C</th><th scope="col">Q3 · A / B / C</th><th scope="col">Q4 · A / B / C</th></tr></thead><tbody id="rtcCoverageRows"></tbody></table></div></details><p class="rtc-footnote"><b>Interpretation:</b> the 80% per-scene floor is a spatial-coverage feasibility screen. All 12 selected area/orbit groups are distinct within each area; one group is sampled for each slot, and duplicate slots from the initial seeded draws were deterministically replaced from the remaining candidates. Low samples need review; other candidate groups require the same QA. This is not flood classification, OPERA validation, event/baseline adequacy, ground truth, or proof of comparability. <a href="https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc" target="_blank" rel="noopener">Open collection metadata ↗</a></p></section>{PANEL_END}'''


CSS = f'''{CSS_START}.rtc-sample{{margin:14px 0 12px;padding:13px;background:#f8faf8;border:1px solid #dfe7e1;border-radius:7px}}.rtc-head{{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}}.rtc-head h3{{font-size:13px;margin:4px 0}}.rtc-head p{{font-size:10px;line-height:1.45;color:#596861;margin:4px 0}}.rtc-download{{flex:none;color:#167568;font-size:10px}}.rtc-metrics{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}.rtc-metrics span{{padding:6px 8px;background:#fff;border:1px solid #e0e7e2;border-radius:5px;color:#596861;font-size:9px}}.rtc-metrics b{{color:#1a4f46;font-size:11px}}.rtc-details{{background:#fff;border:1px solid #e3e9e4;border-radius:5px}}.rtc-details summary{{padding:8px 10px;color:#34483f;font-size:10px;font-weight:650;cursor:pointer;min-height:36px}}.rtc-table-wrap{{overflow:auto;max-height:440px}}.rtc-table{{width:100%;border-collapse:collapse;min-width:610px;font-size:9px}}.rtc-table caption{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}.rtc-table th,.rtc-table td{{border-top:1px solid #edf0ed;padding:7px 8px;text-align:left;vertical-align:middle}}.rtc-table thead th{{position:sticky;top:0;background:#f4f7f4;color:#64736c;z-index:1}}.rtc-table tbody th{{min-width:120px;color:#263a32;font-size:9px}}.rtc-table tbody th small{{display:block;color:#77867e;font-weight:450;margin-top:2px}}.rtc-cell{{display:flex;flex-direction:column;gap:3px;white-space:nowrap}}.rtc-cell span{{color:#68776f}}.rtc-pass{{color:#176c5d}}.rtc-review{{color:#9d542c}}.rtc-footnote{{font-size:9px;line-height:1.55;color:#596861;margin:9px 0 0}}.rtc-footnote a{{color:#167568}}.rtc-area-readout{{margin:10px 0;padding:9px;background:#f3f7f4;border:1px solid #dfe7e1;border-radius:5px;font-size:9px;line-height:1.5}}.rtc-area-readout b{{color:#34483f}}@media(max-width:700px){{.rtc-head{{display:block}}.rtc-download{{display:inline-block;margin-top:7px}}}}{CSS_END}'''


PROFILE_RENDERER = f'''{PROFILE_START}function renderS1rtcAreaCoverage(city){{const row=s1rtcCoverageData.find(x=>x.city===city);if(!row)return'';return`<div class="rtc-area-readout"><b>2025 sampled VV coverage:</b> ${{row.sampled_quarter_pixel_passes}} of 8 sampled groups met the 80% spatial screen.<br>${{row.quarter_results.map(q=>`Q${{q.quarter}} A · ${{q.samples[0].date||'no eligible group'}} · ${{q.samples[0].valid_fraction===null?'not sampled':(q.samples[0].valid_fraction*100).toFixed(1)+'% valid'}} &nbsp; | &nbsp; B · ${{q.samples[1].date||'no eligible group'}} · ${{q.samples[1].valid_fraction===null?'not sampled':(q.samples[1].valid_fraction*100).toFixed(1)+'% valid'}}`).join('<br>')}}</div>`}}{PROFILE_END}'''


TABLE_RENDERER = f'''{TABLE_START}function renderS1rtcCoverageTable(){{const body=$('rtcCoverageRows');if(!body)return;body.innerHTML=s1rtcCoverageData.map(a=>`<tr><th scope="row">${{a.city}}<small>${{a.region}}</small></th>${{a.quarter_results.map(q=>`<td><div class="rtc-cell">${{q.samples.map((s,i)=>{{const fraction=s.valid_fraction;const cls=fraction!==null&&fraction>=0.8?'rtc-pass':'rtc-review';return`<span>${{i?'B':'A'}} · ${{s.date||'No sample'}}</span><b class="${{cls}}">${{fraction===null?'—':(fraction*100).toFixed(1)+'% valid'}}</b>`}}).join('')}}</div></td>`).join('')}}</tr>`).join('')}}renderS1rtcCoverageTable();{TABLE_END}'''


PROFILE_RENDERER_MULTI = f'''{PROFILE_START}function renderS1rtcAreaCoverage(city){{const row=s1rtcCoverageData.find(x=>x.city===city);if(!row)return'';const value=s=>s.valid_fraction===null?'not sampled':(s.valid_fraction*100).toFixed(1)+'% valid';return '<div class="rtc-area-readout"><b>2025 sampled VV coverage:</b> '+row.sampled_quarter_pixel_passes+' of '+row.sampled_group_count+' sampled groups met the 80% spatial screen.<br>'+row.quarter_results.map(q=>'Q'+q.quarter+' · '+q.samples.map((s,i)=>String.fromCharCode(65+i)+' '+(s.date||'no eligible group')+' · '+value(s)).join(' | ')).join('<br>')+'</div>'}}{PROFILE_END}'''

TABLE_RENDERER_MULTI = f'''{TABLE_START}function renderS1rtcCoverageTable(){{const body=$('rtcCoverageRows');if(!body)return;body.innerHTML=s1rtcCoverageData.map(a=>'<tr><th scope="row">'+a.city+'<small>'+a.region+'</small></th>'+a.quarter_results.map(q=>'<td><div class="rtc-cell">'+q.samples.map((s,i)=>{{const fraction=s.valid_fraction;const cls=fraction!==null&&fraction>=0.8?'rtc-pass':'rtc-review';return '<span>'+String.fromCharCode(65+i)+' · '+(s.date||'No sample')+'</span><b class="'+cls+'">'+(fraction===null?'—':(fraction*100).toFixed(1)+'% valid')+'</b>'}}).join('')+'</div></td>').join('')+'</tr>').join('')}}renderS1rtcCoverageTable();{TABLE_END}'''

def replace_marked(text: str, start: str, end: str, replacement: str, *, before: str | None = None) -> str:
    if start in text and end in text:
        left = text.index(start)
        right = text.index(end, left) + len(end)
        return text[:left] + replacement + text[right:]
    if before is None or before not in text:
        raise ValueError(f"Could not find Site insertion point for {start}")
    return text.replace(before, replacement + before, 1)


def build() -> None:
    audit = json.loads(UNIQUE_AUDIT.read_text())
    summary = audit["summary"]
    if (summary.get("areas") != 16 or summary.get("us_areas") != 8 or
            summary.get("international_areas") != 8 or len(audit.get("areas", [])) != 16):
        raise ValueError("Coverage audit must contain the complete 8+8 area set")
    if (summary.get("selected_area_orbit_groups") != 192 or
            summary.get("unique_area_orbit_groups") != 192 or
            summary.get("duplicate_selections") != 0):
        raise ValueError("Unique coverage audit does not contain 192 distinct area/orbit groups")
    data = []
    for area in audit["areas"]:
        if len(area["quarter_results"]) != 4 or any(len(q["samples"]) != 3 for q in area["quarter_results"]):
            raise ValueError(f"Expected three samples in each quarter for {area['city']}")
        data.append({
            "region": area["region"], "city": area["city"],
            "sampled_quarter_pixel_passes": area["sampled_groups_passing_80pct"],
            "sampled_group_count": area["sampled_group_count"],
            "all_sampled_groups_meet_pixel_screen": area["all_12_sampled_groups_meet_pixel_screen"],
            "quarter_results": area["quarter_results"],
        })
    combined = {
        "audit": "ATLAS unique-group Sentinel-1 RTC VV coverage screen",
        "source": audit["source"], "period": audit.get("period"),
        "item_url_template": "https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc/items/{item_id}",
        "measurement": {"band": "VV", "resolution_m": 10,
            "source_declared_nodata_values": sorted({s.get("stac_nodata") for a in audit["areas"] for q in a["quarter_results"] for s in q["samples"] if s.get("stac_nodata") is not None}),
            "validity_definition": "Finite VV pixels not equal to the source-declared nodata value; spatial data coverage only."},
        "summary": {
            "areas": 16, "us_areas": 8, "international_areas": 8,
            "sampling_design": "Three distinct sampled orbit groups per quarter; without replacement within each area and quarter.",
            "selected_groups_per_area": 12, "selected_orbit_groups": summary["selected_area_orbit_groups"],
            "unique_orbit_groups": summary["unique_area_orbit_groups"],
            "duplicate_group_selections": summary["duplicate_selections"],
            "selected_groups_above_80pct": summary["samples_passing_80pct"],
            "unique_groups_above_80pct": summary["samples_passing_80pct"],
            "areas_with_all_sampled_groups_above_80pct": summary["areas_passing_all_12_samples"],
            "retained_prior_unique_groups": summary["retained_prior"],
            "replacement_raster_reads": summary["replacement_raster_reads"]},
        "source_audit_sha256": hashlib.sha256(UNIQUE_AUDIT.read_bytes()).hexdigest(),
        "areas": [{"region": a["region"], "city": a["city"],
            "sampled_quarter_pixel_passes": a["sampled_groups_passing_80pct"],
            "sampled_group_count": a["sampled_group_count"],
            "all_sampled_groups_meet_pixel_screen": a["all_12_sampled_groups_meet_pixel_screen"],
            "quarter_results": a["quarter_results"]} for a in audit["areas"]],
        "interpretation_limits": [
            "This is an availability screen for a deterministic sample, not a population estimate.",
            "All 192 selected area/orbit groups are distinct within their respective areas.",
            "Each pass measures finite, non-nodata Sentinel-1 RTC VV pixels only; it says nothing about water classification.",
            "This screen does not validate OPERA DSWx-S1, event/baseline adequacy, independent labels, or confirmatory comparability."]}
    COMBINED_AUDIT.write_text(json.dumps(combined, indent=2) + "\n")
    panel = PANEL
    data_js = f"{DATA_START}const s1rtcCoverageData={json.dumps(data, ensure_ascii=False, separators=(',', ':'))};{DATA_END}"
    html = HTML.read_text()
    html = replace_marked(html, CSS_START, CSS_END, CSS, before=".reference-grid{display:grid")
    html = replace_marked(html, DATA_START, DATA_END, data_js, before="const assets=[")
    profile_anchor = "let selectedStudyArea=studyAreas[0];"
    html = replace_marked(html, PROFILE_START, PROFILE_END, PROFILE_RENDERER_MULTI, before=profile_anchor)
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
    html = replace_marked(html, PANEL_START, PANEL_END, panel, before='<div class="reference-grid">')
    html = replace_marked(html, TABLE_START, TABLE_END, TABLE_RENDERER_MULTI, before="drawStudyAreas();")
    HTML.write_text(html)
    shutil.copyfile(COMBINED_AUDIT, ASSET)
    LEGACY_REPLICATE_ASSET.unlink(missing_ok=True)


if __name__ == "__main__":
    build()
