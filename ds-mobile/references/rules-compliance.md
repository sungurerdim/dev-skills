# Rules: Security, Privacy & Store Compliance

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect (search+check patterns), fix (concrete action), platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Security** | SEC-01–11 (4 CRITICAL, 7 CRITICAL, 1 HIGH) | ~12 |
| **Privacy** | PRV-01–05 (2 CRITICAL, 2 CRITICAL) | ~111 |
| **Regulatory Compliance** | PRV-06–18 (8 CRITICAL, 5 CRITICAL) | ~152 |
| **Store Compliance** | STO-01–20 (12 CRITICAL, 7 HIGH, 1 MEDIUM) | ~340 |

---

## Security

### SEC-01 [CRITICAL] Secure Data Storage
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
- **Source:** OWASP MASVS-STORAGE

### SEC-02 [CRITICAL] No Hardcoded Credentials
Zero secrets in source code.
- **Detect:**
  - Search for: `**/.env`, `**/credentials*`, `**/secrets*` committed to git
  - Check with specific patterns (skip lines containing `// noqa`, `// safe:`, `// example`, `// test`, `// mock`):

  | ID | Pattern | Label |
  |----|---------|-------|
  | S01 | `AIza[0-9A-Za-z\-_]{35}` | Firebase/Google API key |
  | S02 | `AKIA[0-9A-Z]{16}` | AWS Access Key ID |
  | S03 | `sk_live_[A-Za-z0-9]{20,}` | Stripe live secret key |
  | S04 | `pk_live_[A-Za-z0-9]{20,}` | Stripe live publishable key |
  | S05 | `-----BEGIN (RSA\|EC\|OPENSSH) PRIVATE KEY-----` | PEM private key |
  | S06 | `(api[_-]?key\|apiKey\|API_KEY)\s*[:=]\s*["'][A-Za-z0-9\-_]{20,}["']` | Generic API key assignment |
  | S07 | `client_secret\s*[:=]\s*["'][A-Za-z0-9\-_]{20,}["']` | OAuth client secret |
  | S08 | `(password\|passwd)\s*[:=]\s*["'][^"']{8,}["']` | Hardcoded password |
  | S09 | `https://[a-z0-9-]+\.firebaseio\.com` | Firebase Realtime DB URL |
  | S10 | `sk-[a-zA-Z0-9]{20,}` | OpenAI / generic secret key |
  | S11 | `bearer\s+[A-Za-z0-9\-_.]{20,}` | Hardcoded bearer token |
  | S12 | Base64 patterns >40 chars in string literals | Encoded secrets |

  - Exclude: `.env.example`, test fixtures with dummy values
  - Per match: record file + line + first 6 chars of value + `***`. Never print full secret.
- **Fix:** Move to environment variables or platform keychain. Add to `.gitignore`. Use server-side proxy for API keys
- **Source:** OWASP M1

### SEC-03 [CRITICAL] Debug Mode Off in Release
- **Detect:**
  - Android: `android:debuggable="true"` in AndroidManifest.xml
  - iOS: check build configuration for DEBUG symbols in release
  - Flutter: `kDebugMode` used in release-visible code paths
- **Fix:** Android: ensure `android:debuggable` absent or false in release manifest. iOS: strip debug info. Flutter: guard with `kDebugMode` or `assert`
- **Source:** OWASP M8

### SEC-04 [CRITICAL] TLS Enforced, No HTTP
- **Detect:**
  - Android: `android:usesCleartextTraffic="true"` in AndroidManifest.xml, or missing `network_security_config.xml`
  - iOS: `NSAllowsArbitraryLoads` = YES in Info.plist
  - Search for: `http://` URLs in source (excluding localhost/10.0/192.168)
- **Fix:** Android: `network_security_config.xml` with `cleartextTrafficPermitted="false"`. iOS: remove ATS exceptions. Replace http:// with https://
- **Source:** OWASP M5

### SEC-05 [CRITICAL] Certificate Pinning (Selective)
Pin public keys for high-risk endpoints (auth, payment). Not recommended for all endpoints.
- **Detect:** No pinning config for endpoints handling credentials or payment
- **Fix:**
  - Android: `network_security_config.xml` with `<pin-set>` including 2+ pins
  - iOS: TrustKit or Info.plist ATS pinning
  - Plan rotation: pre-generate backup key, 3-6 month rollout window
- **Note:** OWASP recommends against blanket pinning. Pin selectively with backup pins
- **Source:** OWASP Pinning Cheat Sheet

