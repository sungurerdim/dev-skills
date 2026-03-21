# CRAAP+ Research Methodology

## Source Tiers

| Tier | Score | Type |
|------|-------|------|
| T1 | 95-100 | Official docs (MDN, RFC, vendor) |
| T2 | 85-94 | Official repo (releases, CHANGELOG) |
| T3 | 70-84 | Recognized experts (core contributors) |
| T4 | 55-69 | Community curated (SO high votes) |
| T5 | 40-54 | General community (blogs, Reddit) |
| T6 | 0-39 | Unverified (AI-gen, >12mo, unknown) |

## Modifiers

| Condition | Effect |
|-----------|--------|
| Fresh 0-3mo | +10 |
| Core maintainer / domain authority | +10 |
| Cross-verified by independent source | +10 |
| High engagement | +5 |
| Dated >12mo | -15 |
| Sponsored / paid content | -15 |
| Vendor self-promotion | -5 |
| AI-generated without human review | -20 |
| Anonymous / no author attribution | -10 |

## CRAAP+ Scoring Dimensions

| Dimension | Weight | Scoring |
|-----------|--------|---------|
| Currency | 20% | <3mo: 100, 3-12mo: 70, 1-2y: 40, >2y: 10 |
| Relevance | 25% | Direct: 100, Related: 70, Tangential: 30 |
| Authority | 25% | T1: 100, T2: 85, T3: 70, T4: 50, T5: 30 |
| Accuracy | 20% | Cross-verified: 100, Single: 60, Unverified: 30 |
| Purpose | 10% | Educational: 100, Info: 80, Commercial: 40 |

## Quality Bands

| Band | Score | Meaning |
|------|-------|---------|
| [A] Primary | 85-100 | Core evidence |
| [B] Supporting | 70-84 | Corroborating |
| [C] Background | 50-69 | Context only |
| [WARN] | <50 | Replace source |

Score < 50 → discard. Irrelevant → discard. Duplicate → skip. Outdated >2y → flag, seek newer.

## Verification Rules

1. **Triangulation + Citation:** No claim enters synthesis unless verified by 2+ independent sources (different organizations, not mirrors). Every claim cites at least one source. Remove unsupported claims.

2. **Recency Validation:** For statistics, market data, and tech claims: if newest source >12mo old, flag as "potentially outdated" in output.

3. **Source Diversity:** Valid research requires sources from ≥2 categories: official/institutional, academic/research, expert/practitioner, community/market. Single-category → confidence downgrade.

4. **Bias Detection:** Flag sources with commercial interest in the conclusion. Apply vendor self-promotion modifier.

## Confidence Levels

| Condition | Level |
|-----------|-------|
| 2+ T1 agree, triangulated, no contradictions | HIGH |
| T1-T2 majority, minor contradictions resolved | MEDIUM |
| Mixed sources, unresolved conflicts, thin coverage | LOW |

Never report HIGH without cross-verification.

Contradiction resolution: T1 overrides all > Newer wins (same tier) > Higher engagement > Note unresolved.

## Quality Gate

Before returning output, verify: ≥2 source categories, ≥1 band-A source, no unsupported claims in synthesis. If gate fails, report LOW confidence with explicit gaps rather than presenting thin evidence as reliable.

## Deep Mode (Iterative Deepening)

1. **Seed:** 5 parallel searches, 10-15 sources
2. **Backward snowball:** extract references from T1-T2 sources
3. **Forward snowball:** newer sources citing initial results
4. **Keyword expansion:** new terms discovered → expanded search

Saturation: stop when last 3 sources repeat themes or 80%+ overlap.

## Dependency Mode

Registry endpoints for version/CVE checking:

| Ecosystem | Endpoint |
|-----------|----------|
| Python | `pypi.org/pypi/{pkg}/json` |
| Node | `registry.npmjs.org/{pkg}` |
| Rust | `crates.io/api/v1/crates/{pkg}` |
| Go | `pkg.go.dev/{pkg}?tab=versions` |

**Flow:** Fetch latest → SemVer compare → Changelog for major → CVE check → Deprecation check. Batch by ecosystem, parallel fetch same registry, sequential changelog for major only.
