# ATLAS Apple distribution readiness

Updated 2026-11-04 America/Chicago. The user confirmed that ATLAS should use their existing Apple Account for its Apple deployment while the Google Cloud, AWS, Azure, and Oracle accounts are being set up. This note separates the private browser deployment from the Apple app release path.

## Current verified state

- The deployed ATLAS product is a private, browser-based Site at `https://atlas-water-screening.shawdaimarie.chatgpt.site/`, currently version 61 and restricted to the owner `shawdaimarie@gmail.com` (Sites reports one allowed user and zero external visitors). Version 61 succeeded from Site-source commit `1bf4d1659270e6516235433259bf3b657361eb6b`, deployment `appgdep_6aeb0960487881919cdf41f78877eee8`; live evidence is in `outputs/atlas-v61-live-revalidation-2026-11-04.md`. It is not hosted by Apple.
- The repository contains a static web experience in `dist/index.html`; it has no `.xcodeproj`, `.xcworkspace`, Swift source, or iOS app target.
- This Mac has Apple command-line developer tools, but `xcodebuild -version` fails because the active developer directory is Command Line Tools rather than a full Xcode installation. An iOS archive cannot be built here yet.
- The user explicitly directed that Apple deployment use their existing Apple Account while they are creating the four cloud accounts. An Apple Account does not host the browser Site. Apple Developer Program membership and App Store Connect access remain unverified. The Mac has only Command Line Tools; `xcodebuild -version` confirms full Xcode is unavailable, and there is no iOS app target in this repository. No app record, bundle identifier, signing team, certificates, provisioning profile, or TestFlight build has been verified or created. Account ownership alone does not establish distribution readiness.

## Apple account release path

An Apple Account can sign in to Apple developer services. App development and device testing can begin without paid membership, but Apple says distribution through TestFlight and App Store Connect requires Apple Developer Program membership. Apple provides App Store and TestFlight distribution for Apple-platform apps; those services do not replace the current website host or make an owner-only web page an iOS app.

To make an Apple release buildable and reviewable:

1. Install the full Xcode application and confirm its supported iOS SDK/simulator versions.
2. Decide the target: native iOS/iPadOS app, or continue with the private browser-based Site. A thin web-view wrapper is not a release-ready substitute without native value and Apple review.
3. If proceeding with an app, confirm the existing developer account's team, membership, legal entity/seller identity, and account-holder or developer access in App Store Connect. Keep Apple credentials and signing keys in Apple's protected account and signing tools; do not put them in the repository or ATLAS runtime.
4. Define an app identifier, privacy disclosures, app support/contact details, accessibility acceptance, data-source attribution, and the account/review access needed for Apple's review. The current owner-only Site and Sign in with ChatGPT flow must be tested in the app review context before submission.
5. Implement the app experience, build and sign an archive in Xcode, run simulator and device checks, upload a build to App Store Connect, and verify a TestFlight install before any App Store submission.

## Readiness gate

Apple app distribution is **not ready and has not been attempted**. The latest private browser Site v61 is operational, but remains separate from an iOS application. The current private web deployment is Site v61 and remains available as a browser demo. The user specified their existing Apple Account as the intended Apple distribution account; its Developer Program membership and App Store Connect access still need verification. To distribute ATLAS as an iOS app through TestFlight or the App Store, full Xcode must be installed and a native app target designed, implemented, signed, and tested. Apple allows development and testing on personal devices without paid membership; TestFlight and App Store Connect distribution require Apple Developer Program membership ([program overview](https://developer.apple.com/help/account/membership/programs-overview/)). The current owner-only Site and ChatGPT sign-in also need a deliberate app-review/access plan. This Apple app path does not host the browser Site, change the ATLAS research score, or count as a Google Cloud, AWS, Azure, or Oracle deployment.

## Apple references

- [Apple Developer Program](https://developer.apple.com/programs/): describes membership benefits, TestFlight, and distribution.
- [Apple developer program overview](https://developer.apple.com/help/account/membership/programs-overview): distinguishes personal-device testing from distribution tools, including Certificates, Identifiers & Profiles, TestFlight, and App Store Connect.
- [App Store Connect workflow](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-workflow/): describes app build, beta, and distribution management.
