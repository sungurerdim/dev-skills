# Rules: Mobile — Security, Privacy & Store Compliance

## Security

### MSEC-01 [CRITICAL] Secure Data Storage
applies_when: always
PII, credentials, tokens must not be in plaintext storage.
- **Detect:**
  - Search: `**/SharedPreferences*.{java,kt}`, `**/UserDefaults*.swift`, `**/*.dart`
  - Check for: `SharedPreferences`, `UserDefaults`, `getSharedPreferences`, `NSUserDefaults`, plaintext SQLite with columns named `password`, `token`, `email`, `phone`, `ssn`
  - Proximity pattern: `SharedPreferences` or `UserDefaults` within 5 lines of `token`, `key`, `secret`, `password`, `credential`, `api_key` → CRITICAL (secrets in insecure storage)
  - Exclude: test files, mock files
- **Fix:** Replace with platform secure storage:
  - Flutter: `flutter_secure_storage`
  - iOS: `Keychain` (Secure Enclave backed)
  - Android: `EncryptedSharedPreferences` / `AndroidKeystore`
  - RN: `react-native-keychain`
- **Impact:** Plaintext-stored credentials or PII are readable by any process or attacker with device/filesystem access, including via a rooted device or backup extraction.
- **Source:** OWASP MASVS-STORAGE

### MSEC-07 [HIGH] Code Obfuscation
applies_when: always
Release builds must be obfuscated.
- **Detect:**
  - Flutter: missing `--obfuscate` in release build commands or CI scripts
  - Android: missing or empty `proguard-rules.pro`, R8 disabled
  - iOS: missing symbol stripping in release config
- **Fix:**
  - Flutter: `flutter build --obfuscate --split-debug-info=<dir>`
  - Android: enable R8, add `-keep class io.flutter.** { *; }` to proguard-rules.pro
  - iOS: strip debug symbols in release (bitcode is deprecated — removed in Xcode 14; never recommend enabling it)
  - RN: enable Hermes bytecode
- **Impact:** An unobfuscated release build hands a reverse engineer a near-source-quality map of the app's logic, secrets, and validation rules.
- **Source:** OWASP M7, MASVS-RESILIENCE

### MSEC-11 [HIGH] Backup Disabled (Android)
applies_when: platforms∋android
- **Detect:** `android:allowBackup` missing or `="true"` in AndroidManifest.xml
- **Fix:** Set `android:allowBackup="false"`
- **Impact:** With backup enabled, `adb backup` (or a cloud backup) can extract the app's private storage — including any data MSEC-01 was supposed to keep off the device's reach — without root.
- **Source:** MASVS-STORAGE

### MSEC-12 [HIGH] Device Attestation Currency (SafetyNet → Play Integrity)
applies_when: platforms∋android
SafetyNet Attestation API was fully shut down 31 Jan 2025 — calls now return errors; any code path depending on it is broken in production.
- **Detect:**
  - Search: `play-services-safetynet` in `build.gradle(.kts)`, `SafetyNetClient`, `SafetyNet.getClient`, `safetynet` imports
  - Firebase App Check configured with the SafetyNet provider
- **Fix:** Migrate to the Play Integrity API (`com.google.android.gms:play-services-integrity`); Firebase App Check → Play Integrity provider. Map verdicts (`MEETS_DEVICE_INTEGRITY` etc.) to the old attestation decisions; test the failure path — attestation outages must degrade gracefully, not lock users out
- **Impact:** A broken attestation call fails silently or throws in production, either locking out legitimate users or leaving the app with no working device-integrity signal at all.
- **Source:** developer.android.com/privacy-and-security/safetynet (deprecated → replaced by Play Integrity); Firebase App Check SafetyNet turndown

