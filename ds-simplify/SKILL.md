# /ds-simplify

Codebases accumulate dead exports, single-caller helpers, fallback branches, orphan modules, and premature abstractions. Each one earns a spot in context without earning its keep. Skill detects each class, presents a delete-or-keep table with concrete reasons, and applies only what the user approves.

**Approved Simplification** — Overengineering hygiene with one approval batch, zero silent deletion.

## Triggers

- User runs `/ds-simplify`
- User asks to remove dead code, clean up the project, kill overengineering, or find duplicates
- User asks "are there any orphan files", "is anything unused", or "is this overengineered"
- After large refactor or feature removal — suggest a simplify pass

### Triggers — ÇAĞIRIR / ÇAĞIRMAZ

| ÇAĞIRIR | ÇAĞIRMAZ |
|---------|----------|
| "remove dead code", "find orphan files", "kill overengineering" | "audit security / privacy" (→ ds-compliance) |
| "is this overengineered (single-caller, premature abstraction)" | "score project architecture" (→ ds-blueprint) |
| "find duplicates in this module" | "DRY audit across full project (with paths)" (→ ds-review --meta-quality --meta-scope=dry) |
| "delete obsolete fallbacks / quarantine markers" | "fix lint / type errors" (→ ds-fix) |

## Contract

- Standalone; uses `ds/audit/findings.md` when fresh, own scan otherwise. State: `ds/audit/simplify.json`.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- Detection only — zero deletion without approval batch. Every finding cites file:line + concrete ref count or pattern.
- Delete execution delegates to `/ds-commit` — one reversible commit per approved batch.
- Three similar lines beat a premature abstraction: abstractions on ≤3 usages → finding.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Scan + report, no approval prompt, no deletion |
| `--scope={x}` | Single scope: dead-code, single-caller, fallback, dead-branch, premature-abstraction, quarantine, test-realism, io-drift, ssot-violation, orphan, all |
| `--auto` | All phases, list Category B items (every deletion is B), skip without asking |
| `--force-approve` | Apply every pending deletion without asking |
| `--resume` | Resume from `ds/audit/simplify.json` without prompt |
| `--clean` | Delete existing state, start fresh |

Without flags: present mode menu (full scan / preview / single scope).

## Scopes

| Scope | What It Covers |
|-------|---------------|
| dead-code | Exports with zero references via LSP `findReferences` or cross-file grep |
| single-caller | Helpers, utilities, or components referenced from exactly one site — inline candidate |
| fallback | Backward-compat branches, legacy import paths, defensive checks with no live hit |
| dead-branch | Feature-flag branches where only one path has executed in recent history |
| premature-abstraction | Generics, hooks, wrappers, base classes built on ≤3 concrete usages |
| quarantine | `// removed`, `// legacy`, `// deprecated`, `// TODO delete`, `_unused` markers |
| test-realism | Test fixtures with unrealistic data (`{tiny-email}`, `{tiny-price}`, empty-string secrets, length-1 arrays as "collection") |
| io-drift | Function signature vs caller signature mismatch — unused params, extra args at call site |
| ssot-violation | Same constant, URL, regex, or rule duplicated across 2+ files |
| orphan | Modules, assets, or images with zero inbound references from source, config, or docs |

## Delegation

**Owns:** dead-code, single-caller, fallback, dead-branch, premature-abstraction, quarantine, test-realism, io-drift, ssot-violation, orphan | **Delegates:** ds-commit → per-batch delete commit after approval | **Receives:** ds-review → overengineering findings routed here; ds-ship → Phase 3 simplify pass

## Execution Flow

Setup → Scan → Report → Approve → Execute → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Recovery check:** DETECT `ds/audit/simplify.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` scope, skip `done` scopes, announce `[SMP] Resuming from Phase {N}: {name}`. On Summary success, delete state. Verify `ds/audit/` in `.gitignore`.

2. **State:** `{ mode, scopes_selected, scopes_done[], findings_per_scope: {scope: [{id, file, line, kind, evidence, proposal}]}, approval_decisions: {id: keep|delete|defer}, batch_commits: [hash], git_hash }`.

3. **Findings file check:** `ds/audit/findings.md` fresh → read entries with scopes `simplify`, `hygiene`, `ai-hygiene`, `dead-code`, `architecture/premature-abstraction`. Use as prior signal. Absent/stale → own scan.

4. **Mode selection.** No flags → ask: Full Scan (all scopes), Preview (no approval), Single Scope (choose one).

5. **Project detection.** Identify language(s) + LSP availability. LSP present (TypeScript, Go, Python, Dart, Rust) → use `findReferences` / `documentSymbol`. LSP absent → grep fallback.

**Gate:** Mode selected, LSP availability determined, scope list locked. If fails → user does not select a mode → re-present once; still no selection → default Preview (no deletion) with WARN in state.data.mode, proceed.

### Phase 2: Scan

For each active scope, run the detector. Max 2 scopes in parallel.

**2.1 dead-code:**

