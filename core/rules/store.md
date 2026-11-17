# Store — technical submission blockers the repo can show

Loaded for apps shipped through an app store. Listing content (name, description, screenshots, positioning) is out of scope. Store minimums (SDK levels, library versions) change: read the value from the build files and compare it with the live requirement page named in the rule. Consent before tracking is PRV-01; in-app AI disclosure is UX-10a.

### REL-02 [CRITICAL] Release build not signed for the store
- **Detect:** an Android `release` build type using `signingConfigs.debug` or no release signing config; keystore passwords in tracked build files; iOS release archives on a development or ad-hoc profile; an `eas.json` production profile without store distribution credentials. A committed keystore or key file is SEC-01.
- **Mech:** T `git grep -nIE 'signingConfig[[:space:]]*(=)?[[:space:]]*signingConfigs\.debug|storePassword|keyPassword|CODE_SIGN_IDENTITY|PROVISIONING_PROFILE|"distribution"' -- '*.gradle' '*.kts' '*.properties' '*.pbxproj' 'eas.json'`
- **Fix:** a release signing config that reads the keystore and passwords from the environment or CI secrets; App Store distribution signing (Xcode automatic signing, fastlane `match`, EAS credentials); Play App Signing for the upload key.
- **Impact:** the store refuses the upload, or a leaked signing key lets anyone ship updates as the app.
- **Source:** Android, Sign your app; Apple, Distributing your app for beta testing and releases.

