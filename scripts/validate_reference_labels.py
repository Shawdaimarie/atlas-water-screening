"""Validate blinded double interpretation before reference labels enter analysis."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LABELS = {"event_floodwater", "persistent_water", "nonwater", "ambiguous", "unobservable"}
ROLES = {"labeler", "adjudicator"}
INDEPENDENCE = {"independent_primary", "lineage_qualified_sensitivity", "not_independent", "unknown"}
REQUIRED = {
    "sample_id", "labeler_id", "role", "label", "blind_to_opera", "reference_source_id",
    "reference_acquired_at", "reference_sensor", "reference_resolution_m", "reference_lineage",
    "independence_status", "independence_basis", "reference_license", "evidence_url",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        return reader.fieldnames, list(reader)


def _is_true(value: str) -> bool:
    return value.strip().casefold() in {"true", "1", "yes"}


def _source_metadata_error(row: dict[str, str]) -> str | None:
    for key in ("reference_source_id", "reference_sensor", "reference_lineage", "independence_basis", "reference_license", "evidence_url"):
        if not row.get(key, "").strip():
            return f"missing {key}"
    try:
        acquired = datetime.fromisoformat(row["reference_acquired_at"].strip().replace("Z", "+00:00"))
    except ValueError:
        return "reference_acquired_at is not ISO-8601"
    if acquired.tzinfo is None or acquired.utcoffset() is None:
        return "reference_acquired_at must include a timezone"
    try:
        resolution = float(row["reference_resolution_m"])
        if resolution <= 0:
            return "reference_resolution_m must be positive"
    except ValueError:
        return "reference_resolution_m must be numeric"
    if not row["evidence_url"].strip().startswith("https://"):
        return "evidence_url must use HTTPS"
    return None


def validate_labels(sample_path: Path, label_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    _, sample_rows = _read(sample_path)
    label_fields, labels = _read(label_path)
    missing = sorted(REQUIRED - set(label_fields))
    if missing:
        raise ValueError(f"Label file is missing columns: {', '.join(missing)}")
    sample_ids = [row.get("sample_id", "").strip() for row in sample_rows]
    if not sample_ids or any(not sid for sid in sample_ids) or len(set(sample_ids)) != len(sample_ids):
        raise ValueError("Sample frame must have unique, nonempty sample_id values")
    known = set(sample_ids)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    source_rows: dict[str, dict[str, str]] = {}
    for row in labels:
        sid, labeler_id = row.get("sample_id", "").strip(), row.get("labeler_id", "").strip()
        role = row.get("role", "").strip().casefold()
        label = row.get("label", "").strip().casefold()
        if sid not in known:
            raise ValueError(f"Label references unknown sample_id: {sid!r}")
        if not labeler_id or role not in ROLES or label not in LABELS:
            raise ValueError(f"Invalid labeler, role, or label for sample {sid}")
        pair = (sid, labeler_id)
        if pair in seen:
            raise ValueError(f"Duplicate labeler row for {sid}/{labeler_id}")
        seen.add(pair)
        if row.get("independence_status", "").strip() not in INDEPENDENCE:
            raise ValueError(f"Invalid independence_status for sample {sid}")
        metadata_error = _source_metadata_error(row)
        if metadata_error:
            raise ValueError(f"{sid}/{labeler_id}: {metadata_error}")
        source_id = row["reference_source_id"].strip()
        normalized = {key: row[key].strip() for key in (
            "reference_acquired_at", "reference_sensor", "reference_resolution_m", "reference_lineage",
            "independence_status", "independence_basis", "reference_license", "evidence_url")}
        if source_id in source_rows and source_rows[source_id] != normalized:
            raise ValueError(f"Reference source metadata conflicts for source {source_id}")
        source_rows[source_id] = normalized
        grouped[sid].append(row)

    output: list[dict[str, Any]] = []
    for sid in sample_ids:
        rows = grouped.get(sid, [])
        initial = [row for row in rows if row["role"].strip().casefold() == "labeler"]
        adjudicators = [row for row in rows if row["role"].strip().casefold() == "adjudicator"]
        labels_by_labeler = [row["label"].strip().casefold() for row in initial]
        structurally_complete = len(initial) == 2 and len({row["labeler_id"].strip() for row in initial}) == 2
        agreement = structurally_complete and labels_by_labeler[0] == labels_by_labeler[1]
        adjudicated = False
        adjudicated_label = ""
        if not agreement and structurally_complete and len(adjudicators) == 1:
            adjudicated = True
            adjudicated_label = adjudicators[0]["label"].strip().casefold()
        elif len(adjudicators) > 1:
            raise ValueError(f"More than one adjudicator row for sample {sid}")
        final_label = labels_by_labeler[0] if agreement else adjudicated_label
        independent = structurally_complete and all(
            row["independence_status"].strip() == "independent_primary" for row in initial)
        required_reviewers = initial + (adjudicators if not agreement else [])
        blinded = structurally_complete and all(_is_true(row["blind_to_opera"]) for row in required_reviewers)
        ready = bool(final_label and independent and blinded)
        output.append({
            "sample_id": sid,
            "initial_labeler_count": len(initial),
            "labeler_1": labels_by_labeler[0] if labels_by_labeler else "",
            "labeler_2": labels_by_labeler[1] if len(labels_by_labeler) > 1 else "",
            "agreement": bool(agreement),
            "adjudicated": bool(adjudicated),
            "adjudicated_label": adjudicated_label,
            "final_label": final_label,
            "both_labelers_blinded": bool(blinded),
            "primary_independent_reference": bool(independent),
            "primary_label_review_ready": bool(ready),
            "label_classifiable": bool(final_label and final_label not in {"ambiguous", "unobservable"}),
            "status": "ready_for_analysis_review" if ready else "incomplete_or_sensitivity_only",
        })

    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_frame_sha256": _sha256(sample_path),
        "label_file_sha256": _sha256(label_path),
        "sample_units": len(sample_ids),
        "double_labeled_units": sum(row["initial_labeler_count"] == 2 for row in output),
        "agreements": sum(row["agreement"] for row in output),
        "adjudicated_disagreements": sum(row["adjudicated"] for row in output),
        "primary_label_review_ready_units": sum(row["primary_label_review_ready"] for row in output),
        "classifiable_reference_units": sum(row["label_classifiable"] for row in output),
        "confirmatory_enrollment_established": False,
        "interpretation_limit": "This quality gate checks declared review completeness, blinding, and reference lineage fields; it does not verify the truth or licensing of supplied references, event timing eligibility, sample precision, or study enrollment.",
    }
    return output, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-frame", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    rows, summary = validate_labels(args.sample_frame, args.labels)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "reference_label_qc.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary["qc_csv_sha256"] = _sha256(csv_path)
    (args.output_dir / "reference_label_qc_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Samples: {summary['sample_units']}; primary label review ready: {summary['primary_label_review_ready_units']}; confirmatory enrollment: not established")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
