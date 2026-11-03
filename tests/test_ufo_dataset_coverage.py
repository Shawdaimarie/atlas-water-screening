import zipfile

from scripts.audit_ufo_dataset_coverage import (
    approximate_area_km2,
    clip_polygon_to_bbox,
    zip_read_contiguous_members,
)


def test_clip_polygon_to_bbox_preserves_overlap():
    polygon = [[-2, -2], [2, -2], [2, 2], [-2, 2], [-2, -2]]
    clipped = clip_polygon_to_bbox(polygon, (-1, -1, 1, 1))
    assert len(clipped) == 4
    assert approximate_area_km2(clipped) > 48_000


def test_clip_polygon_to_bbox_returns_empty_for_disjoint_polygon():
    polygon = [[-2, -2], [-1, -2], [-1, -1], [-2, -1], [-2, -2]]
    assert clip_polygon_to_bbox(polygon, (1, 1, 2, 2)) == []
    assert approximate_area_km2([]) == 0


def test_contiguous_zip_reader_includes_last_member_extra_field(monkeypatch, tmp_path):
    archive_path = tmp_path / "members.zip"
    extra = b"\x99\x99\x04\x00test"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("first.json", '{"id":"first"}')
        info = zipfile.ZipInfo("last.json")
        info.compress_type = zipfile.ZIP_DEFLATED
        info.extra = extra
        archive.writestr(info, '{"id":"last"}')

    data = archive_path.read_bytes()
    entries = []
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            entries.append({
                "name": info.filename,
                "method": info.compress_type,
                "compressed_size": info.compress_size,
                "local_header_offset": info.header_offset,
            })

    def ranged_bytes(_url, start, end, timeout=45):
        return data[start : end + 1], len(data)

    monkeypatch.setattr("scripts.audit_ufo_dataset_coverage.request_bytes", ranged_bytes)
    assert zip_read_contiguous_members("https://example.invalid/archive.zip", entries) == {
        "first.json": b'{"id":"first"}',
        "last.json": b'{"id":"last"}',
    }
