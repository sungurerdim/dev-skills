# /ds-review

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
- Fully functional standalone — uses `.findings.md` for optimization when available

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

Without flags: present mode selection to the user.

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

**Scope boundary:** Architecture-level assessment. Questions design decisions, evaluates pattern consistency. Does NOT fix individual code issues (unused imports, type errors, formatting).

### Performance Scopes (--perf)

Deep performance analysis beyond the tactical `performance` scope. Checks areas that require profiling-level analysis.

| Group | Checks |
|-------|--------|
| Bundle | Bundle size analysis, tree-shaking effectiveness, unused dependencies, dynamic imports (web); unused packages, APK/IPA size analysis (mobile) |
| Startup | Cold start time, critical rendering path, lazy initialization, deferred loading; TTID <2s / TTFD <4s targets (mobile) |
| Runtime | Memory leaks, event listener cleanup, DOM thrashing, layout thrashing, jank detection (web); unnecessary widget rebuilds, `saveLayer()` overhead (mobile) |
| Caching | HTTP caching headers, service worker caching, API response caching, memoization (web); local DB cache-then-network, stream-based repository pattern (mobile) |
| Network | Request waterfall, redundant requests, payload size, compression, prefetching |
| Web Vitals | LCP (preload check, `fetchpriority="high"`, render-blocking CSS), INP (long task detection, `scheduler.yield()`, `content-visibility: auto`), CLS (missing `width`/`height` on images/videos, missing `min-height` on dynamic slots) — web projects |
| Mobile | Widget rebuild optimization (Riverpod `select()`), const constructors, `Opacity` widget anti-pattern, `AnimatedBuilder` with `child` parameter, image sizing, list virtualization — mobile projects |
| Database | Query performance, N+1 detection, connection pooling, index usage |

**Scope boundary:** Performance-specific deep dive. Produces optimization recommendations with estimated impact. Fixes only low-risk optimizations (const constructors, unused imports, memoization). High-impact changes (architecture, caching strategy) report as `needs_approval`.

## Execution Flow

Setup → Analyze → [Gap Analysis] → [Plan] → Apply → [Needs-Approval] → Summary

### Phase 1: Setup [SKIP if --auto]

1. Pre-flight: check if git repo (optional, warn if not)
2. Recovery check: if progress artifact exists from prior run, ask: Resume / Start fresh
3. **Mode selection.** If no `--tactical`/`--strategic`/`--perf` flag, ask the user:
   - **Tactical** — file-level fixes: security, hygiene, types, performance, privacy (9 scopes)
   - **Strategic** — architecture-level: patterns, coupling, testing, production readiness (8 scopes)
   - **Performance** — deep profiling: bundle size, startup time, memory, caching, Core Web Vitals
4. **Scope selection.** If no `--scope` flag, ask which scopes to check (default: all for selected mode)
5. If uncommitted changes detected, ask: continue / stash first / cancel

### Phase 2: Analyze

**Findings file check:** If `.findings.md` exists and its `git_hash` matches current HEAD, filter findings by the active scopes. For each matching finding:
1. Read the file:line and surrounding context (±10 lines)
2. Verify the finding is still valid (code may have changed since analysis)
3. If confirmed → add to fix list. If false positive or already resolved → discard silently.
4. After verification, proceed to fix confirmed findings.

Skip own analysis for scopes covered by the findings file. For scopes NOT in the findings file, run own analysis below.

**If no findings file or stale:** Analyze the codebase in batches of 2 scope groups. Each batch receives scope definitions from the appropriate references file.

**Tactical analysis** prompts focus on: grep for patterns, read context (50 lines), score findings by severity. For repository hygiene (committed binaries, secrets): verify files are git-tracked via `git ls-files`.

**Strategic analysis** prompts focus on: evaluate patterns across the codebase, flag structural issues even if not auto-fixable, question consistency not just correctness.

