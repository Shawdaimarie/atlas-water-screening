"""Static checks for provider-parity release policy and protected manifests.

These tests validate declared policy only. They do not prove that any cloud
account, runner, network path, cluster, registry, or deployment exists.
"""
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MATRIX = yaml.safe_load((ROOT / "deployment/cloud/provider-matrix.yaml").read_text())
OWNER_INPUTS = yaml.safe_load(
    (ROOT / "deployment/cloud/owner-inputs.example.yaml").read_text()
)


def test_all_four_clouds_share_private_digest_based_release_contract():
    providers = MATRIX["providers"]
    assert set(providers) == {"google_cloud", "aws", "microsoft_azure", "oracle_cloud"}
    contract = MATRIX["release_contract"]
    assert MATRIX["runtime_contract"] == "kubernetes"
    assert contract["identity_provider"] == "github_actions_oidc"
    assert contract["build_once"] is True
    assert contract["deploy_by_digest"] is True
    assert contract["static_cloud_credentials"] == "forbidden"
    assert contract["private_cluster_api_required"] is True
    assert contract["provider_connected_deploy_runner_required"] is True
    assert contract["deploy_runner_must_be_ephemeral"] is True
    assert contract["deploy_runner_must_not_execute_untrusted_pull_requests"] is True

    runner_evidence = {
        "google_cloud": "ephemeral_runner_private_dns_and_route_allow_deny_test",
        "aws": "ephemeral_runner_private_dns_and_route_allow_deny_test",
        "microsoft_azure": "ephemeral_runner_private_dns_and_route_allow_deny_test",
        "oracle_cloud": "ephemeral_runner_private_dns_and_route_allow_deny_test",
    }
    for provider, evidence in runner_evidence.items():
        assert evidence in providers[provider]["security_evidence"]
        assert providers[provider]["readiness"].startswith("pending_")


def test_owner_handoff_template_is_unprovisioned_and_nonsecret():
    assert OWNER_INPUTS["schema_version"] == 1
    assert OWNER_INPUTS["owner"]["apple_account_role"] == "undecided"
    assert OWNER_INPUTS["budget"]["monthly_ceiling"] is None
    assert OWNER_INPUTS["providers"]["google_cloud"]["account_ready"] is False
    assert OWNER_INPUTS["providers"]["aws"]["account_ready"] is False
    assert OWNER_INPUTS["providers"]["microsoft_azure"]["account_ready"] is False
    assert OWNER_INPUTS["providers"]["oracle_cloud"]["account_ready"] is False
    serialized = (ROOT / "deployment/cloud/owner-inputs.example.yaml").read_text().lower()
    for forbidden in ("password:", "private_key:", "access_key:", "auth_token:", "recovery_code:"):
        assert forbidden not in serialized


def test_kubernetes_workload_preserves_restricted_container_baseline():
    namespace = yaml.safe_load((ROOT / "deployment/k8s/namespace.yaml").read_text())
    documents = list(yaml.safe_load_all((ROOT / "deployment/k8s/deployment.yaml").read_text()))
    deployment = next(item for item in documents if item["kind"] == "Deployment")
    service = next(item for item in documents if item["kind"] == "Service")
    pod = deployment["spec"]["template"]["spec"]
    container = pod["containers"][0]
    security = container["securityContext"]

    assert namespace["metadata"]["labels"]["pod-security.kubernetes.io/enforce"] == "restricted"
    assert deployment["spec"]["replicas"] >= 2
    assert pod["automountServiceAccountToken"] is False
    assert pod["securityContext"]["runAsNonRoot"] is True
    assert pod["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault"
    assert security["allowPrivilegeEscalation"] is False
    assert security["readOnlyRootFilesystem"] is True
    assert security["capabilities"]["drop"] == ["ALL"]
    assert container["resources"]["requests"] and container["resources"]["limits"]
    assert container["env"][-1]["name"] == "ATLAS_ALLOWED_HOSTS"
    assert "localhost" in container["env"][-1]["value"]
    for probe in (container["readinessProbe"], container["livenessProbe"]):
        assert {header["name"]: header["value"] for header in probe["httpGet"]["httpHeaders"]}["Host"] == "localhost"
    assert service["spec"]["type"] == "ClusterIP"


def test_kubernetes_network_policy_denies_by_default_and_allows_only_ingress_and_dns():
    docs = list(yaml.safe_load_all((ROOT / "deployment/k8s/network-policy.yaml").read_text()))
    policies = {doc["metadata"]["name"]: doc for doc in docs}
    deny = policies["atlas-default-deny"]["spec"]
    assert deny["podSelector"] == {}
    assert set(deny["policyTypes"]) == {"Ingress", "Egress"}

    approved = policies["atlas-api-approved-paths"]["spec"]
    assert approved["podSelector"]["matchLabels"]["app.kubernetes.io/name"] == "atlas-api"
    assert len(approved["ingress"]) == 1
    source = approved["ingress"][0]["from"][0]
    assert source["namespaceSelector"]["matchLabels"]["atlas.network/role"] == "trusted-ingress"
    assert source["podSelector"]["matchLabels"]["app.kubernetes.io/name"] == "atlas-ingress-controller"
    assert {port["port"] for port in approved["ingress"][0]["ports"]} == {8080}
    assert len(approved["egress"]) == 1
    destination = approved["egress"][0]["to"][0]
    assert destination["namespaceSelector"]["matchLabels"]["kubernetes.io/metadata.name"] == "kube-system"
    assert destination["podSelector"]["matchLabels"]["k8s-app"] == "kube-dns"
    assert {port["port"] for port in approved["egress"][0]["ports"]} == {53}


def test_kubernetes_workload_budget_and_disruption_budget_match_two_replicas():
    docs = list(yaml.safe_load_all((ROOT / "deployment/k8s/resource-controls.yaml").read_text()))
    quota, pdb = docs
    assert quota["kind"] == "ResourceQuota"
    assert quota["spec"]["hard"]["pods"] == "10"
    assert pdb["kind"] == "PodDisruptionBudget"
    assert pdb["spec"]["minAvailable"] == 1
    assert pdb["spec"]["selector"]["matchLabels"]["app.kubernetes.io/name"] == "atlas-api"
