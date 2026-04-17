# /ds-compliance

Single missing privacy policy or unpatched XSS can mean fines, data breaches, or store rejection. Skill audits 80+ rules across 8 compliance domains with file:line precision.

**Security & Regulatory Compliance** — OWASP security, privacy laws, data protection, web security, and internationalization.

## Triggers

- User runs `/ds-compliance`
- User asks about GDPR, KVKK, CCPA, HIPAA, or other regulatory compliance
- User asks to check for security vulnerabilities, secrets, or injection risks
- User asks about privacy, data protection, or consent requirements
- User asks about CSP, CORS, XSS, CSRF, or web security
- User asks about internationalization compliance

Covers 80+ rules across 8 compliance domains.

## Contract

- Every finding cites file and line — never infer or assume
- Unverifiable rules are skipped, not guessed
- Only audits compliance — code fixes are CAT-1 (auto) or CAT-2 (user approval)
- Standalone. Uses blueprint/.ds-findings.md when available; own analysis when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode=<mode>` | `audit`, `audit+fix`, `quick-fix` |
| `--scope=<domains>` | Comma-separated: security, privacy, regulatory, web, network, arch, perf, i18n, or `all` |
| `--type=<type>` | Override auto-detection: `web`, `api`, `cli`, `library` |

Without flags: present mode selection to the user.

## Scopes

| Scope | What It Covers |
|-------|---------------|
| security | OWASP Top 10, secrets, TLS, input validation |
| privacy | Data collection, consent, retention, PII handling |
| regulatory | GDPR, CCPA, KVKK, LGPD, PIPL, UK GDPR, HIPAA, and framework-specific rules |
| web | CSP, CORS, XSS, CSRF prevention |
| a11y | WCAG 2.2 AA, semantic labels, contrast, keyboard navigation |
| i18n | Locale support, RTL, number/date formatting |

## Execution Flow

Detect -> Configure -> Scan -> Report -> [Fix] -> [Needs-Approval] -> Summary

### Phase 1: Detect

1. **IDU:** Profile → Config.regulations, Config.data, Config.audience, Type+Stack. Findings(compliance scopes) → verify + use. Absent → own analysis.

2. **Project detection.** Search for config files to identify project type:
   - **Web frontend:** `package.json` with react/next/vue/nuxt/angular/svelte/astro
   - **API/backend:** express/fastify/nestjs, fastapi/django/flask, go.mod with gin/echo, Cargo.toml with actix/axum, spring-boot
   - **CLI/library:** bin field, commander/yargs/click/cobra/clap, or library exports without bin
   - Override with `--type` flag if auto-detection is wrong

3. **Stack detection.** Identify framework, language, architecture pattern, auth, database, ORM, API style, testing, CI/CD, i18n, deployment.

4. **Mode selection.** No `--mode` flag → ask user:
   - **Audit Only** — scan all domains, report only
   - **Audit & Fix** — scan, review findings, then fix
   - **Quick Fix** — scan and auto-fix, minimal review

5. **Scope selection.** No `--scope` flag → ask which domains to audit (default: all applicable).
   - For regulatory scope: detect frameworks (GDPR, KVKK, CCPA, etc.) from codebase patterns, confirm with user

**Gate:** Project type identified, mode and scope confirmed, regulatory frameworks resolved.

### Phase 2: Architecture Discovery

**When:** Scope includes 3+ domains or `all`. Skip for narrow scans.

1. Analyze codebase architecture (pattern, auth, database, ORM, API style, testing, CI/CD, i18n, deployment)
2. Present detected architecture to user for confirmation
3. Classify rules as:
   - **CAT-1 Conformance:** Universal best practices, existing patterns used incorrectly, bugs, security flaws — auto-fixable
   - **CAT-2 Enhancement:** New layers/patterns not in current architecture — requires explicit approval
4. Present enhancement opportunities, ask which to include (default: none)

**Gate:** Architecture confirmed by user, every rule classified as CAT-1 or CAT-2, approved enhancements finalized.

### Phase 3: Rule Loading

Load reference files matching scope:

| Scope | Reference File |
|-------|---------------|
| security, privacy, regulatory | [rules-compliance.md](references/rules-compliance.md) |
| web (frontend only) | [rules-web.md](references/rules-web.md) |
| security (CLI/library only) | [rules-security.md](references/rules-security.md) |
| network | [rules-network.md](references/rules-network.md) |
| arch | [rules-arch.md](references/rules-arch.md) |
| perf | [rules-perf.md](references/rules-perf.md) |
| a11y | [rules-a11y.md](references/rules-a11y.md) |
| i18n | [rules-i18n.md](references/rules-i18n.md) |

**Gate:** All reference files for in-scope domains loaded successfully; unloadable domains marked N/A.

### Phase 4: Scan

Per domain in scope, scan codebase:

1. Search for relevant files
2. Search contents for violation patterns
3. Read files to verify findings in context
4. Skip rules that cannot be verified

**Confidence:** HIGH = specific grep match + context verified, MEDIUM = pattern match, ambiguous context, LOW = heuristic only.

**False positive prevention:** Check surrounding context. Never flag: `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING` blocks, test fixtures.

**Large scope (3+ domains):** Track progress with numbered checklist. Append findings to `.ds-findings.md` in project root (add to .gitignore) — file exists with fresh `git_hash` → preserve findings from other scopes and append only your own. After each domain scan, append findings. Enables recovery if context is lost.

**Gate:** Every in-scope domain scanned, all findings recorded with severity and confidence.

### Phase 5: Report

```
## Audit Report -- [project_name]
Stack: [stack] | Scanned: [domains] | Date: [today]
Architecture: [detected summary]

