# /ds-review

Code review catches what tests miss — security holes, dead code, wrong abstractions, and performance traps hiding in plain sight. Skill scans for all of them with file:line precision.

**Code Improvement** — Tactical fixes and strategic architecture alignment in a single skill.

## Triggers

- User runs `/ds-review`
- User asks to refactor, improve, simplify, or clean up code
- User asks about code quality, complexity, or architecture improvements
- User asks to reduce duplication, fix patterns, or improve maintainability

Three modes: `--tactical` for file-level quality fixes, `--strategic` for architecture-level assessment, `--perf` for deep performance profiling.

## Contract

- Every fix cites file:line with before/after — no blind modifications
- Only modifies lines required by the finding — no scope creep
- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| `--tactical` | File-level fixes: security, hygiene, types, performance, privacy |
| `--strategic` | Architecture-level: patterns, coupling, testing, production readiness |
| `--perf` | Deep performance profiling: bundle size, startup, memory, caching, Core Web Vitals |
| `--auto` | All scopes, no questions, single-line summary |
| `--preview` | Analyze and report findings without applying fixes |
| `--scope=<name>` | Specific scope(s), comma-separated |
| `--loop` | Re-run until clean or max 3 iterations (tactical only) |
| `--force-approve` | Auto-apply needs_approval items without asking |
| `--resume` | Resume from `ds/audit/review.json` without prompting |
| `--clean` | Delete existing state and start fresh |
| `--no-bootstrap` | Skip auto-invoke of `/ds-blueprint` when findings are absent or stale (testing only) |

Without flags: present mode selection to user.

## Scopes

### Tactical Scopes (--tactical)

9 scopes, 97 checks. Scope definitions in [references/scopes-tactical.md](references/scopes-tactical.md). Detailed detect/fix patterns for performance in [references/rules-performance.md](references/rules-performance.md).

| Group | Scopes |
|-------|--------|
| Security & Privacy | security, robustness, privacy |
| Code Quality | hygiene, types, simplify |
| Performance | performance |
| AI Cleanup | ai-hygiene, doc-sync |

**Scope boundary:** File-level fixes within current architecture. Finds repeated code, unnecessary abstractions, missing types — does NOT question architectural decisions. If an issue requires architectural change, report as `needs_approval`.

### Strategic Scopes (--strategic)

8 scopes, 92 checks. Scope definitions in [references/scopes-strategic.md](references/scopes-strategic.md). Detailed detect/fix patterns for architecture and testing in [references/rules-quality.md](references/rules-quality.md).

| Group | Scopes |
|-------|--------|
| Structure | architecture, patterns, cross-cutting |
| Quality | testing, maintainability |
| Production Readiness | production-readiness |
| Completeness | functional-completeness, ai-architecture |

**Per-scope mandatory checks ([references/principles.md](references/principles.md)):**

- **architecture, patterns:** Evaluate by name — SOLID (SRP, OCP, LSP, ISP, DIP) and GRASP (Information Expert, Low Coupling >7 unrelated imports, High Cohesion). Cite the violated principle in the finding title (see [references/principles.md §2](references/principles.md)).
- **production-readiness:** Enumerate reliability patterns — flag missing timeout on every external call, retry-with-backoff on transient failures (idempotent ops only), circuit breaker on high-volume services, health checks (liveness + readiness), idempotency keys on externally-exposed write endpoints, graceful shutdown handler, structured logging (no raw `print`/`console.log` in production paths), fail-fast input validation at every system boundary (see [references/principles.md §4](references/principles.md)).
- **testing:** Verify Test Pyramid (unit-heavy, E2E-light — flag inverted pyramid as HIGH), AAA pattern presence, realistic test data, regression-test-before-fix discipline, coverage as diagnostic not goal (see [references/principles.md §7](references/principles.md)).

**Scope boundary:** Architecture-level assessment. Questions design decisions, evaluates pattern consistency. Does NOT fix individual code issues (unused imports, type errors, formatting).

### Performance Scopes (--perf)

Deep performance analysis beyond tactical `performance` scope. Checks areas requiring profiling-level analysis.

| Group | Checks |
|-------|--------|
| Bundle | Bundle size analysis, tree-shaking, unused dependencies, dynamic imports |
| Startup | Cold start time, critical rendering path, lazy initialization, deferred loading |
| Runtime | Memory leaks, event listener cleanup, layout thrashing, jank detection |
| Caching | HTTP caching headers, service worker caching, API response caching, memoization |
| Network | Request waterfall, redundant requests, payload size, compression, prefetching |
| Web Vitals | LCP, INP, and CLS optimization checks for web projects |
| Mobile | Widget rebuild optimization, const constructors, image sizing, list virtualization |
| Database | Query performance, N+1 detection, connection pooling, index usage |

**Scope boundary:** Performance-specific deep dive. Produces optimization recommendations with estimated impact. Fixes only low-risk optimizations (const constructors, unused imports, memoization). High-impact changes (architecture, caching strategy) report as `needs_approval`.

