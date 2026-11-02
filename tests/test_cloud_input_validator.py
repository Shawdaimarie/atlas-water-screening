from scripts.validate_cloud_inputs import validate_inputs


def valid_onboarding_inputs():
    return {
        "schema_version": 1,
        "owner": {
            "contact_email": "owner@example.com",
            "apple_account_role": "sign_in_only",
            "data_residency_decision": "us-central-only",
            "staging_production_boundary": "separate-projects",
            "approved_api_hostname": "api.example.com",
        },
        "budget": {
            "currency": "USD",
            "monthly_ceiling": 300,
            "alert_thresholds_percent": [50, 80, 100],
            "alert_recipient_emails": ["owner@example.com"],
        },
        "providers": {
            "google_cloud": {
                "account_ready": True,
                "project_id": "atlas-gcp-research",
                "billing_account_confirmed": True,
                "region": "us-central1",
                "workload_identity_provider_ready": False,
            },
            "aws": {
                "account_ready": True,
                "account_id": "123456789012",
                "billing_confirmed": True,
                "region": "us-east-2",
                "github_oidc_role_ready": False,
            },
            "microsoft_azure": {
                "account_ready": True,
                "tenant_id": "00000000-0000-0000-0000-000000000001",
                "subscription_id": "00000000-0000-0000-0000-000000000002",
                "billing_confirmed": True,
                "region": "centralus",
                "entra_federated_identity_ready": False,
            },
            "oracle_cloud": {
                "account_ready": True,
                "tenancy_ocid": "ocid1.tenancy.oc1..aaaaaa",
                "compartment_ocid": "ocid1.compartment.oc1..bbbbbb",
                "billing_confirmed": True,
                "home_region": "us-ashburn-1",
                "github_oidc_and_registry_identity_ready": False,
            },
        },
    }


def test_owner_inputs_can_pass_onboarding_before_oidc_is_configured():
    assert validate_inputs(valid_onboarding_inputs()) == []


def test_release_readiness_requires_all_four_federated_identities():
    errors = validate_inputs(valid_onboarding_inputs(), release_ready=True)
    assert len(errors) == 4
    assert any("google_cloud.workload_identity_provider_ready" in error for error in errors)
    assert any("aws.github_oidc_role_ready" in error for error in errors)
    assert any("microsoft_azure.entra_federated_identity_ready" in error for error in errors)
    assert any("oracle_cloud.github_oidc_and_registry_identity_ready" in error for error in errors)


def test_malformed_provider_identifier_is_rejected():
    data = valid_onboarding_inputs()
    data["providers"]["aws"]["account_id"] = "not-an-account-id"
    errors = validate_inputs(data)
    assert "providers.aws.account_id has an invalid format" in errors


def test_secret_like_fields_are_rejected_without_echoing_values(tmp_path, capsys):
    import yaml

    from scripts.validate_cloud_inputs import main

    data = valid_onboarding_inputs()
    data["providers"]["aws"]["secret_access_key"] = "must-not-appear-in-output"
    path = tmp_path / "owner-inputs.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    assert main(["--inputs", str(path)]) == 1
    output = capsys.readouterr().out
    assert "secret_access_key" in output
    assert "must-not-appear-in-output" not in output

