# App Store Submission Notes — Proactive Template

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

## Common Rejection Cookbook (Hazır Cevaplar)

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

## Pre-Submission Self-Audit (zorunlu — submit edilemeden önce)

Skill bu maddeleri PASS/FAIL ile değerlendirir:

- [ ] **Account deletion flow** in-app erişilebilir (Guideline 5.1.1(v))
- [ ] **Privacy Policy URL** canlı + KVKK/GDPR/CCPA bölümleri var (HTTP 200 verify)
- [ ] **Support URL** canlı, gerçek e-posta yanıtlanıyor
- [ ] **Privacy Manifest** (`PrivacyInfo.xcprivacy`) iOS bundle'da
- [ ] **Required Reason API** beyanları tam
- [ ] **Apple Sign-In** (3rd-party social login varsa zorunlu — Guideline 4.8)
- [ ] **IAP sandbox** gerçek satın alma akışı test edildi
- [ ] **Backend production** çalışıyor (review reviewer gerçek transaction yapacak)
- [ ] **Crash-free** son 50 oturum (TestFlight/Play Internal'da)
- [ ] **Screen recording** çekildi (60-90 sn, 1080p, MP4 H.264)
- [ ] **Demo account credentials** üretildi (tek kullanımlık)
- [ ] **AI services list** tam ve lisans/kaynak URL'leri doğrulandı

CRITICAL eksiklik varsa SKILL submit etmeyi durdurur ve eksiklikleri raporlar.

---

## Screen Recording Şot Listesi (Apple Guideline 2.1 zorunlu)

| # | Kare | Süre | Detay |
|---|------|------|-------|
| 1 | App launch | 2-3 sn | Splash → home |
| 2 | Sign-in flow (her provider) | 8-10 sn each | OIDC native diyalogları görünmeli |
| 3 | Hassas izin prompt'ları | 3 sn each | Mic / Camera / Location / Contacts |
| 4 | Core feature flow | 10-30 sn | Ana iş akışı end-to-end |
| 5 | Paid content / IAP flow | 15-20 sn | Sandbox satın alma + balance update |
| 6 | UGC: report + block | 5 sn each | Kullanıcı içeriği varsa zorunlu |
| 7 | History / saved data view | 3 sn | Daha önce yapılmış iş |
| 8 | **Account deletion flow** | 10 sn | Settings → Delete Account → confirm |

Toplam: 60-120 saniye, 1080p, MP4 (H.264). Yükleme: TestFlight build attachment veya unlisted YouTube link.

iOS kayıt: QuickTime Player → New Movie Recording → Camera dropdown → iPhone.
Android kayıt: `adb shell screenrecord --bit-rate 8000000 /sdcard/{{APP_NAME}}-flow.mp4`.

---

## Google Play Adaptation

Google Play **App Review Notes** alanı yok. Bunun yerine:

| Apple field | Google Play karşılığı |
|-------------|----------------------|
| App Review Notes | "App access" → "All functionality available" + Test Account Credentials |
| Privacy Nutrition Label | "Data safety" form |
| Sign-In Information | "Test Account Credentials" |
| Demo Account Required | "Login required" toggle |

Ek Google'a özgü gereksinimler:
- "Data safety" formunda **Ephemeral** toggle (server'da kalıcı yoksa)
- Permissions Declaration (Manifest'te) `RECORD_AUDIO` / `CAMERA` / `LOCATION` için use case açıklaması zorunlu

---

## Re-Submission Workflow

Reject geldiyse:

1. Reviewer'ın tam olarak hangi guideline'a refere ettiğini çıkar (e-posta'da Guideline X.Y.Z formatında)
2. Bu dosyanın "Common Rejection Cookbook" bölümünden ilgili hazır cevabı kopyala
3. **Reject yalnızca bilgi eksikliği** ise → "Reply" et, hazır cevabı yapıştır + "no code change in this resubmission" not düş
4. **Reject kod değişikliği gerektiriyorsa** → düzelt → yeni build → yeni TestFlight/Internal upload → re-submission notes alanına: `RESUBMISSION — {{REJECT_REASON}}. Addressed by: {{CHANGE}}. See section X of original submission notes.`

---

## Versiyonlama

Her release'de `ds/launch/submission-meta.yml` güncelle:

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

`ds/launch/submission-meta.yml` versiyon kontrolünde tutulur (Category B — komitlenmiş, audit trail).

---

## Sources

- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Account deletion guide: https://developer.apple.com/news/?id=12m9d7yq
- Required Reason API list: https://developer.apple.com/documentation/bundleresources/privacy_manifest_files/describing_use_of_required_reason_api
- Privacy Manifest spec: https://developer.apple.com/documentation/bundleresources/privacy_manifest_files
- Google Play Policy Center: https://play.google.com/console/about/policy/
- AI service consent (NEW 2025): App Store guideline 5.1.1(i) update
- Indie maker @oozn proactive submission insight (2026-04, TR community)
