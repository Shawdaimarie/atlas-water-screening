# ATLAS multi-cloud release runbook

**Status:** preparation only. The owner reports that Google Cloud, AWS, Azure, and Oracle Cloud accounts are being created; ATLAS has not verified account readiness. No cluster is configured. The same release contract applies to GKE, EKS, AKS, and OKE; see `provider-matrix.yaml` for the machine-readable matrix.

## Account and environment bootstrap

Use the owner-created accounts associated with `shawdaimarie@gmail.com`; account registration, identity proofing, MFA, billing, and acceptance of provider terms stay in the provider consoles with the account owner. Do not put credentials or recovery material in this repository, tickets, email, or the hosted Site. Account creation does not establish deployment readiness.

Before creating resources, record only non-secret identifiers and owner decisions in a private inventory: provider account/project/tenant/subscription/tenancy and compartment IDs, approved region, billing ceiling and alert recipients, environment, support contact, and approved API hostname. Confirm data residency and account ownership. If a provider supports it, keep production separate from staging at the account/project/subscription/compartment boundary. Turn on MFA for named human administrators, document a monitored break-glass route, and enable control-plane audit logs before provisioning.

### Fail-closed input preflight

Copy `deployment/cloud/owner-inputs.example.yaml` to the ignored local file `deployment/cloud/owner-inputs.local.yaml`, then complete only non-secret account identifiers and owner-approved choices. Run:

```sh
.venv/bin/python scripts/validate_cloud_inputs.py
```

This onboarding check requires the four provider accounts and billing confirmations, project/account/tenant/subscription/tenancy and compartment identifiers, regions, a monthly budget ceiling and alert recipients, and explicit data-residency and staging/production decisions. It reports missing field paths without printing field values. It rejects credential-like keys and never contacts a provider or creates resources.

After the exact GitHub OIDC/federated trust configurations and approved API hostname exist, run the stricter static readiness check:

```sh
.venv/bin/python scripts/validate_cloud_inputs.py --release-ready
```

The stricter mode requires all four provider identity-readiness flags. A pass validates the local handoff record only; it does not prove that cloud identity, network paths, cluster access, billing, or policy work in a live provider. Those still require provider-side allow/deny and staging evidence from the release flow below.

Create resources through reviewed, versioned IaC with encrypted remote state, state locking, restricted state access, and a recovery copy. Set budgets, service quotas, region policy, and alerts first. Default to private cluster control planes, private worker nodes, private registries, no public database, and no public API. Any exception requires a written threat and access review before provisioning. Do not create paid resources just to validate an account.

### Private-cluster deployment runner gate

A green GitHub-hosted build does not mean the deploy job can reach a private GKE, EKS, AKS, or OKE API. Network reachability and cloud authorization are separate controls. Before enabling a provider deploy workflow, select and verify an ephemeral runner or private build worker with DNS and routed access to that provider's private endpoint. Keep OIDC trust constrained to the exact repository, protected branch, workflow, environment, and audience. Never make a private cluster public just to simplify CI access.

| Provider | Private endpoint connectivity requirement | Evidence before deploy workflow activation |
|---|---|---|
| Google Cloud | A GKE private endpoint is reachable only through the VPC or routed private network. Google documents Cloud Build private-pool access patterns; the private-pool/GKE control-plane path may require Private Service Connect and Cloud VPN because VPC peering is not transitive. | Runner/pool route and private DNS resolution; allowed and denied control-plane connection tests; exact OIDC claims; cost estimate for any VPN/runner resources. |
| AWS | A private EKS endpoint requires a client inside or connected to the cluster VPC. CodeBuild can be configured for VPC access, or use an ephemeral GitHub Actions runner in the VPC to retain GitHub OIDC federation. | Private endpoint DNS and route test from the selected runner; denied connection from outside; IAM trust allow/deny test; NAT/VPC endpoint and runner cost estimate. |
| Microsoft Azure | A private AKS API requires an agent in the cluster VNet, a peered VNet, or another routed network with private DNS. Microsoft-hosted Azure Pipelines agents do not support private AKS clusters; if GitHub OIDC remains the release identity, use a network-connected GitHub runner. | Private FQDN resolution and route from the selected runner; denied external control-plane path; Entra federation allow/deny test; runner and network cost estimate. |
| Oracle Cloud | A private OKE API requires an agent with routed VCN access and correct private DNS. OCI DevOps managed build stages can be configured for private VCN access; alternatively use a network-connected GitHub runner for GitHub OIDC-based deploy identity. | Private endpoint DNS and route test from the selected runner; denied external path; separate OKE authorization and OCIR publish identity tests; NAT/service-gateway and runner cost estimate. |

