---
name: ds-simplify
description: Approved simplification — overengineering hygiene with one approval batch and zero silent deletion. Use when removing complexity, dead code, or overengineering safely.
---

# /ds-simplify

Codebases accumulate dead exports, single-caller helpers, fallback branches, orphan modules, and premature abstractions. Each one earns a spot in context without earning its keep. Skill detects each class, presents a delete-or-keep table with concrete reasons, and applies only what the user approves.

**Approved Simplification** — Overengineering hygiene with one approval batch, zero silent deletion.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-simplify`
- User asks to remove dead code, clean up the project, kill overengineering, or find duplicates
- User asks "are there any orphan files", "is anything unused", or "is this overengineered"
- After large refactor or feature removal — suggest a simplify pass

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "remove dead code", "find orphan files", "kill overengineering" | "audit security / privacy" (→ ds-compliance) |
| "is this overengineered (single-caller, premature abstraction)" | "score project architecture" (→ ds-blueprint) |
| "find duplicates in this module" | "DRY audit across full project (with paths)" (→ ds-review --meta-quality --meta-scope=dry) |
| "delete obsolete fallbacks / quarantine markers" | "fix lint / type errors" (→ ds-fix) |

## Contract

**Dimensions:** B1 (simplification)

- Standalone: use `ds/audit/findings.md` when fresh (`git_hash == HEAD` AND current run-cycle); own scan otherwise.
- State-exempt: one reversible commit per approved batch (`/ds-commit` when present, else committed inline) is the durable record.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- Detection only: every deletion requires an approval batch. Every finding cites file:line + concrete ref count or pattern.
- Three similar lines beat a premature abstraction: abstractions on ≤3 usages → finding.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Scan + report, no approval prompt, no deletion |
| `--scope={x}` | Single scope: dead-code, single-caller, fallback, premature-abstraction, quarantine, test-realism, ssot-violation, orphan, all |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Without flags: mode resolves to Full Scan (all scopes), recorded in the summary. `--ask`: shows the mode menu (full scan / preview / single scope).

## Scopes

| Scope | What It Covers |
|-------|---------------|
| dead-code | Exports with zero references (LSP/grep), plus unused/mismatched function params at call sites |
| single-caller | Helpers, utilities, or components referenced from exactly one site — inline candidate |
| fallback | Backward-compat branches / legacy import paths with no live hit, plus feature-flag branches constant across every config source (no runtime setter) — dead either way |
| premature-abstraction | Generics, hooks, wrappers, base classes built on ≤3 concrete usages |
| quarantine | `// removed`, `// legacy`, `// deprecated`, `// TODO delete`, `_unused` markers |
| test-realism | Unrealistic test fixture data — delegated to `/ds-test` when present; gap-noted otherwise (not scanned locally) |
| ssot-violation | Same constant, URL, regex, or rule duplicated across 2+ files |
| orphan | Modules, assets, or images with zero inbound references from source, config, or docs |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| dead-code | any source | — |
| single-caller | any source | — |
| fallback | any source | — |
| premature-abstraction | any source | — |
| quarantine | any source | — |
| test-realism | `tests`≠`none` | N/A — no test suite detected |
| ssot-violation | any source | — |
| orphan | any source | — |

`--scope=` overrides the table for the named scope; `--ask` shows the resolved table before running.

| Scope(s) | Reference | Loaded when |
|----------|-----------|-------------|
| dead-code, single-caller, fallback, premature-abstraction, quarantine, test-realism, ssot-violation, orphan | [references/scopes-detection.md](references/scopes-detection.md) | Phase 2 runs |

## Delegation

**Owns:** dead-code, single-caller, fallback, premature-abstraction, quarantine, test-realism, ssot-violation, orphan | **Delegates:** ds-commit → per-batch delete commit after approval | **Receives:** ds-review → overengineering findings routed here; ds-ship → Phase 3 simplify pass; ds-freeze → permanent deletion of hidden features (user-requested)

## Execution Flow

