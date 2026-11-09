#!/usr/bin/env python3
"""Screen Copernicus EMS Risk & Recovery product AOIs against ATLAS study boxes.

This is a discovery audit only. Catalog AOI overlap does not establish event
labels, source independence, imagery lineage, or valid OPERA observations.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import requests
from shapely import wkt
from shapely.geometry import box

CATALOG_URL = "https://riskandrecovery.emergency.copernicus.eu/api/public-activations/"
SOURCE_GUIDE = "https://mapping.emergency.copernicus.eu/about/how-to-harvest-cems-mapping-data/preparedness-and-recovery-data/"
REGISTER_PATH = Path("data/study_area_register.json")
OUTPUT_PATH = Path("outputs/atlas-cems-risk-recovery-aoi-audit.json")


def fetch_catalog(session: requests.Session) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    urls: list[str] = []
    url: str | None = CATALOG_URL
    while url:
        urls.append(url)
        response = session.get(url, timeout=60)
        response.raise_for_status()
        page = response.json()
        if not isinstance(page, dict) or not isinstance(page.get("results"), list):
            raise ValueError("Expected a paginated JSON activation catalog")
        rows.extend(page["results"])
        url = page.get("next")
    codes = [x.get("code") for x in rows]
    if len(codes) != len(set(codes)):
        raise ValueError("Catalog returned duplicate activation codes")
    return rows, urls


def audit(register_path: Path = REGISTER_PATH, output_path: Path = OUTPUT_PATH,
          session: requests.Session | None = None) -> dict[str, Any]:
    register = json.loads(register_path.read_text(encoding="utf-8"))
    areas = register["results"]
    if len(areas) != 16 or sum(x["region"] == "United States" for x in areas) != 8:
        raise ValueError("Expected the canonical 8 U.S. + 8 international frame")
    shapes = [(a, box(*map(float, a["aoi_bbox_wgs84"].split(",")))) for a in areas]
    own_session = session is None
    session = session or requests.Session()
    if own_session:
        session.headers.update({"User-Agent": "ATLAS-evidence-screen/1.0"})
    catalog, page_urls = fetch_catalog(session)
    matches: list[dict[str, Any]] = []
    for activation in catalog:
        for product in activation.get("products") or []:
            for source_aoi in product.get("linkedAois") or []:
                extent = source_aoi.get("extent")
                if not extent:
                    continue
                source_shape = wkt.loads(extent)
                for area, site_shape in shapes:
                    if source_shape.intersects(site_shape):
                        matches.append({
                            "city": area["city"], "region": area["region"],
                            "activation_code": activation.get("code"),
                            "activation_name": activation.get("name"),
                            "category": activation.get("category"),
                            "sub_category": activation.get("subCategory"),
                            "event_time": activation.get("eventTime"),
                            "phase": activation.get("actDrmPhase"),
                            "closed": activation.get("closed"),
                            "product_name": product.get("productName"),
                            "product_analysis": product.get("analysisName"),
                            "source_aoi_name": source_aoi.get("aoiName"),
                            "source_aoi_extent_wkt": extent,
                            "source_aoi_area_km2": source_aoi.get("sqkm"),
                            "activation_url": f"{CATALOG_URL}?code={activation.get('code')}",
                        })
    per_area = []
    for area in areas:
        rows = [x for x in matches if x["city"] == area["city"]]
        per_area.append({"city": area["city"], "region": area["region"],
                         "intersecting_product_aois": len(rows),
                         "distinct_activations": len({x["activation_code"] for x in rows}),
                         "flood_activations": len({x["activation_code"] for x in rows if str(x["category"]).casefold() == "flood"})})
    flood_codes = sorted({x.get("code") for x in catalog if str(x.get("category", "")).casefold() == "flood"})
    result = {
        "schema_version": 1,
        "audit_id": "atlas-cems-risk-recovery-aoi-audit",
        "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "source": {"name": "Copernicus EMS Risk & Recovery public activation catalog",
                   "catalog_url": CATALOG_URL, "documentation_url": SOURCE_GUIDE,
                   "page_urls": page_urls, "activation_count": len(catalog),
                   "flood_activation_count": len(flood_codes), "flood_activation_codes": flood_codes},
        "study_frame": {"area_count": len(areas), "us_area_count": 8, "international_area_count": 8,
                        "footprint": "Fixed 25 km x 25 km WGS84 screening bounding boxes in data/study_area_register.json"},
        "counts": {"product_aoi_intersections": len(matches),
                   "intersecting_flood_product_aois": sum(str(x["category"]).casefold() == "flood" for x in matches),
                   "areas_with_any_intersection": sum(x["intersecting_product_aois"] > 0 for x in per_area),
                   "areas_with_flood_intersection": sum(x["flood_activations"] > 0 for x in per_area)},
        "areas": per_area,
        "matches": matches,
        "limits": ["Catalog AOI polygons were intersected with ATLAS fixed bounding boxes; this is a geographic discovery screen.",
                   "A non-match does not prove no useful product exists outside the currently published catalog.",
                   "Product AOI overlap is not an independent reference label or field observation; imagery lineage, class semantics, resolution, licensing, event-time suitability, and pixel-level coverage require review.",
                   "No study-area eligibility or score is awarded by this screen."],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=REGISTER_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    result = audit(args.register, args.output)
    print(json.dumps({"catalog_count": result["source"]["activation_count"],
                      "flood_count": result["source"]["flood_activation_count"],
                      **result["counts"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
