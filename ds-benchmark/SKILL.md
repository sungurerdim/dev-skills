---
name: ds-benchmark
description: Ideal-vs-current gap analysis — research 5-10 comparable projects, synthesize the ideal architecture, produce a dimension-by-dimension gap table. Use when benchmarking against best-in-class or deciding which architectural gaps to close.
---

# /ds-benchmark

Teams drift toward internal tastes — architecture that made sense to the original author doesn't match where the problem space has landed. Without an explicit external benchmark, the project's "ideal" is whatever the last contributor felt.

**Ideal-vs-Current Benchmark** — research 5–10 comparable projects, synthesize the ideal architecture, produce a dimension-by-dimension gap table, and let the user decide which gaps to close.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

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
| "OSS positioning research vs alternatives" | "marketing positioning / copy" (→ external / manual) |
| "am I doing this the right way" | "fix the issues you find" (→ ds-review / ds-fix) |

## Contract

**Dimensions:** A1 (market positioning)

- Standalone; uses blueprint profile + `ds/audit/findings.md` when fresh (`git_hash == HEAD` AND current run-cycle) to skip re-detection.
- State-exempt: single regenerable report/audit.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- Research delegated to `/ds-research` when present — never re-implements CRAAP+ scoring. Absent → degraded inline search (Phase 3 fallback), all sources capped at T2 and labeled `untiered`.
- Writes `ds/audit/findings.md` (`scope=ideal-gap`); contributes gap section to ds-ship report when invoked under it.
- Zero autonomous architectural change. Every gap closure is Category B → user decision.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Research + synthesis + gap table, no approval block |
| `--competitors={n}` | Target count of comparables (default 7; min 3, max 12) |
| `--scope={x}` | Narrow to a single dimension: architecture, stack, data-model, ux, security, privacy, operational, all |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Without flags: benchmark the dimensions resolved `ran` by the Scopes table below; `--scope=` narrows further.

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

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| architecture | any source | — |
| stack | any source | — |
| data-model | db ≠ none | N/A — no persistence layer detected |
| ux | ui ≠ none | N/A — no UI surface |
| security | auth ≠ none or api ≠ none | N/A — no auth/API surface detected |
| privacy | pii=yes or integrations includes an analytics/tracking SDK | N/A — no personal-data path detected |
| operational | deploy ≠ none | N/A — no deploy target detected |

An `unknown` signal never excludes a scope — it still runs, reported `unknown → ran`. `--scope=` overrides this table for the named scope(s); `--ask` shows the resolved table before running.

## Delegation

**Owns:** benchmark, ideal-synthesis, ideal-gap, competitive-analysis | **Delegates:** ds-research → 5–10 comparables with CRAAP+ tiering (absent → inline degraded search, tiers capped at T2); ds-docs → `--adr` to record every accepted gap decision as ADR (absent → minimal ADR written inline) | **Receives:** ds-ship → Phase 1 ideal-vs-current gap; ds-productize → competitor price-map scan (CPR-01)

## Execution Flow

Setup → Define → Research → Synthesize → Gap → [Approve] → [Record] → Summary

### Phase 1: Setup

1. **Blueprint profile check.** Search instruction file(s) for `## Blueprint Profile`. Found → read type, stack, audience, priorities. Not found → own detection + prompt for problem definition.

**Gate:** Blueprint-profile check (step 1) found a match, or a one-sentence problem definition is recorded. If fails → no profile + own detection insufficient (empty repo, no manifest) → default: infer the problem statement from README, package metadata, and directory structure; still insufficient (truly empty repo) → abort with `only you can do: no problem definition inferable`. `--ask`: prompt "No project profile found — describe the problem space in one sentence." User declines → abort: "Cannot benchmark without problem definition."

### Phase 2: Define Problem Space

1. Extract from blueprint profile: one-sentence value proposition, target audience, stated constraints.
2. Profile missing → default: infer all three (one-sentence problem statement; target audience — public users / internal team / developers / operators; non-negotiable constraints — keep language, keep framework, keep primary DB) from repo signals (README, manifest, existing stack). `--ask`: ask the user for each instead.
3. Default: proceed directly on the extracted definition, recorded in the summary. `--ask`: present extracted definition: `"Researching ideal for: {problem} for {audience} under {constraints} — confirm? [Y/n]"`. Accept affirmative (`y`/`yes`/`ok`/`confirmed`/`looks good`); suggested changes → apply, redisplay, re-confirm; decline/abort → exit cleanly.

