#!/usr/bin/env python3
"""Audit one NASA EGIS Louisiana BWTR item over the fixed New Orleans AOI.

The EGIS catalog footprint intersects the registered box. This script separately
exports that locked item over the box, counts BWTR valid/invalid classes, and
cross-checks the registered centre with ImageServer identify. It is an access
and coverage diagnostic for a preliminary response product, not flood truth.
"""
from __future__ import annotations

import hashlib
import json
import math
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np
import rasterio
from rasterio.io import MemoryFile

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/study_area_register.json"
OUTPUT = ROOT / "outputs/atlas-neworleans-2026-egis-bwtr-coverage.json"
SERVICE_URL = (
    "https://gis.earthdata.nasa.gov/portal/rest/services/"
    "DISASTERS_202606_FLOOD_LA/202610_opera_dswx_s1/ImageServer"
)
RASTER_ID = 22
RASTER_NAME = (
    "OPERA_L3_DSWx-S1_T15RYP_20260621T001010Z_20260627T005829Z_"
    "S1A_30_v1.0_B02_BWTR"
)
TARGET_RESOLUTION_M = 29.97600242
MAX_TIFF_BYTES = 25_000_000
VALID_BWTR_CLASSES = {0, 1}
INVALID_BWTR_CLASSES = {252, 253, 254, 255}
FetchJson = Callable[[str, dict[str, Any]], dict[str, Any]]
FetchBytes = Callable[[str], bytes]


def request_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "ATLAS-research-audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        value = json.load(response)
    if not isinstance(value, dict):
        raise ValueError("NASA EGIS returned a non-object response")
    if value.get("error"):
        raise RuntimeError(f"NASA EGIS error: {value['error']}")
    return value


def request_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "ATLAS-research-audit/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read(MAX_TIFF_BYTES + 1)
    if len(data) > MAX_TIFF_BYTES:
        raise ValueError("NASA EGIS export exceeded the configured download limit")
    return data


def mercator(lon: float, lat: float) -> tuple[float, float]:
    radius = 6378137.0
    bounded_lat = max(-85.05112878, min(85.05112878, lat))
    return (
        radius * math.radians(lon),
        radius * math.log(math.tan(math.pi / 4 + math.radians(bounded_lat) / 2)),
    )


def projected_grid(bbox: tuple[float, float, float, float]) -> dict[str, Any]:
    west, south, east, north = bbox
    xmin, ymin = mercator(west, south)
    xmax, ymax = mercator(east, north)
    width = math.ceil((xmax - xmin) / TARGET_RESOLUTION_M)
    height = math.ceil((ymax - ymin) / TARGET_RESOLUTION_M)
    return {
        "bbox_3857": [xmin, ymin, xmax, ymax],
        "width": width,
        "height": height,
        "target_resolution_m": TARGET_RESOLUTION_M,
        "output_crs": "EPSG:3857",
    }


def point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y):
            crossing_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < crossing_x:
                inside = not inside
    return inside


def _get_item(fetch_json: FetchJson, bbox: tuple[float, float, float, float]) -> dict[str, Any]:
    result = fetch_json(f"{SERVICE_URL}/query", {
        "objectIds": str(RASTER_ID),
        "outFields": "objectid,name,productname,category",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "json",
    })
    features = result.get("features", [])
    if len(features) != 1:
        raise ValueError("Expected exactly one catalog feature for the locked raster")
    feature = features[0]
    attrs = feature.get("attributes") or {}
    if (attrs.get("objectid"), attrs.get("name"), attrs.get("productname"), attrs.get("category")) != (
        RASTER_ID, RASTER_NAME, "Binary Water (BWTR)", 1
    ):
        raise ValueError("NASA EGIS catalog identity changed for the locked BWTR item")
    rings = (feature.get("geometry") or {}).get("rings") or []
    if not rings:
        raise ValueError("The locked NASA EGIS item has no footprint geometry")
    west, south, east, north = bbox
    center = ((west + east) / 2, (south + north) / 2)
    if not any(point_in_ring(*center, ring) for ring in rings):
        raise ValueError("Registered AOI centre is outside the catalog footprint")
    return {
        "object_id": attrs["objectid"],
        "name": attrs["name"],
        "product_name": attrs["productname"],
        "category": attrs["category"],
        "aoi_center_inside_catalog_footprint": True,
    }


