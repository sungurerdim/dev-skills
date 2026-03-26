# /ds-compliance

A single missing privacy policy or an unpatched XSS can mean fines, data breaches, or store rejection. This skill audits 80+ rules across 8 compliance domains with file:line precision.

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
- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- Every finding receives a disposition in the summary — zero silent drops (FRC)

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

Detect -> Configure -> Scan -> Report -> [Fix] -> Summary

### Phase 1: Detect

1. **Upstream check:** Search for `## Blueprint Profile` in known instruction files. If found:
   - **Config.regulations** → skip regulation detection, use stated frameworks (GDPR, KVKK, CCPA) directly
   - **Config.data** → know data types to scan for (PII, credentials, sensitive data)
   - **Config.audience** → public users: stricter compliance requirements
   - **Type + Stack** → skip own project detection

   **Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, read findings matching compliance scopes. Use verified findings to skip redundant analysis. If stale or absent, run own full analysis.

2. **Project detection.** Search for config files to identify project type:
   - **Web frontend:** `package.json` with react/next/vue/nuxt/angular/svelte/astro
   - **API/backend:** express/fastify/nestjs, fastapi/django/flask, go.mod with gin/echo, Cargo.toml with actix/axum, spring-boot
   - **CLI/library:** bin field, commander/yargs/click/cobra/clap, or library exports without bin
   - Override with `--type` flag if auto-detection is wrong

3. **Stack detection.** Identify framework, language, architecture pattern, auth, database, ORM, API style, testing, CI/CD, i18n, deployment.

4. **Mode selection.** If no `--mode` flag, ask the user:
   - **Audit Only** — scan all domains, report only
   - **Audit & Fix** — scan, review findings, then fix
   - **Quick Fix** — scan and auto-fix, minimal review

5. **Scope selection.** If no `--scope` flag, ask which domains to audit (default: all applicable).
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
| i18n | [rules-i18n.md](references/rules-i18n.md) |

**Gate:** All reference files for in-scope domains loaded successfully; unloadable domains marked N/A.

### Phase 4: Scan

For each domain in scope, scan the codebase:

1. Search for relevant files
2. Search contents for violation patterns
3. Read files to verify findings in context
4. Skip rules that cannot be verified

**Confidence:** HIGH = specific grep match + context verified, MEDIUM = pattern match, ambiguous context, LOW = heuristic only.

**False positive prevention:** Check surrounding context. Never flag: `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING` blocks, test fixtures.

**Large scope (3+ domains):** Track progress with a numbered checklist. Append findings to `.ds-findings.md` in project root (add to .gitignore) — if the file exists with a fresh `git_hash`, preserve findings from other scopes and append only your own. After each domain scan, append findings. This enables recovery if context is lost.

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

1. Present fix plan grouped by category (CAT-1 auto-fixable, CAT-2 pre-approved)
2. Confirmation:
   - `quick-fix`: Apply all, summary only
   - `audit+fix`: Show plan, ask proceed/cancel
   - `audit`: Ask which severities to fix
3. Apply fixes grouped by file. Different files can be fixed in parallel, same file sequentially.
4. Present fix summary: `ds-compliance: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N`

**FRC accounting:** Every finding from the audit/analyze phase appears with a disposition (fixed, failed, skipped, needs-approval, not-applicable). `fixed + failed + skipped + needs_approval + not_applicable = total`.

**Gate:** `fixed + failed + skipped + needs_approval + not_applicable = total`; every modified file re-read and verified.

## Quality Gates

1. No cascading breakage after fixes
2. Format preservation (indentation, code style)
3. Scope boundary (only touch required lines)
4. Stack consistency (use correct framework APIs)

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

