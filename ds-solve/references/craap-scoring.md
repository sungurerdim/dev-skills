# CRAAP+ Scoring for ds-solve Research

Subset of the full CRAAP+ methodology, covering the scoring dimensions used by ds-solve's Research phase to rank alternatives.

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