### SEC-06 [CRITICAL] Strong Cryptography
AES-256-GCM symmetric. No MD5/SHA-1 for security. Platform crypto APIs only.
- **Detect:**
  - Search for: `MD5`, `SHA1`, `SHA-1` in non-checksum context, `ECB` mode, `DES`, `RC4`, hardcoded IV/nonce
  - Custom crypto implementations (non-platform)
- **Fix:** Use platform APIs: iOS CryptoKit, Android javax.crypto, Dart pointycastle. AES-256-GCM with random IV
- **Source:** OWASP M10, MASVS-CRYPTO

### SEC-07 [CRITICAL] Code Obfuscation
Release builds must be obfuscated.
- **Detect:**
  - Flutter: missing `--obfuscate` in release build commands or CI scripts
  - Android: missing or empty `proguard-rules.pro`, R8 disabled
  - iOS: missing bitcode/symbol stripping in release config
- **Fix:**
  - Flutter: `flutter build --obfuscate --split-debug-info=<dir>`
  - Android: enable R8, add `-keep class io.flutter.** { *; }` to proguard-rules.pro
  - iOS: enable bitcode, strip debug symbols in release
  - RN: enable Hermes bytecode
- **Source:** OWASP M7, MASVS-RESILIENCE

### SEC-08 [CRITICAL] Supply Chain Security
Dependencies audited, versions pinned, lockfile committed.
- **Detect:**
  - Unpinned versions: `^`, `~`, `latest`, `>=` without upper bound in pubspec.yaml/package.json/build.gradle
  - Missing lockfile (pubspec.lock, package-lock.json, yarn.lock) in git
- **Fix:** Pin exact versions. Commit lockfiles
- **Source:** OWASP M2

### SEC-09 [CRITICAL] Server-Side Auth
Auth and authorization validated server-side. Client-side checks are UX convenience only.
- **Detect:** Auth state determined solely by local token existence without server validation. No token expiry check
- **Fix:** Validate every API request server-side. Short-lived access tokens + refresh token rotation
- **Source:** OWASP M3

### SEC-10 [CRITICAL] OAuth 2.1 + PKCE
Authorization Code + PKCE for mobile. No implicit grant.
- **Detect:**
  - Search for: `response_type=token` (implicit grant), missing `code_verifier`, missing `code_challenge`
  - Long-lived tokens without rotation mechanism
- **Fix:** PKCE flow: random code_verifier per request, S256 code_challenge_method, app-specific redirect URIs
- **Source:** RFC 9700

### SEC-11 [HIGH] Backup Disabled (Android)
- **Detect:** `android:allowBackup` missing or `="true"` in AndroidManifest.xml
- **Fix:** Set `android:allowBackup="false"`
- **Source:** MASVS-STORAGE

---

## Privacy

### PRV-01 [CRITICAL] Runtime Consent UI
Equal-weight Accept/Reject. Purpose-level granularity. Data deletion mechanism.
- **Detect:**
  - No consent dialog/screen in app (search for consent/gdpr/privacy in codebase)
  - Accept button larger or more prominent than Reject
  - No account/data deletion flow
- **Fix:** In-app consent with equal-sized buttons. Per-purpose toggles. Account deletion endpoint and UI
- **Note:** For KVKK-specific consent requirements (acik riza, VERBIS), see PRV-11
- **Source:** GDPR Art. 7, CNIL 2025

### PRV-02 [CRITICAL] OS Permission != Consent
System permission prompts do not satisfy GDPR consent.
- **Detect:** Permission request (camera, contacts, location) without separate GDPR consent when data processing extends beyond immediate feature use
- **Fix:** Consent management alongside permission requests. Document purpose and legal basis
- **Source:** CNIL January 2025 ruling

### PRV-03 [CRITICAL] Privacy Policy
URL in store listing + accessible in-app. AI service usage disclosed.
- **Detect:**
  - No privacy policy link in app (search settings/about screen)
  - Third-party AI services (OpenAI, Anthropic, Google AI) used without disclosure
- **Fix:** Add privacy policy to in-app settings. Disclose AI providers and data processing purposes
- **Source:** App Store, Play Store requirements

### PRV-04 [CRITICAL] Data Minimization
Collect only necessary data. No fingerprinting.
- **Detect:**
  - Permissions requested beyond feature requirements
  - Device fingerprinting libraries (adjust, appsflyer device fingerprint, custom device ID collection)
  - IMEI, MAC address, or hardware identifier collection for tracking
- **Fix:** Remove unnecessary permissions. Replace device fingerprinting with privacy-preserving identifiers
- **Source:** MASVS-PRIVACY, GDPR Art. 25, Apple ATT

