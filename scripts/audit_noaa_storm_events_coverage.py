#!/usr/bin/env python3
"""Screen NOAA/NWS Storm Events flood-location reports against ATLAS U.S. AOIs.

This is an event-location discovery audit. The CSV locations are reported points,
not inundation polygons, independent pixel labels, or a probability sample.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "work" / "noaa_stormevents_2024_2026"
DEFAULT_OUTPUT = ROOT / "outputs" / "atlas-noaa-storm-events-coverage-audit.json"
SOURCE_BASE = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles"
FILES = {
    2024: {
        "details": ("details_2024.csv.gz", "StormEvents_details-ftp_v1.0_d2024_c20260728.csv.gz", "2070b83eccab041b36360ab73645b9a249c3eefc5b92b5b3fc0cbba4d9fcc09c"),
        "locations": ("locations_2024.csv.gz", "StormEvents_locations-ftp_v1.0_d2024_c20260728.csv.gz", "8847a6336e1af94000f7ecfb4a80c06bf0d5c1ac122fe39da5b2e379dc62c1b4"),
    },
    2025: {
        "details": ("details_2025.csv.gz", "StormEvents_details-ftp_v1.0_d2025_c20260819.csv.gz", "d9b46b4c6aae554723cadbb9691f3d5258371c02e530ba815d6fe41e4550149f"),
        "locations": ("locations_2025.csv.gz", "StormEvents_locations-ftp_v1.0_d2025_c20260819.csv.gz", "64847e91cf90e3bffbb8338f91b95bc6e527ff1f1b999b80336f24dc1187dc22"),
    },
    2026: {
        "details": ("details_2026.csv.gz", "StormEvents_details-ftp_v1.0_d2026_c20261026.csv.gz", "53e6118446f19a522abeb7ececca1dfdae3090117bc1297e2a774f21f13ee83a"),
        "locations": ("locations_2026.csv.gz", "StormEvents_locations-ftp_v1.0_d2026_c20261026.csv.gz", "6525caf4737c691c49f6df6a0b2605f8bb015086f3dcfebb31b156c4cc2a8428"),
    },
}
INCLUDED_START = dt.date(2024, 9, 1)
INCLUDED_END = dt.date(2026, 11, 2)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def point_in_bbox(longitude: float, latitude: float, bbox: tuple[float, float, float, float]) -> bool:
    west, south, east, north = bbox
    return west <= longitude <= east and south <= latitude <= north


def flood_event_type(value: str) -> bool:
    return "FLOOD" in value.upper()


def _read_details(path: Path, year: int) -> dict[tuple[int, str, str], dict[str, str]]:
    details: dict[tuple[int, str, str], dict[str, str]] = {}
    with gzip.open(path, "rt", encoding="latin1", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"EPISODE_ID", "EVENT_ID", "EVENT_TYPE", "BEGIN_DATE_TIME", "END_DATE_TIME"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Unexpected details CSV schema in {path.name}")
        for row in reader:
            if not flood_event_type(row.get("EVENT_TYPE", "")) or not row.get("BEGIN_DATE_TIME"):
                continue
            try:
                begin_date = dt.datetime.strptime(row["BEGIN_DATE_TIME"], "%d-%b-%y %H:%M:%S").date()
            except ValueError:
                continue
            if INCLUDED_START <= begin_date <= INCLUDED_END:
                key = (year, row["EPISODE_ID"], row["EVENT_ID"])
                details[key] = row
    return details


def audit(input_dir: Path, register_path: Path = ROOT / "data" / "study_area_register.json") -> dict[str, Any]:
    register = json.loads(register_path.read_text(encoding="utf-8"))["results"]
    areas = []
    for area in register:
        bbox = tuple(float(value) for value in area["aoi_bbox_wgs84"].split(","))
        if len(bbox) != 4:
            raise ValueError(f"Expected west,south,east,north bbox for {area['city']}")
        areas.append({"region": area["region"], "city": area["city"], "bbox": bbox})

    event_details: dict[tuple[int, str, str], dict[str, str]] = {}
    source_files: dict[str, dict[str, Any]] = {}
    for year, tables in FILES.items():
        for kind, (local_name, remote_name, expected_hash) in tables.items():
            path = input_dir / local_name
            if not path.is_file():
                raise FileNotFoundError(f"Missing source file: {path}; see audit documentation for download URL")
            actual_hash = sha256(path)
            if actual_hash != expected_hash:
                raise ValueError(f"SHA-256 mismatch for {path.name}: {actual_hash}")
            source_files[f"{year}_{kind}"] = {
                "filename": remote_name,
                "download_url": f"{SOURCE_BASE}/{remote_name}",
                "sha256": actual_hash,
                "compressed_bytes": path.stat().st_size,
            }
        event_details.update(_read_details(input_dir / tables["details"][0], year))

    events_by_area: dict[tuple[str, str], dict[tuple[int, str, str], dict[str, Any]]] = defaultdict(dict)
    report_counts: Counter[tuple[str, str]] = Counter()
    for year, tables in FILES.items():
        with gzip.open(input_dir / tables["locations"][0], "rt", encoding="latin1", newline="") as stream:
            reader = csv.DictReader(stream)
            required = {"EPISODE_ID", "EVENT_ID", "LOCATION_INDEX", "LOCATION", "LATITUDE", "LONGITUDE"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError(f"Unexpected locations CSV schema for {year}")
            for location_row in reader:
                key = (year, location_row["EPISODE_ID"], location_row["EVENT_ID"])
                detail = event_details.get(key)
                if detail is None:
                    continue
                try:
                    latitude = float(location_row["LATITUDE"])
                    longitude = float(location_row["LONGITUDE"])
                except (TypeError, ValueError):
                    continue
                if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                    continue
                for area in areas:
                    if area["region"] != "United States" or not point_in_bbox(longitude, latitude, area["bbox"]):
                        continue
                    area_key = (area["region"], area["city"])
                    event = events_by_area[area_key].setdefault(key, {
                        "year": year,
                        "episode_id": detail["EPISODE_ID"],
                        "event_id": detail["EVENT_ID"],
                        "event_type": detail["EVENT_TYPE"],
                        "state": detail["STATE"],
                        "county_or_zone": detail["CZ_NAME"],
                        "nws_office": detail["WFO"],
                        "begin_date_time_local": detail["BEGIN_DATE_TIME"],
                        "end_date_time_local": detail["END_DATE_TIME"],
                        "timezone_code": detail["CZ_TIMEZONE"],
                        "flood_cause": detail.get("FLOOD_CAUSE", ""),
                        "report_source": detail.get("SOURCE", ""),
                        "event_narrative": detail.get("EVENT_NARRATIVE", ""),
                        "locations": [],
                        "_location_keys": set(),
                    })
                    location_key = (location_row["LOCATION_INDEX"], latitude, longitude, location_row.get("LOCATION", ""))
                    if location_key not in event["_location_keys"]:
                        event["_location_keys"].add(location_key)
                        event["locations"].append({
                            "location_index": location_row["LOCATION_INDEX"],
                            "place": location_row.get("LOCATION", ""),
                            "latitude": latitude,
                            "longitude": longitude,
                        })
                        report_counts[area_key] += 1

    output_areas = []
    for area in areas:
        area_key = (area["region"], area["city"])
        grouped = sorted(events_by_area.get(area_key, {}).values(), key=lambda item: (item["begin_date_time_local"], item["event_id"]))
        for event in grouped:
            event.pop("_location_keys", None)
            event["location_report_count"] = len(event["locations"])
        counts = Counter(item["event_type"] for item in grouped)
        if area["region"] != "United States":
            status = "outside_dataset_geographic_scope"
        elif grouped:
            status = "official_flood_or_flash_flood_location_reports_found"
        else:
            status = "no_point_reports_found_in_screened_files"
        output_areas.append({
            "region": area["region"],
            "city": area["city"],
            "status": status,
            "unique_event_ids": len(grouped),
            "location_reports": report_counts[area_key],
            "event_type_counts": dict(sorted(counts.items())),
            "events": grouped,
        })
    us_areas = [area for area in output_areas if area["region"] == "United States"]
    return {
        "audit_id": "atlas-noaa-storm-events-fixed-aoi-screen",
        "schema_version": 1,
        "generated_from": "fixed 8+8 register and pinned NOAA/NWS Storm Events bulk CSV releases",
        "dataset": {
            "publisher": "NOAA National Centers for Environmental Information; event data supplied through National Weather Service Storm Data",
            "event_types_included": "EVENT_TYPE contains FLOOD, including Flood, Flash Flood, and Coastal Flood variants",
            "years_screened": [2024, 2025, 2026],
            "requested_study_window": [INCLUDED_START.isoformat(), INCLUDED_END.isoformat()],
            "source_files": source_files,
            "limitations": [
                "The database covers the United States and adjacent waters; international rows are outside its geographic scope.",
                "Storm Events records are curated significant-event reports and are subject to reporting, timing, and geolocation limitations.",
                "NCEI says events take approximately three months to appear. The pinned 2026 release has flood records through July 31; the August-November portion of the ATLAS window is absent from this downloaded release.",
            ],
        },
        "method": {
            "join_key": ["year", "EPISODE_ID", "EVENT_ID"],
            "geometry": "screen each NWS location-table point inside the frozen rectangular AOI bbox; a hit is location context, not an inundation extent",
            "time": "preserve NWS BEGIN_DATE_TIME and its local CZ_TIMEZONE string; no timezone conversion or OPERA match is asserted",
            "deduplication": "count unique (year, EPISODE_ID, EVENT_ID); retain distinct LOCATION_INDEX/place/coordinate points within each event",
            "candidate_frame_changed": False,
        },
        "summary": {
            "candidate_areas": len(output_areas),
            "us_candidates": len(us_areas),
            "international_candidates": len(output_areas) - len(us_areas),
            "us_areas_with_nws_flood_location_reports": sum(area["unique_event_ids"] > 0 for area in us_areas),
            "us_unique_area_event_pairs": sum(area["unique_event_ids"] for area in us_areas),
            "us_location_report_points": sum(area["location_reports"] for area in us_areas),
            "international_areas_outside_dataset_scope": sum(area["status"] == "outside_dataset_geographic_scope" for area in output_areas),
            "confirmatory_areas_eligible": 0,
            "score_credit": 0,
        },
        "areas": output_areas,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--register", type=Path, default=ROOT / "data" / "study_area_register.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit(args.input_dir, args.register)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
