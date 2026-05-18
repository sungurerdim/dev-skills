# /ds-review

Code review catches what tests miss — security holes, dead code, wrong abstractions, and performance traps hiding in plain sight. Skill scans for all of them with file:line precision.

**Code Improvement** — Tactical fixes and strategic architecture alignment in a single skill.

## Triggers

- User runs `/ds-review`
- User asks to refactor, improve, simplify, or clean up code
- User asks about code quality, complexity, or architecture improvements
- User asks to reduce duplication, fix patterns, or improve maintainability

Four modes: `--tactical` for file-level quality fixes, `--strategic` for architecture-level assessment, `--perf` for deep performance profiling, `--meta-quality` for principle-based holistic audit (SSOT/DRY/KISS/YAGNI/SoC + criteria-fit + consolidation paths).

### Triggers — ÇAĞIRIR / ÇAĞIRMAZ

| ÇAĞIRIR | ÇAĞIRMAZ |
|---------|----------|
| "improve code quality (tactical)", "review my architecture (strategic)" | "format and lint only" (→ ds-fix) |
| "deep performance profiling" | "set up perf budget + CI gate" (→ ds-launch --perf-budget) |
| "principle-based audit (SSOT / DRY / KISS / YAGNI / SoC)" | "score overall project health" (→ ds-blueprint) |
| "reduce duplication, improve maintainability" | "remove dead code / orphan files" (→ ds-simplify) |

## Contract