### PRV-05 [CRITICAL] Right to Erasure
Complete data deletion including backend and backups.
- **Detect:** No data deletion UI/endpoint. Deletion removes app access but retains backend data
- **Fix:** Implement complete erasure: databases, backups, third-party services. Provide deletion UI in account settings
- **Source:** GDPR Art. 17, EDPB 2025 enforcement

---

## Regulatory Compliance (Framework-Tagged)

Rules in this section are only checked when the corresponding framework is in `ACTIVE_FRAMEWORKS`. Tag format: `[FRAMEWORK: X,Y]` means check only if X or Y is active.

**Common detect strategy for PRV-06–13:** Each framework rule checks for absence of framework-specific compliance artifacts. Pattern: (1) Search compliance/privacy files for framework keywords, (2) verify consent mechanism meets framework requirements, (3) check cross-border transfer safeguards if applicable. Specific keywords per rule below.

### PRV-06 [CRITICAL] CCPA/CPRA Compliance [FRAMEWORK: CCPA]
California Consumer Privacy Act + California Privacy Rights Act.
Applies when: annual revenue > $28.8M, OR process data of 100K+ consumers, OR 50%+ revenue from selling/sharing personal information.
- **Detect:**
  - No "Do Not Sell or Share My Personal Information" link in app settings
  - No opt-out mechanism for data sale/sharing
  - No 12-month data collection disclosure
  - Search for: absence of `doNotSell`, `optOut`, `ccpa`, `cpra` in settings/privacy screens
  - Financial incentive programs without opt-in consent
- **Fix:** Add "Do Not Sell/Share" toggle in settings. Implement opt-out API. Disclose data categories collected in past 12 months. Honor Global Privacy Control (GPC) signal. Respond to consumer requests within 45 days
- **Note:** CPRA added right to correct inaccurate data, right to limit use of sensitive PI, and California Privacy Protection Agency (CPPA) enforcement
- **Source:** CCPA 1798.120, CPRA 2023 amendments

### PRV-07 [CRITICAL] LGPD Compliance [FRAMEWORK: LGPD]
Brazil Lei Geral de Protecao de Dados.
- **Detect:**
  - No legal basis declaration for each data processing activity
  - No DPO (Encarregado) contact in privacy policy
  - Cross-border data transfer without adequate safeguards
  - No consent granularity (all-or-nothing)
  - Search for: absence of `lgpd`, `encarregado`, `anpd` in privacy-related files
- **Fix:** Declare legal basis per processing activity (10 legal bases available). Appoint and disclose DPO. Implement consent with per-purpose granularity. Add cross-border transfer safeguards (Standard Contractual Clauses or adequacy). Support data portability in structured format
- **Note:** ANPD can impose fines up to 2% of revenue in Brazil (capped at R$50M per infraction)
- **Source:** LGPD Lei 13.709/2018, ANPD regulations

### PRV-08 [CRITICAL] PIPL Compliance [FRAMEWORK: PIPL]
China Personal Information Protection Law.
- **Detect:**
  - No separate consent per processing purpose
  - Data stored outside China without Security Impact Assessment (SCIA) or Standard Contract
  - No local data storage for Chinese users
  - Sensitive personal information processed without explicit separate consent
  - Search for: absence of `pipl`, `scia`, `cross_border_assessment` in compliance files
- **Fix:** Obtain separate consent for each processing purpose. Store data in China or complete SCIA for cross-border transfer (>1M individuals: mandatory security assessment by CAC). Explicit consent for sensitive data (biometrics, financial, health, minors). Appoint local representative if processing from outside China
- **Note:** Penalties up to 5% of annual revenue or CNY 50M. App can be ordered removed from stores
- **Source:** PIPL 2021, CAC cross-border data flow regulations 2024

### PRV-09 [CRITICAL] UK GDPR Compliance [FRAMEWORK: UK_GDPR]
UK General Data Protection Regulation (post-Brexit).
- **Detect:**
  - No ICO registration for data processing activities
  - No UK representative designated (if processing UK data from outside UK)
  - Age-Appropriate Design Code (AADC) not implemented for services accessed by children
  - Search for: absence of `uk_gdpr`, `aadc`, `ico_registration` in compliance/privacy files (do not search bare `ico` — matches favicon.ico/icons)
- **Fix:** Register with ICO. Designate UK representative if not established in UK. Implement AADC for child-accessible services: default high privacy, age estimation, no nudge techniques, no profiling by default. Data Protection Fee paid to ICO
- **Note:** ICO can issue fines up to GBP 17.5M or 4% of global turnover. AADC is mandatory for all online services likely accessed by children under 18
- **Source:** UK GDPR 2018, Data Protection Act 2018, ICO Age-Appropriate Design Code

