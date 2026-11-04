#!/usr/bin/env python3
"""Measure actual GEOID-Flood label coverage in the St. Louis candidate AOI.

This follows the pinned catalog's intersecting EMSR203 label chips, verifies
the label-only shard hash, mosaics only those 12 chips in memory, and counts
published classes inside the fixed ATLAS AOI. It is historical training-split
diagnostic evidence, not current-window or held-out validation.
"""
from __future__ import annotations

import hashlib
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import numpy as np
import pyarrow.parquet as pq
import rasterio
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile
from rasterio.merge import merge
from rasterio.warp import transform_geom
from shapely import wkb
from shapely.geometry import box, mapping


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/study_area_register.json"
CATALOG = ROOT / "work/geoid-flood-pinned/tile_catalog.parquet"
CATALOG_SHA256 = "8599287a1a8cffc73014938a72698acd360414e47fbc54cdaa953b4ce3ab0e6d"
REVISION = "15db1cc0babbe3e570aa9fb582823c533504c971"
SHARD_PATH = "geoid-flood/shards/train/label/train-label-00000-of-00001.tar"
SHARD_URL = f"https://huggingface.co/datasets/links-ads/geoid-flood/resolve/{REVISION}/{SHARD_PATH}"
SHARD_SHA256 = "fc68e4cfbbf95db0e466552bf572b3fc7050d83bdfdeeef3f5deee3e3dab58ab"
SHARD_BYTES = 74_137_600
OUTPUT = ROOT / "outputs/atlas-geoid-flood-stlouis-label-coverage.json"
REPORT = ROOT / "outputs/atlas-geoid-flood-stlouis-label-coverage.md"