## Delegation

**Owns:** hygiene, types, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, performance (profiling via --perf) | **Delegates:** ds-simplify → overengineering / dead-code / orphan / premature-abstraction; ds-blueprint → bootstrap when `ds/audit/findings.md` absent or stale | **Receives:** ds-ship → Phase 2 rule audit

## Execution Flow

Setup → Analyze → [Gap Analysis] → [Plan] → Apply → [Needs-Approval] → Summary

### Phase 1: Setup [SKIP if --auto — except step 1 Recovery Check]

1. **Recovery check:** DETECT `ds/audit/review.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read files referenced by pending findings, discard findings whose file:line changed), skip `done` phases, announce `[REV] Resuming from Phase {N}: {name}. Phases 1-{N-1} complete.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start, append if missing.
2. **State `data` shape:** `{ mode, scopes_selected, scopes_done[], findings[{id, severity, file, line, scope, title, disposition}], fixed_count, failed_count, needs_approval[] }`.
3. Pre-flight: check if git repo (optional, warn if not)
4. **IDU:** Profile → Config.priorities, Config.quality, Current Scores, Toolchain, Type+Stack. Findings(security, hygiene, types, performance, architecture, patterns) → verify + use. Absent → own analysis.
5. **Mode selection.** If no `--tactical`/`--strategic`/`--perf` flag, ask:
   - **Tactical** — file-level fixes: security, hygiene, types, performance, privacy (9 scopes)
   - **Strategic** — architecture-level: patterns, coupling, testing, production readiness (8 scopes)
   - **Performance** — deep profiling: bundle size, startup time, memory, caching, Core Web Vitals
6. **Scope selection.** If no `--scope` flag, ask which scopes to check (default: all for selected mode)
7. If uncommitted changes detected, ask: continue / stash first / cancel

**Gate:** Mode and scope selection confirmed (explicitly or via flags). If fails → re-present the mode/scope menu; if the user declines all options or gives no response after 2 prompts, exit with WARN "No mode selected — run /ds-review with --tactical, --strategic, or --perf to proceed."

### Phase 2: Analyze

**Findings bootstrap rule.** Before any analysis:
1. `ds/audit/findings.md` absent → invoke `/ds-blueprint --preview --scope=all`, wait for completion, re-read. Skill owns detection SSOT; re-implementing it here is duplicate work.
2. `ds/audit/findings.md` exists but `git_hash` ≠ HEAD → invoke `/ds-blueprint --refresh`, wait for completion, re-read.
3. `ds/audit/findings.md` exists + fresh → proceed.

The auto-invoke step MAY be skipped via `--no-bootstrap` for testing, in which case the review runs its own scope analysis per the legacy path below.

**Findings file check:** If `ds/audit/findings.md` exists and its `git_hash` matches current HEAD, filter findings by active scopes. Per matching finding:
1. Read file:line and surrounding context (±10 lines)
2. Verify finding is still valid (code may have changed since analysis)
3. If confirmed → add to fix list. If false positive or already resolved → classify as `not-applicable` (false positive) or `already-resolved` and record in state file with reason; both count as Skipped in the FRC accounting.
4. After verification, proceed to fix confirmed findings.

Skip own analysis for scopes covered by findings file. For scopes NOT in findings file, run own analysis below.

**If no findings file after bootstrap or `--no-bootstrap`:** Analyze codebase in batches of 2 scope groups. Each batch receives scope definitions from appropriate references file.

**Tactical analysis** prompts focus on: grep for patterns, read context (50 lines), score findings by severity. For repository hygiene (committed binaries, secrets): verify files are git-tracked via `git ls-files`.

**Strategic analysis** prompts focus on: evaluate patterns across codebase, flag structural issues even if not auto-fixable, question consistency not just correctness.

Cross-scope dedup: merge findings at same file:line, keep highest severity.

**Skip patterns:** `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING`, platform guards, test fixtures.

Wait for all batches before proceeding.

**Gate:** If findings = 0 -> print "All {N} checks evaluated across {scopes}: 0 findings" confirmation line, then skip to summary. This distinguishes a clean result from a skipped analysis. If fails (analysis incomplete or bootstrap invocation of /ds-blueprint did not return) → mark affected scopes as `inconclusive` in state, log "bootstrap incomplete — scopes {names} unanalyzed", proceed to summary with partial results and WARN status.

**CRITICAL escalation:** If any CRITICAL finding detected, re-read full file section (±20 lines around finding) and verify it's genuine CRITICAL — not false positive from pattern matching. If evidence is insufficient, downgrade to HIGH. Only confirmed CRITICALs proceed to fix plan.

### Phase 3: Gap Analysis (strategic only)

Calculate gaps: current vs ideal metrics for coupling, cohesion, complexity, coverage. Use project-type defaults:

| Type | Coupling | Cohesion | Complexity | Coverage |
|------|----------|----------|------------|----------|
| cli | <40% | >75% | <10 | 70%+ |
| library | <30% | >80% | <8 | 85%+ |
| api | <50% | >70% | <12 | 80%+ |
| web | <60% | >65% | <15 | 70%+ |
| mobile | <55% | >65% | <12 | 65%+ |
| devtool | <35% | >75% | <10 | 80%+ |

Display Current vs Ideal table. Technology assessment: evaluate key decisions as OK / Questionable / Problematic (with evidence). Include only Questionable/Problematic.

Categorize recommendations by effort/impact: Quick Win -> Moderate -> Complex -> Major.

**Gate:** Current vs Ideal table and categorized recommendations produced. If fails → for any metric that could not be computed (e.g., coverage tool absent, coupling analysis incomplete), insert a `?` in the Current column with a note "metric unavailable — {reason}", output the partial table, and continue; do not block on missing metrics.

### Phase 4: Plan Review (skip if --auto)

Print findings table (ID, severity, title, file:line). Ask:

- **Fix All** (recommended) — apply all fixable findings
- **By Severity** — choose which severities to fix
- **Review Each** — approve each finding individually
- **Report Only** — no fixes, just the report

**Gate:** User selected a plan action (Fix All / By Severity / Review Each / Report Only). If fails → re-present the four options once; if no selection after 2 attempts, default to Report Only and note the default in state.data.plan_action.

### Phase 5: Apply [SKIP if --preview]

Apply fixes grouped by file:
- Different files: parallel
- Same file: sequential (re-read after each edit)
- Minimal diff, preserve surrounding code style
- Before adding any import/API, verify it exists in codebase or dependencies
- Cross-module change: report as `needs_approval`

After all fixes: run available lint/type/test checks. If fixes introduce new errors, repeat fix-verify (max 3 iterations).

**Loop mode (`--loop`):** After applying fixes:
1. Re-read all modified files + their direct dependents (importers, callers)
2. Re-analyze for new findings caused by fixes (cascade breakage)
3. If new findings found, apply fixes for new findings
4. Max 3 iterations. If still finding issues after 3 loops, report remaining and stop.

Per fix, include education: why (impact if unfixed), avoid (anti-pattern), prefer (correct pattern).

**Gate:** All approved fixes applied and lint/type/test checks pass (or max 3 fix-verify iterations exhausted). If fails → revert the offending fix via `git checkout -- {file}`, record the finding as `failed` in state.data.findings with the lint/type/test error captured, and continue applying remaining approved fixes.

### Phase 5a: Needs-Approval Review [CONDITIONAL]

Items flagged `needs_approval` (cross-module changes, architectural decisions):
- **--auto without --force-approve:** List items, skip them, note in summary
- **--force-approve:** Apply all needs_approval items without asking
- **Interactive:** Present needs_approval items. Ask: Apply All / Review Each / Skip All

**Gate:** All needs_approval items resolved (applied, skipped, or deferred). If fails → if the user declined to respond, mark all unresolved items as `deferred` in state.data.needs_approval and record `deferred (user did not respond)` as disposition; proceed to Phase 5b.

### Phase 5b: CRITICAL Escalation

If any CRITICAL finding detected: flag for manual review before auto-fixing. In interactive mode, show finding with full context and ask for explicit confirmation. CRITICAL findings should be verified with extra scrutiny — re-read file section and surrounding context.

**Gate:** Every CRITICAL finding explicitly confirmed or downgraded before fix. If fails (user does not respond to confirmation prompt) → do not apply the CRITICAL fix; mark the finding as `deferred (awaiting manual review)` in state.data.findings, include it in the Needs Approval section of the summary, and continue with non-CRITICAL fixes.

### Phase 6: Loop (--loop flag, tactical only)

If applied > 0:
1. Cascade check — verify dependent files don't need updates
2. Re-analyze modified + cascade-affected files
3. Re-apply for new findings

Max 3 iterations. Summary shows per-iteration breakdown.

**Gate:** Zero new findings on re-analysis, or max 3 iterations reached. If fails (new findings still appear after 3 iterations) → record remaining findings in state.data.findings with disposition `open (loop exhausted)`, set summary status to WARN, and report the count of unresolved cascade findings to the user.

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

**Auto output:** `refactor: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N`

Status: OK (failed=0), WARN (failed>0 no CRITICAL), FAIL (CRITICAL unfixed or error).

**Gate:** Summary table printed and `fixed + failed + skipped + needs_approval + not_applicable = total` verified. Every finding has a disposition. If fails (accounting does not balance) → identify findings missing a disposition, assign `failed (disposition missing)` to each, reprint the summary table, and set status to WARN so the imbalance is visible.

## Score Calculation

```
base_score = 100
CRITICAL: -25, HIGH: -10, MEDIUM: -3, LOW: -1
scope_score = max(0, base_score + sum(penalties))
```

Cap: any CRITICAL -> max 40, 3+ HIGH -> max 60.

## Quality Gates

- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/review.json` updated per scope + per fix, gitignored, deleted on successful Summary.
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