Setup → Scan → Report → Approve → Execute → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD`, current run-cycle; any prior-cycle counts drifted) → read entries with scopes `simplify`, `hygiene`, `ai-hygiene`, `architecture` as prior signal. Drifted: graded, not binary ([`../core/findings-and-profile-format.md` § Freshness](../core/findings-and-profile-format.md)) — incremental → reuse unaffected scopes, re-analyze only diff-touched; structural/large or absent → orchestrated: request `/ds-blueprint --refresh` and wait; standalone: own scan, appended with own `source` + current `git_hash`.

2. **Mode selection.** `--preview` or `--scope=` passed → skip this step, that mode applies. Otherwise — default: mode resolves to Full Scan (all scopes), recorded in the summary, no menu shown. `--ask`: present a menu covering every mode, each with a one-line what-it-does: Full Scan (recommended) — all scopes / Preview — scan only, no approval / Single Scope — choose one scope / (Cancel).

3. **Project detection.** Fresh profile → reuse `Stack`/`Toolchain`, skip language re-detection; absent/drifted → detect language(s) from manifests. Either way, probe LSP directly (profile can't say if the server is live this session): present (TypeScript, Go, Python, Dart, Rust) → `findReferences`/`documentSymbol`; absent → grep fallback.

**Gate:** Mode selected, LSP availability determined, scope list locked. If fails → user does not select a mode → re-present once; still no selection → default Preview (no deletion) with WARN in state.data.mode, proceed.

### Phase 2: Scan

For each active scope, run the detector (max 2 scopes in parallel). Per-scope detection steps, evidence format, tool preference (Knip / Vulture / ts-prune / LSP / grep fallback), and proposal: [references/scopes-detection.md](references/scopes-detection.md).

**False positive prevention:** per signal, re-read 3 lines around match, verify no skip pattern (`# noqa`, `# intentional`, `# safe:`), exclude generated files (`*.g.*`, `*.pb.*`, `*.gen.*`).

**Gate:** Every scope executed, each finding carrying file:line evidence + proposal. If a scope fails (LSP unavailable for dead-code, file unreadable) → mark it `inconclusive` with reason, continue the rest, note in Phase 3 report as "inconclusive — {reason}".

### Phase 3: Report

Single delete-or-keep table:

```
| ID    | Scope                 | File:Line          | Kind          | Evidence                            | Proposal              |
|-------|-----------------------|--------------------|---------------|-------------------------------------|-----------------------|
| S{n}  | {scope}               | {file}:{line}      | {kind}        | {n} references                      | {action-proposal}     |
| S{n}  | ssot-violation        | ({n} files)        | constant      | `"{dup-literal}"` in {n} files      | Central export        |
```

Per-scope summary line below the table: `Scope {scope-name}: {n} findings, {m} clean`. `test-realism` row: `covered by /ds-test — run it for fixture-realism analysis` or `test-realism not analyzed — requires /ds-test`, per [references/scopes-detection.md](references/scopes-detection.md) `test-realism`.

Write findings to `ds/audit/findings.md` with `scope=simplify` and `category` column set `B` for every row (every deletion is approval-gated).

**Gate:** Table displayed with every finding's proposal. If fails → zero findings across all scopes → print "ds-simplify: 0 findings — codebase is clean" and skip to Phase 7 Summary directly.

### Phase 4: Approve [skip if --preview]

All findings are Category B — every deletion requires approval.

