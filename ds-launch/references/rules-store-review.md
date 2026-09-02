# Rules: Store Review Readiness

Each check scans the codebase/metadata and produces PASS/FAIL with severity, `file:line`, and a fix — not a manual checklist. Loaded when the Review scope resolves to run (see SKILL.md Scopes table).

| Section | Rules |
|---------|-------|
| **App Completeness & Metadata** | LCH-01 to LCH-05 (2 CRITICAL, 2 HIGH, 1 MEDIUM) |
| **Privacy & Consent** | LCH-06 to LCH-10 (5 HIGH) |
| **Monetization & Payments** | LCH-11 to LCH-12 (1 CRITICAL, 1 HIGH) |
| **Content & Rating** | LCH-13 to LCH-16 (1 HIGH, 3 MEDIUM) |
| **Platform & Build** | LCH-17 to LCH-19 (1 HIGH, 2 MEDIUM) |
| **Pre-Submission Testing** | LCH-20 to LCH-23 (3 HIGH, 1 MEDIUM) |
| **Release Rollout** | LCH-24 (1 MEDIUM) |
| **Additional Pre-Submission & Metadata Checks** | LCH-25 to LCH-28 (4 HIGH) |

**Review timing (informational, not a check):** Apple 24-48h typical; Google Play 1-7 days (longer for a first app) — see [aso-2026-updates.md](aso-2026-updates.md) § Store Submission Timeline for the full 60-day pre-launch schedule.

## App Completeness & Metadata

### LCH-01 [CRITICAL] Privacy Policy URL Live and Accessible

**Detect:** Scan store metadata + in-app configs for a privacy policy URL; `curl -s -o /dev/null -w '%{http_code}' {url}` must return `200`.

**Fix:** Publish a live, publicly accessible privacy policy page; add its URL to both store listings and in-app settings before submission.

**Impact:** Outright rejection — no review proceeds without a live policy URL.

**Source:** App Store Review Guidelines (https://developer.apple.com/app-store/review/guidelines/) 5.1.1; Play Console Privacy Policy requirement.

---

### LCH-02 [CRITICAL] Metadata Completeness (No Placeholder Content)

**Detect:** Scan store metadata directories for empty fields or placeholder content (draft markers, lorem ipsum, "TBD").

**Fix:** Fill every required listing field with final content before submitting; remove draft/placeholder markers.

**Impact:** Outright rejection under Guideline 2.1 (App Completeness).

**Source:** App Store Review Guidelines 2.1; Play Store Metadata Policy.

---

### LCH-03 [MEDIUM] Platform Cross-Reference in Listing Text

**Detect:** Search listing text for competing-platform mentions (naming the other store, "also available on…").

**Fix:** Remove references to competing platforms from store listing copy.

**Impact:** Listing edit demand or takedown.

**Source:** App Store Review Guidelines 3.1; Play Store Metadata Policy.

---

### LCH-04 [HIGH] Reviewer-Access Gap (Missing Demo Credentials)

**Detect:** Login/auth flow detected in the app but `ds/launch/submission-notes-apple.txt` is absent or missing its demo-credentials section.

**Fix:** Generate submission notes via `--submission-notes` and provide pre-provisioned reviewer credentials before submitting.

**Impact:** Automatic rejection — the reviewer cannot proceed past the login wall.

**Source:** App Store Review Guidelines 2.1.

---

### LCH-05 [HIGH] App Completeness / Remote Feature Gating

**Detect:** Primary feature classes wrapped in remote-config/feature-flag conditions with no guaranteed-on default for the reviewer.

**Fix:** Ensure every primary feature has a guaranteed-on default reachable without a remote-config round trip that could return "off".

**Impact:** Rejection under Guideline 2.1 — the app looks broken to the reviewer.

**Source:** App Store Review Guidelines 2.1; Play Store Deceptive Behavior Policy.

## Privacy & Consent

### LCH-06 [HIGH] Permission Usage Descriptions Present

**Detect:** Parse `Info.plist` / `AndroidManifest.xml` for permissions missing a usage-description string.

**Fix:** Add a clear `NS*UsageDescription` (iOS) or permission rationale (Android) for every requested permission.

**Impact:** Rejection or review delay — the reviewer cannot verify the permission's purpose.

**Source:** App Store Review Guidelines 5.1.1; Play Store Permissions Policy.

---

### LCH-07 [HIGH] Privacy Manifest + SDK Compliance

**Detect:** Scan for `PrivacyInfo.xcprivacy`; flag third-party SDKs shipped without a matching privacy manifest.

**Fix:** Add the app's own privacy manifest and confirm every bundled SDK ships its own (upgrade SDKs that don't).

