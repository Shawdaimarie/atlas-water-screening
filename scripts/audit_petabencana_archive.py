#!/usr/bin/env python3
"""Screen PetaBencana's Jakarta flooded-area archive for date-window integrity.

This is a discovery-source check only. PetaBencana returns neighborhood area
IDs and maximum reported flood states; it does not provide pixel truth. The
audit compares each returned ``last_updated`` timestamp with the requested
window and records response hashes so stale fallback data are visible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://data.petabencana.id/floods/archive"
WINDOWS = (
    {
        "label": "Jakarta March 2025 flood window",
        "start": "2025-03-01T00:00:00+0700",
        "end": "2025-03-08T23:00:00+0700",
    },
    {
        "label": "January 2020 positive-control window",
        "start": "2020-01-01T00:00:00+0700",
        "end": "2020-01-08T23:00:00+0700",
    },
    {
        "label": "October 2022 stale-control window",
        "start": "2022-10-01T00:00:00+0700",
        "end": "2022-10-15T23:00:00+0700",
    },
    {
        "label": "January 2026 current-window check",
        "start": "2026-01-01T00:00:00+0700",
        "end": "2026-01-08T23:00:00+0700",
    },
)


def summarize_window(window: dict, payload: dict, response_sha256: str) -> dict:
    rows = payload.get("result")
    if payload.get("statusCode") != 200 or not isinstance(rows, list):
        raise ValueError("PetaBencana returned an unexpected response envelope")
    start_date = date.fromisoformat(window["start"][:10])
    end_date = date.fromisoformat(window["end"][:10])
    updated_dates = []
    for row in rows:
        timestamp = row.get("last_updated")
        if not isinstance(timestamp, str):
            raise ValueError("Archive row is missing a string last_updated field")
        updated_dates.append(datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date())
    in_window = [d for d in updated_dates if start_date <= d <= end_date]
    if not rows:
        outcome = "empty"
    elif in_window:
        outcome = "has_returned_updates_within_requested_window"
    else:
        outcome = "returned_rows_are_outside_requested_window"
    return {
        "label": window["label"],
        "request_start": window["start"],
        "request_end": window["end"],
        "response_sha256": response_sha256,
        "returned_area_count": len(rows),
        "returned_distinct_area_id_count": len({str(row.get("area_id", "")) for row in rows}),
        "returned_area_id_sample": sorted({str(row.get("area_id", "")) for row in rows})[:10],
        "returned_update_date_min": min(updated_dates).isoformat() if updated_dates else None,
        "returned_update_date_max": max(updated_dates).isoformat() if updated_dates else None,
        "returned_rows_with_update_date_in_requested_window": len(in_window),
        "screening_outcome": outcome,
        "maximum_reported_state": max((row.get("max_state", 0) for row in rows), default=None),
    }


def fetch_window(window: dict) -> dict:
    url = f"{API_URL}?{urlencode({'start': window['start'], 'end': window['end']})}"
    request = Request(url, headers={"User-Agent": "ATLAS-reference-source-screen/1.0"})
    with urlopen(request, timeout=30) as response:
        raw = response.read()
    payload = json.loads(raw)
    result = summarize_window(window, payload, hashlib.sha256(raw).hexdigest())
    result["request_url"] = url
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/atlas-petabencana-archive-screen.json"),
    )
    args = parser.parse_args()
    results = [fetch_window(window) for window in WINDOWS]
    output = {
        "audit": "PetaBencana Jakarta archive date-window integrity screen",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "api": API_URL,
        "documentation": "https://docs.petabencana.id/master-1/routes/flooded-area-archive",
        "results": results,
        "interpretation_limits": [
            "The archive returns reported neighborhood area IDs and maximum flood-state values, not water-pixel labels.",
            "Rows whose last_updated timestamps fall outside the requested period are treated as stale or anomalous and cannot establish a matched event reference.",
            "A date-window response does not establish fixed-AOI overlap, independent label quality, or confirmatory sampling adequacy.",
        ],
        "score_credit": 0,
        "confirmatory_enrollment_eligible": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps([
        {key: value for key, value in result.items() if key != "request_url"}
        for result in results
    ], indent=2))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
