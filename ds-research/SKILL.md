# /ds-research

AI models hallucinate sources, cite outdated data, and can't distinguish a blog post from a peer-reviewed study. This skill searches, scores source reliability, and synthesizes with citations.

**Smart Research** — Parallel search, tier sources, synthesize, recommend.

## Triggers

- User runs `/ds-research`
- User asks to research a topic, compare technologies, or investigate solutions
- User asks "what's the best way to...", "compare X vs Y", or "what are the options for..."
- User needs evidence-based analysis with source verification

## Contract

- Searches both local codebase files and web sources.
- Fully functional standalone — zero dependency on other skills. When blueprint profile exists, uses project context. When absent, runs own complete analysis with identical quality.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| `--quick` | T1-T2 sources only |
| `--deep` | All tiers, resumable |

Without flags: present depth selection to the user.

Only include verified, accessible sources and URLs. Present T5/T6 sources with confidence caveat. Resolve contradictions when sources disagree. Cite specific source tiers in every synthesis.

## Execution Flow

Setup → Parse Query → Research → Synthesize → [Needs-Approval] → Output

### Phase 1: Setup [SKIP with flags]

Recovery check: if progress artifact exists from prior deep run, ask: Resume / Start fresh.

1. **Depth selection.** If no `--quick`/`--deep` flag, ask the user:
   - **Quick** — T1-T2 sources only, fast results
   - **Standard** — T1-T4 sources, balanced depth
   - **Deep** — all tiers, 20+ sources, resumable

2. **Scope selection.** Ask what areas to search:
   - Local codebase, Security/CVE, Changelog/releases, Dependencies

**Gate:** Depth and search scope selected.

### Phase 2: Parse Query

**Findings file check:** If `.ds-findings.md` exists, check for relevant findings that provide research context. Use project type and stack from findings metadata.

**IDU:** Profile → Type + Stack, Config.constraints. Findings() → verify + use. Absent → own analysis.

Extract from arguments: concepts, tech domain, comparison mode, search mode (troubleshoot/changelog/security).

**Date handling:** Resolve current date from system context. Include it explicitly in every search query to prevent stale results (e.g., "React 19 migration guide 2026").

**Gate:** Query parsed into concepts, domain, and search mode with current date resolved.

### Phase 3: Research

Search in batches of 2 search queries, applying the CRAAP+ methodology from [references/craap.md](references/craap.md):

| Track | What | When |
|-------|------|------|
| Local codebase | Search project files | If focus includes local |
| T1: Official docs | Search official sites | Always |
| T2: GitHub/changelogs | Search github.com | Always |
| T3: Technical blogs | Search general | Standard+ |
| T4: Community (SO/Reddit) | Search stackoverflow, reddit | Standard+ |
| Security (NVD/CVE/Snyk) | Dependency mode per CRAAP+ | If security query |
| Comparison A/B | Full search + analyze + synthesize | If comparison detected |

For each source found:
1. Assign tier (T1-T6) based on source type
2. Apply modifiers (freshness, authority, cross-verification)
3. Calculate CRAAP+ score (Currency 20%, Relevance 25%, Authority 25%, Accuracy 20%, Purpose 10%)
4. Discard sources scoring <50

**Gate:** At least one source with CRAAP+ score >=50 found per search track.

### Phase 4: Synthesize

Validate outputs: verify all claims cite sources, check for contradictions, remove unsupported assertions. T1-T2 sources: resolve conflicts. T3+: aggregate.

**Mandatory saturation gate:** After each batch, if 3+ T1/T2 sources agree, skip remaining lower-tier searches.

**Gate:** All claims cite sources and contradictions resolved.

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 6: Output

Executive summary, evidence hierarchy (primary T1-T2, supporting T3-T4), contradictions resolved, knowledge gaps, recommendation (DO/AVOID/CONSIDER).

**Source format (compact):**
```
Sources:
  [{tier}] {Tn}|{score}|{domain}|{title}
  [{tier}] {Tn}|{score}|{domain}|{title}
  ...
```

Bands: [A] Primary (85-100), [B] Supporting (70-84), [C] Background (50-69).

**Summary format:**
```
ds-research: {OK|WARN|FAIL} | Sources: N | CRAAP+ avg: {score} | Claims: N verified | Fixed: N | Skipped: N | Failed: N | Total: N
```

**Gate:** Output includes executive summary, evidence hierarchy, and source list with tier/score.

## Quality Gates

- Every claim cites at least one source with CRAAP+ score ≥50
- Contradictory sources noted explicitly with confidence assessment
- Only cite actually retrieved and verified sources and URLs
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No web search results | Fall back to local codebase and documentation search |
| All sources score below CRAAP+ threshold | Report as low-confidence, recommend manual verification |
| Source URL returns 404 or is inaccessible | Mark source as unverified, note in output |
| Contradictory high-tier sources | Present both positions with confidence assessment, let user decide |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No web results | Fall back to local codebase search only |
| All sources score <50 | Report low-confidence findings, recommend manual verification |
| Query too broad | Ask user to narrow scope with specific sub-questions |