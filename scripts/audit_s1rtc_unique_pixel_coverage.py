#!/usr/bin/env python3
"""Replace duplicate quarterly RTC samples so each AOI has 12 unique groups.

The three existing draws were independently and uniformly selected with
replacement. Duplicate slots are filled by a deterministic uniform draw from
the remaining eligible orbit groups. Selection is stratified by AOI and quarter.
This measures spatial data availability only, not water classification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts import audit_s1rtc_pixel_coverage as source


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/study_area_register.json"
INPUTS = [
    ROOT / "outputs/atlas-s1rtc-pixel-coverage-audit.json",
    ROOT / "outputs/atlas-s1rtc-pixel-coverage-replicate-2.json",
    ROOT / "outputs/atlas-s1rtc-pixel-coverage-replicate-3.json",
]
OUTPUT = ROOT / "outputs/atlas-s1rtc-pixel-coverage-unique-audit.json"
CHECKPOINT = ROOT / "work/atlas-s1rtc-unique-checkpoints.json"
SEED = "ATLAS-S1RTC-quarterly-unique-v1"
TARGET_PER_QUARTER = 3


def group_id_from_record(record: dict[str, Any]) -> str:
    fields = ("date", "platform", "orbit_state", "absolute_orbit")
    if any(record.get(field) is None for field in fields):
        return ""
    return "|".join(str(record[field]) for field in fields)


def select_unique_quarter(
    candidates: dict[str, list[dict[str, Any]]],
    previous: list[dict[str, Any]],
    area: str,
    quarter: int,
    seed: str = SEED,
    target: int = TARGET_PER_QUARTER,
) -> list[dict[str, Any]]:
    """Retain unique prior draws and deterministically fill duplicate slots."""
    eligible = sorted(
        (group, items) for group, items in candidates.items()
        if int(group[5:7]) in range((quarter - 1) * 3 + 1, quarter * 3 + 1)
    )
    candidate_map = dict(eligible)
    retained: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, record in enumerate(previous, start=1):
        group = group_id_from_record(record)
        if group and group in candidate_map and group not in seen:
            retained.append({
                "group_id": group,
                "items": candidate_map[group],
                "origin": f"prior_draw_{index}",
                "prior_record": record,
            })
            seen.add(group)
        else:
            retained.append({"group_id": None, "items": [], "origin": "duplicate_replacement"})
    while len(retained) < target:
        retained.append({"group_id": None, "items": [], "origin": "duplicate_replacement"})
    if len(retained) > target:
        raise ValueError(f"Expected no more than {target} prior draws for {area} Q{quarter}")

    missing = sum(not slot["group_id"] for slot in retained)
    available = [group for group in candidate_map if group not in seen]
    if len(available) < missing:
        raise ValueError(
            f"{area} Q{quarter} has {len(candidate_map)} eligible groups; "
            f"cannot produce {target} unique samples"
        )
    material = f"{seed}|{area}|Q{quarter}".encode()
    random_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    replacements = iter(random.Random(random_seed).sample(available, missing))
    for slot in retained:
        if not slot["group_id"]:
            group = next(replacements)
            slot["group_id"] = group
            slot["items"] = candidate_map[group]
    if len({slot["group_id"] for slot in retained}) != target:
        raise ValueError(f"Duplicate remained after selection for {area} Q{quarter}")
    return retained


def _result_from_prior(record: dict[str, Any], candidate_count: int, slot: int, origin: str) -> dict[str, Any]:
    result = dict(record)
    result.update({
        "candidate_orbit_groups": candidate_count,
        "sample_slot": slot,
        "selection_origin": origin,
    })
    return result


def run(
    register_path: Path = REGISTER,
    input_paths: list[Path] | None = None,
    output_path: Path = OUTPUT,
    checkpoint_path: Path = CHECKPOINT,
) -> dict[str, Any]:
    inputs = input_paths or INPUTS
    if len(inputs) != 3:
        raise ValueError("Exactly three separately seeded source audits are required")
    reports = [json.loads(path.read_text()) for path in inputs]
    register = json.loads(register_path.read_text())
    areas = register.get("results")
    if not isinstance(areas, list) or len(areas) != 16:
        raise ValueError("Expected the registered 8 U.S. and 8 international areas")
    report_maps = [{area["city"]: area for area in report.get("areas", [])} for report in reports]
    if any(set(mapping) != {area["city"] for area in areas} for mapping in report_maps):
        raise ValueError("The three source audits must cover the same 16 registered cities")

    checkpoint: dict[str, Any] = {
        "protocol": SEED,
        "register_sha256": hashlib.sha256(register_path.read_bytes()).hexdigest(),
        "completed": {},
    }
    if checkpoint_path.is_file():
        try:
            prior = json.loads(checkpoint_path.read_text())
            if prior.get("protocol") == SEED and prior.get("register_sha256") == checkpoint["register_sha256"]:
                checkpoint = prior
        except (OSError, json.JSONDecodeError):
            pass

    rows = []
    origins: Counter[str] = Counter()
    for area in areas:
        city, region = area["city"], area["region"]
        bbox = [float(value) for value in area["aoi_bbox_wgs84"].split(",")]
        candidate_groups = source._orbit_groups(source._items_for_area(bbox))
        quarter_rows = []
        for quarter in range(1, 5):
            previous = [
                next(q for q in report_map[city]["quarter_results"] if q["quarter"] == quarter)
                for report_map in report_maps
            ]
            slots = select_unique_quarter(candidate_groups, previous, city, quarter)
            sample_results = []
            for slot_index, selected in enumerate(slots, start=1):
                group = selected["group_id"]
                prior_record = selected.get("prior_record")
                if prior_record is not None:
                    result = _result_from_prior(
                        prior_record, len(candidate_groups_for_quarter(candidate_groups, quarter)),
                        slot_index, selected["origin"],
                    )
                    origins["retained_prior"] += 1
                else:
                    cache_key = f"{city}|Q{quarter}|{group}"
                    cached = checkpoint["completed"].get(cache_key)
                    items = selected["items"]
                    item_ids = [item["id"] for item in items]
                    if cached and cached.get("item_ids") == item_ids:
                        result = cached["result"]
                    else:
                        origins["replacement_raster_reads"] += 1
                        print(f"[{city} Q{quarter} slot {slot_index}] reading replacement group {group}", flush=True)
                        fraction, valid, footprint = source._pixel_fraction_for_group(items, bbox)
                        first = items[0]
                        result = {
                            "quarter": quarter,
                            "date": group.split("|", 1)[0],
                            "platform": first["properties"].get("platform"),
                            "orbit_state": first["properties"].get("sat:orbit_state"),
                            "relative_orbit": first["properties"].get("sat:relative_orbit"),
                            "absolute_orbit": first["properties"].get("sat:absolute_orbit"),
                            "candidate_orbit_groups": len(candidate_groups_for_quarter(candidate_groups, quarter)),
                            "items": [
                                {"id": item["id"], "item_url": next((link["href"] for link in item.get("links", [])
                                    if link.get("rel") == "self"), None),
                                 "asset_checksum": item["assets"]["vv"].get("file:checksum"),
                                 "asset_bytes": item["assets"]["vv"].get("file:size")}
                                for item in items
                            ],
                            "asset_band": "VV",
                            "stac_nodata": items[0]["assets"]["vv"].get("raster:bands", [{}])[0].get("nodata"),
                            "stac_spatial_resolution_m": items[0]["assets"]["vv"].get("raster:bands", [{}])[0].get("spatial_resolution"),
                            "valid_pixels": valid,
                            "aoi_pixels": footprint,
                            "valid_fraction": round(fraction, 6),
                            "meets_80pct_pixel_coverage_screen": fraction >= source.MIN_VALID_FRACTION,
                            "validity_definition": "Finite VV backscatter pixels not equal to declared nodata; spatial data coverage only.",
                            "sample_slot": slot_index,
                            "selection_origin": "duplicate_replacement",
                        }
                        checkpoint["completed"][cache_key] = {"item_ids": item_ids, "result": result}
                        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                        temporary = checkpoint_path.with_suffix(checkpoint_path.suffix + ".tmp")
                        temporary.write_text(json.dumps(checkpoint, indent=2) + "\n")
                        temporary.replace(checkpoint_path)
                    result = dict(result)
                    result.update({"sample_slot": slot_index, "selection_origin": "duplicate_replacement"})
                    origins["replacement_unique_groups"] += 1
                sample_results.append(result)
            passes = sum(sample["valid_fraction"] is not None and sample["valid_fraction"] >= source.MIN_VALID_FRACTION
                         for sample in sample_results)
            quarter_rows.append({"quarter": quarter, "samples": sample_results,
                                 "candidate_orbit_groups": len(candidate_groups_for_quarter(candidate_groups, quarter)),
                                 "samples_passing_80pct": passes})
        flat = [sample for quarter in quarter_rows for sample in quarter["samples"]]
        rows.append({"region": region, "city": city, "bbox_wgs84": area["aoi_bbox_wgs84"],
                     "sample_rule": "Three unique orbit groups per 2025 calendar quarter, selected under the fixed stratified random rule; duplicates in the prior three independent draws were replaced uniformly from remaining eligible groups.",
                     "sampled_group_count": len(flat),
                     "sampled_groups_passing_80pct": sum(s["valid_fraction"] is not None and s["valid_fraction"] >= source.MIN_VALID_FRACTION for s in flat),
                     "all_12_sampled_groups_meet_pixel_screen": len(flat) == 12 and all(s["valid_fraction"] is not None and s["valid_fraction"] >= source.MIN_VALID_FRACTION for s in flat),
                     "quarter_results": quarter_rows})

    groups = [(row["city"], sample["date"], sample["platform"], sample["orbit_state"], sample["absolute_orbit"])
              for row in rows for quarter in row["quarter_results"] for sample in quarter["samples"]]
    if len(groups) != 192 or len(set(groups)) != 192:
        raise ValueError("The all-area sample must contain 192 unique area/orbit groups")
    if sum(row["region"] == "United States" for row in rows) != 8 or sum(row["region"] == "International" for row in rows) != 8:
        raise ValueError("The output must retain the balanced 8+8 study-area design")

    summary = {
        "areas": len(rows),
        "us_areas": sum(row["region"] == "United States" for row in rows),
        "international_areas": sum(row["region"] == "International" for row in rows),
        "samples_per_area": 12,
        "samples_per_quarter": 3,
        "selected_area_orbit_groups": len(groups),
        "unique_area_orbit_groups": len(set(groups)),
        "duplicate_selections": len(groups) - len(set(groups)),
        "samples_passing_80pct": sum(row["sampled_groups_passing_80pct"] for row in rows),
        "areas_passing_all_12_samples": sum(row["all_12_sampled_groups_meet_pixel_screen"] for row in rows),
        **origins,
    }
    output = {
        "audit": "ATLAS unique quarterly Sentinel-1 RTC VV spatial-availability sample",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": reports[0]["source"],
        "period": reports[0]["period"],
        "register_sha256": hashlib.sha256(register_path.read_bytes()).hexdigest(),
        "input_audits": [
            {"path": (str(path.relative_to(ROOT)) if path.resolve().is_relative_to(ROOT) else path.name),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
             "seed": report.get("pixel_coverage_screen", {}).get("sample_seed")}
            for path, report in zip(inputs, reports)
        ],
        "measurement": {"band": "VV", "nominal_spacing_m": 10,
                        "validity_definition": "Finite source pixels unequal to declared nodata; spatial availability only.",
                        "minimum_valid_fraction": source.MIN_VALID_FRACTION},
        "sampling": {"seed": SEED, "strata": "fixed AOI × 2025 calendar quarter",
                     "unit": "platform × acquisition date × orbit state × absolute orbit; tiled items for one group are mosaicked",
                     "selection": "Retain each unique group from three independent uniform-with-replacement draws. For duplicate or unavailable slots, deterministically sample uniformly without replacement from remaining eligible groups. This produces three unique groups per quarter.",
                     "repeated_groups_across_different_AOIs_allowed": True},
        "summary": summary,
        "areas": rows,
        "interpretation_limits": [
            "This is a uniform quarterly sample of archive spatial availability, not event/baseline sampling adequacy.",
            "Sentinel-1 RTC VV backscatter is not a water classification and does not validate OPERA DSWx-S1.",
            "Nodata coverage alone does not assess speckle, layover/shadow, radiometric quality, acquisition-geometry balance, or classification accuracy.",
            "A 2025 sample does not establish coverage for every event, date, asset, or the full 2024–2026 study window.",
            "Independent event labels and confirmatory study-area enrollment remain unmet.",
            "Planetary Computer SAS links are temporary and never included in outputs or checkpoints.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    return output


def candidate_groups_for_quarter(groups: dict[str, list[dict[str, Any]]], quarter: int) -> dict[str, list[dict[str, Any]]]:
    low, high = (quarter - 1) * 3 + 1, quarter * 3
    return {group: items for group, items in groups.items() if low <= int(group[5:7]) <= high}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=REGISTER)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--inputs", type=Path, nargs=3, default=INPUTS)
    args = parser.parse_args()
    result = run(args.register, args.inputs, args.output, args.checkpoint)
    print(json.dumps(result["summary"], indent=2))
    print(f"Saved unique, redacted audit: {args.output}")


if __name__ == "__main__":
    main()
