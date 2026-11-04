"""Screen USGS Global Flood Impacts Database events in the 16 fixed ATLAS AOIs.

Event points provide independent event/context leads only. They are not mapped
flood extents, pixel labels, or evidence that water occurred within the AOI.
The workbook is parsed with the Python standard library to keep the audit
reproducible without a spreadsheet dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import urllib.request
import zipfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from xml.etree.ElementTree import iterparse

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK_URL = (
    "https://www.sciencebase.gov/catalog/file/get/69e7e00db66b0164d0f7302d"
    "?f=__disk__c3%2F44%2Fd6%2Fc344d62cc5d115d408726fb52d9d459c6e1b5ed1"
)
SCIENCEBASE_ITEM_URL = "https://www.sciencebase.gov/catalog/item/69e7e00db66b0164d0f7302d"
DATA_GOV_URL = "https://catalog.data.gov/dataset/the-global-flood-impacts-database-gfid"
EXPECTED_MD5 = "3ea4849f12f98a58855d06b9f1b9a5bc"
USER_AGENT = "ATLAS-open-data-research/1.0"
COMMON_START = date(2024, 9, 1)
COMMON_END = date(2026, 11, 2)
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG_REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def _column_index(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference)
    if not letters:
        raise ValueError(f"Invalid Excel cell reference: {reference!r}")
    index = 0
    for char in letters.group(0):
        index = index * 26 + ord(char) - ord("A") + 1
    return index - 1


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    strings: list[str] = []
    with archive.open("xl/sharedStrings.xml") as source:
        for _, element in iterparse(source, events=("end",)):
            if element.tag == NS + "si":
                strings.append("".join(part.text or "" for part in element.iter(NS + "t")))
                element.clear()
    return strings


def _worksheet_path(archive: zipfile.ZipFile, sheet_name: str) -> str:
    from xml.etree import ElementTree as ET

    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}
    sheets = workbook.find(NS + "sheets")
    for sheet in sheets or []:
        if sheet.attrib.get("name") == sheet_name:
            target = targets[sheet.attrib[REL_NS + "id"]]
            return target.lstrip("/") if target.startswith("/") else "xl/" + target
    raise ValueError(f"Workbook has no {sheet_name!r} sheet")


def _cell_value(cell: Any, shared: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(part.text or "" for part in cell.iter(NS + "t"))
    value = cell.find(NS + "v")
    raw = value.text if value is not None and value.text is not None else ""
    if cell_type == "s" and raw:
        return shared[int(raw)]
    return raw


def iter_aggregated_rows(workbook_path: Path) -> Iterable[dict[str, str]]:
    """Yield rows from the GFID `Aggregated` sheet using streaming XML parsing."""
    with zipfile.ZipFile(workbook_path) as archive:
        shared = _shared_strings(archive)
        path = _worksheet_path(archive, "Aggregated")
        headers: list[str] | None = None
        with archive.open(path) as source:
            for _, row in iterparse(source, events=("end",)):
                if row.tag != NS + "row":
                    continue
                cells = {
                    _column_index(cell.attrib["r"]): _cell_value(cell, shared)
                    for cell in row.findall(NS + "c")
                }
                row_number = int(row.attrib.get("r", "0"))
                row.clear()
                if row_number == 1:
                    width = max(cells, default=-1) + 1
                    headers = [cells.get(index, "").strip() for index in range(width)]
                    continue
                if headers is None:
                    raise ValueError("GFID aggregated sheet is missing its header row")
                if not cells:
                    continue
                yield {
                    headers[index]: value
                    for index, value in cells.items()
                    if index < len(headers) and headers[index]
                }


def _excel_date(value: str | None) -> date | None:
    if value is None or not value.strip() or value.strip().upper() in {"NA", "N/A"}:
        return None
    raw = value.strip()
    try:
        number = float(raw)
    except ValueError:
        try:
            return date.fromisoformat(raw[:10])
        except ValueError:
            return None
    # Excel's 1900 date system includes a fictitious leap day; the commonly
    # used 1899-12-30 epoch correctly maps dates after February 1900.
    return (datetime(1899, 12, 30) + timedelta(days=number)).date()


def _number(value: str | None) -> float | None:
    if value is None or not value.strip() or value.strip().upper() in {"NA", "N/A"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def point_in_bbox(latitude: float, longitude: float, bbox: list[float]) -> bool:
    west, south, east, north = bbox
    return west <= longitude <= east and south <= latitude <= north


def distance_to_bbox_km(latitude: float, longitude: float, bbox: list[float]) -> float:
    """Approximate point-to-box geodesic distance for discovery ranking."""
    west, south, east, north = bbox
    closest_lat = min(max(latitude, south), north)
    closest_lon = min(max(longitude, west), east)
    lat1, lat2 = math.radians(latitude), math.radians(closest_lat)
    dlat = lat2 - lat1
    dlon = math.radians(closest_lon - longitude)
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0088 * 2 * math.asin(min(1.0, math.sqrt(h)))


def screen_rows(
    rows: Iterable[dict[str, str]], areas: list[dict[str, Any]], source_md5: str
) -> dict[str, Any]:
    boxes = {
        area["city"]: [float(value) for value in area["aoi_bbox_wgs84"].split(",")]
        for area in areas
    }
    events_by_city: dict[str, list[dict[str, Any]]] = {city: [] for city in boxes}
    nearby_by_city: dict[str, list[dict[str, Any]]] = {city: [] for city in boxes}
    considered = 0
    in_window = 0
    for row in rows:
        considered += 1
        event_date = _excel_date(row.get("Date"))
        if event_date is None or not COMMON_START <= event_date <= COMMON_END:
            continue
        in_window += 1
        latitude = _number(row.get("Lat"))
        longitude = _number(row.get("Lon"))
        if latitude is None or longitude is None:
            continue
        for city, bbox in boxes.items():
            inside = point_in_bbox(latitude, longitude, bbox)
            distance = distance_to_bbox_km(latitude, longitude, bbox)
            if not inside and distance > 25:
                continue
            event = {
                    "date": event_date.isoformat(),
                    "source": row.get("Source"),
                    "source_id": row.get("Source_ID"),
                    "country": row.get("Country"),
                    "location": row.get("Location"),
                    "adm1": row.get("Adm1"),
                    "adm2": row.get("Adm2"),
                    "representative_lat": latitude,
                    "representative_lon": longitude,
                    "fatalities": _number(row.get("Fatalities")),
                    "affected": _number(row.get("Affected")),
                    "houses_damaged": _number(row.get("Houses Damaged")),
                    "houses_destroyed": _number(row.get("Houses Destroyed")),
                    "representative_point_inside_fixed_aoi": inside,
                    "distance_to_fixed_aoi_km": round(distance, 3),
                }
            nearby_by_city[city].append(event)
            if inside:
                events_by_city[city].append(event)
    area_results = []
    for area in areas:
        city = area["city"]
        events = sorted(
            events_by_city[city], key=lambda event: (event["date"], event["source"] or "")
        )
        area_results.append(
            {
                "city": city,
                "region": area["region"],
                "nominal_aoi_km2": area.get("aoi_area_km2", 625),
                "representative_event_points_in_fixed_bbox": len(events),
                "source_counts": dict(Counter(event["source"] or "unknown" for event in events)),
                "events": events,
                "representative_event_points_within_25km_of_bbox": len(nearby_by_city[city]),
                "nearby_discovery_leads": sorted(
                    nearby_by_city[city],
                    key=lambda event: (event["distance_to_fixed_aoi_km"], event["date"]),
                ),
            }
        )
    return {
        "schema_version": 1,
        "audit_id": "usgs-gfid-fixed-aoi-event-screen-2026-11-04",
        "status": "event_context_discovery_only",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": {
            "title": "The Global Flood Impacts Database (GFID)",
            "publisher": "U.S. Geological Survey",
            "data_gov_url": DATA_GOV_URL,
            "sciencebase_item_url": SCIENCEBASE_ITEM_URL,
            "workbook_url": WORKBOOK_URL,
            "workbook_name": "AggregatedFloodData.xlsx",
            "workbook_md5": source_md5,
            "expected_workbook_md5": EXPECTED_MD5,
            "user_agent": USER_AGENT,
        },
        "analysis_window": {
            "start": COMMON_START.isoformat(),
            "end": COMMON_END.isoformat(),
            "date_field": "Aggregated.Date, interpreted as Excel 1900-system serial date or ISO date",
            "spatial_test": "representative Lat/Lon point strictly inside fixed AOI bounding box; no buffer",
        },
        "counts": {
            "aggregated_rows_scanned": considered,
            "rows_with_event_date_in_common_window": in_window,
            "study_areas": len(areas),
            "areas_with_representative_points_in_aoi": sum(
                bool(events_by_city[area["city"]]) for area in areas
            ),
            "representative_points_in_all_areas": sum(map(len, events_by_city.values())),
            "nearby_representative_points_within_25km_all_areas": sum(
                map(len, nearby_by_city.values())
            ),
        },
        "areas": area_results,
        "interpretation_limits": [
            "GFID aggregates event-impact records from source databases. It supplies independent event context, not per-pixel flood labels or mapped inundation boundaries.",
            "A representative coordinate inside a 625 km² box does not prove the reported inundation occurred within that box; source geocoding precision and impact geometry must be checked per record.",
            "Points within 25 km of a box are nearby discovery leads only; the buffer is not a substitute for the fixed-area intersection criterion.",
            "Multiple records may describe duplicate or overlapping events. Source rows are retained and not counted as unique events without source-level review and duplicate reconciliation.",
            "Reported impacts have source-specific definitions, coverage, and missingness; blanks are unknown, not zero.",
            "This event discovery screen does not change confirmatory enrollment or the ATLAS score.",
        ],
    }


def _download_workbook(destination: Path) -> str:
    request = urllib.request.Request(WORKBOOK_URL, headers={"User-Agent": USER_AGENT})
    digest = hashlib.md5()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != EXPECTED_MD5:
        destination.unlink(missing_ok=True)
        raise ValueError(f"GFID workbook MD5 mismatch: expected {EXPECTED_MD5}, got {actual}")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, help="Use a local copy of the exact source workbook")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "outputs/atlas-usgs-gfid-aoi-event-audit.json"
    )
    args = parser.parse_args()
    workbook = args.workbook or Path("/tmp/atlas-gfid-aggregated.xlsx")
    if not workbook.exists():
        md5 = _download_workbook(workbook)
    else:
        md5 = hashlib.md5(workbook.read_bytes()).hexdigest()
        if md5 != EXPECTED_MD5:
            raise ValueError(f"GFID workbook MD5 mismatch: expected {EXPECTED_MD5}, got {md5}")
    register = json.loads((ROOT / "data/study_area_register.json").read_text(encoding="utf-8"))
    result = screen_rows(iter_aggregated_rows(workbook), register["results"], md5)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))
    for area in result["areas"]:
        print(f"{area['city']}: {area['representative_event_points_in_fixed_bbox']} representative points")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
