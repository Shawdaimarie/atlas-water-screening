"""Screen an open ASEAN design-event flood atlas against ATLAS's fixed city boxes.

This is a modeled-hazard exposure screen, not an observed-event validation audit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.mask import mask
from rasterio.warp import transform_geom


RECORD_URL = "https://zenodo.org/records/21403070"
DOI = "10.5281/zenodo.21403070"
LICENSE = "CC-BY-4.0"
SCENARIO_DIR = "ssp585_2020"
SCENARIO_LABEL = "SSP5-8.5_2020"
RETURN_PERIODS = (10, 100, 1000)
HAZARDS = ("coastal", "fluvial", "pluvial")
DEPTH_THRESHOLDS_M = (0.0, 0.1)
PACKAGE_FILES = {
    "Singapore": {
        "filename": "singapore_flood_atlas.zip",
        "size": 22_449_935,
        "md5": "cdff30cedf012df7179d3a83a735866a",
    },
    "Jakarta": {
        "filename": "jakarta_flood_atlas.zip",
        "size": 57_406_347,
        "md5": "4fb4c0e6e8cc8bffcb80cc20167c5392",
    },
    "Bangkok": {
        "filename": "bangkok_flood_atlas.zip",
        "size": 93_837_667,
        "md5": "6bcb4dcce022499817fbefe64a1aaac7",
    },
}


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_bbox(value: str) -> tuple[float, float, float, float]:
    parts = tuple(float(item) for item in value.split(","))
    if len(parts) != 4 or not all(math.isfinite(item) for item in parts):
        raise ValueError(f"Invalid WGS84 AOI box: {value!r}")
    west, south, east, north = parts
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError(f"Invalid WGS84 AOI box: {value!r}")
    return west, south, east, north


def _aoi_polygon(bbox: tuple[float, float, float, float]) -> dict[str, Any]:
    west, south, east, north = bbox
    return {
        "type": "Polygon",
        "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]],
    }


def _check_package(city: str, archive: Path) -> dict[str, Any]:
    expected = PACKAGE_FILES[city]
    if not archive.is_file():
        raise FileNotFoundError(f"Missing {city} archive: {archive}")
    actual_size = archive.stat().st_size
    actual_md5 = md5_file(archive)
    if actual_size != expected["size"] or actual_md5 != expected["md5"]:
        raise ValueError(
            f"{city} archive does not match the pinned Zenodo v2 package "
            f"(size={actual_size}, md5={actual_md5})"
        )
    with zipfile.ZipFile(archive) as zipped:
        names = set(zipped.namelist())
        if "README.md" not in names or "LICENSE" not in names:
            raise ValueError(f"{city} package is missing README or LICENSE")
        readme = zipped.read("README.md").decode("utf-8")
        license_text = zipped.read("LICENSE").decode("utf-8")
        if "Design-event" not in readme or LICENSE.lower() not in license_text.lower():
            raise ValueError(f"{city} package does not declare the expected design-event data and license")
    return {"filename": expected["filename"], "bytes": actual_size, "md5": actual_md5}


def _raster_row(
    archive: Path,
    city: str,
    area: dict[str, Any],
    hazard: str,
    return_period: int,
) -> dict[str, Any]:
    inner = (
        f"maps/{city.lower()}_{SCENARIO_DIR}_rp{return_period}/{hazard}/"
        f"{hazard}_depth_{SCENARIO_LABEL}_rp{return_period}.tif"
    )
    vsi_path = f"/vsizip/{archive}/{inner}"
    source_geometry = _aoi_polygon(parse_bbox(area["aoi_bbox_wgs84"]))
    with rasterio.open(vsi_path) as dataset:
        if dataset.count != 1 or dataset.crs is None:
            raise ValueError(f"Unexpected raster structure for {city}/{hazard}/RP{return_period}")
        if not (math.isclose(abs(dataset.res[0]), 30.0, abs_tol=0.02)
                and math.isclose(abs(dataset.res[1]), 30.0, abs_tol=0.02)):
            raise ValueError(f"Expected 30 m cells for {city}/{hazard}/RP{return_period}")
        target_geometry = transform_geom("EPSG:4326", dataset.crs, source_geometry)
        clipped, transform = mask(
            dataset, [target_geometry], crop=True, filled=False, all_touched=False
        )
        raster = clipped[0]
        inside = geometry_mask(
            [target_geometry],
            out_shape=raster.shape,
            transform=transform,
            invert=True,
            all_touched=False,
        )
        valid = inside & ~np.ma.getmaskarray(raster) & np.isfinite(raster.data)
        total = int(inside.sum())
        valid_count = int(valid.sum())
        values = raster.data[valid]
        result = {
            "city": city,
            "region": area["region"],
            "hazard": hazard,
            "scenario": SCENARIO_LABEL,
            "return_period_years": return_period,
            "source_raster": inner,
            "crs": dataset.crs.to_string(),
            "resolution_m": [abs(dataset.res[0]), abs(dataset.res[1])],
            "pixel_rule": "pixel center inside the registered WGS84 bounding box",
            "aoi_pixels": total,
            "valid_depth_pixels": valid_count,
            "valid_pixel_fraction": valid_count / total if total else None,
            "wet_depth_gt_0_pixels": int(np.count_nonzero(values > DEPTH_THRESHOLDS_M[0])),
            "wet_depth_ge_0_10_pixels": int(np.count_nonzero(values >= DEPTH_THRESHOLDS_M[1])),
            "max_depth_m": float(values.max()) if valid_count else None,
            "wet_area_gt_0_km2": float(np.count_nonzero(values > 0.0) * 900 / 1_000_000),
            "wet_area_ge_0_10_km2": float(np.count_nonzero(values >= 0.1) * 900 / 1_000_000),
            "area_method": "30 m x 30 m projected pixel counts within valid-data cells only; missing/nodata cells are excluded, not treated as dry; depth >0 and >=0.10 m reported separately",
            "wet_area_denominator_pixels": valid_count,
            "nodata_value": (
                float(dataset.nodata)
                if dataset.nodata is not None and math.isfinite(float(dataset.nodata))
                else None
            ),
        }
        if total == 0:
            raise ValueError(f"No AOI pixel centers overlap {city}/{hazard}/RP{return_period}")
        return result


def build_audit(register: dict[str, Any], archive_dir: Path) -> dict[str, Any]:
    by_city = {area["city"]: area for area in register["results"]}
    if len(by_city) != len(register["results"]):
        raise ValueError("Study-area register has duplicate city names")
    cities = list(PACKAGE_FILES)
    missing = [city for city in cities if city not in by_city]
    if missing:
        raise ValueError(f"Study-area register is missing atlas cities: {missing}")
    packages = {
        city: _check_package(city, archive_dir / package["filename"])
        for city, package in PACKAGE_FILES.items()
    }
    rows = [
        _raster_row(archive_dir / PACKAGE_FILES[city]["filename"], city, by_city[city], hazard, rp)
        for city in cities
        for hazard in HAZARDS
        for rp in RETURN_PERIODS
    ]
    return {
        "audit_id": "atlas-asean-flood-atlas-fixed-aoi-screen",
        "schema_version": 1,
        "source": {
            "title": "Open Multi-Hazard Flood Atlas — Singapore, Kuala Lumpur, Bangkok and Jakarta",
            "doi": DOI,
            "record_url": RECORD_URL,
            "version": "v2 (2026-07-17)",
            "license": LICENSE,
            "data_type": "modeled design-event depth scenarios, not event observations",
            "source_author_validation_claim": "Dataset README calls the atlas validated and describes a frozen documented-hotspot register; this audit does not independently reproduce or verify that validation.",
        },
        "selection_rule": {
            "cities": cities,
            "scenario": SCENARIO_LABEL,
            "return_periods_years": list(RETURN_PERIODS),
            "hazards": list(HAZARDS),
            "spatial_rule": "ATLAS fixed 25 km x 25 km WGS84 bbox; pixel centers inside the box; transform to each source UTM CRS",
            "depth_thresholds_m": {"wet_area_gt_0": 0.0, "screening_area_ge_0_10": 0.1},
            "raster_resolution": "30 m",
        },
        "packages": packages,
        "results": rows,
        "interpretation_limits": [
            "Scenario return periods are modeled design conditions, not dated observed floods or event/baseline samples.",
            "This is a hazard-layer and exposure-context screen; it is not an independent validation set for ATLAS or for the source atlas.",
            "The three-city supplementary source is not balanced across the full 8+8 study frame and does not change confirmatory eligibility.",
            "The reported pixel area uses 30 m projected cells and the same pixel-center inclusion rule in all three cities; summary threshold depth>0 and threshold depth>=0.10 m are kept separate.",
            "The source README states model validation is described in an accompanying manuscript; that manuscript and frozen validation registers were not independently reviewed in this screening run.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--register", type=Path, default=Path("data/study_area_register.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/atlas-asean-flood-atlas-fixed-aoi-screen.json"))
    args = parser.parse_args()
    register = json.loads(args.register.read_text(encoding="utf-8"))
    audit = build_audit(register, args.archive_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(audit['results'])} fixed-AOI model-hazard screens to {args.output}")


if __name__ == "__main__":
    main()