def fetch_shard(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with urlopen(SHARD_URL, timeout=120) as response, path.open("wb") as output:
            total = 0
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > SHARD_BYTES:
                    raise ValueError("GEOID-Flood label shard exceeded its pinned size")
                output.write(chunk)
    size = path.stat().st_size
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if size != SHARD_BYTES or digest != SHARD_SHA256:
        raise ValueError("GEOID-Flood label shard size or SHA-256 differs from the pinned release")
    return digest


def class_summary(pixels: np.ndarray) -> dict[str, Any]:
    if pixels.ndim != 1 or pixels.size == 0:
        raise ValueError("Expected a nonempty one-dimensional AOI label sample")
    values, counts = np.unique(pixels, return_counts=True)
    histogram = {str(int(value)): int(count) for value, count in zip(values, counts)}
    unexpected = set(map(int, values)) - {0, 1, 2, 255}
    if unexpected:
        raise ValueError(f"Unexpected GEOID-Flood label classes: {sorted(unexpected)}")
    total = int(pixels.size)
    valid = total - histogram.get("255", 0)
    return {
        "pixel_count": total,
        "class_counts": histogram,
        "mapped_label_pixels": valid,
        "mapped_label_fraction": valid / total,
        "flooded_water_pixels": histogram.get("2", 0),
        "flooded_water_fraction_of_all_aoi_pixels": histogram.get("2", 0) / total,
        "outside_map_pixels": histogram.get("255", 0),
    }


def audit(register_path: Path = REGISTER, catalog_path: Path = CATALOG,
          shard_path: Path = ROOT / "work/geoid-flood-pinned/train-label-00000-of-00001.tar") -> dict[str, Any]:
    catalog_bytes = catalog_path.read_bytes()
    catalog_hash = hashlib.sha256(catalog_bytes).hexdigest()
    if catalog_hash != CATALOG_SHA256:
        raise ValueError("GEOID-Flood catalog SHA-256 differs from the pinned release")
    records = pq.read_table(catalog_path).to_pylist()
    register_bytes = register_path.read_bytes()
    areas = json.loads(register_bytes).get("results", [])
    matches = [area for area in areas if area.get("city") == "St. Louis" and area.get("region") == "United States"]
    if len(matches) != 1:
        raise ValueError("Expected exactly one registered U.S. St. Louis area")
    area = matches[0]
    west, south, east, north = map(float, area["aoi_bbox_wgs84"].split(","))
    aoi = box(west, south, east, north)
    catalog_rows = [
        row for row in records
        if row["event_id"] == "EMSR203"
        and wkb.loads(row["geometry"]).intersects(aoi)
    ]
    if not catalog_rows or {row["split"] for row in catalog_rows} != {"train"}:
        raise ValueError("Pinned catalog no longer has the expected St. Louis training rows")
    if {str(row["tile_id"]) for row in catalog_rows} != {"5"}:
        raise ValueError("Pinned catalog no longer maps the St. Louis rows to the expected tile")
    bbox_ids = sorted({int(row["bbox_id"]) for row in catalog_rows})
    if len(bbox_ids) != 12:
        raise ValueError("Expected 12 catalog label chips intersecting the fixed St. Louis AOI")
    shard_hash = fetch_shard(shard_path)

    memories: list[MemoryFile] = []
    datasets = []
    try:
        with tarfile.open(shard_path, mode="r:") as archive:
            for bbox_id in bbox_ids:
                member_name = f"EMSR203-5/label/EMSR203-5-{bbox_id}_label.tif"
                member = archive.getmember(member_name)
                if not member.isfile() or member.size > 20_000_000:
                    raise ValueError("Unexpected or oversized label chip in GEOID-Flood shard")
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError("Missing label chip bytes in GEOID-Flood shard")
                memory = MemoryFile(stream.read())
                dataset = memory.open()
                if dataset.count != 1 or dataset.dtypes[0] != "uint8" or dataset.crs is None or dataset.crs.to_epsg() != 32615:
                    raise ValueError("Unexpected GEOID-Flood label chip raster metadata")
                if (dataset.width, dataset.height) != (1024, 1024):
                    raise ValueError("Unexpected GEOID-Flood label chip dimensions")
                memories.append(memory)
                datasets.append(dataset)
        mosaic, transform = merge(datasets)
    finally:
        for dataset in datasets:
            dataset.close()
        for memory in memories:
            memory.close()

    aoi_utm = transform_geom("EPSG:4326", "EPSG:32615", mapping(aoi))
    inside = geometry_mask([aoi_utm], out_shape=mosaic.shape[1:], transform=transform, invert=True)
    summary = class_summary(mosaic[0][inside])
    return {
        "audit_id": "atlas-geoid-flood-stlouis-label-coverage",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "area": {
            "region": area["region"],
            "city": area["city"],
            "fixed_aoi_bbox_wgs84": [west, south, east, north],
            "register_sha256": hashlib.sha256(register_bytes).hexdigest(),
        },
        "source": {
            "dataset": "links-ads/geoid-flood",
            "revision": REVISION,
            "catalog_sha256": catalog_hash,
            "catalog_rows_intersecting_aoi": len(catalog_rows),
            "event_id": "EMSR203",
            "event_date": "2017-04-28",
            "benchmark_split": "train",
            "label_shard_path": SHARD_PATH,
            "label_shard_bytes": SHARD_BYTES,
            "label_shard_sha256": shard_hash,
            "label_license": "CC BY 4.0; retain dataset and Copernicus attribution",
            "label_classes": {"0": "background", "1": "permanent water", "2": "flooded water", "255": "outside mapped area / ignore"},
        },
        "raster": {
            "chip_count": len(datasets),
            "bbox_ids": bbox_ids,
            "crs": "EPSG:32615",
            "pixel_size_m": 10,
            "mosaic_shape": list(mosaic.shape),
            "grid_transform": list(transform)[:6],
            **summary,
        },
        "interpretation_limits": [
            "The label chips belong to the GEOID-Flood training split and a 2017 event outside the common ATLAS 2024-2026 window.",
            "Catalog tile-footprint union coverage is not the same as in-AOI mapped-label coverage; class 255 pixels are outside mapped areas and excluded from label assessment.",
            "This is an operational expert reference, not absolute ground truth; no OPERA comparison, independent adjudication, sample frame, or confirmatory enrollment was performed.",
            "This source result adds no score points and does not change 0/16 confirmatory eligibility.",
        ],
    }


def main() -> None:
    result = audit()
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    r = result["raster"]
    REPORT.write_text(
        "# GEOID-Flood St. Louis label coverage audit\n\n"
        "**Run:** 2026-11-04\n\n"
        "Inspected the 12 pinned GEOID-Flood label chips whose catalog footprints intersect the fixed 25 × 25 km St. Louis AOI. "
        f"Inside the AOI, {r['mapped_label_pixels']:,}/{r['pixel_count']:,} 10 m pixels have mapped labels "
        f"({r['mapped_label_fraction']:.2%}); {r['outside_map_pixels']:,} pixels are class 255/outside the mapped label area. "
        f"Class counts are `{json.dumps(r['class_counts'], sort_keys=True)}`.\n\n"
        "This is EMSR203 (2017-04-28), in the GEOID-Flood **training** split. The result distinguishes label-pixel coverage from catalog tile-footprint coverage. "
        "It is historical diagnostic evidence only: it is outside the shared 2024–2026 window, has not been independently adjudicated, and adds no score or enrollment.\n\n"
        "The audit pins and verifies the 703,922-byte metadata catalog and 74,137,600-byte label shard by SHA-256, extracts only the 12 relevant TIFFs in memory, "
        "and counts classes within the registered AOI geometry. See [machine-readable result](atlas-geoid-flood-stlouis-label-coverage.json).\n"
    )
    print(json.dumps({"chip_count": r["chip_count"], "pixel_count": r["pixel_count"],
                      "mapped_label_fraction": r["mapped_label_fraction"],
                      "class_counts": r["class_counts"], "output": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