### PRV-10 [CRITICAL] ePrivacy Compliance [FRAMEWORK: EPRIVACY]
EU ePrivacy Directive (Cookie Law) + upcoming ePrivacy Regulation.
- **Detect:**
  - Tracking cookies/SDKs loaded before user consent
  - No cookie/tracking consent banner or in-app consent mechanism
  - Essential cookies not properly categorized (exempt from consent)
  - Check for: tracking SDK init (`Firebase.initializeApp`, `Adjust.start`, `AppsFlyer.init`, analytics init) before consent check
- **Fix:** Block all non-essential tracking until consent obtained. Categorize: strictly necessary (exempt), analytics, marketing, personalization. Provide granular opt-in. Re-consent annually or on purpose change. Essential-only cookies do not require consent
- **Note:** ePrivacy Regulation (replacing Directive) expected to align with GDPR. Current Directive implemented differently per EU member state
- **Source:** ePrivacy Directive 2002/58/EC, CNIL/DPA guidance

### PRV-11 [CRITICAL] KVKK Compliance [FRAMEWORK: KVKK]
Turkey Kisisel Verilerin Korunmasi Kanunu.
- **Detect:**
  - No VERBIS (Veri Sorumlulari Sicil Bilgi Sistemi) registration reference
  - No explicit consent for data processing (acik riza)
  - Data transfer abroad without KVKK Board approval or adequate country determination
  - No data controller (veri sorumlusu) obligations documented
  - Search for: absence of `kvkk`, `verbis`, `acik_riza`, `veri_sorumlusu` in compliance files
- **Fix:** Register with VERBIS. Obtain explicit consent (acik riza) with clear purpose statement. Cross-border transfer only to adequate countries or with Board approval + binding commitments. Implement data subject rights: access, correction, deletion, objection. Retain processing records
- **Note:** KVKK Board can impose fines from TRY 50K to TRY 6M. KVKK closely mirrors GDPR but has distinct consent and cross-border transfer requirements
- **Source:** KVKK 6698, KVKK Board decisions

### PRV-12 [CRITICAL] PIPA Compliance [FRAMEWORK: PIPA]
South Korea Personal Information Protection Act.
- **Detect:**
  - No separate consent per data collection purpose
  - Consent not obtained before collection
  - No notification of data processing to data subjects
  - Third-party data sharing without separate consent
  - Search for: absence of `pipa`, `pipc` in compliance files
- **Fix:** Obtain separate opt-in consent per purpose before collection. Notify: purpose, items collected, retention period, right to refuse. Separate consent for third-party sharing. Mandatory privacy impact assessment for large-scale processing. Appoint CPO (Chief Privacy Officer)
- **Note:** PIPC enforcement. Fines up to 3% of related revenue. Criminal penalties possible
- **Source:** PIPA 2011 (amended 2023), PIPC guidelines

### PRV-13 [CRITICAL] PDPA Compliance [FRAMEWORK: PDPA]
Thailand/Singapore Personal Data Protection Act.
- **Detect:**
  - No consent mechanism for data collection
  - No DPO appointed (mandatory for certain processing)
  - Cross-border transfer without adequate safeguards
  - No data breach notification mechanism
  - Search for: absence of `pdpa`, `pdpc` in compliance files
- **Fix:** Obtain consent before collection and use. Appoint DPO if required. Cross-border transfer only with adequate protection (consent, contractual, binding corporate rules). Notify PDPC of breaches within 72 hours (Singapore) / without delay (Thailand). Implement access, correction, deletion, portability rights
- **Note:** Thailand PDPA: fines up to THB 5M + criminal penalties. Singapore PDPA: fines up to SGD 1M or 10% of annual turnover
- **Source:** Thailand PDPA 2019, Singapore PDPA 2012 (amended 2021)

### PRV-14 [CRITICAL] Data Processing Agreement [FRAMEWORK: GDPR,UK_GDPR,LGPD,KVKK]
Written agreement with all data processors covering scope, purpose, security measures, sub-processor controls.
- **Detect:**
  - Third-party SDKs processing personal data without documented DPA
  - Check for: third-party SDK usage (analytics, crash reporting, advertising SDKs) without corresponding DPA reference in compliance docs
  - No processor list maintained
- **Fix:** Execute DPA (Art. 28 GDPR) with every processor. Document: processing scope, security measures, sub-processor approval, data return/deletion on termination. Maintain processor registry. Review annually
- **Source:** GDPR Art. 28, UK GDPR Art. 28, LGPD Art. 39, KVKK Art. 12

