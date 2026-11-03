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
| Google Cloud | A GKE private endpoint is reachable only through the VPC or routed private network. Google documents Cloud Build private-pool access patterns; the private-pool/GKE control-plane path may require Private Service Connect and Cloud VPN because VPC peering is not transitive. | Runner/pool route and private DNS resolu