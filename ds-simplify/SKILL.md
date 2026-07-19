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
- State-exempt: one reversible commit per approved batch (delegated to `/ds-commit`) is the durable record.
- FRC+DSC enforced. Detected pre-existing / out-of-scope errors get a concrete disposition (W11), fixed inline or escalated with a concrete blocker.
- Detection only: every deletion requires an approval batch. Every finding cites file:line + concrete ref count or pattern.
- Three similar lines beat a premature abstraction: abstractions on ≤3 usages → finding.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Scan + report, no approval prompt, no deletion |
| `--scope={x}` | Single scope: dead-code, single-caller, fallback, dead-branch, premature-abstraction, quarantine, test-realism, io-drift, ssot-violation, orphan, all |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

Without flags: present mode menu (full scan / preview / single scope).

## Scopes

| Scope | What It Covers |
|-------|---------------|
| dead-code | Exports with zero references via LSP `findReferences` or cross-file grep |
| single-caller | Helpers, utilities, or components referenced from exactly one site — inline candidate |
| fallback | Backward-compat branches, legacy import paths, defensive checks with no live hit |
| dead-branch | Feature-flag branches whose flag value is constant across every config source (no runtime setter) — the untaken branch is dead |
| premature-abstraction | Generics, hooks, wrappers, base classes built on ≤3 concrete usages |
| quarantine | `// removed`, `// legacy`, `// deprecated`, `// TODO delete`, `_unused` markers |
| test-realism | Test fixtures with unrealistic data (`{tiny-email}`, `{tiny-price}`, empty-string secrets, length-1 arrays as "collection") |
| io-drift | Function signature vs caller signature mismatch — unused params, extra args at call site |
| ssot-violation | Same constant, URL, regex, or rule duplicated across 2+ files |
| orphan | Modules, assets, or images with zero inbound references from source, config, or docs |

## Delegation

**Owns:** dead-code, single-caller, fallback, dead-branch, premature-abstraction, quarantine, test-realism, io-drift, ssot-violation, orphan | **Delegates:** ds-commit → per-batch delete commit after approval | **Receives:** ds-review → overengineering findings routed here; ds-ship → Phase 3 simplify pass; ds-freeze → permanent deletion of hidden features (user-requested)

## Execution Flow

Setup → Scan → Report → Approve → Execute → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → read entries with scopes `simplify`, `hygiene`, `ai-hygiene`, `dead-code`, `architecture/premature-abstraction`. Use as prior signal. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scan, appended with own `source` + current `git_hash`.

2. **Mode selection.** No flags → present a menu covering every mode, each with a one-line what-it-does: Full Scan (recommended) — all scopes / Preview — scan only, no approval / Single Scope — choose one scope / (Cancel). A disambiguating flag skips the menu. Under `--auto`: skip the menu — mode resolves to Full Scan (all scopes).

3. **Project detection.** Identify language(s) + LSP availability. LSP present (TypeScript, Go, Python, Dart, Rust) → use `findReferences` / `documentSymbol`. LSP absent → grep fallback.

**Gate:** Mode selected, LSP availability determined, scope list locked. If fails → user does not select a mode → re-present once; still no selection → default Preview (no deletion) with WARN in state.data.mode, proceed.

### Phase 2: Scan

For each active scope, run the detector. Max 2 scopes in parallel.