- Every fix cites file:line with before/after — no blind modifications. Only modifies lines required by the finding; no scope creep.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--tactical` | File-level fixes: security, hygiene, types, performance, privacy |
| `--strategic` | Architecture-level: patterns, coupling, testing, production readiness |
| `--perf` | Deep performance profiling: bundle size, startup, memory, caching, Core Web Vitals |
| `--meta-quality` | Principle-based holistic audit: SSOT, DRY, KISS, YAGNI, SoC + criteria-fit + consolidation paths |
| `--meta-scope={list}` | Meta-quality scope(s): `ssot`, `dry`, `kiss`, `yagni`, `soc`, `overengineering`, `redundancy`, `obsolete`, `duplicate`, `all`. Default: `all` |
| `--criteria-fit` | Enable Phase 3b: project-ideal vs codebase-actual baselines from [references/criteria-fit.md](references/criteria-fit.md) |
| `--suggest-paths` | Enable Phase 4a path proposals: 3 consolidation paths per finding (effort / impact / risk) from [references/path-proposals.md](references/path-proposals.md) |
| `--auto` | All scopes, no questions, single-line summary |
| `--preview` | Analyze + report findings without applying fixes |
| `--scope={name}` | Specific scope(s), comma-separated |
| `--loop` | Re-run until clean or max 3 iterations (tactical only) |
| `--force-approve` | Auto-apply needs_approval items without asking |
| `--resume` | Resume from `ds/audit/review.json` without prompting |
| `--clean` | Delete existing state, start fresh |
| `--no-bootstrap` | Skip auto-invoke of `/ds-blueprint` when findings absent/stale (testing only) |

Without flags: present mode selection.

## Scopes

### Tactical Scopes (--tactical)

9 scopes, 97 checks. Definitions in [references/scopes-tactical.md](references/scopes-tactical.md). Detect/fix patterns for performance in [references/rules-performance.md](references/rules-performance.md).

| Group | Scopes |
|-------|--------|
| Security & Privacy | security, robustness, privacy |
| Code Quality | hygiene, types, simplify |
| Performance | performance |
| AI Cleanup | ai-hygiene, doc-sync |

**Scope boundary:** file-level fixes within current architecture. Finds repeated code, unnecessary abstractions, missing types — does NOT question architectural decisions. Issue requiring architectural change → `needs_approval`.

### Strategic Scopes (--strategic)

8 scopes, 92 checks. Definitions in [references/scopes-strategic.md](references/scopes-strategic.md). Detect/fix patterns for architecture and testing in [references/rules-quality.md](references/rules-quality.md).

| Group | Scopes |
|-------|--------|
| Structure | architecture, patterns, cross-cutting |
| Quality | testing, maintainability |
| Production Readiness | production-readiness |
| Completeness | functional-completeness, ai-architecture |

**Per-scope mandatory checks ([references/principles.md](references/principles.md)):**

- **architecture, patterns:** evaluate by name — SOLID (SRP, OCP, LSP, ISP, DIP) and GRASP (Information Expert, Low Coupling >7 unrelated imports, High Cohesion). Cite violated principle in finding title ([references/principles.md §2](references/principles.md)).
- **production-readiness:** enumerate reliability patterns — flag missing timeout on every external call, retry-with-backoff on transient failures (idempotent ops only), circuit breaker on high-volume services, health checks (liveness + readiness), idempotency keys on externally-exposed write endpoints, graceful shutdown handler, structured logging (no raw `print`/`console.log` in production paths), fail-fast input validation at every system boundary ([references/principles.md §4](references/principles.md)).
- **testing:** verify Test Pyramid (unit-heavy, E2E-light — inverted = HIGH), AAA presence, realistic test data, regression-test-before-fix discipline, coverage as diagnostic not goal ([references/principles.md §7](references/principles.md)).

**Scope boundary:** architecture-level assessment. Questions design decisions, evaluates pattern consistency. Does NOT fix individual code issues (unused imports, type errors, formatting).

### Performance Scopes (--perf)

Deep performance analysis beyond tactical `performance` scope.

| Group | Checks |
|-------|--------|
| Bundle | Bundle size, tree-shaking, unused deps, dynamic imports |
| Startup | Cold start, critical rendering path, lazy init, deferred loading |
| Runtime | Memory leaks, event listener cleanup, layout thrashing, jank |
| Caching | HTTP cache headers, service worker, API response cache, memoization |
| Network | Request waterfall, redundant requests, payload size, compression, prefetching |
| Web Vitals | LCP, INP, CLS for web projects |
| Mobile | Widget rebuild optimization, const constructors, image sizing, list virtualization |
| Database | Query performance, N+1 detection, connection pooling, index usage |

**Scope boundary:** performance-specific deep dive. Produces optimization recs with estimated impact. Fixes only low-risk (const constructors, unused imports, memoization). High-impact changes (architecture, caching strategy) → `needs_approval`.

### Meta-Quality Scopes (--meta-quality)

5 scopes + 4 aliases. Definitions + detector rules in [references/meta-quality-scopes.md](references/meta-quality-scopes.md).

| Scope | Detector summary |
|-------|------------------|
| `ssot` | Same fact/constant/business-rule in 2+ authoritative locations |
| `dry` | Same code pattern in ≥3 places with AST/token similarity ≥85% |
| `kiss` | Solution complexity exceeds problem size — cyclomatic >12 for single use-case |
| `yagni` | Defined but 0 callers / 0 references — feature, param, or flag never used |
| `soc` | One responsibility scattered across 3+ modules (non-cross-cutting) |
| `overengineering` | Alias for combined `ssot + kiss + yagni` |
| `redundancy` | Alias for `dry` + duplicate constants |
| `obsolete` | Unreachable code, legacy paths, deprecated APIs with zero modern callers |
| `duplicate` | Alias for `dry` at function/module granularity |
| `all` | Every scope above |

**Scope boundary:** principle-level audit. Flags violations of SSOT / DRY / KISS / YAGNI / SoC, evaluates project criteria fit, proposes consolidation paths. Does NOT fix without explicit user selection — every finding produces 3 path proposals (effort / impact / risk).

**Anti-overengineering 3-gate** (every finding passes ALL three before being flagged — see [references/principles.md](references/principles.md)):

1. Does this break something currently working? Yes → flag. No → continue.
2. Does this mislead a future reader? Yes → flag. No → continue.
3. Is the added complexity worth its keep? No → flag. Yes → do NOT flag.

Findings that fail all three are silently discarded — false-positive guard.

## Delegation

**Owns:** hygiene, types, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, performance (profiling via --perf) | **Delegates:** ds-simplify → overengineering / dead-code / orphan / premature-abstraction; ds-blueprint → bootstrap when `ds/audit/findings.md` absent or stale | **Receives:** ds-ship → Phase 2 rule audit

## Execution Flow

**Tactical / Strategic / Perf:**
```
Setup → Analyze → [Gap Analysis] → [Plan] → Apply → [Needs-Approval] → Summary
```

**Meta-Quality:**
```
Setup → Analyze-Principles → [Criteria-Fit] → [Suggest-Paths] → Apply (gated) → [Needs-Approval] → Summary
```

### Phase 1: Setup [SKIP if --auto — except step 1 Recovery Check]

1. **Recovery check:** DETECT `ds/audit/review.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read files for pending findings, discard findings whose file:line changed), skip `done` phases, announce `[REV] Resuming from Phase {N}: {name}. Phases 1-{N-1} complete.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start.
2. **State `data`:** `{ mode, scopes_selected, scopes_done[], findings[{id, severity, file, line, scope, title, disposition}], fixed_count, failed_count, needs_approval[] }`.
3. Pre-flight: check if git repo (optional, warn if not).
4. **IDU:** Profile → Config.priorities, Config.quality, Current Scores, Toolchain, Type+Stack. Findings(security, hygiene, types, performance, architecture, patterns) → verify + use. Absent → own analysis.
5. **Mode selection.** No mode flag → ask: Tactical / Strategic / Performance / Meta-Quality / All (tactical → strategic → meta-quality sequentially, skip --perf unless explicit).
6. **Scope selection.** No `--scope` → ask which scopes (default: all for selected mode).
7. Uncommitted changes detected → ask: continue / stash first / cancel.

**Gate:** Mode + scope confirmed (explicitly or via flags). If fails → re-present menu; user declines / no response after 2 prompts → exit with WARN "No mode selected — run /ds-review with --tactical, --strategic, --perf, or --meta-quality to proceed."

### Phase 2: Analyze

**Findings bootstrap rule.** Before any analysis:
1. `ds/audit/findings.md` absent → invoke `/ds-blueprint --preview --scope=all`, wait for completion, re-read. Skill owns detection SSOT; re-implementing it here is duplicate work.
2. `ds/audit/findings.md` exists but `git_hash` ≠ HEAD → invoke `/ds-blueprint --refresh`, wait for completion, re-read.
3. `ds/audit/findings.md` exists + fresh → proceed.

Auto-invoke MAY be skipped via `--no-bootstrap` for testing — then review runs own scope analysis.

**Findings file check:** if `ds/audit/findings.md` exists + `git_hash` matches HEAD, filter findings by active scopes. Per matching finding:
1. Read file:line + surrounding context (±10 lines).
2. Verify finding still valid (code may have changed).
3. Confirmed → add to fix list. False positive or already resolved → classify as `not-applicable` (false positive) or `already-resolved`, record in state with reason; both count as Skipped in FRC accounting.
4. After verification, proceed to fix confirmed.

Skip own analysis for scopes covered by findings file. Scopes NOT in findings file → run own analysis below.

**If no findings file after bootstrap or `--no-bootstrap`:** analyze in parallel-planned batches. Group scopes by cost — read-only (parallel), AST-based (parallel sharing LSP cache), opus-grade reasoning (serial). Announce plan before starting.

| Batch | Active scopes (subset of selected) | Concurrency |
|-------|-----------------------------------|-------------|
| Read-only | hygiene, types, doc-sync, ai-hygiene | Parallel |
| AST | architecture, patterns, cross-cutting, simplify, performance | Parallel (shared LSP cache) |
| Cross-file / opus-grade | security, privacy, ai-architecture, production-readiness, testing | Serial |

**Tactical analysis:** grep for patterns, read context (50 lines), score findings by severity. For repository hygiene (committed binaries, secrets): verify via `git ls-files`.

**Strategic analysis:** evaluate patterns across codebase, flag structural issues even if not auto-fixable, question consistency not just correctness.

Cross-scope dedup: merge findings at same file:line, keep highest severity.

**Skip patterns:** `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING`, platform guards, test fixtures.

Wait for all batches before proceeding.

**Gate:** Findings = 0 → print `"All {N} checks evaluated across {scopes}: 0 findings"`, skip to summary. Distinguishes clean from skipped. If fails (analysis incomplete or bootstrap `/ds-blueprint` didn't return) → mark affected scopes `inconclusive` in state, log "bootstrap incomplete — scopes {names} unanalyzed", proceed to summary with partial results + WARN status.

**CRITICAL escalation:** any CRITICAL finding → re-read full file section (±20 lines), verify genuine — not pattern-matching false positive. Evidence insufficient → downgrade to HIGH. Only confirmed CRITICALs proceed.

### Phase 3: Gap Analysis (strategic only)

Calculate gaps: current vs ideal for coupling, cohesion, complexity, coverage. Project-type defaults:

| Type | Coupling | Cohesion | Complexity | Coverage |
|------|----------|----------|------------|----------|
| cli | <40% | >75% | <10 | 70%+ |
| library | <30% | >80% | <8 | 85%+ |
| api | <50% | >70% | <12 | 80%+ |
| web | <60% | >65% | <15 | 70%+ |
| mobile | <55% | >65% | <12 | 65%+ |
| devtool | <35% | >75% | <10 | 80%+ |

Display Current vs Ideal table. Technology assessment: evaluate key decisions OK / Questionable / Problematic (with evidence). Include only Questionable/Problematic.

Categorize recs by effort/impact: Quick Win → Moderate → Complex → Major.

**Gate:** Current vs Ideal table + categorized recs produced. If fails → metric uncomputable (coverage tool absent, coupling analysis incomplete) → insert `?` in Current column with note "metric unavailable — {reason}", output partial table, continue; do not block on missing metrics.

### Phase 3a: Analyze-Principles (--meta-quality only)

Per active meta-scope from [references/meta-quality-scopes.md](references/meta-quality-scopes.md):

1. Apply detector rule with stated threshold + AST/token similarity gate.
2. Run anti-overengineering 3-gate — fail any one → flag, pass all three → discard.
3. Cross-scope dedup: merge same file:line, keep highest-confidence.
4. Record finding: file:line, scope, principle name, evidence (cited code), confidence.

Skip patterns: test fixtures, generated files, framework-required boilerplate, public-API signatures, `# intentional`, `_` prefix.

