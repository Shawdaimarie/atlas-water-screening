# ATLAS v61 live revalidation — 2026-11-04

## Release identity and access

- Private Sites project `appgprj_6ae8f548d7a48191adbbfe7affb04a94` published v61 at `https://atlas-water-screening.shawdaimarie.chatgpt.site`.
- Sites control-plane readback confirms v61 is the latest version, deployment `appgdep_6aeb0960487881919cdf41f78877eee8` succeeded, and the live URL remains active. Current access policy is custom/owner-only: `shawdaimarie@gmail.com` is the only allowed user and external visitor count is zero. Site source commit: `1bf4d1659270e6516235433259bf3b657361eb6b`. The source was uploaded through PR [#9](https://github.com/Shawdaimarie/atlas-water-screening/pull/9), merged to canonical main as `0918a5cc00e3232c9f6e4e541894923d4d6fbb3c`; all 28 Site-source file blobs match main exactly.
- Production browser replay shows the SenForFlood card, its dataset-paper and Dataverse citations, the machine-readable audit link, and the interpretation report link. The app still labels its map and scenario results as synthetic fixtures and states that no NASA observation was retrieved.
- This release is the private browser Site. Apple distribution is planned with the user's existing Apple Account; it does not constitute an iOS build or Apple release. Full Xcode, Developer Program membership, and App Store Connect readiness remain unverified.

## SenForFlood screen

The pinned Hugging Face snapshot contained 4,023 mask GeoTIFFs (27,681,760 bytes). Every mask was retrieved, size checked, hashed, and opened; 177 AppleDouble sidecars were excluded. Reprojected footprints were compared with all 16 registered study boxes. Result: 0/4,023 chips overlap and 0/16 areas have mask-chip coverage in this snapshot. See `outputs/atlas-senforflood-mask-coverage-audit.md` and its JSON manifest for revision, paths, sizes, SHA-256 digests, and results.

This is not evidence that floods did not occur. The repository says its upload is in progress, so the finding is limited to pinned revision `aa33be10fffbd3a82370fdd91327d8545107b43f`. Automatic DFO masks are not independent ground truth; analyst-created CEMS masks still need event-time, imagery-lineage, adequacy, and licensing review. The audit adds no independent labels or confirmatory sites.

## Verification

- Full local suite after the v61 change: `.venv/bin/python -m pytest -q` — **171 passed in 1.94 s** on revalidation; one environment warning notes urllib3 running with LibreSSL.
- `git diff --check` succeeded.
- Live private production page rendered the new card and report links. Confirmatory eligibility remains **0/16**.
- Canonical score remains **60/100 provisional**. No score points were awarded for discovery coverage or the deployed evidence card. PR #9 CI runs 41815923447 and 41815980306 both passed tests, image/smoke, and dependency-security jobs.

## Remaining limits

The browser workflow still runs on synthetic scenario/map/asset fixtures. Real event-linked OPERA observations, independent licensed labels, completed probability sampling and precision checks, cloud releases, provider security enforcement, and native Apple release evidence remain outstanding. The current cloud account preflight reports 29 missing or invalid inputs.
