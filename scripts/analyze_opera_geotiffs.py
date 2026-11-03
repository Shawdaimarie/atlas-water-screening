"""Pixel-QA and asset overlap analysis for locally authorized OPERA DSWx-S1 BWTR COGs.

This module never downloads data or accepts remote URLs. Supply a manifest of
already-authorized local files; credentials and temporary download tokens stay
outside the analysis process and repository.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

try:
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.warp import transform_geom
    from rasterio.windows import Window, from_bounds, transform as window_transform
except ImportError as exc:  # pragma: no cover - exercised by CLI users without optional extra
    raise SystemExit("Install geospatial support with: pip install -r requirements-analysis.txt") from exc


PRODUCT = "OPERA_L3_DSWX-S1_V1"
PRODUCT_DOI = "https://doi.org/10.5067/OPDSWS1-L3V1"
PRODUCT_BAND = "BWTR_Binary_water"
WATER_CLASSES = {1}
VALID_CLASSES = {0, 1}
INVALID_CLASSES = {250, 251, 255}


@dataclass(frozen=True)
class Observation:
    path: Path
    acquired_at: date
    period: str
    selection_anchor: date
    granule_id: str
    product_version: str
    processing_version: str
    retrieved_at: str


def _features(document: dict[str, Any]) -> list[dict[str, Any]]:
    if document.get("type") == "FeatureCollection":
        features = document.get("features", [])
    elif document.get("type") == "Feature":
        features = [document]
    else:
        raise ValueError("GeoJSON must be a Feature or FeatureCollection")
    if not features:
        raise ValueError("GeoJSON must contain at least one feature")
    if any(f.get("geometry") is None for f in features):
        raise ValueError("Null geometries are not allowed")
    return features


def load_geojson(path: Path, *, id_key: str | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    document = json.loads(path.read_text())
    features = _features(document)
    geometries = [f["geometry"] for f in features]
    if id_key is None:
        return geometries, []
    records = []
    seen: set[str] = set()
    for index, feature in enumerate(features, start=1):
        props = feature.get("properties") or {}
        asset_id = str(props.get(id_key, "")).strip()
        if not asset_id or asset_id in seen:
            raise ValueError(f"Each asset needs a unique non-empty {id_key!r}")
        seen.add(asset_id)
        records.append({
            "asset_id": asset_id,
            "asset_name": str(props.get("asset_name") or asset_id),
            "geometry": feature["geometry"],
        })
    return geometries, records


def load_manifest(path: Path) -> list[Observation]:
    required = {"path", "band", "acquired_at", "selection_anchor", "period", "granule_id",
                "product_version", "processing_version", "retrieved_at"}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"Manifest must include columns: {', '.join(sorted(required))}")
        rows = list(reader)
    if not rows:
        raise ValueError("Manifest has no observations")
    seen_dates: set[date] = set()
    anchors: dict[str, date] = {}
    observations = []
    versions = set()
    processing_versions = set()
    root = path.resolve().parent
    for row in rows:
        if row["band"].strip() != PRODUCT_BAND:
            raise ValueError(f"Expected pinned band {PRODUCT_BAND}, got {row['band'].strip()!r}")
        period = row["period"].strip().lower()
        if period not in {"event", "baseline"}:
            raise ValueError(f"Invalid period {period!r}; use 'event' or 'baseline'")
        acquired_at = date.fromisoformat(row["acquired_at"].strip()[:10])
        if acquired_at in seen_dates:
            raise ValueError(f"Duplicate acquisition date {acquired_at} in {period} period; mosaic tile granules first")
        seen_dates.add(acquired_at)
        selection_anchor = date.fromisoformat(row["selection_anchor"].strip()[:10])
        if period in anchors and anchors[period] != selection_anchor:
            raise ValueError(f"All {period} observations must share one predeclared selection_anchor")
        anchors[period] = selection_anchor
        target = (root / row["path"].strip()).resolve()
        if not target.is_relative_to(root):
            raise ValueError("Manifest paths must remain within the manifest directory")
        if not target.is_file():
            raise ValueError(f"Observation file not found: {row['path']}")
        version = row["product_version"].strip()
        if version != PRODUCT:
            raise ValueError(f"Expected pinned product {PRODUCT}, got {version!r}")
        versions.add(version)
        processing_version = row["processing_version"].strip()
        if not processing_version:
            raise ValueError("processing_version must be copied from product metadata")
        processing_versions.add(processing_version)
        retrieved_value = row["retrieved_at"].strip()
        try:
            retrieved_dt = datetime.fromisoformat(retrieved_value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("retrieved_at must be an ISO-8601 timestamp with timezone") from exc
        if retrieved_dt.tzinfo is None:
            raise ValueError("retrieved_at must include a timezone")
        observations.append(Observation(target, acquired_at, period, selection_anchor,
                                        row["granule_id"].strip(), version, processing_version,
                                        retrieved_dt.isoformat()))
    if versions != {PRODUCT}:
        raise ValueError("All observations must use the same pinned product version")
    if len(processing_versions) != 1:
        raise ValueError("All observations must use one processing software version")
    return sorted(observations, key=lambda o: (o.period, o.acquired_at, o.granule_id))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _metric_projected_meters(crs: Any) -> bool:
    if crs is None or not crs.is_projected:
        return False
    units = str(getattr(crs, "linear_units", "")).lower()
    return units in {"metre", "meter", "metres", "meters"}


def _pixel_grid(geometry: dict[str, Any], src: Any, *, src_crs: str,
                all_touched: bool = False) -> tuple[Any, Any]:
    projected = transform_geom(src_crs, src.crs, geometry, precision=-1)
    left, bottom, right, top = _bounds(projected)
    raw = from_bounds(left, bottom, right, top, transform=src.transform)
    col0, row0 = math.floor(raw.col_off), math.floor(raw.row_off)
    col1, row1 = math.ceil(raw.col_off + raw.width), math.ceil(raw.row_off + raw.height)
    window = Window(col0, row0, max(1, col1 - col0), max(1, row1 - row0))
    data = src.read(1, window=window, boundless=True, fill_value=255)
    transform = window_transform(window, src.transform)
    selected = geometry_mask([projected], out_shape=data.shape, transform=transform, invert=True,
                             all_touched=all_touched)
    return data, selected


def _bounds(geometry: dict[str, Any]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    def walk(value: Any) -> None:
        if isinstance(value, (list, tuple)):
            if len(value) >= 2 and isinstance(value[0], (int, float)) and isinstance(value[1], (int, float)):
                xs.append(float(value[0])); ys.append(float(value[1]))
            else:
                for child in value:
                    walk(child)
    walk(geometry["coordinates"])
    if not xs or not ys:
        raise ValueError("Geometry has no coordinates")
    return min(xs), min(ys), max(xs), max(ys)


def _metrics(data: Any, selected: Any) -> dict[str, int | float | None]:
    import numpy as np
    total = int(np.count_nonzero(selected))
    if total == 0:
        return {"footprint_pixels": 0, "valid_pixels": 0, "water_pixels": 0, "valid_fraction": 0.0, "water_fraction_valid": None, "unexpected_classes": 0}
    values = data[selected]
    valid = np.isin(values, list(VALID_CLASSES))
    water = np.isin(values, list(WATER_CLASSES))
    valid_count = int(np.count_nonzero(valid))
    water_count = int(np.count_nonzero(water & valid))
    unexpected = ~np.isin(values, list(VALID_CLASSES | INVALID_CLASSES))
    return {
        "footprint_pixels": total,
        "valid_pixels": valid_count,
        "water_pixels": water_count,
        "valid_fraction": valid_count / total,
        "water_fraction_valid": water_count / valid_count if valid_count else None,
        "unexpected_classes": int(np.count_nonzero(unexpected)),
    }


def analyze(manifest_path: Path, aoi_path: Path, assets_path: Path, *,
            aoi_crs: str = "EPSG:4326", assets_crs: str = "EPSG:4326",
            min_valid_fraction: float = 0.8, min_dates: int = 3) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0 < min_valid_fraction <= 1:
        raise ValueError("min_valid_fraction must be in (0, 1]")
    if min_dates < 1:
        raise ValueError("min_dates must be at least 1")
    aoi_geometries, _ = load_geojson(aoi_path)
    if len(aoi_geometries) != 1:
        raise ValueError("AOI GeoJSON must contain exactly one feature")
    _, assets = load_geojson(assets_path, id_key="asset_id")
    if not assets:
        raise ValueError("Asset file must contain at least one asset")
    observations = load_manifest(manifest_path)
    per_observation: list[dict[str, Any]] = []
    per_asset_period: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: {"event": [], "baseline": []})

    for obs in observations:
        with rasterio.open(obs.path) as src:
            if src.count != 1:
                raise ValueError(f"Expected a single-band BWTR raster: {obs.path.name}")
            if not _metric_projected_meters(src.crs):
                raise ValueError(f"Expected projected metre CRS, got {src.crs}")
            xres, yres = src.res
            if not (abs(abs(xres) - 30) <= 0.5 and abs(abs(yres) - 30) <= 0.5):
                raise ValueError(f"Expected nominal 30 m DSWx-S1 posting, got {src.res}")
            aoi_data, aoi_mask = _pixel_grid(aoi_geometries[0], src, src_crs=aoi_crs)
            aoi_stats = _metrics(aoi_data, aoi_mask)
            source_sha256 = file_sha256(obs.path)
            for asset in assets:
                data, selected = _pixel_grid(asset["geometry"], src, src_crs=assets_crs, all_touched=True)
                stats = _metrics(data, selected)
                candidate = (
                    aoi_stats["valid_fraction"] >= min_valid_fraction
                    and stats["footprint_pixels"] > 0
                    and stats["valid_fraction"] >= min_valid_fraction
                    and stats["unexpected_classes"] == 0
                )
                row = {
                    "product_band": PRODUCT_BAND,
                    "granule_id": obs.granule_id,
                    "acquired_at": obs.acquired_at.isoformat(),
                    "period": obs.period,
                    "selection_anchor": obs.selection_anchor.isoformat(),
                    "product_version": obs.product_version,
                    "processing_version": obs.processing_version,
                    "retrieved_at": obs.retrieved_at,
                    "product_doi": PRODUCT_DOI,
                    "asset_id": asset["asset_id"],
                    "asset_name": asset["asset_name"],
                    "aoi_valid_fraction": round(float(aoi_stats["valid_fraction"]), 6),
                    "asset_valid_fraction": round(float(stats["valid_fraction"]), 6),
                    "asset_water_fraction_valid": (round(float(stats["water_fraction_valid"]), 6) if stats["water_fraction_valid"] is not None else None),
                    "aoi_valid_pixels": aoi_stats["valid_pixels"],
                    "asset_valid_pixels": stats["valid_pixels"],
                    "asset_water_pixels": stats["water_pixels"],
                    "unexpected_classes": stats["unexpected_classes"],
                    "candidate_observation": candidate,
                    "source_file": obs.path.name,
                    "source_sha256": source_sha256,
                    "analysis_code_sha256": file_sha256(Path(__file__).resolve()),
                    "data_mode": "local_user_supplied_opera_file_unverified",
                }
                per_observation.append(row)
                if candidate:
                    per_asset_period[asset["asset_id"]][obs.period].append(row)

    comparisons: list[dict[str, Any]] = []
    for asset in assets:
        def selection_order(row: dict[str, Any]) -> tuple[int, str, str]:
            anchor = date.fromisoformat(row["selection_anchor"])
            acquired = date.fromisoformat(row["acquired_at"])
            return abs((acquired - anchor).days), acquired.isoformat(), row["granule_id"]
        event_rows = sorted(per_asset_period[asset["asset_id"]]["event"], key=selection_order)
        baseline_rows = sorted(per_asset_period[asset["asset_id"]]["baseline"], key=selection_order)
        matched_n = min(len(event_rows), len(baseline_rows))
        eligible = len(event_rows) >= min_dates and len(baseline_rows) >= min_dates
        if eligible:
            # Deterministic nearest-to-anchor selection; same N in both periods.
            matched_event, matched_baseline = event_rows[:matched_n], baseline_rows[:matched_n]
            event_mean = sum(r["asset_water_fraction_valid"] for r in matched_event) / matched_n
            baseline_mean = sum(r["asset_water_fraction_valid"] for r in matched_baseline) / matched_n
            delta = event_mean - baseline_mean
        else:
            matched_event, matched_baseline = [], []
            event_mean = baseline_mean = delta = None
        comparisons.append({
            "asset_id": asset["asset_id"],
            "asset_name": asset["asset_name"],
            "status": "candidate_coverage_pass" if eligible else "unknown_insufficient_qa_valid_dates",
            "event_qa_valid_dates": len(event_rows),
            "baseline_qa_valid_dates": len(baseline_rows),
            "matched_dates_per_period": matched_n if eligible else 0,
            "event_selected_dates": ";".join(r["acquired_at"] for r in sorted(matched_event, key=lambda r: r["acquired_at"])),
            "baseline_selected_dates": ";".join(r["acquired_at"] for r in sorted(matched_baseline, key=lambda r: r["acquired_at"])),
            "event_mean_water_fraction": round(event_mean, 6) if event_mean is not None else None,
            "baseline_mean_water_fraction": round(baseline_mean, 6) if baseline_mean is not None else None,
            "water_fraction_difference": round(delta, 6) if delta is not None else None,
            "min_valid_fraction": min_valid_fraction,
            "min_dates_per_period": min_dates,
            "selection_rule": "nearest_to_predeclared_period_anchor_then_earliest_date_then_granule_id",
            "data_mode": "local_user_supplied_opera_file_unverified",
            "interpretation_limit": "water fraction is not damage, service failure, or independent flood truth",
        })
    return per_observation, comparisons


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="CSV of local, already-authorized BWTR GeoTIFFs")
    parser.add_argument("--aoi", type=Path, required=True, help="Single-feature AOI GeoJSON")
    parser.add_argument("--assets", type=Path, required=True, help="Asset FeatureCollection GeoJSON with asset_id properties")
    parser.add_argument("--aoi-crs", default="EPSG:4326")
    parser.add_argument("--assets-crs", default="EPSG:4326")
    parser.add_argument("--min-valid-fraction", type=float, default=0.8)
    parser.add_argument("--min-dates", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run_started_at = datetime.now(timezone.utc).isoformat()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    observations, comparisons = analyze(args.manifest, args.aoi, args.assets, aoi_crs=args.aoi_crs,
                                       assets_crs=args.assets_crs, min_valid_fraction=args.min_valid_fraction,
                                       min_dates=args.min_dates)
    write_csv(args.output_dir / "observation_qa.csv", observations)
    write_csv(args.output_dir / "asset_event_baseline_comparison.csv", comparisons)
    source_observations = load_manifest(args.manifest)
    run_manifest = {
        "schema_version": 1,
        "run_started_at": run_started_at,
        "run_completed_at": datetime.now(timezone.utc).isoformat(),
        "analysis_script_sha256": file_sha256(Path(__file__).resolve()),
        "data_mode": "local_user_supplied_opera_file_unverified",
        "inputs": {
            "manifest": {"file": args.manifest.name, "sha256": file_sha256(args.manifest)},
            "aoi": {"file": args.aoi.name, "sha256": file_sha256(args.aoi)},
            "assets": {"file": args.assets.name, "sha256": file_sha256(args.assets)},
            "observations": [{"granule_id": o.granule_id, "acquired_at": o.acquired_at.isoformat(),
                              "period": o.period, "band": PRODUCT_BAND, "file": o.path.name, "sha256": file_sha256(o.path),
                              "product_version": o.product_version, "processing_version": o.processing_version,
                              "retrieved_at": o.retrieved_at} for o in source_observations],
        },
        "analysis": {"product_doi": PRODUCT_DOI, "min_valid_fraction": args.min_valid_fraction,
                     "min_dates_per_period": args.min_dates, "aoi_crs": args.aoi_crs,
                     "assets_crs": args.assets_crs,
                     "band": PRODUCT_BAND,
                     "bwtr_water_classes": sorted(WATER_CLASSES),
                     "bwtr_valid_classes": sorted(VALID_CLASSES),
                     "bwtr_mask_classes": sorted(INVALID_CLASSES)},
        "outputs": {name: file_sha256(args.output_dir / name) for name in
                    ("observation_qa.csv", "asset_event_baseline_comparison.csv")},
        "independent_label_validation_performed": False,
    }
    (args.output_dir / "run_manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n")
    print(f"Wrote {len(observations)} observation-asset QA rows and {len(comparisons)} asset comparisons")


if __name__ == "__main__":
    main()
