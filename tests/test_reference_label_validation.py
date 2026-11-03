import csv
import json
from pathlib import Path

import pytest

from scripts.validate_reference_labels import REQUIRED, validate_labels


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _source(source_id="ref-a", **changes):
    row = {
        "reference_acquired_at": "2025-02-03T12:00:00Z",
        "reference_sensor": "airborne optical imagery",
        "reference_resolution_m": "0.5",
        "reference_lineage": "independent image interpretation; not derived from OPERA or Sentinel-1",
        "independence_status": "independent_primary",
        "independence_basis": "separate optical sensor and acquisition",
        "reference_license": "CC BY 4.0",
        "evidence_url": "https://example.org/reference",
        "reference_source_id": source_id,
    }
    row.update(changes)
    return row


def _label(sample_id, labeler_id, label, *, role="labeler", blind="true", source_id="ref-a", **source_changes):
    return {
        "sample_id": sample_id,
        "labeler_id": labeler_id,
        "role": role,
        "label": label,
        "blind_to_opera": blind,
        **_source(source_id, **source_changes),
    }


def test_complete_blinded_labels_and_adjudicated_disagreement(tmp_path):
    sample = tmp_path / "samples.csv"
    labels = tmp_path / "labels.csv"
    _write_csv(sample, ["sample_id"], [{"sample_id": "s1"}, {"sample_id": "s2"}])
    rows = [
        _label("s1", "a", "event_floodwater"), _label("s1", "b", "event_floodwater"),
        _label("s2", "a", "persistent_water"), _label("s2", "b", "nonwater"),
        _label("s2", "c", "persistent_water", role="adjudicator"),
    ]
    _write_csv(labels, sorted(REQUIRED), rows)
    qc, summary = validate_labels(sample, labels)
    assert [row["primary_label_review_ready"] for row in qc] == [True, True]
    assert [row["agreement"] for row in qc] == [True, False]
    assert [row["adjudicated"] for row in qc] == [False, True]
    assert summary["primary_label_review_ready_units"] == 2
    assert summary["confirmatory_enrollment_established"] is False


def test_incomplete_unblinded_and_sensitivity_labels_remain_unready(tmp_path):
    sample, labels = tmp_path / "samples.csv", tmp_path / "labels.csv"
    _write_csv(sample, ["sample_id"], [{"sample_id": "s1"}, {"sample_id": "s2"}, {"sample_id": "s3"}])
    rows = [
        _label("s1", "a", "nonwater"),
        _label("s2", "a", "nonwater", blind="false"), _label("s2", "b", "nonwater"),
        _label("s3", "a", "event_floodwater", source_id="s1", independence_status="lineage_qualified_sensitivity"),
        _label("s3", "b", "event_floodwater", source_id="s2", independence_status="lineage_qualified_sensitivity"),
    ]
    _write_csv(labels, sorted(REQUIRED), rows)
    qc, summary = validate_labels(sample, labels)
    assert [row["primary_label_review_ready"] for row in qc] == [False, False, False]
    assert summary["primary_label_review_ready_units"] == 0


def test_label_validator_rejects_duplicate_and_unknown_sample_rows(tmp_path):
    sample, labels = tmp_path / "samples.csv", tmp_path / "labels.csv"
    _write_csv(sample, ["sample_id"], [{"sample_id": "s1"}])
    duplicate = [_label("s1", "a", "nonwater"), _label("s1", "a", "nonwater")]
    _write_csv(labels, sorted(REQUIRED), duplicate)
    with pytest.raises(ValueError, match="Duplicate labeler row"):
        validate_labels(sample, labels)
    _write_csv(labels, sorted(REQUIRED), [_label("other", "a", "nonwater")])
    with pytest.raises(ValueError, match="unknown sample_id"):
        validate_labels(sample, labels)


@pytest.mark.parametrize("changes, message", [
    ({"reference_acquired_at": "2025-02-03T12:00:00"}, "must include a timezone"),
    ({"evidence_url": "http://example.org/reference"}, "must use HTTPS"),
    ({"reference_resolution_m": "0"}, "must be positive"),
])
def test_label_validator_rejects_invalid_reference_metadata(tmp_path, changes, message):
    sample, labels = tmp_path / "samples.csv", tmp_path / "labels.csv"
    _write_csv(sample, ["sample_id"], [{"sample_id": "s1"}])
    _write_csv(labels, sorted(REQUIRED), [_label("s1", "a", "nonwater", **changes)])
    with pytest.raises(ValueError, match=message):
        validate_labels(sample, labels)


def test_same_reference_source_cannot_have_conflicting_provenance(tmp_path):
    sample, labels = tmp_path / "samples.csv", tmp_path / "labels.csv"
    _write_csv(sample, ["sample_id"], [{"sample_id": "s1"}])
    rows = [_label("s1", "a", "nonwater"), _label("s1", "b", "nonwater", reference_sensor="drone imagery")]
    _write_csv(labels, sorted(REQUIRED), rows)
    with pytest.raises(ValueError, match="metadata conflicts"):
        validate_labels(sample, labels)
