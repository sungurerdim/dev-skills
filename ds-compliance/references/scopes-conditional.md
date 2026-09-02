# Reference: Conditional Scopes

Consumer: ds-compliance Phase 1 (Secrets Migrate Mode, Mobile-Fallback Checks) and Phase 1 step 6 / Delegation (Transactional Messaging, A9 Ecosystem Rules). Each section below loads only when its own activation signal is present — zero checks, zero cost, when absent.

## Mobile-Fallback Checks (`/ds-mobile` absent)

Runs in addition to [rules-compliance.md](rules-compliance.md) when a mobile project is detected and `/ds-mobile` is not installed (Phase 1 step 6):

| Check | Detect | Impact |
|-------|--------|--------|
| Platform manifest permissions | `AndroidManifest.xml` `uses-permission` list / `Info.plist` usage-description keys not matching declared feature use | An over-broad permission is both a privacy finding and a store-review rejection risk |
| Mobile secure-storage APIs | Credentials or tokens held outside Keychain (iOS) / Keystore (Android) | Plaintext credential storage on-device is recoverable by anyone with filesystem access |
| Store privacy-label consistency | PRV-18 crosscheck — a stated data-collection label not matching actual code behavior | A store-facing privacy label is itself a compliance declaration; a mismatch is a misrepresentation, not just an internal gap |
| iOS Privacy Manifest completeness | App or any bundled SDK missing `PrivacyInfo.xcprivacy`, or omitting required-reason API declarations / collected data types / tracking domains | Apple requires this file since May 2024; App Store Connect rejects incomplete manifests — a missing manifest blocks release outright |

**Source:** Apple Privacy Manifests — https://developer.apple.com/documentation/bundleresources/privacy_manifest_files

## Secrets Migrate Mode (`--secrets-migrate`)

Per hardcoded secret detected in security scope:

1. **Surface** — file:line, redacted fragment (first 4 chars + `***`), kind (API key / token / password / webhook URL / etc.).
2. **Ask per secret:**
   - **Rotate first?** Exposed in git history? `Yes` → require rotation before vault migration; propose provider-specific path ({provider-rotation-flow}: e.g. AWS IAM, Stripe dashboard, GitHub token settings).
   - **Destination vault?** `env (local)` / `.env.example + CI secret store` / `HashiCorp Vault` / `AWS Secrets Manager` / `GCP Secret Manager` / `Azure Key Vault` / `cloud provider native` / `other`.
   - **Migration path?** Show replacement snippet: `const {var} = process.env.{ENV_KEY}` (or stack equivalent) + config file update (`.env.example` entry, CI secret declaration).
3. **Apply** — replace hardcoded with reference, add `.env.example` placeholder entry, README line pointing at vault, and (if `gh` supported) add GitHub Action secret with blank value for user to populate.
4. **Git history** — secret ever committed → propose `git-filter-repo` surgery as Category B. Autonomous history rewrite is forbidden.

Every secret is its own needs-approval item, and secret rotation/migration matches the publish/irreversible exception list (rotating/transmitting a real credential) — never decided automatically, default or `--ask`. Every run lists each secret and marks it `skipped (only you can do)` until the human acts.

## Transactional Messaging

**Activate when:** messaging SDK/provider dependency, a consent field in the schema, or reminder-scheduling code is detected — those three signals are the whole activation contract, evaluated here. Zero checks when absent. ds-blueprint installed alongside → its `references/detection.md` § Step 5 carries the fuller provider-signal catalog; absent → the three signals above stand alone, no capability lost.

| Check | Rule |
|-------|------|
| Consent capture | Explicit opt-in recorded per channel (SMS/WhatsApp/email/push) with timestamp, distinct from general account creation |
| Lawful basis | Transactional-only messages (appointment reminders, receipts) map to legitimate interest/contract performance; marketing content in the same channel requires separate consent (KVKK Art. 5, GDPR Art. 6) |
| Opt-out mechanism | STOP/unsubscribe honored within the regulation-mandated window (immediate for SMS per most carrier rules) |
| Provider disclosure | Privacy policy names the messaging provider(s) and what data is shared (phone number, message content) — cross-ref PRV-15 Data Processing Agreement |

## A9 — Google / Apple Ecosystem Rules

**Activate when:** blueprint profile `Integrations` field is `google-workspace` or `apple-ecosystem`. Zero checks when absent.

| Provider | Rule | Scope |
|----------|------|-------|
| Google | Google API Limited Use policy compliance — data from restricted scopes cannot be transferred to AI/ads/analytics | privacy |
| Google | Data-disclosure label ↔ API usage consistency — every declared data type collected via Google APIs matches the actual scope usage | privacy |
