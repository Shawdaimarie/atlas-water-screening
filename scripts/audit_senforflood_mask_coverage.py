#!/usr/bin/env python3
"""Audit SenForFlood flood-mask chip coverage against the fixed ATLAS AOIs.

This is source-discovery/coverage evidence only. DFO masks are automatic
change-detection outputs and are not independent ground truth. CEMS masks are
analyst-created dataset labels but retain source-lineage, event-timing, license,
and adequacy checks before possible reference use.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import box, mapping
from rasterio.warp import transform_bounds, transform_geom


REPO_ID = "matosak/SenForFlood"
API_BASE = f"https://huggingface.co/api/datasets/{REPO_ID}/tree"
FILE_BASE = f"https://huggingface.co/datasets/{REPO_ID}/resolve"
DATASET_API = f"https://huggingface.co/api/datasets/{REPO_ID}"
DATAVERSE_API = "https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/ZQCODX"
REGISTER = Path("data/study_area_register.json")
OUTPUT = Path("outputs/atlas-senforflood-mask-coverage-audit.json")
CACHE = Path("work/senforflood-mask-cache")
UA = "ATLAS-SenForFlood-mask-coverage-audit/1.0"


def _request(url: str, *, timeout: int = 90) -> tuple[bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    last_error: Exception | None = None
    for attempt in range(10):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read(), dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in (408, 425, 429, 500, 502, 503, 504):
                raise
            retry_after = exc.headers.get("Retry-After", "")
            try:
                delay = float(retry_after)
            except (TypeError, ValueError):
                delay = min(2**attempt, 30)
        except (TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            delay = min(2**attempt, 30)
        time.sleep(min(delay, 60))
    assert last_error is not None
    raise last_error


def _json_url(url: str) -> tuple[Any, dict[str, str]]:
    raw, headers = _request(url)
    return json.loads(raw), headers


def select_mask_manifest_entries(entries: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    mask_tifs = [
        row for row in entries
        if row.get("type") == "file"
        and "/flood_mask/" in row.get("path", "")
        and row["path"].lower().endswith(".tif")
    ]
    masks = [row for row in mask_tifs if not Path(row["path"]).name.startswith("._")]
    return masks, len(mask_tifs) - len(masks)


def get_source_manifest() -> tuple[str, list[dict[str, Any]], dict[str, Any], int]:
    dataset_meta, _ = _json_url(DATASET_API)
    revision = str(dataset_meta.get("sha") or "")
    if not revision:
        raise RuntimeError("Hugging Face dataset API did not return a pinned repository revision")
    url = API_BASE + f"/{revision}?recursive=true&expand=false&limit=1000"
    entries: list[dict[str, Any]] = []
    while url:
        page, headers = _json_url(url)
        entries.extend(page)
        link = headers.get("Link", "")
        match = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = match.group(1) if match else ""
    masks, hidden_files_excluded = select_mask_manifest_entries(entries)
    return revision, masks, dataset_meta, hidden_files_excluded


def load_areas(path: Path = REGISTER) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    areas = payload.get("results", [])
    if len(areas) != 16:
        raise ValueError(f"Expected 16 registered areas, found {len(areas)}")
    out = []
    for area in areas:
        bbox = [float(v) for v in area["aoi_bbox_wgs84"].split(",")]
        if len(bbox) != 4:
            raise ValueError(f"Invalid AOI bbox for {area.get('city')}")
        out.append({
            "key": f"{area['region']}/{area['city']}",
            "region": area["region"],
            "city": area["city"],
            "bbox": bbox,
            "geometry": box(*bbox),
        })
    return out


def _cache_name(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8")).hexdigest() + ".tif"


def fetch_mask(row: dict[str, Any], revision: str, cache_dir: Path) -> tuple[dict[str, Any], Path, str]:
    path = row["path"]
    target = cache_dir / _cache_name(path)
    if target.exists() and target.stat().st_size == int(row.get("size", -1)):
        raw = target.read_bytes()
    else:
        encoded = urllib.parse.quote(path, safe="/")
        url = f"{FILE_BASE}/{revision}/{encoded}?download=true"
        raw, _ = _request(url, timeout=180)
        expected = int(row.get("size", -1))
        if expected >= 0 and len(raw) != expected:
            raise ValueError(f"Size mismatch for {path}: expected {expected}, received {len(raw)}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return row, target, hashlib.sha256(raw).hexdigest()


def inspect_mask(
    row: dict[str, Any], path: Path, sha256: str, areas: list[dict[str, Any]],
) -> dict[str, Any]:
    with rasterio.open(path) as src:
        if src.crs is None:
            return {"path": row["path"], "error": "missing CRS"}
        bounds4326 = transform_bounds(src.crs, "EPSG:4326", *src.bounds, densify_pts=21)
        footprint = box(*bounds4326)
        matches = []
        for area in areas:
            if not footprint.intersects(area["geometry"]):
                continue
            geom_in_src = transform_geom("EPSG:4326", src.crs, mapping(area["geometry"]), precision=8)
            inside = geometry_mask([geom_in_src], out_shape=src.shape, transform=src.transform, invert=True)
            if not inside.any():
                continue
            data = src.read(1)
            valid_inside = inside.copy()
            if src.nodata is not None:
                valid_inside &= data != src.nodata
            values, counts = np.unique(data[valid_inside], return_counts=True)
            class_counts = {str(int(v)): int(n) for v, n in zip(values, counts)}
            matches.append({
                "area": area["key"],
                "chip_pixels_inside_aoi": int(inside.sum()),
                "valid_mask_pixels_inside_aoi": int(valid_inside.sum()),
                "mask_class_counts_inside_chip_aoi_intersection": class_counts,
            })
        data = src.read(1)
        parts = row["path"].split("/")
        source = parts[0] if parts else "unknown"
        event = "/".join(parts[:3]) if source == "DFO" else "/".join(parts[:2])
        return {
            "path": row["path"],
            "repository_oid": row.get("oid"),
            "size_bytes": row.get("size"),
            "sha256": sha256,
            "source_group": source,
            "event_group": event,
            "crs": src.crs.to_string(),
            "shape": list(src.shape),
            "nodata": src.nodata,
            "mask_class_counts": {str(int(v)): int(n) for v, n in zip(*np.unique(data, return_counts=True))},
            "bounds_wgs84": [round(float(v), 8) for v in bounds4326],
            "intersections": matches,
        }


def run_audit(cache_dir: Path = CACHE, register: Path = REGISTER) -> dict[str, Any]:
    revision, masks, hf_meta, hidden_files_excluded = get_source_manifest()
    areas = load_areas(register)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        fetched = list(pool.map(lambda row: fetch_mask(row, revision, cache_dir), masks))
    inspected = [inspect_mask(row, path, sha, areas) for row, path, sha in fetched]
    failures = [item for item in inspected if item.get("error")]
    if failures:
        raise RuntimeError(f"Could not read {len(failures)} flood-mask TIFFs; first: {failures[0]}")
    intersections = [item for item in inspected if item["intersections"]]
    per_area: dict[str, dict[str, Any]] = {}
    for area in areas:
        chips = [
            {"path": item["path"], "event_group": item["event_group"], **match}
            for item in intersections for match in item["intersections"] if match["area"] == area["key"]
        ]
        per_area[area["key"]] = {
            "region": area["region"],
            "city": area["city"],
            "intersecting_mask_chips": len(chips),
            "intersecting_event_groups": sorted({item["event_group"] for item in chips}),
            "source_groups": sorted({item["event_group"].split("/")[0] for item in chips}),
            "total_valid_pixels_across_chips_not_deduplicated": sum(
                item["valid_mask_pixels_inside_aoi"] for item in chips
            ),
            "chip_intersections": chips,
        }
    dv, _ = _json_url(DATAVERSE_API)
    version = dv.get("data", {}).get("latestVersion", {})
    return {
        "audit_id": "atlas_senforflood_mask_coverage",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": {
            "dataset": "SenForFlood",
            "huggingface_repo": f"https://huggingface.co/datasets/{REPO_ID}",
            "huggingface_revision": revision,
            "huggingface_metadata_last_modified": hf_meta.get("lastModified"),
            "huggingface_license_tag": next((tag.split(":", 1)[1] for tag in hf_meta.get("tags", []) if tag.startswith("license:")), None),
            "dataverse_doi": "10.7910/DVN/ZQCODX",
            "dataverse_version": version.get("versionNumber"),
            "dataverse_publication_date": version.get("publicationDate"),
            "dataverse_license": version.get("license"),
            "manifest_mask_files": len(masks),
            "manifest_mask_bytes": sum(int(row.get("size", 0)) for row in masks),
            "mask_file_sha256_count": len(inspected),
            "nonstandard_hidden_appledouble_tif_files_excluded": hidden_files_excluded,
            "mask_files_by_source_group": {
                group: sum(1 for item in inspected if item["source_group"] == group)
                for group in sorted({item["source_group"] for item in inspected})
            },
            "event_groups": len({item["event_group"] for item in inspected}),
        },
        "method": {
            "fixed_aoi": "Exact intersection with the same registered WGS84 bounding boxes used by ATLAS.",
            "coverage_unit": "Mask-chip pixels intersecting each fixed AOI. Counts may repeat across chips/events and are not deduplicated; not an AOI-wide coverage fraction.",
            "label_interpretation": "Source-coded mask values only; no value is assumed to mean independently verified floodwater without source-specific lineage review.",
            "eligibility": "Discovery only. DFO masks are automatic change-detection outputs. Neither source group is treated as confirmatory independent truth by this screen.",
        },
        "summary": {
            "registered_areas": len(areas),
            "us_areas": sum(1 for a in areas if a["region"] == "United States"),
            "international_areas": sum(1 for a in areas if a["region"] != "United States"),
            "valid_mask_files_inspected": len(inspected),
            "mask_chips_intersecting_any_area": len(intersections),
            "areas_with_any_mask_chip_intersection": sum(1 for row in per_area.values() if row["intersecting_mask_chips"]),
            "areas_with_confirmatory_independent_labels_from_this_audit": 0,
        },
        "areas": list(per_area.values()),
        "intersecting_mask_chips": intersections,
        "source_file_checksums": [
            {"path": item["path"], "repository_oid": item["repository_oid"],
             "size_bytes": item["size_bytes"], "sha256": item["sha256"]}
            for item in inspected
        ],
        "limitations": [
            "SenForFlood's published abstract describes 350+ events across continents, but this Hugging Face repository marks uploads as in progress; this audit reflects only the pinned repository revision, not necessarily the full Dataverse release.",
            "A mask-chip intersection does not establish an event date, full AOI coverage, correct projection alignment to OPERA, license compatibility for redistribution, or independent pixel truth.",
            "The DFO subset uses automatically generated masks. CEMS labels are analyst-created but require event, imagery-lineage, source-provenance, and spatial-coverage review before any independent reference use.",
            "Per-chip pixel counts are repeated across temporal samples and must not be summed as unique area coverage.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=CACHE)
    parser.add_argument("--register", type=Path, default=REGISTER)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    report = run_audit(args.cache_dir, args.register)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report["summary"], indent=2))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