### PRV-15 [CRITICAL] Data Protection Impact Assessment [FRAMEWORK: GDPR,UK_GDPR,LGPD,PIPL]
DPIA required for high-risk processing: large-scale profiling, systematic monitoring, sensitive data, new technologies.
- **Detect:**
  - Large-scale processing of sensitive data (health, biometrics, location tracking) without documented DPIA
  - Systematic monitoring of public areas
  - Automated decision-making with legal effects
  - Check for: `LocationManager`, `CLLocationManager`, `BiometricPrompt`, `HealthKit`, `health_connect` in source code — verify DPIA documentation exists when these APIs are used
- **Fix:** Conduct DPIA: describe processing, assess necessity/proportionality, identify risks, define mitigations. Consult DPA if high residual risk. Document and review annually. PIPL requires separate PIA for cross-border transfers. LGPD: RIPD (Relatorio de Impacto) for high-risk processing
- **Source:** GDPR Art. 35, UK GDPR Art. 35, LGPD Art. 38, PIPL Art. 55

### PRV-16 [CRITICAL] Breach Notification [FRAMEWORK: GDPR,CCPA,LGPD,PIPL,UK_GDPR,KVKK,PIPA,PDPA]
Timely notification to authority and affected individuals upon data breach.
- **Detect:**
  - No breach notification procedure documented
  - No incident response plan in app/backend documentation
  - No breach detection mechanism
- **Fix:** Implement breach detection and response plan. Notification timelines:

  | Framework | Authority | Individuals | Notes |
  |-----------|-----------|-------------|-------|
  | GDPR | 72 hours | Without undue delay (high risk) | Supervisory authority |
  | UK_GDPR | 72 hours | Without undue delay (high risk) | ICO |
  | CCPA | AG if 500+ CA residents | Without unreasonable delay | Attorney General |
  | LGPD | Reasonable timeframe | Reasonable timeframe | ANPD |
  | PIPL | Immediately | Immediately | CAC/authority |
  | KVKK | As soon as possible | As soon as possible | KVKK Board |
  | PIPA | 72 hours | 72 hours | PIPC |
  | PDPA (SG) | 72 hours | As warranted | PDPC |
  | PDPA (TH) | Without delay | Without delay | PDPC |

- **Source:** GDPR Art. 33-34, CCPA 1798.150, LGPD Art. 48, PIPL Art. 57, KVKK Art. 12

### PRV-17 [CRITICAL] Data Portability [FRAMEWORK: GDPR,CCPA,UK_GDPR,LGPD,PIPA]
Users can export their data in machine-readable format.
- **Detect:**
  - No data export feature in app
  - No API endpoint for data export
  - Search for: absence of `data_export`, `download_my_data`, `portability`, `exportUserData` in settings/account screens (do not search bare `export`/`download` — matches JS module exports and generic download handlers)
- **Fix:** Implement data export in structured, machine-readable format (JSON, CSV). Cover all user-provided data. Provide in-app "Download My Data" button. GDPR: direct transfer to another controller when technically feasible. Response within 30 days (GDPR/UK) or 45 days (CCPA)
- **Source:** GDPR Art. 20, CCPA 1798.100, UK GDPR Art. 20, LGPD Art. 18

### PRV-18 [CRITICAL] Consent Withdrawal [FRAMEWORK: GDPR,UK_GDPR,LGPD,PIPL,KVKK,PIPA,PDPA]
Withdrawing consent must be as easy as giving it. Processing stops upon withdrawal.
- **Detect:**
  - No consent withdrawal mechanism in app settings
  - Withdrawal process harder than consent (e.g., requires email/call to withdraw but tap to consent)
  - Processing continues after withdrawal
  - Check for: consent collection without matching withdrawal UI
- **Fix:** Add consent management screen in settings. Toggle per processing purpose. Withdrawal = one tap (same as consent). Stop processing immediately upon withdrawal. Inform user that withdrawal doesn't affect lawfulness of prior processing. Log withdrawal timestamp
- **Source:** GDPR Art. 7(3), UK GDPR Art. 7(3), LGPD Art. 8, PIPL Art. 15, KVKK Art. 7

---

## Store Compliance

### STO-01 [CRITICAL] Target API Level
Android: `targetSdkVersion` must meet current Play Store deadline. iOS: compile against latest Xcode SDK by Apple's deadline.
- **Detect:**
  - Android: `targetSdkVersion` or `targetSdk` in `build.gradle(.kts)` < `POLICY.android_new_target_sdk` (new apps) or `POLICY.android_update_target_sdk` (updates)
  - iOS: `IPHONEOS_DEPLOYMENT_TARGET` in `project.pbxproj` < `POLICY.min_ios_deployment`
  - Flutter: `compileSdk` in `android/app/build.gradle`, `platform :ios` in `Podfile`
  - React Native: `compileSdkVersion` in `android/build.gradle`, deployment target in Xcode project
