#!/usr/bin/env python3
"""Screen public Sentinel-1 RTC scene-date metadata for all ATLAS study AOIs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests


API = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
COLLECTION = "sentinel-1-rtc"
DEFAULT_START = "2024-09-01T00:00:00Z"
DEFAULT_END = "2026-11-02T23:59:59Z"


def query_area(
    session: requests.Session,
    area: dict[str, object],
    start: str,
    end: str,
) -> dict[str, object]:
    xmin, ymin, xmax, ymax = map(
        float, str(area["aoi_bbox_wgs84"]).split(",")
    )
    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [xmin, ymin],
                [xmax, ymin],
                [xmax, ymax],
                [xmin, ymax],
                [xmin, ymin],
            ]
        ],
    }
    body: dict[str, object] = {
        "collections": [COLLECTION],
        "intersects": polygon,
        "datetime": f"{start}/{end}",
        "limit": 100,
    }
    dates: set[str] = set()
    item_count = 0
    pages = 0
    while True:
        response = session.post(API, json=body, timeout=60)
        response.raise_for_status()
        page = response.json()
        pages += 1
        for item in page.get("features", []):
            item_count += 1
            timestamp = item.get("properties", {}).get("datetime")
            if timestamp:
                dates.add(str(timestamp)[:10])
        next_link = next(
            (link for link in page.get("links", []) if link.get("rel") == "next"),
            None,
        )
        if next_link is None:
            break
        body = next_link.get("body", {})
        if pages > 100:
            raise RuntimeError(f"Pagination exceeded 100 pages for {area['city']}")

    ordered_dates = sorted(dates)
    return {
        "region": area["region"],
        "city": area["city"],
        "aoi_bbox_wgs84": area["aoi_bbox_wgs84"],
        "item_count": item_count,
        "distinct_dates": len(ordered_dates),
        "first_date": ordered_dates[0] if ordered_dates else None,
        "last_date": ordered_dates[-1] if ordered_dates else None,
        "dates": ordered_dates,
        "year_months": sorted({value[:7] for value in ordered_dates}),
        "pages_read": pages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--areas", type=Path, default=Path("data/study_area_register.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/atlas-sentinel1-rtc-coverage-audit.json"))
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    args = parser.parse_args()

    areas = json.loads(args.areas.read_text(encoding="utf-8"))["results"]
    with requests.Session() as session:
        session.headers.update({"User-Agent": "ATLAS-RTC-coverage-audit/1.0"})
        results = [query_area(session, area, args.start, args.end) for area in areas]

    date_sets = [set(row["dates"]) for row in results]
    month_sets = [set(row["year_months"]) for row in results]
    common_dates = sorted(set.intersection(*date_sets)) if date_sets else []
    all_months = set.union(*month_sets) if month_sets else set()
    common_months = sorted(set.intersection(*month_sets)) if month_sets else []
    report = {
        "collection": COLLECTION,
        "api": API,
        "query_window": [args.start, args.end],
        "spatial_method": "STAC intersects against each registered WGS84 AOI bounding polygon",
        "area_count": len(results),
        "results": results,
        "temporal_summary": {
            "exact_acquisition_dates_common_to_all_areas": len(common_dates),
            "common_dates": common_dates,
            "shared_year_months": common_months,
            "months_with_any_area": len(all_months),
            "months_with_metadata_in_all_areas": len(common_months),
            "shared_month_fraction": round(len(common_months) / len(all_months), 4)
            if all_months
            el