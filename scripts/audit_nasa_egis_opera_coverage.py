#!/usr/bin/env python3
"""Screen NASA EGIS disaster-service catalog footprints against ATLAS AOIs.

This audits public catalog metadata only. It does not download or classify
rasters, establish valid-pixel coverage, select study events, or provide
independent flood labels.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable


BASE_URL = "https://gis.earthdata.nasa.gov/portal/rest/services"
REGISTER_PATH = Path("data/study_area_register.json")
DEFAULT_OUTPUT = Path("outputs/atlas-nasa-egis-opera-footprint-audit.json")
OUT_FIELDS = "OBJECTID,Name,Date,ProductName,GroupName,Category"
FetchJson = Callable[[str, dict[str, str]], dict[str, Any]]


def fetch_json(url: str, params: dict[str, str]) -> dict[str, Any]:
    """Fetch a public NASA ArcGIS REST JSON response with bounded retries."""
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{url}?{query}",
        headers={"User-Agent": "ATLAS-public-metadata-audit/1.0"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.load(response)
            if isinstance(data, dict) and data.get("error"):
                raise RuntimeError(json.dumps(data["error"], sort_keys=True))
            return data
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            if attempt == 2:
                raise RuntimeError(f"NASA EGIS request failed for {url}: {exc}") from exc
            time.sleep(0.25 * (2**attempt))
    raise AssertionError("unreachable")


def is_opera_dswx_image_service(name: str, service_type: str) -> bool:
    normalized = name.casefold()
    return service_type == "ImageServer" and "opera" in normalized and "dswx" in normalized


def bbox_intersects(extent: dict[str, Any], bbox: tuple[float, float, float, float]) -> bool:
    """Cheap coarse rejection for geographic service extents only."""
    sr = extent.get("spatialReference") or {}
    wkid = sr.get("latestWkid", sr.get("wkid"))
    if wkid not in {4326, 4269}:
        return True
    xmin, ymin, xmax, ymax = bbox
    return not (
        xmax < extent["xmin"] or xmin > extent["xmax"]
        or ymax < extent["ymin"] or ymin > extent["ymax"]
    )


def make_spatial_query(bbox: tuple[float, float, float, float]) -> dict[str, str]:
    xmin, ymin, xmax, ymax = bbox
    geometry = {
        "xmin": xmin,
        "ymin": ymin,
        "xmax": xmax,
        "ymax": ymax,
        "spatialReference": {"wkid": 4326},
    }
    return {
        "where": "1=1",
        "geometry": json.dumps(geometry, separators=(",", ":")),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": OUT_FIELDS,
        "returnGeometry": "false",
        "f": "json",
    }


def catalog_record(attributes: dict[str, Any]) -> dict[str, Any]:
    """Preserve source attributes and normalize only the service date field."""
    raw_date = attributes.get("date")
    if isinstance(raw_date, (int, float)):
        date_utc = dt.datetime.fromtimestamp(raw_date / 1000, dt.timezone.utc).date().isoformat()
    else:
        date_utc = None
    name = str(attributes.get("name") or "")
    product = str(attributes.get("productname") or "")
    identity = f"{name} {product}".casefold()
    is_s1_water = (
        ("dswx_s1" in identity or "dswx-s1" in identity)
        and ("wtr" in identity or "bwtr" in identity)
        and "change" not in identity
        and "chng" not in identity
    )
    return {
        "object_id": attributes.get("objectid"),
        "name": attributes.get("name"),
        "date_raw": raw_date,
        "date_utc": date_utc,
        "product_name": product or None,
        "group_name": attributes.get("groupname"),
        "category": attributes.get("category"),
        "candidate_sentinel1_water_observation": is_s1_water,
        "metadata_only": True,
    }


def _read_service(
    folder: str,
    service_name: str,
    areas: list[dict[str, Any]],
    fetch: FetchJson,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    base = f"{BASE_URL}/{urllib.parse.quote(folder, safe='')}/{urllib.parse.quote(service_name, safe='')}/ImageServer"
    metadata = fetch(base, {"f": "json"})
    service_url = base
    service_title = metadata.get("name", service_name)
    extent = metadata.get("fullExtent") or {}
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for area in areas:
        bbox = tuple(float(value) for value in area["aoi_bbox_wgs84"].split(","))
        if not bbox_intersects(extent, bbox):
            continue
        try:
            response = fetch(f"{base}/query", make_spatial_query(bbox))
            for feature in response.get("features", []):
                records.append({
                    "city": area["city"],
                    "region": area["region"],
                    "service_folder": folder,
                    "service_name": service_title,
                    "service_url": service_url,
                    "catalog": catalog_record(feature.get("attributes") or {}),
                })
        except Exception as exc:  # retain failures; an incomplete catalog screen is not a pass
            errors.append({"city": area["city"], "service_url": service_url, "error": str(exc)})
    service = {
        "folder": folder,
        "name": service_title,
        "url": service_url,
        "description": str(metadata.get("serviceDescription") or "")[:1200],
        "extent": extent,
        "service_data_type": metadata.get("serviceDataType"),
    }
    return {"service": service, "errors": errors}, records


def audit(register_path: Path = REGISTER_PATH, fetch: FetchJson = fetch_json) -> dict[str, Any]:
    register = json.loads(register_path.read_text(encoding="utf-8"))
    areas = register["results"]
    if (
        len(areas) != 16
        or sum(a["region"] == "United States" for a in areas) != 8
        or sum(a["region"] != "United States" for a in areas) != 8
    ):
        raise ValueError("Expected the canonical 8 U.S. and 8 international area register")
    root = fetch(BASE_URL, {"f": "json"})
    folders = sorted(folder for folder in root.get("folders", []) if "DISASTERS" in folder.upper())

    def list_folder(folder: str) -> tuple[str, list[dict[str, str]]]:
        data = fetch(f"{BASE_URL}/{urllib.parse.quote(folder, safe='')}", {"f": "json"})
        return folder, data.get("services", [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        folder_results = list(pool.map(list_folder, folders))
    services = sorted(
        (folder, entry["name"])
        for folder, entries in folder_results
        for entry in entries
        if is_opera_dswx_image_service(entry.get("name", ""), entry.get("type", ""))
    )

    def read(item: tuple[str, str]):
        folder, service_name = item
        try:
            return _read_service(folder, service_name, areas, fetch)
        except Exception as exc:
            base = (
                f"{BASE_URL}/{urllib.parse.quote(folder, safe='')}/"
                f"{urllib.parse.quote(service_name, safe='')}/ImageServer"
            )
            return ({
                "service": {"folder": folder, "name": service_name, "url": base},
                "errors": [{"city": "*", "service_url": base, "stage": "service_metadata", "error": str(exc)}],
            }, [])

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(read, services))
    service_records = [item[0] for item in results]
    records = [record for item in results for record in item[1]]
    errors = [error for item in service_records for error in item["errors"]]

    per_area: list[dict[str, Any]] = []
    for area in areas:
        rows = [row for row in records if row["city"] == area["city"]]
        s1_rows = [row for row in rows if row["catalog"]["candidate_sentinel1_water_observation"]]
        s1_dates = sorted({row["catalog"]["date_utc"] for row in s1_rows if row["catalog"]["date_utc"]})
        per_area.append({
            "city": area["city"],
            "region": area["region"],
            "s1_water_catalog_footprint_records": len(s1_rows),
            "s1_water_catalog_dates": s1_dates,
            "all_opera_catalog_records": len(rows),
            "records": rows,
        })

    return {
        "schema_version": 1,
        "audit_id": "atlas-nasa-egis-opera-footprint-audit",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": {
            "service_directory": BASE_URL,
            "register": str(register_path),
            "folder_filter": "folder name contains DISASTERS; ImageServer name contains OPERA and DSWx",
            "spatial_test": "NASA ArcGIS ImageServer catalog query intersects each fixed AOI WGS84 envelope",
        },
        "coverage_limit": (
            "Catalog item footprints do not prove valid pixels, source raster availability, event relevance, "
            "independent flood truth, or confirmatory enrollment. Disaster-response maps may be preliminary; "
            "inspect each source description and product lineage before analysis."
        ),
        "counts": {
            "candidate_disaster_folders": len(folders),
            "candidate_opera_dswx_image_services": len(services),
            "service_metadata_errors": sum(
                error.get("stage") == "service_metadata" for error in errors
            ),
            "area_service_query_errors": len(errors),
            "catalog_footprint_records": len(records),
            "areas_with_s1_water_footprint_records": sum(
                bool(a["s1_water_catalog_footprint_records"]) for a in per_area
            ),
        },
        "services": [item[0]["service"] for item in results],
        "areas": per_area,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=REGISTER_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = audit(args.register)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))
    print(f"Wrote {args.output}")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