Cross-scope dedup: merge findings at same file:line, keep highest severity.

**Skip patterns:** `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING`, platform guards, test fixtures.

Wait for all batches before proceeding.

**Gate:** If findings = 0 -> skip to summary.

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

### Phase 4: Plan Review (skip if --auto)

Present findings table (ID, severity, title, file:line). Ask the user:

- **Fix All** (recommended) — apply all fixable findings
- **By Severity** — choose which severities to fix
- **Review Each** — approve each finding individually
- **Report Only** — no fixes, just the report

### Phase 5: Apply [SKIP if --preview]

Apply fixes grouped by file:
- Different files: parallel
- Same file: sequential (re-read after each edit)
- Minimal diff, preserve surrounding code style
- Before adding any import/API, verify it exists in codebase or dependencies
- Cross-module change: report as `needs_approval`

After all fixes: run available lint/type/test checks. If fixes introduce new errors, repeat fix-verify (max 3 iterations).

For each fix, include education: why (impact if unfixed), avoid (anti-pattern), prefer (correct pattern).

### Phase 5a: Needs-Approval Review [CONDITIONAL]

Items flagged `needs_approval` (cross-module changes, architectural decisions):
- **--auto without --force-approve:** List items, skip them, note in summary
- **--force-approve:** Apply all needs_approval items without asking
- **Interactive:** Present needs_approval items. Ask: Apply All / Review Each / Skip All

### Phase 5b: CRITICAL Escalation

If any CRITICAL finding is detected: flag for manual review before auto-fixing. In interactive mode, show the finding with full context and ask for explicit confirmation. CRITICAL findings should be verified with extra scrutiny — re-read the file section and surrounding context.

### Phase 6: Loop (--loop flag, tactical only)

If applied > 0:
1. Cascade check — verify dependent files don't need updates
2. Re-analyze modified + cascade-affected files
3. Re-apply for new findings

Max 3 iterations. Summary shows per-iteration breakdown.

### Phase 7: Summary

**Tactical output:**
```
refactor complete (tactical)
============================
| Scope          | Findings | Fixed | Failed |
|----------------|----------|-------|--------|
| security       |     3    |   3   |   0    |
| hygiene        |     5    |   4   |   1    |
| Total          |     8    |   7   |   1    |

Applied: 7 | Failed: 1 | Needs Approval: 0 | Total: 8
```

**Strategic output:**
```
refactor complete (strategic)
=============================
| Metric     | Current | Ideal | Gap  |
|------------|---------|-------|------|
| Coupling   |   55%   |  50%  | -5%  |
| Cohesion   |   68%   |  70%  | +2%  |
| Complexity |   14    |  12   | -2   |
| Coverage   |   82%   |  80%  |  OK  |

Recommendations by effort:
  Quick Win:  [PAT-05] Inconsistent error handling
  Moderate:   [ARC-03] Circular dependency
  Complex:    [TST-07] Missing integration tests

Applied: 4 | Failed: 0 | Needs Approval: 2 | Total: 6
```

**Auto output:** `refactor: {OK|WARN|FAIL} | Applied: N | Failed: N | Total: N`

Status: OK (failed=0), WARN (failed>0 no CRITICAL), FAIL (CRITICAL unfixed or error).

## Score Calculation

```
base_score = 100
CRITICAL: -25, HIGH: -10, MEDIUM: -3, LOW: -1
scope_score = max(0, base_score + sum(penalties))
```

Cap: any CRITICAL -> max 40, 3+ HIGH -> max 60.

## Severity Levels

| Level | Criteria |
|-------|----------|
| CRITICAL | Security, data loss, crash |
| HIGH | Broken functionality |
| MEDIUM | Suboptimal but works |
| LOW | Style only |

When uncertain, choose lower severity.

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No findings | Report clean score, skip fix phases |
| All findings are LOW | Report only, skip fix prompt |
| Single file project | Run all applicable scopes on that file |
