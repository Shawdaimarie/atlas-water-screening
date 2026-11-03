#!/usr/bin/env python3
"""Measure a balanced, exploratory sample of real Sentinel-1 RTC pixel coverage.

This screens data availability only. It does not classify floodwater or validate
OPERA DSWx-S1. Planetary Computer SAS URLs are held in memory and never written
to the report, cache, log, or source tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError


STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION = "sentinel-1-rtc"
WINDOW_START = "2025-01-01T00:00:00Z"
WINDOW_END = "2025-12-31T23:59:59Z"
SAMPLE_SEED = "ATLAS-S1RTC-quarterly-coverage-v1"
TARGET_RESOLUTION_M = 10.0
MIN_VALID_FRACTION = 0.80
_SAS_TOKENS: dict[tuple[str, str], str] = {}


def _request_json(url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Accept": "application/geo+json, application/json",
                 **({"Content-Type": "application/json"} if data is not None else {})},
    )
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                value = json.load(response)
            break
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 5:
                raise
            retry_after = exc.headers.get("Retry-After", "")
            try:
                delay = min(60.0, max(1.0, float(retry_after)))
            except ValueError:
                delay = min(30.0, 2.0 ** attempt)
            time.sleep(delay)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object from the public data API")
    return value


def _items_for_area(bbox: list[float]) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {
        "collections": [COLLECTION], "bbox": bbox,
        "datetime": f"{WINDOW_START}/{WINDOW_END}", "limit": 100,
    }
    items: list[dict[str, Any]] = []
    while True:
        page = _request_json(f"{STAC}/search", payload)
        items.extend(page.get("features", []))
        next_link = next((link for link in page.get("links", []) if link.get("rel") == "next"), None)
        if not next_link:
            return items
        if next_link.get("method", "GET").upper() == "POST":
            payload = next_link.get("body") or {}
            url = next_link["href"]
            page = _request_json(url, payload)
        else:
            url = next_link["href"]
            page = _request_json(url)
        items.extend(page.get("features", []))
        while True:
            next_link = next((link for link in page.get("links", []) if link.get("rel") == "next"), None)
            if not next_link:
                return items
            if next_link.get("method", "GET").upper() == "POST":
                url = next_link["href"]
                payload = next_link.get("body") or {}
                page = _request_json(url, payload)
            else:
                page = _request_json(next_link["href"])
            items.extend(page.get("features", []))


def _orbit_groups(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        props = item.get("properties") or {}
        stamp = str(props.get("datetime", ""))
        if not stamp or "vv" not in (item.get("assets") or {}):
            continue
        day = date.fromisoformat(stamp[:10])
        if not (date(2025, 1, 1) <= day <= date(2025, 12, 31)):
            continue
        orbit = props.get("sat:absolute_orbit")
        platform = props.get("platform")
        if orbit is None or not platform:
            continue
        group_id = f"{day.isoformat()}|{platform}|{props.get('sat:orbit