# Secret Patterns — filename exclusions and content regexes

**Consumers:** ds-commit and ds-pr (staging exclusion), ds-fix and ds-review (content scan), ds-compliance (secrets scope), ds-issue and ds-build (pre-commit scan), any skill that stages files or scans source.

## Filename set — always excluded from bulk staging

Canonical, carried in full by every consumer; a partial copy is drift, and the missed pattern is the one that leaks.

`.env`, `.env.*`, `*.pem`, `*.key`, `credentials.*`, `secrets.*`

Also excluded when present: `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `id_rsa`, `id_ed25519`, `*.ovpn`, `serviceAccount*.json`, `google-services.json` with a non-placeholder `api_key`, `.npmrc`/`.pypirc` containing `_authToken`/`password`.

The exclusion is filename-based, never content-based: a user who names a matching file explicitly (`git add {file}`, `--staged-only` after staging it) has it staged exactly as asked. Every excluded file is listed in the summary.

## Content regexes — scanned in the working tree, the diff, and the commit message

Exclude `.git/`, `node_modules/`, `build/`, `dist/`, `.dart_tool/`, `vendor/`, `__pycache__/`, `bin/`, `obj/`, `_build/`, `deps/`, `.terraform/`, `target/`, lockfiles, and `*.example` files.

| Pattern | Matches |
|---------|---------|
| `AKIA[0-9A-Z]{16}` | AWS access key id |
| `(?i)(aws_secret_access_key\|secret_access_key)\s*[=:]\s*["']?[A-Za-z0-9/+=]{40}` | AWS secret key |
| `(?i)(api_key\|api_secret\|secret_key\|access_token\|auth_token\|client_secret\|password\|passwd)\s*[=:]\s*["'][^"'${}]{8,}` | Generic assignment — a quoted literal ≥ 8 chars that is not a `${VAR}` placeholder |
| `-----BEGIN (RSA \|EC \|DSA \|OPENSSH \|PGP )?PRIVATE KEY-----` | Private key block |
| `sk-[A-Za-z0-9_-]{20,}` | OpenAI / Anthropic API key (`sk-proj-…`, `sk-ant-…`) |
| `sk_(live\|test)_[A-Za-z0-9]{10,}` | Stripe secret key |
| `rk_(live\|test)_[A-Za-z0-9]{10,}` | Stripe restricted key |
| `AIza[0-9A-Za-z_-]{35}` | Google API key |
| `ghp_[A-Za-z0-9]{36}` | GitHub personal access token (classic) |
| `github_pat_[A-Za-z0-9_]{22,}` | GitHub PAT (fine-grained) |
| `gh[oursp]_[A-Za-z0-9]{36}` | GitHub OAuth/user/server/refresh tokens |
| `xox[baprs]-[A-Za-z0-9-]+` | Slack token |
| `glpat-[A-Za-z0-9_-]{20,}` | GitLab PAT |
| `(?i)(mongodb(\+srv)?\|postgres(ql)?\|mysql\|redis\|amqp)://[^:\s]+:[^@\s]{4,}@` | Connection URL with embedded password |
| `eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}` | JWT literal (flag in source and config only; ignore in tests named `*jwt*`) |
| `(?i)-----BEGIN CERTIFICATE-----` | Certificate — LOW unless paired with a key |

A match is CRITICAL after the second pass in `severity-score-categories.md` (re-read ±20 lines; skip fixtures, `*.example`, documented placeholders such as `sk-live-0000…`). Secrets are **never auto-fixed** — the finding reports the site, states "rotate this credential now, then add the variable name with a placeholder value to `.env.example`", and the run's status is FAIL until the owner acts.

## Scanner augmentation (advisory, zero-dependency baseline stays)

| Tool present | Use |
|--------------|-----|
| `gitleaks` | `gitleaks dir . --no-banner --redact=60` alongside the regexes; merge by `file:line`. |
| `trufflehog` | Offer a verified scan for CRITICAL triage — its verifiers tell a live credential from an expired one. Never probe a credential yourself. |
| Neither | The regex table above stands alone. |

History check for every hit: `git log --all --oneline -- {file}` and `git log -S'{fragment}' --all` — a secret already in history needs rotation even after the working-tree fix; rewriting history is the owner's call.
