"""Create and restore hash-verified backups of a manifested analysis run."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

RECOVERY_MANIFEST = "recovery-manifest.json"
RUN_MANIFEST = "run_manifest.json"
DEFAULT_MAX_BYTES = 2 * 1024 * 1024 * 1024


class RecoveryError(ValueError):
    """Raised when an artifact backup cannot be safely verified or restored."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(raw: str) -> PurePosixPath:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise RecoveryError(f"Unsafe artifact path: {raw!r}")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise RecoveryError(f"Unsafe artifact path: {raw!r}")
    if path.as_posix() != raw:
        raise RecoveryError(f"Artifact path is not normalized: {raw!r}")
    return path


def _load_run(run_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    run_dir = run_dir.resolve(strict=True)
    manifest_path = run_dir / RUN_MANIFEST
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise RecoveryError(f"Missing regular {RUN_MANIFEST} in {run_dir}")
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RecoveryError(f"Cannot read valid {RUN_MANIFEST}: {exc}") from exc
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict) or not outputs:
        raise RecoveryError("run_manifest.json must contain a nonempty outputs hash map")
    artifacts = []
    for raw, expected_hash in sorted(outputs.items()):
        rel = _safe_relative(raw)
        if rel.parts[0] in {RUN_MANIFEST, RECOVERY_MANIFEST, "recovery-report.json"}:
            raise RecoveryError(f"Output path conflicts with recovery metadata: {raw}")
        if len(str(expected_hash)) != 64 or any(c not in "0123456789abcdef" for c in str(expected_hash)):
            raise RecoveryError(f"Invalid SHA-256 in run manifest for {raw}")
        path = run_dir.joinpath(*rel.parts)
        if any(part.is_symlink() for part in [run_dir.joinpath(*rel.parts[:i]) for i in range(1, len(rel.parts) + 1)]):
            raise RecoveryError(f"Symlink output is not permitted: {raw}")
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(run_dir) or not resolved.is_file():
            raise RecoveryError(f"Output is not a regular file under the run directory: {raw}")
        actual = sha256_file(resolved)
        if actual != expected_hash:
            raise RecoveryError(f"Output checksum mismatch: {raw}")
        artifacts.append({"path": rel.as_posix(), "sha256": actual, "size_bytes": resolved.stat().st_size})
    return manifest, artifacts


def create_backup(run_dir: Path, archive_path: Path, *, max_bytes: int = DEFAULT_MAX_BYTES) -> dict[str, Any]:
    run_dir = run_dir.resolve(strict=True)
    archive_path = archive_path.expanduser().absolute()
    if archive_path.exists():
        raise RecoveryError(f"Backup destination already exists: {archive_path}")
    if archive_path.is_relative_to(run_dir):
        raise RecoveryError("Backup archive must be outside the run directory")
    manifest, artifacts = _load_run(run_dir)
    total = sum(item["size_bytes"] for item in artifacts) + (run_dir / RUN_MANIFEST).stat().st_size
    if total > max_bytes:
        raise RecoveryError(f"Run is larger than the configured backup limit ({max_bytes} bytes)")
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    recovery = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_manifest_sha256": sha256_file(run_dir / RUN_MANIFEST),
        "artifacts": artifacts,
        "total_uncompressed_bytes": total,
        "analysis_data_mode": manifest.get("data_mode", "not_declared"),
        "note": "Analysis outputs and their run manifest only; source input data are referenced by hashes but are not backed up.",
    }
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".atlas-backup-", suffix=".tar.gz", dir=archive_path.parent, delete=False) as temp:
            temp_path = Path(temp.name)
        with tarfile.open(temp_path, "w:gz") as tar:
            tar.add(run_dir / RUN_MANIFEST, arcname=RUN_MANIFEST, recursive=False)
            for item in artifacts:
                path = run_dir.joinpath(*_safe_relative(item["path"]).parts)
                tar.add(path, arcname=f"outputs/{item['path']}", recursive=False)
            payload = json.dumps(recovery, sort_keys=True, indent=2).encode() + b"\n"
            import io
            info = tarfile.TarInfo(RECOVERY_MANIFEST)
            info.size = len(payload)
            info.mode = 0o600
            tar.addfile(info, io.BytesIO(payload))
        if archive_path.exists():
            raise RecoveryError(f"Backup destination appeared during write: {archive_path}")
        os.replace(temp_path, archive_path)
        temp_path = None
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
    return {"archive": str(archive_path), "archive_sha256": sha256_file(archive_path),
            "run_manifest_sha256": recovery["run_manifest_sha256"], "artifacts": len(artifacts),
            "total_uncompressed_bytes": total, "data_mode": recovery["analysis_data_mode"]}


