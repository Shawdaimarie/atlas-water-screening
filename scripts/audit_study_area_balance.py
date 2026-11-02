"""Enforce matched QA-valid observation counts across the complete 8+8 program."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

try:
    from .analyze_opera_geotiffs import analyze, file_sha256, load_geojson, load_manifest, PRODUCT_DOI
except ImportError:  # direct CLI execution from scripts/
    from analyze_opera_geotiffs import analyze, file_sha256, load_geojson, load_manifest, PRODUCT_DOI


def _safe_input(root: Path, raw: str) -> Path:
    path = (root / raw).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Required input must be a local file under {root}: {raw}")
    return path


def expected_program() -> dict[str, str]:
    register_path = Path(__file__).resolve().parents[1] / "data" / "study_area_register.json"
    register = json.loads(register_path.read_text())
    results = register["results"]
    if len(results) != 16:
        raise ValueError("Canonical register must contain 16 candidates")
    return {row["city"].casefold(): row["region"] for row in results}


def validate_areas(areas: list[dict[str, Any]]) -> None:
    expected = expected_program()
    if len(areas) != 16:
        raise ValueError("A balanced run must include all 16 registered study areas")
    seen: dict[str, str] = {}
    for area in areas:
        city = str(area.get("city", "")).strip()
        region = str(area.get("region", "")).strip()
        key = city.casefold()
        if not key or key not in expected:
            raise ValueError(f"Area {city!r} is not in the canonical study-area register")
        if key in seen:
            raise ValueError(f"Duplicate registered study area: {city}")
        if region.casefold() != expected[key].casefold():
            raise ValueError(f"Region classification mismatch for {city}: expected {expected[key]}")
        seen[key] = region
    if set(seen) != set(expected):
        missing = sorted(set(expected) - set(seen))
        raise ValueError(f"All registered areas are required; missing: {', '.join(missing)}")
    if sum(value == "united states" for value in (v.casefold() for v in seen.values())) != 8:
        raise ValueError("Canonical design requires exactly 8 U.S. areas")
    if sum(value == "international" for value in (v.casefold() for v in seen.values())) != 8:
        raise ValueError("Canonical design requires exactly 8 international areas")


def global_balance(areas: list[dict[str, Any]], observations_by_area: dict[str, list[dict[str, Any]]],
                   *, min_dates: int = 3) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    validate_areas(areas)
    if min_dates < 1:
        raise ValueError("min_dates must be at least 1")

    area_dates: dict[str, dict[str, dict[str, Any]]] = {}
    availability: list[dict[str, Any]] = []
    for area in areas:
        key = area["city"].casefold()
        rows = observations_by_area.get(area["city"], [])
        asset_ids = {row["asset_id"] for row in rows}
        if not asset_ids:
            raise ValueError(f"No asset observations were produced for {area['city']}")
        by_period_date: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_period_date[(row["period"], row["acquired_at"])].append(row)
        dates = {"event": {}, "baseline": {}}
        for (period, acquired_at), date_rows in by_period_date.items():
            if period not in dates:
                raise ValueError(f"Invalid period {period!r} for {area['city']}")
            if {row["asset_id"] for row in date_rows} != asset_ids:
                raise ValueError(f"Incomplete per-asset QA rows for {area['city']} {acquired_at}")
            anchor_values = {row["selection_anchor"] for row in date_rows}
            if len(anchor_values) != 1:
                raise ValueError(f"Inconsistent selection anchors for {area['city']} {acquired_at}")
            if all(bool(row["candidate_observation"]) for row in date_rows):
                dates[period][acquired_at] = {
                    "selection_anchor": anchor_values.pop(),
                    "granule_id": date_rows[0]["granule_id"],
                    "asset_rows": {row["asset_id"]: row for row in date_rows},
                }
        area_dates[key] = dates
        availability.append({
            "city": area["city"],
            "region": area["region"],
            "event_qa_valid_dates": len(dates["event"]),
            "baseline_qa_valid_dates": len(dates["baseline"]),
            "assets_evaluated": len(asset_ids),
        })

    global_n = min(
        min((len(d["event"]) for d in area_dates.values()), default=0),
        min((len(d["baseline"]) for d in area_dates.values()), default=0),
    )
    status = "globally_balanced_candidate" if global_n >= min_dates else "insufficient_global_qa_valid_coverage"
    for row in availability:
        row.update({"global_status": status, "global_matched_dates_per_period": global_n if status == "globally_balanced_candidate" else 0,
                    "required_min_dates_per_period": min_dates})

    comparisons: list[dict[str, Any]] = []
    for area in areas:
        dates = area_dates[area["city"].casefold()]
        if status != "globally_balanced_candidate":
            for aid in sorted({r["asset_id"] for r in observations_by_area[area["city"]]}):
                comparisons.append({"city": area["city"], "region": area["region"], "asset_id": aid,
                                   "status": status, "matched_dates_per_period": 0,
                                   "event_mean_water_fraction": None, "baseline_mean_water_fraction": None,
                                   "water_fraction_difference": None})
            continue

        selected: dict[str, list[str]] = {}
        selected_rows: dict[str, list[dict[str, Any]]] = {}
        for period in ("event", "baseline"):
            candidates = dates[period]
            anchor = date.fromisoformat(next(iter(candidates.values()))["selection_anchor"])
            ranked = sorted(candidates.items(), key=lambda item: (
                abs((date.fromisoformat(item[0]) - anchor).days), item[0], item[1]["granule_id"]))
            selected_rows[period] = [item[1] for item in ranked[:global_n]]
            selected[period] = sorted(item[0] for item in ranked[:global_n])
        asset_ids = sorted(selected_rows["event"][0]["asset_rows"])
        for aid in asset_ids:
            event_values = [r["asset_rows"][aid]["asset_water_fraction_valid"] for r in selected_rows["event"]]
            baseline_values = [r["asset_rows"][aid]["asset_water_fraction_valid"] for r in selected_rows["baseline"]]
            event_mean = sum(event_values) / global_n
            baseline_mean = sum(baseline_values) / global_n
            comparisons.append({
                "city": area["city"], "region": area["region"], "asset_id": aid,
                "status": status, "matched_dates_per_period": global_n,
                "event_selected_dates": ";".join(selected["event"]),
                "baseline_selected_dates": ";".join(selected["baseline"]),
                "product_version": selected_rows["event"][0]["asset_rows"][aid]["product_version"],
                "processing_version": selected_rows["event"][0]["asset_rows"][aid]["processing_version"],
                "product_doi": selected_rows["event"][0]["asset_rows"][aid]["product_doi"],
                "event_source_sha256": ";".join(r["asset_rows"][aid]["source_sha256"] for r in selected_rows["event"]),
                "baseline_source_sha256": ";".join(r["asset_rows"][aid]["source_sha256"] for r in selected_rows["baseline"]),
                "analysis_code_sha256": selected_rows["event"][0]["asset_rows"][aid]["analysis_code_sha256"],
                "event_mean_water_fraction": round(event_mean, 6),
                "baseline_mean_water_fraction": round(baseline_mean, 6),
                "water_fraction_difference": round(event_mean - baseline_mean, 6),
                "selection_rule": "global_count_then_nearest_to_predeclared_area_period_anchor_then_earliest_date_then_granule_id",
                "data_mode": "local_user_supplied_opera_file_unverified",
                "interpretation_limit": "water fraction is not damage, service failure, or independent flood truth",
            })
    return availability, comparisons


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-package", type=Path, required=True,
                        help="JSON with a study_areas array for all 16 candidates")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--min-valid-fraction", type=float, default=0.8)
    parser.add_argument("--min-dates", type=int, default=3)
    args = parser.parse_args()
    root = args.study_package.resolve().parent
    package = json.loads(args.study_package.read_text())
    areas = package.get("study_areas")
    if not isinstance(areas, list):
        raise ValueError("Study package must contain a study_areas list")
    validate_areas(areas)
    run_started_at = datetime.now(timezone.utc).isoformat()
    observations_by_area = {}
    all_observations = []
    input_inventory = []
    source_inventory = []
    for area in areas:
        for key in ("manifest", "aoi", "assets"):
            if not isinstance(area.get(key), str):
                raise ValueError(f"Each area needs a local {key} path")
        manifest_path = _safe_input(root, area["manifest"])
        aoi_path = _safe_input(root, area["aoi"])
        assets_path = _safe_input(root, area["assets"])
        input_inventory.append({
            "city": area["city"], "region": area["region"],
            "manifest": {"file": area["manifest"], "sha256": file_sha256(manifest_path)},
            "aoi": {"file": area["aoi"], "sha256": file_sha256(aoi_path)},
            "assets": {"file": area["assets"], "sha256": file_sha256(assets_path)},
        })
        source_inventory.extend({"city": area["city"], "granule_id": obs.granule_id,
                                 "acquired_at": obs.acquired_at.isoformat(), "period": obs.period,
                                 "file": obs.path.name, "sha256": file_sha256(obs.path),
                                 "product_version": obs.product_version,
                                 "processing_version": obs.processing_version,
                                 "retrieved_at": obs.retrieved_at}
                                for obs in load_manifest(manifest_path))
        _, asset_rows = load_geojson(assets_path, id_key="asset_id")
        obs, _ = analyze(manifest_path, aoi_path, assets_path,
                         aoi_crs=area.get("aoi_crs", "EPSG:4326"),
                         assets_crs=area.get("assets_crs", "EPSG:4326"),
                         min_valid_fraction=args.min_valid_fraction,
                         min_dates=args.min_dates)
        observations_by_area[area["city"]] = obs
        all_observations.extend({"city": area["city"], "region": area["region"], **row} for row in obs)
    availability, comparisons = global_balance(areas, observations_by_area, min_dates=args.min_dates)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "area_coverage.csv", availability)
    write_csv(args.output_dir / "balanced_comparisons.csv", comparisons)
    write_csv(args.output_dir / "observation_qa.csv", all_observations)
    script_path = Path(__file__).resolve()
    outputs = ("area_coverage.csv", "balanced_comparisons.csv", "observation_qa.csv")
    run_manifest = {
        "schema_version": 1,
        "run_started_at": run_started_at,
        "run_completed_at": datetime.now(timezone.utc).isoformat(),
        "analysis_script_sha256": file_sha256(script_path),
        "pixel_analysis_script_sha256": file_sha256(Path(__file__).with_name("analyze_opera_geotiffs.py")),
        "study_package": {"file": args.study_package.name, "sha256": file_sha256(args.study_package)},
        "data_mode": "local_user_supplied_opera_file_unverified",
        "inputs_by_area": input_inventory,
        "source_observations": source_inventory,
        "analysis": {"product_doi": PRODUCT_DOI, "min_valid_fraction": args.min_valid_fraction,
                     "min_dates_per_period": args.min_dates,
                     "selection_rule": "one global count; nearest to predeclared area-period anchor; ties to earliest date then granule ID"},
        "global_status": availability[0]["global_status"],
        "global_matched_dates_per_period": availability[0]["global_matched_dates_per_period"],
        "outputs": {name: file_sha256(args.output_dir / name) for name in outputs},
        "independent_label_validation_performed": False,
    }
    (args.output_dir / "run_manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n")
    print(f"Areas: {len(availability)}; global status: {availability[0]['global_status']}; matched dates/period: {availability[0]['global_matched_dates_per_period']}")


if __name__ == "__main__":
    main()
