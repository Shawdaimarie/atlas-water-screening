#!/usr/bin/env python3
"""Screen public OPERA DSWx-HLS EGIS acquisition metadata across the 8+8 AOIs.

This is a metadata-only, cross-sensor availability screen. It does not download
rasters, assess pixel QA, confirm floods, or create independent reference labels.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
SERVICE_URL = (
    "https://gis.earthdata.nasa.gov/portal/rest/services/"
    "C2617126679-POCLOUD/OPERA_L3_DSWX-HLS_V1_B01_WTR/ImageServer"
)
SERVICE_GUIDE = "https://podaac.github.io/tutorials/notebooks/GIS/OPERA_EGIS_access.html"
SCIENCE_WORKFLOW = (
    "https://podaac.github.io/tutorials/notebooks/GIS/"
    "OPERA_EGIS_access_Python_LakeMead_timeseries.html"
)
USER_AGENT = "ATLAS-OPERA-HLS-coverage-screen/1.0"
FIELDS = "objectid,datetime,name,cloud_coverage,spacecraft_name,tileid,processingdate"


def epoch_ms(date_text: str) -> int:
    """Convert a UTC date or ISO timestamp to epoch milliseconds."""
    value = dt.datetime.fromisoformat(date_text.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return int(value.astimezone(dt.timezone.utc).timestamp() * 1000)


def _get_json(session: requests.Session, url: str, params: dict[str, Any], timeout: int) -> dict[str, Any]:
    response = session.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        error = payload["error"]
        raise RuntimeError(f"EGIS REST error {error.get('code')}: {error.get('message')}")
    return payload


def query_area(
    session: requests.Session,
    area: dict[str, Any],
    start_date: str,
    end_date_exclusive: str,
    timeout: int = 90,
    page_size: int = 1000,
) -> dict[str, Any]:
    """Fetch primary scene metadata intersecting one exact registered AOI box."""
    west, south, east, north = [float(value) for value in area["aoi_bbox_wgs84"].split(",")]
    geometry = {
        "xmin": west,
        "ymin": south,
        "xmax": east,
        "ymax": north,
        "spatialReference": {"wkid": 4326},
    }
    params: dict[str, Any] = {
        "f": "json",
        "where": "category=1",
        "geometry": json.dumps(geometry, separators=(",", ":")),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "time": f"{epoch_ms(start_date)},{epoch_ms(end_date_exclusive)}",
        "outFields": FIELDS,
        "returnGeometry": "false",
        "orderByFields": "datetime ASC,objectid ASC",
    }

    features: list[dict[str, Any]] = []
    offset = 0
    while True:
        page = _get_json(
            session,
            f"{SERVICE_URL}/query",
            {**params, "resultOffset": offset, "resultRecordCount": page_size},
            timeout,
        )
        rows = page.get("features", [])
        features.extend(rows)
        if not page.get("exceededTransferLimit", False) or not rows:
            break
        offset += len(rows)

    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in features:
        attrs = feature.get("attributes", {})
        timestamp = attrs.get("datetime")
        if timestamp is None:
            continue
        date = dt.datetime.fromtimestamp(timestamp / 1000, tz=dt.timezone.utc).date().isoformat()
        by_date[date].append(attrs)

    acquisitions = []
    for date, records in sorted(by_date.items()):
        cloud_values = [
            int(record["cloud_coverage"])
            for record in records
            if isinstance(record.get("cloud_coverage"), (int, float))
        ]
        acquisitions.append(
            {
                "date_utc": date,
                "scene_records": len(records),
                "spacecraft": sorted({str(r["spacecraft_name"]) for r in records if r.get("spacecraft_name")}),
                "tile_ids": sorted({str(r["tileid"]) for r in records if r.get("tileid")}),
                "scene_names": sorted({str(r["name"]) for r in records if r.get("name")}),
                "scene_cloud_coverage_percent_min": min(cloud_values) if cloud_values else None,
                "scene_cloud_coverage_percent_max": max(cloud_values) if cloud_values else None,
            }
        )

    return {
        "region": area["region"],
        "city": area["city"],
        "aoi_bbox_wgs84": area["aoi_bbox_wgs84"],
        "primary_scene_records": len(features),
        "distinct_acquisition_dates": len(acquisitions),
        "first_acquisition_date": acquisitions[0]["date_utc"] if acquisitions else None,
        "last_acquisition_date": acquisitions[-1]["date_utc"] if acquisitions else None,
        "acquisitions": acquisitions,
        "status": "metadata_screen_only",
    }


def build_audit(
    register_path: Path,
    start_date: str = "2024-09-01",
    end_date_exclusive: str = "2026-11-03",
    timeout: int = 90,
) -> dict[str, Any]:
    """Run the common EGIS metadata screen for all 16 registered study areas."""
    start_ms, end_ms = epoch_ms(start_date), epoch_ms(end_date_exclusive)
    if end_ms <= start_ms:
        raise ValueError("end_date_exclusive must be later than start_date")

    register = json.loads(register_path.read_text(encoding="utf-8"))
    areas = register.get("results", [])
    if len(areas) != 16:
        raise ValueError(f"expected 16 registered AOIs, found {len(areas)}")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    service_metadata = _get_json(session, SERVICE_URL, {"f": "json"}, timeout)
    if service_metadata.get("error"):
        raise RuntimeError("EGIS service metadata returned an error")

    results = []
    errors = []
    for area in areas:
        try:
            results.append(query_area(session, area, start_date, end_date_exclusive, timeout))
        except Exception as exc:  # preserve each area failure; do not silently treat it as zero coverage
            errors.append({
                "region": area.get("region"),
                "city": area.get("city"),
                "error_type": type(exc).__name__,
                "error": str(exc)[:300],
            })
    results.sort(key=lambda row: (row["region"], row["city"]))
    errors.sort(key=lambda row: (str(row["region"]), str(row["city"])))
    successful = len(results)
    return {
        "audit_id": "atlas-opera-dswx-hls-egis-availability-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "product": "OPERA_L3_DSWX-HLS_V1_B01_WTR",
        "source_service_url": SERVICE_URL,
        "source_guide_url": SERVICE_GUIDE,
        "source_science_workflow_url": SCIENCE_WORKFLOW,
        "source_service_metadata": {
            "current_version": service_metadata.get("currentVersion"),
            "pixel_size_x_m": service_metadata.get("pixelSizeX"),
            "pixel_size_y_m": service_metadata.get("pixelSizeY"),
            "time_extent_epoch_ms": service_metadata.get("timeInfo", {}).get("timeExtent"),
            "service_description": service_metadata.get("serviceDescription"),
        },
        "query": {
            "start_date_utc_inclusive": start_date,
            "end_date_utc_exclusive": end_date_exclusive,
            "time_start_epoch_ms": start_ms,
            "time_end_epoch_ms": end_ms,
            "spatial_filter": "Exact registered AOI WGS84 bounding box; esriSpatialRelIntersects",
            "catalog_filter": "category=1 (Primary scene records)",
            "fields": FIELDS,
            "authentication": "No Earthdata credentials supplied; public EGIS REST catalog endpoint",
            "rasters_downloaded": False,
        },
        "areas_expected": 16,
        "areas_succeeded": successful,
        "areas_failed": len(errors),
        "all_area_queries_succeeded": successful == 16 and not errors,
        "areas_with_at_least_90_metadata_dates": sum(
            row["distinct_acquisition_dates"] >= 90 for row in results
        ),
        "total_scene_records": sum(row["primary_scene_records"] for row in results),
        "total_area_date_pairs": sum(row["distinct_acquisition_dates"] for row in results),
        "interpretation_limits": [
            "The screen counts primary EGIS catalog records and unique acquisition dates, not pixels passing QA.",
            "Per-scene cloud_coverage metadata is not an AOI valid-pixel fraction.",
            "OPERA DSWx-HLS uses optical HLS inputs and is a cross-sensor comparison stream relative to DSWx-S1; it is not independent field truth and is not a substitute for the target DSWx-S1 product.",
            "No event is confirmed by this archive screen. Event timing, event/baseline balance, raster QA, licensing/governance, and independent labels remain separate gates.",
        ],
        "areas": results,
        "errors": errors,
    }


def render_markdown(audit: dict[str, Any], json_path: Path) -> str:
    """Render a compact, traceable Markdown summary of the audit."""
    lines = [
        "# OPERA DSWx-HLS EGIS 8+8 acquisition-availability screen",
        "",
        f"**Checked:** {audit['generated_at_utc']}  ",
        f"**Window:** [{audit['query']['start_date_utc_inclusive']}, {audit['query']['end_date_utc_exclusive']}) UTC  ",
        f"**Areas queried:** {audit['areas_succeeded']}/16; **areas with at least 90 metadata dates:** {audit['areas_with_at_least_90_metadata_dates']}/16  ",
        f"**Primary scene records:** {audit['total_scene_records']}; **area/date pairs:** {audit['total_area_date_pairs']}",
        "",
        "This query uses the same fixed WGS84 AOI boxes as the OPERA DSWx-S1 metadata screen and NASA's public EGIS ImageServer for the optical OPERA DSWx-HLS `B01_WTR` layer.",
        "",
        "| Region | Area | Primary scene records | Unique acquisition dates | First date | Last date |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in audit["areas"]:
        lines.append(
            f"| {row['region']} | {row['city']} | {row['primary_scene_records']} | "
            f"{row['distinct_acquisition_dates']} | {row['first_acquisition_date'] or '—'} | "
            f"{row['last_acquisition_date'] or '—'} |"
        )
    lines.extend(["", "## Interpretation and limits", ""])
    lines.extend(f"- {note}" for note in audit["interpretation_limits"])
    lines.extend([
        "- Scene-level cloud metadata may help prioritize pixel review but is not a substitute for measuring valid-pixel coverage in the fixed AOI.",
        "- This is not an event-selection result, scientific validation, or confirmatory enrollment. No score points follow from discovery metadata alone.",
        "",
        f"Machine-readable results: [{json_path.name}]({json_path.name}).",
        "",
        f"Reproduce with `python scripts/audit_opera_hls_egis_coverage.py`. Source: [NASA PO.DAAC EGIS guide]({SERVICE_GUIDE}) and [official EGIS time-series workflow]({SCIENCE_WORKFLOW}).",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=ROOT / "data/study_area_register.json")
    parser.add_argument("--start-date", default="2024-09-01")
    parser.add_argument("--end-date-exclusive", default="2026-11-03")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--output-json", type=Path, default=ROOT / "outputs/atlas-opera-hls-egis-coverage-audit.json")
    parser.add_argument("--output-markdown", type=Path, default=ROOT / "outputs/atlas-opera-hls-egis-coverage-audit.md")
    args = parser.parse_args()

    audit = build_audit(args.register, args.start_date, args.end_date_exclusive, args.timeout)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(args.output_json.read_bytes()).hexdigest()
    markdown = render_markdown(audit, args.output_json)
    markdown += f"\nJSON SHA-256: `{digest}`.\n"
    args.output_markdown.write_text(markdown, encoding="utf-8")
    print(json.dumps({
        "output_json": str(args.output_json),
        "output_markdown": str(args.output_markdown),
        "areas_expected": audit["areas_expected"],
        "areas_succeeded": audit["areas_succeeded"],
        "areas_failed": audit["areas_failed"],
        "areas_with_at_least_90_metadata_dates": audit["areas_with_at_least_90_metadata_dates"],
        "total_scene_records": audit["total_scene_records"],
        "all_area_queries_succeeded": audit["all_area_queries_succeeded"],
        "rasters_downloaded": False,
        "sha256": digest,
    }, indent=2))
    return 0 if audit["all_area_queries_succeeded"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
