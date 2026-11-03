#!/usr/bin/env python3
"""Screen Global Flood Database MODIS event maps in registered ATLAS AOIs.

This is a historical reference-coverage discovery audit, not evidence that GFD
is contemporaneous ground truth for the current OPERA study window.
The source is licensed CC BY-NC 4.0 and must not be used commercially.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import shapefile
from rasterio.features import geometry_mask
from shapely.geometry import box, shape


SOURCE_COMMIT = "0d20b91d124b5a9987d40392b5e3463d78f1f894"
SOURCE_BASE = (
    "https://raw.githubusercontent.com/cloudtostreet/"
    f"MODIS_GlobalFloodDatabase/{SOURCE_COMMIT}/data/shp_files/"
)
SHAPE_BASENAME = "dfo_polys_20191203"
SHAPE_EXTENSIONS = ("shp", "shx", "dbf", "prj")
BUCKET = "gfd_v1_4"
BUCKET_API = f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o"
LICENSE = "CC-BY-NC-4.0"
DEFAULT_REGISTER = Path("data/study_area_register.json")
DEFAULT_OUTPUT = Path("outputs/atlas-gfd-event-extent-coverage-audit.json")
DEFAULT_CACHE = Path("work/gfd-event-map-cache")


def _request_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "ATLAS-GFD-coverage-audit/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        value = json.load(response)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def _download(url: str, path: Path, expected_size: int | None = None) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "ATLAS-GFD-coverage-audit/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = response.read()
    if expected_size is not None and len(payload) != expected_size:
        raise ValueError(f"Download size mismatch: expected {expected_size}, got {len(payload)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return payload


def list_bucket_objects() -> list[dict[str, Any]]:
    url = BUCKET_API + "?maxResults=1000"
    objects: list[dict[str, Any]] = []
    while url:
        page = _request_json(url)
        objects.extend(page.get("items", []))
        token = page.get("nextPageToken")
        url = BUCKET_API + "?maxResults=1000&pageToken=" + urllib.parse.quote(token) if token else ""
    return [item for item in objects if item.get("name", "").endswith(".zip")]


def _event_id_for_filename(name: str) -> int | None:
    parts = name.split("_", 2)
    try:
        return int(parts[1]) if len(parts) >= 3 and parts[0] == "DFO" else None
    except ValueError:
        return None


def _iso(value: Any) -> str | None:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.date().isoformat() if isinstance(value, dt.datetime) else value.isoformat()
    return None


def select_latest_mapped_overlaps(
    event_records: Iterable[dict[str, Any]],
    object_by_event_id: dict[int, dict[str, Any]],
    areas: list[dict[str, Any]],
) -> dict[str, dict[str, Any] | None]:
    """Select latest catalogued mapped event whose DFO polygon intersects AOI."""
    selected: dict[str, dict[str, Any] | None] = {
        f"{area['region']}/{area['city']}": None for area in areas
    }
    aoi_shapes = {
        f"{area['region']}/{area['city']}": box(*map(float, area["aoi_bbox_wgs84"].split(",")))
        for area in areas
    }
    for event in event_records:
        event_id = int(event.get("id", event.get("ID")))
        obj = object_by_event_id.get(event_id)
        if obj is None or event.get("geometry") is None:
            continue
        for key, aoi in aoi_shapes.items():
            if not event["geometry"].intersects(aoi):
                continue
            candidate = {
                "event_id": event_id,
                "event_start": _iso(event.get("Began", event.get("began"))),
                "country": event.get("Country", event.get("country")),
                "main_cause": event.get("MainCause", event.get("maincause")),
                "severity": event.get("Severity", event.get("severity")),
                "area_km2": event.get("Area", event.get("area")),
            }
            candidate["gfd_object"] = {
                "name": obj["name"],
                "size_bytes": int(obj["size"]),
                "md5_hash_base64": obj.get("md5Hash"),
                "crc32c_base64": obj.get("crc32c"),
            }
            candidate["event_end"] = _iso(event.get("Ended", event.get("ended")))
            current = selected[key]
            if current is None or (candidate.get("event_end") or "") > (current.get("event_end") or ""):
                selected[key] = candidate
    return selected


def summarize_aoi_bands(
    bands: dict[str, np.ndarray], aoi_mask: np.ndarray,
) -> dict[str, Any]:
    flooded = bands["flooded"][aoi_mask]
    clear_perc = bands["clear_perc"][aoi_mask]
    duration = bands["duration"][aoi_mask]
    permanent = bands["jrc_perm_water"][aoi_mask]
    valid = np.isfinite(flooded) & np.isin(flooded, (0, 1))
    mapped_water = valid & (flooded == 1)
    permanent_valid = np.isfinite(permanent) & np.isin(permanent, (0, 1))
    nonpermanent_valid = valid & permanent_valid & (permanent == 0)
    event_flood_candidate = mapped_water & permanent_valid & (permanent == 0)
    clear_valid = np.isfinite(clear_perc) & valid
    duration_valid = np.isfinite(duration) & valid
    return {
        "aoi_raster_pixels": int(aoi_mask.sum()),
        "flood_classified_pixels": int(valid.sum()),
        "mapped_water_pixels_including_permanent": int(mapped_water.sum()),
        "nonwater_pixels": int((valid & (flooded == 0)).sum()),
        "classified_fraction_of_aoi": round(float(valid.sum() / aoi_mask.sum()), 6) if aoi_mask.any() else None,
        "jrc_permanent_water_pixels": int((permanent_valid & (permanent == 1) & valid).sum()),
        "jrc_permanent_water_valid_pixels": int((permanent_valid & valid).sum()),
        "nonpermanent_classified_pixels": int(nonpermanent_valid.sum()),
        "event_flood_candidate_pixels": int(event_flood_candidate.sum()),
        "event_flood_candidate_fraction_of_nonpermanent_classified": round(
            float(event_flood_candidate.sum() / nonpermanent_valid.sum()), 6
        ) if nonpermanent_valid.any() else None,
        "clear_perc_valid_pixels": int(clear_valid.sum()),
        "clear_perc_ge_80pct_pixels": int((clear_valid & (clear_perc >= 0.8)).sum()),
        "clear_perc_ge_90pct_pixels": int((clear_valid & (clear_perc >= 0.9)).sum()),
        "duration_valid_event_flood_candidate_pixels": int((duration_valid & event_flood_candidate & (duration > 0)).sum()),
        "gfd_missing_pixels": int((~valid).sum()),
    }


def _load_shapes(cache: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    cache.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for extension in SHAPE_EXTENSIONS:
        name = f"{SHAPE_BASENAME}.{extension}"
        path = cache / name
        if not path.exists():
            _download(SOURCE_BASE + name, path)
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    reader = shapefile.Reader(str(cache / SHAPE_BASENAME), encoding="latin1")
    records = []
    for item in reader.iterShapeRecords():
        attrs = item.record.as_dict()
        records.append({**attrs, "geometry": shape(item.shape.__geo_interface__)})
    return records, hashes


def _read_raster_map(
    obj: dict[str, Any], cache: Path, area: dict[str, Any],
) -> dict[str, Any]:
    import rasterio
    from contextlib import ExitStack
    from rasterio.merge import merge
    from rasterio.warp import transform_bounds

    name = obj["name"]
    zip_path = cache / name
    size = int(obj["size"])
    if not zip_path.exists() or zip_path.stat().st_size != size:
        url = f"https://storage.googleapis.com/{BUCKET}/{urllib.parse.quote(name)}"
        payload = _download(url, zip_path, size)
    else:
        payload = zip_path.read_bytes()
    expected_md5 = obj.get("md5Hash")
    observed_md5 = base64.b64encode(hashlib.md5(payload).digest()).decode("ascii")
    if expected_md5 and observed_md5 != expected_md5:
        raise ValueError(f"GCS MD5 mismatch for {name}")
    zip_sha256 = hashlib.sha256(payload).hexdigest()
    with zipfile.ZipFile(zip_path) as archive:
        tif_members = [item for item in archive.namelist() if item.lower().endswith(".tif")]
        properties_members = [item for item in archive.namelist() if item.endswith("_properties.json")]
        license_members = [item for item in archive.namelist() if item.lower().endswith("license.txt")]
        if not tif_members or len(properties_members) != 1:
            raise ValueError(f"Unexpected GFD archive structure in {name}")
        raster_paths = []
        for member in tif_members:
            raster_path = cache / Path(member).name
            if not raster_path.exists():
                with archive.open(member) as source, raster_path.open("wb") as target:
                    while True:
                        block = source.read(8 * 1024 * 1024)
                        if not block:
                            break
                        target.write(block)
            raster_paths.append(raster_path)
        properties = json.loads(archive.read(properties_members[0]))
        license_text = archive.read(license_members[0]).decode("utf-8", "replace") if license_members else ""
    west, south, east, north = map(float, area["aoi_bbox_wgs84"].split(","))
    geojson = {"type": "Polygon", "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]]}
    with ExitStack() as stack:
        datasets = [stack.enter_context(rasterio.open(path)) for path in raster_paths]
        first = datasets[0]
        if first.crs is None or first.count != 5:
            raise ValueError(f"Unexpected GFD raster CRS or band count for {name}")
        expected_bands = ("flooded", "duration", "clear_views", "clear_perc", "jrc_perm_water")
        if tuple(first.descriptions) != expected_bands:
            raise ValueError(f"Unexpected GFD band names for {name}: {first.descriptions}")
        for dataset in datasets[1:]:
            if dataset.crs != first.crs or dataset.count != 5 or tuple(dataset.descriptions) != expected_bands:
                raise ValueError(f"Inconsistent GFD raster tile in {name}")
        bounds = transform_bounds("EPSG:4326", first.crs, west, south, east, north, densify_pts=21)
        values, transform = merge(
            datasets, bounds=bounds, res=first.res, indexes=[1, 2, 3, 4, 5], nodata=np.nan,
        )
        mask = geometry_mask([geojson], out_shape=values.shape[1:], transform=transform, invert=True)
        stats = summarize_aoi_bands(dict(zip(expected_bands, values)), mask)
        raster_info = {
            "crs": str(first.crs), "resolution": [float(v) for v in first.res],
            "tile_count": len(datasets), "bands": list(first.descriptions),
        }
    return {
        **stats,
        "gfd_object_name": name,
        "gfd_zip_bytes": size,
        "gfd_zip_md5_hash_base64": expected_md5,
        "gfd_zip_sha256": zip_sha256,
        "raster_tiles": [
            {"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in raster_paths
        ],
        "properties": properties,
        "raster": raster_info,
        "license_text_contains_noncommercial": "noncommercial" in license_text.lower() or "non-commercial" in license_text.lower(),
    }


def audit(register_path: Path = DEFAULT_REGISTER, cache_path: Path = DEFAULT_CACHE) -> dict[str, Any]:
    register = json.loads(register_path.read_text(encoding="utf-8"))
    areas = register.get("results")
    if not isinstance(areas, list) or len(areas) != 16:
        raise ValueError("Expected canonical 8 U.S. and 8 international AOIs")
    event_records, shape_hashes = _load_shapes(cache_path / "dfo-source")
    bucket_objects = list_bucket_objects()
    object_by_event_id = {
        event_id: obj for obj in bucket_objects
        if (event_id := _event_id_for_filename(obj.get("name", ""))) is not None
    }
    selected = select_latest_mapped_overlaps(event_records, object_by_event_id, areas)
    area_results = []
    for area in areas:
        key = f"{area['region']}/{area['city']}"
        candidate = selected[key]
        result = {"region": area["region"], "city": area["city"], "selected_event": candidate}
        if candidate is not None:
            obj = object_by_event_id[candidate["event_id"]]
            result["map_screen"] = _read_raster_map(obj, cache_path / "maps", area)
        else:
            result["map_screen"] = None
        area_results.append(result)
    maps = [row["map_screen"] for row in area_results if row["map_screen"]]
    selected_events = [row["selected_event"] for row in area_results if row["selected_event"]]
    return {
        "schema_version": 1,
        "audit_id": "atlas-gfd-event-extent-coverage-audit",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": {
            "repository": "https://github.com/cloudtostreet/MODIS_GlobalFloodDatabase",
            "source_commit": SOURCE_COMMIT,
            "shape_files": {name: SOURCE_BASE + name for name in shape_hashes},
            "shape_file_sha256": shape_hashes,
            "gcs_bucket": f"gs://{BUCKET}",
            "bucket_api": BUCKET_API,
            "bucket_zip_objects": len(bucket_objects),
            "license": LICENSE,
            "license_scope": "research-only, noncommercial use; do not incorporate source maps into commercial products",
        },
        "selection_rule": "For each fixed AOI, select the most recent DFO event polygon with an intersecting geometry and a matching GFD map object; selection is made by event end date before inspecting raster pixels.",
        "spatial_test": "Exact shapefile polygon intersection for event discovery; then raster-cell center inclusion in each fixed registered WGS84 AOI bounding rectangle.",
        "summary": {
            "candidate_areas": 16,
            "areas_with_latest_mapped_event_polygon": sum(row["selected_event"] is not None for row in area_results),
            "areas_with_classified_gfd_pixels": sum(bool(row["map_screen"] and row["map_screen"]["flood_classified_pixels"] > 0) for row in area_results),
            "areas_with_event_flood_candidate_pixels": sum(bool(row["map_screen"] and row["map_screen"]["event_flood_candidate_pixels"] > 0) for row in area_results),
            "total_selected_flood_map_aoi_pixels": sum(row["map_screen"]["aoi_raster_pixels"] for row in area_results if row["map_screen"]),
            "total_selected_flood_classified_pixels": sum(row["map_screen"]["flood_classified_pixels"] for row in area_results if row["map_screen"]),
            "total_selected_event_flood_candidate_pixels": sum(row["map_screen"]["event_flood_candidate_pixels"] for row in area_results if row["map_screen"]),
            "selected_map_event_date_range": [
                min((event.get("event_start") for event in selected_events if event.get("event_start")), default=None),
                max((event.get("event_end") for event in selected_events if event.get("event_end")), default=None),
            ],
        },
        "interpretation_limits": [
            "GFD is an event-specific MODIS-derived water map archive from 2000–2018. The raw flooded band includes permanent water; the event-flood candidate screen excludes pixels marked permanent water in the supplied JRC band. It is a different sensor lineage from Sentinel-1, but is not field truth and has its own algorithm, cloud limitations, DFO event-selection process, and published uncertainty.",
            "The current ATLAS confirmatory product OPERA DSWx-S1 begins after this archive event period. These historical masks cannot validate the current 2024–2026 study window or qualify current-site enrollment.",
            "Only the latest mapped DFO event polygon intersecting each AOI was screened; an intersecting polygon does not imply that the GFD flood raster has valid or flooded pixels within the AOI.",
            "The source license is CC BY-NC 4.0. This audit is research discovery only; GFD source data must not be used commercially without separate permission or a compatible license.",
            "No GFD rasters are committed; reproduce by rerunning the audit to download and checksum selected source maps into the ignored work cache.",
        ],
        "areas": area_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit(args.register, args.cache)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
