---
name: ds-review
description: Code improvement — tactical fixes plus strategic architecture alignment. Use when reviewing code for bugs, quality, or architectural fit.
---

# /ds-review

Code review catches what tests miss — security holes, dead code, wrong abstractions, and performance traps hiding in plain sight. Skill scans for all of them with file:line precision.

**Code Improvement** — Tactical fixes and strategic architecture alignment in a single skill.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-review`
- User asks to refactor, improve, or clean up code
- User asks about code quality, complexity, or architecture improvements
- User asks to reduce duplication, fix patterns, or improve maintainability

Four modes: `--tactical` for file-level quality fixes, `--strategic` for architecture-level assessment, `--perf` for deep performance profiling, `--meta-quality` for principle-based whole-project audit (SSOT/DRY/KISS/SoC + criteria-fit + consolidation paths).

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "improve code quality (tactical)", "review my architecture (strategic)" | "format and lint only" (→ ds-fix) |
| "deep performance profiling" | "set up perf budget + CI gate" (→ ds-launch --perf-budget) |
| "principle-based audit (SSOT / DRY / KISS / SoC)" | "score overall project health" (→ ds-blueprint) |
| "reduce duplication, improve maintainability" | "remove dead code / orphan files" (→ ds-simplify) |

## Contract

**Dimensions:** B1 (code quality), D1 (performance), D2 (resource economy), D9 (API contract breakage)
**Framework alignment (advisory):** ISO/IEC 25010 (B1), Google SRE PRR + Well-Architected Performance Efficiency (D1), Semantic Versioning (D9).

- Every fix cites file:line with before/after — no blind modifications. Only modifies lines required by the finding; no scope creep.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- State-exempt: fixes land in the working tree / commits as they are applied — git is the durable record; re-run re-verifies remaining findings.

## Arguments

| Flag | Effect |
|------|--------|
| `--tactical` | File-level fixes: security, hygiene, types, performance, privacy |
| `--strategic` | Architecture-level: patterns, coupling, testing, production readiness |
| `--perf` | Deep performance profiling: bundle size, startup, memory, caching, Core Web Vitals |
| `--meta-quality` | Principle-based whole-project audit: SSOT, DRY, KISS, SoC + criteria-fit + consolidation paths |
| `--meta-scope={list}` | Meta-quality scope(s): `ssot`, `dry`, `kiss`, `soc`, `api-surface`, `redundancy`, `all`. Default: `all` |
| `--criteria-fit` | Enable Phase 3b: project-ideal vs codebase-actual baselines from [references/criteria-fit.md](references/criteria-fit.md) |
| `--suggest-paths` | Enable Phase 4a path proposals: 3 consolidation paths per finding (effort / impact / risk) from [references/path-proposals.md](references/path-proposals.md) |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `needs-human`. |
| `--preview` | Analyze + report findings without applying fixes |
| `--scope={name}` | Specific scope(s), comma-separated; `all` forces a full-repo scan even when a diff exists |
| `--diff[={ref}]` | Force diff scoping explicitly: bare → working tree + staged vs HEAD; with `{ref}` → merge-base diff vs that ref. Redundant when a diff already exists — see Phase 1 default |
| `--loop` | Re-run until clean or max 3 iterations (tactical only) |

Default: mode resolves to All — tactical → strategic → meta-quality sequentially (`--perf` excluded unless explicit). `--ask`: present mode selection.

## Scopes

### Tactical Scopes (--tactical)

8 scopes, 86 checks. Definitions in [references/scopes-tactical.md](references/scopes-tactical.md). Detect/fix patterns for performance in [references/rules-performance.md](references/rules-performance.md).

| Group | Scopes |
|-------|--------|
| Security & Privacy | security, robustness, privacy |
| Code Quality | hygiene, types |
| Performance | performance |
| AI Cleanup | ai-hygiene, doc-sync |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| security | any source | — |
| hygiene | any source | — |
| types | any source | — |
| performance | any source | — |
| ai-hygiene | any source | — |
| robustness | any source | — |
| privacy | pii=yes or auth ≠ none or integrations contain an analytics SDK | N/A — no personal-data path detected |
| doc-sync | any source | — |

**Scope boundary:** file-level fixes within current architecture. Finds repeated code, unnecessary abstractions, missing types; architectural decisions stay out of scope — issue requiring architectural change → `needs_approval`.

### Strategic Scopes (--strategic)

9 scopes, 103 checks. Definitions in [references/scopes-strategic.md](references/scopes-strategic.md). Detect/fix patterns for architecture and testing in [references/rules-quality.md](references/rules-quality.md).

| Group | Scopes |
|-------|--------|
| Structure | architecture, patterns, cross-cutting, contract-consistency |
| Quality | testing, maintainability |
| Production Readiness | production-readiness |
| Completeness | functional-completeness, ai-architecture |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| architecture | any source | — |
| patterns | any source | — |
| cross-cutting | any source | — |
| contract-consistency | any source | — |
| testing | any source | — |
| maintainability | any source | — |
| production-readiness | deploy ≠ none | N/A — deploy=none (library/CLI, no long-running process) |
| functional-completeness | ui ≠ none or api ≠ none | N/A — no user-facing surface detected |
| ai-architecture | integrations contain an LLM SDK or product-facing LLM features detected | N/A — no LLM integration detected |

**Per-scope mandatory checks** — each scope is evaluated against a named principle set, and the finding title cites the principle it violates:

| Scope | Principle set |
|-------|---------------|
| architecture, patterns | SOLID + GRASP — [../core/principles.md §2](../core/principles.md) |
| production-readiness | Reliability patterns — [../core/principles.md §4](../core/principles.md) |
| testing | Testing discipline — [../core/principles.md §7](../core/principles.md) |
| contract-consistency | One concept → one name across the codebase; flag only after 3+ concrete examples of the same lexicon drift |

**Taste-dependent judgment → rubric, not rules.** Where a scope turns on "is this the right abstraction" there is no pattern to grep, so the strategic pass is closed by a verifier run against [references/rubric-architecture.md](references/rubric-architecture.md): five dimensions, a level per dimension, each level claimed only with a `file:line` example of the named signal. Delegate it as its own pass with the rubric as the whole contract; the returned levels are untrusted until the cited lines are re-read. Rule-shaped findings stay in `rules-quality.md` — the rubric covers only what a rule cannot express.

**Scope boundary:** architecture-level assessment. Questions design decisions, evaluates pattern consistency. Individual code issues (unused imports, type errors, formatting) stay out of scope — they belong to `--tactical`.

### Performance Scopes (--perf)

Deep performance analysis beyond the tactical `performance` scope: 11 check groups spanning bundle, startup, runtime, caching, network, Web Vitals, mobile, database, cost, resource economy, and scale envelope. Group definitions in [references/scopes-performance.md](references/scopes-performance.md).

**Signal:** any source — `--perf` is explicit opt-in, so no group is excluded by project signal.

**Scope boundary:** performance-specific deep dive. Produces optimization recs with estimated impact, each backed by a before/after measurement. Fixes only low-risk (const constructors, unused imports, memoization). High-impact changes (architecture, caching strategy) → `needs_approval`.

### Meta-Quality Scopes (--meta-quality)

5 detector scopes — `ssot`, `dry`, `kiss`, `soc`, `api-surface` — plus 1 derived alias (`redundancy` = dry+duplicate constants) and `all`. Detector thresholds and per-scope rules: [references/meta-quality-scopes.md](references/meta-quality-scopes.md).

**Signal:** any source — these are universal code-quality principles, not gated by project signal once `--meta-quality` is selected.

**Delegated scopes.** `yagni`, `obsolete`, and function/module-level `duplicate` detection are not run here — ds-simplify present → delegate; absent → one inline dead-export grep (zero cross-file references) with the gap-note `[scope] not analyzed — requires ds-simplify`. Detail: [references/meta-quality-scopes.md](references/meta-quality-scopes.md).

**Scope boundary:** principle-level audit. Flags violations of SSOT / DRY / KISS / SoC, evaluates project criteria fit, proposes consolidation paths. Fixes only on explicit user selection — every finding produces 3 path proposals (effort / impact / risk).

**Anti-overengineering 3-gate:** report a finding only when at least one harm signal is present — it breaks something, it misleads a future reader about what is canonical, or it is not worth its keep. No signal → silently discard, counted in the summary as `discarded (no harm signal)`. Full gate with the tie-breaking rule: [../core/principles.md §9](../core/principles.md).

## Delegation

**Owns:** perf-profiling (deep, `--perf` mode) | **Delegates:** ds-simplify → overengineering / dead-code / orphan / premature-abstraction; ds-blueprint → bootstrap when `ds/audit/findings.md` absent or stale | **Receives:** ds-fix → code-level quality fixes; ds-ship → Phase 2 rule audit. Verified consumer of ds-blueprint findings (hygiene, types, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, contract-consistency, performance): verifies + fixes, does not re-produce.; ds-freeze → flag-gate defer-hidden items

## Execution Flow

**Tactical / Strategic / Perf:**
Setup → Analyze → [Gap Analysis] → [Plan] → Apply → [Needs-Approval] → Summary

**Meta-Quality:**
Setup → Analyze-Principles → [Criteria-Fit] → [Suggest-Paths] → Apply (gated) → [Needs-Approval] → Summary

### Phase 1: Setup [--ask]

1. Pre-flight: `git rev-parse --is-inside-work-tree` → `true` (non-zero exit → warn, continue — git optional).
2. **Upstream artifacts:** Profile → Config.priorities, Config.quality, Current Scores, Toolchain, Type+Stack. Findings(security, hygiene, types, performance, architecture, patterns) → verify + use. Absent → own analysis.
3. **Mode selection.** Default: All — tactical → strategic → meta-quality sequentially (`--perf` excluded unless explicit) — recorded in the summary. A disambiguating mode flag always resolves it without asking. `--ask` with no mode flag → present a menu covering every mode, each with a one-line what-it-does: All (recommended) — tactical → strategic → meta-quality sequentially (skip --perf unless explicit) / Tactical — file-level quality fixes / Strategic — architecture-level assessment / Performance — deep perf profiling / Meta-Quality — principle-based whole-project audit / (Cancel).
4. **Scope selection.** Default: every scope for the selected mode. `--ask` with no `--scope` → ask which scopes.
5. **Diff-default resolution.** `--scope=all` → full-repo scan, skip this step. Otherwise detect whether a diff exists and scope to it automatically (an explicit `--diff[={ref}]` forces the same resolution against the named ref):
   - Base branch: `git symbolic-ref -q refs/remotes/origin/HEAD`, stripped of `refs/remotes/origin/`; unresolved → `main`; that absent too → `master`.
   - Change set: `git diff --name-only` (working tree) ∪ `git diff --name-only --cached` (staged) ∪ `git diff --name-only origin/{base}...HEAD` (branch vs base; skip this leg when `origin/{base}` does not resolve).
   - Any non-empty → scope every selected scope to that file set plus direct consumers (importers/callers — W2). All empty → full-repo scan.
6. **Checkpoint pre-gate** ([../core/checkpoint-protocol.md](../core/checkpoint-protocol.md)): `git status --porcelain` → non-empty. Default: proceed where the planned fixes are disjoint from the dirty paths; a fix that targets a dirty file resolves `needs-human` (a revert would discard the user's uncommitted edits) instead of touching it. `--ask`: Commit first (recommended) / Stash / Proceed anyway (state the risk: failed fixes are reverted via `git checkout -- {file}`, which also discards uncommitted edits in that file) / Cancel.

**Gate:** Mode + scope resolved (flag, default, or `--ask` confirmation). If fails → re-present under `--ask`; user declines / no response after 2 prompts → exit with WARN "No mode selected — run /ds-review with --tactical, --strategic, --perf, or --meta-quality to proceed."

### Phase 2: Analyze

**Findings bootstrap** (before any analysis — blueprint owns detection SSOT; re-implementing it here is duplicate work):

| `ds/audit/findings.md` state | Action |
|-------------------------------|--------|
| Fresh (`git_hash == HEAD`, produced in the current run-cycle; a prior-cycle file — however recent — counts as stale) | Verify + fix from it: filter by active scopes; per matching finding read file:line + context (±10 lines), confirm still valid; confirmed → fix list; false positive or already resolved → `not-applicable` / `already-resolved` (both count as Skipped). Skip own analysis for the scopes it covers. |
| Stale or absent, and `/ds-blueprint` is present | Invoke `/ds-blueprint --refresh` (absent entirely → `--preview --scope=all`), wait for completion, re-read, then apply the row above. |
| `/ds-blueprint` is absent | Run own scope analysis (below); append results with `source: ds-review` and the current `git_hash`. |

Scopes the findings file does not cover always run own analysis regardless of row.

**Own analysis** (scopes not covered above, or no findings file at all): analyze in parallel-planned batches grouped by cost. Announce plan before starting.

| Batch | Active scopes (subset of selected) | Concurrency |
|-------|-----------------------------------|-------------|
| Read-only | hygiene, types, doc-sync, ai-hygiene | Parallel |
| AST | architecture, patterns, cross-cutting, performance | Parallel (shared LSP cache) |
| Cross-file / opus-grade | security, privacy, ai-architecture, production-readiness, testing | Serial |

**Tactical analysis:** grep for patterns, read context (50 lines), score findings by severity. For repository hygiene (committed binaries, secrets): verify via `git ls-files`.

**Diff scope in effect (resolved in Phase 1):** every selected scope runs on the resolved file set plus direct consumers only. Findings-file entries outside the set → out of scope for this run, not skipped: exclude from disposition totals, note count once in summary.

**Strategic analysis:** evaluate patterns across codebase, flag structural issues even if not auto-fixable, question consistency not just correctness.

Cross-scope dedup: merge findings at same file:line, keep highest severity. **Skip patterns:** `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING`, platform guards, test fixtures. Wait for all batches before proceeding.

**Anti-overengineering 3-gate:** every candidate finding — tactical, strategic, perf, or meta-quality — is screened before it is reported. Report only when at least one harm signal is present: it breaks something now or on a predictable path, it misleads a future reader about what is canonical, or it is not worth its keep. No signal → silent discard, counted `discarded (no harm signal): {n}` in the summary. Full gate with the tie-breaking rule: [../core/principles.md §9](../core/principles.md).

**Confidence gate:** every finding records a confidence score 0-10 beside severity. Non-CRITICAL findings scoring below 8 → move to a `low-confidence` rollup (count + one-line list in the summary), excluded from the default fix list; user promotes individual items via Review Each. CRITICAL findings below 8 → route through CRITICAL escalation below rather than dropping.

**Negation-shaped checks (production-readiness, security scopes):** "missing X" findings (missing timeout, absent retry, no input validation) are the weakest class for probabilistic review — confirm each by enumerating the relevant call sites and showing X absent at each; pattern-absence alone is insufficient evidence. Deterministic rule scanner configured in the project (semgrep/opengrep class) → run its matching rules as cross-check; absent → the call-site enumeration stands as the evidence.

**Gate:** Every selected scope analyzed with a recorded finding count. Findings = 0 → print `"All {N} checks evaluated across {scopes}: 0 findings"`, skip to summary. Distinguishes clean from skipped. If fails (analysis incomplete or bootstrap `/ds-blueprint` didn't return) → mark affected scopes `inconclusive`, log "bootstrap incomplete — scopes {names} unanalyzed", proceed to summary with partial results + WARN status.

**CRITICAL escalation:** any CRITICAL finding → re-read full file section (±20 lines), verify genuine — not pattern-matching false positive. Then an adversarial re-check, CRITICAL findings only (a same-context review anchors to the analysis that produced the finding and rubber-stamps it): fresh context available (a second pass that receives only the cited code + finding text, none of the producing analysis) → have it re-derive the finding from that evidence alone; unavailable → re-derive in-session from a clean re-read of the cited lines, writing the evidence down before consulting the original rationale. Re-derivation diverges or evidence insufficient → downgrade to HIGH. Only confirmed CRITICALs proceed. Keep this pass CRITICAL-scoped — critique loops on high-confidence trivial findings degrade accuracy.

### Phase 3: Gap Analysis (strategic only)

Calculate gaps: current vs ideal for coupling, cohesion, complexity, coverage — load the per-project-type ideal thresholds from [references/scopes-strategic.md § Gap Thresholds](references/scopes-strategic.md).

Display Current vs Ideal table. Technology assessment: evaluate key decisions OK / Questionable / Problematic (with evidence) — include only Questionable/Problematic. Categorize recs by effort/impact: Quick Win → Moderate → Complex → Major.

**Gate:** Current vs Ideal table + categorized recs produced. If fails → metric uncomputable (coverage tool absent, coupling analysis incomplete) → insert `?` in Current column with note "metric unavailable — {reason}", output partial table, continue; do not block on missing metrics.

### Phase 3a: Analyze-Principles (--meta-quality only)

Per active meta-scope from [references/meta-quality-scopes.md](references/meta-quality-scopes.md):

1. Apply detector rule with stated threshold + AST/token similarity gate.
2. Run anti-overengineering 3-gate — any harm signal present → keep the finding; no signal → discard, counted `discarded (no harm signal)` in the summary.
3. Cross-scope dedup: merge same file:line, keep highest-confidence.
4. Record finding: file:line, scope, principle name, evidence (cited code), confidence.

Skip patterns: test fixtures, generated files, framework-required boilerplate, public-API signatures, `# intentional`, `_` prefix.

