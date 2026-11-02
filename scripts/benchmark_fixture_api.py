"""Repeatable local-only benchmark for the synthetic 12-row fixture API.

Predeclared acceptance target: local POST /api/analyses latency p95 < 100 ms
on this recorded machine, after 25 warmups and over 500 sequential requests.
This does not represent cloud latency, raster processing, or a production SLO.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import statistics
import time
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8017"
PAYLOAD = b'{"area_id":"houston_fixture","method":"aggregate","min_coverage_pct":50}'


def request_once():
    req = Request(
        BASE_URL + "/api/analyses",
        data=PAYLOAD,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    with urlopen(req, timeout=5) as response:
        body = json.load(response)
        status = response.status
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert status == 200 and body["asset_count"] == 12
    return elapsed_ms


def percentile(values, p):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * p))]


def main():
    for _ in range(25):
        request_once()

    sequential = [request_once() for _ in range(500)]
    start = time.perf_counter()
    concurrent = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(request_once) for _ in range(1000)]
        for future in as_completed(futures):
            concurrent.append(future.result())
    elapsed = time.perf_counter() - start

    result = {
        "target": {"sequential_p95_ms_lt": 100},
        "environment": "local Uvicorn API at 127.0.0.1:8017; synthetic 12-row payload",
        "warmups": 25,
        "sequential_requests": len(sequential),
        "sequential_median_ms": round(statistics.median(sequential), 3),
        "sequential_p95_ms": round(percentile(sequential, 0.95), 3),
        "concurrent_requests": len(concurrent),
        "concurrency": 8,
        "concurrent_elapsed_s": round(elapsed, 3),
        "concurrent_requests_per_second": round(len(concurrent) / elapsed, 2),
        "concurrent_p95_ms": round(percentile(concurrent, 0.95), 3),
        "result": "PASS" if percentile(sequential, 0.95) < 100 else "FAIL",
        "limitations": "No raster workload, cloud network, billed cost, or production capacity is represented.",
    }
    print(json.dumps(result, indent=2))
    if result["result"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
