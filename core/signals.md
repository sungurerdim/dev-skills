# Signals — what the project is, so a run loads only what applies

Resolved once per run by `ds_detect.py`; never guessed. They decide which `core/rules/` files are read (`core/rules/README.md`).

## The line

```
Signals: ui=web,ios api=rest db=postgres auth=jwt billing=stripe pii=yes i18n=no tests=vitest ci=github deploy=docker platforms=web,ios audience=public integrations=stripe,sentry mobile=flutter
```

Absent key = `unknown` (the consumer detects it); `none` = detected absent. Values are lowercase tokens; multi-valued keys are comma-joined.

## Keys

Detected by `ds_detect.py signals` (this directory): one call, the same result for every skill. `By`: `file` = a file or dependency fact; `tool` = an installed CLI answered; `judge` = a heuristic shown with `?` that the model confirms by reading the code it rests on.

| Key | Values | By |
|-----|--------|----|
| `ui` | `none` · `web` · `ios` · `android` · `desktop` · `cli-tui` | file |
| `api` | `none` · `rest` · `graphql` · `grpc` · `rpc` | file |
| `db` | `none` · `postgres` · `mysql` · `sqlite` · `mongodb` · `redis` · `dynamodb` · `firestore` · `other` | file |
| `auth` | `none` · `session` · `jwt` · `oauth` · `firebase` · `clerk` · `auth0` · `supabase` · `other` | judge |
| `billing` | `none` · `stripe` · `paddle` · `lemonsqueezy` · `store-iap` · `revenuecat` · `other` | file |
| `pii` | `yes` · `no` | judge |
| `i18n` | `yes` · `no` | file |
| `tests` | `none` · runner names | file |
| `ci` | `none` · `github` · `gitlab` · `circle` · `azure` · `other` | file |
| `deploy` | `none` · `docker` · `k8s` · `serverless` · `paas` · `static` · `vps` · `store` | file |
| `platforms` | `web` · `ios` · `android` · `desktop` · `cli` · `library` | file |
| `mobile` | `none` · `flutter` · `react-native` · `expo` · `swiftui` · `compose` · `kmp` · `capacitor` | file |
| `audience` | `public` · `internal` · `developers` | judge |
| `integrations` | `none` or provider names | file |
| `public_repo` | `yes` · `no` · `unknown` | tool (`gh`) |
| `secrets_mgmt` | `none` · `env` · `vault` · `cloud-sm` | file |
| `size` | `small` (< 200 source files) · `medium` (< 2000) · `large` | file |

## Use

- Absent key = `unknown`. `unknown` never silently excludes a scope: the scope runs and the summary names the unresolved signal.
- A scope whose signal is detected absent is reported once: `N/A — {key}=none`.
- Echo the resolved `Signals:` line in the report so a wrong detection is visible.