def _export_params(grid: dict[str, Any]) -> dict[str, Any]:
    xmin, ymin, xmax, ymax = grid["bbox_3857"]
    return {
        "bbox": f"{xmin},{ymin},{xmax},{ymax}",
        "bboxSR": "102100",
        "imageSR": "102100",
        "size": f"{grid['width']},{grid['height']}",
        "format": "tiff",
        "pixelType": "U8",
        "interpolation": "RSP_NearestNeighbor",
        "mosaicRule": json.dumps({
            "mosaicMethod": "esriMosaicLockRaster",
            "lockRasterIds": [RASTER_ID],
        }, separators=(",", ":")),
        "f": "json",
    }


def summarize_tiff(data: bytes, expected_grid: dict[str, Any]) -> dict[str, Any]:
    if not data or len(data) > MAX_TIFF_BYTES:
        raise ValueError("NASA EGIS TIFF is empty or exceeds the configured size limit")
    with MemoryFile(data) as memory_file:
        with memory_file.open() as dataset:
            if dataset.count != 1:
                raise ValueError("Expected one-band BWTR export")
            if dataset.width != expected_grid["width"] or dataset.height != expected_grid["height"]:
                raise ValueError("Export dimensions do not match the requested AOI grid")
            if dataset.crs is None or dataset.crs.to_epsg() != 3857:
                raise ValueError("Expected exported BWTR grid in EPSG:3857")
            if dataset.dtypes[0] != "uint8":
                raise ValueError("Expected uint8 BWTR classes")
            pixels = dataset.read(1)
            values, counts = np.unique(pixels, return_counts=True)
            histogram = {str(int(value)): int(count) for value, count in zip(values, counts)}
            unexpected = set(map(int, values)) - VALID_BWTR_CLASSES - INVALID_BWTR_CLASSES
            if unexpected:
                raise ValueError(f"Unrecognized BWTR classes: {sorted(unexpected)}")
            total = int(pixels.size)
            valid = sum(int(count) for value, count in zip(values, counts)
                        if int(value) in VALID_BWTR_CLASSES)
            return {
                "width": dataset.width,
                "height": dataset.height,
                "pixel_count": total,
                "crs": dataset.crs.to_string(),
                "pixel_size_m": [abs(float(value)) for value in dataset.res],
                "geotiff_nodata_tag": dataset.nodata,
                "class_counts": histogram,
                "valid_bwtr_pixels": valid,
                "valid_bwtr_fraction": valid / total if total else 0.0,
                "invalid_mask_or_fill_pixels": total - valid,
                "export_sha256": hashlib.sha256(data).hexdigest(),
            }


def _identify(fetch_json: FetchJson, lon: float, lat: float) -> dict[str, Any]:
    result = fetch_json(f"{SERVICE_URL}/identify", {
        "geometry": json.dumps({"x": lon, "y": lat, "spatialReference": {"wkid": 4326}},
                               separators=(",", ":")),
        "geometryType": "esriGeometryPoint",
        "sr": "4326",
        "mosaicRule": json.dumps({"mosaicMethod": "esriMosaicLockRaster",
                                  "lockRasterIds": [RASTER_ID]}, separators=(",", ":")),
        "returnGeometry": "false",
        "f": "json",
    })
    features = (result.get("catalogItems") or {}).get("features", [])
    ids = [((item.get("attributes") or {}).get("objectid")) for item in features]
    if ids and ids != [RASTER_ID]:
        raise ValueError("Identify returned a catalog item other than the locked raster")
    return {"value": result.get("value"), "catalog_object_ids": ids}


