# /ds-simplify

Codebases accumulate dead exports, single-caller helpers, fallback branches, orphan modules, and premature abstractions. Each one earns a spot in context without earning its keep. Skill detects each class, presents a delete-or-keep table with concrete reasons, and applies only what the user approves.

**Approved Simplification** — Overengineering hygiene with one approval batch, zero silent deletion.

## Triggers

- User runs `/ds-simplify`
- User asks to remove dead code, clean up the project, kill overengineering, or find duplicates
- User asks "are there any orphan files", "is anything unused", or "is this overengineered"
- After large refactor or feature removal — suggest a simplify pass

## Contract

- Standalone; uses `.audit/findings.md` when fresh, own scan otherwise. FRC+DSC enforced. State: `.audit/simplify.json`.
- Detection only — zero deletion without approval batch. Every finding cites file:line + concrete ref count or pattern.
- Delete execution delegates to `/ds-commit` — one reversible commit per approved batch.
- Three similar lines beat a premature abstraction: abstractions on ≤3 usages → finding.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Scan + report, no approval prompt, no deletion |
| `--scope=X` | Single scope: dead-code, single-caller, fallback, dead-branch, premature-abstraction, quarantine, test-realism, io-drift, ssot-violation, orphan, all |
| `--auto` | All phases, list Category B items (every deletion is B), skip without asking |
| `--force-approve` | Apply every pending deletion without asking |
| `--resume` | Resume from `.audit/simplify.json` without prompt |
| `--clean` | Delete existing state, start fresh |

Without flags: present mode menu (full scan / preview / single scope).

## Scopes

| Scope | What It Covers |
|-------|---------------|
| dead-code | Exports with zero references via LSP `findReferences` or cross-file grep |
| single-caller | Helpers, utilities, or components referenced from exactly one site — inline candidate |
| fallback | Backward-compat branches, legacy import paths, defensive checks with no live hit |
| dead-branch | Feature-flag branches where only one path has executed in recent history |
| premature-abstraction | Generics, hooks, wrappers, or base classes built on ≤3 concrete usages |
| quarantine | `// removed`, `// legacy`, `// deprecated`, `// TODO delete`, `_unused` markers |
| test-realism | Test fixtures with unrealistic data (`a@b.c`, `$1`, empty string secrets, length-1 arrays as "collection") |
| io-drift | Function signature vs caller signature mismatch — unused params, extra args at call site |
| ssot-violation | Same constant, URL, regex, or rule duplicated across 2+ files |
| orphan | Modules, assets, or images with zero inbound references from source, config, or docs |

## Delegation

**Owns:** dead-code, single-caller, fallback, dead-branch, premature-abstraction, quarantine, test-realism, io-drift, ssot-violation, orphan | **Delegates:** ds-commit → per-batch delete commit after approval | **Receives:** ds-review → overengineering findings routed here; ds-ship → Phase 3 simplify pass

## Execution Flow

Setup → Scan → Report → Approve → Execute → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Recovery check:** DETECT `.audit/simplify.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete state. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` scope, skip `done` scopes, announce `[SMP] Resuming from Phase {N}: {name}`. On successful Summary, delete state; remove `.audit/` if empty. Verify `.audit/` in `.gitignore`; add if missing.

2. **State shape:** `{ mode, scopes_selected, scopes_done[], findings_per_scope: {scope: [{id, file, line, kind, evidence, proposal}]}, approval_decisions: {id: keep|delete|defer}, batch_commits: [hash], git_hash }`.

3. **Findings file check:** `.audit/findings.md` exists and fresh → read entries with scopes `simplify`, `hygiene`, `ai-hygiene`, `dead-code`, `architecture/premature-abstraction`. Use as prior signal. Absent or stale → run own scan.

4. **Mode selection.** No flags → ask user: Full Scan (all scopes), Preview (no approval), Single Scope (choose one).

5. **Project detection.** Identify language(s) and LSP availability. LSP present (TypeScript, Go, Python, Dart, Rust) → use `findReferences` / `documentSymbol`. LSP absent → grep fallback.

