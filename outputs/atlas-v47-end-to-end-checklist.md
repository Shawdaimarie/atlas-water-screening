# ATLAS v47 production end-to-end checklist

**Checked:** 2026-11-04 UTC  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Status:** private owner-only Site, v47 active. Demo analysis values are generated synthetic fixtures; they are not operational flood measurements.

## Release identity

- Sites readback reports the Site active at v47, with custom owner-only access and zero external visitors.
- Site source commit: `e7eb90f889b4ba49aa7af5ccfd6dc1217bd9393e`.
- Deployment: `appgdep_6aeac6f99dc0819190d494d8eec18931` (succeeded).
- Deployed archive SHA-256: `c933347c4d8171347a3d3cbd54a74ce381e4ae1b9cb6ab89198f911912f7d3ec`; 18 packaged files.

## Production walkthrough and results

1. **Load and access:** the authenticated production page loaded. Sites readback reports the owner as the only allowed account and zero external visitors.
2. **16-area evidence panel:** all eight U.S. and eight international candidate choices appear in the same evidence screen. The shared framework and validation caveats are visible. Selecting Singapore displays its profile, public-agency context, value-integration question, comparable validation path, and scope limit.
3. **Scenario and method:** selected Baton Rouge and Hurricane Ida, then selected the quality-aware aggregate method. The page updated to the Baton Rouge/Ida title and windows, with a 6.8% synthetic median overlap.
4. **Asset detail:** selected Southeast Water Plant; its selected state and asset detail are visible in the deployed page.
5. **Evidence CSV:** downloaded and parsed the production export: 12 rows, all for Baton Rouge/Hurricane Ida, the event window `2021-08-29/2021-08-30`, baseline `2021-08-15/2021-08-25`, method `aggregate`, and provenance `synthetic_fixture_no_live_NASA_data`. The page displayed its download-success status.
6. **8+8 register CSV:** downloaded and parsed the production register: 16 rows, 8 United States and 8 International. It includes the common footprint, source evidence, value-integration questions, validation paths, and scope limits.
7. **Published evidence ledger:** parsed the live JSON endpoint: 16 areas, 8+8 split, 0 confirmatory-eligible areas, and 3 areas with 12 candidate OPERA S1-water catalog records (Miami 3, Tampa 7, New Orleans 2).
8. **Linked NASA EGIS audit:** parsed the live audit JSON. It contains 27 catalog-footprint records across the screened audit; 12 are candidate S1-water layers in the same three areas. The records are metadata/footprint discovery only, not independent truth or proof of complete-scene pixel coverage.
9. **Browser console:** zero console errors during the production interaction replay.

## Source test results

- Full current-worktree test suite in the digest-pinned Python 3.12 Bookworm environment, with both lock files installed using hash verification: **139 passed in 2.47 seconds**.
- The test run verifies repository behavior; it does not turn synthetic fixtures or public catalog metadata into scientific validation.

## Guided walkthrough

The production page is open in the authenticated in-app browser. The current view is set to Singapore's candidate profile alongside the separate Baton Rouge/Hurricane Ida synthetic demo. To replay the demo, choose **Quality-aware aggregate**, select **Southeast Water Plant**, and choose **Export evidence**. The browser downloads a 12-row synthetic CSV. The 16-area readiness ledger and linked catalog-footprint audit are below the candidate profiles.

## Research and release limits

- Demo map, assets, overlap, coverage, confidence, and exports remain synthetic; no NASA granule is loaded by this walkthrough.
- The 8+8 city list is a candidate screen, not a confirmatory comparison. **0/16** areas meet the complete confirmatory eligibility gates; the study still needs event-matched QA-valid OPERA scenes, licensed independent reference labels, probability sampling, adjudication, and the predeclared precision gate.
- The canonical rubric remains **60/100 provisional**. This release and user-interface testing do not add scientific-validity points.
- The user has directed the project to use their existing Apple account for future Apple-platform distribution. Site v47 remains a browser Site and is not hosted by Apple. Apple Developer membership/App Store Connect access remain unverified; this Mac has Command Line Tools but no full Xcode, and the repository has no iOS app target. No Apple build or submission was attempted. See [Apple distribution readiness](atlas-apple-distribution-readiness.md).
- Google Cloud, AWS, Microsoft Azure, and Oracle deployments remain preparation-only; no provider infrastructure has been deployed.
