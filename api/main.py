"""ATLAS local demo API. All fixture records are synthetic, not NASA observations."""
from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

MAX_REQUEST_BYTES = 16 * 1024


class _BodyTooLarge(Exception):
    pass


class RequestBodyLimitMiddleware:
    """Reject oversized JSON bodies, including chunked requests without a length."""
    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        content_length = dict(scope.get("headers", [])).get(b"content-length")
        if content_length:
            try:
                if int(content_length) > self.max_bytes:
                    await self._too_large(scope, receive, send)
                    return
            except ValueError:
                await JSONResponse({"detail": "Invalid Content-Length"}, status_code=400)(scope, receive, send)
                return

        received = 0

        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise _BodyTooLarge()
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _BodyTooLarge:
            await self._too_large(scope, receive, send)

    async def _too_large(self, scope, receive, send):
        response = JSONResponse({"detail": f"Request body exceeds {self.max_bytes} bytes"}, status_code=413)
        await response(scope, receive, send)


def configured_cors_origins() -> list[str]:
    """Read exact browser origins; never accept wildcard CORS in production."""
    configured = os.getenv("ATLAS_CORS_ORIGINS")
    if configured is None:
        return ["http://127.0.0.1:8000", "http://localhost:8000"]
    origins = [value.strip().rstrip("/") for value in configured.split(",") if value.strip()]
    if not origins or "*" in origins:
        raise RuntimeError("ATLAS_CORS_ORIGINS must contain exact, non-wildcard origins")
    return origins


def configured_allowed_hosts() -> list[str]:
    """Require an exact host allowlist for deployed API instances."""
    configured = os.getenv("ATLAS_ALLOWED_HOSTS")
    if configured is None:
        return ["localhost", "127.0.0.1", "testserver"]
    hosts = [value.strip().lower() for value in configured.split(",") if value.strip()]
    if not hosts or "*" in hosts:
        raise RuntimeError("ATLAS_ALLOWED_HOSTS must contain exact, non-wildcard hosts")
    return hosts


class Asset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: str
    asset_name: str
    asset_type: str
    single_overlap_pct: float = Field(ge=0, le=100)
    aggregate_overlap_pct: float = Field(ge=0, le=100)
    valid_coverage_pct: float = Field(ge=0, le=100)
    confidence_pct: int = Field(ge=0, le=100)


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    area_id: Literal["houston_fixture", "baton_rouge_fixture"] = "houston_fixture"
    method: Literal["single", "aggregate"] = "single"
    min_coverage_pct: float = Field(default=50, ge=0, le=100)


DATA = [
    ("TX-001", "Bayou East Substation", "Electric substation", 28.6, 21.4, 96, 78),
    ("TX-002", "Southeast Water Plant", "Water treatment", 23.1, 18.9, 93, 73),
    ("TX-003", "South Loop Pump Station", "Pump station", 18.4, 12.2, 89, 69),
    ("TX-004", "Ship Channel Rail Yard", "Rail infrastructure", 14.2, 9.8, 92, 66),
    ("TX-005", "Central Grid Feeder", "Electric distribution", 9.7, 8.1, 95, 72),
    ("TX-006", "Port Access Bridge", "Road bridge", 8.4, 6.4, 88, 64),
    ("TX-007", "North Creek Reservoir", "Water storage", 6.9, 7.1, 90, 70),
    ("TX-008", "Westside Lift Station", "Pump station", 5.3, 4.9, 84, 59),
    ("TX-009", "East Beltway Interchange", "Road infrastructure", 3.8, 3.4, 92, 71),
    ("TX-010", "Medical District Feeder", "Electric distribution", 2.1, 1.9, 91, 68),
    ("TX-011", "Cypress Water Storage", "Water storage", 1.6, 1.4, 87, 62),
    ("TX-012", "Airport Cargo Apron", "Transport infrastructure", 0.8, 0.7, 95, 75),
]

_REGISTER_PATH = Path(__file__).resolve().parents[1] / "data" / "study_area_register.json"
_REGISTER = json.loads(_REGISTER_PATH.read_text())
_STUDY_AREAS = _REGISTER.get("results", [])
_EVIDENCE_PATH = Path(__file__).resolve().parents[1] / "data" / "study_area_evidence.json"
_EVIDENCE = json.loads(_EVIDENCE_PATH.read_text()).get("records", [])
_EVIDENCE_BY_CITY = {record["city"]: record for record in _EVIDENCE}
if (
    len(_STUDY_AREAS) != 16
    or sum(area.get("region") == "United States" for area in _STUDY_AREAS) != 8
    or sum(area.get("region") == "International" for area in _STUDY_AREAS) != 8
    or set(_EVIDENCE_BY_CITY) != {area.get("city") for area in _STUDY_AREAS}
):
    raise RuntimeError("Study-area register and evidence profiles must match exactly 8 U.S. and 8 international candidates")


def make_rows(req: AnalysisRequest):
    rows = []
    for row in DATA:
        a = Asset(
            asset_id=row[0], asset_name=row[1], asset_type=row[2],
            single_overlap_pct=row[3], aggregate_overlap_pct=row[4],
            valid_coverage_pct=row[5], confidence_pct=row[6],
        )
        if a.valid_coverage_pct < req.min_coverage_pct:
            continue
        overlap = a.single_overlap_pct if req.method == "single" else a.aggregate_overlap_pct
        record = a.model_dump()
        if req.area_id == "baton_rouge_fixture":
            record["asset_id"] = record["asset_id"].replace("TX-", "LA-")
        rows.append({**record, "observed_overlap_pct": overlap, "status": "synthetic_fixture", "is_unknown": False})
    rows.sort(key=lambda x: x["observed_overlap_pct"], reverse=True)
    return rows