**Gate:** Mode selected, LSP availability determined, scope list locked.

### Phase 2: Scan

For each active scope, run the detector. Max 2 scopes in parallel.

**2.1 dead-code:**
1. Collect all exported symbols (language-specific: `export`, `module.exports`, `pub fn`, `public`, Dart `public` by default).
2. For each export, count references via LSP `findReferences` or `git grep -w <name>`.
3. Reference count = 0 → finding. Include file:line of export + "zero references" evidence.
4. Skip exports listed in public API manifests (`exports` field in `package.json`, Dart `lib/` public re-exports, `__all__` in Python).

**2.2 single-caller:**
1. Collect internal exports (not in public API).
2. Count references. Count = 1 → finding with caller file:line + "1 reference at X" evidence.
3. Propose: inline at caller, remove export.
4. Skip: recursive helpers, classes with subclasses, trait implementations.

**2.3 fallback:**
1. Scan for patterns: `// @deprecated`, `// backward compat`, `// legacy`, `if (oldVersion)`, `catch { return null }` with no re-throw, feature detection where the feature is guaranteed by minimum runtime version.
2. Each match → finding with file:line + evidence snippet + proposal.

**2.4 dead-branch:**
1. Grep feature flag references (`process.env.FEATURE_X`, `flags.X`, `if (config.X)`).
2. Flag with only one path ever taken in last 100 commits (check by git log of the flag's file) → finding.
3. Evidence: flag name + "only true path observed in last 100 commits".

**2.5 premature-abstraction:**
1. Find generic containers, base classes, wrappers, higher-order hooks, render props with ≤3 concrete usages.
2. Evidence: abstraction file:line + usage count + `file:line` of each usage.
3. Proposal: inline usages, drop abstraction.

**2.6 quarantine:**
1. Grep: `// removed`, `// legacy`, `// deprecated`, `// TODO: delete`, `// kill this`, `// unused`, variable `_unused*`.
2. Each match → finding with context.

**2.7 test-realism:**
1. Scan test files for: email `a@b.c`, `test@test.test`, price `$1`, `$0.01`, id `1`/`"1"`/`"a"`, array `[]` or `[1]` used as "collection", string `"test"` / `"foo"`.
2. Each finding → propose realistic replacement (`user.lastname+audit@example.com`, `$129.99`, Unicode name, `[` 3–5 realistic items `]`).

**2.8 io-drift:**
1. For each function definition, collect its signature (param names + types).
2. Diff against every call site — unused params, extra args at call site, params passed in wrong order (type-checked only if LSP).
3. Mismatch → finding with function file:line + caller file:line.

**2.9 ssot-violation:**
1. Build constant map: string/number literals ≥3 chars appearing in 2+ source files.
2. Filter: exclude test fixtures, exclude framework-expected literals (config keys, HTTP status codes, well-known MIME types).
3. Remaining duplicates → finding. Evidence: each occurrence file:line.
4. Propose: single export location.

**2.10 orphan:**
1. Collect: source files, images, JSON, CSS/SCSS, `.md` files under `docs/` or repo root.
2. For each, grep all tracked files for the filename (with and without extension) and relative path patterns.
3. Zero inbound references → finding.
4. Skip: entry points, config files named by convention (`.eslintrc*`, `tsconfig.json`, etc.), `README.md`, `LICENSE`, `CHANGELOG.md`.

**False positive prevention:** For every signal, re-read 3 lines around the match, verify no skip pattern (`# noqa`, `# intentional`, `# safe:`), exclude generated files (`*.g.*`, `*.pb.*`, `*.gen.*`).

**Gate:** Every scope executed. Every finding has file:line evidence + proposal.

### Phase 3: Report

Single delete-or-keep table:

```
| ID  | Scope                | File:Line          | Kind          | Evidence                        | Proposal              |
|-----|----------------------|--------------------|---------------|----------------------------------|-----------------------|
| S01 | dead-code            | src/util.ts:42     | export fn     | 0 references                     | Delete fn + export    |
| S02 | single-caller        | src/helpers.ts:17  | export const  | 1 ref at src/main.ts:88          | Inline at caller      |
| S03 | premature-abstraction | src/base.ts:5     | abstract class| 2 subclasses, no third planned   | Drop base, inline     |
| S04 | ssot-violation       | (3 files)          | constant      | `"api.example.com"` in 3 files   | Central export        |
| ... |                      |                    |               |                                  |                       |
```

Per-scope summary line below the table: `Scope {n}: {k} findings, {m} clean`.

Write findings to `.audit/findings.md` with `scope=simplify` and the `category` column set to `B` for every row (every deletion is approval-gated).

**Gate:** Table displayed with every finding's proposal.

### Phase 4: Approve [skip if --preview]

All findings are Category B — every deletion requires approval.

1. Present the full table.
2. Offer: **Apply All** / **Review Each** / **Skip All** / **Apply by Scope**.
3. Apply All → all rows → `delete`. Skip All → all → `skipped (user declined)`. Review Each → per-row `keep | delete | defer`. Apply by Scope → per-scope bulk.
4. `--auto` without `--force-approve`: list all, mark every row `skipped (needs-approval)` in summary.
5. `--force-approve`: all rows → `delete`.

Record every decision in `approval_decisions`. Batch pending deletions by scope.

**Gate:** Every finding has a decision. Accounting matches total.

### Phase 5: Execute [skip if --preview or zero approvals]

Per approved batch:

1. Apply the deletion / inline / compaction in-place.
2. Re-run quick tests (`ds-test --quick` if available; else `npm test --bail`, `go test ./...`, `pytest -x`, etc.). Test failure → revert the batch, mark batch `failed (tests broke)`, continue to next scope.
3. Invoke `/ds-commit --single` with a concise message: `refactor(simplify): remove {n} {scope} findings`. Record the resulting hash.
4. Update state: move approved IDs to `done`.

Parallel execution per scope is allowed. Commits are one-per-scope-batch so a user can revert a single scope cleanly.

**Gate:** Every approved batch either committed or cleanly rolled back. No test failures left in-tree.

### Phase 6: Needs-Approval Review [needs_approval > 0]

No separate needs-approval items beyond the Phase 4 batch — every item was B.

### Phase 7: Summary

FRC+DSC accounting.

```
| ID  | Scope                | Disposition                        |
|-----|----------------------|------------------------------------|
| S01 | dead-code            | fixed (deleted in c1a2b3f)         |
| S02 | single-caller        | skipped (user declined)            |
| S03 | premature-abstraction | deferred (user chose defer)       |
| S04 | ssot-violation       | failed (tests broke, reverted)     |
```

Summary line:

`ds-simplify: {OK|WARN|FAIL} | Removed: N | Deferred: N | Skipped: N | Failed: N | Total: N`

On success: delete `.audit/simplify.json`. If `.audit/` empties, remove the directory.

**Gate:** Every finding has exactly one disposition. Accounting balances.

## Quality Gates

W1: cite file:line + reference count, never assume. W2: verify no new broken import after deletion. W3: only task-required lines — do not reformat adjacent code. W4: re-read file after context gap before deletion. W5: uncertain coupling → defer, not delete. W6: verify all scopes produced output. W7: dedup file:line — single finding for multi-scope hits, keep tightest proposal. W8: no raw shell interpolation. W9: state in `.audit/simplify.json`, `.audit/` gitignored, state deleted on Summary.

- Deletion is reversible: every batch ends in a git commit — rollback = `git revert {hash}`.
- Framework contracts honored: do not delete exports required by framework (Next.js `generateMetadata`, React Server Component signatures, Dart widget `build`, etc.).

## Error Recovery

| Situation | Action |
|-----------|--------|
| LSP unavailable | Fall back to `git grep` with word boundaries; confidence = MEDIUM for dead-code scope |
| Test suite missing | Skip post-delete test gate with warning; ask user to confirm before commit |
| Framework-required export flagged | Honor framework rule, mark finding `not-applicable (framework contract)` |
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