- **Fix:** Update target/compile SDK. Run full test suite against new platform behaviors (scoped storage, notification permissions, photo picker, etc.)
- **Note:** See `references/scoring.md` Live Policy Fetch for current values
- **Source:** Google Play SDK requirements, Apple Xcode release notes

### STO-02 [CRITICAL] Age Rating
Content must match declared age rating. Apple uses updated questionnaire with 13+/16+/18+ tiers.
- **Detect:**
  - Missing age rating metadata in store configuration
  - Content–rating mismatch: search source for keywords (`violence`, `gambling`, `casino`, `alcohol`, `tobacco`, `drug`, `sexual`, `gore`, `weapon`, `horror`) and cross-reference with declared rating
  - Apple: verify questionnaire completed with new 13+/16+/18+ age tiers (effective Jan 31, 2026)
  - UGC-enabled apps without moderation → must declare higher rating
- **Fix:** Complete age rating questionnaire. Align content with declared rating. If UGC: implement moderation + report mechanism, declare accordingly
- **Source:** App Store 4.1, Play Store IARC

### STO-03 [CRITICAL] Privacy Labels (iOS)
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
- **Source:** App Store 5.1.2, November 2025 enforcement

### STO-04 [CRITICAL] Data Safety (Android)
Play Store Data Safety section must accurately reflect all data collection including SDKs.
- **Detect:**
  - SDK → data type mapping (same table as STO-03)
  - Encryption claim: verify TLS enforcement (cross-ref SEC-04) — if `usesCleartextTraffic="true"`, encryption claim is false
  - Third-party sharing: SDKs that transmit data to external servers (ads, analytics) must be declared as shared
  - Data deletion: if PRV-05 (Right to Erasure) not implemented, "data deletion" claim is inaccurate
- **Fix:** Complete Data Safety form. Map each SDK to data types. Verify encryption and deletion claims match implementation
- **Source:** Google Play Data Safety

### STO-05 [CRITICAL] Restore Purchases
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
- **Source:** App Store 3.1.1, Play Store subscription policy

### STO-06 [CRITICAL] AI Disclosure
Third-party AI services must be disclosed. On-device ML (Core ML, ML Kit on-device) exempt.
- **Detect:**
  - Cloud AI API usage: search for `openai`, `anthropic`, `gemini`, `claude`, `gpt`, `dall-e`, `whisper`, `stability.ai` in source and dependencies
  - Distinguish on-device vs cloud: `CoreML`, `MLKit` (on-device mode), `TFLite` → exempt. API calls to external AI endpoints → must disclose
  - AI-generated content without labeling (images, text generated by AI shown to users)
  - Model versioning: if AI model version affects output, version must be documented
- **Fix:** Disclose AI provider and purpose in privacy policy and app metadata. Label AI-generated content when shown to users. Document model versions in release notes when relevant
- **Source:** App Store 5.1.2(i), November 2025

### STO-07 [CRITICAL] Age Verification API
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
- **Source:** US State Laws, Apple WWDC 2024, Google Play Policy

### STO-08 [CRITICAL] COPPA
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
- **Source:** COPPA Rule 16 CFR 312, App Store Kids Category, Play Store Families Policy

### STO-09 [CRITICAL] Subscription Transparency
All auto-renewal terms, pricing, and trial conditions must be visible on the purchase screen before the user commits.
- **Detect:**
  - Paywall/purchase screen missing any of:
    - Subscription price and billing period (monthly/yearly)
    - Auto-renewal disclosure ("Subscription automatically renews unless cancelled")
    - Free trial duration and post-trial price
    - Introductory offer terms (if applicable)
  - Search UI files for paywall/purchase screens: `paywall`, `subscription`, `premium`, `upgrade`, `purchase`
  - Verify pricing text is visible without scrolling on standard screen sizes
  - Terms of Service and Privacy Policy links missing from purchase screen
- **Fix:** Display all subscription terms on purchase screen: price, period, auto-renewal statement, trial length + post-trial price. Add ToS and Privacy Policy links. Ensure all text is visible without scrolling
- **Source:** App Store 3.1.2, Play Store Subscriptions Policy, EU Consumer Rights Directive

### STO-10 [CRITICAL] Subscription Cancellation
Users must be able to manage and cancel subscriptions easily. Apple requires in-app cancellation mechanism.
- **Detect:**
  - iOS: no in-app subscription management or cancellation UI (required since StoreKit 2)
    - Search for: `showManageSubscriptions`, `ManageSubscriptionsSheet`, subscription settings screen
  - Android: no link to Play Store subscription management
    - Search for: `play.google.com/store/account/subscriptions`, deep link to subscription management
  - No grace period handling: app immediately locks content when billing fails instead of showing retry state
  - Missing subscription status indicators (active, expired, grace period, billing retry)
