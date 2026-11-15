# Signals — what the project is, so a run loads only what applies

Resolved once per run (by `ds-audit`, or by any skill that needs them) with the detection column below; never guessed. They decide which `core/rules/` files are read (`core/rules/README.md`).

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

## Use

- Absent key = `unknown`. `unknown` never silently excludes a scope: the scope runs and the summary names the unresolved signal.
- A scope whose signal is detected absent is reported once: `N/A — {key}=none`.
- Echo the resolved `Signals:` line in the report so a wrong detection is visible.
