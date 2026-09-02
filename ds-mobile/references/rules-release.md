# Rules: Release Readiness & Store Submission

Rules for release-ready mode. Each rule: ID, severity, title, detect pattern, fix action.

## Build Configuration

### REL-02 [CRITICAL] Release Signing Configuration
Release builds must use release signing, not debug, on every platform the app ships to.
- **Detect:**
  - Android: `signingConfig = signingConfigs.debug` in release block, or no release signing config defined
  - iOS: archive built with a development/ad-hoc provisioning profile instead of an App Store distribution profile; expired or revoked distribution certificate
  - Expo/EAS: `eas.json` build profile missing `"distribution": "store"` credentials, or `credentialsSource` pointing at local ad-hoc keys for a production build
- **Fix:** Android: configure release signing with a keystore, credentials in CI secrets not source code. iOS: build with an App Store distribution certificate + profile (`xcodebuild archive` / Xcode Cloud / fastlane `match`). Expo/EAS: run `eas credentials` to provision store-distribution credentials for the production build profile.
- **Impact:** A release build signed with the debug key (or unsigned) cannot be uploaded to either store — this fails at the build/upload step, before any review even starts.
- **Source:** Android App Bundle requirements, Apple code signing guide, Expo EAS credentials docs

### REL-04 [HIGH] Version Format
The app's version identifiers must follow the platform's required format on every platform it ships to.
- **Detect:**
  - Flutter: version in pubspec.yaml not matching `^\d+\.\d+\.\d+\+\d+$`
  - Native Android: `versionName` not semver-shaped, or `versionCode` not a monotonically increasing integer across releases
  - Native iOS: `CFBundleShortVersionString` not semver-shaped, or `CFBundleVersion` not incremented since the last submitted build
  - Expo/EAS: `app.json`/`app.config.*` `version` not semver-shaped, or `eas.json` build profile missing `"autoIncrement"` for `buildNumber`/`versionCode` while multiple builds ship from the same version
- **Fix:** Set version to proper semver+build format for the detected platform(s); for Expo/EAS, enable `autoIncrement` (or bump `ios.buildNumber`/`android.versionCode` manually before every submission).
- **Impact:** A malformed version string can be silently rejected by store tooling or, worse, accepted and then unable to receive future updates through the normal upgrade path.
- **Source:** Flutter versioning guide, Apple CFBundleVersion guide, Expo app version docs

### REL-07 [MEDIUM] Android Minification
Release builds should enable code and resource shrinking.
- **Detect:** `minifyEnabled` or `shrinkResources` set to false in release buildType
- **Fix:** Enable both minifyEnabled and shrinkResources.
- **Impact:** Skipping minification ships a larger binary with unstripped class/resource names, giving up free size reduction the build tooling already provides.
- **Source:** Android developer guide

### REL-08 [HIGH] Store Artifact Format
Each store requires its own artifact shape and architecture coverage.
- **Detect:**
  - Android: abiFilters excluding arm64-v8a, or build scripts using `build apk` instead of `appbundle`
  - iOS: archive missing a valid `.ipa` export, or App Store Connect upload skipping the Xcode/Transporter validation step
  - Expo/EAS: `eas build` profile targeting `"buildType": "apk"` for a production Android submission instead of `"app-bundle"`
- **Fix:** Android: remove restrictive abiFilters, build with `flutter build appbundle` / `./gradlew bundleRelease`. iOS: export a distribution `.ipa` and validate with `xcrun altool --validate-app` or Transporter before upload. Expo/EAS: set the production build profile's `"buildType": "app-bundle"`.
- **Impact:** Google Play requires AAB with 64-bit support for new submissions — an APK-only or 32-bit-only build is rejected at upload.
- **Source:** Google Play 64-bit requirement, Apple App Store Connect upload guide, Expo EAS build profiles docs

### REL-26 [HIGH] Staged Rollout Configured
Production releases roll out to a percentage of users first, not 100% at once, on platforms that support it.
- **Detect:** Play Console release created at 100% rollout with no staged percentage step; App Store Connect phased release not enabled for a release with any CRITICAL/HIGH finding still open; EAS/OTA update (`expo-updates`) pushed to all channels simultaneously with no canary channel.
- **Fix:** Android: start Play Console staged rollout at 5-20%, monitor crash-free rate and ANR rate before increasing. iOS: enable App Store Connect's phased release (7-day automatic ramp). Expo: push OTA updates to a canary release channel first.
- **Impact:** A defect that only appears at scale (a rare crash, a backend interaction under real load) reaches every user simultaneously with no rollback window, instead of being caught at 5-20% and halted.
- **Source:** Google Play staged rollout docs, App Store Connect phased release docs, Expo EAS Update channels docs

## Privacy & Compliance