- **Fix:** iOS: implement `showManageSubscriptions` or `ManageSubscriptionsSheet`. Android: deep link to `https://play.google.com/store/account/subscriptions`. Show subscription status. Handle grace period (3-day iOS, variable Android) gracefully
- **Source:** App Store 3.1.2(a), Play Store Subscription Policy

### STO-11 [CRITICAL] Sign in with Apple
If the app offers third-party social login, Sign in with Apple must be offered alongside (iOS only).
- **Detect:**
  - Search for third-party OAuth providers: `GoogleSignIn`, `google_sign_in`, `FacebookLogin`, `facebook_auth`, `TwitterLogin`, `GIDSignIn`, `ASAuthorizationAppleIDProvider`, `sign_in_with_apple`
  - If any third-party OAuth found AND no `ASAuthorizationAppleIDProvider` or `sign_in_with_apple` → CRITICAL
  - Exemptions: educational institution apps (managed Apple IDs), enterprise internal apps, government apps, apps using only company's own first-party auth
  - Sign in with Apple button placement: must be equal or more prominent than other login options
- **Fix:** Add Sign in with Apple alongside existing OAuth providers. Use `ASAuthorizationAppleIDProvider` (native) or `sign_in_with_apple` (Flutter). Ensure button is equally or more prominent than alternatives. Handle credential revocation
- **Source:** App Store 4.8, Apple Human Interface Guidelines

### STO-12 [HIGH] App Completeness
App must be fully functional with no placeholder content, broken features, or incomplete sections.
- **Detect:**
  - Placeholder content patterns in UI strings and assets:
    - `lorem ipsum`, `placeholder`, `coming soon`, `under construction`, `TODO`, `FIXME` in user-visible strings
    - `dummy`, `sample`, `test data` in production data/assets
  - Non-functional UI elements: buttons with empty `onPressed`/`onTap`/`onClick` handlers
  - Search for: `onPressed: null`, `onTap: () {}`, `onPressed: () {}`, `// TODO`, `NotImplementedError`
  - Empty screens or sections (scaffold with no content)
  - Test/demo credentials visible in production builds
- **Fix:** Replace all placeholder content with real content. Implement or remove non-functional UI elements. Remove test data and demo credentials from production builds
- **Source:** App Store 2.1, Play Store Spam and Minimum Functionality Policy

### STO-13 [HIGH] Metadata Accuracy
Store listing metadata must accurately reflect app functionality. No misleading claims.
- **Detect:**
  - Screenshots that don't reflect actual app UI (device mockups with fabricated screens)
  - Description claims features not present in codebase
  - Fake reviews or testimonials in description
  - Credentials or certifications claimed without verification
  - App name contains price indicators ("Free") that may become inaccurate
  - Search store metadata files: `fastlane/metadata`, `android/fastlane`, `ios/fastlane`, store listing drafts
- **Fix:** Ensure screenshots show real app UI. Align description with implemented features. Remove fake testimonials or unverifiable claims. Update metadata on each release
- **Source:** App Store 2.3, Play Store Metadata Policy

### STO-14 [HIGH] Permission Justification
Every requested permission must have a clear use case. Unused or unjustified permissions cause rejection.
- **Detect:**
  - Declared permissions not used in code:
    - Android: compare `AndroidManifest.xml` `<uses-permission>` against actual API usage in source
    - iOS: compare `Info.plist` `NS*UsageDescription` keys against framework imports
  - Permission ↔ privacy label mismatch: permission declared but data type not in privacy labels (STO-03/STO-04)
  - Sensitive permissions without user-facing justification string:
    - Camera (`CAMERA`), Microphone (`RECORD_AUDIO`), Location (`ACCESS_FINE_LOCATION`), Contacts (`READ_CONTACTS`), Photos (`READ_MEDIA_IMAGES`)
  - Background location without foreground use case demonstrated first
- **Fix:** Remove unused permissions. Add `NS*UsageDescription` strings for all iOS permissions. Ensure each permission maps to a declared data practice. Request sensitive permissions in context (when feature is used, not at launch)
- **Source:** App Store 5.1.1, Play Store Permissions Policy