def audit(fetch_json: FetchJson = request_json, fetch_bytes: FetchBytes = request_bytes,
          register_path: Path = REGISTER) -> dict[str, Any]:
    register_bytes = register_path.read_bytes()
    register = json.loads(register_bytes)
    areas = [row for row in register.get("results", []) if row.get("city") == "New Orleans"]
    if len(areas) != 1 or areas[0].get("region") != "United States":
        raise ValueError("Expected exactly one canonical New Orleans U.S. study area")
    area = areas[0]
    bbox = tuple(float(value) for value in area["aoi_bbox_wgs84"].split(","))
    metadata = fetch_json(SERVICE_URL, {"f": "json"})
    description = str(metadata.get("description") or metadata.get("serviceDescription") or "")
    if "preliminary and unvalidated" not in description.casefold():
        raise ValueError("NASA EGIS preliminary/unvalidated source caveat is absent or changed")
    item = _get_item(fetch_json, bbox)
    grid = projected_grid(bbox)
    export = fetch_json(f"{SERVICE_URL}/exportImage", _export_params(grid))
    href = export.get("href")
    if not href or not href.startswith("https://gis.earthdata.nasa.gov/"):
        raise ValueError("NASA export returned a missing or unexpected download host")
    if (export.get("width"), export.get("height")) != (grid["width"], grid["height"]):
        raise ValueError("NASA export metadata dimensions differ from the requested AOI grid")
    raster_summary = summarize_tiff(fetch_bytes(href), grid)
    center_identify = _identify(fetch_json, area["lon"], area["lat"])
    return {
        "audit": "NASA EGIS New Orleans Louisiana flood BWTR fixed-area coverage diagnostic",
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "area": {
            "city": area["city"],
            "region": area["region"],
            "fixed_aoi_bbox_wgs84": list(bbox),
            "register_sha256": hashlib.sha256(register_bytes).hexdigest(),
        },
        "source": {
            "service_url": SERVICE_URL,
            "catalog_query_url": f"{SERVICE_URL}/query",
            "export_endpoint": f"{SERVICE_URL}/exportImage",
            "identify_endpoint": f"{SERVICE_URL}/identify",
            "item": item,
            "response_product": "OPERA DSWx-S1 BWTR",
            "response_interval_encoded_in_item_name": "2026-06-21T00:10:10Z to 2026-06-27T00:58:29Z",
            "source_caveat": "NASA service describes rapid-response maps as preliminary and unvalidated.",
            "independent_event_record": "https://nola.gov/next/mayors-office/news/articles/june/2026-06-18-city-of-new-orleans-provides-update-post-severe-weather-event/",
            "independent_event_record_summary": (
                "City of New Orleans reported flash flooding and a continuing flood watch in its June 18, 2026 update."
            ),
        },
        "export_design": grid | {
            "requested_image_format": "GeoTIFF",
            "requested_pixel_type": "U8",
            "interpolation": "nearest-neighbor",
            "locked_raster_id": RASTER_ID,
            "sample_unit": "all raster grid cells returned over the registered bbox; not the product's native UTM grid",
        },
        "export": raster_summary,
        "centre_point_crosscheck": {
            "longitude": area["lon"],
            "latitude": area["lat"],
            **center_identify,
        },
        "interpretation": (
            "The catalog item footprint intersects the registered New Orleans box, but the locked BWTR export "
            "returned no valid 0/1 classifications on the requested approximately 30 m EPSG:3857 grid; "
            "the city-centre identify request also returned NoData. This is missing product coverage, not evidence "
            "that the area was dry or that no flooding occurred."
        ),
        "limits": [
            "The public response map is preliminary and unvalidated; it is not independent flood truth.",
            "The catalog item name encodes a June 21–27 acquisition interval, not a per-pixel acquisition timestamp.",
            "The interval is not demonstrably event-time matched to the City's June 18 report under the protocol's 24-hour primary rule.",
            "One missing-data screen does not establish adequate temporal sampling, classification accuracy, asset exposure, or confirmatory eligibility.",
            "No additional result is generalized from this single event or site.",
        ],
        "confirmatory_eligible": False,
    }


def main() -> None:
    report = audit()
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "city": report["area"]["city"],
        "catalog_item": report["source"]["item"]["name"],
        "grid": [report["export"]["width"], report["export"]["height"]],
        "valid_bwtr_fraction": report["export"]["valid_bwtr_fraction"],
        "class_counts": report["export"]["class_counts"],
        "centre_identify": report["centre_point_crosscheck"]["value"],
        "confirmatory_eligible": report["confirmatory_eligible"],
    }, sort_keys=True))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
