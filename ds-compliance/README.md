# ds-compliance

Audit web, API, CLI, and library projects against 160+ rules. Security, architecture, performance, a11y, i18n.

Auto-detects project type and loads the appropriate rule set.

## Install

See the [main README](../README.md#install) for install instructions per AI tool.

## Use

Run `/ds-compliance`, or ask to audit your project.

## Scopes

| Scope | What It Checks |
|-------|---------------|
| security | Secrets, injection, TLS, crypto, auth |
| privacy | Data minimization, consent, erasure |
| regulatory | GDPR, KVKK, CCPA, and 6 more frameworks |
| arch | Architecture patterns, coupling, DI |
| testing | Coverage, test quality |
| perf | N+1 queries, caching, resource management |
| network | API design, rate limiting |
| web | CSP, CORS, XSS, CSRF (frontend only) |
| i18n | Internationalization, hardcoded strings |

## Modes

| Mode | What It Does |
|------|-------------|
| **Audit Only** | Scan and report |
| **Audit & Fix** | Scan, review, then fix |
| **Quick Fix** | Scan and auto-fix |
