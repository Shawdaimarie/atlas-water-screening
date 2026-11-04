from scripts.audit_singapore_pub_flood_alert import audit_payload


def test_observed_pub_flood_alert_point_inside_aoi_is_only_an_event_lead():
    payload = {
        "data": {
            "records": [
                {
                    "datetime": "2025-05-22T20:16:06+08:00",
                    "updatedTimestamp": "2025-09-03T11:52:52+08:00",
                    "item": {
                        "status": "Actual",
                        "readings": [
                            {
                                "event": "Flood",
                                "certainty": "Observed",
                                "headline": "Flood Warning",
                                "description": "Flash flood at Wan Tho Ave.",
                                "senderName": "PUB",
                                "area": {
                                    "areaDesc": "Wan Tho Ave, Singapore",
                                    "circle": ["1.33201", "103.87015", "1"],
                                },
                            }
                        ],
                    },
                }
            ]
        }
    }
    result = audit_payload(
        payload,
        [103.707480, 1.239811, 103.932120, 1.464389],
        "2025-05-22",
        "a" * 64,
        "2026-11-04T09:20:00+00:00",
    )
    assert result["summary"] == {
        "returned_records": 1,
        "flood_readings": 1,
        "flood_reading_centers_inside_aoi": 1,
        "observed_certainty_inside_aoi": 1,
    }
    assert result["reports"][0]["center_inside_fixed_aoi"] is True
    assert any("not a mapped flood extent" in x for x in result["interpretation_limits"])
    assert any("not confirmatory validation" in x for x in result["interpretation_limits"])


def test_alert_center_outside_aoi_is_not_counted_as_intersection():
    payload = {
        "data": {
            "records": [
                {
                    "item": {
                        "readings": [
                            {
                                "event": "Flood",
                                "area": {"circle": ["1.5", "103.9", "1"]},
                            }
                        ]
                    }
                }
            ]
        }
    }
    result = audit_payload(
        payload,
        [103.707480, 1.239811, 103.932120, 1.464389],
        "2025-05-22",
        "b" * 64,
        "2026-11-04T09:20:00+00:00",
    )
    assert result["summary"]["flood_reading_centers_inside_aoi"] == 0
    assert result["reports"][0]["center_inside_fixed_aoi"] is False
