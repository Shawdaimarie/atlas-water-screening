#!/usr/bin/env python3
"""Read native OPERA BWTR pixels over the fixed Tampa candidate AOI.

The script uses HTTP byte ranges through GDAL's /vsicurl/ handler; it does not
download or persist the full source GeoTIFF. It is a focused source-access and
pixel-QA audit, not a flood-event validation workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform
from rasterio.windows import Window, from_bounds, transform as window_transform


BASE_URL = "https://aria-share.jpl.nasa.gov/20240926-Hurricane_Helene/DSWx"
DATES = ("20240914", "20240926")
INVALID_CLASSES = {250, 251, 255}
VALID_CLASSES = {0, 1}


def _densified_bbox_geometry(bbox: tuple[float, float, float, float]) -> dict[str, Any]:
    xmin, ymin, xmax, ymax = bbox
    points: list[tuple[float, float]] = []
    for i in range(101):
        t = i / 100
        points.extend(
            (
                (xmin + (xmax - xmin) * t, ymin),
                (xmax, ymin + (ymax - ymin) * t),
                (xmax - (xmax - xmin) * t, ymax),
                (xmin, ymax - (ymax - ymin) * t),
            )
        )
    return {"points": points}


def _source_headers(url: str) -> dict[str, Any]:
    head = urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60)
    with head:
        headers = head.headers
        result = {
            "http_status": head.status,
            "content_length_bytes": int(headers["Content-Length"]),
            "etag": headers.get("ETag"),
            "last_modified": headers.get("Last-Modified"),
            "content_type": headers.get("Content-Type"),
        }
    request = urllib.request.Request(url, headers={"Range": "bytes=0-1023"})
    with urllib.request.urlopen(request, timeout=60) as response:
        first_kib = response.read(1024)
        result["range_probe"] = {
            "http_status": response.status,
            "content_range": response.headers.get("Content-Range"),
            "bytes_read": len(first_kib),
            "first_1024_bytes_sha256": hashlib.sha256(first_kib).hexdigest(),
        }
    return result


def _covering_window(fractional_window: Window, width: int, height: int) -> Window:
    """Return an in-raster window enclosing the bounds plus a one-pixel margin."""
    col_start = max(0, math.floor(fractional_window.col_off) - 1)
    row_start = max(0, math.floor(fractional_window.row_off) - 1)
    col_stop = min(
        width, math.ceil(fractional_window.col_off + fractional_window.width) + 1
    )
    row_stop = min(
        height, math.ceil(fractional_window.row_off + fractional_window.height) + 1
    )
    if col_stop <= col_start or row_stop <= row_start:
        raise ValueError("The study AOI does not overlap the source raster.")
    return Window(col_start, row_start, col_stop - col_start, row_stop - row_start)


def _summarize_classes(values: np.ndarray) -> dict[str, Any]:
    counts = Counter(int(value) for value in values)
    aoi_pixels = int(values.size)
    valid_pixels = sum(counts.get(value, 0) for value in VALID_CLASSES)
    invalid_pixels = sum(counts.get(value, 0) for value in INVALID_CLASSES)
    unexpected = {
        str(value): count
        for value, count in sorted(counts.items())
        if value not in VALID_CLASSES | INVALID_CLASSES
    }
    valid_fraction = valid_pixels / aoi_pixels if aoi_pixels else None
    return {
        "aoi_pixel_count": aoi_pixels,
        "class_counts": {str(value): count for value, count in sorted(counts.items())},
        "valid_pixel_count": valid_pixels,
        "invalid_pixel_count": invalid_pixels,
        "unexpected_class_counts": unexpected,
        "valid_fraction": valid_fraction,
        "water_fraction_of_valid_pixels": counts.get(1, 0) / valid_pixels if valid_pixels else None,
        "passes_80_percent_valid_pixel_floor": bool(
            valid_fraction is not None and valid_fraction >= 0.80 and not unexpected
        ),
    }


def audit_date(date: str, bbox: tuple[float, float, float, float]) -> dict[str, Any]:
    filename = f"{date}_DSWx-S1_BWTR.tif"
    source_url = f"{BASE_URL}/{filename}"
    source_path = f"/vsicurl/{source_url}"
    source = _source_headers(source_url)
    points = _densified_bbox_geometry(bbox)["points"]
    with rasterio.open(source_path) as dataset:
        xs, ys = transform(
            "EPSG:4326",
            dataset.crs,
            [point[0] for point in points],
            [point[1] for point in points],
        )
        geometry = {"type": "Polygon", "coordinates": [list(zip(xs, ys))]}
        aoi_x = xs
        aoi_y = ys
        fractional_window = from_bounds(
            min(aoi_x), min(aoi_y), max(aoi_x), max(aoi_y), dataset.transform
        )
        window = _covering_window(fractional_window, dataset.width, dataset.height)
        pixels = dataset.read(1, window=window)
        inside = geometry_mask(
            [geometry],
            out_shape=pixels.shape,
            transform=window_transform(window, dataset.transform),
            invert=True,
            all_touched=False,
        )
        values = pixels[inside]
        summary = _summarize_classes(values)
        return {
            "acquisition_date": f"{date[:4]}-{date[4:6]}-{date[6:]}",
            "asset_name": filename,
            "source_url": source_url,
            "source_headers_and_range_probe": source,
            "raster": {
                "driver": dataset.driver,
                "width_pixels": dataset.width,
                "height_pixels": dataset.height,
                "band_count": dataset.count,
                "band": 1,
                "dtype": dataset.dtypes[0],
                "crs": str(dataset.crs),
                "pixel_size_m": list(dataset.res),
                "nodata": dataset.nodata,
                "selected_metadata_tags": {
                    key: dataset.tags().get(key)
                    for key in (
                        "DSWX_PRODUCT_VERSION",
                        "PRODUCT_TYPE",
                        "PRODUCT_SOURCE",
                        "SOFTWARE_VERSION",
                        "RTC_TRACK_NUMBER",
                        "RTC_ABSOLUTE_ORBIT_NUMBER",
                        "RTC_ORBIT_PASS_DIRECTION",
                        "PROCESSING_DATETIME",
                        "SPATIAL_COVERAGE",
                    )
                },
            },
            "aoi_sampling": {
                "bbox_wgs84": list(bbox),
                "pixel_rule": "pixel center within densified projected AOI polygon (all_touched=false)",
                "window": {
                    "column_offset": int(window.col_off),
                    "row_offset": int(window.row_off),
                    "width": int(window.width),
                    "height": int(window.height),
                },
                **summary,
                "valid_classes_0_nonwater_1_water": sorted(VALID_CLASSES),
                "invalid_classes": sorted(INVALID_CLASSES),
            },
            "full_source_sha256": None,
            "full_source_sha256_note": "Full GeoTIFF was not downloaded; integrity metadata records server ETag and a SHA-256 of the first 1 KiB range response.",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    register = json.loads(Path("data/study_area_register.json").read_text())
    tampa = next(area for area in register["results"] if area["city"] == "Tampa")
    bbox = tuple(float(value) for value in tampa["aoi_bbox_wgs84"].split(","))
    results = [audit_date(date, bbox) for date in DATES]
    document = {
        "audit": "Native OPERA DSWx-S1 V1 BWTR pixel audit for the fixed Tampa Hurricane Helene candidate AOI",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "study_area_register_sha256": hashlib.sha256(Path("data/study_area_register.json").read_bytes()).hexdigest(),
        "study_area": {
            "city": tampa["city"],
            "region": tampa["region"],
            "aoi_bbox_wgs84": list(bbox),
            "aoi_area_km2_nominal": tampa["aoi_area_km2"],
        },
        "product": {
            "name": "OPERA_L3_DSWX-S1_V1",
            "band": "BWTR_Binary_water",
            "class_interpretation": {"0": "valid non-water", "1": "valid water", "250": "invalid", "251": "invalid", "255": "nodata/invalid"},
            "source_limit": "NASA/JPL service metadata describes these products as preliminary and unvalidated.",
            "validation_limit": "Two single scenes do not constitute event/baseline sampling, independent reference labels, or an estimate of classification accuracy.",
        },
        "scenes": results,
        "eligibility_result": "not eligible for confirmatory enrollment: fewer than three QA-valid dates per period and no independent reference-label comparison",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "scene_count": len(results), "summary": [
        {"date": scene["acquisition_date"], "aoi_pixels": scene["aoi_sampling"]["aoi_pixel_count"], "classes": scene["aoi_sampling"]["class_counts"], "valid_fraction": scene["aoi_sampling"]["valid_fraction"], "water_fraction": scene["aoi_sampling"]["water_fraction_of_valid_pixels"], "passes_80_percent_floor": scene["aoi_sampling"]["passes_80_percent_valid_pixel_floor"]}
        for scene in results
    ]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
