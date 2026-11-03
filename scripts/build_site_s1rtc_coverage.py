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
REPLICATE_AUDIT = ROOT / "outputs/atlas-s1rtc-pixel-coverage-replicate-2.json"
COMBINED_AUDIT = ROOT / "outputs/atlas-s1rtc-pixel-coverage-combined-audit.json"
ASSET = ROOT / "dist/s1rtc-pixel-coverage-replicates.json"


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


PANEL = f'''{PANEL_START}<section class="rtc-sample" aria-labelledby="rtcSampleTitle"><div class="rtc-head"><div><div class="eyebrow">Real raster availability samples · 2025</div><h3 id="rtcSampleTitle">Sentinel-1 coverage varies across the candidate areas</h3><p>Two separately seeded draws of one RTC orbit group per calendar quarter for each fixed 25 × 25 km area. The screen measures finite, non-nodata VV pixels only.</p></div><a class="rtc-download" href="s1rtc-pixel-coverage-replicates.json" download="atlas-s1rtc-pixel-coverage-replicates.json">Download the paired coverage audit ↗</a></div><div class="rtc-metrics"><span><b>109 / 128</b> selected groups at or above 80%</span><span><b>10 / 16</b> areas at or above 80% in all eight selected groups</span></div><details class="rtc-details" open><summary>Compare eight sampled dates for all 16 areas</summary><div class="rtc-table-wrap"><table class="rtc-table"><caption>Valid VV pixel coverage for two separately seeded sample groups per quarter and study area</caption><thead><tr><th scope="col">Study area</th><th scope="col">Q1 · A / B</th><th scope="col">Q2 · A / B</th><th scope="col">Q3 · A / B</th><th scope="col">Q4 · A / B</th></tr></thead><tbody id="rtcCoverageRows"></tbody></table></div></details><p class="rtc-footnote"><b>Interpretation:</b> the 80% per-scene floor is a spatial-coverage feasibility screen. Some area/quarter groups repeat across the two draws; the download reports repeated groups and unique-group totals. Low samples show that selected groups need review; other candidate groups require the same QA. This is not flood classification, OPERA validation, event/baseline adequacy, ground truth, or proof of comparability. <a href="https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc" target="_blank" rel="noopener">Open collection metadata ↗</a></p></section>{PANEL_END}'''


CSS = f'''{CSS_START}.rtc-sample{{margin:14px 0 12px;padding:13px;background:#f8faf8;border:1px solid #dfe7e1;border-radius:7px}}.rtc-head{{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}}.rtc-head h3{{font-size:13px;margin:4px 0}}.rtc-head p{{font-size:10px;line-height:1.45;color:#596861;margin:4px 0}}.rtc-download{{flex:none;color:#167568;font-size:10px}}.rtc-metrics{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}.rtc-metrics span{{padding:6px 8px;background:#fff;border:1px solid #e0e7e2;border-radius:5px;color:#596861;font-size:9px}}.rtc-metrics b{{color:#1a4f46;font-size:11px}}.rtc-details{{background:#fff;border:1px solid #e3e9e4;border-radius:5px}}.rtc-details summary{{padding:8px 10px;color:#34483f;font-size:10px;font-weight:650;cursor:pointer;min-height:36px}}.rtc-table-wrap{{overflow:auto;max-height:440px}}.rtc-table{{width:100%;border-collapse:collapse;min-width:610px;font-size:9px}}.rtc-table caption{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}.rtc-table th,.rtc-table td{{border-top:1px solid #edf0ed;padding:7px 8px;text-align:left;vertical-align:middle}}.rtc-table thead th{{position:sticky;top:0;background:#f4f7f4;color:#64736c;z-index:1}}.rtc-table tbody th{{min-width:120px;color:#263a32;font-size:9px}}.rtc-table tbody th small{{display:block;color:#77867e;font-weight:450;margin-top:2px}}.rtc-cell{{display:flex;flex-direction:column;gap:3px;white-space:nowrap}}.rtc-cell span{{color:#68776f}}.rtc-pass{{color:#176c5d}}.rtc-review{{color:#9d542c}}.rtc-footnote{{font-size:9px;line-height:1.55;color:#596861;margin:9px 0 0}}.rtc-footnote a{{color:#167568}}.rtc-area-readout{{margin:10px 0;padding:9px;background:#f3f7f4;border:1px solid #dfe7e1;border-radius:5px;font-size:9px;line-height:1.5}}.rtc-area-readout b{{color:#34483f}}@media(max-width:700px){{.rtc-head{{display:block}}.rtc-download{{display:inline-block;margin-top:7px}}}}{CSS_END}'''


