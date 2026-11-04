"""Audit a dated PUB flood-alert API response against the fixed Singapore AOI.

This is an exploratory event-lead screen. It does not label pixels or enroll a
site for confirmatory validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
API_URL = "https://api-open.data.gov.sg/v2/real-time/api/weather/flood-alerts"
DATASET_URL = "https://data.gov.sg/datasets/d_f1404e08587ce555b9ea3f565e2eb9a3/view"
AREA = "Singapore"
QUERY_DATE = "2025-05-22"
USER_AGENT = "ATLAS-open-data-research/1.0"


def point_in_bbox(latitude: float, longitude: float, bbox: list[float]) -> bool:
    """Check a [west,south,east,north] WGS84 box without buffering."""
    west, south, east, north = bbox
    return west <= longitude <= east and south <= latitude <= north


def audit_payload(
    payload: dict[str, Any],
    bbox: list[float],
    query_date: str,
    response_sha256: str,
    retrieved_at_utc: str,
) -> dict[str, Any]:
    records = payload.get("data", {}).get("records", [])
    reports = []
    for record in records:
        item = record.get("item", {})
        for reading in item.get("readings", []):
            if reading.get("event", "").casefold() != "flood":
                continue
            area = reading.get("area", {})
            circle = area.get("circle") or []
            try:
                latitude, longitude = float(circle[0]), float(circle[1])
            except (IndexError, TypeError, ValueError):
                latitude = longitude = None
            reports.append(
                {
                    "datetime": record.get("datetime"),
                    "updated_timestamp": record.get("updatedTimestamp"),
                    "headline": reading.get("headline"),
                    "description": reading.get("description"),
                    "certainty": reading.get("certainty"),
                    "status": item.get("status"),
                    "sender_name": reading.get("senderName"),
                    "area_description": area.get("areaDesc"),
                    "circle_as_reported": circle,
                    "center_inside_fixed_aoi": (
                        point_in_bbox(latitude, longitude, bbox)
                        if latitude is not None and longitude is not None
                        else None
                    ),
                }
            )
    intersecting = [r for r in reports if r["center_inside_fixed_aoi"] is True]
    return {
        "schema_version": 1,
        "audit_id": "singapore-pub-flood-alert-2025-05-22",
        "status": "exploratory_event_lead_screen",
        "area": AREA,
        "query_date": query_date,
        "retrieved_at_utc": retrieved_at_utc,
        "source": {
            "dataset": "Flood Alerts across Singapore",
            "agency": "PUB, Singapore's national water agency",
            "dataset_url": DATASET_URL,
            "api_url": API_URL,
            "license": "Singapore Open Data Licence (per data.gov.sg dataset page)",
            "response_sha256": response_sha256,
            "user_agent": USER_AGENT,
        },
        "fixed_aoi_bbox_wgs84": bbox,
        "summary": {
            "returned_records": len(records),
            "flood_readings": len(reports),
            "flood_reading_centers_inside_aoi": len(intersecting),
            "observed_certainty_inside_aoi": sum(
                r.get("certainty") == "Observed" for r in intersecting
            ),
        },
        "reports": reports,
        "interpretation_limits": [
            "A point/circle in an official alert is an event-location lead, not a mapped flood extent.",
            "A dated alert does not provide a contemporaneous independent pixel-label sample or water-depth truth.",
            "This exploratory source query was performed after inspecting prior study evidence and is not confirmatory validation.",
            "The query screens only the requested date; it does not estimate event frequency or complete temporal coverage.",
            "No Singapore site becomes confirmatory-eligible from this alert alone.",
        ],
    }


def fetch_day(query_date: str) -> tuple[dict[str, Any], str]:
    query = urllib.parse.urlencode({"date": query_date})
    request = urllib.request.Request(
        f"{API_URL}?{query}", headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
    return json.loads(body), hashlib.sha256(body).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=QUERY_DATE)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs/atlas-singapore-pub-flood-alert-audit.json",
    )
    args = parser.parse_args()
    register = json.loads((ROOT / "data/study_area_register.json").read_text())
    area = next(r for r in register["results"] if r["city"] == AREA)
    west, south, east, north = map(float, area["aoi_bbox_wgs84"].split(","))
    payload, response_hash = fetch_day(args.date)
    report = audit_payload(
        payload,
        [west, south, east, north],
        args.date,
        response_hash,
        datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(
        f"Flood reports: {report['summary']['flood_readings']}; "
        f"centers inside fixed Singapore AOI: "
        f"{report['summary']['flood_reading_centers_inside_aoi']}"
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
