---
name: ds-compliance
description: Security and regulatory compliance — OWASP, privacy laws, data protection, web security, i18n. Use when auditing for security/privacy compliance, GDPR/KVKK, or pre-release legal review.
---

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

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "GDPR/KVKK/CCPA/HIPAA audit", "regulatory compliance check" | "audit code quality" (→ ds-review) |
| "OWASP Top 10 security scan" | "fix lint errors / format" (→ ds-fix) |
| "privacy compliance audit (consent, retention, DSR)" | "design event taxonomy" (→ ds-analytics) |
| "CSP/CORS/XSS/CSRF audit" | "mobile app store privacy labels" (→ ds-mobile / ds-launch) |

## Contract

- Every finding cites file:line — never infer. Unverifiable rules skipped, not guessed. Only audits compliance; code fixes are CAT-1 (auto) or CAT-2 (approval).
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- **Mobile-project overlap-skip (OVERLAP-4 runtime enforce):** When project signals mobile (`pubspec.yaml` with `flutter:`, `package.json` with `react-native`, `*.xcodeproj`, or `build.gradle` with `android {}`), default-skip security/privacy/regulatory — owned by `/ds-mobile`. Announce: "Mobile project detected — security/privacy/regulatory delegated to /ds-mobile". Override with `--scope=security,privacy,regulatory`.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode={x}` | `audit`, `audit+fix`, `quick-fix` |
| `--scope={list}` | security, privacy, regulatory, web, network, arch, perf, i18n, or `all` |
| `--type={t}` | Override auto-detection: `web`, `api`, `cli`, `library` |
| `--secrets-migrate` | Interactive rotation / vault migration walkthrough for hardcoded secrets |
| `--resume` | Resume from `ds/audit/compliance.json` without prompting |
| `--clean` | Delete existing state, start fresh |

Without flags: present mode selection.

### Secrets Migrate Mode (`--secrets-migrate`)

Per hardcoded secret detected in security scope:

1. **Surface** — file:line, redacted fragment (first 4 chars + `***`), kind (API key / token / password / webhook URL / etc.).
2. **Ask per secret:**
   - **Rotate first?** Exposed in git history? `Yes` → require rotation before vault migration; propose provider-specific path ({provider-rotation-flow}: e.g. AWS IAM, Stripe dashboard, GitHub token settings).
   - **Destination vault?** `env (local)` / `.env.example + CI secret store` / `HashiCorp Vault` / `AWS Secrets Manager` / `GCP Secret Manager` / `Azure Key Vault` / `cloud provider native` / `other`.
   - **Migration path?** Show replacement snippet: `const {var} = process.env.{ENV_KEY}` (or stack equivalent) + config file update (`.env.example` entry, CI secret declaration).
3. **Apply** — replace hardcoded with reference, add `.env.example` placeholder entry, README line pointing at vault, and (if `gh` supported) add GitHub Action secret with blank value for user to populate.
4. **Git history** — secret ever committed → propose `git-filter-repo` surgery as Category B. Autonomous history rewrite is forbidden.

Every secret is its own needs-approval item. `--auto` lists them, marks all `skipped (needs-approval)`.

## Scopes

| Scope | What It Covers |
|-------|---------------|
| security | OWASP Top 10, secrets, TLS, input validation |
| privacy | Data collection, consent, retention, PII handling |
| regulatory | GDPR, CCPA, KVKK, LGPD, PIPL, UK GDPR, HIPAA, framework-specific |
| web | CSP, CORS, XSS, CSRF prevention |
| a11y | WCAG 2.2 AA, semantic labels, contrast, keyboard nav |
| i18n | Locale support, RTL, number/date formatting |

## Delegation

**Owns:** regulatory, privacy (canonical — GDPR / KVKK / CCPA / etc.), a11y-regulatory-framing (ADA / EN301549 mapping), security-regulatory, i18n, secrets-migrate (`--secrets-migrate`) | **Delegates:** ds-mobile → security/privacy/regulatory when mobile detected (`pubspec.yaml` / `Info.plist` / `AndroidManifest.xml`); ds-frontend → a11y implementation + fixes; ds-analytics → event-property PII scan | **Receives:** ds-ship → Phase 2 regulatory pass

## Execution Flow

```
Detect → Configure → Scan → Report → [Fix] → [Needs-Approval] → Summary
```

### Phase 1: Detect

**Recovery check:** DETECT `ds/audit/compliance.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read files for pending findings, discard stale), skip `done` phases, announce `[CMP] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start.

**State `data`:** `{ mode, scopes_selected, scopes_done[], regulations_resolved[], findings[{id, severity, file, line, scope, cat, disposition}], fix_progress }`.

1. **IDU:** Profile → Config.regulations, Config.data, Config.audience, Type+Stack. Findings(compliance scopes) → verify + use. Absent → own analysis.

2. **Project detection.** Search for config to identify type:
   - **Web frontend:** `package.json` with react/next/vue/nuxt/angular/svelte/astro
   - **API/backend:** express/fastify/nestjs, fastapi/django/flask, go.mod with gin/echo, Cargo.toml with actix/axum, spring-boot
   - **CLI/library:** bin field, commander/yargs/click/cobra/clap, or library exports without bin
   - Override with `--type` if auto-detection wrong

3. **Stack detection.** Framework, language, architecture pattern, auth, DB, ORM, API style, testing, CI/CD, i18n, deployment.

4. **Mode selection.** No `--mode` → ask: Audit Only / Audit & Fix / Quick Fix.

5. **Scope selection.** No `--scope` → ask which domains (default: all applicable). Regulatory scope: detect frameworks (GDPR, KVKK, CCPA, etc.) from codebase patterns, confirm.

6. **Overlap routing (runtime enforcement — OVERLAP-1, -2, -4):**
   - **Mobile project detected** (`pubspec.yaml` with `flutter:` OR `Info.plist` OR `AndroidManifest.xml`) → invoke `/ds-mobile --scope=security,privacy,regulatory`, wait for completion, read its `ds/audit/findings.md` updates, remove `security/privacy/regulatory` from active scope. Keep only non-mobile-covered scopes (a11y, i18n, web, network, perf, arch) locally. Rationale: ds-mobile authoritative; running both duplicates findings.
   - **a11y scope active + project has frontend** (framework detected in `package.json` / equivalent) → announce delegation: "a11y implementation + fixes delegated to /ds-frontend. This run keeps regulatory framing only (ADA / EN301549 mapping)." Mark a11y `framing-only`; emit only regulatory-mapping findings.
   - **Privacy scope active** → canonical owner. Announce: "/ds-launch --privacy narrows to store-label-correctness; /ds-analytics --privacy-audit narrows to event-property PII scan. This run emits canonical privacy findings."

**Gate:** Project type identified; mode + scope confirmed; regulatory frameworks resolved; overlap routing applied. If fails → type undetected + no `--type` response → default `web`, announce, proceed; regulatory ambiguous after detection → present detected signals, require explicit framework selection before proceeding.

### Phase 2: Architecture Discovery

**When:** scope includes 3+ domains or `all`. Skip for narrow scans.

1. Analyze architecture (pattern, auth, DB, ORM, API style, testing, CI/CD, i18n, deployment).
2. Present detected architecture for confirmation.
3. Classify rules:
   - **CAT-1 Conformance:** universal best practice, existing pattern misused, bug, security flaw — auto-fixable
   - **CAT-2 Enhancement:** new layers/patterns not in current architecture — needs approval
4. Present enhancement opportunities, ask which to include (default: none).

**Gate:** Architecture confirmed; every rule classified CAT-1 / CAT-2; approved enhancements finalized. If fails → user unconfirmed (no response or rejection) → re-present detected architecture with brief explanation, ask once more; still unconfirmed → proceed with auto-detected, add WARN: `"Architecture unconfirmed — CAT-2 classifications may be inaccurate"` in state.data.

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

**Gate:** All reference files for in-scope domains loaded; unloadable marked N/A. If fails → file missing → mark domain `N/A` in state.data.scopes_done, continue with available, surface missing path in report.

### Phase 4: Scan

Per in-scope domain:

1. Search for relevant files.
2. Search contents for violation patterns.
3. Read files to verify findings in context.
4. Skip rules that cannot be verified.
5. **Defense-in-depth check ([references/principles.md §5](references/principles.md)):** flag when only one control layer is detected for a sensitive operation (e.g. input validation present but no output encoding AND no auth layer). Single-control reliance is itself a finding regardless of how strong that control is.

**Confidence:** HIGH = match + context verified. MEDIUM = pattern, ambiguous. LOW = heuristic.

**False-positive prevention:** check surrounding context. Never flag `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING`, test fixtures.

**Large scope (3+ domains):** numbered progress checklist + append findings to `ds/audit/findings.md` (add to `.gitignore`) — file exists with fresh `git_hash` → preserve findings from other scopes, append only your own. After each domain scan, append. Enables recovery on context loss.

**Gate:** Every in-scope domain scanned; findings recorded with severity + confidence. If fails → domain(s) un-scan-able (no scannable source, access denied, reference N/A) → mark `inconclusive` in state.data.findings, continue with successful ones, list skipped domains in Phase 5 report.

### Phase 5: Report

```
## Audit Report — {project-name}
Stack: {stack} | Scanned: {domains} | Date: {today}
Architecture: {detected-summary}

