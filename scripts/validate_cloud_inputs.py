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
        ceiling = Decimal(str(budget.get("monthly_ceiling", "")))
        if not ceiling.is_finite() or ceiling <= 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        errors.append("budget.monthly_ceiling must be a positive number")
    thresholds = budget.get("alert_thresholds_percent")
    if not isinstance(thresholds, list) or not thresholds:
        errors.append("budget.alert_thresholds_percent must include at least one threshold")
    elif any(
        not isinstance(value, (int, float)) or isinstance(value, bool) or not 1 <= value <= 100
        for value in thresholds
    ):
        errors.append("budget.alert_thresholds_percent values must be numbers from 1 to 100")
    recipients = budget.get("alert_recipient_emails")
    if not isinstance(recipients, list) or not recipients or any(
        not isinstance(value, str) or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value)
        for value in recipients
    ):
        errors.append("budget.alert_recipient_emails must contain at least one valid email")

    providers = data.get("providers") if isinstance(data.get("providers"), dict) else {}
    for provider, fields in PROVIDER_FIELDS.items():
        entry = providers.get(provider)
        if not isinstance(entry, dict):
            errors.append(f"providers.{provider} section is required")
            continue
        if entry.get("account_ready") is not True:
            errors.append(f"providers.{provider}.account_ready must be true")
        for field in fields["identifiers"]:
            value = entry.get(field)
            if not _filled(value):
                errors.append(f"providers.{provider}.{field} is required")
            elif not IDENTIFIER_PATTERNS[(provider, field)].fullmatch(str(value)):
                errors.append(f"providers.{provider}.{field} has an invalid format")
        if entry.get(fields["billing"]) is not True:
            errors.append(f"providers.{provider}.{fields['billing']} must be true")
        if not _filled(entry.get(fields["region"])):
            errors.append(f"providers.{provider}.{fields['region']} is required")
        if release_ready and entry.get(fields["identity"]) is not True:
            errors.append(f"providers.{provider}.{fields['identity']} must be true for release readiness")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--example",
        action="store_true",
        help="Validate the blank example handoff instead of owner-inputs.local.yaml.",
    )
    parser.add_argument(
        "--release-ready",
        action="store_true",
        help="Also require the four provider OIDC/federated identities and API hostname.",
    )
    args = parser.parse_args(argv)
    path = EXAMPLE_INPUT if args.example else args.inputs
    if not path.is_file():
        print(f"FAIL: input file not found: {path}", file=sys.stderr)
        print(f"Copy {EXAMPLE_INPUT} to {DEFAULT_INPUT} and fill non-secret values.", file=sys.stderr)
        return 2
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        # Do not include parser text that could echo user-supplied scalar values.
        print(f"FAIL: unable to parse YAML ({type(error).__name__})", file=sys.stderr)
        return 2

    errors = validate_inputs(data, release_ready=args.release_ready)
    if errors:
        print(f"FAIL: {len(errors)} cloud onboarding/release requirement(s) missing or invalid:")
        for error in errors:
            print(f"- {error}")
        print("No cloud resources were created.")
        return 1
    stage = "release readiness" if args.release_ready else "account onboarding"
    print(f"PASS: non-secret inputs satisfy the four-provider {stage} checklist.")
    print("This validator does not authenticate to a provider or create resources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
