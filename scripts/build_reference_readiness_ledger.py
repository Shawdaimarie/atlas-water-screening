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
    "rtc": "atlas-s1rtc-pixel-coverage-unique-audit.json",
    "rtc_valid_quota": "atlas-s1rtc-valid-quota-audit.json",
    "c2s": "atlas-c2s-flood-dataset-audit.json",
    "ufo": "atlas-ufo-dataset-coverage-audit.json",
    "floodplanet": "atlas-floodplanet-coverage-audit.json",
    "sen1floods11": "atlas-sen1floods11-label-footprint-audit.json",
    "geoid": "atlas-geoid-flood-overlap-audit.json",
    "geoid_labels": "atlas-geoid-flood-stlouis-label-coverage.json",
    "gfd_points": "atlas-global-flood-db-validation-audit.json",
    "gfd_extent": "atlas-gfd-event-extent-coverage-audit.json",
    "groundsource": "atlas-groundsource-event-coverage-audit.json",
    "spacenet8": "atlas-spacenet8-louisiana-coverage-audit.json",
    "cems": "atlas-cems-event-discovery-audit.json",
    "mumbai_nrsc": "atlas-mumbai-nrsc-reference-lead.json",
    "jakarta_incidents": "atlas-jakarta-incident-data-audit.json",
    "jakarta_bpb_event": "atlas-jakarta-bpbd-jan2026-aoi-context.json",
    "nasa_egis": "atlas-nasa-egis-opera-footprint-audit.json",
}
JSON_OUT = OUT / "atlas-reference-readiness-ledger.json"
CSV_OUT = OUT / "atlas-reference-readiness-ledger.csv"
DIST_JSON = DIST / JSON_OUT.name
DIST_CSV = DIST / CSV_OUT.name
DIST_JAKARTA_AUDIT = DIST / INPUTS["jakarta_incidents"]
DIST_JAKARTA_EVENT_AUDIT = DIST / INPUTS["jakarta_bpb_event"]
DIST_NASA_EGIS_AUDIT = DIST / INPUTS["nasa_egis"]
DIST_GEOID_LABEL_AUDIT = DIST / INPUTS["geoid_labels"]
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
    rtc_quota = load_json(INPUTS["rtc_valid_quota"])
    c2s = load_json(INPUTS["c2s"])["registered_areas"]
    ufo = load_json(INPUTS["ufo"])["registered_areas"]
    floodplanet = load_json(INPUTS["floodplanet"])["registered_areas"]
    sen = {area_key(x["region"], x["city"]): x for x in load_json(INPUTS["sen1floods11"])["areas"]}
    geoid = {area_key(x["region"], x["city"]): x for x in load_json(INPUTS["geoid"])["results"]}
    geoid_label_audit = load_json(INPUTS["geoid_labels"])
    gfd_points = load_json(INPUTS["gfd_points"])["area_match_counts"]
    gfd_extent = {area_key(x["region"], x["city"]): x for x in load_json(INPUTS["gfd_extent"])["areas"]}
    groundsource_audit = load_json(INPUTS["groundsource"])
    groundsource = {area_key(x["region"], x["city"]): x for x in groundsource_audit["areas"]}
    groundsource_opportunities = {
        area_key(x["region"], x["city"]): x
        for x in groundsource_audit["acquisition_opportunity_screen"]["areas"]
    }
    spacenet = load_json(INPUTS["spacenet8"])["results"]
    cems = load_json(INPUTS["cems"])
    mumbai_nrsc = load_json(INPUTS["mumbai_nrsc"])
    jakarta_incidents = load_json(INPUTS["jakarta_incidents"])
    jakarta_event = load_json(INPUTS["jakarta_bpb_event"])
    nasa_egis = {
        area_key(x["region"], x["city"]): x
        for x in load_json(INPUTS["nasa_egis"])["areas"]
    }
    nrsc_present = mumbai_nrsc.get("candidate_area") == "Mumbai"
    nrsc_documents = len(mumbai_nrsc.get("event", {}).get("mapped_tiles", [])) if nrsc_present else 0
    nrsc_use = mumbai_nrsc.get("coverage_and_use", {})
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
        egis_area = nasa_egis[key]
        egis_s1 = [
            x for x in egis_area.get("records", [])
            if (x.get("catalog") or {}).get("candidate_sentinel1_water_observation") is True
        ]
        egis_dates = sorted({
            x["catalog"]["date_utc"] for x in egis_s1
            if (x.get("catalog") or {}).get("date_utc")
        })
        row = {
            "region": region,
            "city": city,
            "nominal_aoi_km2": area["aoi_area_km2"],
            "opera_cmr_dates_2024_09_to_2026_11": area["unique_acquisition_dates"],
            "rtc_sampled_groups_passing_80pct": rtc_area["sampled_groups_passing_80pct"],
            "rtc_sampled_groups_total": rtc_area["sampled_group_count"],
            "rtc_all_12_sampled_groups_pass": rtc_area["all_12_sampled_groups_meet_pixel_screen"],
            "c2s_label_chips": c2s_area["label_chip_count"],
            "c2s_label_valid_pixels": c2s_area.get("label_valid_pixels_across_overlapping_chips", 0),
            "c2s_water_pixels": c2s_area.get("water_pixels_across_overlapping_chips", 0),
            "c2s_dates": c2s_dates,
            "ufo_labeled_chips": ufo_area["chip_count"],
            "floodplanet_hand_label_chips": fp_area["label_chip_count"],
            "sen1floods11_hand_label_footprints": sen[key]["hand_labeled_chip_footprints_intersecting"],
            "geoid_flood_tiles": geoid_area["intersecting_tiles"],
            "geoid_paper_eligible_tiles": geoid_area["paper_eligible_tiles"],
            "geoid_mapped_label_fraction": (
                geoid_label_audit["raster"]["mapped_label_fraction"] if city == "St. Louis" else None
            ),
            "geoid_outside_mapped_label_fraction": (
                1 - geoid_label_audit["raster"]["mapped_label_fraction"] if city == "St. Louis" else None
            ),
            "gfd_validation_points": point_count,
            "gfd_event_map_flood_candidate_pixels": gfd_map.get("event_flood_candidate_pixels", 0),
            "gfd_event_map_event_start": gfd_event.get("event_start"),
            "gfd_event_map_event_end": gfd_event.get("event_end"),
            "groundsource_event_records_discovery_only": groundsource[key]["intersecting_event_records"],
            "groundsource_leads_with_product_date_within_1_calendar_day": groundsource_opportunities[key]["events_with_product_date_within_1_day"],
            "groundsource_top_leads_with_near_date_and_3_pre_post_metadata": sum(
                candidate["has_calendar_date_match_within_1_day"]
                and candidate["has_3_pre_event_metadata_dates"]
                and candidate["has_3_post_event_metadata_dates"]
                for candidate in groundsource_opportunities[key]["top_candidates"][:3]
            ),
            "groundsource_top_metadata_opportunity_leads": [
                {
                    "event_id": candidate["event_id"],
                    "reported_start_date": candidate["reported_start_date"],
                    "reported_end_date": candidate["reported_end_date"],
                    "nearest_product_date_offset_calendar_days": candidate["nearest_product_date_offset_calendar_days"],
                    "pre_event_30d_product_dates": candidate["pre_event_30d_product_dates"],
                    "post_event_30d_product_dates": candidate["post_event_30d_product_dates"],
                }
                for candidate in groundsource_opportunities[key]["top_candidates"][:3]
            ],
            "cems_rapid_mapping_flood_aoi_overlaps": cems_by_area.get(key, {}).get("intersecting_flood_aois", 0),
            "spacenet8_unique_object_references": s["unique_feature_ids"],
            "spacenet8_flooded_yes_objects": s["flooded"],
            "spacenet8_unknown_flood_status_objects": s["flood_status_unknown"],
            "nrsc_official_map_documents": nrsc_documents if city == "Mumbai" else 0,
            "nrsc_official_use_marked": bool(nrsc_use.get("source_marks_maps_for_official_use")) if city == "Mumbai" else False,
            "nrsc_fixed_aoi_overlap_verified": bool(nrsc_use.get("fixed_aoi_overlap_verified")) if city == "Mumbai" else False,
            "nrsc_reuse_license_verified": bool(nrsc_use.get("reuse_license_verified")) if city == "Mumbai" else False,
            "nasa_egis_s1_water_catalog_footprint_records": len(egis_s1),
            "nasa_egis_s1_water_catalog_dates": egis_dates,
            "nasa_egis_s1_water_catalog_temporal_records": [
                {
                    "object_id": (x.get("catalog") or {}).get("object_id"),
                    "name": (x.get("catalog") or {}).get("name"),
                    "date_utc": (x.get("catalog") or {}).get("date_utc"),
                    "date_basis": (x.get("catalog") or {}).get("date_basis"),
                    "granule_name_interval_start_utc": (x.get("catalog") or {}).get("granule_name_interval_start_utc"),
                    "granule_name_interval_end_utc": (x.get("catalog") or {}).get("granule_name_interval_end_utc"),
                    "service_folder": x.get("service_folder"),
                }
                for x in egis_s1
            ],
            "nasa_egis_disaster_services": sorted({x["service_folder"] for x in egis_s1}),
            "jakarta_bpbd_2026_reported_affected_kelurahan_count": (
                jakarta_event["spatial_screen"]["reported_affected_kelurahan_count"]
                if city == "Jakarta" else None
            ),
            "jakarta_bpbd_2026_affected_kelurahan_polygons_intersecting_aoi": (
                jakarta_event["spatial_screen"]["positive_area_intersection_count"]
                if city == "Jakarta" else None
            ),
            "jakarta_bpbd_2026_not_returned_by_aoi_intersection_query": (
                jakarta_event["spatial_screen"]["not_returned_by_aoi_intersection_query"]
                if city == "Jakarta" else None
            ),
            "confirmatory_enrollment_eligible": False,
            "reason_not_enrolled": "No area currently meets the complete event-matched independent-label, QA-valid observation, blinded adjudication, probability-sample, and precision gates.",
        }
        rows.append(row)

    if len(rows) != 16 or sum(r["region"] == "United States" for r in rows) != 8 or sum(r["region"] != "United States" for r in rows) != 8:
        raise ValueError("Study register is no longer a balanced 8+8 design")
    if sum(r["confirmatory_enrollment_eligible"] for r in rows) != 0:
        raise ValueError("No confirmatory site may be inferred from source intersection counts")

    source_hashes = {
        "data/study_area_register.json": hashlib.sha256(REGISTER.read_bytes()).hexdigest(),
        **{
            name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
            for name in INPUTS.values()
        },
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
        "rtc_unique_area_orbit_groups": rtc["summary"]["unique_area_orbit_groups"],
        "rtc_duplicate_selections": rtc["summary"]["duplicate_selections"],
        "rtc_matched_quota_groups_selected": rtc_quota["summary"]["valid_groups_selected"],
        "rtc_matched_quota_target_groups": rtc_quota["summary"]["target_valid_groups"],
        "rtc_matched_quota_areas": rtc_quota["summary"]["areas_meeting_12_group_quota"],
        "rtc_matched_quota_supplemental_groups_screened": rtc_quota["summary"]["supplemental_groups_screened"],
        "c2s_areas_with_labels": sum(bool(r["c2s_label_chips"]) for r in rows),
        "spacenet8_areas_with_objects": sum(bool(r["spacenet8_unique_object_references"]) for r in rows),
        "spacenet8_positive_objects": sum(r["spacenet8_flooded_yes_objects"] for r in rows),
        "spacenet8_unknown_objects": sum(r["spacenet8_unknown_flood_status_objects"] for r in rows),
        "areas_with_unverified_official_map_leads": sum(bool(r["nrsc_official_map_documents"]) for r in rows),
        "areas_with_nasa_egis_s1_water_catalog_leads": sum(bool(r["nasa_egis_s1_water_catalog_footprint_records"]) for r in rows),
        "nasa_egis_s1_water_catalog_footprint_records": sum(r["nasa_egis_s1_water_catalog_footprint_records"] for r in rows),
        "nrsc_official_map_documents": sum(r["nrsc_official_map_documents"] for r in rows),
        "groundsource_event_records_are_validation_labels": False,
        "areas_with_three_groundsource_top_metadata_opportunities": sum(
            r["groundsource_top_leads_with_near_date_and_3_pre_post_metadata"] == 3 for r in rows
        ),
        "cities_with_nonspatial_administrative_event_leads": 1,
        "areas_with_official_event_admin_area_aoi_context": sum(
            bool(r["jakarta_bpbd_2026_affected_kelurahan_polygons_intersecting_aoi"])
            for r in rows
        ),
        "jakarta_bpbd_2026_affected_kelurahan_polygons_intersecting_aoi":
            jakarta_event["spatial_screen"]["positive_area_intersection_count"],
        "jakarta_bpbd_2026_reported_affected_kelurahan_count":
            jakarta_event["spatial_screen"]["reported_affected_kelurahan_count"],
        "jakarta_incident_source_rows": jakarta_incidents["observed_data"]["csv_rows"],
        "jakarta_incident_source_reporting_periods": jakarta_incidents["observed_data"]["distinct_reporting_periods"],
    }
    return {
        "audit": "ATLAS normalized per-area reference and observation readiness ledger",
        "created_from": "Pinned source-audit snapshots; no original dataset archive or satellite observation was reread by this join",
        "design": {"us_areas": 8, "international_areas": 8, "nominal_aoi_km2": 625},
        "summary": summary,
        "input_sha256": source_hashes,
        "city_specific_nonspatial_leads": [
            {
                "city": "Jakarta",
                "region": "International",
                "source_title": jakarta_incidents["source"]["dataset_title"],
                "source_page": jakarta_incidents["source"]["dataset_page"],
                "source_csv_sha256": jakarta_incidents["source"]["raw_csv_sha256"],
                "csv_rows": jakarta_incidents["observed_data"]["csv_rows"],
                "reporting_periods": jakarta_incidents["observed_data"]["distinct_reporting_periods"],
                "distinct_kelurahan": jakarta_incidents["observed_data"]["distinct_kelurahan"],
                "coordinate_or_geometry_field_present": jakarta_incidents["observed_data"]["coordinate_or_geometry_field_present"],
                "explicit_reuse_license_verified": jakarta_incidents["reuse_and_quality_gates"]["explicit_reuse_license_verified"],
                "confirmatory_enrollment_eligible": jakarta_incidents["classification"]["confirmatory_enrollment_eligible"],
            }
        ],
        "city_specific_official_event_area_context": [
            {
                "city": "Jakarta",
                "region": "International",
                "event_interval_local_dates": jakarta_event["event"]["official_interval_local_dates"],
                "reported_inundated_household_units": jakarta_event["event"]["bpbd_reported_inundated_household_units"],
                "reported_inundated_road_segments": jakarta_event["event"]["bpbd_reported_inundated_road_segments"],
                "reported_affected_kelurahan_count": jakarta_event["spatial_screen"]["reported_affected_kelurahan_count"],
                "positive_area_intersections_with_fixed_aoi": jakarta_event["spatial_screen"]["positive_area_intersection_count"],
                "not_returned_by_aoi_intersection_query": jakarta_event["spatial_screen"]["not_returned_by_aoi_intersection_query"],
                "bpbd_sources": jakarta_event["event"]["bpbd_sources"],
                "boundary_source": jakarta_event["boundary_source"]["url"],
                "boundary_query_sha256": jakarta_event["boundary_source"]["query_response_sha256"],
                "event_location_within_aoi_verified": False,
                "pixel_labels_or_raster_qa_present": False,
                "confirmatory_enrollment_eligible": False,
            }
        ],
        "interpretation_limits": [
            "Counts are source-specific and are not comparable sample sizes across sensors or label types.",
            "Groundsource records are news-derived event leads, not flood labels or validated demand.",
            "The two NRSC Mumbai event-map PDFs are marked for official use; AOI overlap and reuse permission are unverified, so they are tracked as discovery leads and excluded from validation counts.",
            "Deduplicated RTC VV valid-pixel samples are availability screens, not OPERA DSWx-S1 water classifications or event/baseline adequacy.",
            "GFD, C2S, GEOID-Flood, and SpaceNet 8 leads are historical; they do not establish event-matched, independent, balanced validation for the shared 2024-2026 window.",
            "No candidate is confirmatory until all gates in data/validation_protocol.yaml are independently met.",
            "The Jakarta BPBD 2024 incident extract is a nonspatial administrative lead with quarter-coded reporting and no event-day coordinates; it is not a pixel label and cannot establish fixed-AOI overlap or confirmatory eligibility.",
            "For Jakarta's January 2026 event, 20 of 21 BPBD-reported affected kelurahan polygons positively intersect the fixed AOI. This administrative-area context does not locate inundation within the overlapping polygon portions, prove event-day satellite classes, supply independent pixel labels, or qualify the site for confirmatory enrollment.",
            "NASA EGIS catalog footprint intersections are same-product OPERA discovery leads; they do not establish complete-scene pixel coverage or independent reference truth. Record counts may include multiple product layers for one acquisition.",
        ],
        "areas": rows,
    }


