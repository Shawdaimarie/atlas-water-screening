# ATLAS Apple distribution readiness

Updated 2026-11-03. This note separates the existing private web deployment from a future Apple-platform app release.

## Current verified state

- The deployed ATLAS product is a private, browser-based Site at `https://atlas-water-screening.shawdaimarie.chatgpt.site/`, currently version 27 and restricted to the owner account. Its authenticated UI and live evidence-ledger endpoint were checked. It is not hosted by Apple.
- The repository contains a static web experience in `dist/index.html`; it has no `.xcodeproj`, `.xcworkspace`, Swift source, or iOS app target.
- This Mac has Apple command-line developer tools, but `xcodebuild -version` fails because the active developer directory is Command Line Tools rather than a full Xcode installation. An iOS archive cannot be built here yet.
- The user confirmed the existing Apple account is the intended Apple distribution account while the four cloud accounts are being applied for. The Apple Account page currently shows its sign-in screen; no sign-in was performed, so Developer Program membership and App Store Connect access remain unverified. The Mac has only Command Line Tools; `xcodebuild -version` confirms full Xcode is unavailable, and there is no iOS app target in this repository. No app record, bundle identifier, signing team, certificates, provisioning profile, or TestFlight build has been verified or created. Account ownership alone does not establish distribution readiness.

## Apple account release path

An Apple Account can sign in to Apple developer services. App development and device testing can begin without paid membership, but Apple says distribution through TestFlight and App Store Connect requires Apple Developer Program membership. Apple provides App Store and TestFlight distribution for Apple-platform apps; those services do not replace the current website host or make an owner-only web page an iOS app.

To make an Apple release buildable and reviewable:

1. Install the full Xcode application and confirm its supported iOS SDK/simulator versions.
2. Decide the target: native iOS/iPadOS app, or continue with the private browser-based Site. A thin web-view wrapper is not a release-ready substitute without native value and Apple review.
3. If proceeding with an app, confirm the existing developer account's team, membership, legal entity/seller identity, and account-holder or developer access in App Store Connect. Keep Apple credentials and signing keys in Apple's protected account and signing tools; do not put them in the repository or ATLAS runtime.
4. Define an app identifier, privacy disclosures, app support/contact details, accessibility acceptance, data-source attribution, and the account/review access needed for Apple's review. The current owner-only Site and Sign in with ChatGPT flow must be tested in the app review context before submission.
5. Implement the app experience, build and sign an archive in Xcode, run simulator and device checks, upload a build to App Store Connect, and verify a TestFlight install before any App Store submission.

## Readiness gate

Apple distribution is **not ready and has not been attempted**. The current private web deployment is Site v27 and remains available as a browser demo. The existing Apple Account can open the live site in Safari, but Apple does not host this browser deployment through an Apple Account. To distribute ATLAS as an iOS app through TestFlight or the App Store, the account's Developer Program/App Store Connect access must be verified, full Xcode installed, and a native app target designed, implemented, signed, and tested. Apple says free membership is enough to begin development and test on personal devices; TestFlight/App Store Connect distribution requires Apple Developer Program membership ([program overview](https://developer.apple.com/help/account/membership/programs-overview/)). The current owner-only Site and ChatGPT sign-in also need a deliberate app-review/access plan. This Apple track does not change the ATLAS research score or count as a Google Cloud, AWS, Azure, or Oracle deployment.

## Apple references

- [Apple Developer Program](https://developer.apple.com/programs/): describes membership benefits, TestFlight, and distribution.
- [Apple developer program overview](https://developer.apple.com/help/account/membership/programs-overview): distinguishes personal-device testing from distribution tools, including Certificates, Identifiers & Profiles, TestFlight, and App Store Connect.
- [App Store Connect workflow](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-workflow/): describes app build, beta, and distribution management.
