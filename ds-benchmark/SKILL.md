# /ds-benchmark

Teams drift toward internal tastes — architecture that made sense to the original author doesn't match where the problem space has landed. Without an explicit external benchmark, the project's "ideal" is whatever the last contributor felt.

**Ideal-vs-Current Benchmark** — research 5–10 comparable projects, synthesize the ideal architecture, produce a dimension-by-dimension gap table, and let the user decide which gaps to close.

## Triggers

- User runs `/ds-benchmark`
- User asks to compare with competitors, learn from similar projects, or "what would ideal look like"
- User asks "am I doing this the right way" or "how do leading projects solve this"
- User preparing an OSS release and wants a credible positioning story

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "compare with competitors", "what would ideal look like" | "audit my own code quality" (→ ds-review) |
| "ideal-vs-current gap table" | "score project health from inside" (→ ds-blueprint) |
| "OSS positioning research vs alternatives" | "marketing positioning / copy" (→ ds-market) |
| "am I doing this the right way" | "fix the issues you find" (→ ds-review / ds-fix) |

## Contract

- Standalone; uses blueprint profile + `ds/audit/findings.md` when fresh to skip re-detection. State: `ds/audit/benchmark.json`.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- Research delegated to `/ds-research` — never re-implements web-search or CRAAP+ scoring.
- Writes `ds/audit/findings.md` (`scope=ideal-gap`); contributes gap section to ds-ship report when invoked under it.
- Zero autonomous architectural change. Every gap closure is Category B → user decision.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Research + synthesis + gap table, no approval block |
| `--competitors={n}` | Target count of comparables (default 7; min 3, max 12) |
| `--scope={x}` | Narrow to a single dimension: architecture, stack, data-model, ux, security, privacy, operational, all |
| `--resume` | Resume from `ds/audit/benchmark.json` without prompt |
| `--clean` | Delete existing state, start fresh |

Without flags: full benchmark across every dimension.

## Scopes

| Scope | What It Covers |
|-------|---------------|
| architecture | Module layout, layering, entry points, data flow |
| stack | Language, framework, persistence, queue, cache, auth provider |
| data-model | Primary entities, relationships, normalization level, indexing |
| ux | Core user flows, latency posture, mobile/desktop/web split |
| security | AuthN / AuthZ model, session storage, secret handling, transport |
| privacy | Data-collection scope, retention, user-rights endpoints, consent model |
| operational | Deploy target, observability, incident runbook, cost envelope |

## Delegation

**Owns:** benchmark, ideal-synthesis, ideal-gap, competitive-analysis | **Delegates:** ds-research → 5–10 comparables with CRAAP+ tiering; ds-docs → `--adr` to record every accepted gap decision as ADR (optional) | **Receives:** ds-ship → Phase 1 ideal-vs-current gap

## Execution Flow

Setup → Define → Research → Synthesize → Gap → Approve → Record → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Recovery check:** DETECT `ds/audit/benchmark.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → skip `done` phases, announce `[BEN] Resuming from Phase {N}`. On Summary success, delete state. Verify `ds/audit/` in `.gitignore`.

2. **State:** `{ problem_definition, competitors: [{name, url, tier, strengths, weaknesses}], ideal: {dimension: synthesis}, gaps: [{id, dimension, ideal, current, gap_type, proposal, category, decision}], git_hash }`.

3. **Blueprint profile check.** Search `## Blueprint Profile`. Found → read type, stack, audience, priorities. Absent → own detection + prompt for problem definition.

**Gate:** Profile located or problem definition ready. If fails → no profile + own detection insufficient (empty repo, no manifest) → prompt "No project profile found — describe the problem space in one sentence." User declines → abort: "Cannot benchmark without problem definition."

### Phase 2: Define Problem Space

1. Extract from blueprint profile: project name, one-sentence value proposition, target audience, stated constraints.
2. Profile missing → ask user: one-sentence problem statement; target audience (public users / internal team / developers / operators); non-negotiable constraints (keep language, keep framework, keep primary DB).
3. Present extracted definition: `"Researching ideal for: {problem} for {audience} under {constraints} — confirm? [Y/n]"`.

**Gate:** User confirmed problem space. Accept affirmative (`y`/`yes`/`ok`/`confirmed`/`looks good`). Suggested changes → apply, redisplay, re-confirm. Declines/abort → exit cleanly. If fails (no response or ambiguous after 2 prompts) → treat as implicit confirmation of auto-extracted statement, add WARN `"Problem space auto-confirmed — no explicit user confirmation"` to state, proceed.