### STO-15 [CRITICAL] ATT Compliance (iOS)
App Tracking Transparency prompt must appear before any tracking occurs. IDFA access requires ATT.
- **Detect:**
  - Tracking SDK initialization before ATT prompt:
    - Search for SDK init calls (`Firebase.initializeApp`, `Adjust.start`, `AppsFlyer.init`, `FBSDKApplicationDelegate`, `FacebookSdk.sdkInitialize`) and verify they occur after ATT response
    - Search for: `ATTrackingManager.requestTrackingAuthorization`, `app_tracking_transparency`
  - IDFA usage without ATT: `ASIdentifierManager.advertisingIdentifier` called without prior ATT check
  - Privacy label ↔ ATT inconsistency: "Data Used to Track You" declared but no ATT prompt, or ATT prompt present but tracking not declared
  - Pre-ATT prompt (custom explanation screen) missing — direct system prompt without context
- **Fix:** Show custom explanation screen before ATT prompt. Initialize tracking SDKs only after ATT authorization. Gate IDFA access behind ATT status check. Align privacy labels with ATT behavior
- **Source:** App Store 5.1.2(i), Apple ATT Framework

### STO-16 [HIGH] Push Notification Consent
Apps should explain notification value before triggering the OS permission prompt.
- **Detect:**
  - OS notification permission requested at app launch without prior explanation
  - Search for notification permission request: `UNUserNotificationCenter.requestAuthorization`, `Notification.requestPermission`, `firebase_messaging` permission request
  - Permission request in `didFinishLaunchingWithOptions`, `application:didFinishLaunching`, `main()`, `initState()` (first screen)
  - No notification preference/settings screen for granular opt-in/out
- **Fix:** Add pre-permission screen explaining notification types and value. Defer OS prompt to contextual moment (after user action that benefits from notifications). Add notification preferences screen for category-level opt-in/out
- **Source:** Apple HIG Notifications, Play Store User Data Policy

### STO-17 [HIGH] Deep Linking
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
- **Source:** Apple Universal Links, Android App Links, Play Store Deep Linking Policy

### STO-18 [MEDIUM] Store Listing Localization
Store metadata should be localized for all languages the app supports.
- **Detect:**
  - App supports multiple locales (ARB files, `.lproj` directories, `values-xx/strings.xml`) but store metadata only in one language
  - Search for: `fastlane/metadata/*/`, locale-specific store listing directories
  - Compare app-supported locales against store listing locales
  - Screenshots not localized (same screenshots for all locales)
- **Fix:** Translate store metadata (title, subtitle, description, keywords, what's new) for each supported locale. Localize screenshots to show translated UI. Use Fastlane or store console for metadata management
- **Source:** App Store Localization, Play Store Translation Best Practices

### STO-19 [HIGH] Background Mode Justification (iOS)
Every declared `UIBackgroundModes` capability must have real functional usage. Unused background modes cause rejection.
- **Detect:**
  - Search `Info.plist` for `UIBackgroundModes` array entries: `audio`, `location`, `voip`, `fetch`, `remote-notification`, `bluetooth-central`, `bluetooth-peripheral`, `external-accessory`, `processing`
  - For each declared mode, verify actual usage in source code:

    | Mode | Required Evidence |
    |------|------------------|
    | `audio` | `AVAudioSession`, audio playback/recording API usage |
    | `location` | `CLLocationManager` with `allowsBackgroundLocationUpdates` |
    | `voip` | PushKit or VoIP call handling |
    | `fetch` | `BGAppRefreshTask` or `performFetchWithCompletionHandler` |
    | `remote-notification` | Silent push handling with content-available |
    | `bluetooth-central` | `CBCentralManager` background scanning |

  - Declared mode with no matching API usage → HIGH (will be rejected)
- **Fix:** Remove unused `UIBackgroundModes` entries. If background capability is needed, ensure corresponding API is implemented and functional
- **Source:** App Store 2.5.4, Apple Background Execution Guide

### STO-20 [HIGH] Billing Library Version (Android)
Play Billing Library must meet minimum version requirement. Outdated versions are rejected.
- **Detect:**
  - Search `build.gradle(.kts)` for: `com.android.billingclient:billing`, `com.android.billingclient:billing-ktx`
  - Compare version against `POLICY.min_billing_lib` (see `references/scoring.md`)
  - Flutter: check `in_app_purchase_android` plugin version which bundles Billing Library
  - React Native: check `react-native-iap` version for bundled Billing Library version
  - Missing migration from deprecated APIs (e.g., `querySkuDetailsAsync` → `queryProductDetailsAsync`)
- **Fix:** Update Play Billing Library to >= `POLICY.min_billing_lib`. Migrate deprecated API calls. Test purchase flow end-to-end after upgrade
- **Source:** Play Billing Library Release Notes, Play Store Billing Policy
