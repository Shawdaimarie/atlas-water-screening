#!/usr/bin/env python3
"""Screen Google Groundsource news-event polygons against ATLAS AOIs.

This is event discovery only. It does not read satellite pixels or treat the
news-derived event polygons as flood-inundation labels or independent truth.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Iterable

import pyarrow.parquet as pq
from fsspec.implementations.http import HTTPFileSystem
from shapely import wkb
from shapely.geometry import box


RECORD_ID = "18647054"
API_URL = f"https://zenodo.org/api/records/{RECORD_ID}"
PARQUET_KEY = "groundsource_2026.parquet"
REGISTER_PATH = Path("data/study_area_register.json")
DEFAULT_OUTPUT = Path("outputs/atlas-groundsource-event-coverage-audit.json")
WINDOW_START = "2024-09-01"
WINDOW_END = "2026-02-03"


def _date(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        return dt.date.fromisoformat(value[:10]).isoformat()
    except ValueError:
        return None


def intersecting_records(
    rows: Iterable[dict[str, Any]], areas: list[dict[str, Any]],
    start_date: str = WINDOW_START, end_date: str = WINDOW_END,
) -> list[dict[str, Any]]:
    """Keep date-valid records whose WKB event geometry intersects an AOI box."""
    aoi_shapes = [
        (area, box(*map(float, area["aoi_bbox_wgs84"].split(","))))
        for area in areas
    ]
    aoi_shapes = [(area, aoi, aoi.bounds) for area, aoi in aoi_shapes]
    matches: list[dict[str, Any]] = []
    for row in rows:
        start = _date(row.get("start_date"))
        end = _date(row.get("end_date")) or start
        if start is None or end is None or end < start_date or start > end_date:
            continue
        geometry = row.get("geometry")
        if not geometry:
            continue
        shape = wkb.loads(geometry)
        min_x, min_y, max_x, max_y = shape.bounds
        for area, aoi, (aoi_min_x, aoi_min_y, aoi_max_x, aoi_max_y) in aoi_shapes:
            if (
                max_x < aoi_min_x or min_x > aoi_max_x
                or max_y < aoi_min_y or min_y > aoi_max_y
            ):
                continue
            if shape.intersects(aoi):
                matches.append({
                    "city": area["city"],
                    "region": area["region"],
                    "event_id": row.get("uuid"),
                    "start_date": start,
                    "end_date": end,
                    "reported_area_km2": row.get("area_km2"),
                    "match_basis": "news-derived event geometry intersects fixed WGS84 AOI envelope",
                })
    return matches


def summarize(matches: list[dict[str, Any]], areas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for area in areas:
        rows = [row for row in matches if row["city"] == area["city"]]
        event_ids = {row["event_id"] for row in rows if row["event_id"]}
        dates = sorted({row["start_date"] for row in rows})
        output.append({
            "city": area["city"],
            "region": area["region"],
            "intersecting_event_records": len(rows),
            "distinct_event_ids": len(event_ids),
            "distinct_start_dates": len(dates),
            "start_date_counts_by_year": {
                str(year): sum(day.startswith(f"{year}-") for day in dates)
                for year in range(int(WINDOW_START[:4]), int(WINDOW_END[:4]) + 1)
                if any(day.startswith(f"{year}-") for day in dates)
            },
            "start_date_range": [dates[0], dates[-1]] if dates else None,
        })
    return output


def audit(
    register_path: Path = REGISTER_PATH,
    api_get: Any | None = None,
    parquet_factory: Any | None = None,
) -> dict[str, Any]:
    if api_get is None:
        import requests
        api_get = lambda url: requests.get(url, timeout=60)
    if parquet_factory is None:
        parquet_factory = lambda url: pq.ParquetFile(
            HTTPFileSystem(block_size=8 * 1024 * 1024).open(url, "rb")
        )

    register = json.loads(register_path.read_text(encoding="utf-8"))
    areas = register["results"]
    if len(areas) != 16 or sum(a["region"] == "United States" for a in areas) != 8:
        raise ValueError("Expected the canonical 8 U.S. and 8 international AOI register")

    response = api_get(API_URL)
    response.raise_for_status()
    record = response.json()
    files = [item for item in record["files"] if item["key"] == PARQUET_KEY]
    if len(files) != 1:
        raise ValueError("Pinned Zenodo record did not return the expected parquet file")
    source_file = files[0]
    parquet = parquet_factory(source_file["links"]["self"])

    selected_groups = []
    rows: list[dict[str, Any]] = []
    group_dates = []
    for index in range(parquet.metadata.num_row_groups):
        group = parquet.metadata.row_group(index)
        stats = group.column(parquet.schema.names.index("start_date")).statistics
        if not stats or not stats.has_min_max:
            raise ValueError(f"Parquet row group {index} lacks start_date min/max statistics")
        group_dates.append({"row_group": index, "min": stats.min, "max": stats.max, "rows": group.num_rows})
        if stats.max < WINDOW_START or stats.min > WINDOW_END:
            continue
        selected_groups.append(index)
        table = parquet.read_row_group(index, columns=["uuid", "geometry", "start_date", "end_date", "area_km2"])
        data = table.to_pydict()
        rows.extend({key: data[key][i] for key in data} for i in range(table.num_rows))

    matches = intersecting_records(rows, areas)
    area_results = summarize(matches, areas)
    return {
        "schema_version": 1,
        "audit_id": "atlas-groundsource-event-coverage-audit",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": {
            "record_id": RECORD_ID,
            "doi": f"https://doi.org/10.5281/zenodo.{RECORD_ID}",
            "title": record["metadata"].get("title"),
            "license": (record["metadata"].get("license") or {}).get("id"),
            "file_key": PARQUET_KEY,
            "file_size_bytes": source_file["size"],
            "file_checksum": source_file.get("checksum"),
            "total_dataset_rows": parquet.metadata.num_rows,
            "all_row_group_date_ranges": group_dates,
            "screened_row_groups": selected_groups,
            "screened_source_rows": len(rows),
        },
        "analysis_window": {
            "start_inclusive": WINDOW_START,
            "end_inclusive": WINDOW_END,
            "source_max_available_event_date": WINDOW_END,
        },
        "spatial_test": "WKB event geometry intersects each fixed WGS84 AOI bounding envelope",
        "interpretation_limit": (
            "Groundsource records are machine-extracted from news reports and geolocated for event discovery. "
            "Their geometries are not satellite-derived inundation boundaries, field observations, independent "
            "flood labels, or proof that flooding occurred throughout the polygon. News coverage and extraction "
            "may be geographically and temporally biased. Intersections do not establish comparable sampling, "
            "pixel quality, event attribution, or confirmatory enrollment."
        ),
        "counts": {
            "candidate_areas": len(areas),
            "areas_with_intersecting_records": sum(a["intersecting_event_records"] > 0 for a in area_results),
            "intersecting_area_records": len(matches),
            "distinct_event_ids_across_area_matches": len({m["event_id"] for m in matches if m["event_id"]}),
        },
        "areas": area_results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=REGISTER_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = audit(args.register)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
