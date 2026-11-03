#!/usr/bin/env python3
"""Screen FloodPlanet hand-label STAC footprints against the 16 ATLAS AOIs."""

from __future__ import annotations

import argparse
import json
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from shapely.geometry import box, shape

try:
    from scripts.audit_ufo_dataset_coverage import zip_entries, zip_read_contiguous_members
except ModuleNotFoundError:
    from audit_ufo_dataset_coverage import zip_entries, zip_read_contiguous_members


ZENODO_RECORD_ID = "15238572"
ZENODO_API = f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}"
DATASET_DOI = "https://doi.org/10.5281/zenodo.15238572"
ZENODO_PAGE = "https://zenodo.org/records/15238572"


def read_areas(path: Path) -> list[dict]:
    register = json.loads(path.read_text(encoding="utf-8"))
    return register["results"]


def area_key(area: dict) -> str:
    return f"{area['region']}/{area['city']}"


def audit(areas: list[dict]) -> dict:
    record = json.load(urllib.request.urlopen(ZENODO_API, timeout=45))
    archive = next(file for file in record["files"] if file["key"].endswith(".zip"))
    archive_url = archive["links"]["self"]
    entries, total_size = zip_entries(archive_url)
    label_entries = [
        entry for entry in entries
        if entry["name"].startswith("stac_catalog/")
        and "/labels/" in entry["name"]
        and entry["name"].endswith(".json")
        and not entry["name"].endswith("/collection.json")
    ]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for entry in label_entries:
        event = entry["name"].split("/")[1]
        grouped[event].append(entry)

    aoi_shapes = {
        area_key(area): box(*map(float, area["aoi_bbox_wgs84"].split(",")))
        for area in areas
    }
    items = []
    errors = []
    for event, event_entries in sorted(grouped.items()):
        try:
            content_by_name = zip_read_contiguous_members(archive_url, event_entries)
        except Exception as exc:
            errors.append({"event": event, "error": f"{type(exc).__name__}: {exc}"})
            continue
        for entry in event_entries:
            try:
                item = json.loads(content_by_name[entry["name"]])
                footprint = shape(item["geometry"])
                overlaps = []
                for key, aoi in aoi_shapes.items():
                    intersection = footprint.intersection(aoi)
                    if not intersection.is_empty and intersection.area > 0:
                        overlaps.append({"area": key, "intersection_area_degrees2": round(intersection.area, 12)})
                props = item.get("properties", {})
                items.append({
                    "item_id": item.get("id"),
                    "event": props.get("Event"),
                    "datetime": props.get("datetime"),
                    "bbox_wgs84": item.get("bbox"),
                    "gsd_m": props.get("gsd"),
                    "label_source": props.get("Image source"),
                    "label_class_description": props.get("Data Description"),
                    "item_license": props.get("license"),
                    "overlapping_areas": overlaps,
                })
            except Exception as exc:
                errors.append({"item": entry["name"], "error": f"{type(exc).__name__}: {exc}"})

    by_area: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        for overlap in item["overlapping_areas"]:
            by_area[overlap["area"]].append({**item, **overlap})
    summaries = {}
    for area in areas:
        key = area_key(area)
        matches = by_area[key]
        summaries[key] = {
            "label_chip_count": len(matches),
            "events": sorted({match["event"] for match in matches if match.get("event")}),
            "dates": sorted({(match.get("datetime") or "")[:10] for match in matches if match.get("datetime")}),
            "spatial_reference_sensor": "PlanetScope hand labels (different sensor from OPERA Sentinel-1)",
            "matched_chips": [
                {k: match[k] for k in ("item_id", "event", "datetime", "bbox_wgs84", "gsd_m", "label_source", "label_class_description", "item_license", "intersection_area_degrees2")}
                for match in matches
            ],
        }
    license_values = sorted({item["item_license"] for item in items if item.get("item_license")})
    return {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "source": "FloodPlanet Inundation Dataset, STAC label-item metadata in the public Zenodo archive",
        "zenodo_record_id": record.get("id"),
        "doi": record.get("doi") or DATASET_DOI,
        "record_url": ZENODO_PAGE,
        "archive_file": archive["key"],
        "archive_bytes": archive["size"],
        "archive_checksum": archive.get("checksum"),
        "range_read_only": True,
        "zip_member_count": len(entries),
        "stac_label_item_count": len(label_entries),
        "successfully_inspected_item_count": len(items),
        "event_group_count": len(grouped),
        "processing_errors": errors,
        "registered_area_count": len(areas),
        "overlapping_area_count": sum(bool(summary["label_chip_count"]) for summary in summaries.values()),
        "overlapping_label_chip_count": sum(summary["label_chip_count"] for summary in summaries.values()),
        "item_level_license_values": license_values,
        "license_note": "Zenodo landing page does not display a license; each label STAC item must be checked, and the CyVerse listing reports PDDL. Resolve conflicting terms with the data provider before redistribution or commercial use.",
        "registered_areas": summaries,
        "limitations": [
            "A footprint overlap is a candidate reference lead, not proof of event-date or pixel-level alignment with the current OPERA acquisition.",
            "The labels distinguish no-data, not-water, low-confidence water, and water; low-confidence pixels require a predeclared treatment.",
            "The collection covers 19 historical events from 2017–2020, outside the current 2024–2026 OPERA screening window.",
            "STAC item properties describe hand labels based on PlanetScope and co-located temporally near Sentinel imagery; inspect actual label rasters, temporal lags, annotator documentation, and co-registration before validation.",
            "The source is not balanced across the 16 selected city AOIs and cannot establish the full 8+8 comparative design.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--areas", type=Path, default=Path("data/study_area_register.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/atlas-floodplanet-coverage-audit.json"))
    args = parser.parse_args()
    result = audit(read_areas(args.areas))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "archive_bytes", "archive_checksum", "stac_label_item_count",
        "successfully_inspected_item_count", "event_group_count", "processing_errors",
        "overlapping_area_count", "overlapping_label_chip_count",
    )}, indent=2))
    for area, summary in result["registered_areas"].items():
        if summary["label_chip_count"]:
            print(area, json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
