# ATLAS multi-cloud deployment preparation

**Prepared:** 2026-11-02; provider parity runbook expanded 2026-11-02\
**Scope:** deployment readiness for Google Cloud, AWS, Microsoft Azure, and Oracle Cloud Infrastructure (OCI).\
**Status:** preparation only. The owner reports that accounts are being created under `shawdaimarie@gmail.com`. ATLAS has not verified account readiness, billing, MFA, regions, or provider IDs; no credential was requested or stored, no resources were provisioned, and nothing was deployed to these providers.

## Current application boundary

ATLAS currently consists of a private static Sites walkthrough and a separate Starlette API. The API returns synthetic analysis data, exposes the 16-area archive-metadata candidate register, performs no raster processing, has no persistent database, and is not connected to the hosted page. This preparation packages the API as one non-root container and defines a common Kubernetes release contract. It does not make the demo into an operational geospatial service.

An offline WTR GeoTIFF analyzer and a global 16-area coverage gate have since been added as research scripts. They are not connected to the API or Site and are not included in the current container image. The current image is still a synthetic fixture API.

## Common platform shape

Use the same container image and Kubernetes deployment contract in each provider's managed Kubernetes service. This keeps the runtime, health checks, resource limits, rollout behavior, and application security controls consistent. Registry, cluster identity, ingress, DNS, TLS, secret storage, logging, and billing remain provider-specific bindings.

| Provider | Managed Kubernetes target | Image registry | Deployment identity pattern |
|---|---|---|---|
| Google Cloud | Google Kubernetes Engine (GKE) | Artifact Registry | GitHub Actions OIDC through Workload Identity Federation; restrict provider condition to the exact repo, branch, and environment; grant a minimal deploy service account. |
| AWS | Amazon EKS | Amazon ECR | GitHub Actions OIDC to a scoped IAM role; restrict trust to the exact repository/environment and grant only ECR push plus target-cluster deployment permissions. |
| Microsoft Azure | Azure Kubernetes Service (AKS) | Azure Container Registry | GitHub Actions OIDC / Microsoft Entra federated identity; scope registry and cluster roles to the specific resources. |
| Oracle Cloud | Oracle Kubernetes Engine (OKE) | OCI Container Registry | GitHub Actions OIDC authentication for OKE with a repository-scoped trust policy; use narrowly scoped OCI policies and Kubernetes RBAC. OCI documents this pattern for GitHub Actions to OKE. |

GKE, EKS, AKS, and OKE are the four target runtimes for this preparation. The Kubernetes deployment and service manifest in `deployment/k8s/` is shared. Cloud-specific Terraform, ingress/DNS/TLS, registry bootstrap, identity trust policies, and executable deployment workflows are not yet provisioned because the new provider accounts and region/budget choices are pending. `deployment/cloud/provider-matrix.yaml` records equivalent gates and provider-specific identity/registry bindings; `deployment/cloud/RELEASE_RUNBOOK.md` defines one release and evidence flow across all four.

## Security and release contract — same for all four