### Conformance Issues (CAT-1)
| # | Rule | Sev | File:Line | Issue | Impact | Fix | Conf |

### Enhancement Opportunities (CAT-2) — pre-approved
| # | Rule | Sev | File:Line | Issue | Impact | Fix | Conf |

### Potential Issues (LOW confidence)
| # | Rule | File:Line | Issue | Suggested Fix |

### Summary
| Category | CRITICAL | HIGH | MEDIUM | LOW | Total |
```

**Severity:** CRITICAL > HIGH > MEDIUM > LOW. Uncertain → choose lower.

**Gate:** Report with findings + severities + summary. If fails → findings list empty because all domains `inconclusive` or `N/A` → print report with single section `"No verifiable findings — all domains inconclusive or reference files missing"`, list domains + skip reason, exit with status `WARN`.

### Phase 6: Fix [SKIP if audit-only]

**Overwrite prevention:** before generating/modifying any compliance document (Privacy Policy, DPIA, Breach Plan, Processor Registry), check if target exists. Exists → do NOT overwrite — show diff between existing + proposed, ask: "Update existing / Keep existing / Show diff".

1. Present fix plan grouped by category (CAT-1 auto-fixable, CAT-2 pre-approved).
2. Confirmation: `quick-fix` → apply all, summary only; `audit+fix` → show plan, ask proceed/cancel; `audit` → ask which severities.
3. Apply fixes grouped by file. Different files in parallel, same file sequential.

**Gate:** All standard fixes attempted; each recorded. If fails → CAT-1 fix unappliable (file write error, merge conflict, generated doc exists + user chose "Keep existing") → record `failed` in state.data.fix_progress with specific error, continue with remaining, surface all failed IDs in Phase 8 summary.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** All items resolved (applied → fixed/failed, declined → skipped). If fails → unresolved → re-present each with forced binary prompt (Apply / Skip); user declines → mark `skipped (no response)`, proceed.

### Phase 8: Summary

```
ds-compliance: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

FRC+DSC accounting. `fixed + failed + skipped + needs_approval + not_applicable = total`.

**Gate:** Summary balances; every modified file re-read. If fails → identify findings without disposition, assign `disposition: skipped (accounting-fix)`, recompute summary, add WARN: `"{n} finding(s) auto-skipped to balance accounting"`.

**Value Delivered:** 1-5 concrete compliance outcomes. Example shapes (placeholders, not literal):

- `{n} CRITICAL secrets in source intercepted — credentials no longer leak into git history (rotation guidance attached)`
- `{regulation} compliance: {n} consent gaps, {n} retention policy gaps closed — exposure window before {audit-date} eliminated`
- `OWASP Top 10: {n} CRITICAL injection vectors flagged with {file}:{line} — fixes routed to ds-review --tactical for execution`

Zero-finding run: `Compliance scope clean — no regulatory or security findings`.

## Quality Gates

1. No cascading breakage after fixes
2. Format preservation (indentation, code style)
3. Scope boundary (only touch required lines)
4. Stack consistency (use correct framework APIs)
5. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/compliance.json` updated per scope, gitignored, deleted on successful Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for uncovered scopes. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

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
