# /ds-review

Code review catches what tests miss — security holes, dead code, wrong abstractions, and performance traps hiding in plain sight. This skill scans for all of them with file:line precision.

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
- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- Every finding receives a disposition in the summary — zero silent drops (FRC)

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
| Bundle | Bundle size analysis, tree-shaking, unused dependencies, dynamic imports |
| Startup | Cold start time, critical rendering path, lazy initialization, deferred loading |
| Runtime | Memory leaks, event listener cleanup, layout thrashing, jank detection |
| Caching | HTTP caching headers, service worker caching, API response caching, memoization |
| Network | Request waterfall, redundant requests, payload size, compression, prefetching |
| Web Vitals | LCP, INP, and CLS optimization checks for web projects |
| Mobile | Widget rebuild optimization, const constructors, image sizing, list virtualization |
| Database | Query performance, N+1 detection, connection pooling, index usage |

**Scope boundary:** Performance-specific deep dive. Produces optimization recommendations with estimated impact. Fixes only low-risk optimizations (const constructors, unused imports, memoization). High-impact changes (architecture, caching strategy) report as `needs_approval`.

## Execution Flow

Setup → Analyze → [Gap Analysis] → [Plan] → Apply → [Needs-Approval] → Summary

### Phase 1: Setup [SKIP if --auto]

1. Pre-flight: check if git repo (optional, warn if not)
2. **Upstream check:** Search for `## Blueprint Profile` in known instruction files. If found:
   - **Config.priorities** → order scope execution by user priorities
   - **Config.quality** → calibrate severity (prototype: skip LOW, enterprise: flag all)
   - **Current Scores** → start analysis with lowest-scoring dimensions
   - **Project Map.Toolchain** → know existing patterns, avoid incompatible suggestions
   - **Type + Stack** → skip own project detection
3. Recovery check: if progress artifact exists from prior run, ask: Resume / Start fresh
4. **Mode selection.** If no `--tactical`/`--strategic`/`--perf` flag, ask the user:
   - **Tactical** — file-level fixes: security, hygiene, types, performance, privacy (9 scopes)
   - **Strategic** — architecture-level: patterns, coupling, testing, production readiness (8 scopes)
   - **Performance** — deep profiling: bundle size, startup time, memory, caching, Core Web Vitals
5. **Scope selection.** If no `--scope` flag, ask which scopes to check (default: all for selected mode)
6. If uncommitted changes detected, ask: continue / stash first / cancel

**Gate:** Mode and scope selection confirmed (explicitly or via flags).

### Phase 2: Analyze

**Findings file check:** If `.ds-findings.md` exists and its `git_hash` matches current HEAD, filter findings by the active scopes. For each matching finding:
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

**CRITICAL escalation:** If any CRITICAL finding detected, re-read the full file section (±20 lines around the finding) and verify it's a genuine CRITICAL issue — not a false positive from pattern matching. If evidence is insufficient, downgrade to HIGH. Only confirmed CRITICALs proceed to the fix plan.

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

**Gate:** Current vs Ideal table and categorized recommendations produced.

### Phase 4: Plan Review (skip if --auto)

Present findings table (ID, severity, title, file:line). Ask the user:

- **Fix All** (recommended) — apply all fixable findings
- **By Severity** — choose which severities to fix
- **Review Each** — approve each finding individually
- **Report Only** — no fixes, just the report

**Gate:** User selected a plan action (Fix All / By Severity / Review Each / Report Only).

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
2. Re-analyze for new findings caused by the fixes (cascade breakage)
3. If new findings found, apply fixes for the new findings
4. Max 3 iterations. If still finding issues after 3 loops, report remaining and stop.

For each fix, include education: why (impact if unfixed), avoid (anti-pattern), prefer (correct pattern).

**Gate:** All approved fixes applied and lint/type/test checks pass (or max 3 fix-verify iterations exhausted).

### Phase 5a: Needs-Approval Review [CONDITIONAL]

Items flagged `needs_approval` (cross-module changes, architectural decisions):
- **--auto without --force-approve:** List items, skip them, note in summary
- **--force-approve:** Apply all needs_approval items without asking
- **Interactive:** Present needs_approval items. Ask: Apply All / Review Each / Skip All

**Gate:** All needs_approval items resolved (applied, skipped, or deferred).

### Phase 5b: CRITICAL Escalation

If any CRITICAL finding is detected: flag for manual review before auto-fixing. In interactive mode, show the finding with full context and ask for explicit confirmation. CRITICAL findings should be verified with extra scrutiny — re-read the file section and surrounding context.

**Gate:** Every CRITICAL finding explicitly confirmed or downgraded before fix.

### Phase 6: Loop (--loop flag, tactical only)

If applied > 0:
1. Cascade check — verify dependent files don't need updates
2. Re-analyze modified + cascade-affected files
3. Re-apply for new findings

Max 3 iterations. Summary shows per-iteration breakdown.

**Gate:** Zero new findings on re-analysis, or max 3 iterations reached.

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

**FRC accounting:** Every finding from the Analyze phase appears with a disposition (fixed, failed, skipped, needs-approval, not-applicable). `fixed + failed + skipped + needs_approval + not_applicable = total`.

**DSC verification:** Each scope reports how many checks were evaluated vs how many produced findings. Scopes with zero findings listed as clean.

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

**Gate:** Summary table printed and `fixed + failed + skipped + needs_approval + not_applicable = total` verified. Every finding has a disposition.

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
