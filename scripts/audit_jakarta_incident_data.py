"""Audit the official Jakarta 2024 administrative flood incident extract.

The source CSV is not bundled because its reuse terms are unresolved. Download
it from the official resource URL in the report, verify its hash, then pass the
local file to this script.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


DATASET_PAGE = "https://data.go.id/dataset/dataset/data-kejadian-bencana-banjir-tahun-2024"
PORTAL_PAGE = "https://satudata.jakarta.go.id/open-data/detail/data-kejadian-bencana-banjir-tahun-2024"
CSV_RESOURCE = (
    "https://satudata.jakarta.go.id/backend/restapi/v1/datasets/export/"
    "ceaef86431726d799e14c6b9d5f60f49/"
    "data-kejadian-bencana-banjir-tahun-2024.csv"
)
REQUIRED_COLUMNS = {
    "periode_data",
    "triwulan",
    "bulan",
    "wilayah",
    "kecamatan",
    "kelurahan",
    "jumlah_rata_rata_ketinggian_air",
    "jumlah_rw_terdampak",
    "jumlah_kk_terdampak",
    "jumlah_jiwa_terdampak",
    "jumlah_kejadian",
}


def audit_csv(path: Path) -> dict:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = [
            {key.lstrip("\ufeff"): (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(source)
        ]
    if not rows:
        raise ValueError("Jakarta source extract is empty")
    missing_columns = REQUIRED_COLUMNS - set(rows[0])
    if missing_columns:
        raise ValueError(f"Jakarta source extract is missing columns: {sorted(missing_columns)}")
    if any(not re.fullmatch(r"2024(03|06|09|12)", row["periode_data"]) for row in rows):
        raise ValueError("Unexpected Jakarta reporting period; re-review before accepting this extract")

    quarter_rows = Counter(row["periode_data"] for row in rows)
    area_month_keys = Counter(
        (row["periode_data"], row["kecamatan"], row["kelurahan"]) for row in rows
    )
    event_count_sum = sum(int(row["jumlah_kejadian"] or "0") for row in rows)
    has_coordinate_fields = any(
        name.lower() in {"lat", "lon", "latitude", "longitude", "geometry", "geom", "wkt"}
        for name in rows[0]
    )
    return {
        "audit": "ATLAS Jakarta 2024 administrative flood incident source screen",
        "source": {
            "publisher": "Badan Penanggulangan Bencana Daerah Provinsi DKI Jakarta (BPBD DKI Jakarta)",
            "dataset_title": "Data Kejadian Bencana Banjir Tahun 2024",
            "dataset_id": "01f3d0d2-c2d3-401e-9af5-f053ba0e93f6",
            "csv_resource_id": "c74119df-4e30-4873-8ef0-b2a8222566fd",
            "xlsx_resource_id": "1ed4f242-78f0-430a-bdd7-b5b443cae387",
            "dataset_page": DATASET_PAGE,
            "official_portal_page": PORTAL_PAGE,
            "csv_resource_url": CSV_RESOURCE,
            "dataset_modified": "2026-09-03",
            "resource_modified": "2026-06-03",
            "retrieved_date": "2026-11-03",
            "raw_csv_sha256": hashlib.sha256(raw).hexdigest(),
        },
        "observed_data": {
            "csv_rows": len(rows),
            "quarterly_extracts": dict(sorted(quarter_rows.items())),
            "distinct_reporting_periods": len(quarter_rows),
            "distinct_administrative_units": len(
                {(row["kecamatan"], row["kelurahan"]) for row in rows}
            ),
            "distinct_kecamatan": len({row["kecamatan"] for row in rows}),
            "distinct_kelurahan": len({row["kelurahan"] for row in rows}),
            "unique_period_kecamatan_kelurahan_keys": len(area_month_keys),
            "period_unit_keys_with_multiple_rows": sum(count > 1 for count in area_month_keys.values()),
            "event_count_sum_across_source_rows": event_count_sum,
            "event_count_sum_is_distinct_regional_events": False,
            "event_months_present": sorted({int(row["bulan"]) for row in rows}),
            "coordinate_or_geometry_field_present": has_coordinate_fields,
            "day_or_time_of_event_field_present": any(
                name.lower() in {"date", "event_date", "tanggal", "datetime", "timestamp", "time"}
                for name in rows[0]
            ),
            "reported_water_depth_values_are_qualitative_ranges": True,
        },
        "classification": {
            "lead_type": "Administrative incident record; nonspatial and coarsely timed.",
            "can_support": "Evidence that flood incidents were administratively reported in Jakarta districts/villages and months during 2024, subject to source-method review.",
            "cannot_support": [
                "Pixel-level flood extent or water-class validation.",
                "Event-day matching to OPERA or Sentinel-1 scenes.",
                "Fixed-AOI overlap until official administrative boundaries are crosswalked.",
                "Comparable label coverage across all 16 study areas.",
                "Distinct citywide event totals by summing locality-level rows.",
                "ATLAS customer demand or measured risk reduction.",
            ],
            "confirmatory_enrollment_eligible": False,
            "score_credit": 0,
        },
        "reuse_and_quality_gates": {
            "portal_describes_dataset_as_open": True,
            "portal_notice_says_sdi_principles_are_still_being_fulfilled": True,
            "package_license_title": None,
            "package_isopen_flag": False,
            "explicit_reuse_license_verified": False,
            "raw_source_redistributed": False,
            "raw_data_quality_and_collection_method_independently_reviewed": False,
            "fixed_aoi_boundary_overlap_verified": False,
            "next_steps": [
                "Request the data dictionary, incident aggregation method, and written reuse/commercial terms from BPBD DKI Jakarta.",
                "Obtain a versioned official kelurahan boundary layer and perform a preregistered fixed-AOI overlay.",
                "Obtain event-day or finer timestamped records before attempting scene matching.",
                "Keep this source separate from pixel-reference labels unless independent spatial observations are provided.",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path, help="Locally downloaded official CSV resource")
    parser.add_argument("--output", type=Path, default=Path("outputs/atlas-jakarta-incident-data-audit.json"))
    args = parser.parse_args()
    audit = audit_csv(args.csv_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps(audit["observed_data"], sort_keys=True))


if __name__ == "__main__":
    main()
