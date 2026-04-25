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
- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode=<mode>` | `audit`, `audit+fix`, `quick-fix` |
| `--scope=<domains>` | Comma-separated: security, privacy, regulatory, web, network, arch, perf, i18n, or `all` |
| `--type=<type>` | Override auto-detection: `web`, `api`, `cli`, `library` |
| `--secrets-migrate` | Interactive rotation / vault migration walkthrough for every hardcoded secret found |
| `--resume` | Resume from `ds/audit/compliance.json` without prompting |
| `--clean` | Delete existing state and start fresh |

Without flags: present mode selection to the user.

### Secrets Migrate Mode (`--secrets-migrate`)

Per hardcoded secret detected in the security scope:

1. **Surface** — show file:line, redacted fragment (first 4 chars + `***`), and the kind (API key / token / password / webhook URL / etc.).
2. **Ask per secret:**
   - **Rotate first?** Has this secret been exposed in git history? `Yes` → require rotation before vault migration; propose rotation path (provider-specific: AWS IAM, Stripe dashboard, GitHub token settings, etc.).
   - **Destination vault?** `env (local)` / `.env.example + CI secret store` / `HashiCorp Vault` / `AWS Secrets Manager` / `GCP Secret Manager` / `Azure Key Vault` / `cloud provider native` / `other`.
   - **Migration path?** Show the replacement snippet: `const apiKey = process.env.STRIPE_SECRET_KEY` (or stack equivalent) + the config file update (`.env.example` entry, CI secret declaration).
3. **Apply** — replace the hardcoded value with the reference, add an entry to `.env.example` with placeholder, add a README line pointing at the vault, and (if supported by `gh`) add the GitHub Action secret with a blank value for the user to populate.
4. **Git history** — if the secret was ever committed, propose `git-filter-repo` surgery as Category B. Autonomous history rewrite is forbidden.

Every secret is its own needs-approval item. `--auto` lists them and marks all `skipped (needs-approval)`.

## Scopes

| Scope | What It Covers |
|-------|---------------|
| security | OWASP Top 10, secrets, TLS, input validation |
| privacy | Data collection, consent, retention, PII handling |
| regulatory | GDPR, CCPA, KVKK, LGPD, PIPL, UK GDPR, HIPAA, and framework-specific rules |
| web | CSP, CORS, XSS, CSRF prevention |
| a11y | WCAG 2.2 AA, semantic labels, contrast, keyboard navigation |
| i18n | Locale support, RTL, number/date formatting |

## Delegation

**Owns:** regulatory, privacy (canonical — GDPR / KVKK / CCPA / etc.), a11y-regulatory-framing (ADA / EN301549 mapping), security-regulatory, i18n, secrets-migrate (--secrets-migrate mode) | **Delegates:** ds-mobile → security / privacy / regulatory when mobile project detected (pubspec.yaml / Info.plist / AndroidManifest.xml); ds-frontend → a11y implementation and fixes; ds-analytics → event-property PII scan | **Receives:** ds-ship → Phase 2 regulatory pass

## Execution Flow

Detect -> Configure -> Scan -> Report -> [Fix] -> [Needs-Approval] -> Summary

### Phase 1: Detect

1. **Recovery check:** DETECT `ds/audit/compliance.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read files referenced by pending findings, discard stale ones), skip `done` phases, announce `[CMP] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start, append if missing.

   **State `data` shape:** `{ mode, scopes_selected, scopes_done[], regulations_resolved[], findings[{id, severity, file, line, scope, cat, disposition}], fix_progress }`.

2. **IDU:** Profile → Config.regulations, Config.data, Config.audience, Type+Stack. Findings(compliance scopes) → verify + use. Absent → own analysis.

3. **Project detection.** Search for config files to identify project type:
   - **Web frontend:** `package.json` with react/next/vue/nuxt/angular/svelte/astro
   - **API/backend:** express/fastify/nestjs, fastapi/django/flask, go.mod with gin/echo, Cargo.toml with actix/axum, spring-boot
   - **CLI/library:** bin field, commander/yargs/click/cobra/clap, or library exports without bin
   - Override with `--type` flag if auto-detection is wrong

4. **Stack detection.** Identify framework, language, architecture pattern, auth, database, ORM, API style, testing, CI/CD, i18n, deployment.

5. **Mode selection.** No `--mode` flag → ask user:
   - **Audit Only** — scan all domains, report only
   - **Audit & Fix** — scan, review findings, then fix
   - **Quick Fix** — scan and auto-fix, minimal review

6. **Scope selection.** No `--scope` flag → ask which domains to audit (default: all applicable).
   - For regulatory scope: detect frameworks (GDPR, KVKK, CCPA, etc.) from codebase patterns, confirm with user

7. **Overlap routing (runtime enforcement — OVERLAP-1, -2, -4):**
   - **Mobile project detected** (`pubspec.yaml` with `flutter:` OR `Info.plist` OR `AndroidManifest.xml` present) → invoke `/ds-mobile --scope=security,privacy,regulatory`, wait for completion, read its `ds/audit/findings.md` updates, remove `security`, `privacy`, `regulatory` scopes from this run's active-scope list. Keep only non-mobile-covered scopes (a11y, i18n, web, network, perf, arch) in local execution. Rationale: ds-mobile is authoritative for mobile; running both produces duplicate findings (plan OVERLAP-1).
   - **a11y scope active + project has a frontend** (framework detected in `package.json` / equivalent) → announce delegation: "a11y implementation + fixes delegated to /ds-frontend. This run keeps regulatory framing only (ADA / EN301549 mapping)." Mark a11y scope as `framing-only` for this run; do not emit implementation-level findings, emit only regulatory-mapping findings.
   - **Privacy scope active** → canonical owner. Announce: "/ds-launch --privacy narrows to store-label-correctness, /ds-analytics --privacy-audit narrows to event-property PII scan. This run emits canonical privacy findings."

**Gate:** Project type identified, mode and scope confirmed, regulatory frameworks resolved, overlap routing decisions applied. If fails → project type could not be auto-detected and user did not respond to the `--type` prompt; default to `web`, announce the default, and proceed; if regulatory frameworks are ambiguous after detection, present a list of detected signals to the user and require explicit framework selection before proceeding.

### Phase 2: Architecture Discovery

**When:** Scope includes 3+ domains or `all`. Skip for narrow scans.

1. Analyze codebase architecture (pattern, auth, database, ORM, API style, testing, CI/CD, i18n, deployment)
2. Present detected architecture to user for confirmation
3. Classify rules as:
   - **CAT-1 Conformance:** Universal best practices, existing patterns used incorrectly, bugs, security flaws — auto-fixable
   - **CAT-2 Enhancement:** New layers/patterns not in current architecture — requires explicit approval
4. Present enhancement opportunities, ask which to include (default: none)

**Gate:** Architecture confirmed by user, every rule classified as CAT-1 or CAT-2, approved enhancements finalized. If fails → user did not confirm the detected architecture (no response or explicit rejection); re-present the detected architecture with a brief explanation of each component and ask once more; if still unconfirmed, proceed with the auto-detected architecture and add WARN: `"Architecture unconfirmed — CAT-2 classifications may be inaccurate"` in state.data.

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

**Gate:** All reference files for in-scope domains loaded successfully; unloadable domains marked N/A. If fails → a reference file for an in-scope domain could not be loaded (file missing, path wrong); mark that domain as `N/A` in state.data.scopes_done, continue scan with available domains, and surface the missing reference path in the report so the user can restore it before the next run.

### Phase 4: Scan

Per domain in scope, scan codebase:

1. Search for relevant files
2. Search contents for violation patterns
3. Read files to verify findings in context
4. Skip rules that cannot be verified
5. **Defense-in-depth check ([references/principles.md §5](references/principles.md)):** flag when only one control layer is detected for a sensitive operation (e.g., input validation present but no output encoding AND no auth layer). Single-control reliance is itself a finding regardless of how strong that control is.

**Confidence:** HIGH = specific grep match + context verified, MEDIUM = pattern match, ambiguous context, LOW = heuristic only.

**False positive prevention:** Check surrounding context. Never flag: `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING` blocks, test fixtures.

**Large scope (3+ domains):** Track progress with numbered checklist. Append findings to `ds/audit/findings.md` in project root (add to .gitignore) — file exists with fresh `git_hash` → preserve findings from other scopes and append only your own. After each domain scan, append findings. Enables recovery if context is lost.

**Gate:** Every in-scope domain scanned, all findings recorded with severity and confidence. If fails → one or more domains could not be fully scanned (no scannable source files, access denied, or domain reference was N/A); mark those domains as `inconclusive` in state.data.findings, continue with successfully scanned domains, and list the skipped domains in Phase 5 report so the user knows which compliance areas need manual verification.

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

**Gate:** Report presented to user with all findings, severities, and summary table. If fails → findings list is empty because all domains were `inconclusive` or `N/A`; print a report with a single section `"No verifiable findings — all domains inconclusive or reference files missing"`, list the domains and their skip reason, and exit with status `WARN`.

### Phase 6: Fix (skip if audit-only)

**Overwrite prevention:** Before generating or modifying any compliance document (Privacy Policy, DPIA, Breach Plan, Processor Registry), check if target file already exists. Exists → do NOT overwrite — show diff between existing content and proposed changes, ask user: "Update existing / Keep existing / Show diff".

1. Present fix plan grouped by category (CAT-1 auto-fixable, CAT-2 pre-approved)
2. Confirmation:
   - `quick-fix`: Apply all, summary only
   - `audit+fix`: Show plan, ask proceed/cancel
   - `audit`: Ask which severities to fix
3. Apply fixes grouped by file. Different files can be fixed in parallel, same file sequentially.

**Gate:** All standard fixes attempted; each recorded as applied, failed, or skipped. If fails → one or more CAT-1 fixes could not be applied (file write error, merge conflict with existing content, or generated compliance doc already exists and user chose "Keep existing"); record each as `failed` in state.data.fix_progress with the specific error, continue applying remaining fixes, and surface all failed fix IDs in the Phase 8 summary.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped). If fails → one or more needs_approval items have no decision recorded; re-present each unresolved item with a forced binary prompt (Apply / Skip); if user declines to respond, mark as `skipped (no response)` and proceed.

### Phase 8: Summary

```
ds-compliance: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N
```

FRC+DSC accounting.

**Gate:** `fixed + failed + skipped + needs_approval + not_applicable = total`; every modified file re-read and verified. If fails → accounting does not balance (sum of dispositions ≠ total findings in state.data.findings); identify each finding ID without a disposition, assign `disposition: skipped (accounting-fix)` to each, recompute the summary line, and add WARN: `"N finding(s) auto-skipped to balance accounting"`.

## Quality Gates

1. No cascading breakage after fixes
2. Format preservation (indentation, code style)
3. Scope boundary (only touch required lines)
4. Stack consistency (use correct framework APIs)
5. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/compliance.json` updated per scope, gitignored, deleted on successful Summary.

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
