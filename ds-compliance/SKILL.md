---
name: ds-compliance
description: Security and regulatory compliance — OWASP, privacy laws, data protection, web security, i18n. Use when auditing for security/privacy compliance, GDPR/KVKK, or pre-release legal review.
---

# /ds-compliance

Single missing privacy policy or unpatched XSS can mean fines, data breaches, or store rejection. Skill audits 142 rules across 9 compliance domains with file:line precision.

**Security & Regulatory Compliance** — OWASP security, privacy laws, data protection, web security, and internationalization.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-compliance`
- User asks about GDPR, KVKK, CCPA, HIPAA, or other regulatory compliance
- User asks to check for security vulnerabilities, secrets, or injection risks
- User asks about privacy, data protection, or consent requirements
- User asks about CSP, CORS, XSS, CSRF, or web security
- User asks about internationalization compliance

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "GDPR/KVKK/CCPA/HIPAA audit", "regulatory compliance check" | "audit code quality" (→ ds-review) |
| "OWASP Top 10 security scan" | "fix lint errors / format" (→ ds-fix) |
| "privacy compliance audit (consent, retention, DSR)" | "design event taxonomy" (→ external / manual) |
| "CSP/CORS/XSS/CSRF audit" | "mobile app store privacy labels" (→ ds-mobile / ds-launch) |
| "a11y regulatory framing (ADA / EN301549 mapping)" | "implement a11y fixes (keyboard nav, contrast, ARIA)" (→ ds-frontend) |

## Contract

**Dimensions:** C1 (canonical), C2 (canonical, conditional messaging), C3 (regulatory), A7 (regulatory), A8 (rules), A9 (conditional ecosystem rules), A11 (portability crosscheck)
**Framework alignment (advisory):** OWASP ASVS 5.0.0 (C1), OWASP SAMM (C2). Tool-derived security findings carry the tool's own ASVS version tag (OSS DAST tools still emit 4.0.3-tagged results — never present them as ASVS 5.0 coverage).

- Every finding cites file:line — never infer. Unverifiable rules skipped, not guessed. Only audits compliance; code fixes are CAT-1 (auto) or CAT-2 (approval).
- Standalone. Uses blueprint profile when available; `ds/audit/findings.md` only when fresh (`git_hash == HEAD` AND current run-cycle); own analysis otherwise.
- State-exempt: single regenerable report/audit.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Mobile-project overlap (overlap rule, runtime enforcement):** When project signals mobile (`pubspec.yaml` with `flutter:`, `package.json` with `react-native`, `*.xcodeproj`, or `build.gradle` with `android {}`): `/ds-mobile` present → delegate security/privacy/regulatory to it (mobile-authoritative), default-skip those scopes locally, announce "Mobile project detected — security/privacy/regulatory delegated to /ds-mobile". `/ds-mobile` absent → run the mobile-relevant security/privacy/regulatory checks inline (Phase 1 step 6) instead of dropping the three scopes, announce "Mobile project detected, /ds-mobile absent — security/privacy/regulatory audited inline". Override either path with `--scope=security,privacy,regulatory`.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode={x}` | `audit`, `audit+fix`, `quick-fix` |
| `--scope={list}` | security, privacy, regulatory, web, network, arch, perf, a11y, i18n, or `all` |
| `--type={t}` | Override auto-detection: `web`, `api`, `cli`, `library` |
| `--secrets-migrate` | Rotation / vault migration walkthrough for hardcoded secrets — always asks per secret (Secrets Migrate Mode), `--ask` or not |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `needs-human`. |

Default: no disambiguating flag resolves to `--mode=audit` (recommended), recorded in the summary. `--ask` with no disambiguating flag: present mode selection.

### Secrets Migrate Mode (`--secrets-migrate`)

Per hardcoded secret detected in security scope:

1. **Surface** — file:line, redacted fragment (first 4 chars + `***`), kind (API key / token / password / webhook URL / etc.).
2. **Ask per secret:**
   - **Rotate first?** Exposed in git history? `Yes` → require rotation before vault migration; propose provider-specific path ({provider-rotation-flow}: e.g. AWS IAM, Stripe dashboard, GitHub token settings).
   - **Destination vault?** `env (local)` / `.env.example + CI secret store` / `HashiCorp Vault` / `AWS Secrets Manager` / `GCP Secret Manager` / `Azure Key Vault` / `cloud provider native` / `other`.
   - **Migration path?** Show replacement snippet: `const {var} = process.env.{ENV_KEY}` (or stack equivalent) + config file update (`.env.example` entry, CI secret declaration).
3. **Apply** — replace hardcoded with reference, add `.env.example` placeholder entry, README line pointing at vault, and (if `gh` supported) add GitHub Action secret with blank value for user to populate.
4. **Git history** — secret ever committed → propose `git-filter-repo` surgery as Category B. Autonomous history rewrite is forbidden.

Every secret is its own needs-approval item, and secret rotation/migration matches the publish/irreversible exception list (rotating/transmitting a real credential) — never decided automatically, default or `--ask`. Every run lists each secret and marks it `skipped (needs-human)` until the human acts.

## Scopes

| Scope | What It Covers |
|-------|---------------|
| security | OWASP Top 10, secrets, TLS, input validation |
| privacy | Data collection, consent, retention, PII handling |
| regulatory | GDPR, CCPA, KVKK, LGPD, PIPL, UK GDPR (+DUAA), HIPAA, COPPA, EU AI Act, EU Data Act, EU CRA, PCI DSS, framework-specific |
| web | CSP, CORS, XSS, CSRF prevention |
| network | TLS/transport security, API protection, DoS resilience |
| arch | Audit logging, boundary/input validation, dependency security |
| perf | Resource exhaustion prevention, query safety, resource cleanup (compliance-relevant subset) |
| a11y | WCAG 2.2 AA, semantic labels, contrast, keyboard nav |
| i18n | Locale support, RTL, number/date formatting |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| security | any source — every codebase has a security surface | — |
| privacy | `pii=yes`, `auth` ≠ none, or `integrations` includes an analytics SDK | N/A — no personal-data path detected |
| regulatory | `pii=yes`, `jurisdiction` resolved, or `audience=public` | N/A — no regulated-data or public-market signal |
| web | `ui=web` | N/A — no web frontend |
| network | `api` ≠ none or `deploy` ≠ none | N/A — no network-facing surface |
| arch | any source — audit logging, input validation, and dependency hygiene apply broadly | — |
| perf | `db` ≠ none or `api` ≠ none | N/A — no query/service surface to exhaust |
| a11y | `ui` ≠ none | N/A — no UI surface |
| i18n | `audience` ≠ developers | N/A — developer-facing surface, locale support not expected |

## Delegation

**Owns:** regulatory, privacy (canonical — GDPR / KVKK / CCPA / etc.), a11y-regulatory-framing (ADA / EN301549 mapping), security-regulatory, i18n, secrets-migrate (`--secrets-migrate`) | **Delegates:** ds-mobile → security/privacy/regulatory when mobile detected (`pubspec.yaml` / `Info.plist` / `AndroidManifest.xml`); ds-frontend → a11y implementation + fixes | **Receives:** ds-launch → canonical privacy for store labels; ds-ship → Phase 2 regulatory pass; ds-productize → subscription-law + privacy canonical audit

### Transactional Messaging (conditional)

**Activate when:** messaging SDK/provider dependency, a consent field in the schema, or reminder-scheduling code is detected — those three signals are the whole activation contract, evaluated here. Zero checks when absent. ds-blueprint installed alongside → its `references/detection.md` § Step 5 carries the fuller provider-signal catalog; absent → the three signals above stand alone, no capability lost.

| Check | Rule |
|-------|------|
| Consent capture | Explicit opt-in recorded per channel (SMS/WhatsApp/email/push) with timestamp, distinct from general account creation |
| Lawful basis | Transactional-only messages (appointment reminders, receipts) map to legitimate interest/contract performance; marketing content in the same channel requires separate consent (KVKK Art. 5, GDPR Art. 6) |
| Opt-out mechanism | STOP/unsubscribe honored within the regulation-mandated window (immediate for SMS per most carrier rules) |
| Provider disclosure | Privacy policy names the messaging provider(s) and what data is shared (phone number, message content) — cross-ref PRV-15 Data Processing Agreement |