1. **Build once:** build the API container from a reviewed commit; use the same immutable digest in staging and production. Do not rebuild on promotion.
2. **Identity:** CI uses short-lived OIDC federation, never static cloud access keys. Trust is limited to the exact repository, protected branch, deployment environment, and workflow. Separate read/build/publish/deploy permissions and principals.
3. **Supply chain:** pin base image by digest for production, lock and hash Python dependencies, generate an SBOM, scan source/dependencies/image, sign the image, and retain provenance tied to commit and workflow run. Block release on critical/high exploitable findings or an unverifiable artifact.
4. **Container:** run as a non-root UID, read-only root filesystem, no privilege escalation, drop Linux capabilities, default seccomp, no service-account token unless needed, CPU/memory requests and limits, and immutable image digest. The starter Dockerfile and Kubernetes manifest implement the runtime controls that apply without cloud credentials.
5. **Network:** keep the API service private behind authenticated ingress or an approved gateway. Require TLS 1.2+ at the edge. Allow exact frontend origins through `ATLAS_CORS_ORIGINS` and `ATLAS_ALLOWED_HOSTS`; wildcard values are rejected. Do not expose Kubernetes service ports directly to the public Internet.
6. **Secrets and data:** secrets come from each provider's managed secret store and are mounted/retrieved at runtime using workload identity. Never place credentials in Git, container layers, frontend JavaScript, CI logs, or `.env` files. Encrypt storage and backups with provider KMS keys. No real data is currently configured.
7. **Promotion:** run tests, dependency and secret scans, image scan, SBOM/provenance verification, then staging deploy and smoke checks. Require a human approval for production. Promote the already-verified image digest. Use a progressive rollout where supported and retain the previous known-good revision.
8. **Observability:** collect structured logs, health, request rate, error rate, and latency without logging secrets or sensitive asset details. Alert on failed readiness, elevated 5xx, and latency regressions. Keep audit logs for cloud control-plane and CI deployment actions.
9. **Rollback:** stop promotion and roll back to the prior digest/revision if health checks fail, 5xx exceeds 1% for 5 minutes, p95 exceeds 2× the approved baseline for 10 minutes, or a critical user flow fails. These are proposed initial triggers; approve baselines against a real staging workload before production.
10. **Recovery:** define and test cluster recreation, secret restoration, data backup/restore (when persistent data exists), and DNS rollback. No production recovery evidence exists yet.

### Cross-provider acceptance evidence

The machine-readable baseline is in `deployment/cloud/provider-matrix.yaml`; the execution sequence is in `deployment/cloud/RELEASE_RUNBOOK.md`. A provider is release-ready only when every common outcome below has evidence from that provider's actual environment:

- OIDC succeeds only for the approved repository, branch, workflow, audience, and protected environment; a fork pull request and deliberately wrong claims are denied. Cloud access is absent from PR workflows. CI actions are pinned to full commit SHA and each job uses minimum permissions.
- Staging and production use separate deployment identities; image publishing and cluster deployment are separate permissions. Provider admins, billing, and organization policy cannot be changed by the deploy identity.
- Cluster API and nodes are private, ingress is authenticated and TLS 1.2+, direct public Service exposure is blocked, pod-to-pod traffic is policy-limited, and egress is allowlisted. Verify both allowed and denied network paths.
- One signed image digest is built once, scanned in CI and the provider registry, and promoted unchanged. The digest, signature, SBOM, and provenance must survive each registry transfer and be enforced at admission. Block critical/high results unless an explicitly approved, expiring exception is recorded.
- Restricted Pod Security Admission, non-root/read-only containers, default seccomp, limits, workload identity, managed secrets/KMS, audit logs, monitored budgets, restoration, and rollback are proven. The same test plan, evidence fields, thresholds, and report format are used on GKE, EKS, AKS, and OKE.

Account owners keep registration, identity proofing, MFA, billing, and provider terms in the provider consoles. Before provisioning, ATLAS needs only non-secret account/project/tenant/subscription/compartment IDs, approved region, cost ceiling and alert recipients, chosen API hostname, data residency decision, and named owner/support contact. Account creation alone is not a deployment gate pass. No paid resources should be created just to validate signup.

## Pre-release checklist

### Required before any cloud deployment

- [ ] Provider account and billing owner confirmed; select region(s), budget cap, and alert recipients.
- [ ] Decide whether provider accounts are isolated research environments or production tenants; define owner/admin and break-glass path.
- [ ] Create repository/environment OIDC trust with exact subject and audience restrictions; prove a job without the trusted branch/environment is denied.
- [ ] Create private registry, managed cluster, secret store, KMS key, private networking, and authenticated ingress using reviewed IaC.
- [ ] Choose API hostname and add the exact browser origin to `ATLAS_CORS_ORIGINS`; keep current Sites frontend disconnected until API auth/CORS and account-user access are reviewed.
- [x] Generate hash-locked Python runtime, development, and audit dependency sets; pin the Docker base image by digest.
- [ ] Run the prepared test, dependency, secret, and image audit gates in remote CI; generate/verify SBOM, image signature, and provenance, then complete provider policy checks.
- [ ] Deploy staging by immutable image digest and verify health, CORS, invalid-input rejection, request-size rejection, authenticated access, logs, and rollback.
- [ ] Only after actual raster ingestion and its authorization are implemented: verify provenance, pixel/QA semantics, event/baseline selection, and independent reference labels in each enrolled study area.
- [ ] Approve cost/throughput limits for geospatial workloads before enabling real raster processing.

