#!/usr/bin/env python3
"""Compare raw NASA EGIS OPERA WTR point returns over fixed Miami/Tampa AOIs.

This is a deterministic, equal-area, two-site access/availability diagnostic
for NASA's preliminary Hurricane Milton response layers. It is not a full
raster QA result, event/baseline comparison, independent label set, or flood
accuracy assessment.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_nasa_egis_milton_samples import (
    REGISTER,
    SERVICE_URL,
    SCENES,
    _bbox_intersects,
    _fetch_item,
    _request_json,
    _sample_scene,
    _unavailable_scene,
)
from scripts.audit_nasa_egis_opera_samples import equal_area_sample_points


DEFAULT_JSON = ROOT / "outputs/atlas-milton-egis-multisite-pixel-sample.json"
DEFAULT_CSV = ROOT / "outputs/atlas-milton-egis-multisite-pixel-sample.csv"
TARGET_CITIES = {"Miami", "Tampa"}


def audit(fetch_json: Callable[..., dict[str, Any]] = _request_json,
          register_path: Path = REGISTER) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    register_bytes = register_path.read_bytes()
    register = json.loads(register_bytes)
    areas = [area for area in register.get("results", []) if area.get("city") in TARGET_CITIES]
    if {area.get("city") for area in areas} != TARGET_CITIES:
        raise ValueError("The canonical register must contain exactly one Miami and one Tampa AOI")

    metadata = fetch_json(SERVICE_URL, {"f": "json"})
    description = str(metadata.get("description") or "")
    if "preliminary and unvalidated" not in description.casefold():
        raise ValueError("NASA service caveat is missing or changed")

    results: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    for area in areas:
        bbox = tuple(float(value) for value in area["aoi_bbox_wgs84"].split(","))
        city_seed = f"ATLAS-{area['city']}-Milton-EGIS-WTR-v1"
        points = equal_area_sample_points(bbox, seed=city_seed)
        scenes = []
        city_rows = []
        for scene in SCENES:
            item = _fetch_item(fetch_json, scene)
            if _bbox_intersects(item["footprint_bbox_wgs84"], bbox):
                rows, summary = _sample_scene(fetch_json, scene, points)
                summary["catalog_footprint_bbox_wgs84"] = item["footprint_bbox_wgs84"]
            else:
                rows, summary = _unavailable_scene(
                    scene, points, "outside_aoi_footprint", item["footprint_bbox_wgs84"]
                )
            summary["catalog_item"] = item
            scenes.append(summary)
            city_rows.extend(rows)
        sampled_scenes = [scene for scene in scenes if scene["sampling_status"] == "sampled"]
        results.append({
            "city": area["city"],
            "region": area["region"],
            "aoi_bbox_wgs84": list(bbox),
            "sample_design": {
                "points_per_scene": len(points),
                "seed": city_seed,
                "method": "Same seeded jittered equal-area points for all four catalog rasters within this area.",
            },
            "scenes": scenes,
            "scenes_with_any_returned_samples": len(sampled_scenes),
            "all_samples_returned_for_every_overlapping_scene": all(
                scene["samples_returned"] == scene["samples_requested"]
                for scene in sampled_scenes
            ),
            "interpretation": (
                "Access/availability only. Pre/post-landfall dates are not declared baseline/event windows; "
                "NASA marks response maps preliminary and unvalidated."
            ),
        })
        all_rows.extend({"city": area["city"], **row} for row in city_rows)

    report = {
        "audit": "ATLAS NASA EGIS Hurricane Milton matched-point availability screen",
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "service_url": SERVICE_URL,
            "catalog_item_url": "https://gis.earthdata.nasa.gov/portal/home/item.html?id=d20858f42cae4c6b8b4438e847266442",
            "source_caveat": "NASA identifies response-map results as preliminary and unvalidated.",
            "event": "Hurricane Milton, October 2024",
            "class_product": "OPERA DSWx-S1 WTR mosaics; raw classes are interpreted only as product classes.",
        },
        "register_sha256": __import__("hashlib").sha256(register_bytes).hexdigest(),
        "areas": results,
        "summary": {
            "areas": len(results),
            "areas_with_catalog_footprint_samples": sum(
                area["scenes_with_any_returned_samples"] > 0 for area in results
            ),
            "scenes_with_any_returned_samples": sum(
                scene["sampling_status"] == "sampled"
                for area in results for scene in area["scenes"]
            ),
            "total_raw_points_returned": sum(
                scene["samples_returned"] for area in results for scene in area["scenes"]
            ),
            "confirmatory_eligible_areas": 0,
        },
        "limits": [
            "Only Miami and Tampa have catalog item footprints in the registered fixed AOIs for this service.",
            "The NASA EGIS quick-response service is a separate, preliminary/unvalidated product screen.",
            "Point returns do not establish full-AOI finite-pixel coverage, exact acquisition-time matching, or classification accuracy.",
            "The four scenes are not a preregistered event/baseline sample; no change estimate is calculated.",
            "No independent labels, asset intersection, probability sample adequacy, or precision gate was assessed.",
        ],
    }
    return report, all_rows


def write_outputs(report: dict[str, Any], rows: list[dict[str, Any]],
                  json_path: Path = DEFAULT_JSON, csv_path: Path = DEFAULT_CSV) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["city", "date_utc", "phase", "raster_id", "sample_id", "stratum_row", "stratum_col",
              "lon", "lat", "wtr_class", "class_label", "source_resolution_m", "sample_status"]
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    report, rows = audit()
    write_outputs(report, rows, args.json, args.csv)
    for area in report["areas"]:
        compact = {"city": area["city"], "scenes": [
            {key: scene[key] for key in ("date_utc", "phase", "sampling_status", "samples_returned", "class_counts")}
            for scene in area["scenes"]
        ]}
        print(json.dumps(compact, sort_keys=True))
    print(f"Wrote {args.json} and {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