### A9 — Google / Apple Ecosystem Rules (conditional)

**Activate when:** blueprint profile `Integrations` field is `google-workspace` or `apple-ecosystem`. Zero checks when absent.

| Provider | Rule | Scope |
|----------|------|-------|
| Google | Google API Limited Use policy compliance — data from restricted scopes cannot be transferred to AI/ads/analytics | privacy |
| Google | Data-disclosure label ↔ API usage consistency — every declared data type collected via Google APIs matches the actual scope usage | privacy |

## Execution Flow

Detect → Configure → Scan → Report → [Fix] → [Needs-Approval] → Summary

### Phase 1: Detect

1. **Upstream artifacts:** Profile → Config.regulations, Config.data, Config.audience, Type+Stack. Findings(compliance scopes) → verify + use. Absent → own analysis.

2. **Project detection.** Search for config to identify type:
   - **Web frontend:** `package.json` with react/next/vue/nuxt/angular/svelte/astro
   - **API/backend:** express/fastify/nestjs, fastapi/django/flask, go.mod with gin/echo, Cargo.toml with actix/axum, spring-boot
   - **CLI/library:** bin field, commander/yargs/click/cobra/clap, or library exports without bin
   - Override with `--type` if auto-detection wrong

3. **Stack detection.** Framework, language, architecture pattern, auth, DB, ORM, API style, testing, CI/CD, i18n, deployment.

4. **Mode selection.** No `--mode` → present a menu covering every mode, each with a one-line what-it-does: Audit Only (recommended) — scan + report, no changes / Audit & Fix — scan + review + fix / Quick Fix — scan + auto-fix, minimal review / (Cancel). A disambiguating flag (e.g. `--mode`, `--secrets-migrate`) skips the menu.

5. **Scope selection.** Default: all applicable domains, and regulatory frameworks detected from codebase patterns (GDPR, KVKK, CCPA, etc.) apply without confirmation. `--ask`, no `--scope`: ask which domains; confirm the detected regulatory frameworks.

6. **Overlap routing (runtime enforcement of the overlap rules):**
   - **Mobile project detected** (`pubspec.yaml` with `flutter:` OR `Info.plist` OR `AndroidManifest.xml`) → `/ds-mobile` present → invoke `/ds-mobile --scope=security,privacy,regulatory`, wait for completion, read its `ds/audit/findings.md` updates, remove `security/privacy/regulatory` from active scope; keep only non-mobile-covered scopes (a11y, i18n, web, network, perf, arch) locally (ds-mobile authoritative; running both duplicates findings). `/ds-mobile` absent → keep `security/privacy/regulatory` active and run them here: load [rules-compliance.md](references/rules-compliance.md) as usual, plus the mobile-specific surfaces those rules don't already cover — platform manifest permissions (`AndroidManifest.xml` uses-permission list, `Info.plist` usage-description keys) against declared feature use, mobile secure-storage APIs (Keychain/Keystore) for credential handling, and store privacy-label consistency (PRV-18 crosscheck); gap-note "deeper mobile-specific coverage (13-domain release audit) requires /ds-mobile" so the reduced depth is visible, never silent.
   - **a11y scope active + project has frontend** (framework detected in `package.json` / equivalent) → `/ds-frontend` present → announce delegation: "a11y implementation + fixes delegated to /ds-frontend. This run keeps regulatory framing only (ADA / EN301549 mapping)." Mark a11y `framing-only`; emit only regulatory-mapping findings. `/ds-frontend` absent → keep the full a11y scope here: audit and CAT-1-fix directly from [rules-a11y.md](references/rules-a11y.md) (A11Y-01–08) in addition to the regulatory-mapping findings; gap-note "deeper design-system a11y coverage requires /ds-frontend".
   - **Privacy scope active** → canonical owner. Announce: "/ds-launch --privacy narrows to store-label-correctness. This run emits canonical privacy findings, including event-property PII scanning."

**Gate:** Project type identified; mode + scope confirmed; regulatory frameworks resolved; overlap routing applied. If fails → type undetected + no `--type` response → default `web`, announce, proceed; regulatory ambiguous after detection → default: apply the best-guess framework(s) from detected signals (audience, data locality, stack) and record the assumption in the summary; `--ask`: present detected signals, require explicit framework selection before proceeding.

