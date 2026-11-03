#!/usr/bin/env python3
"""Screen latest public UFO PlanetScope label-chip footprints against ATLAS AOIs."""

from __future__ import annotations

import argparse
import json
import math
import struct
import urllib.request
import zlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ZENODO_CONCEPT_RECORD = "15238469"
ZENODO_API = f"https://zenodo.org/api/records/{ZENODO_CONCEPT_RECORD}/versions/latest"
DATASET_DOI = "https://doi.org/10.5281/zenodo.15238469"
EOCD = bytes([0x50, 0x4B, 0x05, 0x06])
CENTRAL_SIG = bytes([0x50, 0x4B, 0x01, 0x02])
LOCAL_SIG = bytes([0x50, 0x4B, 0x03, 0x04])


def request_bytes(url: str, start: int, end: int, timeout: int = 45) -> tuple[bytes, int]:
    request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_range = response.headers.get("Content-Range", "")
        total = int(content_range.rsplit("/", 1)[1])
        return response.read(), total


def request_suffix(url: str, length: int, timeout: int = 45) -> tuple[bytes, int]:
    request = urllib.request.Request(url, headers={"Range": f"bytes=-{length}"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_range = response.headers.get("Content-Range", "")
        total = int(content_range.rsplit("/", 1)[1])
        return response.read(), total


def zip_entries(url: str) -> tuple[list[dict], int]:
    tail, total_size = request_suffix(url, 65_557)
    marker = tail.rfind(EOCD)
    if marker < 0:
        raise ValueError("ZIP end-of-central-directory record is missing")
    _, _, _, _, file_count, directory_size, directory_offset, _ = struct.unpack(
        "<4s4H2IH", tail[marker : marker + 22]
    )
    directory, _ = request_bytes(url, directory_offset, directory_offset + directory_size - 1)
    entries = []
    offset = 0
    fmt = "<4s6H3I5H2I"
    header_size = struct.calcsize(fmt)
    while offset < len(directory):
        fields = struct.unpack(fmt, directory[offset : offset + header_size])
        if fields[0] != CENTRAL_SIG:
            raise ValueError("Malformed ZIP central directory")
        filename_length, extra_length, comment_length = fields[10:13]
        filename = directory[offset + header_size : offset + header_size + filename_length].decode("utf-8")
        entries.append({
            "name": filename,
            "method": fields[4],
            "compressed_size": fields[8],
            "uncompressed_size": fields[9],
            "local_header_offset": fields[-1],
        })
        offset += header_size + filename_length + extra_length + comment_length
    if len(entries) != file_count:
        raise ValueError(f"ZIP central directory lists {len(entries)} entries; EOCD says {file_count}")
    return entries, total_size


def zip_read_member(url: str, entry: dict) -> bytes:
    start = entry["local_header_offset"]
    header, _ = request_bytes(url, start, start + 29)
    fields = struct.unpack("<4s5H3I2H", header)
    if fields[0] != LOCAL_SIG:
        raise ValueError(f"Malformed local ZIP header for {entry['name']}")
    filename_length, extra_length = fields[-2:]
    start += 30 + filename_length + extra_length
    end = start + entry["compressed_size"] - 1
    payload, _ = request_bytes(url, start, end)
    if entry["method"] == 0:
        return payload
    if entry["method"] == 8:
        return zlib.decompress(payload, -15)
    raise ValueError(f"Unsupported ZIP compression method {entry['method']}")


def zip_read_contiguous_members(url: str, entries: list[dict]) -> dict[str, bytes]:
    """Read adjacent ZIP members with one HTTP range request."""
    if not entries:
        return {}
    ordered = sorted(entries, key=lambda entry: entry["local_header_offset"])
    start = ordered[0]["local_header_offset"]
    last = ordered[-1]
    last_header, _ = request_bytes(url, last["local_header_offset"], last["local_header_offset"] + 29)
    last_fields = struct.unpack("<4s5H3I2H", last_header)
    if last_fields[0] != LOCAL_SIG:
        raise ValueError(f"Malformed local ZIP header for {last['name']}")
    filename_length, extra_length = last_fields[-2:]
    end = last["local_header_offset"] + 30 + filename_length + extra_length + last["compressed_size"] - 1
    data, _ = request_bytes(url, start, end)
    result = {}
    for entry in ordered:
        relative = entry["local_header_offset"] - start
        fields = struct.unpack("<4s5H3I2H", data[relative : relative + 30])
        if fields[0] != LOCAL_SIG:
            raise ValueError(f"Malformed local ZIP header for {entry['name']}")
        filename_length, extra_length = fields[-2:]
        payload_start = relative + 30 + filename_length + extra_length
        payload = data[payload_start : payload_start + entry["compressed_size"]]
        if len(payload) != entry["compressed_size"]:
            raise ValueError(f"Truncated ZIP member {entry['name']}")
        if entry["method"] == 0:
            content = payload
        elif entry["method"] == 8:
            content = zlib.decompress(payload, -15)
        else:
            raise ValueError(f"Unsupported ZIP compression method {entry['method']}")
        result[entry["name"]] = content
    return result


def clip_polygon_to_bbox(points: list[list[float]], bbox: tuple[float, float, float, float]) -> list[list[float]]:
    """Clip a polygon ring to an axis-aligned WGS84 rectangle."""
    xmin, ymin, xmax, ymax = bbox
    boundaries = (
        (0, xmin, lambda p: p[0] >= xmin),
        (0, xmax, lambda p: p[0] <= xmax),
        (1, ymin, lambda p: p[1] >= ymin),
        (1, ymax, lambda p: p[1] <= ymax),
    )
    clipped = points[:-1] if points and points[0] == points[-1] else points[:]
    for axis, value, inside in boundaries:
        if not clipped:
            break
        output = []
        prev = clipped[-1]
        prev_inside = inside(prev)
        for cur in clipped:
            cur_inside = inside(cur)
            if cur_inside != prev_inside:
                other = 1 - axis
                denom = cur[axis] - prev[axis]
                fraction = (value - prev[axis]) / denom
                cross = [0.0, 0.0]
                cross[axis] = value
                cross[other] = prev[other] + fraction * (cur[other] - prev[other])
                output.append(cross)
            if cur_inside:
                output.append(cur)
            prev, prev_inside = cur, cur_inside
        clipped = output
    return clipped


def approximate_area_km2(points: list[list[float]]) -> float:
    if len(points) < 3:
        return 0.0
    mean_lat = sum(point[1] for point in points) / len(points)
    xy = [
        (lon * 111.32 * math.cos(math.radians(mean_lat)), lat * 110.574)
        for lon, lat in points
    ]
    area = 0.0
    for index, (x, y) in enumerate(xy):
        x2, y2 = xy[(index + 1) % len(xy)]
        area += x * y2 - x2 * y
    return abs(area) / 2


def area_bbox(area: dict) -> tuple[float, float, float, float]:
    return tuple(map(float, area["aoi_bbox_wgs84"].split(",")))


def area_key(area: dict) -> str:
    return f"{area['region']}/{area['city']}"


def inspect_item(entry: dict, content: bytes, areas: list[dict]) -> dict:
    item = json.loads(content)
    ring = item["geometry"]["coordinates"][0]
    records = []
    for area in areas:
        bbox = area_bbox(area)
        clipped = clip_polygon_to_bbox(ring, bbox)
        overlap_area = approximate_area_km2(clipped)
        if overlap_area <= 0:
            continue
        props = item.get("properties", {})
        records.append({
            "area": area_key(area),
            "overlap_area_km2_approx": round(overlap_area, 5),
            "overlap_fraction_of_nominal_aoi": round(overlap_area / float(area["aoi_area_km2"]), 7),
        })
    props = item.get("properties", {})
    return {
        "item_id": item.get("id"),
        "datetime": props.get("datetime"),
        "location_code": props.get("ufo:location_code"),
        "location": props.get("ufo:location"),
        "event_description": props.get("ufo:event_description"),
        "estimated_flooding_dates": props.get("ufo:estimated_flooding_dates"),
        "flood_driver": props.get("ufo:flood_driver"),
        "gsd_m": props.get("gsd"),
        "cloud_cover_pct": props.get("eo:cloud_cover"),
        "label_water_pixel_count": props.get("ufo:label_water_pixel_count"),
        "label_total_pixel_count": props.get("ufo:label_total_pixel_count"),
        "label_water_pixel_fraction": props.get("ufo:label_water_pixel_fraction"),
        "bbox_wgs84": item.get("bbox"),
        "overlapping_areas": records,
    }


def audit(areas: list[dict], max_workers: int = 16) -> dict:
    record = json.load(urllib.request.urlopen(ZENODO_API, timeout=30))
    archive = next(f for f in record["files"] if f["key"].startswith("UFO_core_data_"))
    zip_url = archive["links"]["self"]
    entries, remote_zip_size = zip_entries(zip_url)
    item_entries = [entry for entry in entries if "/catalog/items/" in entry["name"] and entry["name"].endswith(".json")]
    chips = []
    errors = []
    try:
        # These catalog records are contiguous in the published archive. One small
        # range fetch avoids hundreds of requests to Zenodo's rate-limited endpoint.
        contents = zip_read_contiguous_members(zip_url, item_entries)
        for entry in item_entries:
            try:
                chips.append(inspect_item(entry, contents[entry["name"]], areas))
            except Exception as exc:
                errors.append({"item": entry["name"], "error": f"{type(exc).__name__}: {exc}"})
    except Exception as exc:
        errors.extend({"item": entry["name"], "error": f"{type(exc).__name__}: {exc}"} for entry in item_entries)
    chips.sort(key=lambda item: (item.get("location_code") or "", item.get("datetime") or "", item.get("item_id") or ""))
    by_area = defaultdict(list)
    for chip in chips:
        for match in chip["overlapping_areas"]:
            by_area[match["area"]].append({**chip, **match})
    summaries = {}
    for area in areas:
        key = area_key(area)
        matches = by_area[key]
        summaries[key] = {
            "chip_count": len(matches),
            "event_descriptions": sorted({m.get("event_description") for m in matches if m.get("event_description")}),
            "locations": sorted({m.get("location") for m in matches if m.get("location")}),
            "acquisition_dates": sorted({(m.get("datetime") or "")[:10] for m in matches}),
            "overlap_area_km2_approx_sum_with_possible_chip_overlap": round(sum(m["overlap_area_km2_approx"] for m in matches), 5),
            "nominal_aoi_overlap_fraction_sum_with_possible_chip_overlap": round(sum(m["overlap_fraction_of_nominal_aoi"] for m in matches), 7),
            "chip_records": [
                {key: m[key] for key in (
                    "item_id", "datetime", "location_code", "location", "event_description",
                    "estimated_flooding_dates", "flood_driver", "gsd_m", "cloud_cover_pct",
                    "label_water_pixel_count", "label_total_pixel_count", "label_water_pixel_fraction",
                    "bbox_wgs84", "overlap_area_km2_approx", "overlap_fraction_of_nominal_aoi"
                )}
                for m in matches
            ],
        }
    return {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Urban Flood Observations (UFOv2), latest Zenodo concept record",
        "zenodo_record_id": record["id"],
        "doi": record.get("doi"),
        "concept_doi": record.get("conceptdoi"),
        "release_version": record.get("metadata", {}).get("version"),
        "license": record.get("metadata", {}).get("license", {}).get("id"),
        "archive_file": archive["key"],
        "archive_checksum": archive.get("checksum"),
        "archive_bytes": archive.get("size"),
        "zip_total_bytes": remote_zip_size,
        "zip_member_count": len(entries),
        "stac_chip_item_count": len(item_entries),
        "successfully_inspected_item_count": len(chips),
        "processing_errors": errors,
        "registered_area_count": len(areas),
        "overlapping_chip_count": sum(bool(chip["overlapping_areas"]) for chip in chips),
        "registered_areas": summaries,
        "items": chips,
        "interpretation": [
            "This is a metadata footprint screen; no image or label raster pixels were downloaded or compared.",
            "The dataset contains post-flood PlanetScope imagery and manually annotated visible surface-water masks; masks include pre-existing water and do not separate floodwater from permanent water.",
            "The dataset release notes no pre-flood imagery. It cannot alone satisfy the ATLAS matched event/baseline design.",
            "Overlapping area is approximate WGS84 polygon clipping; per-area sums may double-count overlapping chips and are not deduplicated coverage.",
            "Human labels offer a different sensor than OPERA Sentinel-1 but still require review for temporal match, sampling adequacy, and independent quality controls before any score change.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--areas", type=Path, default=Path("data/study_area_register.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/atlas-ufo-dataset-coverage-audit.json"))
    parser.add_argument("--max-workers", type=int, default=1, help="Retained for CLI compatibility; archive catalog is read in one request")
    args = parser.parse_args()
    areas = json.loads(args.areas.read_text(encoding="utf-8")).get("results", [])
    report = audit(areas, args.max_workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {args.output}: {report['stac_chip_item_count']} chips; "
        f"{report['overlapping_chip_count']} overlap the {len(areas)} AOIs; "
        f"{len(report['processing_errors'])} errors."
    )


if __name__ == "__main__":
    main()
