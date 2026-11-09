from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TF_ROOT = ROOT / "deployment/cloud/terraform"


def _read(provider: str, name: str) -> str:
    return (TF_ROOT / provider / name).read_text()


def test_all_provider_profiles_fail_closed_and_pin_provider_versions():
    expected = {
        "gke": ('hashicorp/google', '7.22.0'),
        "eks": ('hashicorp/aws', '6.21.0'),
        "aks": ('hashicorp/azurerm', '4.62.0'),
        "oke": ('oracle/oci', '8.29.0'),
    }
    for provider, (source, version) in expected.items():
        versions = _read(provider, "versions.tf")
        variables = _read(provider, "variables.tf")
        main = _read(provider, "main.tf")
        example = _read(provider, "terraform.tfvars.example")
        assert source in versions
        assert f'= "= {version}"' in versions
        assert 'default     = false' in variables
        assert 'resource_creation_authorized' in example and '= false' in example.split('resource_creation_authorized', 1)[1]
        assert 'terraform_data.resource_guard' in main
        assert 'error_message = "Cloud resource creation is disabled' in main

    matrix = (ROOT / "deployment/cloud/provider-matrix.yaml").read_text()
    assert matrix.count("schema_validation_platform: linux_arm64") == 4
    assert matrix.count("provider_checksum_platforms: [linux_amd64, linux_arm64]") == 4


def test_all_provider_profiles_keep_cluster_api_private():
    expected = {
        "gke": ['enable_private_nodes    = true', 'enable_private_endpoint = true'],
        "eks": ['endpoint_private_access = true', 'endpoint_public_access  = false'],
        "aks": ['private_cluster_enabled             = true', 'private_cluster_public_fqdn_enabled = false'],
        "oke": ['is_public_ip_enabled = false'],
    }
    for provider, markers in expected.items():
        main = _read(provider, "main.tf")
        for marker in markers:
            assert marker in main


def test_eks_does_not_grant_bootstrap_admin_and_uses_scoped_release_group():
    main = _read("eks", "main.tf")
    assert 'bootstrap_cluster_creator_admin_permissions = false' in main
    assert 'kubernetes_groups = ["atlas-deployers"]' in main
    assert 'endpoint_public_access  = false' in main
    assert 'http_tokens                 = "required"' in main


def test_shared_release_role_is_namespace_scoped_and_cannot_edit_secrets_or_rbac():
    role = (ROOT / "deployment/k8s/rbac/atlas-release-deployer.yaml").read_text()
    assert 'kind: Role\nmetadata:\n  name: atlas-release-deployer\n  namespace: atlas' in role
    assert 'kind: RoleBinding' in role
    assert 'name: atlas-deployers' in role
    rules = role.split('rules:', 1)[1].split('---', 1)[0]
    assert 'secrets' not in rules
    assert 'rbac.authorization.k8s.io' not in rules


def test_terraform_working_state_and_owner_inputs_are_ignored():
    ignore = (ROOT / ".gitignore").read_text()
    assert '**/.terraform/**' in ignore
    assert '*.tfstate' in ignore
    assert '*.tfplan' in ignore
    assert 'terraform.tfvars' in ignore


def test_ci_installs_checksum_pinned_terraform_and_validates_all_four_roots():
    workflow = (ROOT / ".github/workflows/verify.yml").read_text()
    assert "terraform_1.17.1_linux_amd64.zip" in workflow
    assert "4638628058e71a55212b1c563712eac03b902128f40740f3dc8174df12135061" in workflow
    assert "terraform fmt -check -recursive deployment/cloud/terraform" in workflow
    assert "init -backend=false -input=false -lockfile=readonly" in workflow
    assert "for profile in gke eks aks oke" in workflow
    assert "validate -no-color" in workflow
    assert "anchore/sbom-action@66cbf4bc1f1c0d2edc94016e65bc221b6bb0ad6c" in workflow
    assert "aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25" in workflow
    assert "version: v0.76.1" in workflow
    assert "severity: HIGH,CRITICAL" in workflow
    assert "upload-artifact: true" in workflow



def test_runtime_image_uses_pinned_trixie_base_without_setuptools_install():
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "python:3.12-alpine@sha256:e6dae589c1c05976188fd3bd019afd091445fc533ed2ea29001beddc7368a9c8" in dockerfile
    assert "setuptools==" not in dockerfile
