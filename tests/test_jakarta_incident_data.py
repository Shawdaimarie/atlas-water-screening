import csv

from scripts.audit_jakarta_incident_data import audit_csv


def test_jakarta_admin_extract_is_classified_as_nonspatial_lead(tmp_path):
    path = tmp_path / "jakarta.csv"
    rows = [
        {
            "periode_data": "202403",
            "triwulan": "1",
            "bulan": "2",
            "wilayah": "KOTA ADM. JAKARTA BARAT",
            "kecamatan": "KEBON JERUK",
            "kelurahan": "KEDOYA SELATAN",
            "jumlah_rata_rata_ketinggian_air": "30 s.d 70 cm",
            "jumlah_rw_terdampak": "1",
            "jumlah_kk_terdampak": "0",
            "jumlah_jiwa_terdampak": "0",
            "jumlah_kejadian": "1",
        },
        {
            "periode_data": "202403",
            "triwulan": "1",
            "bulan": "2",
            "wilayah": "KOTA ADM. JAKARTA BARAT",
            "kecamatan": "KEBON JERUK",
            "kelurahan": "KEDOYA SELATAN",
            "jumlah_rata_rata_ketinggian_air": "40 cm",
            "jumlah_rw_terdampak": "1",
            "jumlah_kk_terdampak": "0",
            "jumlah_jiwa_terdampak": "0",
            "jumlah_kejadian": "2",
        },
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)

    audit = audit_csv(path)
    observed = audit["observed_data"]
    assert observed["csv_rows"] == 2
    assert observed["unique_period_kecamatan_kelurahan_keys"] == 1
    assert observed["period_unit_keys_with_multiple_rows"] == 1
    assert observed["event_count_sum_across_source_rows"] == 3
    assert observed["event_count_sum_is_distinct_regional_events"] is False
    assert observed["coordinate_or_geometry_field_present"] is False
    assert audit["classification"]["confirmatory_enrollment_eligible"] is False
    assert audit["reuse_and_quality_gates"]["explicit_reuse_license_verified"] is False


def test_jakarta_audit_rejects_unexpected_period_and_missing_spatial_column(tmp_path):
    path = tmp_path / "unexpected.csv"
    path.write_text("periode_data,kecamatan,kelurahan\n202501,A,B\n")
    try:
        audit_csv(path)
    except ValueError as exc:
        assert "missing columns" in str(exc)
    else:
        raise AssertionError("missing audit fields should fail closed")
