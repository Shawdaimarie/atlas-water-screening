#!/usr/bin/env python3
"""Screen Cloud to Street's public hand-labeled SAR chips against ATLAS AOIs."""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_bounds, transform_geom


BUCKET_URL = "https://radiant-mlhub.s3.us-west-2.amazonaws.com/"
PREFIX = "c2smsfloods/chips/"
DATASET_URL = "https://registry.opendata.aws/c2smsfloods/"
DOC_URL = "https://radiantearth.blob.core.windows.net/mlhub/c2smsfloods/ms-dataset_README.pdf"
DATE_PATTERN = re.compile(r"_(\d{8})T\d{6}_")
S3_NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}


def list_s1_label_keys() -> list[str]:
    """List every Sentinel-1 hand-label GeoTIFF without downloading the raster set."""
    keys: list[str] = []
    token: str | None = None
    while True:
        query = {"list-type": "2", "prefix": PREFIX}
        if token:
            query["continuation-token"] = token
        request = urllib.request.Request(
            BUCKET_URL + "?" + urllib.parse.urlencode(query),
            headers={"User-Agent": "ATLAS-C2S-coverage-audit/1.0"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            root = ET.fromstring(response.read())
        keys.extend(
            key
            for entry in root.findall("s3:Contents", S3_NS)
            if (key := entry.findtext("s3:Key", namespaces=S3_NS))
            and "/s1/" in key
            and key.endswith("/LabelWater.tif")
        )
        if root.findtext("s3:IsTruncated", namespaces=S3_NS) != "true":
            break
        token = root.findtext("s3:NextContinuationToken", namespaces=S3_NS)
        if not token:
            raise RuntimeError("S3 listing was truncated without a continuation token")
    return keys


def parse_label_key(key: str) -> tuple[str, str, str]:
    parts = key.split("/")
    if len(parts) < 6 or parts[-3] != "s1" or parts[-1] != "LabelWater.tif":
        raise ValueError(f"Not a Sentinel-1 LabelWater path: {key}")
    event_id = parts[-4]
    scene_chip = parts[-2]
    match = DATE_PATTERN.search(scene_chip)
    if not match:
        raise ValueError(f"Sentinel acquisition date missing from {scene_chip}")
    date = datetime.strptime(match.group(1), "%Y%m%d").date().isoformat()
    return event_id, scene_chip, date


def area_geometry(area: dict) -> dict:
    xmin, ymin, xmax, ymax = map(float, area["aoi_bbox_wgs84"].split(","))
    return {
        "type": "Polygon",
        "coordinates": [[
            [xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax], [xmin, ymin]
        ]],
    }


def area_key(area: dict) -> str:
    return f"{area['region']}/{area['city']}"


def inspect_chip(key: str, areas: list[dict]) -> dict:
    event_id, scene_chip, date = parse_label_key(key)
    url = BUCKET_URL + urllib.parse.quote(key, safe="/")
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
    ):
        with rasterio.open("/vsicurl/" + url) as dataset:
            if not dataset.crs:
                raise ValueError(f"Missing CRS: {key}")
            bounds = transform_bounds(dataset.crs, "EPSG:4326", *dataset.bounds)
            matches = []
            for area in areas:
                xmin, ymin, xmax, ymax = map(
                    float, area["aoi_bbox_wgs84"].split(",")
                )
                if bounds[0] >= xmax or bounds[2] <= xmin or bounds[1] >= ymax or bounds[3] <= ymin:
                    continue
                clipped_geom = transform_geom(
                    "EPSG:4326", dataset.crs, area_geometry(area)
                )
                try:
                    clipped, _ = mask(dataset, [clipped_geom], crop=True)
                except ValueError:
                    continue
                pixels = clipped[0]
                valid = pixels != dataset.nodata if dataset.nodata is not None else np.ones(pixels.shape, dtype=bool)
                valid_count = int(valid.sum())
                water_count = int(np.count_nonzero((pixels == 1) & valid))
                water_values = sorted(int(v) for v in np.unique(pixels[valid]))
                pixel_area_m2 = abs(dataset.transform.a * dataset.transform.e)
                matches.append({
                    "area": area_key(area),
                    "valid_pixel_count": valid_count,
                    "water_pixel_count": water_count,
                    "pixel_area_m2": pixel_area_m2,
                    "label_valid_area_km2": valid_count * pixel_area_m2 / 1_000_000,
                    "label_water_area_km2": water_count * pixel_area_m2 / 1_000_000,
                    "water_fraction_of_label_valid_pixels": (
                        water_count / valid_count if valid_count else None
                    ),
                    "label_values": water_values,
                })
            return {
                "object_key": key,
                "event_id": event_id,
                "scene_chip": scene_chip,
                "acquisition_date": date,
                "bounds_wgs84": [round(float(v), 7) for v in bounds],
                "overlapping_areas": matches,
            }


def build_report(areas: list[dict], keys: list[str], max_workers: int) -> dict:
    chips: list[dict] = []
    errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(inspect_chip, key, areas): key for key in keys}
        for future in as_completed(futures):
            key = futures[future]
            try:
                chips.append(future.result())
            except Exception as exc:
                errors.append({"object_key": key, "error": f"{type(exc).__name__}: {exc}"})
    chips.sort(key=lambda chip: (chip["event_id"], chip["acquisition_date"], chip["scene_chip"]))
    by_area: dict[str, list[dict]] = defaultdict(list)
    for chip in chips:
        for match in chip["overlapping_areas"]:
            by_area[match["area"]].append({**chip, **match})

    summaries = {}
    for area in areas:
        key = area_key(area)
        matches = by_area[key]
        summaries[key] = {
            "label_chip_count": len(matches),
            "distinct_s1_acquisition_dates": sorted({m["acquisition_date"] for m in matches}),
            "event_ids": sorted({m["event_id"] for m in matches}),
            "chips_with_water_labels": sum(m["water_pixel_count"] > 0 for m in matches),
            "label_valid_pixels_across_overlapping_chips": sum(m["valid_pixel_count"] for m in matches),
            "water_pixels_across_overlapping_chips": sum(m["water_pixel_count"] for m in matches),
            "label_valid_area_km2_across_overlapping_chips": sum(m["label_valid_area_km2"] for m in matches),
            "label_water_area_km2_across_overlapping_chips": sum(m["label_water_area_km2"] for m in matches),
            "nominal_aoi_coverage_fraction_from_label_valid_pixels": (
                sum(m["label_valid_area_km2"] for m in matches) / float(area["aoi_area_km2"])
                if area.get("aoi_area_km2") else None
            ),
            "chip_records": [
                {
                    "event_id": m["event_id"],
                    "scene_chip": m["scene_chip"],
                    "date": m["acquisition_date"],
                    "bounds_wgs84": m["bounds_wgs84"],
                    "valid_pixel_count": m["valid_pixel_count"],
                    "water_pixel_count": m["water_pixel_count"],
                    "pixel_area_m2": m["pixel_area_m2"],
                    "label_valid_area_km2": m["label_valid_area_km2"],
                    "label_water_area_km2": m["label_water_area_km2"],
                    "water_fraction": m["water_fraction_of_label_valid_pixels"],
                    "label_values": m["label_values"],
                }
                for m in matches
            ],
        }
    return {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "Cloud to Street - Microsoft Flood and Clouds Dataset",
        "dataset_url": DATASET_URL,
        "documentation_url": DOC_URL,
        "dataset_license": {
            "aws_registry": "CC-BY-4.0",
            "radiant_earth_documentation_pdf": "CC-BY-SA-4.0",
            "status": "conflicting source terms; do not redistribute until the dataset steward confirms the governing license",
        },
        "input_area_count": len(areas),
        "registered_areas": summaries,
        "source_label_chip_count": len(keys),
        "successfully_inspected_chip_count": len(chips),
        "overlapping_chip_count": sum(bool(chip["overlapping_areas"]) for chip in chips),
        "unique_event_count": len({chip["event_id"] for chip in chips}),
        "processing_errors": errors,
        "chips": chips,
        "interpretation": [
            "This is a spatial coverage screen of hand-labeled event chips, not a completed ATLAS event analysis.",
            "The S1 LabelWater masks were hand drawn from the same S1 scenes, with S2 imagery as supporting visual context; this is an analyst reference, not an independent sensor measurement.",
            "Chip footprints can overlap each other; per-area valid and water pixel counts are sums over chip records and are not deduplicated AOI coverage.",
            "The dataset's event-focused acquisition dates do not by themselves supply three qualifying baseline dates or the required OPERA product observations.",
            "No score points should be awarded until matched input provenance, temporal adequacy, reference independence, and the preregistered QA gates are reviewed.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--areas", type=Path, default=Path("data/study_area_register.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/atlas-c2s-flood-dataset-audit.json"))
    parser.add_argument("--max-workers", type=int, default=12)
    args = parser.parse_args()
    area_data = json.loads(args.areas.read_text(encoding="utf-8"))
    areas = area_data.get("results", [])
    keys = list_s1_label_keys()
    report = build_report(areas, keys, args.max_workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {args.output}: {len(keys)} label objects; "
        f"{report['overlapping_chip_count']} chips overlap {len(areas)} study AOIs; "
        f"{len(report['processing_errors'])} errors."
    )


if __name__ == "__main__":
    main()
