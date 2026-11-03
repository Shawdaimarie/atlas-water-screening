"""Build a normalized 8+8 per-area readiness crosswalk from pinned audits."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DIST = ROOT / "dist"
REGISTER = ROOT / "data/study_area_register.json"
INPUTS = {
    "rtc": "atlas-s1rtc-pixel-coverage-combined-audit.json",
    "c2s": "atlas-c2s-flood-dataset-audit.json",
    "ufo": "atlas-ufo-dataset-coverage-audit.json",
    "floodplanet": "atlas-floodplanet-coverage-audit.json",
    "sen1floods11": "atlas-sen1floods11-label-footprint-audit.json",
    "geoid": "atlas-geoid-flood-overlap-audit.json",
    "gfd_points": "atlas-global-flood-db-validation-audit.json",
    "gfd_extent": "atlas-gfd-event-extent-coverage-audit.json",
    "groundsource": "atlas-groundsource-event-coverage-audit.json",
    "spacenet8": "atlas-spacenet8-louisiana-coverage-audit.json",
    "cems": "atlas-cems-event-discovery-audit.json",
}
JSON_OUT = OUT / "atlas-reference-readiness-ledger.json"
CSV_OUT = OUT / "atlas-reference-readiness-ledger.csv"
DIST_JSON = DIST / JSON_OUT.name
DIST_CSV = DIST / CSV_OUT.name
HTML = DIST / "index.html"
START = "<!-- GENERATED REFERENCE READINESS LEDGER START -->"
END = "<!-- GENERATED REFERENCE READINESS LEDGER END -->"


def load_json(name: str) -> dict:
    return json.loads((OUT / name).read_text())


def area_key(region: str, city: str) -> str:
    return f"{region}/{city}"


def build_ledger() -> dict:
    register = json.loads(REGISTER.read_text())
    rtc = load_json(INPUTS["rtc"])
    c2s = load_json(INPUTS["c2s"])["registered_areas"]
    ufo = load_json(INPUTS["ufo"])["registered_areas"]
    floodplanet = load_json(INPUTS["floodplanet"])["registered_areas"]
    sen = {area_key(x["region"], x["city"]): x for x in load_json(INPUTS["sen1floods11"])["areas"]}
    geoid = {area_key(x["region"], x["city"]): x for x in load_json(INPUTS["geoid"])["results"]}
    gfd_points = load_json(INPUTS["gfd_points"])["area_match_counts"]
    gfd_extent = {area_key(x["region"], x["city"]): x for x in load_json(INPUTS["gfd_extent"])["areas"]}
    groundsource = {area_key(x["region"], x["city"]): x for x in load_json(INPUTS["groundsource"])["areas"]}
    spacenet = load_json(INPUTS["spacenet8"])["results"]
    cems = load_json(INPUTS["cems"])
    cems_by_area = {
        area_key(x["region"], x["city"]): x for x in cems.get("matches", [])
    }
    rtc_by_area = {area_key(x["region"], x["city"]): x for x in rtc["areas"]}
    rows = []

    for area in register["results"]:
        region, city = area["region"], area["city"]
        key = area_key(region, city)
        c2s_area = c2s[key]
        ufo_area = ufo[key]
        fp_area = floodplanet[key]
        s = spacenet[city]["unique_feature_totals"]
        rtc_area = rtc_by_area[key]
        geoid_area = geoid[key]
        map_area = gfd_extent[key]
        point_count = gfd_points[key]
        gfd_event = map_area.get("selected_event") or {}
        gfd_map = map_area.get("map_screen") or {}
        c2s_dates = c2s_area.get("distinct_s1_acquisition_dates", [])
        row = {
            "region": region,
            "city": city,
            "nominal_aoi_km2": area["aoi_area_km2"],
            "opera_cmr_dates_2024_09_to_2026_11": area["unique_acquisition_dates"],
            "rtc_sampled_groups_passing_80pct": rtc_area["sampled_quarter_pixel_passes"],
            "rtc_sampled_groups_total": rtc_area["sampled_group_count"],
            "rtc_all_12_sampled_groups_pass": rtc_area["all_sampled_groups_meet_pixel_screen"],
            "c2s_label_chips": c2s_area["label_chip_count"],
            "c2s_label_valid_pixels": c2s_area.get("label_valid_pixels_across_overlapping_chips", 0),
            "c2s_water_pixels": c2s_area.get("water_pixels_across_overlapping_chips", 0),
            "c2s_dates": c2s_dates,
            "ufo_labeled_chips": ufo_area["chip_count"],
            "floodplanet_hand_label_chips": fp_area["label_chip_count"],
            "sen1floods11_hand_label_footprints": sen[key]["hand_labeled_chip_footprints_intersecting"],
            "geoid_flood_tiles": geoid_area["intersecting_tiles"],
            "geoid_paper_eligible_tiles": geoid_area["paper_eligible_tiles"],
            "gfd_validation_points": point_count,
            "gfd_event_map_flood_candidate_pixels": gfd_map.get("event_flood_candidate_pixels", 0),
            "gfd_event_map_event_start": gfd_event.get("event_start"),
            "gfd_event_map_event_end": gfd_event.get("event_end"),
            "groundsource_event_records_discovery_only": groundsource[key]["intersecting_event_records"],
            "cems_rapid_mapping_activations": cems_by_area.get(key, {}).get("count", 0),
            "spacenet8_unique_object_references": s["unique_feature_ids"],
            "spacenet8_flooded_yes_objects": s["flooded"],
            "spacenet8_unknown_flood_status_objects": s["flood_status_unknown"],
            "confirmatory_enrollment_eligible": False,
            "reason_not_enrolled": "No area currently meets the complete event-matched independent-label, QA-valid observation, blinded adjudication, probability-sample, and precision gates.",
        }
        rows.append(row)

    if len(rows) != 16 or sum(r["region"] == "United States" for r in rows) != 8 or sum(r["region"] != "United States" for r in rows) != 8:
        raise ValueError("Study register is no longer a balanced 8+8 design")
    if sum(r["confirmatory_enrollment_eligible"] for r in rows) != 0:
        raise ValueError("No confirmatory site may be inferred from source intersection counts")

    source_hashes = {
        name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
        for name in INPUTS.values()
    }
    summary = {
        "candidate_areas": len(rows),
        "us_areas": sum(r["region"] == "United States" for r in rows),
        "international_areas": sum(r["region"] != "United States" for r in rows),
        "confirmatory_areas_eligible": sum(r["confirmatory_enrollment_eligible"] for r in rows),
        "areas_with_any_spatial_reference_lead": sum(
            bool(r["c2s_label_chips"] or r["floodplanet_hand_label_chips"] or
                 r["sen1floods11_hand_label_footprints"] or r["geoid_flood_tiles"] or
                 r["gfd_validation_points"] or r["spacenet8_unique_object_references"])
            for r in rows
        ),
        "rtc_groups_passing_80pct": sum(r["rtc_sampled_groups_passing_80pct"] for r in rows),
        "rtc_groups_sampled": sum(r["rtc_sampled_groups_total"] for r in rows),
        "areas_passing_all_12_rtc_samples": sum(r["rtc_all_12_sampled_groups_pass"] for r in rows),
        "c2s_areas_with_labels": sum(bool(r["c2s_label_chips"]) for r in rows),
        "spacenet8_areas_with_objects": sum(bool(r["spacenet8_unique_object_references"]) for r in rows),
        "spacenet8_positive_objects": sum(r["spacenet8_flooded_yes_objects"] for r in rows),
        "spacenet8_unknown_objects": sum(r["spacenet8_unknown_flood_status_objects"] for r in rows),
        "groundsource_event_records_are_validation_labels": False,
    }
    return {
        "audit": "ATLAS normalized per-area reference and observation readiness ledger",
        "created_from": "Pinned audit snapshots; no source archive or raster was reinterpreted by this join",
        "design": {"us_areas": 8, "international_areas": 8, "nominal_aoi_km2": 625},
        "summary": summary,
        "input_sha256": source_hashes,
        "interpretation_limits": [
            "Counts are source-specific and are not comparable sample sizes across sensors or label types.",
            "Groundsource records are news-derived event leads, not flood labels or validated demand.",
            "RTC VV valid-pixel samples are availability screens, not OPERA DSWx-S1 water classifications or event/baseline adequacy.",
            "GFD, C2S, GEOID-Flood, and SpaceNet 8 leads are historical; they do not establish event-matched, independent, balanced validation for the shared 2024-2026 window.",
            "No candidate is confirmatory until all gates in data/validation_protocol.yaml are independently met.",
        ],
        "areas": rows,
    }


def render_card(ledger: dict) -> str:
    s = ledger["summary"]
    return (
        f'{START}<article class="reference-card"><h3>16-area evidence-readiness ledger</h3>'
        f'<b>{s["confirmatory_areas_eligible"]}/16 confirmatory sites eligible · '
        f'{s["rtc_groups_passing_80pct"]}/{s["rtc_groups_sampled"]} sampled RTC groups pass the 80% screen</b>'
        f'<p>The same fixed-area crosswalk lists metadata dates, 12 sampled VV availability groups, and each public reference lead for every U.S. and international candidate. '
        'These source counts have different meanings and do not establish comparable flood labels or adequate event/baseline sampling.</p>'
        f'<a href="{JSON_OUT.name}" download="{JSON_OUT.name}">Download 16-area JSON ↗</a> '
        f'<a href="{CSV_OUT.name}" download="{CSV_OUT.name}">Download 16-area CSV ↗</a></article>{END}'
    )


def build() -> dict:
    ledger = build_ledger()
    JSON_OUT.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    DIST.mkdir(exist_ok=True)
    DIST_JSON.write_bytes(JSON_OUT.read_bytes())
    fields = list(ledger["areas"][0])
    with CSV_OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in ledger["areas"]:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})
    DIST_CSV.write_bytes(CSV_OUT.read_bytes())
    card = render_card(ledger)
    html = HTML.read_text()
    if START in html and END in html:
        before, rest = html.split(START, 1)
        _, after = rest.split(END, 1)
        html = before + card + after
    else:
        anchor = '<article class="reference-card"><h3>Other public reference screens</h3>'
        if html.count(anchor) != 1:
            raise ValueError("Could not locate the public reference-summary card")
        html = html.replace(anchor, card + anchor, 1)
    HTML.write_text(html)
    return ledger


if __name__ == "__main__":
    result = build()
    print(json.dumps(result["summary"], sort_keys=True))