### Phase 3: Research

Invoke `/ds-research` with:

- Query: `"5-10 reputable {problem-space} projects / alternatives / competitors"`
- Emphasis: open-source preferred (inspectable code), mix commercial leaders where relevant
- Output: per-source CRAAP+ tier, short description, "what they do well", "where they fall short"

Target count from `--competitors` (default 7). Too few after filtering → expand search with alternative phrasings; still too few → proceed with available set, flag low-sample-size.

Per competitor record: Name + URL (project identity); CRAAP+ tier — T1 (authoritative) / T2 (supporting) / T3 (inspirational); Strengths (concrete dimensions handled well); Weaknesses (concrete dimensions where they fall short); Architecture signal (public info on stack / module layout / data model).

**Gate:** ≥3 competitors at T1+T2 each with strengths/weaknesses. If fails → `/ds-research` returned fewer than 3 T1+T2 sources → expand search with synonyms, retry once; still insufficient → proceed with available set, flag `low-sample-size: true` in state.data.competitors, note "Ideal synthesis may be speculative due to limited comparables" in report.

### Phase 4: Synthesize Ideal

Per dimension (architecture / stack / data-model / ux / security / privacy / operational):

1. Aggregate competitor signals — convergence vs divergence across T1/T2 sources.
2. Adjust for stated constraints — if user pinned language/framework/DB, "ideal" respects those.
3. Write one-paragraph ideal per dimension: concrete, opinionated, no hedging.
4. **Security/privacy ideal ([references/principles.md §5](references/principles.md)):** the synthesized ideal MUST reflect the security baseline regardless of competitor convergence — boundary validation at every system boundary, least privilege for credentials, no secrets in source, defense in depth (never single-control), vetted crypto only (no custom, no MD5/SHA1/DES/ECB). Competitor consensus contradicts baseline → baseline wins; flag deviation as finding.

Output `ideal` block in state (JSON-shaped): `{"architecture": "{one-paragraph ideal — concrete pattern + data flow}", "stack": "{one-paragraph ideal stack}", ...}` — one key per active scope.

**Gate:** Every active scope has an ideal paragraph. If fails → insufficient competitor signals for a dimension (all T3 or inaccessible) → write `[LOW CONFIDENCE]`-tagged placeholder using only security baseline; flag dimensions as `speculative` in state.data.ideal; note them in gap table header.

### Phase 5: Gap Table

For each dimension, compare ideal vs current (current from blueprint profile + `ds/audit/findings.md`):

```
| ID    | Dimension    | Ideal              | Current            | Gap type             | Proposal             | Category |
|-------|--------------|--------------------|--------------------|----------------------|----------------------|----------|
| G{n}  | {dim}        | {ideal-paragraph}  | {current-state}    | {gap-type}           | {action-proposal}    | {A/B}    |
```

`gap_type`: `missing | excess | wrong | partial-needs-extension`.

**Category rules:**

- Code-level fix not altering architecture or scope → A.
- Architecture / new dependency / new capability / user-facing promise change → B.

Write gap entries to `ds/audit/findings.md` with `scope=ideal-gap` and `category` column set.

**Gate:** Every dimension has at least one row (or explicit "no gap" entry). If fails → dimension marked `speculative` in Phase 4 + current state unknown (no profile, no findings) → insert `"current: unknown — insufficient data"` row with `gap_type: unknown`, `category: B`, `proposal: "Manual assessment required"` so consumers don't silently miss a dimension.

### Phase 6: Approve

Present every Category B gap in one block:

> "These gaps change architecture or scope. For each: **Close** (commit to fixing), **Defer** (note but leave for later), **Intentional deviation** (record as ADR — we chose not to match the ideal)."

Modes: `--auto` → list all, mark `skipped (needs-approval)`. `--force-approve` → mark all `close`. Interactive → per row.

Per "Intentional deviation" → offer `/ds-docs --adr` to record rationale (so future contributors see *why*).

Category A gaps recorded as findings but not executed here — consumers (ds-ship, ds-review) pick up `scope=ideal-gap` A findings and execute.

**Gate:** Every B gap has a decision. If fails → user skipped one or more B gaps without choosing → re-present each undecided gap individually, require a choice; user still declines → record `decision: deferred (no response)` in state.data.gaps so no gap is left unknown.