PROFILE_RENDERER = f'''{PROFILE_START}function renderS1rtcAreaCoverage(city){{const row=s1rtcCoverageData.find(x=>x.city===city);if(!row)return'';return`<div class="rtc-area-readout"><b>2025 sampled VV coverage:</b> ${{row.sampled_quarter_pixel_passes}} of 8 sampled groups met the 80% spatial screen.<br>${{row.quarter_results.map(q=>`Q${{q.quarter}} A · ${{q.samples[0].date||'no eligible group'}} · ${{q.samples[0].valid_fraction===null?'not sampled':(q.samples[0].valid_fraction*100).toFixed(1)+'% valid'}} &nbsp; | &nbsp; B · ${{q.samples[1].date||'no eligible group'}} · ${{q.samples[1].valid_fraction===null?'not sampled':(q.samples[1].valid_fraction*100).toFixed(1)+'% valid'}}`).join('<br>')}}</div>`}}{PROFILE_END}'''


TABLE_RENDERER = f'''{TABLE_START}function renderS1rtcCoverageTable(){{const body=$('rtcCoverageRows');if(!body)return;body.innerHTML=s1rtcCoverageData.map(a=>`<tr><th scope="row">${{a.city}}<small>${{a.region}}</small></th>${{a.quarter_results.map(q=>`<td><div class="rtc-cell">${{q.samples.map((s,i)=>{{const fraction=s.valid_fraction;const cls=fraction!==null&&fraction>=0.8?'rtc-pass':'rtc-review';return`<span>${{i?'B':'A'}} · ${{s.date||'No sample'}}</span><b class="${{cls}}">${{fraction===null?'—':(fraction*100).toFixed(1)+'% valid'}}</b>`}}).join('')}}</div></td>`).join('')}}</tr>`).join('')}}renderS1rtcCoverageTable();{TABLE_END}'''


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
    replicate = json.loads(REPLICATE_AUDIT.read_text())
    for run, expected in ((audit, 56), (replicate, 53)):
        if run.get("summary", {}).get("areas") != 16 or len(run.get("areas", [])) != 16:
            raise ValueError("Coverage audit must contain the complete 8+8 area set")
        if run.get("summary", {}).get("quarterly_samples_above_80pct") != expected:
            raise ValueError("Unexpected coverage sample result; review before building the Site")
    first = {area["city"]: area for area in audit["areas"]}
    second = {area["city"]: area for area in replicate["areas"]}
    if set(first) != set(second):
        raise ValueError("Replicate audits must cover the same study-area set")
    all_draws = []
    data = []
    for city, area in first.items():
        other = second[city]
        if area["region"] != other["region"] or len(area["quarter_results"]) != 4 or len(other["quarter_results"]) != 4:
            raise ValueError(f"Area or quarter structure mismatch for {city}")
        quarters = []
        for a, b in zip(area["quarter_results"], other["quarter_results"]):
            if a["quarter"] != b["quarter"]:
                raise ValueError(f"Quarter mismatch for {city}")
            quarters.append({"quarter": a["quarter"], "samples": [a, b]})
            all_draws.extend(((city, a), (city, b)))
        passes = sum(sample["valid_fraction"] is not None and sample["valid_fraction"] >= 0.8
                     for quarter in quarters for sample in quarter["samples"])
        data.append({"region": area["region"], "city": city,
                     "sampled_quarter_pixel_passes": passes,
                     "all_eight_sampled_groups_meet_pixel_screen": passes == 8,
                     "quarter_results": quarters})
    group_ids = [(city, d["date"], d["platform"], d["orbit_state"], d["absolute_orbit"])
                 for city, d in all_draws if d.get("date") and d.get("absolute_orbit") is not None]
    unique_group_ids = set(group_ids)
    unique_pass_groups = set((city, d["date"], d["platform"], d["orbit_state"], d["absolute_orbit"])
                             for city, d in all_draws if d.get("date") and d.get("absolute_orbit") is not None
                             and d.get("valid_fraction") is not None and d["valid_fraction"] >= 0.8)
    export_areas = []
    sample_fields = ("quarter", "date", "platform", "orbit_state", "relative_orbit",
                     "absolute_orbit", "candidate_orbit_groups", "valid_pixels",
                     "aoi_pixels", "valid_fraction", "meets_80pct_pixel_coverage_screen",
                     "stac_nodata", "asset_band", "stac_spatial_resolution_m")
    for area in data:
        quarters = []
        for quarter in area["quarter_results"]:
            samples = []
            for sample in quarter["samples"]:
                compact = {key: sample[key] for key in sample_fields}
                compact["items"] = [
                    {key: item[key] for key in ("id", "asset_checksum")}
                    for item in sample.get("items", [])]
                samples.append(compact)
            quarters.append({"quarter": quarter["quarter"], "samples": samples})
        export_areas.append({"region": area["region"], "city": area["city"],
                             "sampled_quarter_pixel_passes": area["sampled_quarter_pixel_passes"],
                             "all_eight_sampled_groups_meet_pixel_screen": area["all_eight_sampled_groups_meet_pixel_screen"],
                             "quarter_results": quarters})
    combined = {"audit": "ATLAS paired-seed Sentinel-1 RTC VV coverage sample",
                "source": audit["source"],
                "item_url_template": "https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc/items/{item_id}",
                "measurement": {"band": "VV", "resolution_m": 10,
                "source_declared_nodata_values": sorted({sample.get("stac_nodata") for _, sample in all_draws if sample.get("stac_nodata") is not None}),
                "validity_definition": "Finite VV pixels not equal to the source-declared nodata value; spatial data coverage only."},
                "period": audit["period"],
                "summary": {"areas": 16, "us_areas": 8, "international_areas": 8,
                            "separately_seeded_draws_per_area": 8,
                            "selected_orbit_groups": len(group_ids),
                            "unique_orbit_groups": len(unique_group_ids),
                            "duplicate_group_selections": len(group_ids) - len(unique_group_ids),
                            "selected_groups_above_80pct": sum(d.get("valid_fraction") is not None and d["valid_fraction"] >= 0.8 for _, d in all_draws),
                            "unique_groups_above_80pct": len(unique_pass_groups),
                            "areas_with_all_eight_groups_above_80pct": sum(a["all_eight_sampled_groups_meet_pixel_screen"] for a in data)},
                "replicate_audits": [
                    {"audit": run.get("audit"),
                     "sample_seed": run.get("pixel_coverage_screen", {}).get("sample_seed"),
                     "summary": run.get("summary"),
                     "report_file": report.name,
                     "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest()}
                    for run, report in ((audit, AUDIT), (replicate, REPLICATE_AUDIT))],
                "areas": export_areas,
                "interpretation_limits": [
                    "Two separately seeded random draws are reproducible screens, not statistically independent experiments.",
                    "Repeated area/orbit groups appeared in both draws; duplicate selections are counted once in unique-group totals.",
                    "Each pass is finite, non-nodata VV spatial availability only and says nothing about water classification.",
                    "This 2025 Sentinel-1 RTC screen does not validate OPERA DSWx-S1, event/baseline adequacy, independent labels, or confirmatory comparability."]}
    COMBINED_AUDIT.write_text(json.dumps(combined, indent=2) + "\n")
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
    shutil.copyfile(COMBINED_AUDIT, ASSET)


if __name__ == "__main__":
    build()
