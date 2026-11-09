"""Check public catalog and file-access status for the Jakarta Sinking City deposit."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


CONCEPT_API = "https://zenodo.org/api/records/15806063"
DATASET_PAGE = "https://kclpure.kcl.ac.uk/portal/en/datasets/hack4resilient-jakarta-2025-sinking-city/"


def summarize_record(record: dict, raw: bytes, file_endpoint_status: int | None) -> dict:
    metadata = record.get("metadata") or {}
    access_right = metadata.get("access_right", "unknown")
    exposed_files = record.get("files") or []
    downloadable = access_right == "open" and file_endpoint_status == 200 and bool(exposed_files)
    if downloadable:
        access_state = "open_candidate"
    elif access_right == "restricted":
        access_state = "restricted_unavailable_without_grant"
    elif access_right == "open":
        access_state = "open_record_but_files_unavailable_or_unlisted"
    else:
        access_state = "access_state_unknown_or_unavailable"
    description = metadata.get("description") or ""
    return {
        "audit": "ATLAS Jakarta Sinking City reference-data access screen",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "catalog": {
            "dataset_page": DATASET_PAGE,
            "concept_api": CONCEPT_API,
            "latest_record_id": record.get("id"),
            "concept_record_id": record.get("conceptrecid"),
            "doi": metadata.get("doi"),
            "title": metadata.get("title"),
            "publication_date": metadata.get("publication_date"),
            "access_right": access_right,
            "license_id": (metadata.get("license") or {}).get("id"),
            "public_api_file_count": len(exposed_files),
            "public_file_endpoint_http_status": file_endpoint_status,
            "record_response_sha256": hashlib.sha256(raw).hexdigest(),
            "description_sha256": hashlib.sha256(description.encode("utf-8")).hexdigest(),
        },
        "dataset_page_describes": {
            "flood_depth_points": "BPBD DKI Jakarta flood-depth points, stated coverage 2016–2024",
            "binary_flood_rasters": "flood/no-flood rasters attributed to Copernicus SAR, stated coverage 2019–2023",
            "administrative_depth": "kelurahan-level flood depth, stated coverage 2015–2024 excluding 2021 and 2022",
        },
        "classification": {
            "access_state": access_state,
            "reference_lead": True,
            "confirmatory_eligible": False,
            "score_credit": 0,
            "limits": [
                "Catalog descriptions do not prove the data's geometry, timestamps, completeness, or quality.",
                "The SAR-attributed binary raster is not independent validation of Sentinel-1-derived OPERA unless source lineage proves otherwise.",
                "BPBD point/depth data may be useful only after authorized access, fixed-AOI coverage review, event-time matching, and independent-label QA.",
                "A stated CC-BY-4.0 license does not override the record's restricted access status.",
            ],
            "next_steps": [
                "Request authorized access and data dictionary from the deposit custodians.",
                "If access is granted, checksum and inventory each file; verify geometry, event timestamps, CRS, completeness, and per-site coverage.",
                "Keep BPBD field/administrative observations separate from Copernicus SAR-derived rasters until lineage and independence are established.",
            ],
        },
    }


def _get(url: str) -> tuple[bytes | None, int]:
    request = Request(url, headers={"User-Agent": "ATLAS-research-source-audit/1.0"})
    try:
        with urlopen(request, timeout=30) as response:
            return response.read(), response.status
    except HTTPError as error:
        return error.read(), error.code


def run_audit() -> dict:
    raw, status = _get(CONCEPT_API)
    if status != 200 or raw is None:
        raise RuntimeError(f"Zenodo catalog request returned HTTP {status}")
    record = json.loads(raw)
    links = record.get("links") or {}
    files_url = links.get("files")
    if not files_url:
        raise RuntimeError("Zenodo record did not provide a files endpoint")
    _, file_status = _get(files_url)
    return summarize_record(record, raw, file_status)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("outputs/atlas-jakarta-zenodo-data-access-audit-2026-11-04.json"))
    args = parser.parse_args()
    result = run_audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["catalog"], sort_keys=True))


if __name__ == "__main__":
    main()
