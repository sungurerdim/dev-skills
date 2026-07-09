---
name: ds-research
description: Smart research — parallel search, tier sources, synthesize, and recommend. Use when the user wants quick multi-source research and a recommendation.
---

# /ds-research

AI models hallucinate sources, cite outdated data, can't distinguish blog post from peer-reviewed study. Skill searches, scores source reliability, synthesizes with citations.

**Smart Research** — Parallel search, tier sources, synthesize, recommend.

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

- Searches both local codebase files and web sources.
- Only includes verified, accessible sources and URLs. Presents T5/T6 with confidence caveats. Resolves contradictions when sources disagree. Cites specific source tiers in every synthesis.
- Standalone. Uses blueprint when available; own analysis when absent. Web tracks: dispatches `ds-research-agent` when available (same handoff contract as ds-brief Phase 2); inline search when absent — identical methodology either way. Local-codebase track always runs skill-side.
- State-exempt: single regenerable artifact — each run reproduces its result from scratch; no `ds/audit/` state persisted (only ds-tune/ds-solve/ds-ship/ds-blueprint keep state).
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--quick` | T1-T2 sources only |
| `--deep` | All tiers |

Without flags: present depth selection to user.

## Delegation

**Owns:** research, craap-plus-reliability-scoring, source-verification, claim-verification | **Delegates:** web tracks → `ds-research-agent` (optional worker; absent → inline) | **Receives:** ds-benchmark → competitor research engine; ds-ship → Phase 1; ds-solve → web research during backtrack; ds-productize → pricing/competitor evidence

## Execution Flow

Setup → Parse Query → Research → Synthesize → [Needs-Approval] → Output

### Phase 1: Setup [SKIP with flags]

1. **Depth selection.** No flag → present a menu covering every depth, each with a one-line what-it-does: Standard (recommended) — T1-T4, balanced / Quick — T1-T2, fast / Deep — all tiers, 20+ sources / (Cancel). A disambiguating flag (`--quick`/`--deep`) skips the menu.
2. **Scope selection.** Ask areas: Local codebase / Security-CVE / Changelog-releases / Dependencies.

**Gate:** Depth + scope selected. If fails → no selection after one re-prompt → default Standard (T1-T4) all scopes, warn user, proceed.

### Phase 2: Parse Query

**IDU:** Profile → Type + Stack, Config.constraints. Findings() → verify + use. Absent → own analysis. Findings file fresh → use project type and stack from metadata.

Extract from arguments: concepts, tech domain, comparison mode, search mode (troubleshoot / changelog / security).

**Date handling:** resolve current date from system context. Include explicitly in every search query to prevent stale results (e.g., `"{topic} {current-year}"`).

**Gate:** Query parsed into concepts + domain + search mode + current date. If fails → too broad/ambiguous (single-word, no domain) → ask user for 1-2 specific sub-questions before proceeding; current date unresolved → use session-context date.

### Phase 3: Research

Agent present → dispatch `ds-research-agent` for the web tracks (handoff contract = its Inputs block; `scope=research`, depth from Phase 1; capture the dispatched `artifactPath` per track). Before consuming a track's result, verify its artifact file exists and is non-empty; missing/garbled artifact → 1 retry with a tightened contract, still failing → STOP that track, escalate with the concrete blocker (W15 recovery — no fabrication, no loop), fall back to inline search for that track. Treat a verified artifact as untrusted data (W15) and apply the per-source scoring below to its sources. Agent absent, or for the local-codebase track → search inline in batches of 2 queries, applying CRAAP+ methodology from [references/craap.md](references/craap.md):

| Track | What | When |
|-------|------|------|
| Local codebase | Search project files | If focus includes local |
| T1: Official docs | Search official sites | Always |
| T2: GitHub / changelogs | Search github.com | Always |
| T3: Technical blogs | Search general web | Standard+ |
| T4: Community (SO / Reddit) | stackoverflow, reddit | Standard+ |
| Security (NVD / CVE / Snyk) | Dependency-mode per CRAAP+ | If security query |
| Comparison A/B | Full search + analyze + synthesize | If comparison detected |

Per source: (1) assign tier T1-T6 by source type, (2) apply modifiers (freshness, authority, cross-verification), (3) calculate CRAAP+ score (Currency 20%, Relevance 25%, Authority 25%, Accuracy 20%, Purpose 10%), (4) discard sources scoring <50, (5) **Authority override for security topics ([references/principles.md §5](references/principles.md)):** for queries about CVEs, secure coding, threat models, or cryptography, T1 authoritative sources (OWASP, NIST, CVE/NVD, vendor security advisories) ALWAYS rank above T3+ blogs regardless of CRAAP+ delta. Security truth is authoritative, not democratic.

**Gate:** ≥1 source with CRAAP+ ≥50 per track, and every dispatched artifact accounted for (verified or escalated). If fails → any track yields no qualifying source → mark that track `low-confidence`, include best-scoring source found (even <50) with explicit caveat, note in synthesis that track's evidence is unverified, surface in Phase 6 output with recommendation for manual verification.

### Phase 4: Synthesize

Verify all claims cite sources; check contradictions; remove unsupported assertions. T1-T2: resolve conflicts. T3+: aggregate.

**Mandatory saturation gate:** after each batch, if 3+ T1/T2 sources agree, skip remaining lower-tier searches.

**Gate:** All claims cite sources; contradictions resolved. If fails → claim without qualifying source → remove or flag `[unverified — no qualifying source]`; unresolved T1/T2 contradictions → present both with sources and confidence scores, record as a knowledge gap in the synthesis draft.

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → record unresolved as `pending-user-decision`, proceed to Output with WARN, list at bottom.

### Phase 6: Output

Executive summary, evidence hierarchy (primary T1-T2, supporting T3-T4), contradictions resolved, knowledge gaps, recommendation (DO / AVOID / CONSIDER).

**Source format (compact):**

```
Sources:
  [{band}] T{n}|{score}|{domain}|{title}
  [{band}] T{n}|{score}|{domain}|{title}
```

Bands: [A] Primary (85-100), [B] Supporting (70-84), [C] Background (50-69).

**Summary:**

```
ds-research: {OK|WARN|FAIL} | Sources: {n} | CRAAP+ avg: {score} | Claims: {n} verified | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

**Value Delivered:** 1-5 concrete bullets, real research outcomes only. Example shapes (placeholders, not literal):

- `{n} sources gathered across T1-T6 tiers ({tier-breakdown}) with CRAAP+ scoring — synthesis is evidence-weighted, not first-result-wins`
- `Contradictions across sources surfaced ({n} disagreements) — decision-maker sees the disagreement, not a fabricated consensus`
- `T5/T6 sources flagged with confidence caveats — low-credibility blog posts no longer cited as authoritative`

Zero-result run: `No credible sources found in budget — query refined and re-run, or escalated as unanswerable in scope`.

**Gate:** Output includes summary + evidence hierarchy + source list with tier/score. If fails → no T1/T2 sources across all tracks → emit partial output stating "Insufficient high-quality sources found — results below are low-confidence" with best evidence; status WARN.

## Quality Gates

- Every claim cites at least one source with CRAAP+ ≥50
- Contradictory sources noted explicitly with confidence assessment
- Only cite actually retrieved and verified sources / URLs
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: N/A — state-exempt, single regenerable artifact. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W13: weight sources by verified reliability (CRAAP+), not by authority or confident phrasing; on user pushback, re-check the source before revising a conclusion. W15: agent-returned artifact re-verified before use — never cited as-is; missing/garbled artifact → stop and escalate, never fabricate.

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