### MSEC-13 [HIGH] Entitlements Correctness (iOS)
applies_when: platforms∋ios
- **Detect:** `.entitlements` file declares a capability with no corresponding implementation (`com.apple.developer.applesignin` with no Sign in with Apple code path; push entitlement with no `UNUserNotificationCenter`/APNs registration; iCloud entitlement with no CloudKit/document usage; in-app-purchase entitlement with no StoreKit integration); or an implemented capability (Sign in with Apple, push, iCloud, IAP) with no matching entitlement declared.
- **Fix:** Reconcile `.entitlements` against actual code: remove unused capability declarations, add missing ones for implemented features. Verify in Xcode's Signing & Capabilities tab matches the entitlements file and the provisioning profile.
- **Impact:** A declared-but-unimplemented entitlement is dead attack surface and a provisioning-profile mismatch risk; an implemented-but-undeclared capability fails at runtime or is rejected at App Store review for missing capability configuration.
- **Source:** [Apple Developer — Entitlements](https://developer.apple.com/documentation/bundleresources/entitlements)

### MSEC-14 [HIGH] google-services.json Hygiene (Android)
applies_when: platforms∋android
- **Detect:** `google-services.json` committed with an unrestricted API key (no application/API restrictions set in Google Cloud Console); `package_name` in the file not matching the app's actual `applicationId`; a debug and release `google-services.json` mismatch (wrong Firebase project or SHA-1 fingerprint for the build variant in use).
- **Fix:** Restrict the API key in Google Cloud Console to the app's package name + SHA-1 (Android key restriction); verify `package_name` matches `applicationId` in `build.gradle`; confirm each build variant (debug/release) points to its correct Firebase project and has its SHA-1 fingerprint registered.
- **Impact:** An unrestricted API key extracted from the APK lets an attacker call the project's Firebase services (or a Google API billed to the developer) from outside the app; a package-name/fingerprint mismatch silently breaks Firebase Auth, push, or Dynamic Links for the affected build.
- **Source:** [Firebase — API keys for Firebase](https://firebase.google.com/docs/projects/api-keys)

## Privacy

### MPRV-02 [HIGH] OS Permission != Consent
applies_when: always
System permission prompts do not satisfy GDPR consent.
- **Detect:** Permission request (camera, contacts, location) without separate GDPR consent when data processing extends beyond immediate feature use
- **Fix:** Consent management alongside permission requests. Document purpose and legal basis
- **Impact:** Treating an OS permission grant as GDPR consent processes data without a valid legal basis, exposing the same fine exposure as collecting it with no consent step at all.
- **Source:** CNIL January 2025 ruling

## Store Compliance

### STO-01 [CRITICAL] Target API Level
applies_when: platforms∋ios or platforms∋android
Android: `targetSdkVersion` must meet current Play Store deadline. iOS: compile against latest Xcode SDK by Apple's deadline.
- **Detect:**
  - Android: `targetSdkVersion` or `targetSdk` in `build.gradle(.kts)` < `POLICY.android_new_target_sdk` (new apps) or `POLICY.android_update_target_sdk` (updates)
  - iOS: `IPHONEOS_DEPLOYMENT_TARGET` in `project.pbxproj` < `POLICY.min_ios_deployment`
  - Flutter: `compileSdk` in `android/app/build.gradle`, `platform :ios` in `Podfile`
  - React Native: `compileSdkVersion` in `android/build.gradle`, deployment target in Xcode project
- **Fix:** Update target/compile SDK. Run full test suite against new platform behaviors — Android 16 / API 36 (required for new apps and updates from Aug 31, 2026; extension available to Nov 1, 2026): predictive back enabled by default, edge-to-edge display without opt-out, orientation/aspect-ratio restrictions ignored on large screens, `USE_FULL_SCREEN_INTENT` requires explicit permission
- **Note:** See `references/scoring.md` Live Policy Fetch for current values
- **Impact:** Past the SDK deadline, the store's own submission tooling rejects the build outright — this is not a review judgment call, it is a hard mechanical block.
- **Source:** Google Play SDK requirements, Apple Xcode release notes

### STO-02 [HIGH] Age Rating
applies_when: platforms∋ios or platforms∋android
Content must match declared age rating. Apple uses updated questionnaire with 13+/16+/18+ tiers.
- **Detect:**
  - Missing age rating metadata in store configuration
  - Content–rating mismatch: search source for keywords (`violence`, `gambling`, `casino`, `alcohol`, `tobacco`, `drug`, `sexual`, `gore`, `weapon`, `horror`) and cross-reference with declared rating
  - Apple: verify questionnaire completed with new 13+/16+/18+ age tiers (effective Jan 31, 2026)
  - UGC-enabled apps without moderation → must declare higher rating
- **Fix:** Complete age rating questionnaire. Align content with declared rating. If UGC: implement moderation + report mechanism, declare accordingly
- **Impact:** A rating that undersells mature content triggers takedown and re-review on the next submission, and for UGC apps without moderation, can trigger a policy strike.
- **Source:** App Store 4.1, Play Store IARC

### STO-03 [CRITICAL] Privacy Labels (iOS)
applies_when: platforms∋ios
Every data type collected — directly or via SDKs — must be declared in App Store Connect privacy labels.
- **Detect:**
  - Map each SDK to data practices:

    | SDK Category | Data Types |
    |-------------|------------|
    | Analytics (Firebase, Amplitude) | Usage Data, Diagnostics, Device ID |
    | Crash Reporting (Crashlytics, Sentry) | Diagnostics, Device ID |
    | Ads (AdMob, Meta SDK) | Device ID, Advertising Data, Usage Data |
    | Auth (Firebase Auth, Sign in with Apple) | Email, Name, User ID |
    | Maps/Location SDKs | Precise/Coarse Location |
    | Push (FCM, OneSignal) | Device ID, Push Token |

  - Search for tracking domains: `*.doubleclick.net`, `*.facebook.com/tr`, `*.adjust.com`, `graph.facebook.com`
  - Compare declared labels in App Store Connect against actual SDK data flows
  - Missing "Data Used to Track You" when ATT or IDFA usage detected
- **Fix:** Audit all SDKs and first-party collection. Declare every data type and purpose in App Store Connect. Mark tracking data correctly
- **Impact:** Apple actively cross-references declared privacy labels against actual SDK network behavior; a mismatch is a documented, currently-enforced rejection reason, not a theoretical one.
- **Source:** App Store 5.1.2, November 2025 enforcement

### STO-04 [HIGH] Data Safety (Android)
applies_when: platforms∋android
Play Store Data Safety section must accurately reflect all data collection including SDKs.
- **Detect:**
  - SDK → data type mapping (same table as STO-03)
  - Encryption claim: verify TLS enforcement (cross-ref [security.md](security.md) SEC-04) — if `usesCleartextTraffic="true"`, encryption claim is false
  - Third-party sharing: SDKs that transmit data to external servers (ads, analytics) must be declared as shared
  - Data deletion: if [privacy.md](privacy.md) PRV-04 (Right to Erasure) not implemented, "data deletion" claim is inaccurate
- **Fix:** Complete Data Safety form. Map each SDK to data types. Verify encryption and deletion claims match implementation
- **Impact:** An inaccurate Data Safety form is a policy violation Google enforces post-launch as well as at review — including removal for apps found non-compliant after the fact.
- **Source:** Google Play Data Safety

### STO-05 [HIGH] Restore Purchases
applies_when: platforms∋ios or platforms∋android
Subscription and IAP restoration must be functional with platform-correct APIs.
- **Detect:**
  - No "Restore Purchases" button in subscription/paywall UI
  - Platform-specific API patterns:

    | Platform | Required API |
    |----------|-------------|
    | iOS/Flutter | `SKPaymentQueue.restoreCompletedTransactions()` or `StoreKit2 Transaction.currentEntitlements` |
    | Android/Flutter | `BillingClient.queryPurchasesAsync()` |
    | Flutter plugin | `InAppPurchase.restorePurchases()` or `RevenueCat.restorePurchases()` |
    | React Native | `RNIap.getAvailablePurchases()` or RevenueCat equivalent |

  - Missing subscription management UI (active plan, expiry date, renewal status)
  - No grace period handling — expired subscription shows error instead of grace state
- **Fix:** Add visible restore button on paywall. Implement platform restore API. Show subscription status UI. Handle grace period (billing retry) gracefully
- **Impact:** A user who cannot restore a purchase they already paid for has functionally lost that purchase, and both stores treat a missing restore path as a rejection reason.
- **Source:** App Store 3.1.1, Play Store subscription policy

### STO-06 [HIGH] AI Disclosure
applies_when: platforms∋ios or platforms∋android
Third-party AI services must be disclosed. On-device ML (Core ML, ML Kit on-device) exempt.
- **Detect:**
  - Cloud AI API usage: search for `openai`, `anthropic`, `gemini`, `claude`, `gpt`, `dall-e`, `whisper`, `stability.ai` in source and dependencies
  - Distinguish on-device vs cloud: `CoreML`, `MLKit` (on-device mode), `TFLite` → exempt. API calls to external AI endpoints → must disclose
  - AI-generated content without labeling (images, text generated by AI shown to users)
  - Model versioning: if AI model version affects output, version must be documented
- **Fix:** Disclose AI provider and purpose in privacy policy and app metadata. Label AI-generated content when shown to users. Document model versions in release notes when relevant
- **Impact:** Undisclosed use of a cloud AI provider is an active App Store enforcement target as of November 2025 — the app can be rejected or removed after the fact, not just at initial review.
- **Source:** App Store 5.1.2(i), November 2025

### STO-07 [HIGH] Age Verification API
applies_when: platforms∋ios or platforms∋android
Apps available to minors in US states with age verification laws must integrate platform APIs.
- **Detect:**
  - No age verification integration when app targets general audience in US
  - Platform API availability:

    | Platform | API |
    |----------|-----|
    | iOS 18+ | `AuthorizationProvider.requestAgeVerification()` (Declared Age Range) |
    | Android | Play Integrity Age Signals API |

  - State enforcement timeline: TX (Jan 2026), UT (May 2026), LA (Jul 2026), FL (Jan 2027)
  - Fallback: apps running on older OS versions need alternative age gate
- **Fix:** Integrate platform age verification APIs. Implement fallback age gate for older OS versions. Test with various age ranges
- **Impact:** Once a state's enforcement date passes, distributing without age verification in that jurisdiction is a direct legal-compliance failure, independent of app-store review.
- **Source:** US State Laws, Apple WWDC 2024, Google Play Policy

### STO-08 [HIGH] COPPA
applies_when: platforms∋ios or platforms∋android
Kids-directed apps have strict restrictions on data collection, ads, and third-party SDKs.
- **Detect:**
  - Kids Category (Apple) or Designed for Families (Google) app with:
    - Third-party analytics SDKs (Firebase Analytics, Amplitude, Mixpanel) not configured for COPPA
    - Advertising SDKs serving non-child-safe ads
    - Social features without parental gate
    - External links without parental gate
  - Missing parental consent flow for data collection
  - Analytics SDK exemptions: Firebase Analytics with `analytics_storage` denied, privacy-preserving analytics → allowed
- **Fix:** Remove or configure third-party SDKs for COPPA compliance. Add parental gates before external links and social features. Implement verifiable parental consent. Use only COPPA-compliant ad networks (if ads shown)
- **Impact:** COPPA violations carry direct FTC enforcement with fines that have run into the tens of millions for consumer apps, on top of certain store rejection for kids-category listings.
- **Source:** COPPA Rule 16 CFR 312, App Store Kids Category, Play Store Families Policy

### STO-09 [HIGH] Subscription Transparency
applies_when: platforms∋ios or platforms∋android
All auto-renewal terms, pricing, and trial conditions must be visible on purchase screen before user commits.
- **Detect:**
  - Paywall/purchase screen missing any of:
    - Subscription price and billing period (monthly/yearly)
    - Auto-renewal disclosure ("Subscription automatically renews unless cancelled")
    - Free trial duration and post-trial price
    - Introductory offer terms (if applicable)
  - Search UI files for paywall/purchase screens: `paywall`, `subscription`, `premium`, `upgrade`, `purchase`
  - Verify pricing text visible without scrolling on standard screen sizes
  - Terms of Service and Privacy Policy links missing from purchase screen
- **Fix:** Display all subscription terms on purchase screen: price, period, auto-renewal statement, trial length + post-trial price. Add ToS and Privacy Policy links. Ensure all text visible without scrolling
- **Impact:** Hiding auto-renewal or trial-to-paid pricing until after purchase is a common, well-documented rejection reason under both stores' subscription policies.
- **Source:** App Store 3.1.2, Play Store Subscriptions Policy, EU Consumer Rights Directive

### STO-10 [HIGH] Subscription Cancellation
applies_when: platforms∋ios or platforms∋android
Users must be able to manage and cancel subscriptions easily. Apple requires in-app cancellation mechanism.
- **Detect:**
  - iOS: no in-app subscription management or cancellation UI (required since StoreKit 2)
    - Search for: `showManageSubscriptions`, `ManageSubscriptionsSheet`, subscription settings screen
  - Android: no link to Play Store subscription management
    - Search for: `play.google.com/store/account/subscriptions`, deep link to subscription management
  - No grace period handling: app immediately locks content when billing fails instead of showing retry state
  - Missing subscription status indicators (active, expired, grace period, billing retry)
- **Fix:** iOS: implement `showManageSubscriptions` or `ManageSubscriptionsSheet`. Android: deep link to `https://play.google.com/store/account/subscriptions`. Show subscription status. Handle grace period (3-day iOS, variable Android) gracefully
- **Impact:** No in-app cancellation path is a specific, named Apple rejection reason (3.1.2(a)) since StoreKit 2 made it mandatory.
- **Source:** App Store 3.1.2(a), Play Store Subscription Policy

### STO-11 [CRITICAL] Sign in with Apple
applies_when: platforms∋ios
If app offers third-party social login, Sign in with Apple must be offered alongside (iOS only).
- **Detect:**
  - Search for third-party OAuth providers: `GoogleSignIn`, `google_sign_in`, `FacebookLogin`, `facebook_auth`, `TwitterLogin`, `GIDSignIn`, `ASAuthorizationAppleIDProvider`, `sign_in_with_apple`
  - Third-party OAuth found AND no `ASAuthorizationAppleIDProvider` or `sign_in_with_apple` → CRITICAL
  - Exemptions: educational institution apps (managed Apple IDs), enterprise internal apps, government apps, apps using only company's own first-party auth
  - Sign in with Apple button placement: must be equal or more prominent than other login options
- **Fix:** Add Sign in with Apple alongside existing OAuth providers. Use `ASAuthorizationAppleIDProvider` (native) or `sign_in_with_apple` (Flutter). Ensure button equally or more prominent than alternatives. Handle credential revocation
- **Impact:** Offering third-party social login without Sign in with Apple is Apple's own cited example of a Guideline 4.8 rejection — near-certain when detected, with no partial-credit review outcome.
- **Source:** App Store 4.8, Apple Human Interface Guidelines

### STO-12 [HIGH] App Completeness
applies_when: platforms∋ios or platforms∋android
App must be fully functional with no placeholder content, broken features, or incomplete sections.
- **Detect:**
  - Placeholder content patterns in UI strings and assets:
    - `lorem ipsum`, `placeholder`, `coming soon`, `under construction`, `TODO`, `FIXME` in user-visible strings
    - `dummy`, `sample`, `test data` in production data/assets
  - Non-functional UI elements: buttons with empty `onPressed`/`onTap`/`onClick` handlers
  - Search for: `onPressed: null`, `onTap: () {}`, `onPressed: () {}`, `// TODO`, `NotImplementedError`
  - Empty screens or sections (scaffold with no content)
  - Test/demo credentials visible in production builds
  - Saturated-category removal risk (Section 4.3(b), tightened June 8, 2026): app in a well-established category (dating, flashlight, wallpaper, timers, fortune-telling) with no recent updates or differentiation — Apple may remove existing apps not "updated, improved, or attracting customers", beyond the prior reject-on-submission stance
- **Fix:** Replace all placeholder content with real content. Implement or remove non-functional UI elements. Remove test data and demo credentials from production builds. Saturated category → document differentiation and maintain a regular update cadence before submitting
- **Impact:** Placeholder content or dead UI elements are a first-review rejection reason under both stores' completeness policies, and for saturated categories can trigger removal of an already-live app.
- **Source:** App Store 2.1 and 4.3(b) (June 2026 update), Play Store Spam and Minimum Functionality Policy

### STO-13 [HIGH] Metadata Accuracy
applies_when: platforms∋ios or platforms∋android
Store listing metadata must accurately reflect app functionality. No misleading claims.
- **Detect:**
  - Screenshots that don't reflect actual app UI (device mockups with fabricated screens)
  - Description claims features not present in codebase
  - Fake reviews or testimonials in description
  - Credentials or certifications claimed without verification
  - App name contains price indicators ("Free") that may become inaccurate
  - Search store metadata files: `fastlane/metadata`, `android/fastlane`, `ios/fastlane`, store listing drafts
- **Fix:** Ensure screenshots show real app UI. Align description with implemented features. Remove fake testimonials or unverifiable claims. Update metadata on each release
- **Impact:** Screenshots or descriptions that don't match the shipped app are a rejection reason and, if found post-launch, a listing takedown.
- **Source:** App Store 2.3, Play Store Metadata Policy

### STO-14 [HIGH] Permission Justification
applies_when: platforms∋ios or platforms∋android
Every requested permission must have clear use case. Unused or unjustified permissions cause rejection.
- **Detect:**
  - Declared permissions not used in code:
    - Android: compare `AndroidManifest.xml` `<uses-permission>` against actual API usage in source
    - iOS: compare `Info.plist` `NS*UsageDescription` keys against framework imports
  - Permission ↔ privacy label mismatch: permission declared but data type not in privacy labels (STO-03/STO-04)
  - Sensitive permissions without user-facing justification string:
    - Camera (`CAMERA`), Microphone (`RECORD_AUDIO`), Location (`ACCESS_FINE_LOCATION`), Contacts (`READ_CONTACTS`), Photos (`READ_MEDIA_IMAGES`)
  - Background location without foreground use case demonstrated first
- **Fix:** Remove unused permissions. Add `NS*UsageDescription` strings for all iOS permissions. Ensure each permission maps to declared data practice. Request sensitive permissions in context (when feature is used, not at launch)
- **Impact:** A permission with no matching usage-description string or declared purpose is flagged by both stores' automated review and blocks submission.
- **Source:** App Store 5.1.1, Play Store Permissions Policy

### STO-15 [CRITICAL] ATT Compliance (iOS)
applies_when: platforms∋ios
App Tracking Transparency prompt must appear before any tracking occurs. IDFA access requires ATT.
- **Detect:**
  - Tracking SDK initialization before ATT prompt:
    - Search for SDK init calls (`Firebase.initializeApp`, `Adjust.start`, `AppsFlyer.init`, `FBSDKApplicationDelegate`, `FacebookSdk.sdkInitialize`) and verify they occur after ATT response
    - Search for: `ATTrackingManager.requestTrackingAuthorization`, `app_tracking_transparency`
  - IDFA usage without ATT: `ASIdentifierManager.advertisingIdentifier` called without prior ATT check
  - Privacy label ↔ ATT inconsistency: "Data Used to Track You" declared but no ATT prompt, or ATT prompt present but tracking not declared
  - Pre-ATT prompt (custom explanation screen) missing — direct system prompt without context
- **Fix:** Show custom explanation screen before ATT prompt. Initialize tracking SDKs only after ATT authorization. Gate IDFA access behind ATT status check. Align privacy labels with ATT behavior
- **Impact:** Tracking before the ATT prompt, or a privacy-label/ATT mismatch, is one of Apple's most actively enforced rejection triggers — it is checked by tooling, not just a reviewer's judgment.
- **Source:** App Store 5.1.2(i), Apple ATT Framework

### STO-16 [HIGH] Push Notification Consent
applies_when: platforms∋ios or platforms∋android
Apps should explain notification value before triggering OS permission prompt.
- **Detect:**
  - OS notification permission requested at app launch without prior explanation
  - Search for notification permission request: `UNUserNotificationCenter.requestAuthorization`, `Notification.requestPermission`, `firebase_messaging` permission request
  - Permission request in `didFinishLaunchingWithOptions`, `application:didFinishLaunching`, `main()`, `initState()` (first screen)
  - No notification preference/settings screen for granular opt-in/out
- **Fix:** Add pre-permission screen explaining notification types and value. Defer OS prompt to contextual moment (after user action that benefits from notifications). Add notification preferences screen for category-level opt-in/out
- **Impact:** Requesting notification permission with no context collapses opt-in rates and burns the one-shot OS prompt — a denied prompt cannot be re-asked without a settings deep link.
- **Source:** Apple HIG Notifications, Play Store User Data Policy

### STO-17 [HIGH] Deep Linking
applies_when: platforms∋ios or platforms∋android
Universal Links (iOS) and App Links (Android) must be properly configured and validated.
- **Detect:**
  - iOS: missing or invalid `apple-app-site-association` (AASA) file configuration
    - Search for: `applinks:` in entitlements, `Associated Domains` capability
    - Verify AASA JSON structure: `applinks.details[].appIDs` contains correct team ID + bundle ID
  - Android: missing or invalid `assetlinks.json` configuration
    - Search for: `<intent-filter android:autoVerify="true">` in AndroidManifest.xml
    - Verify `assetlinks.json` references correct package name and SHA-256 fingerprint
  - Flutter: missing deep link handler registration (`go_router`, `auto_route`, `uni_links`)
  - No fallback for unhandled deep links (app crashes or shows blank screen)
- **Fix:** Configure AASA (iOS) and assetlinks.json (Android) with correct app identifiers. Register deep link handlers. Implement fallback for unmatched routes. Test with platform validation tools
- **Impact:** Unverified or misconfigured domain association makes Universal/App Links silently fall back to the browser, breaking every marketing link, email link, and cross-app handoff into the app.
- **Source:** Apple Universal Links, Android App Links, Play Store Deep Linking Policy

### STO-18 [MEDIUM] Store Listing Localization
applies_when: platforms∋ios or platforms∋android
Store metadata should be localized for all languages app supports.
- **Detect:**
  - App supports multiple locales (ARB files, `.lproj` directories, `values-xx/strings.xml`) but store metadata only in one language
  - Search for: `fastlane/metadata/*/`, locale-specific store listing directories
  - Compare app-supported locales against store listing locales
  - Screenshots not localized (same screenshots for all locales)
- **Fix:** Translate store metadata (title, subtitle, description, keywords, what's new) for each supported locale. Localize screenshots to show translated UI. Use Fastlane or store console for metadata management
- **Impact:** Store metadata left in one language undersells the app to every locale the app itself supports, directly hurting conversion in those markets.
- **Source:** App Store Localization, Play Store Translation Best Practices

### STO-19 [HIGH] Background Mode Justification (iOS)
applies_when: platforms∋ios
Every declared `UIBackgroundModes` capability must have real functional usage. Unused background modes cause rejection.
- **Detect:**
  - Search `Info.plist` for `UIBackgroundModes` array entries: `audio`, `location`, `voip`, `fetch`, `remote-notification`, `bluetooth-central`, `bluetooth-peripheral`, `external-accessory`, `processing`
  - Per declared mode, verify actual usage in source code:

    | Mode | Required Evidence |
    |------|------------------|
    | `audio` | `AVAudioSession`, audio playback/recording API usage |
    | `location` | `CLLocationManager` with `allowsBackgroundLocationUpdates` |
    | `voip` | PushKit or VoIP call handling |
    | `fetch` | `BGAppRefreshTask` or `performFetchWithCompletionHandler` |
    | `remote-notification` | Silent push handling with content-available |
    | `bluetooth-central` | `CBCentralManager` background scanning |

  - Declared mode with no matching API usage → HIGH (will be rejected)
- **Fix:** Remove unused `UIBackgroundModes` entries. Background capability needed → ensure corresponding API is implemented and functional
- **Impact:** A declared but unused background mode is a specific, checkable rejection reason — reviewers verify each declared capability has matching functionality.
- **Source:** App Store 2.5.4, Apple Background Execution Guide

### STO-20 [HIGH] Billing Library Version (Android)
applies_when: platforms∋android
Play Billing Library must meet minimum version requirement. Outdated versions are rejected.
- **Detect:**
  - Search `build.gradle(.kts)` for: `com.android.billingclient:billing`, `com.android.billingclient:billing-ktx`
  - Compare version against `POLICY.min_billing_lib` (see `references/scoring.md`)
  - Flutter: check `in_app_purchase_android` plugin version which bundles Billing Library
  - React Native: check `react-native-iap` version for bundled Billing Library version
  - Missing migration from deprecated APIs (e.g., `querySkuDetailsAsync` → `queryProductDetailsAsync`)
- **Fix:** Update Play Billing Library to >= `POLICY.min_billing_lib`. Migrate deprecated API calls. Test purchase flow end-to-end after upgrade
- **Impact:** An outdated Billing Library version is rejected at submission, and calls to APIs Google has since removed (like the old SKU-details call) crash the purchase flow outright.
- **Source:** Play Billing Library Release Notes, Play Store Billing Policy

### STO-21 [HIGH] IAP Purchase Experience Quality
applies_when: platforms∋ios or platforms∋android
Every in-app purchase flow must provide clear product info, loading state, success confirmation, and specific error guidance.
- **Detect:**
  - Purchase buttons without clear product description (icon-only or vague label without explaining what user gets)
  - No loading/processing state during purchase transaction
  - No visual confirmation after successful purchase (no animation, badge, or success message)
  - Generic error messages on IAP failure ("Something went wrong" instead of specific guidance)
  - Platform purchase states not fully handled:
    - iOS: `SKPaymentTransactionObserver` missing handlers for purchasing/purchased/failed/restored/deferred
    - Android: `BillingResult` response codes not mapped to user-friendly messages
    - Flutter: `PurchaseDetails.status` enum not exhaustively handled
    - RN: `react-native-iap` error codes not mapped to user messages
- **Fix:** Each IAP product: clear description of what user receives (quantity, duration, features). Purchase flow: loading state ("Processing purchase...") → success confirmation (visual feedback + updated balance/status) OR specific error message + retry guidance. Handle all platform transaction states exhaustively. Deferred state (Ask to Buy) must show appropriate pending message
- **Impact:** A purchase flow with no loading state or specific error guidance leaves users unsure whether a charge went through, driving support tickets, chargebacks, and refund requests.
- **Source:** Apple HIG Purchasing, Google Play Billing UX Guidelines, Amazon IAP Design Guidelines

### STO-22 [HIGH] Foreground Service Type Declarations (Android 14+)
applies_when: platforms∋android
Apps targeting API 34+ must declare a foreground service type per service — startForeground() without one throws `MissingForegroundServiceTypeException`; Play Console requires type declarations on the app-content page.
- **Detect:**
  - `<service>` entries in AndroidManifest.xml with `android:foregroundServiceType` missing while the app calls `startForeground()`
  - `dataSync`-type services with no handling for the Android 15 six-hour runtime cap (`onTimeout` unimplemented); `shortService` used for work exceeding 3 minutes
  - Foreground services launched from a `BOOT_COMPLETED` receiver for restricted types (mediaPlayback, camera, phoneCall, dataSync — restricted since Android 15)
  - Play Console foreground-service declaration missing for declared types
- **Fix:** Declare the correct `foregroundServiceType` per service + the matching permission (`FOREGROUND_SERVICE_<TYPE>`); implement `onTimeout` for capped types and migrate long `dataSync` work to WorkManager/user-initiated data transfer; complete the Play Console declaration. Android 16 additionally enforces background job quotas on jobs launched from foreground services — verify WorkManager jobs survive
- **Impact:** On API 34+, starting a foreground service without a declared type throws `MissingForegroundServiceTypeException` at runtime — a crash, not a review comment.
- **Source:** developer.android.com/develop/background-work/services/fgs/changes; Play Console foreground-service requirements
