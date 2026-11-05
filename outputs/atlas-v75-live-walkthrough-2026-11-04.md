# ATLAS v75 live production walkthrough

**Checked:** 2026-11-04 America/Chicago  
**Production URL:** https://atlas-water-screening.shawdaimarie.chatgpt.site/  
**Release:** Site v75, active; source commit `0c7e90f4351ffa07aaf8797073bdd89808f08845`  
**Access:** owner-only Site; live Site readback lists `shawdaimarie@gmail.com` as the only owner and zero external visitors.

## Walkthrough performed

Opened the live production URL in a visible ChatGPT in-app browser tab and exercised the current release. The browser showed the ATLAS application rather than a sign-in or error page.

1. **Candidate-area profile:** selected Dubai. The profile rendered the common 625 km² footprint, 1,009 OPERA metadata hits, 381 distinct metadata dates, location-specific Dubai Municipality evidence, a value-integration question, and its validation path. It explicitly described the profile as candidate-only and identified pixel QA and independent labels as pending. The profile displayed 12/12 sampled 2025 RTC groups over the 80% spatial screen.
2. **Scenario switch:** selected Hurricane Ida. The analysis changed to the Baton Rouge scenario and updated its event dates, window labels, and asset IDs.
3. **Method comparison:** selected the quality-aware aggregate. The method label changed to a three-observation illustrative aggregate, the metric/ranking changed, and assets marked synthetic remained labeled as such.
4. **Asset detail:** selected Southeast Water Plant. The detail panel updated to that asset, its illustrative overlap, valid coverage, and synthetic source label.
5. **Evidence export:** activated Export evidence. The live page announced that the file was downloaded with the scenario, observation windows, method, and synthetic-data label.
6. **Study-register export:** activated Download area register. The page announced success; the downloaded CSV was checked locally and contained 16 unique areas (8 U.S.; 8 international).
7. **Live evidence endpoint:** opened the deployed JSON evidence register. The response contained 16 city records (8 U.S.; 8 international), including Jakarta and Dubai, plus the shared study protocol and location-specific evidence and limitations.
8. **Reset:** activated Reset analysis. The live page returned to the single-observation baseline and its original four-asset ranking; the selected study-area profile remained available.
9. **Research evidence panel:** the live page displayed the full 16-area frame (8 U.S. and 8 international), a 192/192 coverage-conditioned RTC quota across 16/16 areas after screening 34 additional groups, the initial 169/192 unconditioned result, and a clear statement that confirmatory eligibility remains 0/16. The 192/192 figure is availability-only and not flood validation.

### Full 16-area profile replay

On a fresh owner-session production tab, selected each candidate area in turn. **16/16 passed** the same rendered-profile checks: selected city and U.S./international label; candidate-only status; public evidence; value-integration question; comparable validation path; evidence-scope limit; and the common 12/12 sampled 2025 RTC availability quota. The sequence covered Houston, Miami, Tampa, New Orleans, New York City, Sacramento, Atlanta, St. Louis, Jakarta, Singapore, Dubai, Mumbai, Bangkok, Tokyo, Manila, and São Paulo. This is an author-run live UI replay; it verifies that the fields render for every area, not the truth of each source claim or scientific eligibility.

## Validation limits

- ATLAS runs against the current production Site. This UI replay verifies the walkthrough controls and their displayed outputs; the scenario, asset, and analysis values are generated synthetic fixtures, not live NASA analysis.
- 192/192 is a deterministic, coverage-conditioned Sentinel-1 RTC spatial-availability quota. It is not an estimate of unconditional archive quality and does not satisfy OPERA event/baseline sampling or independent reference-label requirements.
- The current canonical research score remains **60/100 provisional**; no points were added from this replay. Confirmatory eligibility remains **0/16**.
- The current Python 3.9 worktree test run passed **202/202 in 1.99 seconds** on 2026-11-04 (one existing urllib3/LibreSSL warning). `git diff --check` also passed. This local suite is separate from browser interaction and scientific validation.
- This replay does not verify VoiceOver/screen-reader acceptance, participant usability, independent source-claim review, cloud-provider deployment, or Apple app distribution.

## Guided user walkthrough

Open the URL above and start at the **16-area evidence and coverage screen**. Select Dubai, Mumbai, Jakarta, or Singapore to read its source-backed public-need context and common value-integration fields. Expand **Compare 12 accepted sampled dates for all 16 areas** to inspect the matched RTC coverage display. Scroll to **Reference-label coverage is not yet comparable** to review source-by-source gaps. The banner on the left identifies the synthetic scenario demo; switch between Hurricane Beryl/Houston and Hurricane Ida/Baton Rouge, compare the two screening methods, inspect an asset, export evidence, and reset.

Read the research counts as screening evidence: current eligibility is 0/16, and the scenario/asset metrics are illustrative. The live Site remains private and owner-only.
