"""Screen SpaceNet 8 Louisiana event annotations against fixed ATLAS AOIs.

The audit uses the public vector annotations only. SpaceNet 8 flood attributes
are object-level optical-image labels, not pixel-level water truth or field
observations. No satellite imagery is downloaded by this script.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shapely.geometry import box, shape


BASE = (
    "https://spacenet-dataset.s3.amazonaws.com/spacenet/SN8_floods/"
    "Louisiana-East_Training_Public"
)
MAPPING_URL = f"{BASE}/Louisiana-East_Training_Public_label_image_mapping.csv"
SOURCE_PAGE = "https://www.spacenet.ai/sn8-challenge/"
PAPER = (
    "https://openaccess.thecvf.com/content/CVPR2022W/EarthVision/papers/"
    "Hansch_SpaceNet_8_-_The_Detection_of_Flooded_Roads_and_Buildings_CVPRW_2022_paper.pdf"
)
LICENSE = "CC BY-SA 4.0 for SpaceNet dataset; imagery has separate terms"
USER_AGENT = "ATLAS-research-audit/1.0"


def fetch(url: str, attempts: int = 4) -> bytes:
    """Fetch a public source with bounded retry and no credentials."""
    request = Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=45) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError):
            if attempt + 1 == attempts:
                raise
            time.sleep(0.4 * (2**attempt))
    raise RuntimeError("unreachable")


def read_areas(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    return data["results"]


def parse_bbox(value: str):
    west, south, east, north = (float(part) for part in value.split(","))
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError(f"Invalid WGS84 bbox: {value}")
    return box(west, south, east, north)


def class_for(properties: dict) -> str:
    if properties.get("building") not in (None, "no", "false", False):
        return "building"
    if properties.get("highway") not in (None, "no", "false", False):
        return "road"
    return "other"


def flood_label(value):
    """Normalize source GeoJSON flood labels without treating null as dry."""
    if value is True or (isinstance(value, str) and value.strip().lower() in {"yes", "true"}):
        return True
    if value is False or (isinstance(value, str) and value.strip().lower() in {"no", "false"}):
        return False
    return None


def screen_features(geojson: dict, area_geometry) -> dict:
    """Count unique, intersecting object IDs and flood-label classes."""
    counts = {
        "features_intersecting": 0,
        "unique_feature_ids": 0,
        "flooded": 0,
        "not_flooded": 0,
        "flood_status_unknown": 0,
        "buildings": 0,
        "roads": 0,
        "other": 0,
        "malformed_or_empty_geometry": 0,
    }
    unique = {}
    for feature in geojson.get("features", []):
        properties = feature.get("properties") or {}
        geometry_value = feature.get("geometry")
        try:
            geometry = shape(geometry_value) if geometry_value else None
            if geometry is None or geometry.is_empty or not geometry.is_valid:
                counts["malformed_or_empty_geometry"] += 1
                continue
            overlap = geometry.intersection(area_geometry)
            if overlap.is_empty or (geometry.geom_type in {"Polygon", "MultiPolygon"} and overlap.area <= 0):
                continue
            if geometry.geom_type in {"LineString", "MultiLineString"} and overlap.length <= 0:
                continue
        except (TypeError, ValueError):
            counts["malformed_or_empty_geometry"] += 1
            continue

        counts["features_intersecting"] += 1
        feature_id = properties.get("id") or json.dumps(
            [properties, geometry_value], sort_keys=True, separators=(",", ":")
        )
        label = flood_label(properties.get("flooded"))
        kind = class_for(properties)
        record = {"flooded": label, "kind": kind}
        previous = unique.get(feature_id)
        if previous is not None and previous != record:
            raise ValueError(f"Conflicting duplicate label for feature {feature_id}")
        unique[feature_id] = record

    counts["unique_feature_ids"] = len(unique)
    for record in unique.values():
        counts[record["kind"] + "s" if record["kind"] in ("building", "road") else "other"] += 1
        if record["flooded"] is True:
            counts["flooded"] += 1
        elif record["flooded"] is False:
            counts["not_flooded"] += 1
        else:
            counts["flood_status_unknown"] += 1
    return counts


def audit(areas_path: Path, workers: int = 8) -> dict:
    mapping_bytes = fetch(MAPPING_URL)
    mapping_rows = list(csv.DictReader(io.StringIO(mapping_bytes.decode("utf-8-sig"))))
    if not mapping_rows:
        raise ValueError("SpaceNet 8 tile mapping is empty")
    label_names = [row["label"] for row in mapping_rows]
    if len(label_names) != len(set(label_names)):
        raise ValueError("SpaceNet 8 mapping contains duplicate annotation paths")

    areas = read_areas(areas_path)
    area_geometries = {
        area["city"]: parse_bbox(area["aoi_bbox_wgs84"]) for area in areas
    }
    counts = {
        city: {
            "annotation_files_intersecting": 0,
            "feature_totals": {
                "features_intersecting": 0,
                "unique_feature_ids": 0,
                "flooded": 0,
                "not_flooded": 0,
                "flood_status_unknown": 0,
                "buildings": 0,
                "roads": 0,
                "other": 0,
                "malformed_or_empty_geometry": 0,
            },
            "annotation_files": [],
            "feature_ids": {},
        }
        for city in area_geometries
    }
    fetched = {}

    def get_annotation(label_name: str):
        source_url = f"{BASE}/annotations/{label_name}"
        raw = fetch(source_url)
        return label_name, source_url, raw, json.loads(raw)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(get_annotation, name) for name in label_names]
        for future in as_completed(futures):
            label_name, source_url, raw, document = future.result()
            fetched[label_name] = {
                "source_url": source_url,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "byte_length": len(raw),
                "document": document,
            }

    for label_name in sorted(fetched):
        item = fetched[label_name]
        document = item["document"]
        crs_name = (
            document.get("crs", {}).get("properties", {}).get("name")
            if isinstance(document.get("crs"), dict)
            else None
        )
        if crs_name and "CRS84" not in crs_name and "4326" not in crs_name:
            raise ValueError(f"Unexpected annotation CRS {crs_name}: {label_name}")
        for city, geometry in area_geometries.items():
            tile_counts = screen_features(document, geometry)
            if tile_counts["features_intersecting"] == 0:
                continue
            record = counts[city]
            record["annotation_files_intersecting"] += 1
            record["annotation_files"].append(label_name)
            totals = record["feature_totals"]
            for key, value in tile_counts.items():
                totals[key] += value
            for feature in document.get("features", []):
                properties = feature.get("properties") or {}
                try:
                    geom = shape(feature.get("geometry"))
                    overlap = geom.intersection(geometry)
                    if geom.is_empty or not geom.is_valid or overlap.is_empty:
                        continue
                    if geom.geom_type in {"Polygon", "MultiPolygon"} and overlap.area <= 0:
                        continue
                    if geom.geom_type in {"LineString", "MultiLineString"} and overlap.length <= 0:
                        continue
                except (TypeError, ValueError):
                    continue
                feature_id = properties.get("id")
                if feature_id is not None:
                    entry = record["feature_ids"].setdefault(
                        feature_id,
                        {
                            "flooded": flood_label(properties.get("flooded")),
                            "kind": class_for(properties),
                            "tiles": [],
                        },
                    )
                    if entry["flooded"] != flood_label(properties.get("flooded")) or entry["kind"] != class_for(properties):
                        raise ValueError(f"Conflicting duplicate label for feature {feature_id}")
                    entry["tiles"].append(label_name)

    for city, record in counts.items():
        record["unique_feature_totals"] = {
            "unique_feature_ids": len(record["feature_ids"]),
            "flooded": sum(1 for item in record["feature_ids"].values() if item["flooded"] is True),
            "not_flooded": sum(1 for item in record["feature_ids"].values() if item["flooded"] is False),
            "flood_status_unknown": sum(1 for item in record["feature_ids"].values() if item["flooded"] is None),
            "buildings": sum(1 for item in record["feature_ids"].values() if item["kind"] == "building"),
            "roads": sum(1 for item in record["feature_ids"].values() if item["kind"] == "road"),
            "other": sum(1 for item in record["feature_ids"].values() if item["kind"] == "other"),
        }
        record.pop("feature_ids")

    return {
        "audit": "ATLAS SpaceNet 8 Louisiana object-label footprint screen",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "dataset": "SpaceNet 8 Louisiana-East Training Public",
            "mapping_url": MAPPING_URL,
            "mapping_sha256": hashlib.sha256(mapping_bytes).hexdigest(),
            "annotation_files_listed": len(mapping_rows),
            "annotation_files_fetched": len(fetched),
            "annotations_prefix": f"{BASE}/annotations/",
            "source_page": SOURCE_PAGE,
            "paper": PAPER,
            "license": LICENSE,
            "event": "Hurricane Ida, August 2021",
            "label_construction": "Manual object labels from pre-event and post-event high-resolution optical imagery; source flooded=yes is counted positive, false/no negative, and null remains unknown",
        },
        "method": {
            "area_source": str(areas_path),
            "areas_screened": len(areas),
            "spatial_rule": "Exact geometry intersection of CRS84 GeoJSON annotations and the fixed ATLAS AOI bbox",
            "deduplication": "Unique source feature id per AOI; cross-tile duplicate IDs are counted once in unique_feature_totals",
            "classes": "Building and road types inferred from source properties; flooded boolean retained separately",
            "exclusions": "This is object-level flood-impact evidence, not pixel-level water extent, field truth, or validation of OPERA DSWx-S1 water classes",
        },
        "results": counts,
        "summary": {
            "areas_with_annotation_overlap": sum(
                1 for result in counts.values() if result["annotation_files_intersecting"]
            ),
            "candidate_areas_with_overlap": sorted(
                city for city, result in counts.items() if result["annotation_files_intersecting"]
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--areas", type=Path, default=Path("data/study_area_register.json"))
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/atlas-spacenet8-louisiana-coverage-audit.json")
    )
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error("--workers must be between 1 and 16")
    result = audit(args.areas, args.workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    for city, value in result["results"].items():
        if value["annotation_files_intersecting"]:
            print(city, json.dumps(value["unique_feature_totals"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
