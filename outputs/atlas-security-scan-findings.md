# ATLAS dependency and secret scan record

**Run date:** 2026-11-02\
**Dependency audit:** pip-audit 2.9.0\
**Secret scanner:** detect-secrets 1.5.0\
**Target:** hash-locked Python 3.12 x86_64 development/runtime dependency set and the ARM64 API candidate image.

## Current results

| Check | Result | Scope and evidence |
|---|---|---|
| Hash-locked development install | Pass | pip install --require-hashes -r requirements-dev.lock in disposable Debian Python 3.12 x86_64 with libexpat1. |
| Full unit/fixture suite | Pass | 26 passed in 6.82s with the current lock, Starlette 1.10.0, Rasterio 1.5.2, NumPy 2.5.4, pytest 9.2.0 and httpx2 2.16.0; no warnings. |
| Dependency audit | Pass | python -m pip_audit after locked install: **No known vulnerabilities found**, including pip 26.3 and the audit tool. |
| Secret baseline scan | Pass | detect-secrets scan --all-files over the project, excluding Git, virtual environments, Site checkout, pytest cache and scratch; **0 potential findings**. |
| Secret baseline hook | Pass | git ls-files -co --exclude-standard -z \| xargs -0 detect-secrets-hook --baseline .secrets.baseline; tracked and new nonignored files accepted. |
| Runtime image audit | Pass | Built API image with requirements-runtime.lock; installed hash-locked audit tool into a disposable container layer; **No known vulnerabilities found**. |
| Container HTTP smoke | Pass | Exact image digest sha256:01bbdadffc2edd20903237ad975ce783887b985af7f2a4eed7e5346c5e03c67c (linux/arm64), read-only root: **10/10** workflows passed. |

## Remediation history

An earlier audit found advisories in Starlette, AnyIO, pytest, python-dotenv, and the base image pip. The API was moved from FastAPI to Starlette directly so it could use the fixed Starlette 1.x line. The app now applies TrustedHostMiddleware using exact ATLAS_ALLOWED_HOSTS, and the unused dotenv-capable Uvicorn extra was removed. Current pins are Starlette 1.10.0, AnyIO 4.16.0, Uvicorn 0.54.0, Pydantic 2.14.2, pip 26.3, Rasterio 1.5.2, affine 3.0.1, pytest 9.2.0, and httpx2 2.16.0.

Runtime, development, and audit dependencies are pinned with hashes in requirements-runtime.lock, requirements-dev.lock, and requirements-audit.lock. scripts/refresh_dependency_locks.sh regenerates them using pip-tools 7.6.2. Docker installs the runtime lock with --require-hashes.

The current source audit found no secrets. The generated .secrets.baseline contains no findings; the hook fails if new candidate secrets appear. Review and audit any baseline changes instead of automatically accepting new findings.

## Limits

These are author-run checks, not an independent security review. The GitHub Actions workflow has not yet run remotely. No cloud account or API deployment was used; the live Site remains a separate static, synthetic walkthrough. Provider IAM, authenticated ingress, secret-store integration, cloud image signatures/SBOM, OS-package scanning, recovery, and staging/production scans are still pending.

## Primary project security references

- [Starlette release notes](https://github.com/Kludex/starlette/blob/main/docs/release-notes.md) document the 1.0.1, 1.1.0 and 1.3.1 security fixes and later releases.
- [AnyIO releases](https://github.com/agronholm/anyio/releases) document the 4.14.2 IDNA/TLS fix; the project pins 4.16.0.
- [pytest releases](https://github.com/pytest-dev/pytest/releases) document the 9.0.3 fix; the project pins 9.2.0.
- [Rasterio releases](https://github.com/rasterio/rasterio/releases) document 1.5.2 packaging and Python support; Rasterio 1.5+ requires Python 3.12+.
- [Yelp detect-secrets usage](https://github.com/Yelp/detect-secrets) documents baseline generation and hook checks.