**Deterministic detector preference (advisory):** for `dead-code` / `orphan` / `single-caller` on JS/TS, Knip binary or config present → run it and use its module-graph output (entry-point-aware, framework-plugin coverage) as the primary evidence; absent → LSP/grep detectors below. Repo configured with ts-prune but not Knip → still run it, but note in the report that ts-prune is officially in maintenance mode and recommend migrating to Knip (~150 framework plugins, entry-point-aware). For Python `dead-code`, Vulture present → run with `--min-confidence 80`; findings at ≥80 confidence enter the table directly, below 80 → flag with confidence noted and hold for Review Each; absent → LSP/grep detectors below. Tool output still passes false-positive prevention and the Phase 4 approval batch — the tool upgrades the detector, never bypasses the gate.

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
2. Statically resolvable flags only: the flag's value is a constant across every config source (all env files/`.env.example`, config files, deployment manifests set the same literal; no runtime setter/toggle mechanism exists) → the never-selected branch is dead → finding. Flag value not statically resolvable (remote config, per-tenant, runtime toggle) → skip, never guess runtime behavior.
3. Evidence: flag name + each config source file:line showing the constant value + "no runtime setter found".
4. **Stale-flag governance (advisory):** flags are a distinct compounding debt class — for each flag found in step 1, check for lifecycle metadata (owner + expiry date in the flag registry/config/comment; temporary-vs-permanent designation). Temporary flag with no owner/expiry, or whose value has been constant since a git-blame date older than 90 days → advisory finding "stale flag — assign owner+expiry or remove" (industry practice: owner + expiration set at creation, removal automated — Uber's Piranha removed ~2,000 stale flags this way). Advisory only; never delete a flag whose branch is not provably dead under step 2.

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

**Gate:** Every scope executed, each finding carrying file:line evidence + proposal. If a scope fails (LSP unavailable for dead-code, file unreadable) → mark it `inconclusive` with reason, continue the rest, note in Phase 3 report as "inconclusive — {reason}".

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

1. Present full table — one line per row (`type · target — file:line`) grouped by scope with counts; state the question (`Delete these N items?`). "All" = exactly the displayed set.
2. Offer: **Apply All** / **Apply by Scope** (per-scope bulk alongside the total) / **Review Each** / **Skip All**.
3. Apply All → all rows → `delete`. Skip All → all → `skipped (user declined)`. Review Each → per-row `keep | delete | defer`. Apply by Scope → per-scope bulk.
4. **Under `--auto`:** no approval batch is shown — every row resolves automatically to `delete`, using the same impact/effort/risk reasoning the interactive batch would show (reversible via the batch's git commit in Phase 5, so not on the irreversible-exception list), recorded in the summary.

Record every decision. Batch pending deletions by scope.

**Gate:** Every finding has a decision; accounting matches total. If fails → user declines approval prompt → mark all undecided as `skipped (user declined)`, skip Phase 5 Execute, proceed to Phase 7 Summary.

### Phase 5: Execute [skip if --preview or zero approvals]

Per approved batch:

1. Apply the deletion / inline / compaction in-place.
2. Re-run the project's quick test command directly (`npm test --bail`, `go test ./...`, `pytest -x`, `flutter test`, etc. — fail-fast variant). Test failure → restore the batch's files (`git restore -- {files}` — no commit exists yet at this step), mark `failed (tests broke)`, continue to next scope.
3. Invoke `/ds-commit --single` with: `refactor(simplify): remove {n} {scope} findings`. Record commit hash.

Parallel execution per scope allowed. One commit per scope-batch so user can revert a single scope cleanly.

**Gate:** Every approved batch either committed or cleanly rolled back; no test failures left in-tree. If fails → failure surfaces before the batch commit → `git restore -- {files}`; failure discovered after the commit landed → `git revert {batch-commit-hash}`; either way mark `failed (tests broke, rolled back)`, continue to next scope.

### Phase 6: Needs-Approval Review [needs_approval > 0]

No separate needs-approval items beyond Phase 4 batch — every item was B.

**Gate:** Every Phase 4 batch item resolved (committed or rolled back); none left pending. If fails → an item was left undecided in Phase 4 → surface it here for an explicit decision before Summary.

### Phase 7: Summary

FRC+DSC accounting.

```
| ID    | Scope                | Disposition                            |
|-------|----------------------|----------------------------------------|
| S{n}  | {scope}              | {fixed-deleted-in-hash / skipped / deferred / failed} |
```

`ds-simplify: {OK|WARN|FAIL} | Removed: {n} | Deferred: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

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
- W1: cite file:line + reference count, never assume. W2: verify no new broken import after deletion. W3: only task-required lines — do not reformat adjacent code. W4: re-read file after context gap before deletion. W5: uncertain coupling → defer, not delete. W6: verify all scopes produced output. W7: dedup file:line — single finding for multi-scope hits, keep tightest proposal. W8: no raw shell interpolation. W9: not applicable — state-exempt (one reversible commit per approved batch is the durable record). W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W17: before proposing a new helper, grep for an existing one; consolidate near-duplicate clones to a single source of truth rather than leaving regenerated copies in place.

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

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
