"""Screen WorldFloods v2 metadata footprints against the fixed ATLAS AOIs.

This is an event-footprint discovery audit only. It does not download or inspect
the 1.2 GB reference-mask archive and cannot establish label quality or accuracy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/study_area_register.json"
OUTPUT = ROOT / "outputs/atlas-worldfloods-v2-aoi-coverage-audit.json"
ZENODO_RECORD = "https://zenodo.org/records/8153514"
EXPECTED_RECORD_COUNT = 509


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    """Return whether WGS84 boxes (west, south, east, north) intersect."""
    aw, ass, ae, an = a
    bw, bs, be, bn = b
    return aw <= be and ae >= bw and ass <= bn and an >= bs


def bbox_from_register(raw: str) -> tuple[float, float, float, float]:
    west, south, east, north = map(float, raw.split(","))
    if not (-180 <= west <= east <= 180 and -90 <= south <= north <= 90):
        raise ValueError(f"Invalid WGS84 study-area bbox: {raw}")
    return west, south, east, north


def audit(metadata_zip: Path, register_path: Path = REGISTER) -> dict[str, Any]:
    register = json.loads(register_path.read_text())
    areas = register["results"]
    area_boxes = {
        (area["region"], area["city"]): bbox_from_register(area["aoi_bbox_wgs84"])
        for area in areas
    }
    candidates: dict[tuple[str, str], list[dict[str, Any]]] = {key: [] for key in area_boxes}
    record_count = 0
    with zipfile.ZipFile(metadata_zip) as archive:
        for name in sorted(archive.namelist()):
            if not name.lower().endswith(".json"):
                continue
            raw = json.loads(archive.read(name))
            bounds = raw.get("bounding box")
            if not isinstance(bounds, dict):
                raise ValueError(f"Metadata record lacks bounding box: {name}")
            record_box = (
                float(bounds["west"]), float(bounds["south"]),
                float(bounds["east"]), float(bounds["north"]),
            )
            if not (-180 <= record_box[0] <= record_box[2] <= 180 and -90 <= record_box[1] <= record_box[3] <= 90):
                raise ValueError(f"Invalid WGS84 record bbox: {name}")
            record_count += 1
            for key, area_box in area_boxes.items():
                if intersects(record_box, area_box):
                    candidates[key].append({
                        "metadata_file": name,
                        "event_id": raw.get("event id"),
                        "event_date": raw.get("satellite date"),
                        "source": raw.get("source"),
                        "event_type": raw.get("event type"),
                        "bbox_wgs84": list(record_box),
                    })
    if record_count == 0:
        raise ValueError("No metadata records found in archive")
    matched = sum(bool(items) for items in candidates.values())
    return {
        "audit_id": "atlas-worldfloods-v2-aoi-coverage-audit",
        "source": {
            "title": "WorldFloods extended dataset (v2)",
            "record_url": ZENODO_RECORD,
            "doi": "10.5281/zenodo.8153514",
            "metadata_archive_filename": metadata_zip.name,
            "metadata_archive_sha256": sha256_file(metadata_zip),
            "metadata_records_screened": record_count,
            "expected_metadata_records": EXPECTED_RECORD_COUNT,
            "metadata_count_matches_record": record_count == EXPECTED_RECORD_COUNT,
            "published_map_period": "2016-2023",
            "mask_license": "CC BY-NC 4.0 (verify specific reuse terms before redistribution)",
        },
        "method": {
            "geometry": "Conservative bounding-box intersection between each metadata record bbox and each fixed ATLAS AOI bbox.",
            "exact_aoi_polygon_check": False,
            "rationale": "No bounding-box overlap proves no AOI polygon overlap; a positive bounding-box hit would require exact geometry follow-up.",
        },
        "summary": {
            "study_areas": len(areas),
            "areas_with_candidate_metadata_footprints": matched,
            "areas_without_candidate_metadata_footprints": len(areas) - matched,
            "metadata_records_intersecting_any_aoi": sum(len(items) for items in candidates.values()),
        },
        "areas": [
            {
                "region": key[0], "city": key[1],
                "aoi_bbox_wgs84": list(area_boxes[key]),
                "candidate_metadata_footprints": candidates[key],
                "candidate_count": len(candidates[key]),
                "screened_out_for_confirmatory_use": len(candidates[key]) == 0,
            }
            for key in area_boxes
        ],
        "interpretation_limits": [
            "The metadata screen does not inspect or verify raster masks, pixel labels, georegistration, or label uncertainty.",
            "The WorldFloods v2 archive covers 2016-2023, before the OPERA DSWx-S1 observation window used by ATLAS; matching geography alone would not provide contemporaneous validation.",
            "WorldFloods masks were manually curated from source flood maps and have non-commercial license terms; inspect source imagery lineage before calling any match independent of OPERA.",
            "A no-match result is specific to the fixed ATLAS AOIs and does not imply that a city or country has no flood-reference data.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-zip", type=Path, required=True)
    parser.add_argument("--register", type=Path, default=REGISTER)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = audit(args.metadata_zip, args.register)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2))
    print(f"Saved audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
