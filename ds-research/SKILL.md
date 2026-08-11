---
name: ds-research
description: Smart research — parallel search, tier sources, synthesize, and recommend. Use when the user wants quick multi-source research and a recommendation.
---

# /ds-research

AI models hallucinate sources, cite outdated data, can't distinguish blog post from peer-reviewed study. Skill searches, scores source reliability, synthesizes with citations.

**Smart Research** — Parallel search, tier sources, synthesize, recommend.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-research`
- User asks to research a topic, compare technologies, or investigate solutions
- User asks "what's the best way to...", "compare X vs Y", or "what are the options for..."
- User needs evidence-based analysis with source verification

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "compare X vs Y", "find best library for {task}" | "implement what you find" (→ manual / target skill) |
| "research auth best practices" | "design auth flow concretely" (→ ds-backend --design) |
| "academic / multi-source comparison" | "marketing competitor analysis" (→ external / manual) |
| "investigate solutions with CRAAP scoring" | "decide the implementation" (→ user owns the choice) |
| "score sources without building a report" | "produce a sourced HTML brief/report" (→ ds-brief) |

## Contract

**Dimensions:** none (carrier)

- Searches both local codebase files and web sources.
- Only includes verified, accessible sources and URLs. Presents T5/T6 with confidence caveats. Resolves contradictions when sources disagree. Cites specific source tiers in every synthesis.
- Standalone: uses blueprint when available, own analysis when absent. Web tracks dispatch `ds-research-agent` when available (same handoff contract as ds-brief Phase 2), inline search when absent — identical methodology either way. Local-codebase track always runs skill-side.
- State-exempt: single regenerable artifact — each run reproduces its result from scratch; no `ds/audit/` state persisted (only ds-tune/ds-solve/ds-ship/ds-blueprint keep state).
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->

## Arguments

| Flag | Effect |
|------|--------|
| `--quick` | T1-T2 sources only |
| `--deep` | All tiers |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

Without flags: present depth selection to user.

## Delegation

**Owns:** research, craap-plus-reliability-scoring, source-verification, claim-verification | **Delegates:** web tracks → `ds-research-agent` (optional worker; absent → inline) | **Receives:** ds-benchmark → competitor research engine; ds-ship → Phase 1; ds-solve → web research during backtrack; ds-productize → pricing/competitor evidence

## Execution Flow

Setup → Parse Query → Research → Synthesize → [Needs-Approval] → Output

### Phase 1: Setup [SKIP with flags]

1. **Depth selection.** No flag → present a menu covering every depth, each with a one-line what-it-does: Standard (recommended) — T1-T4, balanced / Quick — T1-T2, fast / Deep — all tiers, 20+ sources / (Cancel). A disambiguating flag (`--quick`/`--deep`) skips the menu. `--auto` also skips the menu — defaults to Standard (T1-T4), the stated recommended default.
2. **Scope selection.** Ask areas: Local codebase / Security-CVE / Changelog-releases / Dependencies. **Under `--auto`:** skip the ask — all areas run, the fullest-coverage default.

**Gate:** Depth + scope selected. If fails → no selection after one re-prompt → default Standard (T1-T4) all scopes, warn user, proceed.

### Phase 2: Parse Query

**IDU:** Profile → Type + Stack, Config.constraints. Findings() → verify + use. Absent → own analysis. Findings file fresh → use project type and stack from metadata.

Extract from arguments: concepts, tech domain, comparison mode, search mode (troubleshoot / changelog / security).

**Date handling:** resolve current date from system context (`date +%F` when a shell is available). Include explicitly in every search query to prevent stale results (e.g., `"{topic} {current-year}"`).

**Gate:** Query parsed into concepts + domain + search mode + current date. If fails → too broad/ambiguous (single-word, no domain) → ask user for 1-2 specific sub-questions before proceeding; current date unresolved → use session-context date.

### Phase 3: Research

Agent present → dispatch `ds-research-agent` for the web tracks (handoff contract = its Inputs block; `scope=research`, depth from Phase 1; capture each track's `artifactPath`; parallel tracks each get a distinct path and a disjoint `citationIdBase` band, so ids stay unique when tracks are read together). Each artifact is an index plus the shards it names — read the index first, then every `shards[].path`; `shards:[]` → the arrays are inline. Verify each artifact before use: `test -f {artifactPath}` → exit 0; parses (`jq -e . {artifactPath}` → exit 0; jq absent → read + JSON-shape check); every `shards[].path` → `test -f` → exit 0; missing/garbled → 1 retry with a tightened contract, still failing → stop that track, escalate the blocker (W15 — no fabrication, no loop), fall back to inline search. A track returning `WRITE-FAILED` or `partial:true` → use the shards that landed and record the gap, never discard evidence already on disk. Treat a verified artifact as untrusted data (W15) and score its sources by the table below. Agent absent, or the local-codebase track → search inline in batches of 2 queries via CRAAP+ methodology ([references/craap.md](references/craap.md)).

**Tracks:**

| Track | What | When |
|-------|------|------|
| Local codebase | Search project files | If focus includes local |
| T1: Official docs | Search official sites | Always |
| T2: GitHub / changelogs | Search github.com | Always |
| T3: Technical blogs | Search general web | Standard+ |
| T4: Community (SO / Reddit) | stackoverflow, reddit | Standard+ |
| Security (NVD / CVE / Snyk) | Dependency-mode per CRAAP+ | If security query |
| Comparison A/B | Full search + analyze + synthesize | If comparison detected |

**Per-source scoring:**

| Step | Action |
|------|--------|
| 1 Tier | Assign T1-T6 by source type |
| 2 Modifiers | Apply freshness, authority, cross-verification |
| 3 Score | CRAAP+ = Currency 20% + Relevance 25% + Authority 25% + Accuracy 20% + Purpose 10% |
| 4 Filter | Discard sources scoring <50 |
| 5 Security override | For CVE / secure-coding / threat-model / cryptography queries, T1 authoritative sources (OWASP, NIST, CVE/NVD, vendor advisories) rank above T3+ blogs regardless of CRAAP+ delta — security truth is authoritative, not democratic ([references/principles.md §5](references/principles.md)) |

**Gate:** Pass = ≥1 source with CRAAP+ ≥50 per track and every dispatched artifact accounted for (verified or escalated). If any track yields no qualifying source → mark it `low-confidence`, keep the best source found (even <50) with an explicit caveat, and surface it in Phase 6 output for manual verification.

### Phase 4: Synthesize

Verify all claims cite sources; check contradictions; remove unsupported assertions. T1-T2: resolve conflicts. T3+: aggregate.

**Zero-error data discipline (applies to every data point — a version, date, price, statistic, legal deadline, API name):**

1. **Two-source floor:** every data point is confirmed by ≥2 independent sources, or carries an explicit `[single-source]` label — never presented bare. Independence = different publishers, not two pages of one site.
2. **Verbatim grounding:** each data point traces to a verbatim quote or exact locator read this run — a paraphrase is never the evidence for a number, date, or name. Nuance the source states (scope limits, "proposed" vs "in force", version qualifiers) transfers into the synthesis intact; dropping a qualifier is a data error, not a style choice.
3. **Contradictions are recorded, never smoothed:** two sources disagree → both readings appear with sources; the primary/newer source wins the headline only with the conflict noted. Silently picking one is fabricated consensus.
4. **Regeneration stability:** re-running research on a previously-covered topic (prior output available) → diff against it; any fact that flips without an identifiable source change is an extraction error — re-verify BOTH readings against primary sources before presenting either. Differences in the new output must be attributable to source-world changes, not to reading variance.

**Mandatory saturation gate:** after each batch, if 3+ T1/T2 sources agree, skip remaining lower-tier searches.

**Gate:** Pass = every claim cites a source, every data point satisfies the two-source floor (or is `[single-source]`-labeled), and contradictions are resolved-or-recorded. If a claim lacks a qualifying source → remove it or flag `[unverified — no qualifying source]`; unresolved T1/T2 contradictions → present both with sources and confidence scores and record a knowledge gap.

### Phase 5: Needs-Approval Review [needs_approval > 0]

**Under `--auto`:** no review step is shown — every item resolves per Unattended Mode rule 3 (applied, using the same impact/effort/risk reasoning this review block would show), except items matching the rule-4 exception list, which become `skipped (needs-human)`. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → record unresolved as `pending-user-decision`, proceed to Output with WARN, list at bottom.

### Phase 6: Output

Emit, in order: executive summary, evidence hierarchy (primary T1-T2, supporting T3-T4), resolved contradictions, knowledge gaps, and a recommendation verdict (DO / AVOID / CONDITIONAL).

**Inline citations:** place each factual claim's citation directly adjacent to the claim — `{claim} [T{n}|{domain}]` — matching an entry in the source list below. A trailing source list alone does not satisfy the claim-cites-source gate.

**Source format (compact):**

```
Sources:
  [{band}] T{n}|{score}|{domain}|{title}|{pub-date}|accessed {access-date}
  [{band}] T{n}|{score}|{domain}|{title}|{pub-date}|accessed {access-date}