### Phase 2: Architecture Discovery

**When:** scope includes 3+ domains or `all`. Skip for narrow scans.

1. Analyze architecture (pattern, auth, DB, ORM, API style, testing, CI/CD, i18n, deployment).
2. Default: proceed directly on the auto-detected architecture. `--ask`: present detected architecture for confirmation.
3. Classify rules:
   - **CAT-1 Conformance:** universal best practice, existing pattern misused, bug, security flaw — auto-fixable
   - **CAT-2 Enhancement:** new layers/patterns not in current architecture — needs approval
4. Default: none of the enhancement opportunities are included. `--ask`: present enhancement opportunities, ask which to include.

**Gate:** Architecture confirmed; every rule classified CAT-1 / CAT-2; approved enhancements finalized. If fails → user unconfirmed (no response or rejection) → re-present detected architecture with brief explanation, ask once more; still unconfirmed → proceed with auto-detected, add WARN: `"Architecture unconfirmed — CAT-2 classifications may be inaccurate"` to the report.

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

**Gate:** All reference files for in-scope domains loaded; unloadable marked N/A. If fails → file missing → mark domain `N/A`, continue with available, surface missing path in report.

### Phase 4: Scan

Per in-scope domain:

1. Search for relevant files.
2. Search contents for violation patterns.
3. Read files to verify findings in context.
4. Skip rules that cannot be verified.
5. **Defense-in-depth check** (core principles §5, [../core/principles.md](../core/principles.md)): flag when only one control layer is detected for a sensitive operation (e.g. input validation present but no output encoding AND no auth layer). Single-control reliance is itself a finding regardless of how strong that control is.

**Confidence:** HIGH = match + context verified. MEDIUM = pattern, ambiguous. LOW = heuristic.

**False-positive prevention:** check surrounding context. Never flag `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING`, test fixtures.

**Large scope (3+ domains):** numbered progress checklist + append findings to `ds/audit/findings.md` (add to `.gitignore`) — file exists with `git_hash` equal to `git rev-parse HEAD` output → preserve findings from other scopes, append only your own. After each domain scan, append. Enables recovery on context loss.

