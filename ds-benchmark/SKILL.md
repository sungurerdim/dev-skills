# /ds-benchmark

Teams drift toward internal tastes — architecture that made sense to the original author doesn't match where the problem space has landed. Without an explicit external benchmark, the project's "ideal" is whatever the last contributor felt.

**Ideal-vs-Current Benchmark** — research 5–10 comparable projects, synthesize the ideal architecture, produce a dimension-by-dimension gap table, and let the user decide which gaps to close.

## Triggers

- User runs `/ds-benchmark`
- User asks to compare with competitors, learn from similar projects, or "what would ideal look like"
- User asks "am I doing this the right way" or "how do leading projects solve this"
- User preparing an OSS release and wants a credible positioning story

## Contract

- Standalone; uses blueprint profile + `ds/audit/findings.md` when fresh to skip re-detection. FRC+DSC enforced. State: `ds/audit/benchmark.json`.
- Research delegated to `/ds-research` — never re-implements web-search or CRAAP+ scoring.
- Writes `ds/audit/findings.md` (scope=ideal-gap); contributes gap section to ds-ship report when invoked under it.
- Zero autonomous architectural change. Every gap closure is Category B → user decision.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Research + synthesis + gap table, no approval block |
| `--competitors=N` | Target count of comparables (default 7; min 3, max 12) |
| `--scope=X` | Narrow to a single dimension: architecture, stack, data-model, ux, security, privacy, operational, all |
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

1. **Recovery check:** DETECT `ds/audit/benchmark.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete state. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → skip `done` phases, announce `[BEN] Resuming from Phase {N}`. On successful Summary, delete state; remove `ds/audit/` if empty. Verify `ds/audit/` in `.gitignore`; add if missing.

2. **State shape:** `{ problem_definition, competitors: [{name, url, tier, strengths, weaknesses}], ideal: {dimension: synthesis}, gaps: [{id, dimension, ideal, current, gap_type, proposal, category, decision}], git_hash }`.

3. **Blueprint profile check.** Search for `## Blueprint Profile`. Found → read project type, stack, audience, priorities. Absent → proceed with own detection + prompt for problem definition.

**Gate:** Profile located or problem definition ready to be asked.

### Phase 2: Define Problem Space

1. Extract from blueprint profile: project name, one-sentence value proposition, target audience, stated constraints.
2. Profile missing → ask user:
   - One-sentence problem statement.
   - Target audience (public users / internal team / developers / operators).
   - Non-negotiable constraints (keep language, keep framework, keep primary DB, etc.).
3. Present the extracted definition back to user: "Researching ideal for: {problem} for {audience} under {constraints} — confirm? [Y/n]".

**Gate:** Problem space confirmed verbatim by user.

### Phase 3: Research

Invoke `/ds-research` with:
- Query: "5-10 reputable {problem-space} projects / alternatives / competitors"
- Emphasis: open-source preferred (code is inspectable), mix commercial leaders where relevant
- Output: per-source CRAAP+ tier, short description, "what they do well", "where they fall short"

Target count from `--competitors` flag (default 7). Too few after filtering → expand search with alternative phrasings; still too few → proceed with available set but flag low-sample-size in the report.

For each competitor, record:

| Field | Description |
|-------|-------------|
| Name + URL | Project identity |
| CRAAP+ tier | T1 (authoritative) / T2 (supporting) / T3 (inspirational) |
| Strengths | Concrete dimensions they handle well |
| Weaknesses | Concrete dimensions where they fall short |
| Architecture signal | Public info on stack / module layout / data model |

**Gate:** ≥3 competitors at T1+T2, each with a strengths/weaknesses table.

### Phase 4: Synthesize Ideal

Per dimension (architecture / stack / data-model / ux / security / privacy / operational):

1. Aggregate competitor signals — what do the T1/T2 sources converge on, what do they diverge on.
2. Adjust for stated constraints — if user pinned language/framework/DB, the "ideal" respects those.
3. Write one-paragraph ideal per dimension: concrete, opinionated, no hedging.

Output as `ideal` block in state:

```json
{
  "architecture": "Layered hexagonal: adapters in /adapters, domain in /domain, entry points in /apps/*. Data flow: HTTP → validator → use-case → repository → driver.",
  "stack": "...",
  ...
}
```

**Gate:** Every active scope has an ideal paragraph.

### Phase 5: Gap Table

For each dimension, compare ideal vs current (current from blueprint profile + `ds/audit/findings.md`):

