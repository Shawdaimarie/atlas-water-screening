#!/usr/bin/env python3
"""Check CMR discovery and unauthenticated access to one OPERA BWTR asset per AOI.

This is an access-readiness audit only. It does not download raster data, assess
pixel QA, identify a flood event, or test independent reference coverage.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
USER_AGENT = "ATLAS-OPERA-access-readiness-audit/1.0"


def fetch_area(area: dict[str, Any], timeout: int = 30) -> dict[str, Any]:
    """Discover one first-date granule, then HEAD its binary-water asset without auth."""
    date = area["first_acquisition_date"]
    day = dt.date.fromisoformat(date)
    start = dt.datetime.combine(day, dt.time.min, tzinfo=dt.timezone.utc)
    end = dt.datetime.combine(day, dt.time.max, tzinfo=dt.timezone.utc)
    params = {
        "short_name": area["collection"],
        "temporal": f"{start.isoformat().replace('+00:00', 'Z')},{end.isoformat().replace('+00:00', 'Z')}",
        "bounding_box": area["aoi_bbox_wgs84"],
        "page_size": "20",
        "sort_key[]": "start_date",
    }
    request = urllib.request.Request(
        f"{CMR_URL}?{urllib.parse.urlencode(params, doseq=True)}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except Exception as exc:  # retain per-area failures in the audit
        return {"region": area["region"], "city": area["city"], "date": date,
                "cmr_status": "error", "error_type": type(exc).__name__,
                "error": str(exc)[:240]}

    entries = payload.get("feed", {}).get("entry", [])
    for entry in entries:
        asset = next((link.get("href") for link in entry.get("links", [])
                      if link.get("href", "").endswith("_B02_BWTR.tif")), None)
        if not asset:
            continue
        head = urllib.request.Request(asset, method="HEAD", headers={"User-Agent": USER_AGENT})
        error_type = None
        try:
            with urllib.request.urlopen(head, timeout=timeout) as response:
                status = response.status
                length = response.headers.get("Content-Length")
        except urllib.error.HTTPError as exc:
            status, length = exc.code, exc.headers.get("Content-Length") if exc.headers else None
        except Exception as exc:
            status, length = None, None
            error_type = type(exc).__name__
        else:
            error_type = None
        return {
            "region": area["region"], "city": area["city"], "date": date,
            "cmr_status": "found", "cmr_entry_count": len(entries),
            "granule_id": entry.get("producer_granule_id"),
            "bwtr_asset_url": asset, "asset_layer": "B02_BWTR", "unauthenticated_head_status": status,
            "content_length": length, "head_error_type": error_type,
            "data_downloaded": False,
        }
    return {"region": area["region"], "city": area["city"], "date": date,
            "cmr_status": "no_wtr_asset", "cmr_entry_count": len(entries),
            "data_downloaded": False}


def build_audit(register: Path, workers: int = 4) -> dict[str, Any]:
    source = json.loads(register.read_text())
    areas = source["results"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(fetch_area, areas))
    rows.sort(key=lambda row: (row["region"], row["city"]))
    status_counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("unauthenticated_head_status", row["cmr_status"]))
        status_counts[key] = status_counts.get(key, 0) + 1
    return {
        "audit_id": "atlas-opera-earthdata-asset-access-v2",
        "created_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "collection": "OPERA_L3_DSWX-S1_V1",
        "method": "For each registered AOI, query public CMR metadata on the first registered acquisition date and HEAD one B02_BWTR asset without credentials.",
        "areas_tested": len(rows), "status_counts": status_counts,
        "interpretation_limit": "CMR discovery does not imply raster access. HTTP status checks are not pixel QA, event verification, or independent labels. No raster bytes are downloaded.",
        "areas": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=ROOT / "data/study_area_register.json")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/atlas-opera-earthdata-access-audit.json")
    args = parser.parse_args()
    audit = build_audit(args.register)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "areas_tested": audit["areas_tested"],
                      "status_counts": audit["status_counts"], "data_downloaded": False}, indent=2))


if __name__ == "__main__":
    main()