**Impact:** Rejection — required-reason APIs undeclared.

**Source:** Apple Privacy Manifest requirement (App Store Review Guidelines).

---

### LCH-08 [HIGH] AI Service Consent Modal

**Detect:** External AI service usage detected (API calls to a third-party AI provider) with no consent modal shown before data leaves the device.

**Fix:** Show a consent modal naming the AI provider and data types before the first call to an external AI service.

**Impact:** Rejection under Guideline 5.1.1(i).

**Source:** App Store Review Guidelines 5.1.1(i).

---

### LCH-09 [HIGH] Account/Data Deletion Flow Present

**Detect:** Search for an account-deletion or data-deletion UI flow reachable from account settings.

**Fix:** Implement an in-app deletion flow that removes the account and its data, reachable without contacting support.

**Impact:** Rejection under Guideline 5.1.1(v).

**Source:** App Store Review Guidelines 5.1.1(v); Play Store Account Deletion Policy.

---

### LCH-10 [HIGH] App Tracking Transparency Prompt Before Tracking

**Detect:** IDFA/tracking SDK initialization before the ATT prompt response, or `PrivacyInfo.xcprivacy` declares tracking without an ATT prompt present.

**Fix:** Gate tracking SDK initialization and IDFA access behind a confirmed ATT authorization; show the custom pre-prompt explanation first.

**Impact:** Rejection, or post-launch takedown on audit.

**Source:** App Store Review Guidelines 5.1.2(i); Apple ATT Framework.

## Monetization & Payments

### LCH-11 [CRITICAL] IAP / External-Payment Link Compliance (Jurisdiction-Conditional)

**Detect:** StoreKit/Play Billing present alongside Stripe/PayPal/checkout URLs for digital content, or "pay on our website" strings pointing off-store. Jurisdiction determines the rule: US App Store storefront allows external payment links without entitlement (Ninth Circuit ruling, Dec 2025); outside the US, the StoreKit External Purchase Link Entitlement is required in designated regions, otherwise IAP-only.

**Fix:** US storefront — external links are permitted (no more visually prominent than IAP). Outside the US — obtain the External Purchase Link Entitlement or remove the external payment path and route digital-content purchases through IAP.

**Impact:** Rejection under Guideline 3.1.1, or post-launch removal.

**Source:** App Store Review Guidelines 3.1.1; Play Store Billing Policy (alternative billing per settlement terms).

---

### LCH-12 [HIGH] Restore Purchases Path Present

**Detect:** Non-consumable IAP or subscription imports detected but no restore-purchases call or UI entry point found.

**Fix:** Add a visible "Restore Purchases" button and implement the platform's restore API (StoreKit `restoreCompletedTransactions` / `BillingClient.queryPurchasesAsync`).

**Impact:** Rejection under Guideline 3.1.2.

**Source:** App Store Review Guidelines 3.1.2; Play Store Subscription Policy.

## Content & Rating

### LCH-13 [MEDIUM] Age Rating Matches Declared Content

**Detect:** Verify age-rating questionnaire completeness against the 13+/16+/18+ tiers.

**Fix:** Complete the age-rating questionnaire and align the declared rating with actual app content, including UGC moderation status.

**Impact:** Rating-questionnaire rejection, re-submission cycle.

**Source:** App Store Review Guidelines 4.1 (age ratings); Play Store IARC.

---

### LCH-14 [HIGH] Clone-Category Differentiation Risk (Guideline 4.3(b))

**Detect:** App's category/concept matches Apple's named spam-prone classes (dating, flashlight, sound effects, wallpaper, simple timers, fortune telling) with no meaningfully differentiated feature set.

**Fix:** Document and implement genuine differentiation before submitting in a saturated category; maintain a regular update cadence.

**Impact:** Submission barred outright, or an existing listing removed.

**Source:** App Store Review Guidelines 4.3(b) (June 2026 revision).

---

### LCH-15 [MEDIUM] Live Activities Misuse (Guideline 4.5.3)

**Detect:** ActivityKit/Live Activities used for promotional or unsolicited content; random/anonymous-chat features present without UGC moderation duties addressed.

