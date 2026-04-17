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

---

## Answer Engine Optimization (AEO)

AI-powered search engines are growing traffic source and citation channel. Sources performing well in AI search results demonstrate higher findability and structured authority.

### AI Search Landscape (2025-2026)

| Metric | Value |
|--------|-------|
| AI search traffic growth | 357% YoY (1.13B visits, June 2025) |
| ChatGPT search share | 55-60% of AI search traffic |
| Perplexity share | 18-22% |
| Gemini share | 10-14% |
| Other (Copilot, You.com, etc.) | 6-15% |

### AEO Optimization Tactics

Sources optimized for AI citation tend to score higher on CRAAP+ dimensions (structured, authoritative, current).

| Tactic | Description | CRAAP+ Impact |
|--------|-------------|---------------|
| Answer-first content | Lead with direct answers, then expand with detail | +Relevance (parseable) |
| Semantic structure | Use clear headings, lists, tables; machine-readable layout | +Authority (structured) |
| Citation density | Reference primary sources, link to data | +Accuracy (verifiable) |
| Schema markup | Implement FAQ, HowTo, Article structured data | +Relevance (discoverable) |
| Freshness signals | Regular updates with visible dates | +Currency (timestamped) |
| Topical authority | Deep coverage of a subject area across multiple pages | +Authority (expertise) |

### CRAAP+ Scoring Adjustment for AI-Cited Sources

Sources actively cited by AI search engines demonstrate verified findability and structured quality.

| Condition | Effect |
|-----------|--------|
| Cited by 1+ AI search engine (ChatGPT, Perplexity, Gemini) | +10 |
| Cited by 2+ AI search engines independently | +15 |
| Appears in AI-generated answer with direct attribution | +5 |

Apply this modifier in the same phase as other CRAAP+ modifiers. AI citation = signal of structured quality, not a guarantee of accuracy — standard triangulation rules still apply.

**Source:** CXL AEO Guide (2026), Frase.io AEO Guide, Ahrefs AI Search Traffic Study (2025)

---

## AI-Assisted Research Verification

When using AI tools (LLM assistants, code generators, AI search) as part of research or development workflow, apply these additional verification gates. AI output is T6 by default until verified.

### Verification Rules for AI-Generated Content

| Rule | Detect | Fix |
|------|--------|-----|
| Never trust AI output without review | AI-generated code, claims, or citations accepted without human verification | Review all AI output as if from an unknown junior contributor. Verify every claim against primary sources |
| Cross-model verification | Single AI model used for both generation and review | Use a secondary AI model or manual review for verification. Generator must not review itself |
| Hallucinated references | AI cites packages, APIs, papers, or URLs that do not exist | Verify every AI-cited source exists before inclusion. Check package registries, resolve URLs, search for papers |
| Security audit for AI code | AI-generated code deployed without security review (Veracode 2025: 45% of AI code has vulnerabilities; CodeRabbit: 2.74x higher vulnerability rate) | Run SAST + DAST on all AI-generated code. Secrets scanning in pre-commit + CI. Never let AI handle auth/payment/encryption without domain expert review |
| Specification before generation | AI prompted without upfront specification, → architectural drift | Write detailed specs before invoking AI. Break work into small, chunked tasks (one function/feature). Provide existing code examples for pattern matching |

### CRAAP+ Scoring for AI-Generated Sources

| Condition | Effect |
|-----------|--------|
| AI-generated content without human review | -20 (already in Modifiers) |
| AI-generated content with expert verification and source triangulation | -5 (reduced penalty) |
| AI-hallucinated package or API (confirmed non-existent) | Discard immediately |

### The 70/30 Delegation Rule

When using AI assistants for research or development, delegate appropriately:

- **AI handles (70%):** Boilerplate, CRUD, test generation, documentation, refactoring, initial source discovery
- **Human handles (30%):** Architecture decisions, security-sensitive code, novel algorithms, source triangulation, final claim verification

**Source:** Addy Osmani (LLM Coding Workflow 2026), Veracode 2025 AI Code Security Report, CodeRabbit Dec 2025 AI Code Analysis, Simon Willison (AI-assisted engineering distinction)
