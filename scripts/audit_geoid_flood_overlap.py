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
                "city": area["city"],
                "intersecting_tiles": len(intersecting),
                "paper_eligible_tiles": sum(
                    e["paper_eligible_tiles"] for e in events
                ),
                "events": events,
            }
        )
    return results


def main() -> None:
    if sys.version_info < (3, 12):
        raise SystemExit("Use Python 3.12 or newer for requirements-reference-audit.lock")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--register",
        type=Path,
        default=Path("data/study_area_register.json"),
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path("work/geoid-flood-pinned/tile_catalog.parquet"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/atlas-geoid-flood-overlap-audit.json"),
    )
    args = parser.parse_args()

    register = json.loads(args.register.read_text())
    rows, digest = load_catalog(args.catalog)
    areas = screen_areas(register["results"], rows)
    output = {
        "dataset": DATASET,
        "revision": REVISION,
        "catalog_path": CATALOG_RELATIVE_PATH,
        "catalog_url": CATALOG_URL,
        "catalog_sha256": digest,
        "audit_runtime": {
            "python": platform.python_version(),
            "pyarrow": pyarrow.__version__,
            "shapely": shapely.__version__,
        },
        "catalog_bytes": args.catalog.stat().st_size,
        "catalog_rows": len(rows),
        "aoi_source": str(args.register),
        "aoi_method": "exact polygon intersection against each fixed ATLAS WGS84 AOI bounding box",
        "paper_tile_filter": "is_valid is true and invalid_pixel_frac <= 0.95",
        "results": areas,
        "summary": {
            "study_areas": len(areas),
            "areas_with_reference_footprint": sum(
                a["intersecting_tiles"] > 0 for a in areas
            ),
            "tiles_in_registered_areas": sum(a["intersecting_tiles"] for a in areas),
            "paper_eligible_tiles_in_registered_areas": sum(
                a["paper_eligible_tiles"] for a in areas
            ),
            "event_ids_in_registered_areas": sorted(
                {e["event_id"] for a in areas for e in a["events"]}
            ),
        },
        "interpretation_limits": [
            "This is catalog-footprint screening, not pixel-level QA of the label or Sentinel-1 rasters.",
            "The source dataset describes manually validated three-class labels derived from CEMS Rapid Mapping products; they are operational expert references, not absolute ground truth.",
            "Paper tile eligibility is a benchmark filter, not the ATLAS per-area sampling adequacy rule.",
            "A footprint overlap does not establish event independence, held-out status, usable raster coverage, asset-level coverage, or adequate statistical sampling.",
        ],
        "license": "CC BY 4.0; retain attribution to GEOID-Flood and the Copernicus source products before redistribution.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(output["summary"], indent=2))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