def restore_backup(archive_path: Path, output_dir: Path, *, max_bytes: int = DEFAULT_MAX_BYTES) -> dict[str, Any]:
    archive_path = archive_path.resolve(strict=True)
    output_dir = output_dir.expanduser().absolute()
    if output_dir.exists():
        raise RecoveryError(f"Restore destination must not already exist: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=".atlas-restore-", dir=output_dir.parent))
    try:
        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                members = tar.getmembers()
                names = [member.name for member in members]
                if len(names) != len(set(names)):
                    raise RecoveryError("Backup contains duplicate member names")
                member_map = {}
                uncompressed = 0
                for member in members:
                    name = _safe_relative(member.name).as_posix()
                    if not member.isfile() or member.issym() or member.islnk():
                        raise RecoveryError(f"Backup contains a non-regular file: {name}")
                    uncompressed += member.size
                    if uncompressed > max_bytes:
                        raise RecoveryError("Backup exceeds the configured uncompressed size limit")
                    member_map[name] = member
                if RUN_MANIFEST not in member_map or RECOVERY_MANIFEST not in member_map:
                    raise RecoveryError("Backup is missing required manifests")
                recovery_file = tar.extractfile(member_map[RECOVERY_MANIFEST])
                run_file = tar.extractfile(member_map[RUN_MANIFEST])
                if recovery_file is None or run_file is None:
                    raise RecoveryError("Cannot read backup manifests")
                recovery = json.loads(recovery_file.read())
                run_bytes = run_file.read()
                if hashlib.sha256(run_bytes).hexdigest() != recovery.get("run_manifest_sha256"):
                    raise RecoveryError("Run manifest checksum mismatch")
                run_manifest = json.loads(run_bytes)
                expected_outputs = run_manifest.get("outputs")
                records = recovery.get("artifacts")
                if not isinstance(expected_outputs, dict) or not isinstance(records, list):
                    raise RecoveryError("Invalid recovery manifest schema")
                record_by_path = {record.get("path"): record for record in records}
                if set(record_by_path) != set(expected_outputs):
                    raise RecoveryError("Recovery manifest and run manifest output lists differ")
                expected_names = {RUN_MANIFEST, RECOVERY_MANIFEST} | {f"outputs/{_safe_relative(path).as_posix()}" for path in expected_outputs}
                if any(_safe_relative(path).parts[0] in {RUN_MANIFEST, RECOVERY_MANIFEST, "recovery-report.json"} for path in expected_outputs):
                    raise RecoveryError("Output path conflicts with recovery metadata")
                if set(member_map) != expected_names:
                    raise RecoveryError("Backup contains missing or unexpected files")
                (temp_dir / RUN_MANIFEST).write_bytes(run_bytes)
                for raw, expected_hash in expected_outputs.items():
                    rel = _safe_relative(raw)
                    member_name = f"outputs/{rel.as_posix()}"
                    member = member_map[member_name]
                    record = record_by_path[raw]
                    if record.get("sha256") != expected_hash or record.get("size_bytes") != member.size:
                        raise RecoveryError(f"Recovery manifest mismatch for {raw}")
                    source = tar.extractfile(member)
                    if source is None:
                        raise RecoveryError(f"Cannot read artifact: {raw}")
                    data = source.read()
                    if hashlib.sha256(data).hexdigest() != expected_hash:
                        raise RecoveryError(f"Artifact checksum mismatch: {raw}")
                    destination = temp_dir.joinpath(*rel.parts)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(data)
        except (tarfile.TarError, OSError, json.JSONDecodeError) as exc:
            if isinstance(exc, RecoveryError):
                raise
            raise RecoveryError(f"Cannot restore backup: {exc}") from exc
        os.replace(temp_dir, output_dir)
        temp_dir = None
        _, restored = _load_run(output_dir)
        report = {
            "restored_at": datetime.now(timezone.utc).isoformat(),
            "archive_sha256": sha256_file(archive_path),
            "run_manifest_sha256": sha256_file(output_dir / RUN_MANIFEST),
            "restored_artifacts": len(restored),
            "all_hashes_verified": True,
            "analysis_data_mode": run_manifest.get("data_mode", "not_declared"),
            "source_inputs_restored": False,
        }
        (output_dir / "recovery-report.json").write_text(json.dumps(report, indent=2) + "\n")
        return {"restore_directory": str(output_dir), **report}
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    backup = sub.add_parser("backup", help="create a checksum-verified run archive")
    backup.add_argument("--run-dir", type=Path, required=True)
    backup.add_argument("--archive", type=Path, required=True)
    restore = sub.add_parser("restore", help="restore a verified archive to a new directory")
    restore.add_argument("--archive", type=Path, required=True)
    restore.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "backup":
        result = create_backup(args.run_dir, args.archive)
    else:
        result = restore_backup(args.archive, args.output_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