### Production release gates

- [ ] Reviewed change and green CI run for the exact commit.
- [ ] No critical/high release-blocking findings; signed artifact and SBOM attached to the release record.
- [ ] Staging E2E suite passes for all required workflows and candidate locations.
- [ ] Human production approval recorded; cloud account/region and cost cap are explicit.
- [ ] Deploy the exact staging digest; health and smoke checks pass.
- [ ] Monitor errors, latency, saturation, and spend for 15 minutes after promotion.
- [ ] Confirm rollback target is still available and execute a rollback drill before first production use.

## Account onboarding inputs (do not put credentials here)

For the accounts the owner is creating under `shawdaimarie@gmail.com`, keep account setup and billing/terms acceptance in the owner's hands. When each account is ready, record only non-secret identifiers in a private configuration inventory:

| Provider | Needed non-secret setup choices | Secrets or credentials |
|---|---|---|
| Google Cloud | Organization/project ID, billing budget ceiling, region, GitHub OIDC provider and workload identity pool/provider names | Never store service-account keys; use WIF with attribute conditions and verify node image-pull identity separately. |
| AWS | Account ID, organization/role boundary, budget ceiling, region, GitHub OIDC role identifiers | Never store IAM user access keys; use scoped role assumption and verify ECR scan plus EKS private endpoint. |
| Azure | Tenant ID, subscription ID, resource group/region, Entra federated identity identifiers | Use federation and managed identities; do not store client secrets. Use Notary Project for image signatures. |
| OCI | Tenancy and compartment OCIDs, home/target region, budget/alert settings, OKE cluster identity | Prove a short-lived registry publish path separately from OKE OIDC; do not commit API signing keys or auth tokens. |

Do not share account passwords, MFA recovery codes, payment details, or cloud key files with this project or its repository.

## Provider references

