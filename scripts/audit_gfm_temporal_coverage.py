#!/usr/bin/env python3
"""Measure multi-date GFM raster availability for all fixed ATLAS AOIs.

For each area's highest-priority event discovery lead, inspect the three
nearest reported pre-event and post-event OPERA metadata dates, plus the event
date. This is a coverage screen only: Groundsource leads are unverified and
GFM shares Sentinel-1 lineage with the target OPERA product.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # Support both direct script execution and test/module imports.
    from scripts.audit_gfm_raster_coverage import API, inspect_item, search_all
except ModuleNotFoundError:  # pragma: no cover - exercised by direct execution.
    from audit_gfm_raster_coverage import API, inspect_item, search_all

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "outputs/atlas-study-area-register.csv"
LEADS = ROOT / "outputs/atlas-groundsource-event-coverage-audit.json"
SINGLE_DATE_AUDIT = ROOT / "outputs/atlas-gfm-raster-coverage-audit.json"
OUTPUT = ROOT / "outputs/atlas-gfm-temporal-coverage-audit.json"
MIN_VALID_FRACTION = 0.80
DATE_COUNT = 3


def _target_dates(candidate: dict[str, Any]) -> dict[str, list[str]]:
    """Return nearest 3 prior, event, and nearest 3 subsequent product dates."""
    pre = sorted(set(candidate.get("pre_event_30d_product_dates") or []))[-DATE_COUNT:]
    post = sorted(set(candidate.get("post_event_30d_product_dates") or []))[:DATE_COUNT]
    event_dates = sorted(set(candidate.get("product_dates_within_reported_event_interval") or []))
    if not event_dates:
        start, end = candidate.get("reported_start_date"), candidate.get("reported_end_date")
        if start and end and start == end:
            event_dates = [start]
    return {"pre_event_30d": pre, "candidate_event": event_dates, "post_event_30d": post}


def _cached_by_city_date() -> dict[tuple[str, str], dict[str, Any]]:
    if not SINGLE_DATE_AUDIT.exists():
        return {}
    try:
        document = json.loads(SINGLE_DATE_AUDIT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    for area in document.get("areas", []):
        bbox = area.get("bbox_wgs84")
        if not isinstance(bbox, list) or len(bbox) != 4:
            continue
        for observation in area.get("observations", []):
            item = observation.get("best_coverage_item")
            date = observation.get("target_date")
            if item and date:
                cache[(area.get("city", ""), date)] = {"bbox_wgs84": bbox, "item": item}
    return cache


def _load_completed(output_path: Path, input_hashes: dict[str, str]) -> dict[str, dict[str, Any]]:
    """Resume only when the frozen AOIs, candidate leads, and cache are unchanged."""
    try:
        previous = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if previous.get("input_sha256") != input_hashes:
        return {}
    return {row["city"]: row for row in previous.get("areas", []) if isinstance(row, dict) and row.get("city")}


def _measure_day(city: str, box: list[float], date: str,
                 cache: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    cached = cache.get((city, date))
    if cached and cached.get("bbox_wgs84") == box:
        item = cached["item"]
        return {"target_date": date, "status": "raster sampled (reused prior audit)",
                "best_coverage_item": item, "gfm_item_count": None,
                "other_raster_errors": []}
    body = {"collections": ["GFM"], "bbox": box,
            "datetime": f"{date}T00:00:00Z/{date}T23:59:59Z", "limit": 100}
    features = search_all(body)
    checked, errors = [], []
    for feature in features:
        try:
            checked.append(inspect_item(feature, box))
        except Exception as exc:  # Record item-level failures without hiding them.
            errors.append({"id": feature.get("id"), "error": f"{type(exc).__name__}: {exc}"})
    best = max(checked, key=lambda item: item.get("valid_fraction", 0), default=None)
    return {"target_date": date,
            "status": "raster sampled" if best else ("raster read failed" if errors else "no GFM item"),
            "best_coverage_item": best, "gfm_item_count": len(features),
            "other_raster_errors": errors}


def _period_summary(days: list[dict[str, Any]]) -> dict[str, Any]:
    fractions = [((row.get("best_coverage_item") or {}).get("valid_fraction")) for row in days]
    valid = [float(value) for value in fractions if value is not None]
    passing = sum(value >= MIN_VALID_FRACTION for value in valid)
    return {"date_slots": len(days), "readable_rasters": len(valid),
            "rasters_at_or_above_80_percent": passing,
            "meets_three_date_80_percent_screen": passing >= DATE_COUNT,
            "valid_fraction_by_date": {row["target_date"]: (row.get("best_coverage_item") or {}).get("valid_fraction")
                                       for row in days}}


def run() -> dict[str, Any]:
    register = list(csv.DictReader(REGISTER.open(encoding="utf-8", newline="")))
    lead_areas = json.loads(LEADS.read_text(encoding="utf-8"))["acquisition_opportunity_screen"]["areas"]
    leads = {row["city"]: row for row in lead_areas}
    input_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in (REGISTER, LEADS, SINGLE_DATE_AUDIT)}
    cache = _cached_by_city_date()
    completed = _load_completed(OUTPUT, input_hashes)
    output = {"audit": "Multi-date Copernicus GFM raster availability screen for ATLAS 8+8 candidate AOIs",
              "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "source": "Copernicus Global Flood Monitoring STAC collection GFM",
              "endpoint": API,
              "input_sha256": input_hashes,
              "date_selection": "Three nearest distinct OPERA metadata dates in the 30 days before and after the first Groundsource candidate lead, plus all OPERA metadata dates within the reported lead interval. Dates are candidate sampling windows, not verified flood-event dates.",
              "validity_rule": "A selected same-day COG is the intersecting item with the greatest fixed-AOI valid fraction; duplicates are not mosaicked. Each date passes at >=80% non-nodata pixels.",
              "independence_limit": "GFM and OPERA DSWx-S1 share Sentinel-1 lineage; GFM is not independent validation truth.",
              "enrollment_limit": "This diagnostic does not verify events, measure OPERA pixels, provide independent labels, or establish confirmatory eligibility.",
              "areas": []}
    for area in register:
        city = area["city"]
        if city in completed:
            output["areas"].append(completed[city])
            print(city, "already saved; skipping", flush=True)
            continue
        candidate = leads[city]["top_candidates"][0]
        dates = _target_dates(candidate)
        box = [float(value) for value in area["aoi_bbox_wgs84"].split(",")]
        periods = {}
        for period, target_dates in dates.items():
            rows = [_measure_day(city, box, date, cache) for date in target_dates]
            periods[period] = {"observations": rows, **_period_summary(rows)}
        record = {"region": area["region"], "city": city, "bbox_wgs84": box,
                  "candidate_event_id": candidate.get("event_id"),
                  "candidate_event_interval": [candidate.get("reported_start_date"), candidate.get("reported_end_date")],
                  "candidate_lead_status": candidate.get("screen_status"),
                  "periods": periods,
                  "pre_post_matched_three_date_screen": bool(
                      periods["pre_event_30d"]["meets_three_date_80_percent_screen"] and
                      periods["post_event_30d"]["meets_three_date_80_percent_screen"]),
                  "confirmatory_eligible": False,
                  "confirmatory_reason": "Event verification, three QA-valid target-product dates per period, independent licensed reference labels, probability sampling, and precision gates remain unmet."}
        output["areas"].append(record)
        OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        print(city, {name: f"{period['rasters_at_or_above_80_percent']}/{period['date_slots']}"
                     for name, period in periods.items()}, flush=True)
    output["summary"] = {"candidate_areas": len(output["areas"]),
                         "us_areas": sum(row["region"] == "United States" for row in output["areas"]),
                         "international_areas": sum(row["region"] != "United States" for row in output["areas"]),
                         "date_slots_screened": sum(sum(period["date_slots"] for period in row["periods"].values()) for row in output["areas"]),
                         "areas_with_at_least_one_80_percent_candidate_event_raster": sum(
                             any((observation.get("best_coverage_item") or {}).get("valid_fraction", 0) >= MIN_VALID_FRACTION
                                 for observation in row["periods"]["candidate_event"]["observations"])
                             for row in output["areas"]),
                         "areas_passing_three_pre_and_three_post_dates": sum(row["pre_post_matched_three_date_screen"] for row in output["areas"]),
                         "confirmatory_eligible_areas": 0}
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    result = run()
    print(json.dumps(result["summary"], indent=2))
