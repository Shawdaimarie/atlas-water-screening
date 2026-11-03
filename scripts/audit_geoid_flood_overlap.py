#!/usr/bin/env python3
"""Screen the GEOID-Flood tile catalog against ATLAS's fixed study AOIs.

Requires Python 3.12. Optional pinned dependencies: pyarrow==23.0.1,
shapely==2.0.7, with compatible NumPy pinned in the audit lock.
The audit reads the small pinned public Parquet catalog, never image shards.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import defaultdict
from pathlib import Path
from urllib.request import urlopen

import pyarrow
import pyarrow.parquet as pq
import shapely
from shapely import union_all, wkb
from shapely.geometry import box


DATASET = "links-ads/geoid-flood"
REVISION = "15db1cc0babbe3e570aa9fb582823c533504c971"
CATALOG_RELATIVE_PATH = "geoid-flood/tile_catalog.parquet"
CATALOG_URL = (
    f"https://huggingface.co/datasets/{DATASET}/resolve/"
    f"{REVISION}/{CATALOG_RELATIVE_PATH}?download=true"
)
CATALOG_SHA256 = "8599287a1a8cffc73014938a72698acd360414e47fbc54cdaa953b4ce3ab0e6d"
MAX_INVALID_FRACTION = 0.95


def load_catalog(path: Path) -> tuple[list[dict], str]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(CATALOG_URL, timeout=60) as response, path.open("wb") as out:
            while chunk := response.read(1024 * 1024):
                out.write(chunk)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != CATALOG_SHA256:
        raise ValueError(f"Catalog checksum mismatch: {digest}")
    table = pq.read_table(path)
    return table.to_pylist(), digest


def screen_areas(areas: list[dict], records: list[dict]) -> list[dict]:
    results = []
    for area in areas:
        west, south, east, north = map(float, area["aoi_bbox_wgs84"].split(","))
        aoi = box(west, south, east, north)
        intersecting = []
        for row in records:
            geometry = wkb.loads(row["geometry"])
            if geometry.intersects(aoi):
                intersecting.append((row, geometry.intersection(aoi)))

        by_event: dict[str, list[tuple[dict, object]]] = defaultdict(list)
        for row, clipped_geometry in intersecting:
            by_event[row["event_id"]].append((row, clipped_geometry))

        events = []
        for event_id, rows in sorted(by_event.items()):
            eligible = [
                (row, clipped)
                for row, clipped in rows
                if row["is_valid"] is True
                and row["invalid_pixel_frac"] is not None
                and row["invalid_pixel_frac"] <= MAX_INVALID_FRACTION
            ]
            footprint_fraction = (
                union_all([clipped for _, clipped in eligible]).area / aoi.area
                if eligible
                else 0.0
            )
            events.append(
                {
                    "event_id": event_id,
                    "event_time": sorted({r["event_time"] for r, _ in rows}),
                    "delineation_time_pre": sorted(
                        {r["delineation_time_pre"] for r, _ in rows}
                    ),
                    "delineation_time_post": sorted(
                        {r["delineation_time_post"] for r, _ in rows}
                    ),
                    "country": sorted({r["countries"] for r, _ in rows}),
                    "benchmark_split": sorted({r["split"] for r, _ in rows}),
                    "intersecting_tiles": len(rows),
                    "paper_eligible_tiles": len(eligible),
                    "eligible_invalid_pixel_fraction_min": min(
                        (r["invalid_pixel_frac"] for r, _ in eligible), default=None
                    ),
                    "eligible_invalid_pixel_fraction_max": max(
                        (r["invalid_pixel_frac"] for r, _ in eligible), default=None
                    ),
                    "eligible_tile_footprint_fraction_of_aoi": round(
                        footprint_fraction, 8
                    ),
                }
            )

        results.append(
            {
                "region": area["region"],
                "