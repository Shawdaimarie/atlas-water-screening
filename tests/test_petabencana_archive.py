from __future__ import annotations

import hashlib

from scripts.audit_petabencana_archive import summarize_window


def test_archive_screen_flags_2025_request_returning_2022_records() -> None:
    window = {
        "label": "Jakarta March 2025 flood window",
        "start": "2025-03-01T00:00:00+0700",
        "end": "2025-03-08T23:00:00+0700",
    }
    payload = {
        "statusCode": 200,
        "result": [
            {"area_id": "4157", "last_updated": "2022-10-07T12:36:18.830Z", "max_state": 2},
            {"area_id": "5394", "last_updated": "2022-10-07T12:36:18.933Z", "max_state": 3},
        ],
    }

    result = summarize_window(window, payload, hashlib.sha256(b"fixture").hexdigest())

    assert result["returned_area_count"] == 2
    assert result["returned_rows_with_update_date_in_requested_window"] == 0
    assert result["returned_update_date_min"] == "2022-10-07"
    assert result["screening_outcome"] == "returned_rows_are_outside_requested_window"


def test_archive_screen_accepts_control_dates_inside_requested_window() -> None:
    window = {
        "label": "January 2020 positive-control window",
        "start": "2020-01-01T00:00:00+0700",
        "end": "2020-01-08T23:00:00+0700",
    }
    payload = {
        "statusCode": 200,
        "result": [
            {"area_id": "901", "last_updated": "2020-01-02T12:00:00.000Z", "max_state": 4},
            {"area_id": "902", "last_updated": "2019-12-27T12:00:00.000Z", "max_state": 2},
        ],
    }

    result = summarize_window(window, payload, hashlib.sha256(b"fixture").hexdigest())

    assert result["returned_rows_with_update_date_in_requested_window"] == 1
    assert result["screening_outcome"] == "has_returned_updates_within_requested_window"


def test_archive_screen_rejects_invalid_response_envelope() -> None:
    window = {"label": "bad", "start": "2025-03-01T00:00:00+0700", "end": "2025-03-08T23:00:00+0700"}
    try:
        summarize_window(window, {"statusCode": 500, "result": []}, "0" * 64)
    except ValueError as exc:
        assert "unexpected response envelope" in str(exc)
    else:
        raise AssertionError("invalid response envelope should fail closed")


def test_archive_screen_flags_stale_rows_for_jakarta_january_2026_event() -> None:
    window = {
        "label": "Jakarta BPBD 22-26 January 2026 event window",
        "start": "2026-01-22T00:00:00+0700",
        "end": "2026-01-26T03:00:00+0700",
    }
    payload = {
        "statusCode": 200,
        "result": [
            {"area_id": "4157", "last_updated": "2022-10-07T12:36:18.830Z", "max_state": 2},
            {"area_id": "5394", "last_updated": "2022-10-07T12:36:18.933Z", "max_state": 3},
        ],
    }

    result = summarize_window(payload=payload, window=window, response_sha256=hashlib.sha256(b"fixture").hexdigest())

    assert result["returned_rows_with_update_date_in_requested_window"] == 0
    assert result["returned_update_date_min"] == "2022-10-07"
    assert result["screening_outcome"] == "returned_rows_are_outside_requested_window"
