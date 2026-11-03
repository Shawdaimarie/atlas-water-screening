#!/usr/bin/env python3
"""Measure a balanced, exploratory sample of real Sentinel-1 RTC pixel coverage.

This screens data availability only. It does not classify floodwater or validate
OPERA DSWx-S1. Planetary Computer SAS URLs are held in memory and never written
to the report, cache, log, or source tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError


STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION = "sentinel-1-rtc"
WINDOW_START = "2025-01-01T00:00:00Z"
WINDOW_END = "2025-12-31T23:59:59Z"
SAMPLE_SEED = "ATLAS-S1RTC-quarterly-coverage-v1"
TARGET_RESOLUTION_M = 10.0
MIN_VALID_FRACTION = 0.80
_SAS_TOKENS: dict[tuple[str, str], str] = {}


def _request_json(url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Accept": "application/geo+json, application/json",
                 **({"Content-Type": "application/json"} if data is not None else {})},
    )
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                value = json.load(response)
            break
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 5:
                raise
            retry_after = exc.headers.get("Retry-After", "")
            try:
                delay = min(60.0, max(1.0, float(retry_after)))
            except ValueError:
                delay = min(30.0, 2.0 ** attempt)
            time.sleep(delay)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object from the public data API")
    return value


def _items_for_area(bbox: list[float]) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {
        "collections": [COLLECTION], "bbox": bbox,
        "datetime": f"{WINDOW_START}/{WINDOW_END}", "limit": 100,
    }
    items: list[dict[str, Any]] = []
    while True:
        page = _request_json(f"{STAC}/search", payload)
        items.extend(page.get("features", []))
        next_link = next((link for link in page.get("links", []) if link.get("rel") == "next"), None)
        if not next_link:
            return items
        if next_link.get("method", "GET").upper() == "POST":
            payload = next_link.get("body") or {}
            url = next_link["href"]
            page = _request_json(url, payload)
        else:
            url = next_link["href"]
            page = _request_json(url)
        items.extend(page.get("features", []))
        while True:
            next_link = next((link for link in page.get("links", []) if link.get("rel") == "next"), None)
            if not next_link:
                return items
            if next_link.get("method", "GET").upper() == "POST":
                url = next_link["href"]
                payload = next_link.get("body") or {}
                page = _request_json(url, payload)
            else:
                page = _request_json(next_link["href"])
            items.extend(page.get("features", []))


def _orbit_groups(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        props = item.get("properties") or {}
        stamp = str(props.get("datetime", ""))
        if not stamp or "vv" not in (item.get("assets") or {}):
            continue
        day = date.fromisoformat(stamp[:10])
        if not (date(2025, 1, 1) <= day <= date(2025, 12, 31)):
            continue
        orbit = props.get("sat:absolute_orbit")
        platform = props.get("platform")
        if orbit is None or not platform:
            continue
        group_id = f"{day.isoformat()}|{platform}|{props.get('sat:orbit_state','unknown')}|{orbit}"
        groups[group_id].append(item)
    return dict(groups)


def select_quarterly_groups(groups: dict[str, list[dict[str, Any]]], area_key: str,
                            sample_seed: str = SAMPLE_SEED) -> list[dict[str, Any]]:
    """Select one orbit group uniformly at random from each calendar quarter."""
    selected = []
    for quarter in range(1, 5):
        candidates = []
        for group_id, items in groups.items():
            month = int(group_id[:7].split("-")[1])
            if (month - 1) // 3 + 1 == quarter:
                candidates.append((group_id, items))
        candidates.sort(key=lambda pair: pair[0])
        if not candidates:
            selected.append({"quarter": quarter, "candidate_orbit_groups": 0, "group_id": None, "items": []})
            continue
        seed_material = f"{sample_seed}|{area_key}|Q{quarter}".encode()
        seed = int.from_bytes(hashlib.sha256(seed_material).digest()[:8], "big")
        group_id, items = random.Random(seed).choice(candidates)
        selected.append({"quarter": quarter, "candidate_orbit_groups": len(candidates),
                         "group_id": group_id, "items": sorted(items, key=lambda i: i["id"])})
    return selected


def _bbox_geometry(bbox: list[float]) -> dict[str, Any]:
    west, south, east, north = bbox
    return {"type": "Polygon", "coordinates": [[[west, south], [east, south],
            [east, north], [west, north], [west, south]]]}


def _sign_asset(href: str) -> str:
    parsed = urllib.parse.urlsplit(href)
    parts = parsed.path.strip("/").split("/", 1)
    if parsed.scheme != "https" or not parsed.netloc or len(parts) != 2:
        raise ValueError("Expected an HTTPS Azure Blob asset URL")
    key = (parsed.netloc.split(".", 1)[0], parts[0])
    token = _SAS_TOKENS.get(key)
    if token is None:
        # One anonymous, short-lived container token avoids one signer request
        # per raster and stays in process memory only.
        token_url = "https://planetarycomputer.microsoft.com/api/sas/v1/token/" + "/".join(
            urllib.parse.quote(part, safe="") for part in key
        )
        response = _request_json(token_url)
        token = response.get("token")
        if not isinstance(token, str) or not token:
            raise ValueError("Public data token service returned no access token")
        _SAS_TOKENS[key] = token
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, token, parsed.fragment))


def _pixel_fraction_for_group(items: list[dict[str, Any]], bbox: list[float]) -> tuple[float, int, int]:
    try:
        import numpy as np
        import rasterio
        from rasterio.features import geometry_mask
        from rasterio.transform import from_bounds
        from rasterio.warp import Resampling, reproject, transform_bounds, transform_geom
        from rasterio.windows import from_bounds as window_from_bounds, transform as window_transform
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Install hash-locked analysis dependencies from requirements-dev.lock in Python 3.12") from exc

    west, south, east, north = bbox
    lon, lat = (west + east) / 2, (south + north) / 2
    zone = max(1, min(60, int((lon + 180) // 6) + 1))
    target_crs = f"EPSG:{32600 + zone if lat >= 0 else 32700 + zone}"
    left, bottom, right, top = transform_bounds("EPSG:4326", target_crs, west, south, east, north, densify_pts=21)
    width = math.ceil((right - left) / TARGET_RESOLUTION_M)
    height = math.ceil((top - bottom) / TARGET_RESOLUTION_M)
    target_transform = from_bounds(left, bottom, left + width * TARGET_RESOLUTION_M,
                                   bottom + height * TARGET_RESOLUTION_M, width, height)
    target_geom = transform_geom("EPSG:4326", target_crs, _bbox_geometry(bbox), precision=-1)
    aoi_mask = geometry_mask([target_geom], out_shape=(height, width), transform=target_transform, invert=True)
    observed = np.zeros((height, width), dtype="uint8")
    for item in items:
        asset = item["assets"]["vv"]
        signed_href = _sign_asset(asset["href"])
        try:
            with rasterio.open(signed_href) as src:
                if src.crs is None or src.count != 1 or src.nodata is None:
                    raise ValueError("VV raster lacks a single-band CRS or nodata declaration")
                stac_band = (asset.get("raster:bands") or [{}])[0]
                if stac_band.get("nodata") is None or float(stac_band["nodata"]) != float(src.nodata):
                    raise ValueError("VV raster nodata does not match the pinned STAC item metadata")
                if stac_band.get("spatial_resolution") is None or float(stac_band["spatial_resolution"]) != 10.0:
                    raise ValueError("VV STAC item does not declare the expected 10 m pixel spacing")
                if not (abs(abs(src.res[0]) - 10.0) <= 0.5 and abs(abs(src.res[1]) - 10.0) <= 0.5):
                    raise ValueError("Unexpected Sentinel-1 RTC pixel spacing")
                src_bounds = transform_bounds("EPSG:4326", src.crs, west, south, east, north, densify_pts=21)
                window = window_from_bounds(*src_bounds, transform=src.transform).round_offsets().round_lengths()
                values = src.read(1, window=window, boundless=True, fill_value=src.nodata)
                valid = np.isfinite(values) & (values != src.nodata)
                projected = np.zeros((height, width), dtype="uint8")
                reproject(source=valid.astype("uint8"), destination=projected,
                          src_transform=window_transform(window, src.transform), src_crs=src.crs,
                          dst_transform=target_transform, dst_crs=target_crs,
                          src_nodata=0, dst_nodata=0, resampling=Resampling.nearest, num_threads=2)
                observed |= projected
        finally:
            signed_href = ""  # Never persist, print, or report the temporary SAS URL.
    selected = int(np.count_nonzero(aoi_mask))
    valid = int(np.count_nonzero(observed & aoi_mask))
    return valid / selected if selected else 0.0, valid, selected


def run(register_path: Path, output_path: Path,
        checkpoint_path: Path = Path("work/atlas-s1rtc-pixel-coverage-checkpoints.json"),
        sample_seed: str = SAMPLE_SEED) -> dict[str, Any]:
    register = json.loads(register_path.read_text())
    areas = register.get("results")
    if not isinstance(areas, list) or len(areas) != 16:
        raise ValueError("Expected the registered 8 U.S. and 8 international candidate areas")
    results = []
    register_sha256 = hashlib.sha256(register_path.read_bytes()).hexdigest()
    checkpoint: dict[str, Any] = {"protocol": sample_seed, "register_sha256": register_sha256, "completed": {}}
    if checkpoint_path.is_file():
        try:
            prior = json.loads(checkpoint_path.read_text())
            if prior.get("protocol") == sample_seed and prior.get("register_sha256") == register_sha256:
                checkpoint = prior
        except (OSError, json.JSONDecodeError):
            pass
    checkpoint.setdefault("completed", {})
    for area in areas:
        bbox = [float(v) for v in area["aoi_bbox_wgs84"].split(",")]
        groups = _orbit_groups(_items_for_area(bbox))
        selected = select_quarterly_groups(groups, area["city"], sample_seed)
        quarters = []
        for sample in selected:
            if not sample["items"]:
                quarters.append({"quarter": sample["quarter"], "candidate_orbit_groups": 0,
                                 "status": "no_sampled_group", "valid_fraction": None})
                continue
            cache_key = f"{area['city']}|Q{sample['quarter']}"
            item_ids = [item["id"] for item in sample["items"]]
            cached = checkpoint["completed"].get(cache_key)
            if cached and cached.get("group_id") == sample["group_id"] and cached.get("item_ids") == item_ids:
                quarter_result = cached["result"]
                quarter_result.setdefault("asset_band", "VV")
                quarter_result.setdefault("stac_nodata", sample["items"][0]["assets"]["vv"].get("raster:bands", [{}])[0].get("nodata"))
                quarter_result.setdefault("stac_spatial_resolution_m", sample["items"][0]["assets"]["vv"].get("raster:bands", [{}])[0].get("spatial_resolution"))
            else:
                print(f"[{area['city']} Q{sample['quarter']}] reading {len(item_ids)} orbit granule(s)", flush=True)
                fraction, valid, footprint = _pixel_fraction_for_group(sample["items"], bbox)
                quarter_result = {
                "quarter": sample["quarter"], "date": sample["group_id"].split("|", 1)[0],
                "platform": sample["items"][0]["properties"].get("platform"),
                "orbit_state": sample["items"][0]["properties"].get("sat:orbit_state"),
                "relative_orbit": sample["items"][0]["properties"].get("sat:relative_orbit"),
                "absolute_orbit": sample["items"][0]["properties"].get("sat:absolute_orbit"),
                "candidate_orbit_groups": sample["candidate_orbit_groups"],
                "asset_band": "VV",
                "stac_nodata": sample["items"][0]["assets"]["vv"].get("raster:bands", [{}])[0].get("nodata"),
                "stac_spatial_resolution_m": sample["items"][0]["assets"]["vv"].get("raster:bands", [{}])[0].get("spatial_resolution"),
                "items": [{"id": item["id"], "item_url": next((link["href"] for link in item.get("links", [])
                           if link.get("rel") == "self"), None),
                           "asset_checksum": item["assets"]["vv"].get("file:checksum"),
                           "asset_bytes": item["assets"]["vv"].get("file:size")} for item in sample["items"]],
                "valid_pixels": valid, "aoi_pixels": footprint,
                "valid_fraction": round(fraction, 6),
                "meets_80pct_pixel_coverage_screen": fraction >= MIN_VALID_FRACTION,
                "validity_definition": "Finite VV backscatter pixels not equal to declared nodata; this is spatial data coverage only.",
                }
                checkpoint["completed"][cache_key] = {"group_id": sample["group_id"], "item_ids": item_ids,
                                                       "result": quarter_result}
                checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                checkpoint_tmp = checkpoint_path.with_suffix(checkpoint_path.suffix + ".tmp")
                checkpoint_tmp.write_text(json.dumps(checkpoint, indent=2) + "\n")
                checkpoint_tmp.replace(checkpoint_path)
            quarters.append(quarter_result)
        fractions = [q["valid_fraction"] for q in quarters if q["valid_fraction"] is not None]
        results.append({
            "region": area["region"], "city": area["city"], "bbox_wgs84": area["aoi_bbox_wgs84"],
            "sample_rule": "One uniformly random eligible orbit group per 2025 calendar quarter, seeded by the recorded protocol string and city; same four-quarter rule for all areas.",
            "sampled_quarters": len(fractions), "sampled_quarter_pixel_passes": sum(x >= MIN_VALID_FRACTION for x in fractions),
            "all_four_quarters_meet_pixel_screen": len(fractions) == 4 and all(x >= MIN_VALID_FRACTION for x in fractions),
            "quarter_results": quarters,
        })
    summary = {
        "audit": "ATLAS exploratory Sentinel-1 RTC sampled pixel coverage",
        "retrieved_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "source": {"stac_api": STAC, "collection": COLLECTION, "collection_url": f"{STAC}/collections/{COLLECTION}",
                   "license": "CC-BY-4.0", "attribution": "Microsoft Planetary Computer; ESA/Copernicus Sentinel-1"},
        "period": {"start": WINDOW_START, "end": WINDOW_END},
        "pixel_coverage_screen": {"band": "VV", "nominal_spacing_m": 10,
                                  "rule": "finite pixels unequal to declared raster nodata; ≥80% in fixed AOI",
                                  "sample_seed": sample_seed, "samples_per_area": 4},
        "summary": {"areas": len(results),
                    "us_areas": sum(a["region"] == "United States" for a in results),
                    "international_areas": sum(a["region"] == "International" for a in results),
                    "areas_with_all_four_sample_quarters_above_80pct": sum(a["all_four_quarters_meet_pixel_screen"] for a in results),
                    "quarterly_samples_above_80pct": sum(a["sampled_quarter_pixel_passes"] for a in results)},
        "interpretation_limits": [
            "This is a four-date-per-area spatial data-availability sample, not event/baseline sampling adequacy.",
            "Sentinel-1 RTC VV backscatter is not a water classification and does not validate OPERA DSWx-S1.",
            "Nodata coverage alone does not assess speckle, layover/shadow, radiometric quality, acquisition geometry balance, or classification accuracy.",
            "A 2025 sample does not establish coverage for every event, date, asset, or the full 2024–2026 study window.",
            "Independent event labels and confirmatory study-area enrollment remain unmet.",
            "Planetary Computer SAS links are temporary and intentionally excluded from this output.",
        ],
        "areas": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=Path("data/study_area_register.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/atlas-s1rtc-pixel-coverage-audit.json"))
    parser.add_argument("--checkpoint", type=Path, default=Path("work/atlas-s1rtc-pixel-coverage-checkpoints.json"))
    parser.add_argument("--seed", default=SAMPLE_SEED,
                        help="Fixed protocol seed; change it only for a separately reported replicate")
    args = parser.parse_args()
    summary = run(args.register, args.output, args.checkpoint, args.seed)
    print(json.dumps(summary["summary"], indent=2))
    print(f"Saved redacted audit: {args.output}")


if __name__ == "__main__":
    main()