- Google: [Workload Identity Federation for deployment pipelines](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines); [Workload Identity Federation best practices](https://docs.cloud.google.com/iam/docs/best-practices-for-using-workload-identity-federation); [Workload Identity Federation for GKE](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/workload-identity). Google recommends attribute conditions for multi-tenant identity providers such as GitHub; this project selects GKE so the runtime is Kubernetes-consistent across providers.
- AWS: [Create an IAM role for OIDC federation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp-oidc.html); [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-id-association.html); [EKS node role and private ECR image pulls](https://docs.aws.amazon.com/eks/latest/userguide/create-node-role.html). This project selects EKS to keep the same Kubernetes contract across all four providers.
- Microsoft: [Authenticate to Azure from GitHub Actions with OpenID Connect](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect); [AKS managed identity and ACR pulls](https://learn.microsoft.com/en-us/azure/aks/managed-identity-overview); [Microsoft Entra Workload ID for AKS](https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview). Use Entra federated credentials and scoped registry/cluster roles.
- Oracle: [Enable GitHub Actions to access an OKE cluster using OIDC](https://docs.oracle.com/en/learn/gaw-oke-odic/index.html). This documents Kubernetes API access; OCI registry publishing is a separate proof required by this project before OKE is release-ready.
- Google: [Workload Identity Federation best practices](https://docs.cloud.google.com/iam/docs/best-practices-for-using-workload-identity-federation) recommends attribute conditions with GitHub and a constrained audience; [GKE Workload Identity Federation](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/workload-identity) distinguishes workload access from node service-account image pulls.
- AWS: [EKS identity and access best practices](https://docs.aws.amazon.com/eks/latest/best-practices/identity-and-access-management.html) covers private cluster endpoints and workload roles; [ECR enhanced scanning](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning-enhanced-enabling.html) documents scan-on-push and continuous scanning configuration.
- Microsoft: [AKS security recommendations](https://learn.microsoft.com/en-us/azure/aks/secure-aks) covers private control planes, Pod Security Admission, and trusted registries; [ACR signing guidance](https://learn.microsoft.com/en-us/azure/container-registry/secure-container-registry) selects Notary Project/Notation because DCT is deprecated and removed 2028-03-31.
- Microsoft: [Notation and Artifact Signing](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-sign-verify-notation-artifact-signing) describes signature verification for container images.
- Oracle: [OKE security recommendations](https://docs.oracle.com/en-us/iaas/Content/Security/Reference/oke_security.htm) recommends private node pools and digest-pinned images; [OCIR vulnerability scanning](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registryscanningimagesforvulnerabilities.htm) explains that repository scanning must be explicitly enabled.

## Prepared artifacts and validation

- `Dockerfile`: Python 3.12 container, non-root runtime, one API process on port 8080.
- `.dockerignore`: excludes local environments, test artifacts, research outputs, and environment files from the image context.
- `deployment/k8s/namespace.yaml`: restricted Pod Security namespace labels.
- `deployment/k8s/deployment.yaml`: two replicas, rolling update, health probes, resource bounds, read-only root filesystem, non-root UID, no privilege escalation/capabilities, no automatic service-account token.
- `api/main.py`: `ATLAS_CORS_ORIGINS` exact-origin allowlist for deployment configuration; local origins remain the default for development; empty/wildcard values fail closed.

### Initial preparation checks (2026-11-02; historical)

- `.venv/bin/python -m pytest -q` — **23 passed in 0.82s**, including exact-origin/wildcard CORS, synthetic WTR GeoTIFF QA, and the full 8+8 global balance gate.
- `docker build -t atlas-api:multicloud-prep .` — passed on `linux/arm64`; pinned base image digest `sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337`.
- Final local image digest: ARM64 `sha256:e37c5559a61bc98a96984095aa656a65a8fcc4d1bc56a9574b696143bbde8911`; separately built AMD64 `sha256:2c84a0a27fc7e8e42789f06bb7cc107fbc1913087634f4f8a5f768407a36c6c2`.
- Restricted ARM64 container smoke — passed health, aggregate analysis (12 synthetic records), unknown-field rejection (422), oversized-body rejection (413), allowed-origin preflight, and denied-origin preflight. The container ran as UID/GID 10001 with read-only root filesystem and a bounded `/tmp` mount.
- AMD64 container smoke — passed `/api/health` after the emulator completed initial startup; this was a local emulation check, not a cloud-node deployment.
- Kubernetes YAML parse and structural check — passed for the Namespace, Deployment, and Service resources, including two replicas, probes, and restricted-container settings. No live cluster API/schema admission was available.

Still required before cloud deployment: remote CI success; image/OS scans; SBOM, signature and provenance verification; provider IAM/OIDC trust tests; cloud-specific Terraform and ingress/secrets configuration; cluster policy/schema validation; and staging/production deployment. No cloud-specific infrastructure or deployment has been tested yet. The existing production Site remains private and separate from this proposed cloud API runtime.

## Executable shared verification gate (local source)

`.github/workflows/verify.yml` runs on pull requests and pushes with read-only repository permission and immutable commit references for its two GitHub Actions. It runs the full Python test suite, builds a container candidate, and fails when `pip-audit` finds known vulnerabilities in runtime or development requirements. The same gate applies before any provider-specific workflow; cloud deployment credentials are deliberately absent from this validation workflow.

### Security scan history

The first audit revealed advisories in the framework and runtime packages. That finding led to the direct Starlette migration and current locked stack; the updated scan results are in outputs/atlas-security-scan-findings.md.

The dependency audit report is authoritative for this release gate. A successful image build does not override a failing audit. Once upstream fixes are available, update pins, rerun the audit and tests, and require green results before adding provider-specific OIDC deploy workflows.


### Latest candidate status (2026-11-02)

- Hash-locked runtime/development/audit dependencies are generated by scripts/refresh_dependency_locks.sh and installed using --require-hashes.
- Full target Python 3.12 x86_64 install/test/audit: 26 passed in 6.82s; no known vulnerabilities; secret hook passed.
- Previous local ARM64 image digest: sha256:01bbdadffc2edd20903237ad975ce783887b985af7f2a4eed7e5346c5e03c67c. Image audit found no known vulnerabilities.
- Latest local ARM64 image tag `atlas-api:goal-2026-11-02`, image ID/digest `sha256:5b23d5c85b0f208fed73a17c62630110273042e33e5323d4bdcba43ebe4ba3f4`; it includes the static candidate register used by the new endpoint.
- Latest read-only container HTTP smoke passed **11/11** checks: health, synthetic fixture areas, 8+8 study-area register, aggregate analysis, CSV, invalid field, size bound, malformed JSON, host allowlist, allowed CORS, denied CORS. The smoke runner now waits for API health with a bounded timeout to avoid a startup race.
- This candidate remains a synthetic fixture API; it has not been deployed to any cloud. The GitHub workflow has not run remotely. Account setup, provider IAM/ingress/secret bindings, SBOM/signature/provenance, OS scanning, staging, recovery and performance testing remain pending.

The Kubernetes sample now includes a required API hostname placeholder for `ATLAS_ALLOWED_HOSTS`. Replace it with the approved ingress hostname before deployment; the API rejects unexpected Host headers.
- scripts/smoke_container.py: repeatable 11-check API smoke test for a local or staging container.

### Provider parity expansion (2026-11-02)

- Added `deployment/cloud/provider-matrix.yaml` as the comparable GKE/EKS/AKS/OKE release policy record, including OIDC trust restrictions, native registry, workload identity, image-pull identity, and per-provider readiness.
- Added `deployment/cloud/RELEASE_RUNBOOK.md` with the same build-once, digest-promotion, protected approval, authenticated staging checks, monitoring window, rollback triggers, and retained evidence for each provider.
- Published review copies at `outputs/atlas-cloud-release-runbook.md` and `outputs/atlas-provider-parity-matrix.yaml` for easy access.
- Used the four providers' official identity and deployment documentation to identify the provider bindings. OCI OKE OIDC is explicitly scoped to cluster authentication; registry publication requires an independent tested short-lived identity path.
- No provider accounts were accessed, no credentials stored, and no infrastructure or cloud deployment was created. The account owner must complete account and billing terms directly; when accounts are ready, only non-secret IDs/region choices are needed to finish the provider bindings.
- This is preparation evidence only and adds no product score points. Current score remains 50/100 provisional; no cloud end-to-end workflow has been run.

### Four-provider parity update (2026-11-02)

- Expanded the common account bootstrap, no-cost pre-provisioning checklist, OIDC allow/deny cases, environment/role separation, private networking, supply-chain verification, runtime policy, log retention, recovery, budget gates, and identical staging E2E outcomes.
- Added provider evidence bindings for GKE/Artifact Analysis, EKS/ECR enhanced scanning, AKS/ACR and Notary Project image signatures, and OKE/OCIR vulnerability scanning. OKE GitHub OIDC remains only an OKE cluster-access pattern until registry publishing has its own verified short-lived identity.
- Owner reports Google Cloud, AWS, Azure, and Oracle Cloud account creation is in progress under `shawdaimarie@gmail.com`. Account signup, terms, billing, MFA, regions, and identity setup are owner-managed and unverified by ATLAS. We have not asked for or received passwords, recovery codes, payment details, access keys, or cloud credentials.
- Added a non-secret onboarding handoff and machine-readable status record. It requires the same owner confirmation, approved region/data-residency decision, cost ceiling and alerts, staging/production boundary, and OIDC setup before any resources are provisioned.
- Clarified that artifact integrity must be preserved and admission-verified after each registry transfer on all providers; Google Artifact Analysis and Oracle registry scanning must be explicitly enabled and their results retained.
- Changes strengthen deployment preparation only; they do not prove provider accounts, remote CI, cloud resources, deployed workflows, or higher project score. Product score remains 50/100 provisional.
- Current rerun on this checkout: 27 tests passed in 0.80s; local restricted-container smoke passed 11/11; provider parity matrix parsed and passed the four-target/common-contract consistency check. The current enrollment and scoring records remain unchanged because cloud staging and scientific validation have not occurred.