### REL-09 [HIGH] Privacy Policy URL Verification
Privacy policy must be live, accessible URL with valid content.
- **Detect:** No privacy policy URL found in project files, or URL returns error/placeholder content
- **Fix:** Publish privacy policy. Add URL to store listings and in-app settings.
- **Impact:** A privacy-policy link that 404s or shows placeholder text fails store review the same as having no link at all, and is often caught only at submission after everything else passed.
- **Source:** App Store / Play Store requirement

### REL-10 [HIGH] iOS Privacy Manifest
PrivacyInfo.xcprivacy required for App Store submission.
- **Detect:** Missing ios/PrivacyInfo.xcprivacy or missing NSPrivacyAccessedAPITypes
- **Fix:** Create privacy manifest with required API type declarations.
- **Impact:** A missing iOS privacy manifest blocks App Store submission outright as of the 2024 enforcement deadline — Xcode itself will flag it before the store does.
- **Source:** Apple privacy manifest requirement (May 2024+)

### REL-12 [HIGH] Account Deletion Support
Apps with authentication must offer account deletion.
- **Detect:** Auth plugins present but no deleteUser/deleteAccount implementation
- **Fix:** Implement account deletion flow accessible from account settings.
- **Impact:** An app with login but no account-deletion path fails both stores' account-deletion policy, a specifically-reviewed requirement since 2022.
- **Source:** App Store 5.1.1, Play Store Account Deletion Policy

### REL-13 [HIGH] Consent Mechanism
Tracking/analytics must not initialize before user consent.
- **Detect:** Analytics/tracking SDK init before consent dialog, or tracking SDKs without consent package
- **Fix:** Block all non-essential tracking until consent obtained. Ensure correct init order.
- **Impact:** Tracking SDKs that initialize before consent collect data during the exact window consent was supposed to gate, which is the specific pattern EU regulators have fined for.
- **Source:** GDPR, App Store 5.1.2

## Dependencies & Quality

### REL-14 [HIGH] Known Vulnerabilities
No known CVEs in production dependencies.
- **Detect:** `dart pub audit` reports HIGH/CRITICAL advisories
- **Fix:** Update affected packages to patched versions.
- **Impact:** A dependency with a known HIGH/CRITICAL CVE is a published, exploitable weakness — the fix is already public, which makes an unpatched app an easier target than one with an undisclosed flaw.
- **Source:** OWASP M2

### REL-15 [HIGH] SDK Constraint Currency
Dart/Flutter SDK constraint should target current stable.
- **Detect:** SDK constraint targeting EOL version (Dart 2.x)
- **Fix:** Update SDK constraint to current stable range.
- **Impact:** An EOL SDK constraint stops receiving security patches and new OS-compatibility fixes, so the gap between the app and the current platform only widens.
- **Source:** Dart versioning policy

### REL-16 [HIGH] Outdated Major Dependencies
Dependencies should not be more than 1 major version behind.
- **Detect:** `flutter pub outdated` shows 2+ packages with major version gap
- **Fix:** Plan and test major version upgrades.
- **Impact:** Dependencies left 2+ majors behind accumulate breaking-change distance until the eventual upgrade becomes a multi-week migration instead of a routine bump.
- **Source:** Dependency management best practices

### REL-17 [MEDIUM] Static Analysis Clean
Release builds should pass flutter analyze without errors.
- **Detect:** `flutter analyze` reports errors or excessive warnings
- **Fix:** Resolve all errors and reduce warnings.
- **Impact:** Shipping a release build with unresolved analyzer errors means known-bad code patterns reach production because nothing in the release path blocked them.
- **Source:** Flutter quality guidelines

### REL-18 [HIGH] Crash Reporting
Production apps must have crash reporting configured and initialized.
- **Detect:** No crash reporting package (Crashlytics, Sentry, etc.) or package present but not initialized
- **Fix:** Add and properly initialize crash reporting SDK.
- **Impact:** With no crash reporting, a production crash is invisible to the team — the first signal is a drop in reviews or usage, not an alert.
- **Source:** Industry standard

## Localization

### REL-19 [HIGH] i18n Setup
Apps should have internationalization configured.
- **Detect:** No lib/l10n/ directory, no .arb files, no localizationsDelegates
- **Fix:** Set up Flutter l10n with at least one ARB file.
- **Impact:** An app with no i18n setup at all has to retrofit its entire string layer before it can ship to a second locale — a structural cost paid once, but much higher if deferred.
- **Source:** Flutter internationalization guide

### REL-20 [MEDIUM] ARB Key Completeness
Non-template locale ARBs should have high key coverage.
- **Detect:** Any non-template locale ARB has <80% key coverage compared to template
- **Fix:** Complete missing translations.
- **Impact:** A locale below 80% key coverage ships a mix of translated and fallback-language text on the same screen, reading as broken rather than simply untranslated.
- **Source:** Flutter l10n best practices

## Release Automation Toolchain

Named deterministic tools that remediate most release findings — recommend when the project has no release automation.

