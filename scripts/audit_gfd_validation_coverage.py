#!/usr/bin/env python3
"""Reproduce GFD/Landsat validation-point coverage against ATLAS site AOIs."""

from __future__ import annotations

import argparse
import csv
import io
import json
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPOSITORY = "https://github.com/cloudtostreet/MODIS_GlobalFloodDatabase"
SOURCE_COMMIT = "0d20b91d124b5a9987d40392b5e3463d78f1f894"
RAW_BASE = (
    "https://raw.githubusercontent.com/cloudtostreet/"
    f"MODIS_GlobalFloodDatabase/{SOURCE_COMMIT}/data/"
)
FILES = {
    "validation_points": "gfd_validation_points_2018_12_17.csv",
    "quality_control_database": "gfd_qcdatabase_2019_08_01.csv",
    "validation_metrics": "gfd_validation_metrics.csv",
}


def read_csv(filename: str) -> list[dict[str, str]]:
    request = urllib.request.Request(
        RAW_BASE + filename,
        headers={"User-Agent": "ATLAS-reference-coverage-audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = response.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(payload)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--areas",
        type=Path,
        default=Path("data/study_area_register.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/atlas-global-flood-db-validation-audit.json"),
    )
    args = parser.parse_args()

    area_data = json.loads(args.areas.read_text(encoding="utf-8"))
    areas = area_data["results"]
    points = read_csv(FILES["validation_points"])
    event_rows = read_csv(FILES["quality_control_database"])
    metrics = read_csv(FILES["validation_metrics"])

    labels = Counter(row.get("validation", "") for row in points)
    event_by_id = {row["ID"]: row for row in event_rows}
    counts: dict[str, int] = {}
    matches_by_area: dict[str, list[dict[str, str]]] = {}
    for area in areas:
        xmin, ymin, xmax, ymax = map(
            float, area["aoi_bbox_wgs84"].split(",")
        )
        key = f"{area['region']}/{area['city']}"
        matches = [
            row
            for row in points
            if xmin <= float(row["point_lon"]) <= xmax
            and ymin <= float(row["point_lat"]) <= ymax
        ]
        counts[key] = len(matches)
        matches_by_area[key] = matches

    sacramento_key = "United States/Sacramento"
    sacramento_points = matches_by_area.get(sacramento_key, [])
    sacramento_labels = Counter(
        row.get("validation", "") for row in sacramento_points
    )
    dfo_ids = sorted({row.get("dfoID", "") for row in sacramento_points})
    candidate_id = dfo_ids[0] if len(dfo_ids) == 1 else None
    event = event_by_id.get(candidate_id or "", {})
    point_dates = sorted(
        {
            datetime.fromtimestamp(
                float(row["date"]) / 1000, tz=timezone.utc
            ).date().isoformat()
            for row in sacramento_points
            if row.get("date")
        }
    )
    metric_rows = [row for row in metrics if row.get("Flood") == candidate_id]
    metric_summary = [
        {
            "method": row.get("Method"),
            "overall_accuracy": row.get("overall_accuracy"),
            "precision": row.get("precision"),
            "recall": row.get("recall"),
            "counts": row.get("counts"),
        }
        for row in metric_rows
    ]

    def iso_date(value: str) -> str | None:
        if not value:
            return None
        return datetime.strptime(value, "%m/%d/%Y").date().isoformat()

    report = {
        "retrieved_utc_date": datetime.now(timezone.utc).date().isoformat(),
        "source_repository": REPOSITORY,
        "source_commit": SOURCE_COMMIT,
        "source_files": {
            key: RAW_BASE + filename for key, filename in FILES.items()
        },
        "registered_aoi_rule": (
            "Exact WGS84 point-in-rectangle check using each registered "
            "25 km x 25 km AOI bounds."
        ),
        "dataset_totals": {
            "validation_point_records": len(points),
            "distinct_dfo_events": len({row.get("dfoID", "") for row in points}),
            "label_values": dict(labels),
        },
        "area_match_counts": counts,
        "sacramento_candidate": {
            "point_count": len(sacramento_points),
            "dfo_event_id": candidate_id,
            "point_reference_labels": dict(sacramento_labels),
            "reference_imagery_dates_utc": point_dates,
            "cataloged_event_interval": {
                "start": iso_date(event.get("Began", "")),
                "end": iso_date(event.get("Ended", "")),
            }
            if event
            else None,
            "reported_event_location": {
                "country": event.get("Country"),
                "longitude": event.get("long"),
                "latitude": event.get("lat"),
                "cause": event.get("MainCause"),
                "validation_source": event.get("Validation"),
            }
            if event
            else None,
            "event_level_published_metrics": metric_summary,
            "assessment": (
                "Not eligible as contemporaneous event validation: all "
                "matched point references are dated more than a year after "
                "the reported flood interval, and their count is below the "
                "study's adequate site/event sampling requirement. Retain "
                "as a discovery lead only; do not count as a passed site or "
                "ATLAS accuracy result."
            ),
        },
        "limits": [
            "The Global Flood Database is a MODIS flood-event archive from "
            "2000-2018; its project repository describes validation points "
            "as analyst interpretations of Landsat imagery.",
            "Point-in-AOI coverage is not equivalent to independent site "
            "validation: temporal match, label protocol, geolocation "
            "uncertainty, spatial sampling adequacy, image provenance, and "
            "held-out status must all pass.",
            "No registered study area currently has qualifying "
            "contemporaneous independent reference labels from these files.",
            "The published event-level metrics summarize larger samples and "
            "cannot be attributed to a study AOI or ATLAS.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {args.output}: {len(points)} points, "
        f"{report['dataset_totals']['distinct_dfo_events']} events, "
        f"{sum(value > 0 for value in counts.values())}/{len(counts)} AOIs with any point."
    )


if __name__ == "__main__":
    main()