```
| ID  | Dimension    | Ideal                                  | Current                                | Gap type           | Proposal                         | Category |
|-----|--------------|----------------------------------------|----------------------------------------|--------------------|----------------------------------|----------|
| G01 | architecture | Layered hexagonal                      | Flat src/, no ports/adapters split     | missing            | Introduce adapters/domain split  | B        |
| G02 | stack        | PostgreSQL + Redis + background queue  | PostgreSQL only, no queue              | missing            | Add BullMQ + Redis for async     | B        |
| G03 | security     | Session rotation on login              | Static session, no rotation            | partial-extension  | Add rotation on login + logout   | B        |
| G04 | operational  | Structured logging (pino / zap)        | console.log                            | wrong              | Replace console.log with pino    | A        |
| ... |              |                                        |                                        |                    |                                  |          |
```

`gap_type`: `missing | excess | wrong | partial-needs-extension`.

Category rules:
- Code-level fix that does not alter architecture or scope → A.
- Architecture, new dependency, new capability, or user-facing promise → B.

Write gap entries to `ds/audit/findings.md` with `scope=ideal-gap` and the `category` column set.

**Gate:** Every dimension has at least one row (or an explicit "no gap" entry).

### Phase 6: Approve

Present every Category B gap in one block:

> "These gaps change architecture or scope. For each: **Close** (commit to fixing), **Defer** (note but leave for later), **Intentional deviation** (record as ADR — we chose not to match the ideal)."

Modes: --auto → list all, mark `skipped (needs-approval)`. --force-approve → mark all `close`. Interactive → per row.

Per "Intentional deviation" decision, offer to invoke `/ds-docs --adr` to record the rationale (so future contributors see *why* the deviation exists).

Category A gaps are recorded as findings but not executed here — this skill does not apply fixes. Consumers (ds-ship, ds-review) pick up `scope=ideal-gap` A findings and execute.

**Gate:** Every B gap has a decision.

### Phase 7: Record

1. Update `ds/audit/findings.md` meta header scopes list to include `ideal-gap`.
2. Each `close` decision → finding remains with `disposition=needs-execution`.
3. Each `defer` decision → finding remains with `disposition=deferred`.
4. Each `intentional-deviation` decision → finding marked `disposition=skipped (intentional)`, ADR written to `docs/adr/NNNN-{slug}.md` if user agreed.

**Gate:** Every B gap persisted with its decision.

### Phase 8: Needs-Approval Review [needs_approval > 0]

Resolved inline in Phase 6. If skipped via `--auto`, surface summary here with count.

### Phase 9: Summary

FRC+DSC accounting.

```
Benchmark: {problem-space}
Competitors: {n} (T1: {x}, T2: {y}, T3: {z})

| Dimension   | Gaps | Closed | Deferred | Intentional | No-gap |
|-------------|------|--------|----------|-------------|--------|
| architecture| 2    | 1      | 1        | 0           | 0      |
| stack       | 1    | 0      | 0        | 1           | 0      |
| ...         |      |        |          |             |        |
```

Summary line:

`ds-benchmark: {OK|WARN|FAIL} | Gaps: N | Close: N | Defer: N | Intentional: N | Skipped: N | Total: N`

On success: delete `ds/audit/benchmark.json`. If `ds/audit/` empties, remove the directory.

**Gate:** Every gap has exactly one decision. Accounting balances.

## Quality Gates

W1: every competitor claim cites source URL + CRAAP+ tier. W2: ideal synthesis honors stated constraints — never proposes a stack change the user pinned out. W3: only `ds/audit/findings.md` + optional ADRs written. W4: re-read blueprint profile before Gap phase. W5: single-source claim → MEDIUM confidence, do not promote to "ideal". W6: every active scope produces a row. W7: dedup competitor claims across sources — merge "do this" signals, keep strongest source. W8: quote all URLs. W9: state in `ds/audit/benchmark.json`, `ds/audit/` gitignored, state deleted on Summary.

- Research budget respected: `/ds-research` returns on its own time; do not spawn parallel research sessions beyond the delegated call.
- Intentional deviation always offered — the ideal is not the law, the user's constraints win.

## Error Recovery

| Situation | Action |
|-----------|--------|
| `/ds-research` returns <3 credible sources | Expand query with problem-space synonyms; still insufficient → flag low-sample-size in report and proceed with available set |
| Competitor info behind paywall | Skip competitor, record "inaccessible" in state, adjust count |
| Blueprint profile missing + user declines to define problem space | Abort with clear message: `Cannot benchmark without problem definition` |
| User rejects every proposed gap | Record all as intentional-deviation, generate ADRs for each |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Novel problem space (no comparables found) | Report: "No credible comparables found. Ideal synthesis is speculative — treat every proposal as B." |
| Comparables are much larger scale | Flag scale mismatch per dimension; ideal is adapted, not copied |
| Pinned constraint conflicts with every ideal | Record conflict as intentional-deviation with "constrained by {reason}" note |
| Pre-launch project with empty codebase | Produce ideal-only report; gap table shows all rows as `missing` |
| Public research unavailable for commercial competitors | Tier T2 sources higher; flag commercial-closed in weakness column |
