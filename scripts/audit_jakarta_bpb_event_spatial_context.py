#!/usr/bin/env python3
"""Screen BPBD-reported Jan. 2026 Jakarta flood subdistricts against the fixed AOI.

This is an administrative-area context screen only. A kelurahan intersecting the
study box does not locate the reported inundation within that kelurahan and is
not a pixel reference label.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AREAS = ROOT / "data" / "study_area_register.json"
DEFAULT_OUTPUT = ROOT / "outputs" / "atlas-jakarta-bpbd-jan2026-aoi-context.json"
LAYER_URL = (
    "https://gis-dpmptsp.jakarta.go.id/arcgis/rest/services/Hosted/"
    "Batas_Administrasi_Kelurahan_DKI_Jakarta/FeatureServer/85/query"
)
BPBD_REPORT_URL = (
    "https://bpbd.jakarta.go.id/berita/"
    "Wkk2MjIwSnZEdjhUcklsb3gwVkh1Zz09/"
    "update-info-terkini-genangan-24-januari-2026-s-d-pukul-08-00-wib"
)
BPBD_RECESSION_URL = (
    "https://bpbd.jakarta.go.id/berita/"
    "WUVyVWZ0ejhuNXRSaFNLSDl6WVNMQT09/"
    "update-info-terkini-genangan-26-januari-2026-s-d-pukul-03-00-wib"
)

# Transcribed from the BPBD report's 24 Jan 2026 08:00 WIB impact list.
# Names are paired with the listed administrative city to avoid name-only joins.
REPORTED_AFFECTED_AREAS = [
    {"city": "JAKARTA BARAT", "kelurahan": name}
    for name in (
        "DURI KOSAMBI",
        "KAPUK",
        "KEDAUNG KALI ANGKE",
        "RAWA BUAYA",
        "JELAMBAR",
        "KEDOYA SELATAN",
        "KEDOYA UTARA",
        "JOGLO",
        "KEMBANGAN SELATAN",
        "KEMBANGAN UTARA",
        "MERUYA SELATAN",
    )
] + [
        {"city": "JAKARTA SELATAN", "kelurahan": name}
    for name in ("RAWAJATI", "PEJATEN TIMUR", "KEBON BARU")
] + [
    {"city": "JAKARTA TIMUR", "kelurahan": name}
    for name in (
        "RAWA TERATE",
        "BIDARA CINA",
        "KAMPUNG MELAYU",
        "CAWANG",
        "CILILITAN",
        "CIPINANG MELAYU",
    )
] + [{"city": "JAKARTA UTARA", "kelurahan": "KAPUK MUARA"}]

def _norm(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]+", "", str(value or "").upper())


def _feature_geometry(feature: dict[str, Any]) -> BaseGeometry:
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict):
        raise ValueError("boundary feature has no geometry")
    return shape(geometry)


def intersecting_reported_areas(
    features: list[dict[str, Any]],
    aoi_geojson: dict[str, Any],
    reported: list[dict[str, str]] = REPORTED_AFFECTED_AREAS,
) -> dict[str, Any]:
    """Return exact positive-area polygon intersections for reported areas."""
    aoi = shape(aoi_geojson)
    expected = {
        (_norm(x["city"]), _norm(x["kelurahan"])): x for x in reported
    }
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for feature in features:
        attrs = feature.get("properties") or feature.get("attributes") or {}
        key = (_norm(attrs.get("wadmkk")), _norm(attrs.get("wadmkd")))
        if key not in expected:
            continue
        geom = _feature_geometry(feature)
        overlap = geom.intersection(aoi)
        by_key[key] = {
            "administrative_city": attrs.get("wadmkk"),
            "kelurahan": attrs.get("wadmkd"),
            "kecamatan": attrs.get("wadmkc"),
            "positive_area_intersection": bool(not overlap.is_empty and overlap.area > 0),
            # Planar degree-squared only distinguishes positive-area overlap;
            # it is deliberately not reported as a physical area measurement.
            "intersection_area_degrees_squared": float(overlap.area),
        }

    not_returned_by_aoi_query = sorted(set(expected) - set(by_key))
    overlaps = [
        row for row in by_key.values() if row["positive_area_intersection"]
    ]
    return {
        "reported_affected_kelurahan_count": len(expected),
        "reported_areas_returned_by_aoi_intersection_query_count": len(by_key),
        "not_returned_by_aoi_intersection_query": [
            {
                "administrative_city": expected[(city, name)]["city"],
                "kelurahan": expected[(city, name)]["kelurahan"],
            }
            for city, name in not_returned_by_aoi_query
        ],
        "positive_area_intersections": sorted(
            overlaps,
            key=lambda row: (row["administrative_city"], row["kelurahan"]),
        ),
        "positive_area_intersection_count": len(overlaps),
    }


def build_query(aoi_bbox: str) -> tuple[str, dict[str, str]]:
    # Keep the service request simple and portable: use its spatial filter to
    # return every boundary crossing the fixed box, then match event names
    # locally. This avoids depending on a provider-specific SQL expression.
    params = {
        "where": "1=1",
        "outFields": "wadmkd,wadmkc,wadmkk",
        "returnGeometry": "true",
        "geometry": aoi_bbox,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outSR": "4326",
        "f": "geojson",
        "resultRecordCount": "2000",
    }
    return LAYER_URL, params


def fetch_features(aoi_bbox: str, timeout: int = 60) -> tuple[list[dict[str, Any]], str]:
    url, params = build_query(aoi_bbox)
    request_url = url + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        request_url,
        headers={"User-Agent": "ATLAS reproducible research audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read()
    digest = hashlib.sha256(payload).hexdigest()
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as error:
        prefix = payload[:100].decode("utf-8", errors="replace")
        raise ValueError(
            "ArcGIS query returned non-JSON content "
            f"(bytes={len(payload)}, prefix={prefix!r})"
        ) from error
    if "error" in data:
        raise RuntimeError(f"ArcGIS query failed with error code {data['error'].get('code')}")
    features = data.get("features")
    if not isinstance(features, list):
        raise ValueError("ArcGIS response is missing features")
    if data.get("exceededTransferLimit"):
        raise ValueError("ArcGIS response exceeded the transfer limit; refusing partial result")
    return features, digest


def create_audit(register_path: Path = DEFAULT_AREAS) -> dict[str, Any]:
    register = json.loads(register_path.read_text(encoding="utf-8"))
    area = next(x for x in register["results"] if x["city"] == "Jakarta")
    bbox = [float(value) for value in area["aoi_bbox_wgs84"].split(",")]
    west, south, east, north = bbox
    aoi = {
        "type": "Polygon",
        "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]],
    }
    features, response_sha = fetch_features(area["aoi_bbox_wgs84"])
    result = intersecting_reported_areas(features, aoi)
    return {
        "audit_id": "jakarta-bpbd-2026-01-fixed-aoi-administrative-context-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "study_area": {
            "city": "Jakarta",
            "region": "International",
            "aoi_bbox_wgs84": area["aoi_bbox_wgs84"],
            "nominal_area_km2": area["aoi_area_km2"],
        },
        "event": {
            "official_interval_local_dates": ["2026-01-22", "2026-01-24"],
            "bpbd_as_of_reported_inundation": "2026-01-24T08:00:00+07:00",
            "bpbd_reported_inundated_household_units": 90,
            "bpbd_reported_inundated_road_segments": 10,
            "bpbd_recession_update": "2026-01-26T03:00:00+07:00",
            "bpbd_sources": [BPBD_REPORT_URL, BPBD_RECESSION_URL],
        },
        "boundary_source": {
            "url": LAYER_URL.rsplit("/query", 1)[0],
            "layer_id": 85,
            "layer_name": "Batas Administrasi Kelurahan DKI Jakarta",
            "service_item_id": "b5502a02bdad4964a81eb93a1fb03597",
            "spatial_reference": "EPSG:4326 requested from service layer EPSG:32748",
            "query_response_sha256": response_sha,
            "query_feature_count": len(features),
        },
        "spatial_screen": result,
        "opera_dates_near_event": ["2026-01-18", "2026-01-21", "2026-01-23", "2026-01-25", "2026-01-26", "2026-01-30"],
        "interpretation": {
            "finding": "A positive-area intersection means an officially listed affected kelurahan polygon overlaps the fixed AOI; it does not locate the reported inundated RT, household, street, or water within that polygon.",
            "not_returned_limit": "A listed area not returned by the boundary service's AOI-intersection query may lie outside the fixed box or reflect a name/boundary-source mismatch; it is not evidence that flooding did not occur.",
            "independent_pixel_labels": False,
            "opera_pixel_qa_performed": False,
            "event_confirmed_for_followup": True,
            "confirmatory_enrollment_eligible": False,
            "score_credit": 0,
            "next_gate": "Locate dated inundation points or licensed polygons inside the AOI, retrieve event and baseline DSWx-S1 rasters, run the preregistered BWTR QA gate, and obtain independent pixel reference labels.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=DEFAULT_AREAS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        result = create_audit(args.register)
    except Exception as error:  # noqa: BLE001 - only the public query diagnostic is included
        print(
            f"FAIL: Jakarta event spatial screen failed ({type(error).__name__}): {error}",
            file=sys.stderr,
        )
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(
        "Positive-area intersecting reported kelurahan polygons: "
        f"{result['spatial_screen']['positive_area_intersection_count']} / "
        f"{result['spatial_screen']['reported_affected_kelurahan_count']}"
    )
    print("This is event-area context only; no raster QA, independent labels, or enrollment credit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
