# ds-compliance

Audit web, API, CLI, and library projects against 80+ rules. Security, privacy, regulatory, web security, network, architecture, performance, i18n.

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
| web | CSP, CORS, XSS, CSRF, WCAG (frontend only) |
| network | TLS enforcement, rate limiting, timeouts, cert pinning |
| arch | Audit logging, input validation, error leakage, dependency security |
| perf | Resource exhaustion, N+1 queries, memory leaks, graceful shutdown |
| i18n | Internationalization, hardcoded strings |

## Modes

| Mode | What It Does |
|------|-------------|
| **Audit Only** | Scan and report |
| **Audit & Fix** | Scan, review, then fix |
| **Quick Fix** | Scan and auto-fix |
