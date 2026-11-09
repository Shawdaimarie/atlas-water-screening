from scripts.audit_jakarta_zenodo_data_access import summarize_record


def _record(access_right="restricted", files=None):
    return {
        "id": 16836145,
        "conceptrecid": "15806063",
        "files": files or [],
        "metadata": {
            "doi": "10.5281/zenodo.16836145",
            "title": "Jakarta Sinking City",
            "publication_date": "2025-08-13",
            "access_right": access_right,
            "license": {"id": "cc-by-4.0"},
            "description": "catalog description",
        },
    }


def test_restricted_jakarta_deposit_is_not_counted_as_available_labels():
    result = summarize_record(_record(), b"fixture", 403)
    assert result["catalog"]["latest_record_id"] == 16836145
    assert result["catalog"]["access_right"] == "restricted"
    assert result["catalog"]["public_api_file_count"] == 0
    assert result["classification"]["access_state"] == "restricted_unavailable_without_grant"
    assert result["classification"]["confirmatory_eligible"] is False
    assert result["classification"]["score_credit"] == 0


def test_open_record_requires_accessible_file_endpoint_and_exposed_files():
    file_row = {"key": "labels.geojson"}
    assert summarize_record(_record("open", [file_row]), b"fixture", 200)["classification"]["access_state"] == "open_candidate"
    assert summarize_record(_record("open", [file_row]), b"fixture", 403)["classification"]["access_state"] == "open_record_but_files_unavailable_or_unlisted"
