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
            raise ValueError(f"Duplicate acquisition date {acquired_at} in {period