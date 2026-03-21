# Rules: Release Readiness & Store Submission

Rules for release-ready mode. Each rule: ID, severity, title, detect pattern, fix action.

## Build Configuration

### REL-01 [CRITICAL] Android SDK Version Compliance
Consolidated into **STO-01** (rules-compliance.md) for single source of truth.
- **Detect:** See STO-01 for target SDK detection patterns and POLICY values
- **Fix:** See STO-01
- **Source:** Google Play Developer Policy

### REL-02 [CRITICAL] Release Signing Configuration
Release builds must use release signing, not debug.
- **Detect:** `signingConfig = signingConfigs.debug` in release block, or no release signing config defined
- **Fix:** Configure release signing with keystore. Store credentials in CI secrets, not source code.
- **Source:** Android App Bundle requirements

### REL-03 [HIGH] iOS Deployment Target Compliance
Consolidated into **STO-01** (rules-compliance.md) for single source of truth.
- **Detect:** See STO-01 for deployment target detection patterns and POLICY values
- **Fix:** See STO-01
- **Source:** Apple Developer requirements

### REL-04 [HIGH] Version Format
pubspec version must follow semver+build format (X.Y.Z+N).
- **Detect:** Version in pubspec.yaml not matching `^\d+\.\d+\.\d+\+\d+$`
- **Fix:** Set version to proper semver+build format.
- **Source:** Flutter versioning guide

### REL-05 [HIGH] ProGuard/R8 Configuration
Release builds need proper ProGuard rules to prevent runtime crashes.
- **Detect:** Missing or empty proguard-rules.pro when R8 is enabled
- **Fix:** Add Flutter-critical keep rules. Test release build thoroughly.
- **Source:** Flutter Android deployment guide

### REL-06 [HIGH] Release Build Flags
Release builds must include obfuscation and debug info splitting.
- **Detect:** Build scripts missing `--obfuscate` and `--split-debug-info`
- **Fix:** Add both flags to release build commands.
- **Source:** Flutter deployment best practices

### REL-07 [MEDIUM] Android Minification
Release builds should enable code and resource shrinking.
- **Detect:** `minifyEnabled` or `shrinkResources` set to false in release buildType
- **Fix:** Enable both minifyEnabled and shrinkResources.
- **Source:** Android developer guide

### REL-08 [HIGH] AAB and 64-bit Support
Play Store requires AAB format and arm64-v8a support.
- **Detect:** abiFilters excluding arm64-v8a, or build scripts using `build apk` instead of `appbundle`
- **Fix:** Remove restrictive abiFilters. Use `flutter build appbundle`.
- **Source:** Google Play 64-bit requirement

## Privacy & Compliance

### REL-09 [CRITICAL] Privacy Policy URL Verification
Privacy policy must be a live, accessible URL with valid content.
- **Detect:** No privacy policy URL found in project files, or URL returns error/placeholder content
- **Fix:** Publish privacy policy. Add URL to store listings and in-app settings.
- **Source:** App Store / Play Store requirement

### REL-10 [HIGH] iOS Privacy Manifest
PrivacyInfo.xcprivacy required for App Store submission.
- **Detect:** Missing ios/PrivacyInfo.xcprivacy or missing NSPrivacyAccessedAPITypes
- **Fix:** Create privacy manifest with required API type declarations.
- **Source:** Apple privacy manifest requirement (May 2024+)

### REL-11 [HIGH] NSUsageDescription Keys
All used permissions must have usage description strings.
- **Detect:** Plugins requiring permissions but missing corresponding NS*UsageDescription in Info.plist
- **Fix:** Add descriptive, user-facing usage descriptions for each permission.
- **Source:** Apple Human Interface Guidelines

### REL-12 [HIGH] Account Deletion Support
Apps with authentication must offer account deletion.
- **Detect:** Auth plugins present but no deleteUser/deleteAccount implementation
- **Fix:** Implement account deletion flow accessible from account settings.
- **Source:** App Store 5.1.1, Play Store Account Deletion Policy

### REL-13 [HIGH] Consent Mechanism
Tracking/analytics must not initialize before user consent.
- **Detect:** Analytics/tracking SDK init before consent dialog, or tracking SDKs without consent package
- **Fix:** Block all non-essential tracking until consent obtained. Ensure correct init order.
- **Source:** GDPR, App Store 5.1.2

## Dependencies & Quality

### REL-14 [CRITICAL] Known Vulnerabilities
No known CVEs in production dependencies.
- **Detect:** `dart pub audit` reports HIGH/CRITICAL advisories
- **Fix:** Update affected packages to patched versions.
- **Source:** OWASP M2

### REL-15 [HIGH] SDK Constraint Currency
Dart/Flutter SDK constraint should target current stable.
- **Detect:** SDK constraint targeting EOL version (Dart 2.x)
- **Fix:** Update SDK constraint to current stable range.
- **Source:** Dart versioning policy

### REL-16 [HIGH] Outdated Major Dependencies
Dependencies should not be more than 1 major version behind.
- **Detect:** `flutter pub outdated` shows 2+ packages with major version gap
- **Fix:** Plan and test major version upgrades.
- **Source:** Dependency management best practices

### REL-17 [MEDIUM] Static Analysis Clean
Release builds should pass flutter analyze without errors.
- **Detect:** `flutter analyze` reports errors or excessive warnings
- **Fix:** Resolve all errors and reduce warnings.
- **Source:** Flutter quality guidelines

### REL-18 [HIGH] Crash Reporting
Production apps must have crash reporting configured and initialized.
- **Detect:** No crash reporting package (Crashlytics, Sentry, etc.) or package present but not initialized
- **Fix:** Add and properly initialize crash reporting SDK.
- **Source:** Industry standard

## Localization

### REL-19 [HIGH] i18n Setup
Apps should have internationalization configured.
- **Detect:** No lib/l10n/ directory, no .arb files, no localizationsDelegates
- **Fix:** Set up Flutter l10n with at least one ARB file.
- **Source:** Flutter internationalization guide

### REL-20 [MEDIUM] ARB Key Completeness
Non-template locale ARBs should have high key coverage.
- **Detect:** Any non-template locale ARB has <80% key coverage compared to template
- **Fix:** Complete missing translations.
- **Source:** Flutter l10n best practices

### REL-21 [MEDIUM] Hardcoded UI Strings
User-visible text should use l10n, not hardcoded strings.
- **Detect:** `Text('...')` with natural language strings in lib/ (excluding generated/l10n/test)
- **Fix:** Extract strings to ARB files.
- **Source:** Flutter internationalization guide