**Gate:** Every in-scope domain scanned; findings recorded with severity + confidence. If fails → domain(s) un-scan-able (no scannable source, access denied, reference N/A) → mark `inconclusive`, continue with successful ones, list skipped domains in Phase 5 report.

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
| Category | BLOCKER | CRITICAL | HIGH | MEDIUM | LOW | Total |
```

**Severity:** BLOCKER > CRITICAL > HIGH > MEDIUM > LOW. BLOCKER = legally mandated gap with a citable source (regulation article / store policy) — feeds ds-ship's mandated-blocker test; ADVISORY findings never block and never count toward blockers. Uncertain → choose lower.

**Gate:** Report with findings + severities + summary. If fails → findings list empty because all domains `inconclusive` or `N/A` → print report with single section `"No verifiable findings — all domains inconclusive or reference files missing"`, list domains + skip reason, exit with status `WARN`.

### Phase 6: Fix [SKIP if audit-only]

**Checkpoint pre-step (before the first fix is written,** [core checkpoint protocol](../core/checkpoint-protocol.md)**):** `git status --porcelain` → empty → proceed. Non-empty and disjoint from this run's planned writes → proceed, list the dirty paths as untouched. Non-empty and a planned fix touches a dirty path → default: mark that fix `skipped (needs-human)`, continue with disjoint fixes. `--ask`: show the dirty files, ask Commit first (recommended) / Stash / Proceed anyway (the mechanical-gate revert path `git checkout -- {file}` also discards pre-existing edits in that file). Never run a bulk fix over uncommitted unrelated changes silently.

**Overwrite prevention:** before generating/modifying any compliance document (Privacy Policy, DPIA, Breach Plan, Processor Registry), check if target exists. Default: Keep existing when it already has non-trivial content, otherwise update; the decision and diff are recorded in the summary. `--ask`: show diff between existing + proposed, ask "Update existing / Keep existing / Show diff".

1. Present fix plan — one line per fix (`[severity] title — file:line`) grouped by category/severity with counts; state the question (`Apply these N fixes?`). "All" = exactly the displayed set.
2. Default: apply all (matches `quick-fix` behavior), summary only. `--ask`: `quick-fix` → apply all, summary only; `audit+fix` → show plan, offer Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / proceed / cancel; `audit` → ask which severities.
3. Apply fixes grouped by file. Different files in parallel, same file sequential.

**Gate:** All standard fixes attempted; each recorded. If fails → CAT-1 fix unappliable (file write error, merge conflict, generated doc exists + user chose "Keep existing") → record `failed` with specific error, continue with remaining, surface all failed IDs in Phase 8 summary.

### Phase 7: Needs-Approval Review [needs_approval > 0]

Default: every item, including CRITICAL, resolves via the same impact/effort/risk reasoning an approval block would show, applied and recorded `fixed`/`failed`; items matching the publish/irreversible exception list (e.g. secret rotation, per the Secrets Migrate section) resolve `skipped (needs-human)` instead. `--ask`: present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed, declined → skipped). If fails → unresolved → re-present each with forced binary prompt (Apply / Skip); user declines → mark `skipped (no response)`, proceed.

### Mechanical Done Gate [any fix applied]

Resolve `{check-cmd}` in Phase 1: ds-quality enforcement arm installed (stop-hook / pre-commit hook / auto-lint) → use its gate command; else detect stack-native format/lint/type/test commands; none detectable → Verification-Infrastructure Gap — report it, offer `/ds-quality`, record the decision, never silently skip. Run `{check-cmd}` once at baseline; baseline red → record red-at-baseline — done condition becomes "no *new* red", baseline reds reported as findings, never inherited as green.

After each Phase 6/7 fix batch: run `{check-cmd}` on the touched scope. Before Phase 8: run the full `{check-cmd}` once — aggregate result gates the summary.

| Result | Action |
|--------|--------|
| Green (no new red) | Proceed; quote the exact command + observed output as Completion Evidence |
| New red, ≤3 attempts on the fix | Repair, re-run the same command — same command string, same scope |
| New red after 3 attempts | Revert the offending fix via `git checkout -- {file}`, disposition `reverted (mechanical gate)` with captured error, continue with remaining |

Never report `OK` while `{check-cmd}` shows a new red.

### Phase 8: Summary

```
ds-compliance: {OK|WARN|FAIL} | Scopes: ran {a,b} · N/A — {c}={reason} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

Disposition accounting — totals balance. `fixed + failed + skipped + needs_approval + not_applicable = total`.

**Gate:** Summary balances; every modified file re-read. If fails → identify findings without disposition, assign `disposition: skipped (accounting-fix)`, recompute summary, add WARN: `"{n} finding(s) auto-skipped to balance accounting"`.

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `{n} CRITICAL secrets in source intercepted — credentials no longer leak into git history (rotation guidance attached)`
- `{regulation} compliance: {n} consent gaps, {n} retention policy gaps closed — exposure window before {audit-date} eliminated`
- `OWASP Top 10: {n} CRITICAL injection vectors flagged with {file}:{line} — {m} fixed directly (CAT-1), {k} escalated for approval (CAT-2)`

Zero-finding run: `Compliance scope clean — no regulatory or security findings`.

## Quality Gates

1. No cascading breakage after fixes
2. Format preservation (indentation, code style)
3. Scope boundary (only touch required lines)
4. Stack consistency (use correct framework APIs)
5. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for uncovered scopes.
6. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| Regulatory framework ambiguous | Default: apply best-guess framework(s) from detected signals, recorded in the summary. `--ask`: list detected signals, ask user to confirm applicable frameworks. |
| Rule references external policy that changed | Flag as needs-verification, use last known version |
| Fix requires architectural change | Classify as needs-approval, present to user |
| Compliance doc template generation fails | Generate partial template, list missing sections |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No source code files | Report empty scan, suggest checking path |
| Mixed project types | Detect all types, apply union of applicable rules |
| Generated code only | Skip generated files, warn if no scannable code remains |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