**Fix:** Restrict Live Activities to their intended live-status use case; add UGC moderation/reporting for any chat feature.

**Impact:** Rejection under 4.5.3, compounding with 1.2 for UGC apps.

**Source:** App Store Review Guidelines 4.5.3, 1.2 (Feb 2026 revision).

---

### LCH-16 [MEDIUM] Content Matches Declared Age Rating

**Detect:** Gambling SDK, loot-box pattern, unrestricted `WebView`, or UGC text input detected alongside a 4+/Everyone age-rating declaration.

**Fix:** Raise the declared age rating to match detected content signals, or remove/restrict the content pattern.

**Impact:** Rating dispute, forced re-submission.

**Source:** App Store Review Guidelines 4.1; Play Store IARC.

## Platform & Build

### LCH-17 [MEDIUM] Crash-Prone Entry-Point Patterns

**Detect:** Scan app entry points for force-unwraps, unhandled exceptions, or other crash-prone patterns on the first-launch path.

**Fix:** Guard entry-point code against nil/exception cases the reviewer's first launch is likely to hit.

**Impact:** Reviewer hits a crash on first launch — instant rejection.

**Source:** App Store Review Guidelines 2.1.

---

### LCH-18 [MEDIUM] SDK / Build Requirement Currency

**Detect:** Check minimum/target SDK version against the current store deadline (iOS 26 SDK required from April 2026).

**Fix:** Rebuild against the current required SDK before the deadline; verify no deprecated API paths are exercised.

**Impact:** Build rejected as non-compliant at upload.

**Source:** Apple Xcode release notes (App Store Review Guidelines); Play Store target API level policy.

---

### LCH-19 [HIGH] Sign in with Apple Alongside Third-Party Social Login

**Detect:** Google/Facebook/Twitter auth SDK detected without a matching `com.apple.developer.applesignin` entitlement or `ASAuthorizationAppleIDProvider` import.

**Fix:** Add Sign in with Apple alongside existing OAuth providers, with equal or greater visual prominence.

**Impact:** Rejection under Guideline 4.8.

**Source:** App Store Review Guidelines 4.8.

## Pre-Submission Testing

### LCH-20 [HIGH] Auth Flow Tested on a Real Device Before Submission

**Detect:** No recorded evidence (in `ds/launch/submission-meta.yml` or the pre-submission audit trail) that every offered sign-in provider (OIDC, Sign in with Apple, first-party) was exercised end-to-end on a physical device before this submission.

**Fix:** Test every auth provider on a real device — sign-in, session persistence, and sign-out — before submitting; record the result.

**Impact:** An untested auth path is the most common reason a reviewer hits a login wall that never resolves — the failure LCH-04 checks for statically, confirmed here by actually running it.