### Conformance Issues (CAT-1)
| # | Rule | Sev | File:Line | Issue | Impact | Fix | Conf |

### Enhancement Opportunities (CAT-2) -- pre-approved
| # | Rule | Sev | File:Line | Issue | Impact | Fix | Conf |

### Potential Issues (LOW confidence)
| # | Rule | File:Line | Issue | Suggested Fix |

### Summary
| Category | CRITICAL | HIGH | MEDIUM | LOW | Total |
```

**Severity order:** CRITICAL > HIGH > MEDIUM > LOW. When uncertain, choose lower severity.

**Gate:** Report presented to user with all findings, severities, and summary table.

### Phase 6: Fix (skip if audit-only)

**Overwrite prevention:** Before generating or modifying any compliance document (Privacy Policy, DPIA, Breach Plan, Processor Registry), check if target file already exists. Exists → do NOT overwrite — show diff between existing content and proposed changes, ask user: "Update existing / Keep existing / Show diff".

1. Present fix plan grouped by category (CAT-1 auto-fixable, CAT-2 pre-approved)
2. Confirmation:
   - `quick-fix`: Apply all, summary only
   - `audit+fix`: Show plan, ask proceed/cancel
   - `audit`: Ask which severities to fix
3. Apply fixes grouped by file. Different files can be fixed in parallel, same file sequentially.

**Gate:** All standard fixes attempted; each recorded as applied, failed, or skipped.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 8: Summary

```
ds-compliance: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N
```

FRC+DSC accounting.

**Gate:** `fixed + failed + skipped + needs_approval + not_applicable = total`; every modified file re-read and verified.

## Quality Gates

1. No cascading breakage after fixes
2. Format preservation (indentation, code style)
3. Scope boundary (only touch required lines)
4. Stack consistency (use correct framework APIs)
5. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Regulatory framework ambiguous | List detected signals, ask user to confirm applicable frameworks |
| Rule references external policy that changed | Flag as needs-verification, use last known version |
| Fix requires architectural change | Classify as needs-approval, present to user |
| Compliance doc template generation fails | Generate partial template, list missing sections |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No source code files | Report empty scan, suggest checking path |
| Mixed project types | Detect all types, apply union of applicable rules |
| Generated code only | Skip generated files, warn if no scannable code remains |
