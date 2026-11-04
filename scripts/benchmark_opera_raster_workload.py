#!/usr/bin/env python3
"""Benchmark the fixed six-scene local OPERA raster pilot.

Run this inside the Python 3.12 container and resource limits named in
outputs/atlas-raster-workload-performance-contract.md. The data are preliminary
response mosaics outside the registered 8+8 study areas.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "outputs/atlas-texas-raster-pilot"
SOURCE_SUMMARY = PILOT / "summary.json"
MANIFEST = PILOT / "manifest.csv"
AOI = PILOT / "aoi.geojson"
ASSETS = PILOT / "assets.geojson"
ANALYZER = ROOT / "scripts/analyze_opera_geotiffs.py"
OUTPUT = ROOT / "outputs/atlas-raster-performance-benchmark.json"
TARGET_LATENCY_SECONDS = 10.0
TARGET_MEMORY_BYTES = 1024**3
TARGET_JOBS_PER_MINUTE = 6.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cgroup_value(path: str) -> str | None:
    try:
        value = Path(path).read_text().strip()
    except OSError:
        return None
    return None if value == "max" else value


def process_peak_rss_bytes(pid: int) -> int | None:
    try:
        status = Path(f"/proc/{pid}/status").read_text()
    except OSError:
        return None
    match = re.search(r"^VmHWM:\s+(\d+)\s+kB$", status, re.MULTILINE)
    return int(match.group(1)) * 1024 if match else None


def verify_inputs(summary: dict) -> list[dict]:
    inputs = []
    for item in summary["input_files"]:
        path = PILOT / item["path"]
        actual = {"path": item["path"], "bytes": path.stat().st_size, "sha256": sha256(path)}
        if actual["bytes"] != item["bytes"] or actual["sha256"] != item["sha256"]:
            raise RuntimeError(f"Input differs from the recorded pilot manifest: {path}")
        inputs.append(actual)
    if len(inputs) != 6:
        raise RuntimeError(f"Expected six fixed scenes; found {len(inputs)}")
    return inputs


def run_once(output_dir: Path) -> dict:
    command = [
        sys.executable, str(ANALYZER),
        "--manifest", str(MANIFEST), "--aoi", str(AOI), "--assets", str(ASSETS),
        "--min-valid-fraction", "0.8", "--min-dates", "3", "--output-dir", str(output_dir),
    ]
    started = time.perf_counter()
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    peak_rss = 0
    while process.poll() is None:
        current_rss = process_peak_rss_bytes(process.pid)
        if current_rss is not None:
            peak_rss = max(peak_rss, current_rss)
        time.sleep(0.005)
    stdout, stderr = process.communicate()
    result_code = process.returncode
    elapsed = time.perf_counter() - started
    if result_code:
        raise RuntimeError(f"Analyzer exited {result_code}: {stderr}\n{stdout}")
    if not peak_rss:
        raise RuntimeError("Could not read the analyzer process peak RSS from /proc")
    qa_path = output_dir / "observation_qa.csv"
    comparison_path = output_dir / "asset_event_baseline_comparison.csv"
    with qa_path.open(newline="", encoding="utf-8") as handle:
        qa_rows = list(csv.DictReader(handle))
    with comparison_path.open(newline="", encoding="utf-8") as handle:
        comparisons = list(csv.DictReader(handle))
    if len(qa_rows) != 6 or {row["aoi_valid_fraction"] for row in qa_rows} != {
        "0.999922", "0.0", "1.0", "0.999929"
    }:
        raise RuntimeError("Per-date QA output differs from the fixed pilot result")
    if len(comparisons) != 1 or comparisons[0]["status"] != "unknown_insufficient_qa_valid_dates":
        raise RuntimeError("Insufficient-date safety gate changed or comparison was emitted")
    return {
        "wall_seconds": round(elapsed, 6),
        "peak_rss_bytes": peak_rss,
        "observation_qa_sha256": sha256(qa_path),
        "comparison_sha256": sha256(comparison_path),
        "qa_row_count": len(qa_rows),
        "comparison_status": comparisons[0]["status"],
        "comparison_emitted": False,
    }


def main() -> None:
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("Run with Python 3.12 in the pinned container")
    if not Path("/proc/self/status").is_file():
        raise SystemExit("Peak-RSS measurement requires Linux /proc")
    summary = json.loads(SOURCE_SUMMARY.read_text(encoding="utf-8"))
    inputs = verify_inputs(summary)
    started_at = datetime.now(timezone.utc).isoformat()
    runs = []
    with tempfile.TemporaryDirectory(prefix="atlas-raster-benchmark-") as temp:
        for index in range(3):
            runs.append(run_once(Path(temp) / f"run-{index + 1}"))
    output_hash_pairs = {(run["observation_qa_sha256"], run["comparison_sha256"]) for run in runs}
    elapsed = [run["wall_seconds"] for run in runs]
    throughput = len(runs) * 60 / sum(elapsed)
    max_memory = max(run["peak_rss_bytes"] for run in runs)
    result = {
        "schema_version": 1,
        "benchmark_id": "atlas-raster-workload-performance",
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "contract": "outputs/atlas-raster-workload-performance-contract.md",
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count_visible": os.cpu_count(),
        "cgroup_cpu_max": cgroup_value("/sys/fs/cgroup/cpu.max"),
        "cgroup_memory_limit_bytes": cgroup_value("/sys/fs/cgroup/memory.max"),
        "packages": {},
        "dataset": summary["dataset"],
        "study_scope": "outside registered 8+8 candidate areas; technical pilot only",
        "analysis_script_sha256": sha256(ANALYZER),
        "inputs": inputs,
        "targets": {
            "max_latency_seconds": TARGET_LATENCY_SECONDS,
            "max_peak_memory_bytes": TARGET_MEMORY_BYTES,
            "min_serial_jobs_per_minute": TARGET_JOBS_PER_MINUTE,
            "runs": 3,
        },
        "runs": runs,
        "summary": {
            "median_wall_seconds": round(median(elapsed), 6),
            "max_wall_seconds": round(max(elapsed), 6),
            "serial_jobs_per_minute": round(throughput, 3),
            "max_peak_rss_bytes": max_memory,
            "all_qa_outputs_identical": len(output_hash_pairs) == 1,
            "all_comparison_gates_identical": len({run["comparison_status"] for run in runs}) == 1,
        },
        "passed_contract": (
            max(elapsed) <= TARGET_LATENCY_SECONDS
            and max_memory < TARGET_MEMORY_BYTES
            and throughput >= TARGET_JOBS_PER_MINUTE
            and len(output_hash_pairs) == 1
            and all(run["comparison_status"] == "unknown_insufficient_qa_valid_dates" for run in runs)
        ),
        "limitations": [
            "Local bounded performance check; no deployed service, concurrent-user, network, or production-scale raster test.",
            "No metered cloud cost was incurred or estimated; this does not satisfy canonical performance or scalability criteria by itself.",
            "Pilot mosaics are preliminary/unvalidated and outside the registered 8+8 sites; no scientific validation is implied.",
        ],
    }
    try:
        import numpy
        import rasterio
        result["packages"] = {"numpy": numpy.__version__, "rasterio": rasterio.__version__}
    except ImportError as exc:
        raise SystemExit(f"Required geospatial package missing: {exc}") from exc
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("python", "platform", "machine", "cpu_count_visible", "cgroup_cpu_max", "cgroup_memory_limit_bytes", "packages", "summary", "passed_contract", "limitations")}, indent=2))
    print(f"Saved {OUTPUT.relative_to(ROOT)}")
    if not result["passed_contract"]:
        raise SystemExit("Raster workload performance contract failed")


if __name__ == "__main__":
    main()