**Source:** Apple TestFlight documentation (https://developer.apple.com/testflight/); App Store Review Guidelines 2.1.

---

### LCH-21 [HIGH] Core Feature End-to-End Tested Against a Production-Equivalent Backend

**Detect:** No recorded evidence that the app's primary user journey was exercised end-to-end against a real (or production-equivalent) backend — not a mock — before submission.

**Fix:** Run the core feature flow start-to-finish against the real backend on a physical device or TestFlight/Internal Testing build; record the result before submitting.

**Impact:** Guideline 2.1 requires a fully working app; a core flow that only works against a local mock is exactly the gap a reviewer's real-world test exposes.

**Source:** App Store Review Guidelines 2.1 (App Completeness).

---

### LCH-22 [HIGH] Data Export Flow Tested End-to-End

**Detect:** App has a data-export/portability feature but no recorded evidence the export was exercised end-to-end (request → generated file → content correctness) before submission.

**Fix:** Run the export flow to completion and verify the output file actually contains the user's data before submitting.

**Impact:** A data-export feature that exists in code but was never run end-to-end is indistinguishable from a broken one the first time a user or regulator relies on it.

**Source:** GDPR Art. 20 (https://eur-lex.europa.eu/eli/reg/2016/679/oj) — right to data portability.

---

### LCH-23 [MEDIUM] Offline / Reconnect Behavior Tested

**Detect:** No recorded evidence the app was tested through a disconnect → offline → reconnect cycle before submission.

**Fix:** Toggle network off mid-session, exercise the app's core flow offline, then reconnect and verify state recovers (queued actions sync, no crash, no data loss); record the result.

**Impact:** Offline/reconnect handling is a common, easily-reproduced reviewer path to a crash or stuck state — exactly the "broken feature" Guideline 2.1 rejects, and one static analysis alone does not catch.

**Source:** App Store Review Guidelines 2.1 (App Completeness).

## Release Rollout

### LCH-24 [MEDIUM] Staged-Rollout Halt Threshold on Crash-Free Rate

**Detect:** Staged/phased rollout in progress (Play Console percentage rollout or App Store Connect phased release) with no defined crash-free-rate threshold that halts or rolls back the rollout.

**Fix:** Define and monitor a crash-free-rate floor (a common practice is 99%) at each rollout stage; halt or roll back — automatically or manually — the moment a stage drops below it, before advancing to the next percentage.

**Impact:** Without a defined halt threshold, a defect that only appears at scale keeps rolling out to more users during the exact window staged rollout exists to protect against.

**Source:** Android vitals documentation (https://developer.android.com/topic/performance/vitals).

## Additional Pre-Submission & Metadata Checks

### LCH-25 [HIGH] Support URL Live and Accessible

**Detect:** Scan store metadata + in-app configs for a support URL / support contact channel; `curl -sIL -o /dev/null -w '%{http_code}' {url}` must return `200`.

**Fix:** Publish a live, reachable support URL (or in-app contact flow backed by a monitored inbox) and add it to both store listings and in-app settings before submission.

**Impact:** A dead or missing support URL is a metadata-completeness rejection reason distinct from the privacy-policy check (LCH-01) — Apple's own guideline frames absent contact info as both a rejection risk and a legal-notice issue in some regions.

**Source:** App Store Review Guidelines (https://developer.apple.com/app-store/review/guidelines/) 1.5 (Developer Information); Play Console — How to support your app's users — https://support.google.com/googleplay/android-developer/answer/113477

---

### LCH-26 [HIGH] IAP Sandbox Purchase Flow Tested Before Submission

**Detect:** App has IAP/subscription products but no recorded evidence (in `ds/launch/submission-meta.yml` or the pre-submission audit trail) that a full sandbox purchase — initiate, complete, verify entitlement granted — was exercised on a physical device before this submission.

**Fix:** Run the complete sandbox purchase flow (Apple Sandbox Tester account / Google License Testing account) end-to-end on a real device for every offered product before submitting; record the result.

**Impact:** IAP is the one flow that cannot be exercised at all before a sandbox/license-test account exists — an untested purchase path is exactly where entitlement bugs first surface, and it surfaces during real user checkout instead of before submission.

**Source:** Apple — Testing In-App Purchases with Sandbox — https://developer.apple.com/documentation/storekit/testing-in-app-purchases-with-sandbox ; Google Play Console — Test in-app billing with application licensing — https://support.google.com/googleplay/android-developer/answer/6062777

---

### LCH-27 [HIGH] Account Deletion Flow Tested End-to-End

**Detect:** App has an account-deletion flow (LCH-09) but no recorded evidence it was exercised end-to-end — request → confirmation → account actually inaccessible/data removed — on a real device before submission.

**Fix:** Run the deletion flow to completion and verify the account can no longer sign in and the data is gone (or scheduled for removal per stated policy) before submitting; record the result.

**Impact:** A deletion flow that exists in code but was never run end-to-end is indistinguishable from a broken one the first time a reviewer or regulator relies on it — the same gap LCH-22 closes for data export, applied to deletion.

**Source:** App Store Review Guidelines 5.1.1(v) (https://developer.apple.com/app-store/review/guidelines/); Play Store Account Deletion Policy.

---

### LCH-28 [HIGH] Consent Screen and Age-Verification Tested Before Submission

**Detect:** App shows an AI-service consent modal (LCH-08) and/or an age-verification/age-gate flow, but no recorded evidence either was exercised end-to-end on a real device before submission.

**Fix:** Walk through the consent modal and age-verification/age-gate flow on a real device, confirm the correct downstream behavior (data blocked until consent given; age-restricted content blocked below the declared threshold) before submitting; record the result.

**Impact:** An untested consent or age-gate is a silent-failure risk in exactly the two areas stores actively enforce post-launch (AI disclosure, age rating) — a static presence check (LCH-08, LCH-13) confirms the UI exists, not that it actually blocks the right thing.

**Source:** App Store Review Guidelines 5.1.1(i), 5.1.2 (https://developer.apple.com/app-store/review/guidelines/); Play Store Families/Age Policy.