async def _validated_request(request: Request) -> AnalysisRequest | JSONResponse:
    try:
        payload = await request.json()
        return AnalysisRequest.model_validate(payload)
    except ValidationError as exc:
        return JSONResponse({"detail": exc.errors(include_context=False)}, status_code=422)
    except (ValueError, UnicodeDecodeError):
        return JSONResponse({"detail": "Invalid JSON body"}, status_code=422)


async def health(request: Request):
    return JSONResponse({"status": "ok", "data_mode": "synthetic_fixture", "live_nasa_ingestion": False})


async def areas(request: Request):
    return JSONResponse([
        {"area_id": "houston_fixture", "label": "Houston, Texas", "data_mode": "synthetic_fixture"},
        {"area_id": "baton_rouge_fixture", "label": "Baton Rouge, Louisiana", "data_mode": "synthetic_fixture"},
    ])


async def study_areas(request: Request):
    """Return candidate register entries without implying pixel or event validation."""
    fields = {
        "region": "region",
        "city": "city",
        "latitude": "lat",
        "longitude": "lon",
        "rationale": "screening_rationale",
        "value_integration_question": "value_integration_question",
        "evidence_url": "evidence_url",
        "need_evidence_type": "need_evidence_type",
        "empirical_evidence": "empirical_evidence",
        "public_value_dimensions": "public_value_dimensions",
        "validation_path": "validation_path",
        "evidence_limit": "evidence_limit",
        "supporting_evidence_url": "supporting_evidence_url",
        "aoi_bbox_wgs84": "aoi_bbox_wgs84",
        "aoi_area_km2": "aoi_area_km2",
        "collection": "collection",
        "temporal_start": "temporal_start",
        "temporal_end": "temporal_end",
        "metadata_granule_hits": "cmr_granule_hits",
        "metadata_acquisition_dates": "unique_acquisition_dates",
        "returned_entries_complete": "returned_entries_complete",
        "status": "status",
    }
    return JSONResponse({
        "data_mode": "archive_metadata_only",
        "analysis_ready": False,
        "disclaimer": "CMR metadata discovery does not establish QA-valid pixels, flood-event coverage, or independent reference labels.",
        "areas": [
            {
                **{output: area[source] for output, source in fields.items() if source in area},
                "need_evidence_type": _EVIDENCE_BY_CITY[area["city"]]["evidence_type"],
                "empirical_evidence": _EVIDENCE_BY_CITY[area["city"]]["empirical_evidence"],
                "public_value_dimensions": _EVIDENCE_BY_CITY[area["city"]]["value_dimensions"],
                "validation_path": _EVIDENCE_BY_CITY[area["city"]]["validation_path"],
                "evidence_limit": _EVIDENCE_BY_CITY[area["city"]]["scope_limit"],
                "supporting_evidence_url": _EVIDENCE_BY_CITY[area["city"]].get("secondary_evidence_url"),
                "analysis_ready": False,
            }
            for area in _STUDY_AREAS
        ],
    })


async def analyze(request: Request):
    req = await _validated_request(request)
    if isinstance(req, JSONResponse):
        return req
    rows = make_rows(req)
    return JSONResponse({
        "area_id": req.area_id,
        "event": "illustrative historical event",
        "method": req.method,
        "unit": "asset-event",
        "asset_count": len(rows),
        "ranked_assets": rows,
        "provenance": {
            "data_mode": "synthetic_fixture",
            "live_nasa_ingestion": False,
            "product_schema_reference": "OPERA DSWx-S1 V1; no source granule loaded",
            "quality_policy": "fixture coverage field used; no actual OPERA masks loaded",
            "threshold_percent": 10,
        },
        "warning": "Observed overlap in this fixture is not proof of damage, service interruption, structural failure, or financial loss.",
    })


async def export(request: Request):
    req = await _validated_request(request)
    if isinstance(req, JSONResponse):
        return req
    rows = make_rows(req)
    out = io.StringIO()
    fields = ["asset_id", "asset_name", "asset_type", "observed_overlap_pct", "valid_coverage_pct", "confidence_pct", "status"]
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row[key] for key in fields})
    return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=atlas-synthetic-fixture.csv"})


app = Starlette(
    debug=False,
    routes=[
        Route("/api/health", health, methods=["GET"]),
        Route("/api/areas", areas, methods=["GET"]),
        Route("/api/study-areas", study_areas, methods=["GET"]),
        Route("/api/analyses", analyze, methods=["POST"]),
        Route("/api/exports/csv", export, methods=["POST"]),
    ],
    middleware=[
        Middleware(CORSMiddleware, allow_origins=configured_cors_origins(), allow_methods=["GET", "POST"], allow_headers=["Content-Type"]),
        Middleware(TrustedHostMiddleware, allowed_hosts=configured_allowed_hosts()),
        Middleware(RequestBodyLimitMiddleware, max_bytes=MAX_REQUEST_BYTES),
    ],
)