### REL-04 [HIGH] Build number not increasing automatically
- **Detect:** `versionCode`, `CFBundleVersion`/`CURRENT_PROJECT_VERSION` or the `pubspec.yaml` build number edited by hand or fixed in config; no single version source for both platforms.
- **Mech:** T `git grep -nIE 'versionCode|CFBundleVersion|CURRENT_PROJECT_VERSION|^version:|"buildNumber"|autoIncrement' -- '*.gradle' '*.kts' '*.plist' '*.pbxproj' 'pubspec.yaml' 'app.json' 'eas.json'`
- **Fix:** derive the build number in the release step (CI run number, commit count, the build service's auto-increment) from one version source.
- **Impact:** uploads fail on a reused build number, usually at the end of a release.
- **Source:** Android, Version your app; Apple, CFBundleVersion.

### STO-01 [CRITICAL] Target SDK or minimum OS out of range
- **Detect:** Android `targetSdk`/`compileSdk` below Google Play's current target-API requirement; iOS archives built with an Xcode and SDK older than App Store Connect accepts; a minimum OS (`minSdk`, `IPHONEOS_DEPLOYMENT_TARGET`, `platform :ios`) below what the dependencies support.
- **Mech:** T `git grep -nIE '(targetSdk|targetSdkVersion|compileSdk|compileSdkVersion|minSdk|minSdkVersion)[[:space:]]*(=|:)?[[:space:]]*[0-9]+|IPHONEOS_DEPLOYMENT_TARGET|platform :ios' -- '*.gradle' '*.kts' '*.properties' '*.pbxproj' 'Podfile' 'app.json' 'app.config.*'`
- **Fix:** raise the target to the current requirement and test that version's behaviour changes; align the minimum OS across the project and its dependencies; build with the required Xcode.
- **Impact:** the upload is refused, or an existing app stops being offered on recent OS versions.
- **Source:** Google Play, Target API level requirements (https://developer.android.com/google/play/requirements/target-sdk); Apple, Upcoming requirements (App Store Connect).

### STO-14 [HIGH] Permission without a usage string or without a use
- **Detect:** iOS APIs for camera, microphone, location, contacts, photos, Bluetooth or tracking used with no `NS*UsageDescription` key in `Info.plist`, or with an empty or generic one; `<uses-permission>` entries (including ones merged from libraries) with no matching API call; Android restricted permissions (SMS, call log, all-files access, exact alarms, background location) without the core feature that needs them.
- **Mech:** T `git grep -nIE '<uses-permission|NS[A-Za-z]+UsageDescription' -- '*.xml' '*.plist' 'app.json' 'app.config.*'` · `git grep -nIE 'AVCaptureDevice|CLLocationManager|CNContactStore|PHPhotoLibrary|CBCentralManager|AVAudioSession|ATTrackingManager' -- '*.swift' '*.m'`
- **Fix:** a specific usage string per iOS API, saying what the user gets; remove unused Android permissions (`tools:node="remove"` for merged ones).
- **Impact:** iOS terminates the app on first access without the string, and review rejects unused or unexplained permissions.
- **Source:** Apple App Review Guideline 5.1.1; Apple, Requesting access to protected resources; Google Play, Permissions and APIs that access sensitive information.

### STO-03 [CRITICAL] Privacy manifest or store data declaration out of date
- **Detect:** an iOS app without `PrivacyInfo.xcprivacy`, or one that does not list the required-reason APIs it calls (file timestamps, system boot time, disk space, active keyboards, `UserDefaults`); privacy-label or Data safety answers that do not match the SDKs receiving personal data in PRV-15's data-flow inventory; a new SDK or capability merged without updating the declaration; "encrypted in transit" declared while cleartext traffic is allowed.
- **Mech:** T `git ls-files | grep -E 'PrivacyInfo\.xcprivacy$'` · `git grep -nIE 'NSFileCreationDate|NSFileModificationDate|creationDate|modificationDate|systemUptime|mach_absolute_time|volumeAvailableCapacity|activeInputModes|UserDefaults' -- '*.swift' '*.m' '*.mm'` · `git grep -nIE 'usesCleartextTraffic="true"|NSAllowsArbitraryLoads' -- '*.xml' '*.plist'`
- **Fix:** a privacy manifest with every required-reason API; derive the label and Data safety answers from the PRV-15 inventory and update them in the same commit as the SDK or capability.
- **Impact:** uploads are rejected for missing manifests, and a wrong declaration leads to removal.
- **Source:** Apple, Privacy manifest files and Describing use of required reason API; Google Play, Data safety section (https://support.google.com/googleplay/android-developer/answer/10787469).

### LCH-09 [HIGH] Account cannot be deleted in the app
applies_when: auth≠none
- **Detect:** the app creates accounts but offers no in-app path that deletes the account and its data (deactivation or "email us" is not deletion); no web deletion URL for Google Play; deletion that leaves the store subscription running with no notice.
- **Mech:** T `git grep -nIiE 'delete.?account|deleteUser|account.?deletion|close.?account' -- ':!*.md'`
- **Fix:** a delete action in account settings that removes the account and its data server-side (PRV-04), a public web deletion URL for Play, and a note to cancel the store subscription.
- **Impact:** review rejects the build, and users cannot leave.
- **Source:** Apple App Review Guideline 5.1.1(v); Google Play, Account deletion requirements.

### VIS-14 [MEDIUM] Icon or launch assets missing a required size
- **Detect:** iOS `AppIcon.appiconset` without the 1024 px marketing icon or with an alpha channel in it; no launch screen (`UILaunchScreen` or a launch storyboard); Android without an adaptive icon (`mipmap-anydpi-v26` foreground and background), with artwork outside the safe zone, without a monochrome layer, or without a splash configured through the SplashScreen API.
- **Mech:** T `git ls-files | grep -iE 'AppIcon\.appiconset/|LaunchScreen|mipmap-anydpi|ic_launcher|splash'` · `git grep -nIE 'UILaunchScreen|UILaunchStoryboardName|windowSplashScreen|Theme\.SplashScreen' -- '*.plist' '*.xml'`
- **Fix:** generate every icon and splash size from one source image with the platform's tool (Xcode single-size icon, Android Studio Image Asset, `flutter_launcher_icons`, Expo config).
- **Impact:** App Store Connect rejects invalid icons, and launchers show cropped or default icons.
- **Source:** Apple HIG, App icons and Launching; Android, Adaptive icons and Splash screens.

### LCH-11 [CRITICAL] Digital goods paid outside store billing
applies_when: billing≠none
- **Detect:** a store build that sells digital content, subscriptions or features through a web checkout (Stripe, Paddle, PayPal) or a link out to buy, without the store's external-purchase or alternative-billing programme for that storefront; physical goods or services routed through in-app purchase.
- **Mech:** T `git grep -nIiE 'stripe|paddle|paypal|lemonsqueezy|checkout' -- '*.swift' '*.kt' '*.java' '*.dart' ':!*test*'`
- **Fix:** the store's in-app purchase for digital goods in store builds, or the platform's external-purchase programme where it applies, checked per storefront.
- **Impact:** rejection or removal, and revenue held by the store.
- **Source:** Apple App Review Guideline 3.1.1 and 3.1.3; Google Play, Payments policy.

### STO-05 [HIGH] No restore-purchases path
applies_when: billing≠none
- **Detect:** in-app purchases with no visible restore action; entitlements kept only as a local flag instead of re-derived from the store (StoreKit 2 `Transaction.currentEntitlements`, Play Billing `queryPurchasesAsync`, the RevenueCat customer info).
- **Mech:** T `git grep -nIE 'restorePurchases|restoreCompletedTransactions|currentEntitlements|queryPurchasesAsync|getAvailablePurchases|AppStore\.sync' -- ':!*.md'`
- **Fix:** a restore button on the paywall and in settings; derive entitlements from the store at start and on restore.
- **Impact:** paying users on a new device lose what they bought, and review rejects the build.
- **Source:** Apple App Review Guideline 3.1.1; Google Play Billing, Process purchases.

### STO-21 [HIGH] Purchase states not all handled
applies_when: billing≠none
- **Detect:** purchase listeners that handle only success; pending or deferred (Ask to Buy, cash payments) purchases treated as failed or granted; cancelled and already-owned results shown as errors; Play purchases never acknowledged; StoreKit transactions never finished.
- **Mech:** T `git grep -nIE 'PurchaseStatus\.|purchaseState|PurchaseState\.PENDING|deferred|acknowledgePurchase|finishTransaction|completePurchase|\.finish\(\)' -- ':!*.md'`
- **Fix:** handle every state the store library defines; grant on a verified purchase, then acknowledge or finish; show pending purchases as pending.
- **Impact:** Play refunds purchases not acknowledged within three days, and users pay without receiving the item.
- **Source:** Google Play Billing, Integrate the library (acknowledge purchases); Apple, StoreKit `Transaction.finish()`.

### STO-20 [HIGH] Play Billing Library below the supported version
applies_when: platforms∋android
- **Detect:** `com.android.billingclient:billing` (or the version bundled by `in_app_purchase_android`, `react-native-iap`, `purchases_flutter`) older than the minimum Play accepts; deprecated calls such as `querySkuDetailsAsync`.
- **Mech:** T `git grep -nIE 'com\.android\.billingclient:billing|in_app_purchase_android|react-native-iap|purchases_flutter|querySkuDetailsAsync' -- ':!*.md'`
- **Fix:** upgrade to a supported major version and migrate deprecated calls; test the purchase flow in the sandbox.
- **Impact:** Play blocks updates that ship an unsupported billing library.
- **Source:** Google Play Billing, Deprecation FAQ (https://developer.android.com/google/play/billing/deprecation-faq).

### STO-15 [CRITICAL] Tracking before App Tracking Transparency
applies_when: platforms∋ios
- **Detect:** IDFA reads, attribution or ad SDKs started before `ATTrackingManager.requestTrackingAuthorization` resolves; tracking SDKs present with no `NSUserTrackingUsageDescription`; the data declaration (STO-03) claiming tracking with no prompt, or the reverse.
- **Mech:** T `git grep -nIE 'advertisingIdentifier|requestTrackingAuthorization|app_tracking_transparency|NSUserTrackingUsageDescription|AppsFlyer|Adjust\.|FBSDKCoreKit|GoogleMobileAds' -- ':!*.md'`
- **Fix:** start tracking SDKs only after an authorized ATT result and in non-tracking mode otherwise; keep the declaration and the prompt consistent.
- **Impact:** rejection, and tracking of users who refused it.
- **Source:** Apple App Review Guideline 5.1.2; Apple, App Tracking Transparency framework.

### STO-19 [HIGH] Capability declared without use
- **Detect:** `UIBackgroundModes` entries (audio, location, voip, fetch, processing, bluetooth) without the matching API use; entitlements (push, Sign in with Apple, iCloud, associated domains) without the feature, or features without the entitlement.
- **Mech:** T `git grep -nIE -A12 'UIBackgroundModes' -- '*.plist'` · `git ls-files '*.entitlements'`
- **Fix:** declare exactly what the code uses; reconcile entitlements with the provisioning profile.
- **Impact:** review rejects unused background modes, and missing entitlements fail at runtime.
- **Source:** Apple App Review Guideline 2.5.4; Apple, Entitlements.

### STO-22 [HIGH] Foreground service without a declared type
applies_when: platforms∋android
- **Detect:** `startForeground()` with no `android:foregroundServiceType` on the service; types without their `FOREGROUND_SERVICE_*` permission; `dataSync` services without `onTimeout`; no matching Play Console declaration.
- **Mech:** T `git grep -nIE 'startForeground|foregroundServiceType|FOREGROUND_SERVICE' -- ':!*.md'`
- **Fix:** the correct type and permission per service, `onTimeout` for time-limited types, WorkManager for deferrable work, and the Play Console declaration.
- **Impact:** the service crashes with `MissingForegroundServiceTypeException`, or the update is rejected.
- **Source:** Android, Foreground service types (https://developer.android.com/develop/background-work/services/fgs/service-types).

### REL-22 [HIGH] Native libraries not aligned for 16 KB pages
applies_when: platforms∋android
- **Detect:** bundled `.so` files (own NDK code or from Flutter, React Native, game engines, ML runtimes) built with 4 KB segment alignment or packaged without 16 KB zip alignment; an outdated NDK or Android Gradle Plugin.
- **Mech:** T `git ls-files '*.so'` · `git grep -nIE 'ndkVersion|useLegacyPackaging|com\.android\.tools\.build:gradle|com\.android\.application' -- '*.gradle' '*.kts' '*.toml'`
- **Fix:** build with a current NDK and AGP, update native dependencies to 16 KB-aligned releases, and check with the APK Analyzer or `zipalign -c -P 16`.
- **Impact:** the app fails to install or crashes on 16 KB devices, and Play rejects the update.
- **Source:** Android, Support 16 KB page sizes (https://developer.android.com/guide/practices/page-sizes).

### REL-08 [MEDIUM] Wrong release artifact
- **Detect:** release scripts producing an APK for Google Play instead of an Android App Bundle; debuggable release builds.
- **Mech:** T `git grep -nIE 'assembleRelease|flutter build apk|debuggable[[:space:]]*(=|:)?[[:space:]]*true' -- ':!*.md'`
- **Fix:** `bundleRelease` or `flutter build appbundle` for Play; `debuggable false` for release builds.
- **Impact:** Play refuses the upload, or a debuggable build ships.
- **Source:** Google Play, Android App Bundles; Android, Prepare your app for release.

### STO-11 [CRITICAL] Third-party login without the Apple-required alternative
applies_when: platforms∋ios
- **Detect:** Google, Facebook or other third-party social login in the iOS app with no Sign in with Apple or another login service that limits data to name and email, allows a private email and does not track.
- **Mech:** T `git grep -nIE 'GoogleSignIn|google_sign_in|FBSDKLoginKit|flutter_facebook_auth|react-native-fbsdk|ASAuthorizationAppleIDProvider|sign_in_with_apple|AppleAuthentication' -- ':!*.md'`
- **Fix:** add Sign in with Apple (or a qualifying service) with equal prominence, unless the app uses only its own account system.
- **Impact:** rejection at review.
- **Source:** Apple App Review Guideline 4.8, Login Services.

### STO-17 [HIGH] Deep links unverified or without a fallback
- **Detect:** custom URL schemes only; no `applinks:` associated-domains entitlement or `autoVerify` App Links intent filter; unknown or stale link paths that crash or open a blank screen.
- **Mech:** T `git grep -nIE 'autoVerify|applinks:|apple-app-site-association|assetlinks\.json|CFBundleURLSchemes' -- ':!*.md'`
- **Fix:** verified Universal Links and App Links with association files matching the team ID, bundle ID, package and signing fingerprint; route unknown paths to a sensible screen.
- **Impact:** links open the browser or another app, or crash the app.
- **Source:** Apple, Supporting associated domains; Android, Verify App Links.

### STO-12 [HIGH] Placeholder or test content in the release build
- **Detect:** user-visible strings or bundled assets with `lorem ipsum`, "coming soon", test accounts or sample data; features switched off remotely in the review build. No-op controls are CMP-16.
- **Mech:** T `git grep -nIiE 'lorem ipsum|coming soon|under construction|placeholder text|test@test|demo123' -- ':!*test*' ':!*.md'`
- **Fix:** ship only finished features; remove test data; keep remote flags on for review.
- **Impact:** incomplete builds are the most common rejection, each costing a review cycle.
- **Source:** Apple App Review Guideline 2.1, App Completeness; Google Play, Minimum functionality policy.
