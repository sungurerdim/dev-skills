# ds-compliance

Single missing privacy policy or unpatched XSS can mean fines, data breaches, or store rejection. Skill audits 158 rules across 9 compliance domains with file:line precision.

**Audit web, API, CLI, and library projects against 158 rules. Security, privacy, regulatory, web security, network, architecture, performance, i18n.**

Auto-detects project type and loads the appropriate rule set.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-compliance ~/.claude/skills/ds-compliance` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

```bash
/ds-compliance                    # full scan + fix — best judgment, recorded in the summary
/ds-compliance --ask              # full scan with interactive approval
/ds-compliance --preview          # scan and report only, no fixes applied
/ds-compliance --scope=security   # single domain
/ds-compliance --secrets-migrate  # rotation / vault walkthrough for hardcoded secrets
```

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
| a11y | WCAG 2.2 AA, semantic labels, contrast, keyboard nav |
| i18n | Internationalization, hardcoded strings |
