#!/usr/bin/env python3
"""Screen latest public UFO PlanetScope label-chip footprints against ATLAS AOIs."""

from __future__ import annotations

import argparse
import json
import math
import struct
import urllib.request
import zlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ZENODO_CONCEPT_RECORD = "15238469"
ZENODO_API = f"https://zenodo.org/api/records/{ZENODO_CONCEPT_RECORD}/versions/latest"
DATASET_DOI = "https://doi.org/10.5281/zenodo.15238469"
EOCD = bytes([0x50, 0x4B, 0x05, 0x06])
CENTRAL_SIG = bytes([0x50, 0x4B, 0x01, 0x02])
LOCAL_SIG = bytes([0x50, 0x4B, 0x03, 0x04])


def request_bytes(url: str, start: int, end: int, timeout: int = 45) -> tuple[bytes, int]:
    request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_range = response.headers.get("Content-Range", "")
        total = int(content_range.rsplit("/", 1)[1])
        return response.read(), total


def request_suffix(url: str, length: int, timeout: int = 45) -> tuple[bytes, int]:
    request = urllib.request.Request(url, headers={"Range": f"bytes=-{length}"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_range = response.headers.get("Content-Range", "")
        total = int(content_range.rsplit("/", 1)[1])
        return response.read(), total


def zip_entries(url: str) -> tuple[list[dict], int]:
    tail, total_size = request_suffix(url, 65_557)
    marker = tail.rfind(EOCD)
    if marker < 0:
        raise ValueError("ZIP end-of-central-directory record is missing")
    _, _, _, _, file_count, directory_size, directory_offset, _ = struct.unpack(
        "<4s4H2IH", tail[marker : marker + 22]
    )
    directory, _ = request_bytes(url, directory_offset, directory_offset + directory_size - 1)
    entries = []
    offset = 0
    fmt = "<4s6H3I5H2I"
    header_size = struct.calcsize(fmt)
    while offset < len(directory):
        fields = struct.unpack(fmt, directory[offset : offset + header_size])
        if fields[0] != CENTRAL_SIG:
            raise ValueError("Malformed ZIP central directory")
        filename_length, extra_length, comment_length = fields[10:13]
        filename = directory[offset + header_size : offset + header_size + filename_length].decode("utf-8")
        entries.append({
            "name": filename,
            "method": fields[4],
            "compressed_size": fields[8],
            "uncompressed_size": fields[9],
            "local_header_offset": fields[-1],
        })
        offset += header_size + filename_length + extra_length + comment_length
    if len(entries) != file_count:
        raise ValueError(f"ZIP central directory lists {len(entries)} entries; EOCD says {file_count}")
    return entries, total_size


def zip_read_member(url: str, entry: dict) -> bytes:
    start = entry["local_header_offset"]
    header, _ = request_bytes(url, start, start + 29)
    fields = struct.unpack("<4s5H3I2H", header)
    if fields[0] != LOCAL_SIG:
        raise ValueError(f"Malformed local ZIP header for {entry['name']}")
    filename_length, extra_length = fields[-2:]
    start += 30 + filename_length + extra_length
    end = start + entry["compressed_size"] - 1
    payload, _ = request_bytes(url, start, end)
    if entry["method"] == 0:
        return payload
    if entry["method"] == 8:
        return zlib.decompress(payload, -15)
    raise ValueError(f"Unsupported ZIP compression method {entry['method']}")


def zip_read_contiguous_members(url: str, entries: list[dict]) -> dict[str, bytes]:
    """Read adjacent ZIP members with one HTTP range request."""
    if not entries:
        return {}
    ordered = sorted(entries, key=lambda entry: entry["local_header_offset"])
    start = ordered[0]["local_header_offset"]
    end = ordered[-1]["local_header_offset"] + 30 + len(ordered[-1]["name"].encode("utf-8")) + ordered[-1]["compressed_size"] - 1
    data, _ = request_bytes(url, start, end)
    result = {}
    for entry in ord