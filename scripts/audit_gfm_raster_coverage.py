#!/usr/bin/env python3
"""Screen Copernicus GFM COG pixels in fixed ATLAS AOIs around candidate dates.

Catalog and Groundsource inputs are discovery leads. This tool does not promote
GFM output to independent truth: GFM and OPERA both use Sentinel-1 data.
"""
from __future__ import annotations

import csv
import json
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "outputs/atlas-study-area-register.csv"
LEADS = ROOT / "outputs/atlas-groundsource-event-coverage-audit.json"
OUTPUT = ROOT / "outputs/atlas-gfm-raster-coverage-audit.json"
API = "https://stac.eodc.eu/api/v1/search"


def post_search(body: dict) -> dict:
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={
        "Content-Type": "application/json", "Accept": "application/geo+json"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)


def search_all(body: dict) -> list[dict]:
    features: list[dict] = []
    while True:
        page = post_search(body)
        features.extend(page.get("features", []))
        next_link = next((link for link in page.get("links", []) if link.get("rel") == "next"), None)
        if not next_link or not next_link.get("body"):
            return features
        body = next_link["body"]


def aoi_polygon(box: list[float]) -> dict:
    west, south, east, north = box
    return {"type": "Polygon", "coordinates": [[[west, south], [east, south],
            [east, north], [west, north], [west, south]]]}


def inspect_item(feature: dict, box: list[float]) -> dict:
    props = feature.get("properties", {})
    asset = feature.get("assets", {}).get("ensemble_flood_extent")
    if not asset or not asset.get("href"):
        return {"id": feature.get("id"), "error": "missing ensemble_flood_extent"}
    href = asset["href"]
    with rasterio.open(href) as src:
        geom = transform_geom("EPSG:4326", src.crs, aoi_polygon(box))
        pixels, _ = mask(src, [geom], crop=True, filled=False)
        values = pixels.compressed()
        valid = int(values.size)
        total = int(pixels.size)
        unique, counts = np.unique(values, return_counts=True)
        return {
            "id": feature.get("id"), "datetime": props.get("datetime"),
            "asset": href, "asset_nodata": src.nodata, "asset_crs": str(src.crs),
            "aoi_pixels": total, "valid_pixels": valid,
            "valid_fraction": valid / total if total else 0.0,
            "class_counts": {str(int(k)): int(v) for k, v in zip(unique, counts)},
            "gfm_version": props.get("processing:version"),
            "constellation": props.get("constellation"),
            "flood_members": props.get("flood_members"),
        }


def main() -> None:
    register = list(csv.DictReader(REGISTER.open()))
    screen = json.load(LEADS.open())["acquisition_opportunity_screen"]["areas"]
    leads = {a["city"]: a for a in screen}
    out = {
        "source": "Copernicus Global Flood Monitoring STAC collection GFM",
        "endpoint": API,
        "created_utc": "2026-11-03",
        "purpose": "Raster-level availability diagnostic around a candidate event lead; not validation evidence.",
        "independence_limit": "GFM uses Sentinel-1, as does the target OPERA DSWx-S1 product; GFM output is not independent reference truth.",
        "validity_gate": "At least 0.80 unmasked pixels over the fixed AOI for each used raster; an AOI must also have at least 3 event and 3 baseline dates, with independently licensed reference labels, before enrollment.",
        "areas": [],
    }
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text())
            if previous.get("source") == out["source"] and previous.get("endpoint") == API:
                out["areas"] = previous.get("areas", [])
        except (OSError, json.JSONDecodeError):
            pass
    completed = {area["city"] for area in out["areas"]}
    for area in register:
        city = area["city"]
        if city in completed:
            print(city, "already saved; skipping", flush=True)
            continue
        box = [float(x) for x in area["aoi_bbox_wgs84"].split(",")]
        candidate = leads[city]["top_candidates"][0]
        pre = candidate.get("pre_event_30d_product_dates", [])
        events = candidate.get("product_dates_within_reported_event_interval", [])
        post = candidate.get("post_event_30d_product_dates", [])
        targets = {
            "baseline_nearest": pre[-1] if pre else None,
            "candidate_event": events[0] if events else candidate.get("reported_start_date"),
            "post_event_nearest": post[0] if post else None,
        }
        observations = []
        for period, target in targets.items():
            if not target:
                observations.append({"period": period, "target_date": None, "status": "no candidate date"})
                continue
            body = {"collections": ["GFM"], "bbox": box,
                    "datetime": f"{target}T00:00:00Z/{target}T23:59:59Z", "limit": 100}
            features = search_all(body)
            checked, errors = [], []
            for feature in features:
                try:
                    checked.append(inspect_item(feature, box))
                except Exception as exc:  # Preserve date-level failures in the audit.
                    errors.append({"id": feature.get("id"), "error": f"{type(exc).__name__}: {exc}"})
            best = max(checked, key=lambda item: item.get("valid_fraction", 0), default=None)
            observations.append({
                "period": period, "target_date": target, "gfm_item_count": len(features),
                "status": "raster sampled" if best else ("raster read failed" if errors else "no GFM item"),
                "best_coverage_item": best, "other_raster_errors": errors,
                "method": "Among same-day intersecting catalog items, report the single COG with the largest valid fraction over this AOI; never combine duplicate overpasses/tiles.",
            })
        valid_event = next((x.get("best_coverage_item") for x in observations if x["period"] == "candidate_event"), None)
        out["areas"].append({
            "region": area["region"], "city": city, "bbox_wgs84": box,
            "candidate_event_id": candidate.get("event_id"),
            "candidate_event_interval": [candidate.get("reported_start_date"), candidate.get("reported_end_date")],
            "candidate_lead_status": candidate.get("screen_status"),
            "observations": observations,
            "event_raster_meets_80_percent": bool(valid_event and valid_event["valid_fraction"] >= 0.8),
            "enrollment_status": "not eligible: one discovery event and at most one sampled date per period; independent reference labels and 3+ valid dates per period remain required",
        })
        OUTPUT.write_text(json.dumps(out, indent=2) + "\n")
        print(city, [(x["period"], x.get("target_date"), (x.get("best_coverage_item") or {}).get("valid_fraction"), x["status"]) for x in observations], flush=True)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
