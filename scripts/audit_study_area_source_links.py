#!/usr/bin/env python3
"""Check reachability of primary and secondary public study-area evidence URLs."""
from __future__ import annotations

import concurrent.futures
import datetime as dt
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/study_area_evidence.json"
OUTPUT = ROOT / "outputs/atlas-study-area-source-link-audit-2026-11-04.json"
REPORT = ROOT / "outputs/atlas-study-area-source-link-audit-2026-11-04.md"


def check_url(city: str, kind: str, url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "ATLAS-public-source-link-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            sample = response.read(1024)
            status = response.status
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type")
        return {
            "city": city,
            "kind": kind,
            "url": url,
            "status": status,
            "final_url": final_url,
            "content_type": content_type,
            "bytes_sampled": len(sample),
            "error": None,
            "assessment": "Direct HTTP GET returned a 2xx response; reachability only.",
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        code = getattr(exc, "code", None)
        return {
            "city": city,
            "kind": kind,
            "url": url,
            "status": code,
            "final_url": None,
            "content_type": None,
            "bytes_sampled": 0,
            "error": str(exc),
            "assessment": "Direct HTTP GET did not return a successful response; inspect the error.",
        }


def build_audit(source: dict, source_bytes: bytes) -> dict:
    records = source["records"]
    if len(records) != 16 or len({r["city"] for r in records}) != 16:
        raise ValueError("Expected exactly one evidence profile for each of the 16 study areas")
    jobs = []
    for record in records:
        jobs.append((record["city"], "primary", record["evidence_url"]))
        if record.get("secondary_evidence_url"):
            jobs.append((record["city"], "secondary", record["secondary_evidence_url"]))
        if record.get("current_official_hotspot_url"):
            jobs.append((record["city"], "official_hotspot", record["current_official_hotspot_url"]))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda job: check_url(*job), jobs))
    primary = [row for row in results if row["kind"] == "primary"]
    secondary = [row for row in results if row["kind"] == "secondary"]
    official_hotspots = [row for row in results if row["kind"] == "official_hotspot"]
    return {
        "run_date": dt.datetime.now(dt.timezone.utc).date().isoformat(),
        "source_file": "data/study_area_evidence.json",
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "area_count": len(records),
        "primary_url_count": len(primary),
        "secondary_url_count": len(secondary),
        "official_hotspot_url_count": len(official_hotspots),
        "interpretation": (
            "Reachability checks do not validate the truth, date, spatial scope, completeness, "
            "local applicability, or licensing of each empirical claim. They do not establish "
            "flood observations, independent labels, confirmatory eligibility, or customer demand."
        ),
        "results": primary,
        "secondary_results": secondary,
        "official_hotspot_results": official_hotspots,
        "reachability_summary": {
            "primary_http_2xx": sum(200 <= (r["status"] or 0) < 300 for r in primary),
            "primary_failures": sum(not (200 <= (r["status"] or 0) < 300) for r in primary),
            "secondary_http_2xx": sum(200 <= (r["status"] or 0) < 300 for r in secondary),
            "secondary_failures": sum(not (200 <= (r["status"] or 0) < 300) for r in secondary),
            "official_hotspot_http_2xx": sum(200 <= (r["status"] or 0) < 300 for r in official_hotspots),
            "official_hotspot_failures": sum(not (200 <= (r["status"] or 0) < 300) for r in official_hotspots),
        },
    }


def main() -> None:
    raw = SOURCE.read_bytes()
    audit = build_audit(json.loads(raw), raw)
    OUTPUT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = audit["reachability_summary"]
    report = [
        "# 8+8 study-area evidence-link audit",
        "",
        f"**Run:** {audit['run_date']}  ",
        "**Source register:** `data/study_area_evidence.json`  ",
        f"**Areas:** {audit['area_count']}  ",
        f"**Primary, secondary, and official hotspot URLs checked:** {audit['primary_url_count']} + {audit['secondary_url_count']} + {audit['official_hotspot_url_count']}",
        "",
        "## Results",
        "",
        f"- Primary evidence URLs returning HTTP 2xx: **{summary['primary_http_2xx']}/{audit['primary_url_count']}**.",
        f"- Secondary evidence URLs returning HTTP 2xx: **{summary['secondary_http_2xx']}/{audit['secondary_url_count']}**.",
        f"- Current official hotspot-list URLs returning HTTP 2xx: **{summary['official_hotspot_http_2xx']}/{audit['official_hotspot_url_count']}**.",
        "- No result is treated as evidence of flood truth, AOI coverage, or scientific validation.",
        "",
        "## Interpretation limits",
        "",
        audit["interpretation"],
        "",
        "The Sacramento City flood-management plan documents 2017 event response outside the shared 2024–2026 observation window. The City's levee-break maps are modeled planning scenarios. Neither source supplies reference pixels for the fixed ATLAS AOI.",
        "",
        f"Machine-readable responses and source checksum: [JSON audit]({OUTPUT.name}).",
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(audit["reachability_summary"], sort_keys=True))


if __name__ == "__main__":
    main()
