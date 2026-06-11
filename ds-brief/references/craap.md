# CRAAP+ Source Reliability (ds-brief, self-contained)

Standalone copy adapted for report sourcing. Every claim in a brief carries ≥1 resolvable source; every datum is confirmed by ≥2 independent sources or visibly flagged. This file defines how a source is scored, tiered, and how contradictions resolve. No dependency on any other skill.

## Source Tiers

| Tier | Score | Type |
|------|-------|------|
| T1 | 95-100 | Official / authoritative (law text, govt gazette, RFC, vendor docs, standards body) |
| T2 | 85-94 | Official repo / primary record (releases, CHANGELOG, registry, court ruling, regulator circular) |
| T3 | 70-84 | Recognized experts (core contributors, named domain authorities, academic PDF) |
| T4 | 55-69 | Community curated (SO high-votes, established trade press) |
| T5 | 40-54 | General community (blogs, Reddit, forums) |
| T6 | 0-39 | Unverified (AI-generated, undated, anonymous, >12mo on volatile topic) |

In the HTML report, tiers collapse to two visible chip: official | secondary** (secondary, T3-T6 → amber chip). The numeric tier/score stays in the findings artifact for ordering.

## Modifiers

| Condition | Effect |
|-----------|--------|
| Fresh 0-3mo | +10 |
| Core maintainer / domain authority / named author | +10 |
| Cross-verified by independent source | +10 |
| Cited by 2+ AI search engines independently | +15 |
| High engagement | +5 |
| Dated >12mo (volatile topic) | -15 |
| Sponsored / paid content | -15 |
| Vendor self-promotion | -5 |
| AI-generated without human review | -20 |
| Anonymous / no author attribution | -10 |

## CRAAP+ Dimensions

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

Score < 50 → discard (or include only with explicit `[doğrulanmadı]` caveat and no datum dependence). Irrelevant → discard. Duplicate / mirror → skip (does NOT count toward the 2× independence requirement). Outdated >2y on a volatile topic → flag, seek newer.

## Verification Rules

1. **Triangulation:** No datum enters the SSOT block unless confirmed by ≥2 **independent** sources (independence test defined in [verification.md](verification.md)). Single-source datum → keep with amber "tek kaynak" badge, never silently.
2. **Citation:** Every claim cites ≥1 source whose URL resolves. Dead/inaccessible link → mark, don't drop the discipline.
3. **Recency:** Statistics, prices, market/tech claims — newest source >12mo old → flag "potentially outdated" in the report.
4. **Source diversity:** Valid brief draws from ≥2 categories (official/institutional, academic, expert/practitioner, community). Single-category → confidence downgrade.
5. **Bias:** Flag commercial interest in the conclusion; apply vendor self-promotion modifier.

## Confidence Levels

| Condition | Level |
|-----------|-------|
| ≥2 T1 agree, triangulated, no contradictions | HIGH |
| T1-T2 majority, minor contradictions resolved | MEDIUM |
| Mixed sources, unresolved conflicts, thin coverage | LOW |

Never report HIGH without cross-verification.

## Contradiction Resolution

Order: **Security/legal authority override > T1 overrides all > Newer wins (same tier) > Higher engagement > Note unresolved.** Resolution picks a `winner` by argmax(trustScore) but the disagreement is preserved and shown in the report (both candidates, with tier + URL) — never silently dropped.

## §Security/Legal Authority Override

For queries about CVEs, secure coding, threat models, cryptography, **or binding legal/regulatory text**, T1 authoritative sources (OWASP, NIST, CVE/NVD, vendor security advisories, the official law text / gazette / regulator) ALWAYS rank above T3+ blogs regardless of CRAAP+ delta. Authoritative truth is not democratic. A secondary source may explain; only the primary source establishes.

**Source of this methodology:** OWASP Secure Coding Practices (https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/); NIST SP 800-218; CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose — California State University, Chico). AEO modifiers: CXL AEO Guide (2026), Ahrefs AI Search Traffic Study (2025).

## Quality Gate (before report build)

Verify: ≥2 source categories present, ≥1 band-A source, no unsupported claim in the SSOT, every datum either ≥2-independent-confirmed or flagged. Gate fails → report LOW confidence with explicit gaps in the "Bilinmeyenler / Belirsizler" section rather than presenting thin evidence as reliable.
