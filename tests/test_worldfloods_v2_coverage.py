import json
import zipfile

from scripts.audit_worldfloods_v2_coverage import audit, intersects


def test_bbox_intersection_is_inclusive_at_shared_edge():
    assert intersects((0, 0, 1, 1), (1, 0, 2, 1))
    assert not intersects((0, 0, 0.9, 1), (1, 0, 2, 1))


def test_audit_reports_candidate_and_nonmatching_areas(tmp_path):
    register = tmp_path / "register.json"
    register.write_text(json.dumps({"results": [
        {"region": "United States", "city": "A", "aoi_bbox_wgs84": "0,0,1,1"},
        {"region": "International", "city": "B", "aoi_bbox_wgs84": "10,10,11,11"},
    ]}))
    archive = tmp_path / "metadata.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("match.json", json.dumps({
            "bounding box": {"west": 0.5, "south": 0.5, "east": 0.6, "north": 0.6},
            "event id": "event-1", "satellite date": "2023-01-01",
        }))
        output.writestr("miss.json", json.dumps({
            "bounding box": {"west": 20, "south": 20, "east": 21, "north": 21},
        }))
    result = audit(archive, register)
    assert result["summary"] == {
        "study_areas": 2,
        "areas_with_candidate_metadata_footprints": 1,
        "areas_without_candidate_metadata_footprints": 1,
        "metadata_records_intersecting_any_aoi": 1,
    }
    assert result["areas"][0]["candidate_metadata_footprints"][0]["event_id"] == "event-1"
    assert result["areas"][1]["screened_out_for_confirmatory_use"] is True


def test_empty_metadata_archive_is_rejected(tmp_path):
    register = tmp_path / "register.json"
    register.write_text(json.dumps({"results": [
        {"region": "United States", "city": "A", "aoi_bbox_wgs84": "0,0,1,1"},
    ]}))
    archive = tmp_path / "empty.zip"
    with zipfile.ZipFile(archive, "w"):
        pass
    try:
        audit(archive, register)
    except ValueError as exc:
        assert "No metadata records" in str(exc)
    else:
        raise AssertionError("empty archive was accepted")
