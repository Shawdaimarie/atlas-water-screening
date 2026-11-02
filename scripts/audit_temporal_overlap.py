"""Audit exact-date and year-month overlap in the saved NASA CMR screen.

Run scripts/screen_study_areas.py first. This uses only archived CMR metadata,
not raster pixels or an event catalogue.
"""
from collections import Counter
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/study_area_register.json"
OUTPUTS = [ROOT / "data/temporal_overlap_audit.json", ROOT / "outputs/atlas-temporal-overlap-audit.json"]


def summarize(obj):
    areas = obj["results"]
    if len(areas) != 16:
        raise ValueError(f"Expected 16 candidate areas; got {len(areas)}")
    date_sets = [set(area["acquisition_dates"]) for area in areas]
    exact_dates = sorted(set.intersection(*date_sets))
    month_sets = [{day[:7] for day in dates} for dates in date_sets]
    common_months = sorted(set.intersection(*month_sets))
    any_area_months = sorted(set.union(*month_sets))
    summary = {
        "query_window": obj["screening_protocol"]["period"],
        "collection": obj["screening_protocol"]["collection"],
        "areas": len(areas),
        "exact_acquisition_dates_common_to_all_areas": len(exact_dates),
        "common_acquisition_dates": exact_dates,
        "year_month_periods_with_at_least_one_metadata_acquisition_in_every_area": len(common_months),
        "common_year_months": common_months,
        "year_month_periods_with_any_area_metadata_acquisition": len(any_area_months),
        "shared_month_coverage_fraction": round(len(common_months) / len(any_area_months), 4),
        "per_area_date_count_min": min(map(len, date_sets)),
        "per_area_date_count_max": max(map(len, date_sets)),
        "limits": "Date metadata only; does not test event alignment, granule downloads, QA masks, valid-pixel percent, or independent labels.",
    }
    return summary


def main():
    summary = summarize(json.loads(SOURCE.read_text()))
    for output in OUTPUTS:
        output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
