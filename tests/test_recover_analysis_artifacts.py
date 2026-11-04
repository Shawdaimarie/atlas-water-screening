import hashlib
import json
import tarfile
from pathlib import Path

import pytest

from scripts.recover_analysis_artifacts import (
    RecoveryError,
    create_backup,
    restore_backup,
)


def make_run(root: Path) -> tuple[Path, bytes]:
    run = root / "run"
    (run / "outputs").mkdir(parents=True)
    payload = b"synthetic analysis output\n"
    (run / "outputs" / "summary.csv").write_bytes(payload)
    (run / "run_manifest.json").write_text(json.dumps({
        "data_mode": "synthetic",
        "outputs": {"outputs/summary.csv": hashlib.sha256(payload).hexdigest()},
    }))
    return run, payload


def test_backup_restore_verifies_hashes_and_reports_input_limit(tmp_path):
    run, payload = make_run(tmp_path)
    archive = tmp_path / "backup.tar.gz"
    restored = tmp_path / "restored"
    created = create_backup(run, archive)
    result = restore_backup(archive, restored)
    assert created["artifacts"] == 1
    assert (restored / "outputs" / "summary.csv").read_bytes() == payload
    report = json.loads((restored / "recovery-report.json").read_text())
    assert result["all_hashes_verified"] is True
    assert report["source_inputs_restored"] is False


def test_backup_rejects_changed_output(tmp_path):
    run, _ = make_run(tmp_path)
    (run / "outputs" / "summary.csv").write_text("changed")
    with pytest.raises(RecoveryError, match="checksum mismatch"):
        create_backup(run, tmp_path / "backup.tar.gz")


@pytest.mark.parametrize("reserved", ["run_manifest.json", "recovery-manifest.json", "recovery-report.json"])
def test_backup_rejects_recovery_metadata_paths(tmp_path, reserved):
    run, _ = make_run(tmp_path)
    payload = b"metadata collision"
    manifest = json.loads((run / "run_manifest.json").read_text())
    manifest["outputs"][reserved] = hashlib.sha256(payload).hexdigest()
    (run / "run_manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(RecoveryError, match="conflicts with recovery metadata"):
        create_backup(run, tmp_path / "backup.tar.gz")


def test_restore_rejects_existing_destination(tmp_path):
    run, _ = make_run(tmp_path)
    archive = tmp_path / "backup.tar.gz"
    create_backup(run, archive)
    dest = tmp_path / "existing"
    dest.mkdir()
    with pytest.raises(RecoveryError, match="must not already exist"):
        restore_backup(archive, dest)


@pytest.mark.parametrize("member_name", ["../escape", "/absolute", "outputs/../escape"])
def test_restore_rejects_unsafe_archive_paths(tmp_path, member_name):
    archive = tmp_path / "unsafe.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        info = tarfile.TarInfo(member_name)
        info.size = 1
        import io
        tar.addfile(info, io.BytesIO(b"x"))
    with pytest.raises(RecoveryError):
        restore_backup(archive, tmp_path / "restored")


def test_restore_rejects_duplicate_members(tmp_path):
    run, _ = make_run(tmp_path)
    archive = tmp_path / "backup.tar.gz"
    create_backup(run, archive)
    duplicate = tmp_path / "duplicate.tar.gz"
    with tarfile.open(archive, "r:gz") as source, tarfile.open(duplicate, "w:gz") as target:
        for member in source.getmembers():
            fileobj = source.extractfile(member)
            target.addfile(member, fileobj)
            if member.name == "run_manifest.json":
                fileobj = source.extractfile(member)
                target.addfile(member, fileobj)
    with pytest.raises(RecoveryError, match="duplicate"):
        restore_backup(duplicate, tmp_path / "restored")