1. Default: every row resolves automatically to `delete`, using the same impact/effort/risk reasoning an approval batch would show (reversible via the batch's git commit in Phase 5, so not on the irreversible-exception list), recorded in the summary.
2. `--ask`: present full table — one line per row (`type · target — file:line`) grouped by scope with counts; state the question (`Delete these N items?`). "All" = exactly the displayed set. Offer: **Apply All** / **Apply by Scope** (per-scope bulk alongside the total) / **Review Each** / **Skip All**.
3. Apply All → all rows → `delete`. Skip All → all → `skipped (user declined)`. Review Each → per-row `keep | delete | defer`. Apply by Scope → per-scope bulk.

Record every decision. Batch pending deletions by scope.

**Gate:** Every finding has a decision; accounting matches total. If fails → user declines approval prompt → mark all undecided as `skipped (user declined)`, skip Phase 5 Execute, proceed to Phase 7 Summary.

### Phase 5: Execute [skip if --preview or zero approvals]

**Checkpoint pre-gate (once, before the first batch):** `git status --porcelain` — clean, or every batch's files are disjoint from dirty paths → proceed; a batch targets a dirty path → stop that batch, record `only you can do: uncommitted changes in {file} overlap the deletion batch`. Full protocol: [../core/checkpoint-protocol.md](../core/checkpoint-protocol.md). Never run a bulk deletion over uncommitted unrelated changes in the same files.

Per approved batch:

1. Apply the deletion / inline / compaction in-place.
2. **Mechanical Done Gate:** run `{check-cmd}` — resolved in Phase 1: ds-quality enforcement arm installed (stop-hook / pre-commit hook / auto-lint) → its gate command; else stack-native lint/type + fail-fast test (`npm test --bail`, `go test ./...`, `pytest -x`, `flutter test`); none detectable → Verification-Infrastructure Gap: report it, offer `/ds-quality`, record the decision. Baseline captured before the first batch; baseline red → done condition is "no *new* red", baseline reds reported, never inherited as green. New red (tests OR lint/type — a deletion can break the type graph with tests still green) → restore the batch's files (`git restore -- {files}` — no commit exists yet at this step), mark `failed (mechanical gate)` with the captured error, continue to next scope.
3. `/ds-commit` present → invoke `/ds-commit --single` with: `refactor(simplify): remove {n} {scope} findings`; record commit hash. Absent → commit inline: `git add {batch files}` then `git commit -m "refactor(simplify): remove {n} {scope} findings"`; record commit hash. Never leave an approved batch uncommitted.
4. After the last batch: run the full `{check-cmd}` once — per-batch greens can compose into a red; the aggregate run's exact command + observed output is the Completion Evidence.

Parallel execution per scope allowed. One commit per scope-batch so user can revert a single scope cleanly.

**Gate:** Every approved batch either committed or cleanly rolled back; aggregate `{check-cmd}` shows no new red. If fails → failure surfaces before the batch commit → `git restore -- {files}`; failure discovered after the commit landed → `git revert {batch-commit-hash}`; either way mark `failed (mechanical gate, rolled back)`, continue to next scope. Never report `OK` with a new red.

### Phase 6: Needs-Approval Review [needs_approval > 0]

No separate needs-approval items beyond Phase 4 batch — every item was B.

**Gate:** Every Phase 4 batch item resolved (committed or rolled back); none left pending. If fails → an item was left undecided in Phase 4 → surface it here for an explicit decision before Summary.

### Phase 7: Summary

Disposition accounting — totals balance.

```
| ID    | Scope                | Disposition                            |
|-------|----------------------|----------------------------------------|
| S{n}  | {scope}              | {fixed-deleted-in-hash / skipped / deferred / failed} |
```

`ds-simplify: {OK|WARN|FAIL} | Removed: {n} | Deferred: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

Closing shape (`Decided without asking` lines, every `only you can do` item in full): [../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md).

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} dead exports / orphan modules deleted — {n} kB of unused code no longer in bundle, faster module load`
- `{n} single-caller helpers inlined — abstraction layer that earned nothing has been removed`
- `{n} premature abstractions (≤3 concrete usages) flagged for Path-A delete — context budget for future readers freed`
- `{n} SSOT violations consolidated — same fact no longer maintained in {n} places that can drift silently`

Zero-finding run: `No simplification opportunities detected — codebase is lean for current usage patterns`.

**Gate:** Every finding has exactly one disposition; accounting balances. If fails → undisposed finding or unbalanced counts → assign `failed (disposition missing)`, recompute totals, reprint table, status WARN.

## Quality Gates

- Deletion is reversible: every batch ends in a git commit — rollback = `git revert {hash}`.
- Framework contracts honored: do not delete exports required by framework (Next.js `generateMetadata`, React Server Component signatures, Dart widget `build`, etc.).
- W2: no new broken import after deletion — the Phase 5 `{check-cmd}` run's observed output is the evidence, no separate prose re-check. W4: re-read file after context gap before deletion. W5: uncertain coupling → defer, not delete. W7: dedup file:line — single finding for multi-scope hits, keep tightest proposal. W9: not applicable — state-exempt (one reversible commit per approved batch is the durable record). W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered.
- W1: cite file:line + reference count, never assume. W3: only task-required lines — do not reformat adjacent code. W6: verify all scopes produced output. W8: no raw shell interpolation. W17: before proposing a new helper, grep for an existing one; consolidate near-duplicate clones to a single source of truth rather than leaving regenerated copies in place. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| LSP unavailable | Fall back to `git grep` with word boundaries; confidence = MEDIUM for dead-code scope |
| Test suite missing | Skip post-delete test gate with warning; ask user to confirm before commit |
| Framework-required export flagged | Honor framework rule, mark `not applicable (framework contract)` |
| Deletion breaks import during execute | Revert batch, mark `failed`, continue to next scope |
| Orphan file claimed by docs-only reference | Treat as live, mark `not applicable (referenced by docs)` |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty project | Report "nothing to simplify", exit |
| Generated code directory | Skip entirely; flag only if the directory itself is orphan |
| Monorepo | Scope scan per workspace; aggregate findings with workspace-prefixed IDs |
| Large codebase (>5k files) | Apply saturation gate: after 2 scopes with consistent patterns, narrow next scope to highest-density directories |
| Public library with `exports` field | Treat every exported symbol as live for dead-code scope |
| Single-caller is a test file | Mark `not applicable (test-only helper)` |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