1. Collect all exported symbols (language-specific: `export`, `module.exports`, `pub fn`, `public`, Dart `public` by default).
2. For each export, count references via LSP `findReferences` or `git grep -w {name}`.
3. Reference count = 0 → finding. Include file:line of export + "zero references" evidence.
4. Skip exports in public API manifests (`exports` in `package.json`, Dart `lib/` public re-exports, `__all__` in Python).

**2.2 single-caller:**

1. Collect internal exports (not in public API).
2. Count references. Count = 1 → finding with caller file:line + "1 reference at {file}:{line}" evidence.
3. Propose: inline at caller, remove export.
4. Skip: recursive helpers, classes with subclasses, trait implementations.

**2.3 fallback:**

1. Scan patterns: `// @deprecated`, `// backward compat`, `// legacy`, `if ({old-version-check})`, `catch { return null }` with no re-throw, feature detection where feature is guaranteed by minimum runtime version.
2. Each match → finding with file:line + evidence snippet + proposal.

**2.4 dead-branch:**

1. Grep feature-flag references (`process.env.{FLAG}`, `flags.{x}`, `if (config.{x})`).
2. Flag with only one path ever taken in last 100 commits (`git log` of flag's file) → finding.
3. Evidence: flag name + "only true path observed in last 100 commits".

**2.5 premature-abstraction:**

1. Find generic containers, base classes, wrappers, higher-order hooks, render props with ≤3 concrete usages.
2. Evidence: abstraction file:line + usage count + file:line of each usage.
3. Proposal: inline usages, drop abstraction.

**2.6 quarantine:**

1. Grep: `// removed`, `// legacy`, `// deprecated`, `// TODO: delete`, `// kill this`, `// unused`, variable `_unused{name}`.
2. Each match → finding with context.

**2.7 test-realism:**

1. Scan test files for: email `{tiny-domain}`, `test@test.test`, price `{trivial-amount}`, id `1`/`"1"`/`"a"`, array `[]` or `[1]` used as "collection", string `"test"`/`"foo"`.
2. Each finding → propose realistic replacement (`{user-prefix}+audit@{realistic-domain}`, `{realistic-price}`, Unicode name, `[` 3–5 realistic items `]`).
3. **Secret-pattern fixtures ([references/principles.md §5](references/principles.md)):** flag test fixtures with strings matching secret-scan regex (`sk-{test}...`, `AKIA...`, `ghp_...`, JWT-like `eyJ...`). Even fake-looking realistic tokens get mistaken for real leaks in CI logs. Propose obvious-fake placeholders (`FAKE_API_KEY_FOR_TESTS`, `not-a-real-token-{n}`).

**2.8 io-drift:**

1. For each function definition, collect signature (param names + types).
2. Diff against every call site — unused params, extra args at call site, wrong-order params (type-checked only if LSP).
3. Mismatch → finding with function file:line + caller file:line.

**2.9 ssot-violation:**

1. Build constant map: string/number literals ≥3 chars appearing in 2+ source files.
2. Filter: exclude test fixtures + framework-expected literals (config keys, HTTP status codes, well-known MIME types).
3. Remaining duplicates → finding. Evidence: each occurrence file:line.
4. Propose: single export location.

**2.10 orphan:**

1. Collect: source files, images, JSON, CSS/SCSS, `.md` files under `docs/` or repo root.
2. Per file, grep all tracked files for filename (with + without extension) and relative path patterns.
3. Zero inbound references → finding.
4. Skip: entry points, config files named by convention (`.eslintrc*`, `tsconfig.json`, etc.), `README.md`, `LICENSE`, `CHANGELOG.md`.

**False positive prevention:** per signal, re-read 3 lines around match, verify no skip pattern (`# noqa`, `# intentional`, `# safe:`), exclude generated files (`*.g.*`, `*.pb.*`, `*.gen.*`).

**Gate:** Every scope executed. Every finding has file:line evidence + proposal. If fails → scope unable to complete (LSP unavailable for dead-code, file unreadable) → log incomplete scope `{ scope, status: "inconclusive", reason }` to state.data.findings_per_scope, continue with remaining, note in Phase 3 report as "inconclusive — {reason}".

### Phase 3: Report

Single delete-or-keep table:

```
| ID    | Scope                 | File:Line          | Kind          | Evidence                            | Proposal              |
|-------|-----------------------|--------------------|---------------|-------------------------------------|-----------------------|
| S{n}  | {scope}               | {file}:{line}      | {kind}        | {n} references                      | {action-proposal}     |
| S{n}  | ssot-violation        | ({n} files)        | constant      | `"{dup-literal}"` in {n} files      | Central export        |
```

Per-scope summary line below the table: `Scope {scope-name}: {n} findings, {m} clean`.

Write findings to `ds/audit/findings.md` with `scope=simplify` and `category` column set `B` for every row (every deletion is approval-gated).

**Gate:** Table displayed with every finding's proposal. If fails → zero findings across all scopes → print "ds-simplify: 0 findings — codebase is clean" and skip to Phase 7 Summary directly.

### Phase 4: Approve [skip if --preview]

All findings are Category B — every deletion requires approval.

1. Present full table.
2. Offer: **Apply All** / **Review Each** / **Skip All** / **Apply by Scope**.
3. Apply All → all rows → `delete`. Skip All → all → `skipped (user declined)`. Review Each → per-row `keep | delete | defer`. Apply by Scope → per-scope bulk.
4. `--auto` without `--force-approve`: list all, mark `skipped (needs-approval)`.
5. `--force-approve`: all rows → `delete`.

Record every decision in `approval_decisions`. Batch pending deletions by scope.

**Gate:** Every finding has a decision; accounting matches total. If fails → user declines approval prompt → mark all undecided as `skipped (user declined)` in state.data.approval_decisions, skip Phase 5 Execute, proceed to Phase 7 Summary.

### Phase 5: Execute [skip if --preview or zero approvals]

Per approved batch:

1. Apply the deletion / inline / compaction in-place.
2. Re-run quick tests (`/ds-test --quick` if available; else `npm test --bail`, `go test ./...`, `pytest -x`, etc.). Test failure → revert batch, mark `failed (tests broke)`, continue to next scope.
3. Invoke `/ds-commit --single` with: `refactor(simplify): remove {n} {scope} findings`. Record commit hash.
4. Update state: move approved IDs to `done`.

Parallel execution per scope allowed. One commit per scope-batch so user can revert a single scope cleanly.

**Gate:** Every approved batch either committed or cleanly rolled back; no test failures left in-tree. If fails → tests break after batch deletion + rollback fails → `git revert {batch-commit-hash}`, mark `failed (tests broke, reverted)` in state.data.batch_commits, continue to next scope.

### Phase 6: Needs-Approval Review [needs_approval > 0]

No separate needs-approval items beyond Phase 4 batch — every item was B.

### Phase 7: Summary

FRC+DSC accounting.

```
| ID    | Scope                | Disposition                            |
|-------|----------------------|----------------------------------------|
| S{n}  | {scope}              | {fixed-deleted-in-hash / skipped / deferred / failed} |
```

`ds-simplify: {OK|WARN|FAIL} | Removed: {n} | Deferred: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

On success: delete `ds/audit/simplify.json`. If `ds/audit/` empties, remove directory.

**Value Delivered:** 1-5 concrete bullets, real deletion outcomes only. Example shapes (placeholders, not literal):

- `{n} dead exports / orphan modules deleted — {n} kB of unused code no longer in bundle, faster module load`
- `{n} single-caller helpers inlined — abstraction layer that earned nothing has been removed`
- `{n} premature abstractions (≤3 concrete usages) flagged for Path-A delete — context budget for future readers freed`
- `{n} SSOT violations consolidated — same fact no longer maintained in {n} places that can drift silently`

Zero-finding run: `No simplification opportunities detected — codebase is lean for current usage patterns`.

**Gate:** Every finding has exactly one disposition; accounting balances. If fails → undisposed finding or unbalanced counts → assign `failed (disposition missing)`, recompute totals, reprint table, status WARN.

## Quality Gates

- Deletion is reversible: every batch ends in a git commit — rollback = `git revert {hash}`.
- Framework contracts honored: do not delete exports required by framework (Next.js `generateMetadata`, React Server Component signatures, Dart widget `build`, etc.).
- W1: cite file:line + reference count, never assume. W2: verify no new broken import after deletion. W3: only task-required lines — do not reformat adjacent code. W4: re-read file after context gap before deletion. W5: uncertain coupling → defer, not delete. W6: verify all scopes produced output. W7: dedup file:line — single finding for multi-scope hits, keep tightest proposal. W8: no raw shell interpolation. W9: state in `ds/audit/simplify.json`, `ds/audit/` gitignored, state deleted on Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W17: before proposing a new helper, grep for an existing one; consolidate near-duplicate clones to a single source of truth rather than leaving regenerated copies in place.

## Error Recovery

| Situation | Action |
|-----------|--------|
| LSP unavailable | Fall back to `git grep` with word boundaries; confidence = MEDIUM for dead-code scope |
| Test suite missing | Skip post-delete test gate with warning; ask user to confirm before commit |
| Framework-required export flagged | Honor framework rule, mark `not-applicable (framework contract)` |
| Deletion breaks import during execute | Revert batch, mark `failed`, continue to next scope |
| Orphan file claimed by docs-only reference | Treat as live, mark `not-applicable (referenced by docs)` |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty project | Report "nothing to simplify", exit |
| Generated code directory | Skip entirely; flag only if the directory itself is orphan |
| Monorepo | Scope scan per workspace; aggregate findings with workspace-prefixed IDs |
| Large codebase (>5k files) | Apply saturation gate: after 2 scopes with consistent patterns, narrow next scope to highest-density directories |
| Public library with `exports` field | Treat every exported symbol as live for dead-code scope |
| Single-caller is a test file | Mark `not-applicable (test-only helper)` |