def render_card(ledger: dict) -> str:
    s = ledger["summary"]
    jakarta_event = ledger["city_specific_official_event_area_context"][0]
    new_orleans = next(row for row in ledger["areas"] if row["city"] == "New Orleans")
    interval_records = [
        row for row in new_orleans["nasa_egis_s1_water_catalog_temporal_records"]
        if row["date_basis"] == "granule_name_interval_only"
    ]
    granule_interval_note = ""
    if interval_records:
        first, last = interval_records[0]["granule_name_interval_start_utc"], interval_records[0]["granule_name_interval_end_utc"]
        granule_interval_note = (
            f' New Orleans has one WTR/BWTR catalog granule whose name encodes {first} to {last}; '
            'the service date field is absent, so this remains a name-only granule interval and is not counted as multiple acquisition dates.'
        )
    return (
        f'{START}<article class="reference-card"><h3>16-area evidence-readiness ledger</h3>'
        f'<b>{s["confirmatory_areas_eligible"]}/16 confirmatory sites eligible · '
        f'{s["rtc_matched_quota_groups_selected"]}/{s["rtc_matched_quota_target_groups"]} selected RTC groups meet the matched 80% quota '
        f'({s["rtc_matched_quota_areas"]}/16 areas; {s["rtc_matched_quota_supplemental_groups_screened"]} extra candidates screened)</b>'
        f'<p>The same fixed-area crosswalk lists metadata dates, 12 sampled VV availability groups, and each public reference lead for every U.S. and international candidate. '
        f'The initial random availability draw passed {s["rtc_groups_passing_80pct"]}/{s["rtc_groups_sampled"]}; the separate matched quota conditions selection on the 80% coverage floor and is not an archive-wide pass-rate estimate. '
        'Mumbai’s two NRSC maps are separately flagged as official-use leads with unverified overlap and reuse terms. Jakarta also has a 2024 BPBD administrative incident extract (260 rows across four reporting periods); it has no coordinates or event-day timestamps, and its reuse license is unverified. These source counts have different meanings and do not establish comparable flood labels or adequate event/baseline sampling.</p>'
        f'<p><b>Jakarta official-event context:</b> BPBD reported 90 inundated RT and 10 roads during the 22–24 January 2026 event; {jakarta_event["positive_area_intersections_with_fixed_aoi"]}/{jakarta_event["reported_affected_kelurahan_count"]} named affected kelurahan boundary polygons positively overlap the fixed box. This supports event relevance only; it does not locate the reported water inside the AOI, provide pixel labels, or pass QA. <a href="{INPUTS["jakarta_bpb_event"]}" target="_blank" rel="noopener">Open Jakarta event/AOI audit ↗</a></p>'
        f'<p><b>Event acquisition opportunities:</b> the three top metadata-ranked Groundsource event leads for each of {s["areas_with_three_groundsource_top_metadata_opportunities"]}/16 areas have an OPERA metadata date within one calendar day and at least three metadata dates in each 30-day pre/post window. Calendar dates do not establish an exact 24-hour match; source events need official verification, and QA-valid pixels and independent labels remain unverified. News coverage is geographically uneven.</p>'
        f'<p><b>NASA EGIS same-product discovery:</b> catalog footprints show OPERA S1-water layers in {s["areas_with_nasa_egis_s1_water_catalog_leads"]}/16 areas. These are event-product discovery leads, not independent labels or QA-valid pixel coverage; area-specific temporal fields and records are included in the register.{granule_interval_note}</p>'
        f'<p><b>Historical reference-pixel coverage:</b> the St. Louis GEOID-Flood 2017 training event has 12 intersecting tile footprints, but the audited labels map {next(row["geoid_mapped_label_fraction"] for row in ledger["areas"] if row["city"] == "St. Louis"):.2%} of the fixed AOI pixels; the rest are outside mapped labels. This is not held-out validation and sits outside the common 2024–2026 window. The other 15 AOIs have no measured GEOID-Flood label-pixel fraction. <a href="{INPUTS["geoid_labels"]}" target="_blank" rel="noopener">Open St. Louis label-coverage audit ↗</a></p>'
        f'<a href="atlas-jakarta-incident-data-audit.json" download="atlas-jakarta-incident-data-audit.json">Download Jakarta source audit ↗</a> '
        f'<a href="{INPUTS["nasa_egis"]}" target="_blank" rel="noopener">Open NASA EGIS catalog-footprint audit ↗</a> '
        f'<a href="atlas-groundsource-event-coverage-audit.json" target="_blank" rel="noopener">Open event/date opportunity JSON ↗</a> '
        f'<a href="atlas-groundsource-event-coverage-audit.json" download="atlas-groundsource-event-coverage-audit.json">Download event/date opportunity JSON ↧</a> '
        f'<a href="{JSON_OUT.name}" download="{JSON_OUT.name}">Download 16-area JSON ↗</a> '
        f'<a href="{CSV_OUT.name}" download="{CSV_OUT.name}">Download 16-area CSV ↗</a></article>{END}'
    )


def build() -> dict:
    ledger = build_ledger()
    JSON_OUT.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    DIST.mkdir(exist_ok=True)
    DIST_JSON.write_bytes(JSON_OUT.read_bytes())
    DIST_JAKARTA_AUDIT.write_bytes((OUT / INPUTS["jakarta_incidents"]).read_bytes())
    DIST_JAKARTA_EVENT_AUDIT.write_bytes((OUT / INPUTS["jakarta_bpb_event"]).read_bytes())
    DIST_NASA_EGIS_AUDIT.write_bytes((OUT / INPUTS["nasa_egis"]).read_bytes())
    DIST_GEOID_LABEL_AUDIT.write_bytes((OUT / INPUTS["geoid_labels"]).read_bytes())
    (DIST / INPUTS["groundsource"]).write_bytes((OUT / INPUTS["groundsource"]).read_bytes())
    fields = list(ledger["areas"][0])
    with CSV_OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
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
