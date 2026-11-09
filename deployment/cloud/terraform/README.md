# ATLAS provider cluster profiles

These four Terraform roots are a first, provider-specific cluster substrate for the shared GKE/EKS/AKS/OKE release contract. They are **not a completed cloud deployment**. They require owner-provisioned accounts, networks, subnets, identities, registry, encryption/logging destinations, private CI runners, and secure remote Terraform state. They create no resources during formatting, initialization, or validation.

The profiles deliberately consume pre-existing private network resources. This avoids guessing at address ranges, region, data residency, runner routes, or monthly cost while the owner is creating accounts. Each profile creates a managed Kubernetes control plane and a small private node pool only after explicit authorization. It does not create or configure VPC/VNet/VCN, IAM federation, budgets, registries, ingress, NAT/firewall, backups, monitoring workspaces, admission policy, API authentication, or provider-connected runners.

## Shared controls

- Terraform and provider versions are pinned in each root; provider lock files include the official package checksums for Linux AMD64 CI and Linux ARM64 local validation.
- Each root has `resource_creation_authorized = false` by default and a hard precondition on its cluster resource. Set it true only after owner approval of account, billing, monthly cap, region/residency, private network and runner access, identity federation, remote encrypted state, and a reviewed costed plan.
- Control-plane endpoints are private. Do not add public endpoint access to make CI convenient; use the provider-connected ephemeral private runner in `RELEASE_RUNBOOK.md`.
- Node pools use private subnets, minimum two nodes, bounded scaling, provider-managed patch/repair, and no SSH key input. Provider-specific validation checks catch some unsafe network shapes, but do not replace live route and access allow/deny tests.
- Shared CI builds the container once for checks, runs a pinned Trivy scan that fails on HIGH/CRITICAL OS or library findings, and retains an SPDX JSON SBOM as a workflow artifact. This does not yet sign or attest the image, promote it to provider registries, or prove admission policy.
- GKE enables Workload Identity and system/workload/control-plane logging. EKS enables private endpoint only, secret encryption by an owner-provided KMS key, control-plane logs, IMDSv2, and a GitHub deploy-role access entry mapped to `atlas-deployers`. AKS disables local accounts and public FQDN, enables private DNS, Azure RBAC, OIDC/workload identity and UDR-only egress. OKE uses a private control-plane IP and caller-supplied restricted NSGs and private worker subnets.
- `deployment/k8s/rbac/atlas-release-deployer.yaml` is the common namespace-scoped deploy permission set. A cluster administrator applies it once after the private cluster is verified. The release role must not manage IAM, secrets, policy, or other namespaces.

## Required before plan/apply

1. Complete the private `deployment/cloud/owner-inputs.local.yaml` onboarding file and pass `scripts/validate_cloud_inputs.py --release-ready`. This checks recorded inputs, not provider configuration.
2. Prepare and verify an encrypted, access-restricted, locked remote state backend. None is configured in these roots. **Do not run `terraform plan` or `apply` with local state.**
3. Prepare owner-managed `terraform.tfvars` from each provider's `terraform.tfvars.example`; never commit actual account or network values. Do not store secrets in variables or state.
4. Verify GitHub OIDC allow/deny claims, split image publishing and cluster deployment identities, protected environments, private ephemeral runner DNS/routes, budgets, quotas, private registry and required image provenance. These profiles do not create those controls.
5. Review each provider's change plan, cost, address allocation, region and data-residency choices with the account owner. Review destructive replacement paths; cluster destruction is billable and can interrupt service.

Initialize only after remote-state configuration is added:

```sh
terraform init
terraform fmt -check -recursive .
terraform validate
```

The repository CI downloads Terraform 1.17.1 from the official release endpoint, verifies its pinned SHA-256, and runs `fmt -check`, `init -backend=false -lockfile=readonly`, and `validate` for all four roots. Local Linux ARM64 validation passed all four roots; provider locks also include Linux AMD64 checksums for the Ubuntu CI runner. CI also scans the built container for HIGH/CRITICAL OS and library vulnerabilities and retains the SPDX JSON SBOM artifact. No cloud authentication, plan, or apply was attempted. This is configuration validation only; it does not establish an accepted cost plan, live identity, image signature/provenance, provider registry, or cloud deployment. The next implementation phase must add remote backends, account/federated identity stacks, cloud audit-log sinks, registry/provenance policy, and private-runner deployment workflows before staging.

## Provider roots

| Provider | Directory | Required network inputs | Private API setting |
|---|---|---|---|
| Google Cloud / GKE | `gke/` | Existing VPC, private subnet, non-overlapping secondary ranges, reserved control-plane /28, pre-created node identity | Private nodes and endpoint; public control-plane CIDRs disabled |
| AWS / EKS | `eks/` | Existing VPC, two or more private subnets in separate AZs, pre-created cluster/node roles, KMS key | Private endpoint on; public endpoint off |
| Microsoft Azure / AKS | `aks/` | Existing private node subnet, private DNS zone, user-assigned control-plane and kubelet identities, managed log workspace | Private cluster, private FQDN disabled, user-defined egress routing |
| Oracle Cloud / OKE | `oke/` | Existing private endpoint subnet, restricted endpoint NSGs, private node subnets in two or more availability domains, approved image/shape | Public endpoint IP disabled |

Provider schema references: [GKE Terraform resource](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_cluster), [EKS Terraform resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_cluster), [AKS Terraform resource](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster), and [OKE Terraform resource](https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/containerengine_cluster).
