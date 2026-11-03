# Local Kubernetes policy smoke result

**Run date:** 2026-11-02  
**Cluster:** disposable kind v1.35.0, Calico v3.32.3  
**ATLAS image:** local `atlas-api:secure-candidate` (`sha256:e5239a544edb12b7525f09a6f025051000dc845c1519f2a6be673244db3b014f4`)

## Result

| Check | Observed result |
|---|---|
| API deployment | 2/2 replicas available; readiness and liveness probes passed after correction below. |
| Approved ingress namespace and pod labels | `GET /api/health` returned HTTP 200 and reported `synthetic_fixture`; `live_nasa_ingestion` was `false`. |
| Untrusted namespace | Request timed out, as required by the default-deny ingress policy. |
| API DNS egress to CoreDNS | `atlas-api.atlas.svc.cluster.local` resolved successfully. |
| API peer TCP egress | Connection timed out, as required by default-deny egress. |
| Resource controls | ResourceQuota and PodDisruptionBudget were accepted; quota reported 2/10 pods. |

## Issue found and fix

The first rollout left both replicas unready because kubelet HTTP probes used each pod IP as the `Host` header, which the API's exact-host middleware rejected with HTTP 400. The deployment now sets `Host: localhost` on both probes and retains `localhost` in the exact allowed-host list alongside the configured API hostname. The repeated rollout reached 2/2 ready replicas.

## Limits

This validates policy enforcement only in a local Calico-backed kind cluster. It does not establish behavior in GKE, EKS, AKS, or OKE, nor authenticate users, validate provider ingress/load-balancer health checks, or create a production cloud deployment. No canonical rubric points were added from this smoke run. The temporary cluster was deleted after verification.
