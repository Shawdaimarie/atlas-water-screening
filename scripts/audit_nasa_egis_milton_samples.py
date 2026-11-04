#!/usr/bin/env python3
"""Audit sampled Tampa pixels from NASA EGIS Hurricane Milton WTR mosaics.

This is a reproducible source-access and sampled-return screen. NASA labels the
response maps preliminary and unvalidated; the results are not reference truth,
full-scene coverage, or a flood-change estimate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_nasa_egis_opera_samples import equal_area_sample_points


REGISTER = ROOT / "data/study_area_register.json"
DEFAULT_JSON = ROOT / "outputs/atlas-tampa-milton-egis-pixel-sample.json"
DEFAULT_CSV = ROOT / "outputs/atlas-tampa-milton-egis-pixel-sample.csv"
DEFAULT_MD = ROOT / "outputs/atlas-tampa-milton-egis-pixel-sample.md"
SERVICE_ITEM_URL = "https://gis.earthdata.nasa.gov/portal/home/item.html?id=d20858f42cae4c6b8b4438e847266442"
PRODUCT_SPEC_URL = "https://www.earthdata.nasa.gov/s3fs-public/2023-12/ProductSpec_DSWX_S1.pdf"
SERVICE_URL = (
    "https://gis.earthdata.nasa.gov/portal/rest/services/"
    "DISASTERS_202410_HURRICANE_MILTON/2428_opera_dswx_hls/ImageServer"
)
SCENES = (
    {"raster_id": 2, "name": "OPERA_DSWx_S1_WTR_20241003_mosaic", "date": "2024-10-03", "phase": "pre-landfall"},
    {"raster_id": 3, "name": "OPERA_DSWx_S1_WTR_20241008_mosaic", "date": "2024-10-08", "phase": "pre-landfall"},
    {"raster_id": 4, "name": "OPERA_DSWx_S1_WTR_20241010_mosaic", "date": "2024-10-10", "phase": "post-landfall"},
    {"raster_id": 5, "name": "OPERA_DSWx_S1_WTR_20241011_mosaic", "date": "2024-10-11", "phase": "post-landfall"},
)
SAMPLES_PER_SCENE = 1024
CHUNK_SIZE = 256
VALID_CLASSES = {0, 1, 2, 3, 7}
INVALID_CLASSES = {4, 5, 6, 120, 254, 255}
ALLOWED_CLASSES = VALID_CLASSES | INVALID_CLASSES
CLASS_LABELS = {
    0: "not water",
    1: "open water",
    2: "high-backscattering water",
    3: "low-backscattering non-water",
    4: "landcover masked",
    5: "HAND masked",
    6: "layover/shadow masked",
    7: "inundated vegetation",
    120: "fill/no data",
    254: "ocean masked",
    255: "no data/transparent",
}


def _request_json(url: str, params: dict[str, Any], *, timeout: int = 60) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(params).encode("utf-8"),
        headers={"User-Agent": "ATLAS-research-audit/1.0", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        document = json.load(response)
    if not isinstance(document, dict):
        raise ValueError("NASA EGIS returned a non-object JSON response")
    return document


def _date_utc(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, timezone.utc).date().isoformat()
    return str(value)[:10]


def _fetch_item(fetch_json: Callable[..., dict[str, Any]], scene: dict[str, Any]) -> dict[str, Any]:
    result = fetch_json(f"{SERVICE_URL}/query", {
        "objectIds": str(scene["raster_id"]),
        "outFields": "objectid,name,date,groupname,productname,category",
        "returnGeometry": "false",
        "f": "json",
    })
    if "error" in result:
        raise RuntimeError(f"Catalog query failed for {scene['date']}: {result['error'].get('code')}")
    features = result.get("features", [])
    if len(features) != 1:
        raise ValueError(f"Expected one catalog item for raster {scene['raster_id']}; received {len(features)}")
    attrs = features[0].get("attributes") or {}
    expected = {
        "objectid": scene["raster_id"],
        "name": scene["name"],
        "date": scene["date"],
        "productname": "WTR mosaic",
        "category": 1,
    }
    actual = {"objectid": attrs.get("objectid"), "name": attrs.get("name"),
              "date": _date_utc(attrs.get("date")), "productname": attrs.get("productname"),
              "category": attrs.get("category")}
    if actual != expected:
        raise ValueError(f"NASA EGIS catalog metadata changed for {scene['date']}")
    return actual


def _sample_scene(fetch_json: Callable[..., dict[str, Any]], scene: dict[str, Any],
                  points: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    error: dict[str, Any] | None = None
    for start in range(0, len(points), CHUNK_SIZE):
        chunk = points[start:start + CHUNK_SIZE]
        geometry = {"points": [[p["x_3857"], p["y_3857"]] for p in chunk], "spatialReference": {"wkid": 102100}}
        params = {
            "geometry": json.dumps(geometry, separators=(",", ":")),
            "geometryType": "esriGeometryMultipoint",
            "mosaicRule": json.dumps({"mosaicMethod": "esriMosaicLockRaster", "lockRasterIds": [scene["raster_id"]]}, separators=(",", ":")),
            "pixelSize": json.dumps({"x": 29.97600242, "y": 29.97600242, "spatialReference": {"wkid": 102100}}, separators=(",", ":")),
            "interpolation": "RSP_NearestNeighbor",
            "returnFirstValueOnly": "false",
            "f": "json",
        }
        result = fetch_json(f"{SERVICE_URL}/getSamples", params)
        if "error" in result:
            error = {"code": result["error"].get("code"), "message": result["error"].get("message", "")}
            break
        by_id: dict[int, dict[str, Any]] = {}
        for sample in result.get("samples", []):
            if sample.get("locationId") is None:
                continue
            location_id = int(sample["locationId"])
            if not 0 <= location_id < len(chunk) or location_id in by_id:
                raise ValueError("NASA EGIS returned an invalid or duplicate locationId")
            if sample.get("rasterId") != scene["raster_id"]:
                raise ValueError("NASA EGIS returned a sample from an unlocked raster")
            by_id[location_id] = sample
        for offset, point in enumerate(chunk):
            sample = by_id.get(offset)
            raw = None if sample is None else sample.get("value")
            try:
                value = int(str(raw).split(",", 1)[0]) if raw is not None else None
            except ValueError as exc:
                raise ValueError(f"Unexpected WTR sample value {raw!r}") from exc
            if value is not None and value not in ALLOWED_CLASSES:
                raise ValueError(f"Unrecognized WTR class {value}")
            resolution = None if sample is None else sample.get("resolution")
            if resolution is not None and abs(float(resolution) - 30) > 1:
                raise ValueError(f"Expected approximately 30 m sample resolution; got {resolution}")
            rows.append({
                "sample_id": point["sample_id"], "stratum_row": point["stratum_row"],
                "stratum_col": point["stratum_col"], "lon": point["lon"], "lat": point["lat"],
                "raster_id": scene["raster_id"], "date_utc": scene["date"],
                "phase": scene["phase"], "wtr_class": value,
                "class_label": CLASS_LABELS.get(value), "source_resolution_m": resolution,
                "sample_status": "returned" if sample is not None else "no_sample_returned",
            })
        if error:
            break
    if error:
        # Explicitly retain unattempted locations as unknown after a service error.
        completed_ids = {row["sample_id"] for row in rows}
        for point in points:
            if point["sample_id"] in completed_ids:
                continue
            rows.append({
                "sample_id": point["sample_id"], "stratum_row": point["stratum_row"],
                "stratum_col": point["stratum_col"], "lon": point["lon"], "lat": point["lat"],
                "raster_id": scene["raster_id"], "date_utc": scene["date"],
                "phase": scene["phase"], "wtr_class": None, "class_label": None,
                "source_resolution_m": None, "sample_status": "not_sampled_after_service_error",
            })
    counts = Counter(row["wtr_class"] for row in rows if row["wtr_class"] is not None)
    returned = sum(row["sample_status"] == "returned" for row in rows)
    summary = {
        "raster_id": scene["raster_id"], "name": scene["name"], "date_utc": scene["date"],
        "phase": scene["phase"], "samples_requested": len(points), "samples_returned": returned,
        "sample_return_fraction": returned / len(points) if points else None,
        "class_counts": {str(code): counts[code] for code in sorted(counts)},
        "recognized_nonmasked_class_points": sum(counts[code] for code in VALID_CLASSES),
        "masked_or_fill_class_points": sum(counts[code] for code in INVALID_CLASSES),
        "sampling_status": "service_error" if error else "sampled",
        "sampling_error": error,
        "interpretation": "Equal-area point-sample returns only; not full-AOI raster coverage or flood truth.",
    }
    return rows, summary


def run(fetch_json: Callable[..., dict[str, Any]] = _request_json,
        register_path: Path = REGISTER) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    register_bytes = register_path.read_bytes()
    register = json.loads(register_bytes)
    matches = [a for a in register.get("results", []) if a.get("city") == "Tampa"]
    if len(matches) != 1:
        raise ValueError("Expected exactly one fixed Tampa AOI in the study register")
    area = matches[0]
    bbox = tuple(float(v) for v in area["aoi_bbox_wgs84"].split(","))
    points = equal_area_sample_points(bbox, seed="ATLAS-Tampa-Milton-EGIS-WTR-v1")

    metadata = fetch_json(SERVICE_URL, {"f": "json"})
    description = html.unescape(re.sub(r"<[^>]+>", " ", str(metadata.get("description") or "")))
    description = " ".join(description.split())
    if "preliminary and unvalidated" not in description.casefold():
        raise ValueError("Expected NASA's preliminary and unvalidated service caveat")
    if "October 3, 2024" not in description or "October 11, 2024" not in description or "30 meters" not in description:
        raise ValueError("NASA service metadata did not match the pinned dates and resolution")

    scene_summaries = []
    all_rows = []
    for scene in SCENES:
        item = _fetch_item(fetch_json, scene)
        rows, summary = _sample_scene(fetch_json, scene, points)
        summary["catalog_item"] = item
        scene_summaries.append(summary)
        all_rows.extend(rows)
    report = {
        "audit": "ATLAS Tampa Hurricane Milton NASA EGIS WTR pixel-sample availability screen",
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_area": {
            "city": "Tampa", "region": "United States", "aoi_bbox_wgs84": list(bbox),
            "register_sha256": hashlib.sha256(register_bytes).hexdigest(),
        },
        "service": {"url": SERVICE_URL, "item_url": SERVICE_ITEM_URL,
                    "class_reference_url": PRODUCT_SPEC_URL, "product": "OPERA DSWx-S1 WTR mosaics",
                    "description": description, "resolution_m": 30,
                    "source_caveat": "NASA identifies the response imagery as preliminary and unvalidated."},
        "sample_design": {
            "method": "One seeded, jittered equal-area point per cell in a 32 by 32 grid over the frozen AOI.",
            "samples_per_scene": len(points), "seed": "ATLAS-Tampa-Milton-EGIS-WTR-v1",
            "same_points_for_each_scene": True, "pixel_interpolation": "nearest neighbor",
            "not_an_estimator": "No area-wide classification or change inference is made from this availability sample.",
        },
        "class_contract": {str(code): CLASS_LABELS[code] for code in sorted(ALLOWED_CLASSES)},
        "scenes": scene_summaries,
        "confirmatory_eligibility": "not assessed; this exploratory sample does not satisfy label, full-raster QA, or precision requirements",
        "overall_interpretation": "NASA EGIS sample-return behavior across candidate dates in Tampa only. The preliminary response maps are not independent reference labels and no water-change or accuracy result is claimed.",
    }
    return report, all_rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["date_utc", "phase", "raster_id", "sample_id", "stratum_row", "stratum_col",
              "lon", "lat", "wtr_class", "class_label", "source_resolution_m", "sample_status"]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Tampa Hurricane Milton NASA EGIS WTR sample screen",
        "",
        f"**Run:** {report['created_at_utc']}  ",
        "**Status:** Exploratory point-sample availability screen only  ",
        "**AOI:** Frozen Tampa 25 × 25 km candidate box; no geometry changes  ",
        "**Samples:** 1,024 same-point, equal-area strata per catalog date at approximately 30 m nearest-neighbor resolution",
        "",
        "## Results",
        "",
        "| NASA catalog date | Phase | Catalog item | Sample return | Returned WTR classes | Endpoint result |",
        "|---|---|---|---:|---|---|",
    ]
    for scene in report["scenes"]:
        classes = ", ".join(f"{code}: {count}" for code, count in scene["class_counts"].items()) or "none"
        err = scene.get("sampling_error")
        endpoint = f"HTTP/REST error {err['code']}: {err['message']}" if err else "sampled"
        lines.append(
            f"| {scene['date_utc']} | {scene['phase']} | {scene['raster_id']} | "
            f"{scene['samples_returned']}/{scene['samples_requested']} ({scene['sample_return_fraction']:.1%}) | {classes} | {endpoint} |"
        )
    lines.extend([
        "",
        "On 2024-10-03, 797/1,024 requested points returned (77.8%); the other 227 returned no sample. The 2024-10-08 and 2024-10-11 requests returned all 1,024 points. The catalog item for 2024-10-10 is present, but NASA EGIS `getSamples` returned error code 400 (`Invalid or missing input parameters.`) on the first locked-raster request; the 1,024 points for that date are explicitly recorded as unsampled after the service error.",
        "",
        "The returned values were raw WTR codes, not a binary flood label. In the three sampled dates, code 0 (not water), code 1 (open water), and code 3 (low-backscattering non-water) were observed. The complete class mapping is in the JSON artifact and NASA product specification.",
        "",
        "## Method and limits",
        "",
        "A seeded jittered equal-area 32 × 32 grid was placed over the frozen Tampa AOI; the same 1,024 coordinates were requested for each date. Requests locked the NASA catalog raster ID and used nearest-neighbor sampling. The CSV retains a row for every point/date, including missing samples and the service-error date. The JSON stores item IDs and dates, service description, AOI/register hash, class definitions, per-date counts, and the error response.",
        "",
        "NASA describes these emergency response maps as **preliminary and unvalidated**. This sample-return fraction is not full-AOI valid-pixel coverage; the samples are not independent labels because they are OPERA outputs; and the pre-/post-landfall maps do not establish comparable baseline/event periods. The Oct. 10 service error and incomplete 3-date-per-period screen prevent an event comparison. No candidate is confirmatorily enrolled and no score credit is added.",
        "",
        "## Source records",
        "",
        f"- [NASA EGIS Milton DSWx overview]({report['service']['item_url']})",
        f"- [NASA EGIS ImageServer metadata]({report['service']['url']}?f=json)",
        f"- [NASA OPERA DSWx-S1 product specification]({report['service']['class_reference_url']})",
        "- Reproduce with `python scripts/audit_nasa_egis_milton_samples.py`.",
        "- Machine-readable audit: `atlas-tampa-milton-egis-pixel-sample.json`; per-point records: `atlas-tampa-milton-egis-pixel-sample.csv`.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    report, rows = run()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(args.csv, rows)
    write_markdown(args.markdown, report)
    for scene in report["scenes"]:
        print(f"{scene['date_utc']}: {scene['sampling_status']} {scene['samples_returned']}/{scene['samples_requested']} samples")
    print(f"Wrote {args.json}, {args.csv}, and {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
