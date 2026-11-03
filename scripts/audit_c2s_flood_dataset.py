#!/usr/bin/env python3
"""Screen Cloud to Street's public hand-labeled SAR chips against ATLAS AOIs."""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_bounds, transform_geom


BUCKET_URL = "https://radiant-mlhub.s3.us-west-2.amazonaws.com/"
PREFIX = "c2smsfloods/chips/"
DATASET_URL = "https://registry.opendata.aws/c2smsfloods/"
DOC_URL = "https://radiantearth.blob.core.windows.net/mlhub/c2smsfloods/ms-dataset_README.pdf"
DATE_PATTERN = re.compile(r"_(\d{8})T\d{6}_")
S3_NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}


def list_s1_label_keys() -> list[str]:
    """List every Sentinel-1 hand-label GeoTIFF without downloading the raster set."""
    keys: list[str] = []
    token: str | None = None
    while True:
        query = {"list-type": "2", "prefix": PREFIX}
        if token:
            query["continuation-token"] = token
        request = urllib.request.Request(
            BUCKET_URL + "?" + urllib.parse.urlencode(query),
            headers={"User-Agent": "ATLAS-C2S-coverage-audit/1.0"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            root = ET.fromstring(response.read())
        keys.extend(
            key
            for entry in root.findall("s3:Contents", S3_NS)
            if (key := entry.findtext("s3:Key", namespaces=S3_NS))
            and "/s1/" in key
            and key.endswith("/LabelWater.tif")
        )
        if root.findtext("s3:IsTruncated", namespaces=S3_NS) != "true":
            break
        token = root.findtext("s3:NextContinuationToken", namespaces=S3_NS)
        if not token:
            raise RuntimeError("S3 listing was truncated without a continuation token")
    return keys


def parse_label_key(key: str) -> tuple[str, str, str]:
    parts = key.split("/")
    if len(parts) < 6 or parts[-3] != "s1" or parts[-1] != "LabelWater.tif":
        raise ValueError(f"Not a Sentinel-1 LabelWater path: {key}")
    event_id = parts[-4]
    scene_chip = parts[-2]
    match = DATE_PATTERN.search(scene_chip)
    if not match:
        raise ValueError(f"Sentinel acquisition date missing from {scene_chip}")
    date = datetime.strptime(match.group(1), "%Y%m%d").date().isoformat()
    return event_id, scene_chip, date


def area_geometry(area: dict) -> dict:
    xmin, ymin, xmax, ymax = map(float, area["aoi_bbox_wgs84"].split(","))
    return {
        "type": "Polygon",
        "coordinates": [[
            [xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax], [xmin, ymin]
        ]],
    }


def area_key(area: dict) -> str:
    return f"{area['region']}/{area['city']}"


def inspect_chip(key: str, areas: list[dict]) -> dict:
    event_id, scene_chip, date = parse_label_key(key)
    url = BUCKET_URL + urllib.parse.quote(key, safe="/")
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
    ):
        with rasterio.open("/vsicurl/" + url) as dataset:
            if not dataset.crs:
                raise ValueError(f"Missing CRS: {key}")
            bounds = transform_bounds(dataset.crs, "EPSG:4326", *dataset.bounds)
            matches = []
            for area in areas:
                xmin, ymin, xmax, ymax = map(
                    float, area["aoi_bbox_wgs84"].split(",")
                )
                if bounds[0] >= xmax or bounds[2] <= xmin or bounds[1] >= ymax or bounds[3] <= ymin:
                    continue
                clipped_geom = transform_geom(
                    "EPSG:4326", dataset.crs, area_geometry(area)
                )
                try:
                    clipped, _ = mask(dataset, [clipped_geom], crop=True)
                except ValueError:
                    continue
       