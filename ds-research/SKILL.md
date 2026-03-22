# /ds-research

**Smart Research** — Parallel search, tier sources, synthesize, recommend.

## Triggers

- User runs `/ds-research`
- User asks to research a topic, compare technologies, or investigate solutions
- User asks "what's the best way to...", "compare X vs Y", or "what are the options for..."
- User needs evidence-based analysis with source verification

## Contract

- Searches both local codebase files and web sources.

## Arguments

| Flag | Effect |
|------|--------|
| `--quick` | T1-T2 sources only |
| `--deep` | All tiers, resumable |

Without flags: present depth selection to the user.

**Do NOT:** Fabricate sources or URLs, present T5/T6 sources without confidence caveat, skip contradiction resolution when sources disagree, or synthesize without citing specific source tiers.

## Execution Flow

Setup → Parse Query → Research → Synthesize → Output

### Phase 1: Setup [SKIP with flags]

Recovery check: if progress artifact exists from prior deep run, ask: Resume / Start fresh.

1. **Depth selection.** If no `--quick`/`--deep` flag, ask the user:
   - **Quick** — T1-T2 sources only, fast results
   - **Standard** — T1-T4 sources, balanced depth
   - **Deep** — all tiers, 20+ sources, resumable

2. **Scope selection.** Ask what areas to search:
   - Local codebase, Security/CVE, Changelog/releases, Dependencies

### Phase 2: Parse Query

Extract from arguments: concepts, tech domain, comparison mode, search mode (troubleshoot/changelog/security).

**Date handling:** Resolve current date from system context. Include it explicitly in every search query to prevent stale results (e.g., "React 19 migration guide 2026").

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

### Phase 4: Synthesize

Validate outputs: verify all claims cite sources, check for contradictions, remove unsupported assertions. T1-T2 sources: resolve conflicts. T3+: aggregate.

**Mandatory saturation gate:** After each batch, if 3+ T1/T2 sources agree, skip remaining lower-tier searches.

### Phase 5: Output

Executive summary, evidence hierarchy (primary T1-T2, supporting T3-T4), contradictions resolved, knowledge gaps, recommendation (DO/DON'T/CONSIDER).

**Source format (compact):**
```
Sources:
  [A] T1|92|docs.example.dev|LibX v5 Migration Guide
  [A] T2|88|github.com/org/libx|v5.0.0 Release Notes
  [B] T3|74|devblog.example.com|Practical LibX v5 Patterns
  [C] T4|62|stackoverflow.com|LibX v5 SSR gotchas
```

Bands: [A] Primary (85-100), [B] Supporting (70-84), [C] Background (50-69).

## Quality Gates

- Every claim cites at least one source with CRAAP+ score ≥50
- Contradictory sources noted explicitly with confidence assessment
- No fabricated URLs or references — only cite actually retrieved sources

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No web results | Fall back to local codebase search only |
| All sources score <50 | Report low-confidence findings, recommend manual verification |
| Query too broad | Ask user to narrow scope with specific sub-questions |