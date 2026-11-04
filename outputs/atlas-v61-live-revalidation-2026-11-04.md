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

## Fresh authenticated browser replay — 2026-11-04

- Sites control-plane readback reconfirmed version 61 as the latest release and deployment `appgdep_6aeb0960487881919cdf41f78877eee8` as `succeeded`. The private production URL remains active and owner-only; the allowed account is `shawdaimarie@gmail.com`, with zero external visitors.
- Opened the production Site in a visible authenticated browser tab. The rendered interface exposed all 16 candidate areas (8 U.S. and 8 international), the 2025 matched RTC availability panel, evidence links, the shared five-step public-value framework, and explicit candidate-only/independent-label gates. Readback showed 192/192 selected spatial-availability groups meeting the 80% screen across 16/16 areas; this remains an availability quota, not event/baseline adequacy or flood validation.
- Selected Singapore, Dubai, and Mumbai in turn. Each profile loaded location-specific public management evidence, its comparable validation path and limits, and the same 12-group 2025 coverage screen. Singapore's single 2025-05-22 PUB point alert is identified as an event lead, not an extent; Dubai's published capacity values remain planned targets; Mumbai's approved flood-mitigation budget is not a measured flood outcome.
- Ran the separate illustrative analysis as Baton Rouge / Hurricane Ida. Changing from single-observation to quality-aware aggregation updated the synthetic ranking from 4 to 3 elevated assets and median overlap from 7.7% to 6.8%. Selecting Southeast Water Plant showed 18.9% synthetic overlap, 93% fixture coverage, and 73% uncalibrated fixture confidence. The export control confirmed download and explicitly labeled the evidence synthetic. Reset returned to the single-scene baseline (4 elevated assets; 7.7% median overlap; Bayou East Substation selected).
- The browser was left open on the live Site with the Baton Rouge / Ida synthetic scenario and Mumbai evidence profile visible. The screenshot shown in the accompanying walkthrough captures this state.
- Current worktree verification in the digest-pinned Python 3.12 Bookworm image, with both lock files installed using `--require-hashes`: **171 passed in 1.94s**. `git diff --check` passed. A recursive comparison found the 27 local `dist/` files byte-identical to the saved v61 Site source; no new Site archive or release was needed.

This replay validates rendered UI paths and download confirmation only. It did not inspect the downloaded CSV bytes in this run, retrieve NASA data, validate flood observations, or convert any area from candidate to confirmatory. Analysis/map/asset values remain generated fixtures; the research score remains **60/100 provisional** and enrollment remains **0/16**.
