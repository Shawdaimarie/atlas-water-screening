#!/usr/bin/env python3
"""Screen public Sen1Floods11 hand-label chip footprints against ATLAS AOIs."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
BUCKET = "sen1floods11"
PREFIX = "v1.1/catalog/sen1floods11_hand_labeled_label/"
LIST_URL = f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o"
AOI_FILE = ROOT / "data/study_area_register.json"
DEFAULT_OUTPUT = ROOT / "outputs/atlas-sen1floods11-label-footprint-audit.json"


def list_metadata_objects() -> list[dict]:
    objects: list[dict] = []
    page_token = None
    while True:
        query = {"prefix": PREFIX, "maxResults": "1000"}
        if page_token:
            query["pageToken"] = page_token
        url = LIST_URL + "?" + urllib.parse.urlencode(query)
        with urllib.request.urlopen(url, timeout=60) as response:
            page = json.load(response)
        objects.extend(page.get("items", []))
        page_token = page.get("nextPageToken")
        if not page_token:
            return objects


def fetch_item(obj: dict) -> tuple[dict, bytes]:
    url = obj.get("mediaLink") or (
        f"https://storage.googleapis.com/{BUCKET}/"
        + urllib.parse.quote(obj["name"], safe="/")
    )
    with urllib.request.urlopen(url, timeout=60) as response:
        body = response.read()
    return json.loads(body), body


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    """Return true only for positive-area overlap of WGS84 [west,south,east,north] boxes."""
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def audit(items: list[tuple[dict, bytes]], areas: list[dict], retrieved_at: str) -> dict:
    if len(areas) != 16 or sum(a["region"] == "United States" for a in areas) != 8:
        raise ValueError("Expected the fixed 8 U.S. + 8 international area register")
    label_items = []
    for item, raw in items:
        if item.get("type") != "Feature" or "bbox" not in item:
            continue  # The prefix also includes its STAC collection document.
        props = item.get("properties", {})
        assets = item.get("assets", {})
        if "LabelHand" not in assets:
            raise ValueError(f"Hand-label catalog item lacks LabelHand asset: {item.get('id')}")
        bbox = item["bbox"]
        if len(bbox) != 4:
            raise ValueError(f"Expected four-value WGS84 bbox for {item.get('id')}")
        label_items.append({
            "id": item["id"],
            "source_country": props.get("country"),
            "datetime": props.get("datetime"),
            "bbox_wgs84": bbox,
            "label_asset": assets["LabelHand"].get("href"),
            "metadata_sha256": hashlib.sha256(raw).hexdigest(),
        })
    if len(label_items) != 446:
        raise ValueError(f"Expected 446 hand-labeled chip items; found {len(label_items)}")
    area_rows = []
    overlaps = []
    for area in areas:
        aoi_bbox = [float(value) for value in area["aoi_bbox_wgs84"].split(",")]
        matched = [item for item in label_items if boxes_intersect(item["bbox_wgs84"], aoi_bbox)]
        area_rows.append({"city": area["city"], "region": area["region"],
                          "aoi_bbox_wgs84": aoi_bbox,
                          "hand_labeled_chip_footprints_intersecting": len(matched),
                          "intersecting_chip_ids": [item["id"] for item in matched]})
        for item in matched:
            overlaps.append({"city": area["city"], "region": area["region"],
                             "chip_id": item["id"], "source_country": item["source_country"],
                             "datetime": item["datetime"], "chip_bbox_wgs84": item["bbox_wgs84"],
                             "label_asset": item["label_asset"]})
    return {
        "audit": "ATLAS Sen1Floods11 hand-labeled chip footprint screen",
        "source": {
            "dataset": "Sen1Floods11 v1.1",
            "repository": "https://github.com/cloudtostreet/Sen1Floods11",
            "paper": "https://openaccess.thecvf.com/content_CVPRW_2020/papers/w11/Bonafilia_Sen1Floods11_A_Georeferenced_Dataset_to_Train_and_Test_Deep_Learning_CVPRW_2020_paper.pdf",
            "public_catalog_prefix": f"gs://{BUCKET}/{PREFIX}",
            "list_api": LIST_URL,
            "retrieved_at_utc": retrieved_at,
            "catalog_objects_listed": len(items),
            "hand_labeled_chip_items": len(label_items),
        },
        "method": {
            "geometry": "STAC item bbox, compared to each fixed rectangular AOI bbox in WGS84",
            "intersection_rule": "strict positive-area bbox intersection; touching boundaries do not count",
            "label_asset_only": "LabelHand; weak labels and Sentinel-1-derived labels are excluded",
            "limits": [
                "Footprint overlap is discovery evidence only; label raster values, valid-pixel fraction, label accuracy, event attribution, and temporal comparability were not inspected.",
                "The dataset paper reports labels from hand review supported by Sentinel-2 classification; the labels are not claimed to be field observations.",
                "No item footprints intersect the fixed ATLAS candidate AOIs, so the dataset supplies no directly matched validation chips for this area register.",
            ],
        },
        "summary": {"areas": 16, "us_areas": 8, "international_areas": 8,
                    "areas_with_label_chip_overlap": sum(row["hand_labeled_chip_footprints_intersecting"] > 0 for row in area_rows),
                    "label_chip_footprint_overlaps": len(overlaps)},
        "areas": area_rows,
        "overlaps": overlaps,
        "catalog_items": label_items,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--area-register", type=Path, default=AOI_FILE)
    args = parser.parse_args()
    objects = list_metadata_objects()
    with ThreadPoolExecutor(max_workers=12) as pool:
        items = list(pool.map(fetch_item, objects))
    area_register = json.loads(args.area_register.read_text())["results"]
    result = audit(items, area_register, datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