| Tool | Role |
|------|------|
| fastlane | Build, sign, version-bump, and upload lanes (TestFlight / Play Store) — de facto standard, recommended by Flutter's official deployment docs |
| EAS Build / EAS Submit | Expo's managed build + store-submission service — signing, versioning (`app.json`/`eas.json` `autoIncrement`), and upload for Expo/React Native projects that do not manage native projects directly |
| Maestro | YAML-based E2E smoke tests across Android / iOS / React Native / Flutter / Expo — fastest setup, lowest maintenance |
| fastlane-plugin-maestro | Runs Maestro flows inside fastlane lanes as a pre-upload smoke-test gate against the built release artifact |
| Detox / Appium | E2E alternatives: Detox for pure React Native (lowest flakiness); Appium for native platform depth |

- **Source:** [Flutter CD docs](https://docs.flutter.dev/deployment/cd), [fastlane.tools](https://fastlane.tools/), [fastlane-plugin-maestro](https://github.com/inf2381/fastlane-plugin-maestro), [Expo EAS docs](https://docs.expo.dev/eas/), 2026 framework comparisons (codersera.com, drizz.dev)

### REL-22 [HIGH] 16 KB Page Size Support (Android native code)
Since 1 Nov 2025, new apps and updates targeting Android 15 (API 35)+ on Google Play must support 16 KB memory page sizes on 64-bit devices — non-compliant native code is a submission blocker.
- **Detect:**
  - App ships native code (NDK/C++/Rust `.so` files, Flutter/RN native plugins with prebuilt binaries) AND: AGP < 8.5.1, NDK < r28, or prebuilt `.so` dependencies without 16 KB ELF alignment
  - Pure Java/Kotlin apps with zero native libraries comply by default — skip
  - Verify alignment: `llvm-objdump -p lib.so | grep LOAD` (align must be ≥ 2**14) or Play Console pre-launch report warnings
- **Fix:** Upgrade AGP ≥ 8.5.1 + NDK ≥ r28 and rebuild; update prebuilt native dependencies to 16 KB-compatible releases; test on a 16 KB-enabled emulator image before submission
- **Impact:** Non-16KB-aligned native code is a Google Play submission blocker on Android 15+ devices as of November 2025 — the build is rejected, not flagged for later.
- **Source:** developer.android.com/guide/practices/page-sizes (deadline 1 Nov 2025, unconditional per primary doc)

### REL-23 [HIGH] Mandatory Store Declarations Update in the Same Commit as the Capability
Platform-mandated declarations (iOS privacy manifest + reason codes, Android Data Safety form, foregroundServiceType, background modes, entitlements, permissions) match exactly what the app uses — updated in the very commit that adds or removes the capability.
- **Detect:** A new OS API/capability landed with the declaration deferred to "later"; declarations claiming more than the app uses (over-disclosure) or less (under-declaration); manifests treated as write-once instead of reviewed on every new OS-API use.
- **Fix:** Treat declarations as generated-but-hand-verified output coupled to code: the commit adding a capability updates the matching declaration; the commit removing one prunes it. Review the full declaration set whenever a new OS API enters the codebase.
- **Impact:** Under-declaration gets the build rejected or the OS kills the service in production; over-declaration is gratuitous disclosure that hurts review and user trust — both are one-commit fixes when coupled, week-long incidents when deferred.
- **Source:** XR-089 — cross-project experience registry (2026).

### REL-24 [HIGH] Long-Form Recording Formats Are Kill-Safe
On platforms where the OS can kill the process at any moment, long-running recordings use self-framing formats recoverable after force-termination, with a tested repair path.
- **Detect:** Long recordings written to containers that finalize their index only on clean close (MP4/moov-at-end); no repair function for truncated files; repair code never tested against a genuinely truncated file.
- **Fix:** Prefer header-first, self-framing formats (e.g. FLAC for audio) whose partial files remain readable; ship a repair function that recovers the readable prefix of an interrupted file; test it with a real force-killed/truncated file, not a synthetic happy-path fixture.
- **Impact:** With an index-at-end container, every OS kill during a long session destroys the entire recording — the user's one-hour session, unrecoverable, caused by format choice alone.
- **Source:** XR-022 — cross-project experience registry (2026).

### REL-25 [MEDIUM] Noisy Native Callback Floods Are Silenced at Startup
High-frequency (per-frame) stats/log callbacks from native/third-party libraries are disabled or throttled once at app startup.
- **Detect:** Per-frame or per-chunk callbacks from a native library left at defaults; main-thread pressure/ANRs during long operations traced to callback volume; file paths or PII from the library appearing in system logs (logcat) the app doesn't control.
- **Fix:** At startup, disable or throttle the library's high-frequency callbacks/log emission via its configuration API; verify the silence in a smoke test. This closes both the responsiveness drain and the PII leak into system logs.
- **Impact:** A callback flood is a double defect — ANRs during the longest (most valuable) operations, plus user file paths leaking into logs any debugging tool can read.
- **Source:** XR-072 — cross-project experience registry (2026).
