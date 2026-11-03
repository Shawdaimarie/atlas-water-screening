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


CSS = f'''{CSS_START}.rtc-sample{{margin:14px 0 12px;padding:13px;background:#f8faf8;border:1px solid #dfe7e1;border-radius:7px}}.rtc-head{{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}}.rtc-head h3{{font-size:13px;margin:4px 0}}.rtc-head p{{font-size:10px;line-height:1.45;color:#596861;margin:4px 0}}.rtc-download{{flex:none;color:#167568;font-size:10px}}.rtc-metrics{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}.rtc-metrics span{{padding:6px 8px;background:#fff;border:1px solid #e0e7e2;border-radius:5px;color:#596861;font-size:9px}}.rtc-metrics b{{color:#1a4f46;font-size:11px}}.rtc-details{{background:#fff;border:1px solid #e3e9e4;border-radius:5px}}.rtc-details summary{{padding:8px 10px;color:#34483f;font-size:10px;font-weight:650;cursor:pointer;min-height:36px}}.rtc-table-wrap{{overflow:auto;max-height:440px}}.rtc-table{{width:100%;border-collapse:collapse;min-width:610px;font-size:9px}}.rtc-table caption{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);whit