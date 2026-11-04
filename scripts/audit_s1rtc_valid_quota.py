#!/usr/bin/env python3
"""Screen remaining same-quarter Sentinel-1 RTC groups for a matched quota.

This supplemental availability audit retains previously selected groups that
pass the predeclared valid-pixel floor, then examines a deterministic random
ordering of unselected groups until each area-quarter has three passing groups
or its candidate pool is exhausted. It does not assess water classes or truth.
"""
from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts import audit_s1rtc_pixel_coverage as source


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/study_area_register.json"
INPUT = ROOT / "outputs/atlas-s1rtc-pixel-coverage-unique-audit.json"
OUTPUT = ROOT / "outputs/atlas-s1rtc-valid-quota-audit.json"
CHECKPOINT = ROOT / "work/atlas-s1rtc-valid-quota-checkpoints.json"
PROTOCOL = "ATLAS-S1RTC-valid-quota-v1"
TARGET_PER_QUARTER = 3


def _quarter(group_id: str) -> int:
    month = int(group_id[5:7])
    return (month - 1) // 3 + 1


def _cache_key(city: str, quarter: int, group_id: str) -> str:
    return f"{city}|Q{quarter}|{group_id}"


def _sample_result(items: list[dict[str, Any]], group_id: str, bbox: list[float],
                   quarter: int, slot: int, candidate_count: int,
                   origin: str, fraction: float, valid: int, footprint: int) -> dict[str, Any]:
    first = items[0]
    asset = first["assets"]["vv"]
    return {
        "quarter": quarter,
        "date": group_id.split("|", 1)[0],
        "platform": first["properties"].get("platform"),
        "orbit_state": first["properties"].get("sat:orbit_state"),
        "relative_orbit": first["properties"].get("sat:relative_orbit"),
        "absolute_orbit": first["properties"].get("sat:absolute_orbit"),
        "candidate_orbit_groups": candidate_count,
        "items": [
            {"id": item["id"],
             "item_url": next((link["href"] for link in item.get("links", [])
                               if link.get("rel") == "self"), None),
             "asset_checksum": item["assets"]["vv"].get("file:checksum"),
             "asset_bytes": item["assets"]["vv"].get("file:size")}
            for item in items
        ],
        "asset_band": "VV",
        "stac_nodata": (asset.get("raster:bands") or [{}])[0].get("nodata"),
        "stac_spatial_resolution_m": (asset.get("raster:bands") or [{}])[0].get("spatial_resolution"),
        "valid_pixels": valid,
        "aoi_pixels": footprint,
        "valid_fraction": round(fraction, 6),
        "meets_80pct_pixel_coverage_screen": fraction >= source.MIN_VALID_FRACTION,
        "validity_definition": "Finite VV backscatter pixels not equal to declared nodata; spatial availability only.",
        "sample_slot": slot,
        "selection_origin": origin,
    }


