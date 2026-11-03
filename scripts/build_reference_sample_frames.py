"""Draw reproducible, stratified reference-label samples from QA-valid OPERA maps.

This creates a probability sample of map pixels for independent interpretation; it
does not create reference labels or establish that a site is confirmatorily ready.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom

try:
    from .audit_study_area_balance import expected_program, validate_areas
except ImportError:  # direct CLI execution from scripts/
    from audit_study_area_balance import expected_program, validate_areas


def _safe_input(root: Path, raw: str) -> Path:
    path = (root / raw).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Required raster must be a local file under {root}: {raw}")
    return path


def _allocate(populations: dict[int, int], target: int) -> dict[int, int]:
    """Proportional stratified allocation with a one-unit minimum per nonempty class."""
    total = sum(populations.values())
    n = min(target, total)
    active = [key for key, size in populations.items() if size]
    allocation = {key: 0 for key in populations}
    if not active:
        return allocation
    if n < len(active):
        # Rare classes cannot all be represented; deterministic allocation is
        # disclosed and the frame remains a valid unequal-probability design.
        for key in sorted(active, key=lambda k: (-populations[k], k))[:n]:
            allocation[key] = 1
        return allocation
    for key in active:
        allocation[key] = 1
    remaining = n - len(active)
    while remaining:
        capacity = {k: populations[k] - allocation[k] for k in active}
        capacity_total = sum(capacity.values())
        if capacity_total <= 0:
            break
        quotas = {k: remaining * capacity[k] / capacity_total for k in active}
        floors = {k: min(capacity[k], math.floor(quotas[k])) for k in active}
        added = sum(floors.values())
        for key, value in floors.items():
            allocation[key] += value
        remaining -= added
        if remaining:
            ranked = sorted(active, key=lambda k: (-(quotas[k] - floors[k]), k))
            for key in ranked:
                if remaining == 0:
                    break
                if allocation[key] < populations[key]:
                    allocation[key] += 1
                    remaining -= 1
            if not added and not ranked:
                break
    return allocation


def _aoi_geometries(path: Path, source_crs: str, target_crs: str) -> list[dict[str, Any]]:
    document = json.loads(path.read_text())
    if document.get("type") == "FeatureCollection":
        features = document.get("features", [])
    elif document.get("type") == "Feature":
        features = [document]
    else:
        features = [{"geometry": document}]
    geometries = [feature.get("geometry") for feature in features if feature.get("geometry")]
    if not geometries:
        raise ValueError(f"AOI file has no geometries: {path}")
    return [transform_geom(source_crs, target_crs, geom, precision=-1) for geom in geometries]


def draw_frame(raster_path: Path, aoi_path: Path, *, aoi_crs: str, city: str, region: str, period: str,
               target_n: int, seed: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if period not in {"event", "baseline"}:
        raise ValueError("period must be event or baseline")
    if target_n < 2:
        raise ValueError("target_n must be at least 2 so both map classes can be represented when present")
    with rasterio.open(raster_path) as src:
        if src.count != 1:
            raise ValueError(f"{city}/{period}: expected a single-band BWTR raster")
        if src.crs is None or not src.crs.is_projected:
            raise ValueError(f"{city}/{period}: raster CRS must be projected")
        if not np.isclose(abs(src.transform.a), 30.0) or not np.isclose(abs(src.transform.e), 30.0):
            raise ValueError(f"{city}/{period}: expected 30 m pixel spacing")
        values = src.read(1)
        valid = src.read_masks(1) > 0
        valid &= np.isin(values, (0, 1))
        in_aoi = geometry_mask(_aoi_geometries(aoi_path, aoi_crs, src.crs.to_string()),
                              out_shape=values.shape, transform=src.transform, invert=True)
        if np.any(valid & ~in_aoi):
            raise ValueError(f"{city}/{period}: valid sampling pixels extend outside the fixed AOI")
        valid &= in_aoi
        rows, cols = np.where(valid)
        classes = values[rows, cols].astype(int)
        populations = {0: int(np.count_nonzero(classes == 0)), 1: int(np.count_nonzero(classes == 1))}
        allocation = _allocate(populations, target_n)
        stable_seed = int.from_bytes(hashlib.sha256(f"{seed}|{city}|{period}".encode()).digest()[:8], "big")
        rng = np.random.default_rng(stable_seed)
        picked: list[tuple[int, int, int, int, float, float]] = []
        for stratum in (0, 1):
            positions = np.flatnonzero(classes == stratum)
            n_h = allocation[stratum]
            if n_h == 0:
                continue
            chosen = rng.choice(positions, size=n_h, replace=False)
            for position in chosen:
                row, col = int(rows[position]), int(cols[position])
                x, y = rasterio.transform.xy(src.transform, row, col, offset="center")
                picked.append((stratum, row, col, populations[stratum], float(x), float(y)))
        picked.sort(key=lambda item: (item[0], item[1], item[2]))
        digest = hashlib.sha256()
        with raster_path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        file_hash = digest.hexdigest()
        records = []
        for index, (stratum, row, col, population, x, y) in enumerate(picked, start=1):
            n_h = allocation[stratum]
            pixel_id = f"{city.casefold().replace(' ', '_')}:{period}:{row}:{col}"
            records.append({
                "sample_id": f"{city.casefold().replace(' ', '_')}:{period}:{index:04d}",
                "city": city, "region": region, "period": period,
                "map_stratum": "mapped_water" if stratum == 1 else "mapped_nonwater",
                "pixel_row": row, "pixel_col": col, "pixel_id": pixel_id,
                "x": x, "y": y, "crs": src.crs.to_string(),
                "stratum_population": population, "stratum_sample_n": n_h,
                "inclusion_probability": n_h / population,
                "design_weight": population / n_h,
                "reference_labeler_1": "", "reference_labeler_2": "",
                "adjudicated_label": "", "reference_source_id": "",
                "reference_acquired_at": "", "reference_license": "",
                "label_status": "pending_independent_interpretation",
            })
        summary = {
            "city": city, "region": region, "period": period,
            "raster_sha256": file_hash, "crs": src.crs.to_string(),
            "aoi_sha256": _sha256(aoi_path), "aoi_crs": aoi_crs,
            "pixel_size_m": [abs(src.transform.a), abs(src.transform.e)],
            "valid_population": sum(populations.values()),
            "strata_population": {"mapped_nonwater": populations[0], "mapped_water": populations[1]},
            "strata_sample_n": {"mapped_nonwater": allocation[0], "mapped_water": allocation[1]},
            "sample_n": len(records), "requested_base_n": target_n,
            "sampling_design": "stratified_simple_random_without_replacement_by_map_class",
            "seed": stable_seed,
            "limitation": "Nominal design only; adjust for spatial design effect after the preregistered pilot. No independent labels are created by this frame.",
        }
    return records, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-package", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target-n", type=int, default=385)
    parser.add_argument("--seed", type=int, default=20261103)
    args = parser.parse_args()
    package_path = args.study_package.resolve()
    package = json.loads(package_path.read_text())
    areas = package.get("study_areas")
    if not isinstance(areas, list):
        raise ValueError("Study package must contain a study_areas list")
    validate_areas(areas)
    expected = expected_program()
    frames, summaries = [], []
    root = package_path.parent
    for area in areas:
        city = area["city"]
        for period in ("event", "baseline"):
            path_key = f"{period}_sampling_raster"
            if not isinstance(area.get(path_key), str):
                raise ValueError(f"{city}: add {path_key} to the study package")
            raster_path = _safe_input(root, area[path_key])
            if not isinstance(area.get("aoi"), str):
                raise ValueError(f"{city}: add a fixed aoi path to the study package")
            aoi_path = _safe_input(root, area["aoi"])
            rows, summary = draw_frame(raster_path, aoi_path, aoi_crs=area.get("aoi_crs", "EPSG:4326"),
                                       city=city, region=area["region"], period=period,
                                       target_n=args.target_n, seed=args.seed)
            if not rows:
                raise ValueError(f"{city}/{period}: no valid pixels inside the fixed AOI")
            frames.extend(rows)
            summaries.append({**summary, "raster_file": area[path_key]})
    if len(summaries) != 32 or {r["city"].casefold() for r in summaries} != set(expected):
        raise ValueError("A sample-frame run must include both periods for all 16 registered areas")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame_path = args.output_dir / "reference_sample_frame.csv"
    with frame_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(frames[0]))
        writer.writeheader()
        writer.writerows(frames)
    summary_path = args.output_dir / "reference_sample_frame_summary.json"
    summary_path.write_text(json.dumps({
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "study_package_sha256": _sha256(package_path),
        "target_n_per_area_period": args.target_n,
        "area_periods": summaries,
        "frame_csv_sha256": _sha256(frame_path),
        "independent_reference_labels_created": False,
        "confirmatory_enrollment_established": False,
    }, indent=2) + "\n")
    print(f"Created {len(frames)} pending reference-label sample units across 16 areas and two periods")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
