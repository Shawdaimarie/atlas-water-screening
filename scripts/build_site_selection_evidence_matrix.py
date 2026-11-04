#!/usr/bin/env python3
"""Build an auditable, non-composite 8+8 site-selection/readiness matrix."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER = ROOT / "data/study_area_register.json"
DEFAULT_LEDGER = ROOT / "outputs/atlas-reference-readiness-ledger.json"
DEFAULT_RTC = ROOT / "outputs/atlas-s1rtc-pixel-coverage-unique-audit.json"
DEFAULT_RTC_QUOTA = ROOT / "outputs/atlas-s1rtc-valid-quota-audit.json"
DEFAULT_JSON = ROOT / "outputs/atlas-site-selection-evidence-matrix.json"
DEFAULT_CSV = ROOT / "outputs/atlas-site-selection-evidence-matrix.csv"
DEFAULT_MD = ROOT / "outputs/atlas-site-selection-evidence-matrix.md"
DIST = ROOT / "dist"
CARD_START = "<!-- GENERATED SITE SELECTION MATRIX START -->"
CARD_END = "<!-- GENERATED SITE SELECTION MATRIX END -->"

REFERENCE_FIELDS = {
    "C2S sparse labels": "c2s_label_chips",
    "UFOv2 label chips": "ufo_labeled_chips",
    "FloodPlanet hand-label chips": "floodplanet_hand_label_chips",
    "Sen1Floods11 label footprints": "sen1floods11_hand_label_footprints",
    "GEOID-Flood tiles": "geoid_flood_tiles",
    "GFD validation points": "gfd_validation_points",
    "SpaceNet 8 object references": "spacenet8_unique_object_references",
    "CEMS rapid-mapping flood AOI overlaps": "cems_rapid_mapping_flood_aoi_overlaps",
}

CRITERIA = [
    {
        "id": "public_research_need",
        "rule": "A location-specific rationale and public evidence URL are recorded for candidate screening.",
        "interpretation": "Supports public research/management relevance only; it does not establish buyer demand or validate the linked evidence source.",
    },
    {
        "id": "balanced_candidate_frame",
        "rule": "Eight U.S. and eight international candidate AOIs use the same nominal 625 km² footprint and OPERA DSWx-S1 V1 metadata window.",
        "interpretation": "A balanced candidate frame is not a representative sample of either region.",
    },
    {
        "id": "archive_metadata_discovery",
        "rule": "Report complete CMR metadata-hit and distinct-date counts for the same product/window; do not convert metadata to observations.",
        "interpretation": "Metadata discovers possible acquisition dates; it says nothing about valid pixels, floodwater, or event matching.",
    },
    {
        "id": "raster_availability_diagnostic",
        "rule": "Report the pinned 12-group-per-area 2025 Sentinel-1 RTC finite/non-nodata VV sample and its 80% spatial-coverage floor.",
        "interpretation": "RTC is a separate availability diagnostic, not OPERA DSWx-S1 validation or event/baseline coverage.",
    },
    {
        "id": "event_discovery_leads",
        "rule": "Report news-derived event leads and metadata-date opportunities as discovery counts only.",
        "interpretation": "Groundsource dates do not establish official event occurrence, exact time, QA-valid imagery, or independent labels.",
    },
    {
        "id": "confirmatory_enrollment",
        "rule": "Require verified event-specific coverage, at least three QA-valid scenes in each event and baseline period, full-AOI and asset coverage review, independent licensed labels, probability sampling, and the predeclared precision gate.",
        "interpretation": "No area currently satisfies the confirmatory gate; all remain candidates or exploratory leads.",
    },
]


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _index(rows: list[dict[str, Any]], source: str) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row.get("region", "")), str(row.get("city", "")))
        if not all(key) or key in result:
            raise ValueError(f"Missing or duplicate area key in {source}: {key!r}")
        result[key] = row
    return result


def build_matrix(register_path: Path = DEFAULT_REGISTER,
                 ledger_path: Path = DEFAULT_LEDGER,
                 rtc_path: Path = DEFAULT_RTC,
                 rtc_quota_path: Path = DEFAULT_RTC_QUOTA) -> dict[str, Any]:
    register_doc = _read_json(register_path)
    ledger_doc = _read_json(ledger_path)
    rtc_doc = _read_json(rtc_path)
    rtc_quota_doc = _read_json(rtc_quota_path)
    register_rows = register_doc.get("results")
    ledger_rows = ledger_doc.get("areas")
    rtc_rows = rtc_doc.get("areas")
    quota_rows = rtc_quota_doc.get("areas")
    if not all(isinstance(rows, list) for rows in (register_rows, ledger_rows, rtc_rows, quota_rows)):
        raise ValueError("Register, readiness ledger, and both RTC audits must each contain area rows")

    register = _index(register_rows, "study-area register")
    ledger = _index(ledger_rows, "reference-readiness ledger")
    rtc = _index(rtc_rows, "unique RTC audit")
    rtc_quota = _index(quota_rows, "RTC valid-quota audit")
    if set(register) != set(ledger) or set(register) != set(rtc) or set(register) != set(rtc_quota):
        missing = {
            "ledger_only": sorted(set(ledger) - set(register)),
            "rtc_only": sorted(set(rtc) - set(register)),
            "register_only": sorted(set(register) - set(ledger) - set(rtc)),
        }
        raise ValueError(f"Study-area sources do not have the same 16-area frame: {missing}")

    regions = {key[0] for key in register}
    if regions != {"United States", "International"}:
        raise ValueError(f"Unexpected candidate regions: {sorted(regions)}")
    if sum(key[0] == "United States" for key in register) != 8 or sum(
        key[0] == "International" for key in register
    ) != 8:
        raise ValueError("Candidate frame must contain exactly eight areas per region")

    matrix_rows = []
    for key in sorted(register, key=lambda value: (value[0] != "United States", value[1])):
        area, readiness, availability = register[key], ledger[key], rtc[key]
        rationale = str(area.get("screening_rationale") or "").strip()
        evidence_url = str(area.get("evidence_url") or "").strip()
        candidate_need_status = "documented_candidate" if rationale and evidence_url else "evidence_missing"
        if area.get("collection") != "OPERA_L3_DSWX-S1_V1":
            raise ValueError(f"Unexpected collection for {key}: {area.get('collection')!r}")
        if area.get("aoi_area_km2") != 625 or readiness.get("nominal_aoi_km2") != 625:
            raise ValueError(f"Candidate AOI does not match the common 625 km² frame: {key}")
        if availability.get("sampled_group_count") != 12:
            raise ValueError(f"Expected 12 RTC groups for {key}; got {availability.get('sampled_group_count')}")

        reference_leads = {
            label: int(readiness.get(field) or 0)
            for label, field in REFERENCE_FIELDS.items()
        }
        top_leads = readiness.get("groundsource_top_metadata_opportunity_leads") or []
        matrix_rows.append({
            "region": key[0],
            "city": key[1],
            "candidate_status": candidate_need_status,
            "screening_rationale": rationale,
            "public_evidence_url": evidence_url,
            "value_integration_question": area.get("value_integration_question", ""),
            "nominal_aoi_km2": int(area["aoi_area_km2"]),
            "collection": area["collection"],
            "temporal_start": area.get("temporal_start"),
            "temporal_end": area.get("temporal_end"),
            "cmr_granule_hits": int(area.get("cmr_granule_hits") or 0),
            "cmr_distinct_dates": int(area.get("unique_acquisition_dates") or 0),
            "cmr_returned_entries_complete": bool(area.get("returned_entries_complete")),
            "rtc_sampled_groups_passing_80pct": int(availability.get("sampled_groups_passing_80pct") or 0),
            "rtc_sampled_groups_total": int(availability["sampled_group_count"]),
            "rtc_all_12_pass": bool(availability.get("all_12_sampled_groups_meet_pixel_screen")),
            "rtc_valid_quota_groups_selected": int(rtc_quota[key].get("selected_valid_groups") or 0),
            "rtc_valid_quota_supplemental_groups_screened": int(rtc_quota[key].get("supplemental_groups_screened") or 0),
            "rtc_valid_quota_met": bool(rtc_quota[key].get("all_quarter_quotas_met")),
            "groundsource_events_discovery_only": int(readiness.get("groundsource_event_records_discovery_only") or 0),
            "groundsource_top_metadata_opportunities": len(top_leads),
            "groundsource_leads_with_near_date_and_3_pre_post_metadata": int(
                readiness.get("groundsource_top_leads_with_near_date_and_3_pre_post_metadata") or 0
            ),
            "reference_lead_counts_by_source": reference_leads,
            "reference_lead_source_count_nonzero": sum(value > 0 for value in reference_leads.values()),
            "confirmatory_enrollment_eligible": bool(readiness.get("confirmatory_enrollment_eligible")),
            "confirmatory_reason_not_enrolled": readiness.get("reason_not_enrolled", ""),
            "interpretation": "Candidate discovery evidence only. Do not infer valid OPERA pixels, flood occurrence, accuracy, market demand, or comparable confirmatory coverage.",
        })

    summary = {
        "candidate_areas": len(matrix_rows),
        "us_candidates": sum(row["region"] == "United States" for row in matrix_rows),
        "international_candidates": sum(row["region"] == "International" for row in matrix_rows),
        "candidates_with_documented_public_need": sum(row["candidate_status"] == "documented_candidate" for row in matrix_rows),
        "candidates_with_complete_cmr_metadata_query": sum(row["cmr_returned_entries_complete"] for row in matrix_rows),
        "areas_passing_all_12_rtc_groups": sum(row["rtc_all_12_pass"] for row in matrix_rows),
        "rtc_groups_passing_80pct": sum(row["rtc_sampled_groups_passing_80pct"] for row in matrix_rows),
        "rtc_groups_sampled": sum(row["rtc_sampled_groups_total"] for row in matrix_rows),
        "areas_meeting_matched_rtc_valid_quota": sum(row["rtc_valid_quota_met"] for row in matrix_rows),
        "matched_rtc_valid_groups_selected": sum(row["rtc_valid_quota_groups_selected"] for row in matrix_rows),
        "supplemental_rtc_groups_screened": sum(row["rtc_valid_quota_supplemental_groups_screened"] for row in matrix_rows),
        "areas_with_three_groundsource_metadata_opportunities": sum(
            row["groundsource_leads_with_near_date_and_3_pre_post_metadata"] >= 3 for row in matrix_rows
        ),
        "areas_with_any_spatial_reference_lead": sum(row["reference_lead_source_count_nonzero"] > 0 for row in matrix_rows),
        "confirmatory_areas_eligible": sum(row["confirmatory_enrollment_eligible"] for row in matrix_rows),
        "composite_site_score_used": False,
    }
    return {
        "audit": "ATLAS evidence-based study-area selection and readiness matrix",
        "schema_version": 1,
        "created_from": "pinned project register and audit outputs; see source hashes",
        "site_selection_policy": (
            "Purposive, stratified 8+8 candidate frame. Public research/management relevance and common archive discovery support candidate status only. "
            "No composite relevance/value score is used. Confirmatory enrollment is a separate fail-closed gate."
        ),
        "criteria": CRITERIA,
        "summary": summary,
        "rows": matrix_rows,
        "source_sha256": {
            str(path.relative_to(ROOT)): _sha256(path)
            for path in (register_path, ledger_path, rtc_path, rtc_quota_path)
        },
        "interpretation_limits": [
            "Public evidence supports documented local research or management context, not ATLAS market demand or purchase intent.",
            "CMR rows and dates are metadata discovery, not retrieved or QA-valid OPERA observations.",
            "RTC VV checks are a separate Sentinel-1 archive availability diagnostic and are not water labels or OPERA DSWx-S1 validation.",
            "Groundsource is news-derived event discovery; dates and geometry require independent official verification.",
            "Nonzero reference-lead counts mix sources with different dates, sensors, classes, licenses, and sampling adequacy; they do not mean a site passes validation.",
            "All areas remain unconfirmed until the same scene-quality, independent-label, sampling, precision, and licensing gates pass.",
        ],
    }


def write_outputs(matrix: dict[str, Any], json_path: Path = DEFAULT_JSON,
                  csv_path: Path = DEFAULT_CSV, md_path: Path = DEFAULT_MD) -> None:
    for path in (json_path, csv_path, md_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(matrix, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = matrix["rows"]
    fieldnames = [key for key, value in rows[0].items() if not isinstance(value, dict)]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({key: row[key] for key in fieldnames} for row in rows)

    summary = matrix["summary"]
    lines = [
        "# ATLAS evidence-based site-selection and readiness matrix",
        "",
        "Generated from the common 8 U.S. + 8 international register and pinned readiness/RTC audits. This is an eligibility crosswalk, not a weighted city ranking.",
        "",
        f"**Frame:** {summary['candidate_areas']} candidates ({summary['us_candidates']} U.S.; {summary['international_candidates']} international). **Confirmatory enrollment:** {summary['confirmatory_areas_eligible']}/{summary['candidate_areas']}. **Initial RTC draw:** {summary['rtc_groups_passing_80pct']}/{summary['rtc_groups_sampled']} groups passed before replacement. **Coverage-conditioned quota:** {summary['matched_rtc_valid_groups_selected']}/192 groups and {summary['areas_meeting_matched_rtc_valid_quota']}/16 areas meet the matched 12-group floor after screening {summary['supplemental_rtc_groups_screened']} additional groups.",
        "",
        "## Shared selection and enrollment criteria",
        "",
        *[f"- **{item['id']}** — {item['rule']} {item['interpretation']}" for item in matrix["criteria"]],
        "",
        "## Per-area evidence",
        "",
        "| Region | Area | Candidate need evidence | OPERA metadata dates | Initial RTC draw ≥80% | Matched RTC quota | Groundsource metadata leads | Independent reference lead types | Confirmatory status |",
        "|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lead_types = ", ".join(f"{name}: {count}" for name, count in row["reference_lead_counts_by_source"].items() if count) or "None found"
        lines.append(
            f"| {row['region']} | {row['city']} | [{row['screening_rationale']}]({row['public_evidence_url']}) | "
            f"{row['cmr_distinct_dates']} | {row['rtc_sampled_groups_passing_80pct']}/{row['rtc_sampled_groups_total']} | "
            f"{row['rtc_valid_quota_groups_selected']}/12 ({row['rtc_valid_quota_supplemental_groups_screened']} extra screened) | "
            f"{row['groundsource_leads_with_near_date_and_3_pre_post_metadata']} (news/event and image metadata only) | {lead_types} | "
            f"{'Eligible' if row['confirmatory_enrollment_eligible'] else 'Not eligible'} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "The candidate frame is supported as a broad, evidence-backed research screen, not as a completed comparable study. Public management evidence does not establish product demand. CMR metadata and Groundsource leads are discovery signals; RTC sample coverage is an auxiliary availability check. Reference-lead counts combine heterogeneous data sources and do not establish independent validation. No candidate passes the confirmatory enrollment gate, so the 8+8 comparative study is not yet empirically complete.",
        "",
        "Inputs are content-hashed in the JSON artifact. Reproduce with `python scripts/build_site_selection_evidence_matrix.py`.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")


def render_site_card(matrix: dict[str, Any]) -> str:
    summary = matrix["summary"]
    return (
        f'{CARD_START}<div class="study-foot"><b>Evidence-based selection criteria:</b> '
        "Candidates use a balanced 8+8 frame, equal nominal 625 km² AOIs, a common OPERA DSWx-S1 V1 metadata window, "
        "and location-specific public research/management evidence. We do not rank cities with an unapproved composite-value score. "
        f'Current gates: {summary["candidate_areas"]}/{summary["candidate_areas"]} candidates have documented public-need context and complete metadata queries; '
        f'the initial 2025 RTC draw passed {summary["rtc_groups_passing_80pct"]}/{summary["rtc_groups_sampled"]} samples, then the coverage-conditioned matched quota selected '
        f'{summary["matched_rtc_valid_groups_selected"]}/192 groups across {summary["areas_meeting_matched_rtc_valid_quota"]}/16 areas after screening {summary["supplemental_rtc_groups_screened"]} additional groups; '
        f'{summary["confirmatory_areas_eligible"]}/16 pass confirmatory enrollment. '
        "Metadata and news-derived event leads are discovery only. Confirmatory enrollment also requires event-specific QA-valid OPERA scenes, "
        "independent licensed labels, probability sampling, and the predeclared precision gate. "
        f'<a href="{DEFAULT_JSON.name}" target="_blank" rel="noopener">Open full selection and readiness matrix ↗</a> '
        f'<a href="atlas-study-area-evidence-register.json" target="_blank" rel="noopener">Open complete 8+8 area evidence register ↗</a> '
        f'<a href="{DEFAULT_CSV.name}" download="{DEFAULT_CSV.name}">Download 8+8 evidence matrix CSV ↧</a></div>{CARD_END}'
    )


def install_site_card(html: str, card: str) -> str:
    if html.count(CARD_START) != html.count(CARD_END) or html.count(CARD_START) > 1:
        raise ValueError("Malformed or duplicate site-selection matrix markers")
    if CARD_START in html:
        before, rest = html.split(CARD_START, 1)
        _, after = rest.split(CARD_END, 1)
        html = before + card + after
        return html
    anchor = '<div class="study-foot">Archive metadata is not a downloaded observation.'
    if html.count(anchor) != 1:
        raise ValueError("Could not locate the study-program archive-discovery caveat")
    return html.replace(anchor, card + anchor, 1)


def publish_site_assets(matrix: dict[str, Any], dist_dir: Path = DIST,
                        json_path: Path = DEFAULT_JSON, csv_path: Path = DEFAULT_CSV) -> None:
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / json_path.name).write_bytes(json_path.read_bytes())
    (dist_dir / csv_path.name).write_bytes(csv_path.read_bytes())
    index_path = dist_dir / "index.html"
    html = index_path.read_text(encoding="utf-8")
    index_path.write_text(install_site_card(html, render_site_card(matrix)), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--rtc", type=Path, default=DEFAULT_RTC)
    parser.add_argument("--rtc-quota", type=Path, default=DEFAULT_RTC_QUOTA)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    matrix = build_matrix(args.register, args.ledger, args.rtc, args.rtc_quota)
    write_outputs(matrix, args.json, args.csv, args.markdown)
    publish_site_assets(matrix, json_path=args.json, csv_path=args.csv)
    print(json.dumps(matrix["summary"], sort_keys=True))
    print(f"Wrote {args.json}, {args.csv}, and {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