**Gate:** Problem space resolved (confirmed under `--ask`, or auto-extracted by default). If fails → under `--ask`, no response or ambiguous after 2 prompts → treat as implicit confirmation of the auto-extracted statement, add WARN `"Problem space auto-confirmed — no explicit user confirmation"` to state, proceed. Without `--ask` this is always the case (no prompt was shown) — same WARN recorded in the summary.

### Phase 3: Research

**Comparable-set framing.** When the problem space admits more than one comparable category (e.g. adjacent product classes), default: pick the single closest-matching category and proceed, stating the choice in the report header. `--ask`: present the candidate framings (each with a one-line what-it-covers) and let the user pick before dispatching research.

Invoke `/ds-research` with:

- Query: `"{target-count} reputable {problem-space} projects / alternatives / competitors"`
- Emphasis: open-source preferred (inspectable code), mix commercial leaders where relevant
- Output: per-source CRAAP+ tier, short description, "what they do well", "where they fall short"

Target count from `--competitors` (default 7); insufficient-sources recovery is owned by the Gate below.

**`/ds-research` absent (standalone fallback):** run inline web search directly — same per-competitor record, but never re-implement CRAAP+ scoring: cap every source at T2, label it `untiered`, and note `research: inline-degraded` in the report header. Single-source data points carry ds-research's `[single-source]` label here too — never presented bare.

Per competitor record: Name + URL (project identity); CRAAP+ tier — T1 (authoritative) / T2 (supporting) / T3 (inspirational); Strengths (concrete dimensions handled well); Weaknesses (concrete dimensions where they fall short); Architecture signal (public info on stack / module layout / data model).

**Deterministic hygiene cross-check (advisory):** comparable is an open-source repo AND a repo-scorecard tool (e.g. OpenSSF Scorecard) is available in-session → run it against that repo, record per-check scores alongside strengths/weaknesses — a machine-checked number beside the qualitative signal. Tool absent → qualitative signals only; no gate needs it.

**Gate:** ≥3 competitors at T1+T2 each with strengths/weaknesses. If fails → `/ds-research` returned fewer than 3 T1+T2 sources → expand search with synonyms, retry once; still insufficient → proceed with available set, flag `low-sample-size: true`, note "Ideal synthesis may be speculative due to limited comparables" in report.

### Phase 4: Synthesize Ideal

Per **resolved** dimension (the scopes marked `ran` in the Scopes table; `--scope=` overrides):

1. Aggregate competitor signals — convergence vs divergence across T1/T2 sources.
2. Adjust for stated constraints — if user pinned language/framework/DB, "ideal" respects those.
3. Write one-paragraph ideal per dimension: concrete, opinionated, no hedging.
4. **Security/privacy ideal ([../core/principles.md §5](../core/principles.md)):** the synthesized ideal MUST reflect the security baseline regardless of competitor convergence — boundary validation at every system boundary, least privilege for credentials, no secrets in source, defense in depth (never single-control), vetted crypto only (no custom, no MD5/SHA1/DES/ECB). Competitor consensus contradicts baseline → baseline wins; flag deviation as finding.

Record one ideal paragraph per active scope: `{"architecture": "{one-paragraph ideal — concrete pattern + data flow}", "stack": "{one-paragraph ideal stack}", ...}`.

**Gate:** Every active scope has an ideal paragraph. If fails → insufficient competitor signals for a dimension (all T3 or inaccessible) → write `[LOW CONFIDENCE]`-tagged placeholder using only security baseline; flag dimension as `speculative`; note it in gap table header.

### Phase 5: Gap Table

For each resolved dimension, compare ideal vs current (current from blueprint profile + `ds/audit/findings.md`) and write one row per gap. Row schema, allowed values, row template, `gap_type` enum, aggregate-score caveat, and Category A/B rules: [references/gap-row-format.md](references/gap-row-format.md).

Write gap entries to `ds/audit/findings.md` with `scope=ideal-gap` and `category` column set. `--preview`: print, don't write.

**Gate:** Every dimension has at least one row (or explicit "no gap" entry). If fails → dimension marked `speculative` in Phase 4 + current state unknown (no profile, no findings) → insert `"current: unknown — insufficient data"` row with `gap_type: unknown`, `category: B`, `proposal: "Manual assessment required"` so consumers don't silently miss a dimension.

### Phase 6: Approve [SKIP if --preview]

