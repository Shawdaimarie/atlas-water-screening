#!/usr/bin/env python3
"""Exercise required HTTP workflows against a running ATLAS API container."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


def request(base: str, path: str, *, method: str = "GET", body: bytes | None = None,
            headers: dict[str, str] | None = None):
    req = urllib.request.Request(base.rstrip("/") + path, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, {key.lower(): value for key, value in response.headers.items()}, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, {key.lower(): value for key, value in exc.headers.items()}, exc.read()


def wait_for_health(base: str, timeout_seconds: float) -> None:
    """Wait for a newly started container without hiding an unhealthy service."""
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | str = "health endpoint did not return HTTP 200"
    while time.monotonic() < deadline:
        try:
            status, _, body = request(base, "/api/health")
            health = json.loads(body) if status == 200 else {}
            if status == 200 and health.get("status") == "ok":
                return
            last_error = f"health endpoint returned HTTP {status}"
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
            last_error = exc
        time.sleep(0.25)
    raise TimeoutError(f"API did not become healthy within {timeout_seconds:g}s: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:18081")
    parser.add_argument("--startup-timeout", type=float, default=30.0)
    args = parser.parse_args()
    wait_for_health(args.base_url, args.startup_timeout)
    checks: list[tuple[str, bool, int]] = []

    status, _, body = request(args.base_url, "/api/health")
    checks.append(("health", status == 200 and json.loads(body)["live_nasa_ingestion"] is False, status))
    status, _, body = request(args.base_url, "/api/areas")
    checks.append(("areas", status == 200 and len(json.loads(body)) == 2, status))
    status, _, body = request(args.base_url, "/api/study-areas")
    study_register = json.loads(body) if status == 200 else {}
    candidate_areas = study_register.get("areas", [])
    checks.append(("study-area-register", status == 200 and len(candidate_areas) == 16 and
                   sum(area["region"] == "United States" for area in candidate_areas) == 8 and
                   sum(area["region"] == "International" for area in candidate_areas) == 8 and
                   study_register.get("analysis_ready") is False, status))

    headers = {"Content-Type": "application/json"}
    status, _, body = request(args.base_url, "/api/analyses", method="POST",
                              body=b'{"method":"aggregate"}', headers=headers)
    result = json.loads(body)
    checks.append(("analysis", status == 200 and result["asset_count"] == 12 and
                   result["ranked_assets"][0]["observed_overlap_pct"] == 21.4 and
                   result["provenance"]["data_mode"] == "synthetic_fixture", status))

    status, _, body = request(args.base_url, "/api/exports/csv", method="POST",
                              body=b'{"method":"single"}', headers=headers)
    checks.append(("csv-export", status == 200 and body.startswith(b"asset_id,") and
                   b"TX-001" in body, status))

    status, _, body = request(args.base_url, "/api/analyses", method="POST",
                              body=b'{"image_url":"http://127.0.0.1:9"}', headers=headers)
    checks.append(("unknown-field-rejected", status == 422, status))
    status, _, _ = request(args.base_url, "/api/analyses", method="POST",
                           body=b" " * 16385, headers=headers)
    checks.append(("body-limit", status == 413, status))
    status, _, _ = request(args.base_url, "/api/analyses", method="POST",
                           body=b"{invalid", headers=headers)
    checks.append(("invalid-json", status == 422, status))
    status, _, _ = request(args.base_url, "/api/health", headers={"Host": "attacker.example"})
    checks.append(("host-allowlist", status == 400, status))

    preflight = {"Origin": "http://localhost:8000", "Access-Control-Request-Method": "GET"}
    status, headers_out, _ = request(args.base_url, "/api/health", method="OPTIONS", headers=preflight)
    checks.append(("cors-allow", status == 200 and headers_out.get("access-control-allow-origin") ==
                   "http://localhost:8000", status))
    preflight["Origin"] = "http://evil.example"
    status, _, _ = request(args.base_url, "/api/health", method="OPTIONS", headers=preflight)
    checks.append(("cors-deny", status == 400, status))

    for name, passed, code in checks:
        print(f"{name}: {'PASS' if passed else 'FAIL'} (HTTP {code})")
    print(f"Summary: {sum(ok for _, ok, _ in checks)}/{len(checks)} checks passed")
    return 0 if all(ok for _, ok, _ in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
