# ATLAS shared Kubernetes baseline

These manifests are a common workload baseline for the GKE, EKS, AKS, and OKE staging targets. They are templates, not a deployable cluster package: provider-specific cluster networking, authenticated ingress, TLS, secret bindings, workload identity, registry policy, and provider admission controls must be supplied and tested before use.

## Network policy contract

`network-policy.yaml` denies ingress and egress for all pods in namespace `atlas`, then permits the `atlas-api` pods to receive TCP/8080 only from an ingress controller whose namespace has label `atlas.network/role=trusted-ingress` and whose pods have label `app.kubernetes.io/name=atlas-ingress-controller`. The API can send DNS to CoreDNS pods selected by `k8s-app=kube-dns` in `kube-system` on UDP/TCP port 53. There is no internet, node, or peer-namespace egress allow rule.

Before applying the workload, make the exact labels true for the selected ingress controller and confirm the cluster CNI enforces Kubernetes NetworkPolicy. A policy object can be accepted by an API server without being enforced by the data plane. Verify an allowed request from the approved ingress path and denied requests from an unapproved namespace, pod, and external route. Include kubelet readiness/liveness probe behavior and provider load-balancer health checks in this test; provider network implementations differ.

The HTTP probes send `Host: localhost`, and the allowed-host list includes `localhost` solely for those node-originated checks. Replace the API hostname placeholder with the exact public/private ingress hostname while preserving this additional `localhost` entry. Verify probe responses on every provider because provider-level health checks may use a different path and source.

The API has no legitimate external egress in its current fixture-only mode. If later code must read object storage, a secret service, or telemetry endpoint, use the provider's private endpoint or controlled egress gateway, add only the required destination/port/identity, then rerun positive and negative network tests. Do not weaken the baseline to `0.0.0.0/0` or all namespaces. A future raster-processing worker should use a separate service account and policy from this API.

`resource-controls.yaml` caps the namespace and keeps one API replica available during voluntary disruptions. Revisit the quota only with a measured capacity and cost case. The deployment defaults to two replicas with per-pod requests and limits; the quota is intentionally finite.

## Unresolved production controls

The shared deployment does not configure authenticated ingress, cloud IAM, persistent data, production secrets, backup, restore, or a provider-native cluster. The fixture API has no user authorization or real-data connector. Do not interpret Kubernetes object validation or green repository CI as a cloud deployment or production security result.
