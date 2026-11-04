#!/usr/bin/env python3
"""Retrieve a fixed, stratified raw-pixel sample from NASA EGIS OPERA imagery.

The pilot is intentionally limited to the public NASA EGIS ImageServer for
Hurricane Helene. It samples the frozen Tampa AOI at the same 1,024 equal-area
locations in the pre-event and syn-event BWTR layers. This is an exploratory
data-path/coverage check, not full-AOI raster QA or independent flood truth.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import random
import re
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/study_area_register.json"
DEFAULT_JSON = ROOT / "outputs/atlas-tampa-helene-egis-pixel-sample.json"
DEFAULT_CSV = ROOT / "outputs/atlas-tampa-helene-egis-pixel-sample.csv"
SERVICE_URL = (
    "https://gis.earthdata.nasa.gov/portal/rest/services/"
    "DISASTERS_202409_HURRICANE_HELENE/202427_opera_dswx_s1/ImageServer"
)
SAMPLE_SEED = "ATLAS-Tampa-Helene-EGIS-BWTR-v1"
SAMPLES_PER_SCENE = 1024
STRATA_SIDE = 32
CHUNK_SIZE = 256
MIN_VALID_DATES_PER_PERIOD = 3
VALID_CLASSES = {0, 1}
INVALID_CLASSES = {250, 251, 255}


def _request_json(url: str, params: dict[str, Any], *, timeout: int = 60) -> dict[str, Any]:
    encoded = urllib.parse.urlencode(params).encode("utf-8")
    # Multipoint payloads exceed common URL limits, so send the same REST
    # parameters in a form-encoded POST body.
    request = urllib.request.Request(
        url,
        data=encoded,
        headers={
            "User-Agent": "ATLAS-research-audit/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        document = json.load(response)
    if not isinstance(document, dict):
        raise ValueError("NASA EGIS returned a non-object JSON response")
    if "error" in document:
        raise RuntimeError(f"NASA EGIS error: {document['error']}")
    return document


def _mercator(lon: float, lat: float) -> tuple[float, float]:
    radius = 6378137.0
    bounded_lat = max(-85.05112878, min(85.05112878, lat))
    return (
        radius * math.radians(lon),
        radius * math.log(math.tan(math.pi / 4 + math.radians(bounded_lat) / 2)),
    )


def equal_area_sample_points(
    bbox: tuple[float, float, float, float],
    *,
    side: int = STRATA_SIDE,
    seed: str = SAMPLE_SEED,
) -> list[dict[str, float | int | str]]:
    """Create one jittered point per equal-area longitude/sine-latitude stratum."""
    west, south, east, north = bbox
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError("AOI bbox must be ordered WGS84 longitude/latitude bounds")
    if side < 1:
        raise ValueError("side must be positive")
    south_sine, north_sine = math.sin(math.radians(south)), math.sin(math.radians(north))
    rng = random.Random(seed)
    points = []
    for row in range(side):
        for col in range(side):
            u_lon = (col + rng.random()) / side
            u_sin = (row + rng.random()) / side
            lon = west + u_lon * (east - west)
            sin_lat = south_sine + u_sin * (north_sine - south_sine)
            lat = math.degrees(math.asin(sin_lat))
            x, y = _mercator(lon, lat)
            points.append({
                "sample_id": f"p{len(points) + 1:04d}",
                "stratum_row": row,
                "stratum_col": col,
                "lon": lon,
                "lat": lat,
                "x_3857": x,
                "y_3857": y,
            })
    return points


def _date_utc(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, timezone.utc).date().isoformat()
    return str(value)[:10]


def _validate_item(attributes: dict[str, Any], *, object_id: int, expected_name: str,
                   expected_date: str) -> dict[str, Any]:
    actual_date = _date_utc(attributes.get("date"))
    if attributes.get("objectid") != object_id:
        raise ValueError(f"Expected raster id {object_id}, got {attributes.get('objectid')!r}")
    if attributes.get("name") != expected_name:
        raise ValueError(f"Expected raster {expected_name!r}, got {attributes.get('name')!r}")
    if actual_date != expected_date:
        raise ValueError(f"Expected {expected_date}, got {actual_date!r} for {expected_name}")
    product_name = attributes.get("productname")
    if product_name != "Binary Water Detection":
        raise ValueError(f"Expected a BWTR item, got {product_name!r}")
    return {
        "raster_id": object_id,
        "name": expected_name,
        "date_utc": expected_date,
        "product_name": product_name,
    }


def _fetch_item(fetch_json: Callable[..., dict[str, Any]], *, object_id: int,
                name: str, date: str) -> dict[str, Any]:
    result = fetch_json(f"{SERVICE_URL}/query", {
        "objectIds": str(object_id),
        "outFields": "objectid,name,date,productname,groupname",
        "returnGeometry": "false",
        "f": "json",
    })
    features = result.get("features", [])
    if len(features) != 1:
        raise ValueError(f"Expected one catalog item for raster id {object_id}; got {len(features)}")
    return _validate_item(features[0].get("attributes") or {}, object_id=object_id,
                          expected_name=name, expected_date=date)


def _sample_item(fetch_json: Callable[..., dict[str, Any]], item: dict[str, Any],
                 points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for start in range(0, len(points), CHUNK_SIZE):
        chunk = points[start:start + CHUNK_SIZE]
        geometry = {
            "points": [[point["x_3857"], point["y_3857"]] for point in chunk],
            "spatialReference": {"wkid": 102100},
        }
        response = fetch_json(f"{SERVICE_URL}/getSamples", {
            "geometry": json.dumps(geometry, separators=(",", ":")),
            "geometryType": "esriGeometryMultipoint",
            "mosaicRule": json.dumps({
                "mosaicMethod": "esriMosaicLockRaster",
                "lockRasterIds": [item["raster_id"]],
            }, separators=(",", ":")),
            "pixelSize": json.dumps({
                "x": 29.97600242,
                "y": 29.97600242,
                "spatialReference": {"wkid": 102100},
            }, separators=(",", ":")),
            "interpolation": "RSP_NearestNeighbor",
            "returnFirstValueOnly": "false",
            "f": "json",
        })
        samples = response.get("samples", [])
        by_id = {int(sample["locationId"]): sample for sample in samples
                 if sample.get("locationId") is not None}
        for point_index, point in enumerate(chunk, start=start):
            sample = by_id.get(point_index - start)
            raw_value = None if sample is None else sample.get("value")
            try:
                value = int(str(raw_value).split(",", 1)[0]) if raw_value is not None else None
            except ValueError as exc:
                raise ValueError(f"Unexpected sampled BWTR value: {raw_value!r}") from exc
            if value is not None and value not in VALID_CLASSES | INVALID_CLASSES:
                raise ValueError(f"Unexpected BWTR class {value} in {item['name']}")
            if sample is not None and sample.get("rasterId") != item["raster_id"]:
                raise ValueError("Sample response contains a different raster ID")
            rows.append({
                "sample_id": point["sample_id"],
                "stratum_row": point["stratum_row"],
                "stratum_col": point["stratum_col"],
                "lon": point["lon"],
                "lat": point["lat"],
                "raster_id": item["raster_id"],
                "raster_name": item["name"],
                "date_utc": item["date_utc"],
                "raw_bwtr_class": value,
                "source_resolution": None if sample is None else sample.get("resolution"),
                "sample_status": "no_sample_returned" if sample is None else "returned",
            })
    return rows


def _summarize(rows: list[dict[str, Any]], item: dict[str, Any]) -> dict[str, Any]:
    counts = Counter(row["raw_bwtr_class"] for row in rows)
    valid = sum(counts[value] for value in VALID_CLASSES)
    water = counts[1]
    return {
        **item,
        "samples_requested": len(rows),
        "samples_returned": sum(row["raw_bwtr_class"] is not None for row in rows),
        "sampled_valid_points": valid,
        "sampled_water_points": water,
        "sampled_not_water_points": counts[0],
        "sampled_invalid_classes": {str(value): counts[value] for value in sorted(INVALID_CLASSES)
                                     if counts[value]},
        "sampled_unexpected_or_missing_points": counts[None] + sum(
            row["raw_bwtr_class"] not in VALID_CLASSES | INVALID_CLASSES | {None} for row in rows),
        "sampled_valid_fraction": valid / len(rows) if rows else None,
        "sampled_water_fraction_of_valid_points": water / valid if valid else None,
        "interpretation": "Balanced equal-area point-sample description only; not a full-AOI raster estimate or accuracy result.",
    }


def run(fetch_json: Callable[..., dict[str, Any]] = _request_json,
        register_path: Path = REGISTER) -> dict[str, Any]:
    register = json.loads(register_path.read_text(encoding="utf-8"))
    candidates = [area for area in register.get("results", []) if area.get("city") == "Tampa"]
    if len(candidates) != 1:
        raise ValueError("Expected one frozen Tampa study-area row")
    area = candidates[0]
    bbox = tuple(float(value) for value in area["aoi_bbox_wgs84"].split(","))
    points = equal_area_sample_points(bbox)

    metadata = fetch_json(SERVICE_URL, {"f": "json"})
    description = html.unescape(re.sub(r"<[^>]+>", " ", str(metadata.get("description") or "")))
    description = " ".join(description.split())
    if "preliminary and unvalidated" not in description.casefold():
        raise ValueError("Expected NASA's preliminary/unvalidated response-map caveat")
    if "30 meters" not in description:
        raise ValueError("Expected NASA's stated 30 m DSWx-S1 pixel spacing")

    items = [
        _fetch_item(fetch_json, object_id=1, name="20240914_DSWx-S1_BWTR", date="2024-09-14"),
        _fetch_item(fetch_json, object_id=3, name="20240926_DSWx-S1_BWTR", date="2024-09-26"),
    ]
    rows = [row for item in items for row in _sample_item(fetch_json, item, points)]
    scene_summaries = [
        _summarize(
            [row for row in rows if row["raster_id"] == item["raster_id"]],
            item,
        )
        for item in items
    ]
    return {
        "audit": "ATLAS Tampa Hurricane Helene NASA EGIS raw BWTR point-sample pilot",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "exploratory_data_access_only_not_validated",
        "candidate_area": {
            "city": area["city"],
            "region": area["region"],
            "bbox_wgs84": list(bbox),
            "register_sha256": hashlib.sha256(register_path.read_bytes()).hexdigest(),
        },
        "event": {
            "name": "Hurricane Helene",
            "event_date_reference": "2024-09-26 landfall in Florida Big Bend",
            "event_reference_url": "https://www.nhc.noaa.gov/archive/2024/al09/al092024.update.09270318.shtml",
            "event_acquisition_date": "2024-09-26",
            "baseline_acquisition_date": "2024-09-14",
            "event_and_baseline_temporal_match": "single paired dates only; outside the three-date-per-period feasibility gate",
        },
        "source": {
            "service_url": SERVICE_URL,
            "service_description_sha256": hashlib.sha256(description.encode()).hexdigest(),
            "service_description_caveat": "NASA EGIS states that the ARIA/OPERA response results are preliminary and unvalidated.",
            "product": "OPERA DSWx-S1 BWTR; service catalog labels these items Binary Water Detection",
            "product_version": "OPERA_L3_DSWX-S1_V1",
            "processing_version": "not_reported_in_service_metadata",
            "service_catalog_ids": [item["raster_id"] for item in items],
            "sample_endpoint": "ImageServer/getSamples",
            "sampled_pixel_spacing_m": 29.97600242,
            "sampling_resampling": "RSP_NearestNeighbor",
            "band_class_contract": {
                "valid": {"0": "not water", "1": "water"},
                "invalid": {"250": "HAND mask", "251": "layover/shadow mask", "255": "fill/no data"},
                "specification_url": "https://developers.google.com/earth-engine/datasets/catalog/OPERA_DSWX_L3_V1_S1",
            },
        },
        "sampling": {
            "seed": SAMPLE_SEED,
            "design": "One independently jittered point in each of 1,024 equal-area strata over the frozen WGS84 AOI; uniform longitude and sine-latitude coordinates; same coordinates reused for both dates.",
            "strata_side": STRATA_SIDE,
            "points_per_scene": len(points),
            "chunk_size": CHUNK_SIZE,
            "point_file_hash": hashlib.sha256(json.dumps(points, sort_keys=True).encode()).hexdigest(),
            "limits": [
                "The point sample does not replace the full 30 m AOI raster and does not establish pixel-level validity for every cell.",
                "One scene per period fails the protocol's three-date feasibility floor; no event/baseline comparison is reported.",
                "The EGIS response is explicitly preliminary and unvalidated; there are no independent event-floodwater labels for this AOI in this audit.",
                "Spatial dependence and uncertainty are not estimated; sampled class proportions are descriptive only.",
            ],
        },
        "scene_summaries": scene_summaries,
        "rows": rows,
        "interpretation": "This verifies public access to real NASA-hosted BWTR pixel classes at matched points on two dates. It is a one-area exploratory access and coverage sample, not a complete event analysis or scientific validation.",
    }


def write_outputs(result: dict[str, Any], json_path: Path = DEFAULT_JSON,
                  csv_path: Path = DEFAULT_CSV) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fieldnames = list(result["rows"][0]) if result["rows"] else []
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=REGISTER)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    result = run(register_path=args.register)
    write_outputs(result, args.json, args.csv)
    for scene in result["scene_summaries"]:
        print(json.dumps(scene, sort_keys=True))
    print(f"Wrote {args.json} and {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
