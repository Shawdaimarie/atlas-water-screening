#!/usr/bin/env python3
"""Validate the non-secret ATLAS four-cloud onboarding handoff, without provisioning."""

from __future__ import annotations

import argparse
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import yaml


DEFAULT_INPUT = Path("deployment/cloud/owner-inputs.local.yaml")
EXAMPLE_INPUT = Path("deployment/cloud/owner-inputs.example.yaml")
PROVIDER_FIELDS = {
    "google_cloud": {
        "identifiers": ("project_id",),
        "billing": "billing_account_confirmed",
        "region": "region",
        "identity": "workload_identity_provider_ready",
    },
    "aws": {
        "identifiers": ("account_id",),
        "billing": "billing_confirmed",
        "region": "region",
        "identity": "github_oidc_role_ready",
    },
    "microsoft_azure": {
        "identifiers": ("tenant_id", "subscription_id"),
        "billing": "billing_confirmed",
        "region": "region",
        "identity": "entra_federated_identity_ready",
    },
    "oracle_cloud": {
        "identifiers": ("tenancy_ocid", "compartment_ocid"),
        "billing": "billing_confirmed",
        "region": "home_region",
        "identity": "github_oidc_and_registry_identity_ready",
    },
}
IDENTIFIER_PATTERNS = {
    ("google_cloud", "project_id"): re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$"),
    ("aws", "account_id"): re.compile(r"^\d{12}$"),
    ("microsoft_azure", "tenant_id"): re.compile(
        r"^[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$"
    ),
    ("microsoft_azure", "subscription_id"): re.compile(
        r"^[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$"
    ),
    ("oracle_cloud", "tenancy_ocid"): re.compile(
        r"^ocid1\.tenancy\.[a-z0-9-]+\.\.[a-z0-9]+$"
    ),
    ("oracle_cloud", "compartment_ocid"): re.compile(
        r"^ocid1\.compartment\.[a-z0-9-]+\.\.[a-z0-9]+$"
    ),
}
FORBIDDEN_KEY_PARTS = (
    "password",
    "secret",
    "token",
    "private_key",
    "privatekey",
    "access_key",
    "accesskey",
    "recovery_code",
    "mfa_code",
    "mfa_seed",
    "payment",
    "card_number",
    "credential_value",
    "credential",
    "api_key",
    "bearer",
    "auth_header",
)


def _filled(value: Any) -> bool:
    return value is not None and str(value).strip() not in {"", "pending", "undecided"}


def _secret_paths(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            normalized = str(key).lower().replace("-", "_")
            if any(part in normalized for part in FORBIDDEN_KEY_PARTS):
                found.append(path)
            found.extend(_secret_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_secret_paths(child, f"{prefix}[{index}]"))
    return found


def validate_inputs(data: Any, release_ready: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be a YAML mapping"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1")

    secrets = _secret_paths(data)
    if secrets:
        errors.append("remove secret-like fields: " + ", ".join(sorted(secrets)))

    owner = data.get("owner") if isinstance(data.get("owner"), dict) else {}
    for field in (
        "apple_account_role",
        "data_residency_decision",
        "staging_production_boundary",
    ):
        if not _filled(owner.get(field)):
            errors.append(f"owner.{field} must be recorded")
    if release_ready and not _filled(owner.get("approved_api_hostname")):
        errors.append("owner.approved_api_hostname must be recorded for release readiness")

    budget = data.get("budget") if isinstance(data.get("budget"), dict) else {}
    if not re.fullmatch(r"[A-Z]{3}", str(budget.get("currency", ""))):
        errors.append("budget.currency must be a three-letter uppercase code")
    try:
        ceiling