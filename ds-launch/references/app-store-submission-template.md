# App Store Submission Notes — Proactive Template

> **Currency rule:** the dated facts in this file (policy names, thresholds, fines, dates, review guidelines) are a verified seed map, never the authority. At run time, re-verify any fact that affects a finding against the live official source (store guideline page, regulator text, platform changelog); the live source wins on conflict. Web access unavailable → apply the seed and mark the finding `unverified-currency`.

> **Why proactive:** Apple App Review reviewers send Guideline 2.1 information requests an average of **2 hours after submission** for AI-using apps. Each round-trip costs **+24-48 hours** in the review queue. Apps that supply this information **upfront** (in the original App Review Information → Notes field) skip the round-trip entirely.
> Source: Indie maker [@oozn](https://x.com/oozn) confirmed pattern in TR indie community 2026-04. Apple's own [App Review documentation](https://developer.apple.com/app-store/review/) also recommends proactive disclosure.

This skill generates a project-specific version of this template. The output goes into:
- **Apple:** App Store Connect → My Apps → [App] → "App Review Information" → Notes
- **Google Play:** Play Console → "App content" → "App access" + "Data safety" notes

---

## Generic Template Structure

```
=== {{APP_NAME}} Submission Notes ===
Version: {{VERSION}}
Build: {{BUILD}}
Submission date: {{DATE}}

----------------------------------------------------------------
1) APP PURPOSE
----------------------------------------------------------------
{{ONE_PARAGRAPH_PURPOSE}}
Target audience: {{AUDIENCE}}
Primary differentiator: {{DIFFERENTIATOR}}
Languages supported: {{LANGUAGES}}

----------------------------------------------------------------
2) HOW TO REVIEW
----------------------------------------------------------------
Screen recording: {{RECORDING_URL}}
The recording shows:
  a) App launch + permission prompts
  b) Sign-in flow ({{AUTH_PROVIDERS}})
  c) Core feature flow
  d) {{IF_HAS_IAP}}Purchase flow (sandbox){{/IF}}
  e) {{IF_HAS_UGC}}Content reporting + blocking flows{{/IF}}
  f) Account deletion flow

Quick test path: {{QUICK_TEST_STEPS}}

----------------------------------------------------------------
3) DEMO / TEST CREDENTIALS
----------------------------------------------------------------
{{IF_HAS_LOGIN}}
Pre-provisioned reviewer account:
  Email:    {{REVIEW_EMAIL}}
  Password: {{REVIEW_PASSWORD}}
  Pre-loaded: {{PRE_LOADED_BENEFITS}}
{{ELSE}}
No login required — app fully functional anonymously.
{{/IF}}

----------------------------------------------------------------
4) EXTERNAL SERVICES, DATA PROVIDERS, AI SERVICES
----------------------------------------------------------------
Authentication:
  {{AUTH_PROVIDERS_DETAIL}}

Payment processors:
  {{PAYMENT_PROCESSORS}}
  No external payment links. Apple Guideline 3.1.1 compliant.

AI / ML services:
{{FOR_EACH_AI_SERVICE}}
  - {{MODEL_NAME}}
    License:  {{LICENSE}}
    Source:   {{REPO_URL}}
    Use:      {{USE_DESCRIPTION}}
    Hosting:  {{HOSTING_LOCATION}}
{{/FOR_EACH_AI_SERVICE}}

{{IF_NO_THIRD_PARTY_AI}}
No data is sent to third-party AI providers. All inference happens
on infrastructure controlled by us / on-device.
{{/IF}}

Other backend services:
  {{OTHER_SERVICES}}

----------------------------------------------------------------
5) DATA HANDLING
----------------------------------------------------------------
{{DATA_HANDLING_PARAGRAPH}}
Account deletion: {{DELETION_PROCEDURE}}

Full breakdown: {{LINK_TO_PRIVACY_LABELS_DOC}}

----------------------------------------------------------------
6) REGIONAL DIFFERENCES
----------------------------------------------------------------
{{REGIONAL_DIFFERENCES_OR_NONE}}

----------------------------------------------------------------
7) REGULATED INDUSTRY
----------------------------------------------------------------
{{REGULATED_OR_NA}}

----------------------------------------------------------------
8) CONTACT
----------------------------------------------------------------
Reviewer-only contact: {{REVIEW_CONTACT_EMAIL}}
Standard support: {{SUPPORT_EMAIL}}
Response SLA: {{SLA_HOURS}} business hours
=== End of submission notes ===
```

---

## Skill Generation Rules

When `/ds-launch --submission-notes` is invoked:

### Detect

| Variable | Detection method |
|----------|-----------------|
| `APP_NAME` | `package.json` name, `pubspec.yaml` name, Info.plist `CFBundleDisplayName` |
| `VERSION` / `BUILD` | platform manifests |
| `AUTH_PROVIDERS` | scan for OAuth/OIDC client IDs, Sign in with Apple capability, Firebase Auth |
| `IAP` presence | StoreKit imports, Google Play Billing dependency |
| `UGC` presence | text input + storage + share/upload patterns |
| `AI_SERVICES` | scan `requirements.txt`, `pubspec.yaml`, `package.json`, code imports for `transformers`, `whisper`, `openai`, `anthropic`, `langchain`, `replicate`, etc. **For each detected: prompt user to confirm name + license + hosting** |
| `LANGUAGES` | i18n string files / locale resources |
| `DELETION_PROCEDURE` | search for "delete account", "account deletion" UI flow |

### Required user input (interactive prompts)

Skill MUST ask these — they cannot be reliably auto-detected:

1. **Reviewer-only contact email** (different from public support)
2. **Screen recording URL** (warn if missing — recording is high-leverage)
3. **For each detected AI service:** confirm hosting location ("our infrastructure" vs "third-party API"). License auto-detected from package metadata, but user must confirm.
4. **Regional differences:** "Are there any?" Default → "consistent across all regions".
5. **Regulated industry:** Default → "N/A". Prompt for credentials if user opts in.

### Output paths

- Generated notes: `ds/launch/submission-notes-{{platform}}.txt`
- YAML metadata for re-runs: `ds/launch/submission-meta.yml`

---

## Common Rejection Cookbook (Ready-Made Replies)

These are the top 5 reject reasons. Each has a copy-paste reply that references back to the original submission notes.

### Guideline 2.1 — App Completeness / Information Needed

**Reviewer says:** "We need additional information to continue review. Describe AI services, regional differences, regulated industry credentials."

**Reply:**
> All of these were addressed in the original submission's App Review Notes. For your convenience, I'm copying them again below:
>
> [Paste sections 1, 4, 6, 7 from original submission notes]
>
> Please let me know if any item needs further clarification.

### Guideline 5.1.1(v) — Account Deletion

**Reviewer says:** "App must support account deletion in-app."

**Reply:**
> Account deletion is implemented at {{LOCATION}}. The flow is shown in the screen recording at timestamp {{TIMESTAMP}}. The backend wipes all account records within 24 hours; local data is deleted by the client at confirmation. See section 5 of the App Review Notes.

### Guideline 3.1.1 — In-App Purchase

**Reviewer says:** "App appears to use payment outside of IAP."

**Reply:**
> All purchases use {{PAYMENT_PROCESSORS}}. There are no external payment links, no web checkout, no crypto, no donations. See section 4 of the App Review Notes.

### Guideline 4.8 — Sign-In Services

**Reviewer says:** "App must offer Sign in with Apple alongside other social logins."

**Reply:**
> Sign in with Apple is offered as the primary option, alongside {{OTHER_PROVIDERS}}. See screen recording timestamp {{TIMESTAMP}}.

### Guideline 5.1.2 — Transparent Data Collection

**Reviewer says:** "Data collection appears non-transparent."

**Reply:**
> Per our Privacy Nutrition Label and the consent screen at first launch (timestamp {{TIMESTAMP}}): data collected is {{LIST}}. All disclosed before the user grants permission. See section 5 of the App Review Notes and our `privacy-labels.md`.

### Guideline 5.1.1(i) — AI Service Consent (NEW 2025)

**Reviewer says:** "App uses external AI services without proper consent disclosure."

**Reply:**
> The app uses the following AI services: {{LIST_WITH_PROVIDER_AND_DATA_TYPES}}. Each is disclosed in the consent modal shown at timestamp {{TIMESTAMP}} before any audio/text/image is uploaded. The user can decline and use only on-device features. See section 4 of the App Review Notes.

---

## Pre-Submission Self-Audit (mandatory — before any submit)

The skill evaluates each item as PASS/FAIL:

- [ ] **Account deletion flow** reachable in-app (Guideline 5.1.1(v))
- [ ] **Privacy Policy URL** live + contains KVKK/GDPR/CCPA sections (HTTP 200 verify)
- [ ] **Support URL** live, with a real monitored email behind it
- [ ] **Privacy Manifest** (`PrivacyInfo.xcprivacy`) present in the iOS bundle
- [ ] **Required Reason API** declarations complete
- [ ] **Apple Sign-In** (mandatory if any 3rd-party social login exists — Guideline 4.8)
- [ ] **IAP sandbox** real purchase flow tested
- [ ] **Backend production** up (the reviewer will perform real transactions)
- [ ] **Crash-free** for the last 50 sessions (on TestFlight/Play Internal)
- [ ] **Screen recording** captured (60-90 s, 1080p, MP4 H.264)
- [ ] **Demo account credentials** generated (single-use)
- [ ] **AI services list** complete, with license/source URLs verified

If any CRITICAL item is missing, the skill stops the submission and reports the gaps.

---

## Screen Recording Shot List (mandatory for Apple Guideline 2.1)

| # | Shot | Duration | Detail |
|---|------|----------|--------|
| 1 | App launch | 2-3 s | Splash → home |
| 2 | Sign-in flow (each provider) | 8-10 s each | Native OIDC dialogs must be visible |
| 3 | Sensitive permission prompts | 3 s each | Mic / Camera / Location / Contacts |
| 4 | Core feature flow | 10-30 s | Main workflow end-to-end |
| 5 | Paid content / IAP flow | 15-20 s | Sandbox purchase + balance update |
| 6 | UGC: report + block | 5 s each | Mandatory if user-generated content exists |
| 7 | History / saved data view | 3 s | Previously created work |
| 8 | **Account deletion flow** | 10 s | Settings → Delete Account → confirm |

Total: 60-120 seconds, 1080p, MP4 (H.264). Upload: TestFlight build attachment or unlisted YouTube link.

iOS recording: QuickTime Player → New Movie Recording → Camera dropdown → iPhone.
Android recording: `adb shell screenrecord --bit-rate 8000000 /sdcard/{{APP_NAME}}-flow.mp4`.

---

## Google Play Adaptation

Google Play has no **App Review Notes** field. Use these equivalents instead:

| Apple field | Google Play equivalent |
|-------------|------------------------|
| App Review Notes | "App access" → "All functionality available" + Test Account Credentials |
| Privacy Nutrition Label | "Data safety" form |
| Sign-In Information | "Test Account Credentials" |
| Demo Account Required | "Login required" toggle |

Additional Google-specific requirements:
- **Ephemeral** toggle in the "Data safety" form (when nothing persists server-side)
- Permissions Declaration (in the Manifest) — a use-case explanation is mandatory for `RECORD_AUDIO` / `CAMERA` / `LOCATION`

---

## Re-Submission Workflow

On a rejection:

1. Extract the exact guideline the reviewer references (in the email, in `Guideline X.Y.Z` format)
2. Copy the matching ready-made reply from this file's "Common Rejection Cookbook" section
3. **If the reject is information-only** → "Reply", paste the ready-made answer + note "no code change in this resubmission"
4. **If the reject requires a code change** → fix → new build → new TestFlight/Internal upload → in the re-submission notes field: `RESUBMISSION — {{REJECT_REASON}}. Addressed by: {{CHANGE}}. See section X of original submission notes.`

---

## Versioning

Update `ds/launch/submission-meta.yml` on every release:

```yaml
version: "1.0.0"
build: 42
submission_date: "2026-05-15"
screen_recording_url: "https://..."
ai_services_changes_since_last:
  added: []
  removed: []
  updated: []
binary_size_mb: 38
new_required_reason_apis: []
known_review_concerns: []
backend_production_health: green
sandbox_iap_verified: true
```

`ds/launch/submission-meta.yml` is kept under version control (Category B — committed, audit trail).

---

## Sources

- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Account deletion guide: https://developer.apple.com/news/?id=12m9d7yq
- Required Reason API list: https://developer.apple.com/documentation/bundleresources/privacy_manifest_files/describing_use_of_required_reason_api
- Privacy Manifest spec: https://developer.apple.com/documentation/bundleresources/privacy_manifest_files
- Google Play Policy Center: https://play.google.com/console/about/policy/
- AI service consent (NEW 2025): App Store guideline 5.1.1(i) update
- Indie maker @oozn proactive submission insight (2026-04, TR community)