**Default:** each Category B gap resolves to `close` or `defer` using the same impact/effort/risk reasoning an approval block would show (constraint-conflicting or low-confidence gaps default to `defer`), recorded in the summary; nothing here matches the irreversible-exception list — Category B only closes findings, never mutates code.

**`--ask`:** present every Category B gap in one block — one scannable line per gap (`dimension · gap_type · current → proposal`) grouped by dimension with counts, and state the question (`Decide these N gaps?`):

> "These gaps change architecture or scope. For each: **Close** (commit to fixing), **Defer** (note but leave for later), **Intentional deviation** (record as ADR — we chose not to match the ideal)."

Ask per row, plus per-dimension bulk (`Close all <dimension>`) alongside a total `Close all`; "all" = exactly the displayed set.

Per "Intentional deviation" → offer `/ds-docs --adr` to record rationale (so future contributors see *why*).

Category A gaps recorded as findings but not executed here — consumers (ds-ship, ds-review) pick up `scope=ideal-gap` A findings and execute.

**Gate:** Every B gap has a decision. If fails → user skipped one or more B gaps without choosing → re-present each undecided gap individually, require a choice; user still declines → record `decision: deferred (no response)` so no gap is left unknown.

### Phase 7: Record [SKIP if --preview]

1. Update `ds/audit/findings.md` meta header scopes list to include `ideal-gap`.
2. `close` decision → finding remains, `disposition=needs-execution`.
3. `defer` decision → finding remains, `disposition=deferred`.
4. `intentional-deviation` → finding `disposition=skipped (intentional)`; ADR written to `docs/adr/NNNN-{slug}.md` if user agreed — via `/ds-docs --adr` when present; absent → write a minimal ADR inline (Context / Decision / Consequences, same path + numbering).

**Gate:** Every B gap persisted with its decision — findings file's `ideal-gap` row count ≥ the gap-row count written in Phase 5. If fails → `ds/audit/findings.md` write failed (file locked, disk error) → print the gap decisions inline as a fallback, surface write error with target path + OS error, ask user to resolve before re-running Phase 7. Zero gaps left undecided (resolved inline in Phase 6, including by default) — a gap left undecided → assign `decision: deferred (no response)` here before Summary.

### Phase 8: Summary

Disposition accounting — totals balance.

```
Benchmark: {problem-space}
Scopes: {ran: a, b, c} · {N/A: d — reason}
Competitors: {n} (T1: {x}, T2: {y}, T3: {z})

| Dimension     | Gaps  | Closed | Deferred | Intentional | Skipped | No-gap |
|---------------|-------|--------|----------|-------------|---------|--------|
| {dim}         | {n}   | {n}    | {n}      | {n}         | {n}     | {n}    |
```

`ds-benchmark: {OK|WARN|FAIL} | Gaps: {n} | Close: {n} | Defer: {n} | Intentional: {n} | Skipped: {n} | Total: {n}`

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} comparable projects benchmarked across {m} dimensions — "ideal" is now externally calibrated, not your internal taste`
- `{n} gaps identified between project and ideal: {n} accepted (close), {n} deferred, {n} declared intentional with ADR — every architectural divergence is now a deliberate decision, not a forgotten one`
- `Stack-fitness gap closed: {old-tech} → {new-tech} proposal documented with effort + risk — informed migration path replaces vague "we should modernize"`

**Gate:** Every gap has exactly one decision; accounting balances. If fails → accounting mismatch (Close + Defer + Intentional + Skipped ≠ total) → identify missing gap IDs, assign `decision: deferred (accounting-fix)`, recompute table, add WARN `"{n} gap(s) auto-deferred to balance accounting"`.

## Quality Gates

- Research budget respected: `/ds-research` returns on its own time; do not spawn parallel research beyond the delegated call.
- Intentional deviation always offered — the ideal is not the law, the user's constraints win.
- W1: every competitor claim cites source URL + CRAAP+ tier. W2: ideal synthesis honors stated constraints — never proposes a stack change the user pinned out. W3: only `ds/audit/findings.md` + optional ADRs written. W4: re-read blueprint profile before Gap phase. W5: `[single-source]`-labeled claim → MEDIUM confidence, do not promote to "ideal". W6: every active scope produces a row. W7: dedup competitor claims across sources — merge "do this" signals, keep strongest source. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W12: derive the "ideal" from verified evidence across comparables — never reverse-engineer it to favor a predetermined choice or special-case the metrics.
- W8: quote all URLs. <!-- portable-only -->

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

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