def run(register_path: Path = REGISTER, input_path: Path = INPUT,
        output_path: Path = OUTPUT, checkpoint_path: Path = CHECKPOINT) -> dict[str, Any]:
    register = json.loads(register_path.read_text())
    initial = json.loads(input_path.read_text())
    areas = register.get("results")
    if not isinstance(areas, list) or len(areas) != 16:
        raise ValueError("Expected exactly the registered 8 U.S. and 8 international candidate areas")
    if len(initial.get("areas", [])) != 16:
        raise ValueError("Initial unique-group audit must cover all 16 registered candidate areas")
    initial_by_city = {row["city"]: row for row in initial["areas"]}
    if set(initial_by_city) != {area["city"] for area in areas}:
        raise ValueError("Register and initial audit city sets differ")

    register_hash = hashlib.sha256(register_path.read_bytes()).hexdigest()
    input_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()
    checkpoint: dict[str, Any] = {"protocol": PROTOCOL, "register_sha256": register_hash,
                                  "input_sha256": input_hash, "completed": {}}
    if checkpoint_path.is_file():
        try:
            prior = json.loads(checkpoint_path.read_text())
            if (prior.get("protocol") == PROTOCOL and prior.get("register_sha256") == register_hash
                    and prior.get("input_sha256") == input_hash):
                checkpoint = prior
        except (OSError, json.JSONDecodeError):
            pass

    result_areas = []
    total_attempts = total_passes = 0
    for area in areas:
        city, region = area["city"], area["region"]
        bbox = [float(value) for value in area["aoi_bbox_wgs84"].split(",")]
        groups = source._orbit_groups(source._items_for_area(bbox))
        quarter_rows = []
        for quarter in range(1, 5):
            eligible = {group: items for group, items in groups.items() if _quarter(group) == quarter}
            original = next(row for row in initial_by_city[city]["quarter_results"]
                            if row["quarter"] == quarter)
            selected: list[dict[str, Any]] = []
            seen: set[str] = set()
            for sample in original["samples"]:
                group_id = (f"{sample['date']}|{sample['platform']}|{sample['orbit_state']}|"
                            f"{sample['absolute_orbit']}")
                if group_id not in eligible or group_id in seen:
                    raise ValueError(f"Initial group {group_id} missing or duplicated in current {city} STAC catalog")
                seen.add(group_id)
                if (sample.get("valid_fraction") is not None
                        and sample["valid_fraction"] >= source.MIN_VALID_FRACTION):
                    kept = dict(sample)
                    kept.update({"sample_slot": len(selected) + 1,
                                 "selection_origin": "retained_initial_pass"})
                    selected.append(kept)

            material = f"{PROTOCOL}|{register_hash}|{input_hash}|{city}|Q{quarter}".encode()
            seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
            remaining = sorted(set(eligible) - seen)
            random.Random(seed).shuffle(remaining)
            attempts = []
            candidate_count = len(eligible)
            for group_id in remaining:
                if len(selected) >= TARGET_PER_QUARTER:
                    break
                items = eligible[group_id]
                item_ids = [item["id"] for item in items]
                key = _cache_key(city, quarter, group_id)
                cached = checkpoint["completed"].get(key)
                if cached and cached.get("item_ids") == item_ids:
                    sample = dict(cached["result"])
                else:
                    print(f"[{city} Q{quarter}] screening candidate {group_id}", flush=True)
                    fraction, valid, footprint = source._pixel_fraction_for_group(items, bbox)
                    sample = _sample_result(items, group_id, bbox, quarter, len(selected) + 1,
                                            candidate_count, "supplemental_candidate", fraction,
                                            valid, footprint)
                    checkpoint["completed"][key] = {"item_ids": item_ids, "result": sample}
                    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                    temporary = checkpoint_path.with_suffix(checkpoint_path.suffix + ".tmp")
                    temporary.write_text(json.dumps(checkpoint, indent=2) + "\n")
                    temporary.replace(checkpoint_path)
                total_attempts += 1
                passes = sample["valid_fraction"] is not None and sample["valid_fraction"] >= source.MIN_VALID_FRACTION
                attempts.append({"group_id": group_id,
                                 "item_ids": item_ids,
                                 "valid_fraction": sample["valid_fraction"],
                                 "passes_floor": passes})
                if passes:
                    sample.update({"sample_slot": len(selected) + 1,
                                   "selection_origin": "supplemental_candidate"})
                    selected.append(sample)
                    seen.add(group_id)
                if len(selected) == TARGET_PER_QUARTER:
                    break
            passed = len(selected)
            total_passes += passed
            quarter_rows.append({
                "quarter": quarter,
                "candidate_orbit_groups": candidate_count,
                "initial_passes_retained": sum(s.get("selection_origin") == "retained_initial_pass" for s in selected),
                "supplemental_groups_screened": len(attempts),
                "selected_valid_groups": passed,
                "quota": TARGET_PER_QUARTER,
                "quota_met": passed == TARGET_PER_QUARTER,
                "selection_rule": "retain initial passing groups; deterministically shuffle remaining groups without replacement and screen until quota is met or pool exhausted",
                "supplemental_attempts": attempts,
                "samples": selected,
            })
        area_pass = sum(q["selected_valid_groups"] for q in quarter_rows)
        result_areas.append({"region": region, "city": city,
                             "candidate_groups": sum(q["candidate_orbit_groups"] for q in quarter_rows),
                             "supplemental_groups_screened": sum(q["supplemental_groups_screened"] for q in quarter_rows),
                             "selected_valid_groups": area_pass,
                             "quota": TARGET_PER_QUARTER * 4,
                             "all_quarter_quotas_met": all(q["quota_met"] for q in quarter_rows),
                             "quarter_results": quarter_rows})

    completed = sum(row["all_quarter_quotas_met"] for row in result_areas)
    report = {
        "audit": "ATLAS Sentinel-1 RTC matched valid-pixel quota availability screen",
        "protocol": PROTOCOL,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Microsoft Planetary Computer Sentinel-1 RTC STAC catalog",
        "register_sha256": register_hash,
        "initial_audit_sha256": input_hash,
        "period": "2025-01-01/2025-12-31",
        "measurement": "fraction of fixed-AOI 10 m grid with finite VV pixels not equal to STAC-declared nodata",
        "valid_pixel_floor": source.MIN_VALID_FRACTION,
        "quota": {"per_area": 12, "per_quarter": 3, "quarters": 4},
        "selection_design": "Initial passing groups are retained; deterministic random ordering without replacement screens additional candidates until three passing groups per area-quarter are found or exhausted. Rejected original selections are excluded from replacement candidates.",
        "summary": {"areas": 16, "us_areas": 8, "international_areas": 8,
                    "areas_meeting_12_group_quota": completed,
                    "valid_groups_selected": total_passes,
                    "target_valid_groups": 192,
                    "supplemental_groups_screened": total_attempts},
        "areas": result_areas,
        "interpretation_limits": [
            "This is only a Sentinel-1 RTC spatial availability screen; it does not measure water classification or flood accuracy.",
            "The deterministic acceptance rule is conditional on the 80% pixel-coverage floor and does not provide a regional population estimate.",
            "It does not establish OPERA BWTR availability, event-baseline matching, independent labels, licensing, or confirmatory study enrollment.",
            "The 12 groups are temporal availability samples, not 12 independent sites or independent validation observations.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], indent=2))
    return report


if __name__ == "__main__":
    run()