**Gate:** Every active meta-scope produces a result (finding count or `0 findings`). If fails (detector can't run, e.g. AST tool unavailable) → mark scope `inconclusive` in state, log "{scope} detector unavailable — {reason}", proceed with remaining.

### Phase 3b: Criteria-Fit (--meta-quality + --criteria-fit)

Compare project's implied/stated criteria to baselines for detected type. Baselines in [references/criteria-fit.md](references/criteria-fit.md).

1. Detect type from blueprint profile (or own detection if absent).
2. Load baseline thresholds for that type (e.g. `small-cli`: SSOT 0-2, DRY 0-3; `web-app`: SSOT 0-1, DRY 0-5; `library`: SSOT 0, SoC 0-1).
3. Compare findings vs baseline. Above baseline → flag as `criteria-mismatch`.
4. Mismatch → ask user: "{scope} count ({n}) exceeds {type} baseline ({max}). Loosen criteria for this project or tighten the codebase?"

**Gate:** Criteria-fit assessment recorded for each active scope. If fails (type undetected + user declines to specify) → use generic baselines, mark assessment `low-confidence`, proceed.

### Phase 4a: Suggest-Paths (--meta-quality + --suggest-paths)

For each finding from Phase 3a, generate 3 paths from [references/path-proposals.md](references/path-proposals.md):

- **Path A — Minimal:** delete duplicates only, no abstraction
- **Path B — Moderate:** extract a shared module / helper
- **Path C — Structural:** unify the API / abstraction at a higher level

Each path includes: estimated effort (hours), impact (scope reach), risk (regression surface), rollback approach.

Present paths grouped by finding. User selects per-finding: `Path A / B / C / Skip / Apply same path to all matching findings`.

**Gate:** Every finding has selected path or explicit `Skip`. If fails → assign `skip (no path selected)`, proceed.

### Phase 4: Plan Review [SKIP if --auto]

Print findings table (ID, severity, title, file:line). Ask: Fix All (recommended) / By Severity / Review Each / Report Only.

**Gate:** User selected plan action. If fails → re-present once; no selection after 2 attempts → default Report Only, note in state.data.plan_action.

### Phase 5: Apply [SKIP if --preview]

Apply fixes grouped by file:
- Different files: parallel
- Same file: sequential (re-read after each edit)
- Minimal diff, preserve surrounding style
- Before adding any import/API, verify it exists in codebase or deps
- Cross-module change → `needs_approval`

After all fixes: run available lint/type/test checks. New errors introduced → repeat fix-verify (max 3 iterations).

**Loop mode (`--loop`):** after applying:
1. Re-read modified files + direct dependents (importers, callers).
2. Re-analyze for new findings caused by fixes (cascade breakage).
3. New findings → apply fixes.
4. Max 3 iterations. Still issues after 3 → report remaining and stop.

Per fix, include education: **why** (impact if unfixed), **avoid** (anti-pattern), **prefer** (correct pattern).

**Gate:** All approved fixes applied + lint/type/test pass (or max 3 fix-verify exhausted). If fails → revert offending fix via `git checkout -- {file}`, record `failed` in state.data.findings with lint/type/test error captured, continue with remaining.

### Phase 5a: Needs-Approval Review [CONDITIONAL]

Items flagged `needs_approval` (cross-module changes, architectural decisions):
- `--auto` without `--force-approve`: list items, skip, note in summary
- `--force-approve`: apply all
- Interactive: present items, ask Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** All resolved (applied, skipped, deferred). If fails → user declined → mark unresolved `deferred` in state.data.needs_approval, disposition `deferred (user did not respond)`, proceed.

### Phase 5b: CRITICAL Escalation

Any CRITICAL → flag for manual review before auto-fixing. Interactive mode: show finding with full context, ask explicit confirmation. CRITICAL verified with extra scrutiny — re-read file section + surrounding context.

**Gate:** Every CRITICAL explicitly confirmed or downgraded. If fails (user doesn't respond to confirmation) → do NOT apply CRITICAL fix; mark `deferred (awaiting manual review)` in state.data.findings, include in Needs Approval section of summary, continue with non-CRITICAL.

### Phase 6: Loop (--loop flag, tactical only)

Applied > 0:
1. Cascade check — verify dependent files don't need updates.
2. Re-analyze modified + cascade-affected files.
3. Re-apply for new findings.

Max 3 iterations. Summary shows per-iteration breakdown.

**Gate:** Zero new findings on re-analysis, or max 3 reached. If fails (new findings after 3) → record remaining in state.data.findings disposition `open (loop exhausted)`, summary status WARN, report count of unresolved cascade findings.

### Phase 7: Summary

**Tactical output:**
```
refactor complete (tactical)
============================
| Scope          | Findings | Fixed | Skipped | Failed |
|----------------|----------|-------|---------|--------|
| {scope}        |   {n}    |  {n}  |   {n}   |  {n}   |
| ...            |          |       |         |        |
| Total          |   {n}    |  {n}  |   {n}   |  {n}   |

Fixed: {n} | Skipped: {n} | Failed: {n} | Needs Approval: {n} | Total: {n}
```

FRC+DSC accounting.

**Strategic output:**
```
refactor complete (strategic)
=============================
| Metric     | Current | Ideal | Gap  |
|------------|---------|-------|------|
| {metric}   | {n}     | {n}   | {n}  |
| ...        |         |       |      |

Recommendations by effort:
  Quick Win:  [{id}] {title}
  Moderate:   [{id}] {title}
  Complex:    [{id}] {title}

Fixed: {n} | Skipped: {n} | Failed: {n} | Needs Approval: {n} | Total: {n}
```

**Auto output:** `refactor: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

Status: OK (failed=0), WARN (failed>0 no CRITICAL), FAIL (CRITICAL unfixed or error).

**Gate:** Summary printed + `fixed + failed + skipped + needs_approval + not_applicable = total` verified; every finding has a disposition. If fails → identify findings missing disposition, assign `failed (disposition missing)`, reprint summary, status WARN.

## Score Calculation

```
base_score = 100
CRITICAL: -25, HIGH: -10, MEDIUM: -3, LOW: -1
scope_score = max(0, base_score + sum(penalties))
```

Cap: any CRITICAL → max 40; 3+ HIGH → max 60.

**Value Delivered:** 1-5 concrete fix outcomes. Example shapes (placeholders, not literal):

- `{n} CRITICAL/HIGH security findings closed ({n} hardcoded secrets, {n} injection vectors) — exposure window before next deploy eliminated`
- `{n} N+1 query patterns fixed in {module} — p95 latency expected to drop on hot paths`
- `{n} architectural SOLID/GRASP violations refactored — module change-coupling reduced, blast radius narrowed for future edits`
- `{n} principle-based findings (SSOT / DRY / KISS / YAGNI / SoC) consolidated via Path-B (shared module) — duplicate logic count went from {before} to {after}`

Zero-finding run: `All checks evaluated across {scopes} — 0 findings`.

## Quality Gates

- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/review.json` updated per scope + per fix, gitignored, deleted on successful Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.
- FRC+DSC enforced.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Finding references deleted or moved file | Mark as not-applicable, continue |
| Fix breaks dependent file | Revert, flag as failed, search consumers before retrying |
| Scope too large (>50 files with findings) | Apply saturation gate, ask user to narrow scope |
| Strategic mode: architecture assessment unclear | Ask user for system context and constraints |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No findings | Report clean score, skip fix phases |
| All findings are LOW | Report only, skip fix prompt |
| Single file project | Run all applicable scopes on that file |
