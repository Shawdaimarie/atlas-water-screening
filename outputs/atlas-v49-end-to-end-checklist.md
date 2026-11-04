# ATLAS Site v49 end-to-end checklist

Updated: 2026-11-04

## Fresh authenticated production replay — 2026-11-04

- Sites control-plane readback confirms v49 is still active at the owner-only production URL, owned by `shawdaimarie@gmail.com`, with zero external visitors.
- Opened the live Site in the in-app browser and checked all 16 study-area controls. Every profile matched its selected area and exposed a location-specific rationale, value-integration question, and comparable validation path (16/16 for each check).
- Ran the demo workflow: selected Baton Rouge / Hurricane Ida, opened Singapore's international evidence profile, changed from single observation to quality-aware aggregate, and inspected Southeast Water Plant. The displayed result changed to 18.9% illustrative overlap, 93% fixture coverage, and 73% uncalibrated fixture confidence; the source remained clearly labeled synthetic.
- Triggered both **Export evidence** and **Download area register**. Each showed its success confirmation. This replay did not inspect the downloaded bytes; earlier release records contain the parsed-export checks.
- Tested **Reset**. It preserved Baton Rouge / Hurricane Ida, returned the method to single observation, and selected the default Bayou East Substation. Restored the page to Baton Rouge / Ida, Singapore, quality-aware aggregate, and Southeast Water Plant for the visible walkthrough.
- The complete current-worktree Python suite passed **141/141 in 1.28 seconds** in the digest-pinned Python 3.12 Bookworm ARM64 container with both `requirements-dev.lock` and `requirements-reference-audit.lock` installed using `--require-hashes`. The earlier local Python 3.9 attempt could not collect because its environment lacks the separate spatial-audit dependencies; it is not the supported verification environment.
- `git diff --check` passed after this replay record was prepared. The current browser replay did not inspect console logs or the saved download bytes.

This addendum verifies the deployed UI workflow and current local regression suite. Fixture analysis remains synthetic; this does not establish flood-science validity, cloud-provider deployment, or Apple app distribution.

## Local evidence refresh after the production replay

- The first package attempt reported a temporary-directory cleanup error after creating the source commit. The commit was verified on the Site-linked branch, packaging succeeded on retry, and v50 was deployed; see the v50 checklist.

- Reproducible BPBD/admin-boundary screen found 20 of 21 named affected kelurahan polygons with positive-area overlap against the fixed Jakarta AOI. Limits and query checksum: `outputs/atlas-jakarta-bpbd-jan2026-aoi-context.md` and `.json`.
- The 8+8 matrix and readiness ledger include this source-linked context, with all 16 profiles still comparable in method and no areas eligible for confirmatory enrollment. The intersecting municipality polygons are not flood pixels, independent labels, or proof that inundation occurred inside the AOI.
- Rebuilt the generated ledger and matrix, then reran the complete pinned Python 3.12 suite: **143 passed in 1.42s**; `git diff --check` passed.
- The 20/21 context and linked JSON were later published as Site v50; the post-deployment record is [here](atlas-v50-end-to-end-checklist.md).

## Release identity

- Product: private, owner-only ATLAS browser Site at <https://atlas-water-screening.shawdaimarie.chatgpt.site/>.
- Saved Site version: 49; deployment `appgdep_6aeacd3f4ca88191850c6d3e32ba3d53` succeeded.
- Source commit: `b3c03bb796395b802a58b514ddcb5d23bed54266`.
- Packaged archive: `/private/tmp/atlas-site-v49.tar.gz`.
- Archive SHA-256: `d5c46ed78c42dbc500c8a343bfd67b6d9047a09714737f45fff6e922e9839ff2`.
- Site readback confirmed version 49 active with owner-only access and zero external visitors.

## Verification evidence

- Authenticated production browser replay changed the scenario to Houston / Hurricane Beryl and back to Baton Rouge / Hurricane Ida; selected Jakarta and Singapore profiles; switched from single observation to quality-aware aggregate; and selected Southeast Water Plant. The resulting page showed the expected Baton Rouge / Ida heading, Singapore profile, aggregate method, and Southeast Water Plant detail.
- Observed asset detail: 18.9% illustrative overlap, 93% fixture coverage, 73% uncalibrated fixture confidence, data source Synthetic.
- The 16-area readiness panel now states that New Orleans has one WTR/BWTR catalog granule whose name encodes `2026-06-21T00:10:10Z` to `2026-06-27T00:58:29Z`; the service date field is absent, so the interval is not counted as multiple acquisition dates.
- The deployed audit JSON endpoint includes the granule-name interval and `date_basis="granule_name_interval_only"`; `date_utc` stays null. This is catalog metadata, not downloaded raster pixels or water labels.
- Fresh live NASA EGIS catalog audit: 40 disaster folders, 9 candidate services, 27 spatial catalog records, zero query/service errors. The report records 12 water-layer records across Tampa, Miami, and New Orleans; New Orleans's name-only interval remains distinct from service acquisition dates.
- Digest-pinned Python 3.12 Bookworm suite passed **141/141 in 1.34 seconds** using `python:3.12-bookworm@sha256:a5bab0ff300f91231c2e68bf73a8a8d60762ac39ce1c50eaf6803e4c38a9062b`.
- `git diff --check` passed; generated source and deployed output copies were checked for consistency.
- Current browser console error list was empty.

## Interpretation and open gates

- All analysis values remain synthetic fixtures. This is a workflow demonstration, not a validated flood product.
- Study frame remains 8 U.S. and 8 international candidate areas; confirmatory enrollment remains **0/16**.
- Canonical evaluation remains **60/100 provisional**; the metadata provenance correction adds no score points.
- Google Cloud, AWS, Microsoft Azure, and Oracle Cloud deployments remain unverified.
- The user's existing Apple Account is selected for future Apple app distribution. The browser Site is not hosted by Apple. There is no iOS app target, full Xcode installation, or verified Apple Developer Program/App Store Connect access; Apple distribution is not ready or attempted. See [Apple distribution readiness](atlas-apple-distribution-readiness.md).