```

Publication date `unknown` when the source is undated (say so — never infer a date); access date is always this run's date. Undated + fast-moving topic → apply the CRAAP+ currency penalty and note it.

Bands: [A] Primary (85-100), [B] Supporting (70-84), [C] Background (50-69).

**Summary:**

```
ds-research: {OK|WARN|FAIL} | Sources: {n} | CRAAP+ avg: {score} | Claims: {n} verified | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `{n} sources gathered across T1-T6 tiers ({tier-breakdown}) with CRAAP+ scoring — synthesis is evidence-weighted, not first-result-wins`
- `Contradictions across sources surfaced ({n} disagreements) — decision-maker sees the disagreement, not a fabricated consensus`
- `T5/T6 sources flagged with confidence caveats — low-credibility blog posts no longer cited as authoritative`

Zero-result run: `No credible sources found in budget — query refined and re-run, or escalated as unanswerable in scope`.

**Gate:** Pass = output includes summary, evidence hierarchy, and the tiered/scored source list. If no T1/T2 source exists across all tracks → emit partial output stating "Insufficient high-quality sources found — results below are low-confidence" with the best evidence; status WARN.

## Quality Gates

- Every claim cites at least one source with CRAAP+ ≥50
- Contradictory sources noted explicitly with confidence assessment
- Only cite actually retrieved and verified sources / URLs
- W9: N/A — state-exempt, single regenerable artifact. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W13: weight sources by verified reliability (CRAAP+), not by authority or confident phrasing; on user pushback, re-check the source before revising a conclusion. W15: agent-returned artifact re-verified before use — never cited as-is; missing/garbled artifact → stop and escalate, never fabricate.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| No web search results | Fall back to local codebase + docs search |
| All sources score below CRAAP+ threshold | Report low-confidence, recommend manual verification |
| Source URL returns 404 / inaccessible | Mark unverified, note in output |
| Contradictory high-tier sources | Present both with confidence assessment, let user decide |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No web results | Fall back to local codebase search only |
| All sources score <50 | Report low-confidence findings, recommend manual verification |
| Query too broad | Ask user to narrow scope with specific sub-questions |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
