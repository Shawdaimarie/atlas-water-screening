#!/usr/bin/env python3
"""Refresh Copernicus EMS Rapid Mapping flood AOI coverage for ATLAS sites.

This is a public event/product discovery audit. A product-map intersection is
not independent ground truth, a field label, or evidence of QA-valid OPERA
observations. Product imagery provenance is retained so independence can be
assessed separately.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import time
from pathlib import Path
from typing import Any
from email.utils import parsedate_to_datetime

import requests
from shapely import wkt
from shapely.geometry import box


ACTIVATIONS_URL = (
    "https://rapidmapping.emergency.copernicus.eu/backend/"
    "dashboard-api/public-activations-info/"
)
DETAILS_URL = (
    "https://rapidmapping.emergency.copernicus.eu/backend/"
    "dashboard-api/public-activations/"
)
REGISTER_PATH = Path("data/study_area_register.json")
OUTPUT_PATH = Path("outputs/atlas-cems-event-discovery-audit.json")
CACHE_PATH = Path("work/cems-rapid-mapping-cache")
SOURCE_GUIDE = (
    "https://mapping.emergency.copernicus.eu/about/"
    "how-to-harvest-cems-mapping-data/emergency-response-data/"
)


def _get_json(session: requests.Session, url: str) -> dict[str, Any]:
    for attempt in range(7):
        response = session.get(url, timeout=60)
        if response.status_code == 429 and attempt < 6:
            retry_after = response.headers.get("Retry-After")
            try:
                delay = max(1.0, float(retry_after)) if retry_after else min(120.0, 5.0 * 2**attempt)
            except ValueError:
                try:
                    delay = max(1.0, (parsedate_to_datetime(retry_after) - dt.datetime.now(dt.timezone.utc)).total_seconds())
                except Exception:
                    delay = min(120.0, 5.0 * 2**attempt)
            time.sleep(delay)
            continue
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"Expected JSON object from {url}")
        return payload
    raise RuntimeError(f"CEMS rate limit persisted after retries: {url}")


def fetch_catalog(session: requests.Session) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    page_urls: list[str] = []
    url: str | None = ACTIVATIONS_URL
    while url:
        page_urls.append(url)
        page = _get_json(session, url)
        page_rows = page.get("results")
        if not isinstance(page_rows, list):
            raise ValueError("Activation catalog page is missing results array")
        rows.extend(page_rows)
        url = page.get("next")
    if len({row.get("code") for row in rows}) != len(rows):
        raise ValueError("Activation catalog contains duplicate codes")
    return rows, page_urls


def _detail(session: requests.Session, code: str) -> dict[str, Any]:
    CACHE_PATH.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_PATH / f"{code}.json"
    if cache_file.exists():
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
    else:
        payload = _get_json(session, f"{DETAILS_URL}?code={code}")
        cache_file.write_text(json.dumps(payload), encoding="utf-8")
    results = payload.get("results")
    if not isinstance(results, list) or len(results) != 1:
        raise ValueError(f"Expected one detail result for {code}")
    return results[0]


def _product_summary(product: dict[str, Any]) -> dict[str, Any]:
    images = product.get("images") or []
    layers = product.get("layers") or []
    version = product.get("version") or {}
    return {
        "type": product.get("type"),
        "monitoring": product.get("monitoring"),
        "feasible": product.get("feasible"),
        "version_status": version.get("statusCode"),
        "imagery": [
            {
                "sensor_type": image.get("sensorType"),
                "sensor_name": image.get("sensorName"),
                "acquisition_time": image.get("acquisitionTime"),
                "new_post_event": image.get("new"),
            }
            for image in images
        ],
        "layers": [
            {"format": layer.get("format"), "name": layer.get("name")}
            for layer in layers
        ],
        "download_url": product.get("downloadPath"),
        "product_extent_wkt": product.get("extent"),
    }


def audit(
    register_path: Path = REGISTER_PATH,
    output_path: Path = OUTPUT_PATH,
    session: requests.Session | None = None,
    request_pause_seconds: float = 1.0,
) -> dict[str, Any]:
    own_session = session is None
    session = session or requests.Session()
    if own_session:
        session.headers.update({"User-Agent": "ATLAS evidence-screen/1.0"})

    register = json.loads(register_path.read_text(encoding="utf-8"))
    areas = register["results"]
    if len(areas) != 16 or sum(x["region"] == "United States" for x in areas) != 8:
        raise ValueError("Expected canonical 8 U.S. and 8 international study areas")
    site_shapes = [
        (area, box(*map(float, area["aoi_bbox_wgs84"].split(","))))
        for area in areas
    ]

    catalog, page_urls = fetch_catalog(session)
    flood_catalog = [
        row for row in catalog
        if str(row.get("category", "")).casefold() == "flood"
    ]
    matches: list[dict[str, Any]] = []
    for index, item in enumerate(flood_catalog):
        if index and request_pause_seconds:
            time.sleep(request_pause_seconds)
        detail = _detail(session, str(item["code"]))
        for aoi in detail.get("aois") or []:
            extent_text = aoi.get("extent")
            if not extent_text:
                continue
            aoi_shape = wkt.loads(extent_text)
            products = aoi.get("products") or []
            for area, site_shape in site_shapes:
                if not aoi_shape.intersects(site_shape):
                    continue
                products_intersecting_site = []
                for product in products:
                    product_shape_text = product.get("extent")
                    if product_shape_text and wkt.loads(product_shape_text).intersects(site_shape):
                        products_intersecting_site.append(_product_summary(product))
                matches.append({
                    "city": area["city"],
                    "region": area["region"],
                    "activation_code": detail.get("code"),
                    "activation_name": detail.get("name"),
                    "countries": detail.get("countries"),
                    "event_time": detail.get("eventTime"),
                    "event_date": (detail.get("eventTime") or "")[:10] or None,
                    "category": detail.get("category"),
                    "aoi_name": aoi.get("name"),
                    "aoi_number": aoi.get("number"),
                    "aoi_extent_wkt": extent_text,
                    "aoi_intersection_area_km2_approx": round(
                        aoi_shape.intersection(site_shape).area * 111.32**2, 4
                    ),
                    "product_count": len(products),
                    "intersecting_products": products_intersecting_site,
                    "detail_api": f"{DETAILS_URL}?code={detail.get('code')}",
                    "interpretation": (
                        "CEMS analyst-derived event mapping discovery lead; imagery lineage, "
                        "map-label semantics, resolution, licensing, and independent validation "
                        "must be audited before use. Not field truth or an OPERA QA result."
                    ),
                })

    per_area = []
    for area in areas:
        area_matches = [m for m in matches if m["city"] == area["city"]]
        per_area.append({
            "city": area["city"],
            "region": area["region"],
            "intersecting_flood_aois": len(area_matches),
            "distinct_activations": len({m["activation_code"] for m in area_matches}),
            "event_dates": sorted({m["event_date"] for m in area_matches if m["event_date"]}),
        })
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    result = {
        "schema_version": 2,
        "audit_id": "atlas-cems-event-discovery-audit",
        "generated_at_utc": now,
        "source": {
            "name": "Copernicus EMS Rapid Mapping public activations and detail API",
            "guide": SOURCE_GUIDE,
            "catalog_endpoint": ACTIVATIONS_URL,
            "detail_endpoint": DETAILS_URL,
            "catalog_count_reported": len(catalog),
            "catalog_codes_unique": len({row.get("code") for row in catalog}),
            "flood_activations_screened": len(flood_catalog),
            "catalog_pages_retrieved": len(page_urls),
            "catalog_page_urls": page_urls,
        },
        "spatial_test": (
            "Exact Shapely WKT polygon intersection between each public CEMS flood AOI "
            "and the fixed study-area WGS84 bounding rectangle; approximate intersection "
            "area uses degree-squared conversion and is only a screening statistic."
        ),
        "counts": {
            "candidate_areas": len(areas),
            "areas_with_intersecting_flood_aois": sum(x["intersecting_flood_aois"] > 0 for x in per_area),
            "intersecting_flood_aois": len(matches),
            "distinct_intersecting_activations": len({m["activation_code"] for m in matches}),
            "intersecting_products": sum(len(m["intersecting_products"]) for m in matches),
        },
        "areas": per_area,
        "matches": matches,
        "limits": [
            "An AOI polygon overlap only establishes spatial relevance of a mapping activation.",
            "CEMS products can be satellite-derived and are not independent ground truth by themselves.",
            "No labels were extracted, adjudicated, or compared with ATLAS predictions in this audit.",
            "Product imagery sensor provenance and use terms remain to be reviewed for any match.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if own_session:
        session.close()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=REGISTER_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    result = audit(args.register, args.output)
    print(json.dumps({"generated_at_utc": result["generated_at_utc"], **result["counts"]}, indent=2))


if __name__ == "__main__":
    main()