### Phase 7: Record

1. Update `ds/audit/findings.md` meta header scopes list to include `ideal-gap`.
2. `close` decision → finding remains, `disposition=needs-execution`.
3. `defer` decision → finding remains, `disposition=deferred`.
4. `intentional-deviation` → finding `disposition=skipped (intentional)`; ADR written to `docs/adr/NNNN-{slug}.md` if user agreed.

**Gate:** Every B gap persisted with its decision. If fails → `ds/audit/findings.md` write failed (file locked, disk error) → write gap decisions to state.data.gaps as fallback, surface write error with target path + OS error, ask user to resolve before re-running Phase 7.

### Phase 8: Needs-Approval Review [needs_approval > 0]

Resolved inline in Phase 6. If skipped via `--auto`, surface summary here with count.

### Phase 9: Summary

FRC+DSC accounting.

```
Benchmark: {problem-space}
Competitors: {n} (T1: {x}, T2: {y}, T3: {z})

| Dimension     | Gaps  | Closed | Deferred | Intentional | No-gap |
|---------------|-------|--------|----------|-------------|--------|
| {dim}         | {n}   | {n}    | {n}      | {n}         | {n}    |
```

`ds-benchmark: {OK|WARN|FAIL} | Gaps: {n} | Close: {n} | Defer: {n} | Intentional: {n} | Skipped: {n} | Total: {n}`

**Value Delivered:** 1-5 concrete bullets, real outcomes only. Example shapes (placeholders, not literal):

- `{n} comparable projects benchmarked across {m} dimensions — "ideal" is now externally calibrated, not your internal taste`
- `{n} gaps identified between project and ideal: {n} accepted (close), {n} deferred, {n} declared intentional with ADR — every architectural divergence is now a deliberate decision, not a forgotten one`
- `Stack-fitness gap closed: {old-tech} → {new-tech} proposal documented with effort + risk — informed migration path replaces vague "we should modernize"`

On success: delete `ds/audit/benchmark.json`. If `ds/audit/` empties, remove directory.

**Gate:** Every gap has exactly one decision; accounting balances. If fails → accounting mismatch (Close + Defer + Intentional + Skipped ≠ total) → identify missing gap IDs in state.data.gaps, assign `decision: deferred (accounting-fix)`, recompute table, add WARN `"{n} gap(s) auto-deferred to balance accounting"`.

## Quality Gates

- Research budget respected: `/ds-research` returns on its own time; do not spawn parallel research beyond the delegated call.
- Intentional deviation always offered — the ideal is not the law, the user's constraints win.
- W1: every competitor claim cites source URL + CRAAP+ tier. W2: ideal synthesis honors stated constraints — never proposes a stack change the user pinned out. W3: only `ds/audit/findings.md` + optional ADRs written. W4: re-read blueprint profile before Gap phase. W5: single-source claim → MEDIUM confidence, do not promote to "ideal". W6: every active scope produces a row. W7: dedup competitor claims across sources — merge "do this" signals, keep strongest source. W8: quote all URLs. W9: state in `ds/audit/benchmark.json`, `ds/audit/` gitignored, state deleted on Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W12: derive the "ideal" from verified evidence across comparables — never reverse-engineer it to favor a predetermined choice or special-case the metrics.

## Error Recovery

| Situation | Action |
|-----------|--------|
| `/ds-research` returns <3 credible sources | Expand query with problem-space synonyms; still insufficient → flag low-sample-size, proceed with available set |
| Competitor info behind paywall | Skip competitor, record "inaccessible" in state, adjust count |
| Blueprint profile missing + user declines to define problem space | Abort: `Cannot benchmark without problem definition` |
| User rejects every proposed gap | Record all as intentional-deviation, generate ADRs for each |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Novel problem space (no comparables found) | Report "No credible comparables found. Ideal synthesis is speculative — treat every proposal as B." |
| Comparables are much larger scale | Flag scale mismatch per dimension; ideal is adapted, not copied |
| Pinned constraint conflicts with every ideal | Record conflict as intentional-deviation with `"constrained by {reason}"` note |
| Pre-launch project with empty codebase | Produce ideal-only report; gap table shows all rows as `missing` |
| Public research unavailable for commercial competitors | Tier T2 sources higher; flag `commercial-closed` in weakness column |
