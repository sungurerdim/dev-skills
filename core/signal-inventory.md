# Signal Inventory — what the project is, so every skill scans only what applies

**Consumers:** ds-blueprint (producer of the `Signals:` line), every skill's scope-resolution table (which scopes run, which are N/A), ds-ship (which delegations earn their cost). A skill running alone with no profile resolves the signals itself with the detection column below — the inventory is the same either way.

## The line

```
Signals: ui=web,ios api=rest db=postgres auth=jwt billing=stripe pii=yes i18n=no tests=vitest ci=github deploy=docker platforms=web,ios audience=public jurisdiction=eu,tr integrations=stripe,sentry mobile=flutter
```

Absent key = `unknown` (the consumer detects it); `none` = detected absent. Values are lowercase tokens; multi-valued keys are comma-joined.

## Keys and detection

| Key | Values | Detect (first hit wins; all paths relative to repo root) |
|-----|--------|----------------------------------------------------------|
| `ui` | `none` · `web` · `ios` · `android` · `desktop` · `cli-tui` | HTML/JSX/TSX/Vue/Svelte/CSS files outside `node_modules` → `web`; `*.xcodeproj`/SwiftUI → `ios`; `AndroidManifest.xml`/Compose → `android`; Electron/Tauri/Flutter desktop targets → `desktop`; a TUI library dep → `cli-tui` |
| `api` | `none` · `rest` · `graphql` · `grpc` · `rpc` | Route registrations (`app.get(`, `@app.route`, `@RestController`, `router.`) → `rest`; `.graphql`/`gql` schema → `graphql`; `.proto` with services → `grpc`; tRPC/JSON-RPC deps → `rpc` |
| `db` | `none` · `postgres` · `mysql` · `sqlite` · `mongodb` · `redis` · `dynamodb` · `firestore` · `other` | Driver/ORM dep or `*_URL` scheme in `.env.example`; migrations dir → confirms |
| `auth` | `none` · `session` · `jwt` · `oauth` · `firebase` · `clerk` · `auth0` · `supabase` · `other` | Auth lib dep, `Authorization` header handling, login route, `passport`/`next-auth`/`devise` |
| `billing` | `none` · `stripe` · `paddle` · `lemonsqueezy` · `store-iap` · `revenuecat` · `other` | SDK dep, webhook route for the provider, `StoreKit`/`BillingClient`/`in_app_purchase` |
| `pii` | `yes` · `no` | Fields named email/phone/address/dob/ssn/national_id/ip in schema or models; user table; analytics SDK; contact form |
| `i18n` | `yes` · `no` | Locale files (`locales/`, `*.arb`, `*.po`, `i18n/`), `Intl`/`gettext`/`i18next`/`flutter_localizations` |
| `tests` | `none` · `{runner}` | Framework dep or test dir (`toolchains.md` per-stack Detect rows) |
| `ci` | `none` · `github` · `gitlab` · `circle` · `azure` · `other` | `.github/workflows/*.yml`, `.gitlab-ci.yml`, `.circleci/`, `azure-pipelines.yml` |
| `deploy` | `none` · `docker` · `k8s` · `serverless` · `paas` · `static` · `vps` · `store` | `Dockerfile`/`compose`, `k8s/`/Helm, `serverless.yml`/`wrangler.*`/`vercel.json`/`netlify.toml`, `Procfile`/`fly.toml`/`render.yaml`, static site config, deploy scripts with `ssh`, `fastlane/`/`eas.json` |
| `platforms` | `web` · `ios` · `android` · `desktop` · `cli` · `library` | Union of `ui` targets plus: `bin`/entrypoint without UI → `cli`; package manifest with no app entry → `library` |
| `mobile` | `none` · `flutter` · `react-native` · `expo` · `swiftui` · `compose` · `kmp` · `capacitor` | `pubspec.yaml` with `flutter:`; `react-native` dep; `app.json` with `expo`; SwiftUI imports; Compose deps; `shared/` KMP module; `capacitor.config.*` |
| `audience` | `public` · `internal` · `developers` | Public repo + landing/README marketing → `public`; SSO-only or private network → `internal`; SDK/CLI/library → `developers`. Profile `Audience:` overrides |
| `jurisdiction` | ISO country/region tokens (`eu`, `uk`, `us-ca`, `tr`, `br`, `ca-qc`, …) or `unknown` | Locale list, legal pages, privacy policy text, store listing regions, currency codes; never guessed from language alone |
| `integrations` | `none` or list | SDK deps and env var prefixes (`STRIPE_`, `SENTRY_`, `FIREBASE_`, `TWILIO_`, `SENDGRID_`, `OPENAI_`, `ANTHROPIC_`, …) |
| `public_repo` | `yes` · `no` · `unknown` | `gh repo view --json visibility` when `gh` is present; else `unknown` |
| `secrets_mgmt` | `none` · `env` · `vault` · `cloud-sm` | `.env.example` only → `env`; Vault/Doppler/1Password/AWS SM/GCP SM SDK → `cloud-sm`/`vault` |
| `size` | `small` · `medium` · `large` | Tracked source files < 200 → small; < 2000 → medium; else large |

## Scope resolution — every skill declares one

Every skill with more than one scope carries a table mapping its scopes to signals, evaluated at setup and echoed in the summary. "Scan everything" is never the default; a scope runs because a signal says it applies.

```
| Scope | Runs when | Otherwise |
|-------|-----------|-----------|
| a11y | ui ≠ none | N/A — no UI surface |
| privacy | pii=yes or auth ≠ none or integrations contain an analytics SDK | N/A — no personal data path detected |
| store | platforms ∩ {ios, android} ≠ ∅ | N/A — no store target |
```

| Outcome | Meaning | Summary token |
|---------|---------|---------------|
| ran | Signal present (or `unknown` — unknown never silently excludes; it runs the scope and reports the signal as unresolved) | `ran` |
| N/A with reason | Signal detected absent | `N/A — {signal}=none` |
| skipped — not part of this mode | Orchestrator mode leaves it out (`--mode=improve` excludes launch legs) | `skipped — not part of this mode` |
| skipped — no signal (orchestrator) | ds-ship skipped a delegation because no signal justifies it | `skipped — no signal ({signal})` |

`--scope=` overrides the table for the named scopes; `--ask` shows the resolved table before running.

## Producer rules (ds-blueprint)

1. Resolve every key; write `Signals:` into the profile and `signals:` into the findings meta.
2. `unknown` is written as such, never guessed.
3. `--refresh` re-detects all keys; a normal run re-detects only keys whose detection files changed (manifest, lockfile, config) since the profile's git hash.