**Gate:** Every active meta-scope produces a result (finding count or `0 findings`). If fails (detector can't run, e.g. AST tool unavailable) → mark scope `inconclusive`, log "{scope} detector unavailable — {reason}", proceed with remaining.

### Phase 3b: Criteria-Fit (--meta-quality + --criteria-fit)

Compare project's implied/stated criteria to baselines for detected type. Baselines in [references/criteria-fit.md](references/criteria-fit.md).

1. Detect type from blueprint profile (or own detection if absent).
2. Load the baseline thresholds for that type from the criteria-fit reference — the per-type table there is the single canonical home.
3. Compare findings vs baseline. Above baseline → flag as `criteria-mismatch`.
4. Mismatch → default: tighten the codebase (the stricter default) unless the codebase's own committed conventions already document the looser criteria in ≥3 files, recording the reasoning in the summary. `--ask`: ask user: "{scope} count ({n}) exceeds {type} baseline ({max}). Loosen criteria for this project or tighten the codebase?"

**Gate:** Criteria-fit assessment recorded for each active scope. If fails (type undetected + user declines to specify) → use generic baselines, mark assessment `low-confidence`, proceed.

### Phase 4a: Suggest-Paths (--meta-quality + --suggest-paths)

For each finding from Phase 3a, generate 3 paths from [references/path-proposals.md](references/path-proposals.md):

- **Path A — Minimal:** delete duplicates only, no abstraction
- **Path B — Moderate:** extract a shared module / helper
- **Path C — Structural:** unify the API / abstraction at a higher level

Each path includes: estimated effort (hours), impact (scope reach), risk (regression surface), rollback approach. Present paths grouped by finding. Default: each finding resolves to Path B (Moderate), the lowest-risk fix that doesn't leave duplication in place; findings with no safely automatable path resolve `Skip`; both recorded with reasoning in the summary. `--ask`: user selects per-finding: `Path A / B / C / Skip / Apply same path to all matching findings`.

**Gate:** Every finding has selected path or explicit `Skip`. If fails → assign `skip (no path selected)`, proceed.

### Phase 4: Plan Review [--ask]

Default: resolves to Fix All (respecting the confidence gate and CRITICAL escalation below), with reasoning recorded in the summary. `--ask`: print findings table — one line per finding (ID, severity, title, file:line) grouped by severity with counts; state the question (`Fix which of these N findings?`). Ask: Fix All (recommended) / By Severity (per-severity bulk `Fix all CRITICAL`/`Fix all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Report Only. "All" = exactly the displayed set. **LOW-noise cap:** LOW findings appear as per-scope count rows (`LOW: {n} in {scope}`) in this table; selecting Review Each or `Fix all LOW` first prints the itemized LOW list (one line each), so any "all" still names exactly the displayed set — the count always shows, the noise stays rolled up.

**Gate:** User selected plan action. If fails → re-present once; no selection after 2 attempts → default Report Only, note the default in the run summary.

### Phase 5: Apply [SKIP if --preview]

Apply fixes grouped by file: different files parallel; same file sequential (re-read after each edit); minimal diff, preserve surrounding style; before adding any import/API, verify it exists in codebase or deps; cross-module change → `needs_approval`.

**Mechanical Done Gate:** resolve `{check-cmd}` at setup — ds-quality enforcement arm installed (stop-hook / pre-commit hook / auto-lint) → use its gate command; else stack-native lint/type/test commands; none detectable → Verification-Infrastructure Gap: report it, offer `/ds-quality`, record the decision, never silently skip. Capture the baseline before the first fix; baseline red → done condition is "no *new* red", baseline reds reported as findings, never inherited as green. After each fix batch: run `{check-cmd}` — new errors introduced → repeat fix-verify with the same command (max 3 iterations). Before Phase 7: run the full `{check-cmd}` once — per-batch greens can compose into a red; the aggregate run's exact command + observed output is the Completion Evidence, and a new red blocks `OK`.

**Loop mode (`--loop`):** after applying: (1) re-read modified files + direct dependents (importers, callers); (2) re-analyze for new findings caused by fixes (cascade breakage); (3) new findings → apply fixes; (4) max 3 iterations — still issues after 3 → report remaining and stop.

Per fix, include education: **why** (impact if unfixed), **avoid** (anti-pattern), **prefer** (correct pattern).

**Gate:** All approved fixes applied + lint/type/test pass (or max 3 fix-verify exhausted). If fails → revert offending fix via `git checkout -- {file}`, record disposition `failed` on the finding with lint/type/test error captured, continue with remaining.

### Phase 5a: Needs-Approval Review [--ask, needs_approval > 0]

Items flagged `needs_approval` (cross-module changes, architectural decisions). Default: every item resolves automatically using the same impact/effort/risk reasoning an approval block would show, recorded in the summary; items matching the publish/irreversible exception list are skipped and recorded `needs-human` instead. `--ask`: state the question (`Approve these N items?`) and present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All resolved (applied, skipped, deferred). If fails → user declined → mark unresolved disposition `deferred (user did not respond)`, proceed.

### Phase 5b: CRITICAL Escalation

Any CRITICAL → verified with extra scrutiny before fixing — re-read file section + surrounding context. Default: CRITICAL fixes resolve automatically by best judgment, applied with the same scrutiny and recorded in the summary, unless the finding matches the publish/irreversible exception list, in which case it is skipped and recorded `needs-human`. `--ask`: show finding with full context, ask explicit confirmation before fixing.

**Gate:** Every CRITICAL explicitly confirmed or downgraded. If fails (user doesn't respond to confirmation) → do NOT apply CRITICAL fix; mark disposition `deferred (awaiting manual review)`, include in Needs Approval section of summary, continue with non-CRITICAL.

### Phase 6: Loop (--loop flag, tactical only)

Applied > 0: (1) cascade check — verify dependent files don't need updates; (2) re-analyze modified + cascade-affected files; (3) re-apply for new findings. Max 3 iterations. Summary shows per-iteration breakdown.

**Gate:** Zero new findings on re-analysis, or max 3 reached. If fails (new findings after 3) → record remaining findings disposition `open (loop exhausted)`, summary status WARN, report count of unresolved cascade findings.

### Phase 7: Summary

**Tactical output:**
```
refactor complete (tactical)
============================
| Scope          | Findings | Fixed | Skipped | Failed |
|----------------|----------|-------|---------|--------|
| {scope}        |   {n}    |  {n}  |   {n}   |  {n}   |
| Total          |   {n}    |  {n}  |   {n}   |  {n}   |

Fixed: {n} | Skipped: {n} | Failed: {n} | Needs Approval: {n} | Total: {n}
```

Disposition accounting — totals balance.

**Strategic output:**
```
refactor complete (strategic)
=============================
| Metric     | Current | Ideal | Gap  |
|------------|---------|-------|------|
| {metric}   | {n}     | {n}   | {n}  |

Recommendations by effort:
  Quick Win:  [{id}] {title}
  Moderate:   [{id}] {title}
  Complex:    [{id}] {title}

Fixed: {n} | Skipped: {n} | Failed: {n} | Needs Approval: {n} | Total: {n}
```

**Summary line:** `refactor: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n} | Discarded (no harm signal): {n}`

Status: OK (failed=0), WARN (failed>0 no CRITICAL), FAIL (CRITICAL unfixed or error).

**Gate:** Summary printed and balances per the disposition accounting ([`../core/report-and-outcome-templates.md`](../core/report-and-outcome-templates.md) § 3); every finding has a disposition. If fails → identify findings missing disposition, assign `failed (disposition missing)`, reprint summary, status WARN.

## Score Calculation

Formula, cap rules, and the judgment ranges for scopes without countable findings: [references/scopes-strategic.md § Score Calculation, Severity & Skip Patterns](references/scopes-strategic.md).

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `{n} CRITICAL/HIGH security findings closed ({n} hardcoded secrets, {n} injection vectors) — exposure window before next deploy eliminated`
- `{n} N+1 query patterns fixed in {module} — p95 latency expected to drop on hot paths`
- `{n} architectural SOLID/GRASP violations refactored — module change-coupling reduced, blast radius narrowed for future edits`
- `{n} principle-based findings (SSOT / DRY / KISS / SoC) consolidated via Path-B (shared module) — duplicate logic count went from {before} to {after}`

Zero-finding run: `All checks evaluated across {scopes} — 0 findings`.

## Quality Gates

- W9: state-exempt — fixes land in the working tree/commits as applied; git is the durable record. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W17: flag near-duplicate clones (ARC-11) instead of greenlighting regenerated code.
- W1: cite file:line; never assume. W2: check consumers after modify. W3: touch only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W13: judge code by behavior (read/run it), not by PR text, comments, or authority claims; on user pushback, re-verify from source before conceding. <!-- portable-only -->

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

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