The shared workflow remains build-once and digest-based. A deploy job must run only on its protected, provider-connected runner group after the verified image digest, SBOM, signature, and provenance are available. Runner registration credentials must be short-lived and scoped; runner instances must be ephemeral or rebuilt between jobs, isolated from untrusted pull requests, and destroyed/recycled after the job. If a provider cannot meet these requirements within the approved budget, pause that provider's deploy workflow and revise the architecture before creating its cluster.

Provider documentation: [GKE private clusters with Cloud Build private pools](https://docs.cloud.google.com/build/docs/private-pools/accessing-private-gke-clusters-with-cloud-build-private-pools); [AWS CodeBuild VPC access](https://docs.aws.amazon.com/codebuild/latest/userguide/vpc-support.html); [AKS security and private API access](https://learn.microsoft.com/en-us/azure/aks/concepts-security); [OCI DevOps managed build-stage private VCN access](https://docs.oracle.com/en-us/iaas/Content/devops/using/managed_buildstage.htm).

### Owner onboarding handoff

While accounts are being created, no credential or console access is needed in this project. Once setup is complete, the owner can provide non-secret account/project/tenant/subscription/tenancy and compartment identifiers, chosen region, billing ceiling and alert destination, data-residency decision, and approved staging/production boundary. Confirm MFA, recovery, and billing directly in each provider console. Do not send passwords, codes, payment data, access keys, or private keys. After those inputs are recorded in an owner-controlled private inventory, validate organization-level policy and repository OIDC trust before provisioning. Use one identical acceptance checklist for each provider; do not declare a provider ready from account creation alone.

## Parity requirements

Each provider must pass the same acceptance outcomes. A native service name is not proof by itself; retain the allow/deny test and configuration evidence for the actual resource.

| Control | Required result on GKE, EKS, AKS, OKE |
|---|---|
| CI identity | GitHub OIDC only; issuer, audience, exact repository, protected branch, workflow, and environment constrained; untrusted fork/branch job denied. No long-lived cloud key, service-principal secret, or OCI auth token. |
| Privilege separation | Separate staging and production identities; separate image publish and cluster deploy permissions; deployment role cannot administer IAM, billing, network policy, or organization settings. Human production approval is required. |
| Network | Private control plane and nodes; no direct public Service; application ingress requires authentication and TLS 1.2+; network policy limits pod traffic; egress uses a documented allowlist. Verify from approved and unapproved networks. |
| Image and provenance | Private registry; publish one immutable digest; generate and verify SBOM, build provenance, and signature; verify digest equality and attached evidence after registry copy; enforce signature/provenance policy at admission; scan at build and in the registry; block critical/high findings unless a time-bounded exception is approved. |
| Runtime | Restricted Pod Security Admission, non-root, read-only root filesystem, no privilege escalation/capabilities, seccomp RuntimeDefault, resource requests/limits, no automatic token unless an explicit workload identity requires it, supported Kubernetes version and patch channel. |
| Secrets and data | Provider secret manager and KMS; workload identity scoped to one service and required resources; encryption in transit and at rest; prove rotation/revocation; no credentials or sensitive asset identifiers in logs. |
| Detection | Control-plane audit events and workload logs reach a retained, access-controlled destination; alert on unauthorized identity attempts, policy changes, failed readiness, 5xx, latency, and budget thresholds. |
| Recovery | Restore IaC state, secrets, registry artifact, and (when introduced) data from documented backups; prove recovery objectives and rollback to the previously verified digest. |

Provider substitutions must meet these same outcomes:

| Provider | CI federation and runtime identity | Registry, scan, and network evidence |
|---|---|---|
| Google Cloud | GitHub OIDC → Workload Identity Federation with attribute conditions scoped to trusted GitHub organization/repository and deployment claims; distinct minimal service accounts. GKE Workload Identity Federation gives each pod only required Google API access. Keep node image-pull identity separate. | Private Artifact Registry with repository scanning explicitly enabled and Artifact Analysis evidence; GKE private endpoint, VPC firewall/network policy, Cloud KMS/Secret Manager, and Cloud Audit Logs. Google documents GitHub as a multi-tenant IdP: issuer check alone is insufficient; attribute condition and audience must be tested. |
| AWS | GitHub OIDC → separate IAM roles for publish and deploy with exact `sub` and audience; EKS Pod Identity (or IRSA) per workload; separate node role for ECR image pulls. | Private ECR with enhanced scanning enabled for selected repositories; private EKS endpoint, security groups, VPC endpoints where appropriate, Secrets Manager/KMS, and CloudTrail. Capture ECR/Inspector scan output and prove the public endpoint is disabled. |
| Microsoft Azure | GitHub OIDC → Microsoft Entra federated credentials with exact issuer, subject, and audience; separate scoped identities for publish and deploy. AKS Workload ID per pod and a separate kubelet managed identity with ACR pull. | Private ACR and Defender for Containers/registry scan evidence; private AKS API, Azure Policy restricted pod/image controls, Key Vault, managed disk encryption, and diagnostic logs. Use Notary Project signing/verification; Azure documents Docker Content Trust enablement as closed to new registries since 2026-05-31 and removal on 2028-03-31. |
| Oracle Cloud | GitHub OIDC → OKE cluster access with exact repository/workflow/branch claims, plus least-privilege OCI IAM/dynamic groups and per-workload Kubernetes RBAC. OKE cluster OIDC does not establish OCI Registry publishing; prove a separate short-lived or managed CI identity before use. | Private OCIR with an OCI Vulnerability Scanning configuration explicitly enabled on the repository and results retained; private OKE endpoint/nodes, NSGs plus Kubernetes network policies, Vault/KMS, and OCI Audit. Reject a static OCI auth token as a shortcut. |

## Release flow

1. Merge a reviewed commit after the shared verification workflow passes. The existing workflow tests, builds, smoke-checks, and audits the local candidate. It does not authenticate to a cloud or publish a release.
2. Produce one release image from that exact commit. Generate an SBOM and provenance, scan the source, dependencies, and image OS packages, sign the image, and store all records with the release. Reject a mutable tag as the deployment identity; record the registry and digest.
3. Use GitHub Actions OIDC with a protected `atlas-staging-<provider>` environment. Configure a provider trust condition for the exact repository, protected branch, workflow/environment, and audience. Verify an unauthorized branch, fork pull request, wrong audience, and wrong environment are denied. Pin every GitHub Action to a full commit SHA, give jobs minimum permissions, and never expose deployment identity to pull-request workflows. Do not use cloud access keys or saved service-principal credentials.
4. Publish or mirror the same image digest into the provider registry. Verify the registry digest, signature, SBOM, and provenance remain attached and valid after transfer, and enforce signature/provenance policy at admission. For OCI, separately validate registry publishing authentication; OKE cluster OIDC alone does not prove registry push access.
5. Deploy the digest to staging with the shared `deployment/k8s/` baseline and provider-specific policy admission. The common network policy defaults to deny and allows the API only from the explicitly labeled ingress-controller namespace/pods plus CoreDNS egress; see `deployment/k8s/README.md`. Confirm the selected CNI enforces policies and test allowed/denied paths, including probes. Supply only reviewed bindings: namespace, authenticated ingress, TLS, private networking, secret manager, KMS, workload identity, logging, registry policy, and health telemetry. Keep the API private behind authenticated ingress.
6. Run the same authenticated end-to-end suite against every provider. Check `/api/health`, `/api/areas`, `/api/study-areas`, analysis, CSV export, invalid input, request size, host/CORS boundaries, identity allow and deny cases, network reachability from approved and unapproved networks, secret rotation, image policy, audit logs, and required user workflows. Confirm the observed runtime image digest equals the approved digest. Label API results fixture-only until real data and user authentication are implemented.
7. Record the staging evidence and obtain human approval in `atlas-production-<provider>`. Promote the same digest; do not rebuild. Observe error rate, latency, saturation, and spend for 15 minutes.
8. Roll back to the recorded previous digest when readiness fails, a required workflow fails, 5xx exceeds 1% for 5 minutes, or p95 latency exceeds twice the approved baseline for 10 minutes. Run a rollback drill before first production use.

## Provider setup evidence required

| Provider | Identity and registry proof | Cluster and network proof |
|---|---|---|
| Google Cloud | Exact WIF allow/deny claims, least-privilege publish/deploy accounts, separate node image-pull identity, Artifact Analysis result, digest/signature/SBOM/provenance preserved and admission-verified. | Private GKE endpoint, per-service-account workload binding, authenticated ingress, VPC/network policy, audit logs, Secret Manager/KMS, restore evidence. |
| AWS | Exact OIDC allow/deny claims, separate ECR publish/EKS deploy roles, node image-pull role, ECR scan result, digest/signature/SBOM/provenance preserved and admission-verified. | Private EKS endpoint, Pod Identity/IRSA per workload, authenticated ingress, security groups/network policy, CloudTrail, Secrets Manager/KMS, restore evidence. |
| Microsoft Azure | Exact Entra federation allow/deny claims, separate ACR publisher/AKS deploy roles, kubelet ACR-pull identity, registry scan, Notation verification, and digest/SBOM/provenance admission evidence. | Private AKS API, Entra user/workload identity, authenticated ingress, Azure Policy/network policy, diagnostic logs, Key Vault, restore evidence. |
| Oracle Cloud | Exact OKE OIDC allow/deny claims, separate proof of registry publishing identity, least-privilege OCI IAM, OCI scan result, digest/signature/SBOM/provenance preserved and admission-verified. | Private OKE endpoint/nodes, workload RBAC and node pull scope, authenticated ingress, NSGs/network policy, OCI Audit, Vault/KMS, restore evidence. |

## Evidence record

For each provider, retain the commit, workflow run, test/audit reports, image digest, SBOM, signature verification, provenance, policy scan, OIDC denial/allow test, staging smoke output, authenticated E2E results, deployment revision, 15-minute health/spend observation, approver, and rollback drill result. Record only non-secret account, project/subscription, region, cluster, registry, environment, and identity identifiers. Never put passwords, MFA codes, payment data, private keys, OIDC tokens, or registry auth tokens in this repository.

## Current readiness

**Checked:** 2026-11-03 America/Chicago. Private ATLAS Site v45 is active at the owner-only URL. Deployment `appgdep_6aeaa307a37c8191ad760a055e109dfd` succeeded from source commit `a3718a6043d131fc989e1d172d41a90e839f6cf7`; the 17-file archive SHA-256 is `7338d6ac98da75340468209d10d89b2dbfa3cb0e958279c7e6a6b94fcc649c2e`. An unauthenticated request returned HTTP 401. Full authenticated interaction replay remains verified on v43; a fresh v45 replay could not be run because the desktop browser bridge returned a transport-closed error. The current hash-locked Python 3.12 suite reports 139 passed in 18.16s. The 192/192 matched RTC quota is conditional spatial availability, not OPERA event validation or flood accuracy. The analysis remains synthetic and confirmatory eligibility is 0/16. The canonical score is 60/100 provisional. See `outputs/atlas-v45-end-to-end-checklist.md` and `outputs/atlas-v43-end-to-end-checklist.md`.

- The four-cloud input validator treats Apple distribution as a separate track. The user's existing Apple account is designated for possible App Store/TestFlight distribution; membership and App Store Connect access are unverified. The current repository has no native Apple app target and the Mac lacks full Xcode. Apple identity is not used for cloud hosting or cloud release readiness.
- The non-secret private handoff file `deployment/cloud/owner-inputs.local.yaml` is absent. The example records the selected Apple distribution role but contains no provider account identifiers or billing decisions. ATLAS has not verified Google Cloud, AWS, Azure, or Oracle account readiness, MFA, regions, billing, budgets, or OIDC/federated identities.
- The current `--example --release-ready` preflight fails closed with 29 missing or invalid requirements. It reports field names only, does not print values, and creates no cloud resources. Provider-specific deploy workflows, trust bindings, registries, clusters, connected runners, and staging environments remain unverified.
- The source-and-release criteria remain identical across GKE, EKS, AKS, and OKE. Use the no-cost onboarding steps above and provision nothing until account IDs, regions, spending ceiling/alerts, residency and environment decisions, and identity setup are verified.
- The current hash-locked Python 3.12 suite reports 139 passed; the v45 checklist records current Site readback and package checks, while the v43 checklist records the last complete authenticated replay. These are author checks, not independent reproduction or provider deployment evidence. The onboarding validator confirms cloud preparation has no Apple account prerequisite.

See `outputs/atlas-v45-end-to-end-checklist.md`, `outputs/atlas-v43-end-to-end-checklist.md`, `outputs/atlas-live-walkthrough.md`, and `outputs/atlas-apple-distribution-readiness.md` for the current Site and Apple-track evidence. See `deployment/cloud/RELEASE_RUNBOOK.md` for the canonical parity contract and release gates.
