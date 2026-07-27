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

In the HTML report, tiers collapse to two visible chips: **official | secondary** (secondary = T3-T6 → amber chip). The numeric tier/score stays in the findings artifact for ordering.

**Tier is not the same as primary.** T1 measures *how authoritative a document is*; `primary` asks a narrower question: was it published by the authority that **issued this specific rule**, on that authority's own domain? A standards aggregator, a national gazette mirror, or a respected institute can be T1 and still not be the issuer. Load-bearing datums require a `primary` source, not merely a T1 one ([verification.md](verification.md) Rule 13) — this is the distinction that stops a brief from resting its central thresholds on well-written secondary material.

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
| Currency | 20% | <3mo: 100, 3-12mo: 70, 1-2y: 40, >2y: 10 — **normative text scores on consolidation, not age**: current consolidated version = 100 regardless of enactment year; an un-versioned reprint = 10 however recently it was published |
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

Score < 50 → discard (or include only with explicit `[unverified]` caveat and no datum dependence). Irrelevant → discard. Duplicate / mirror → skip (does NOT count toward the 2× independence requirement). Outdated >2y on a volatile topic → flag, seek newer.

## Verification Rules

1. **Triangulation:** No datum enters the SSOT block unless confirmed by ≥2 **independent** sources (independence test defined in [verification.md](verification.md)). Single-source datum → keep with amber "single source" badge, never silently.
2. **Citation:** Every claim cites ≥1 source whose URL resolves. Dead/inaccessible link → mark, don't drop the discipline.
3. **Recency:** Statistics, prices, market/tech claims — newest source >12mo old → flag "potentially outdated" in the report.
4. **Source diversity:** Valid brief draws from ≥2 categories (official/institutional, academic, expert/practitioner, community). Single-category → confidence downgrade.
5. **Bias:** Flag commercial interest in the conclusion; apply vendor self-promotion modifier.
6. **Dating:** Every source record carries a publication date and an access date. Undated source → `pubDate: unknown`, stated visibly — a date is never inferred from context or memory.

## Normative source ladder (legal / regulatory / standards topics)

Tier measures *how reliable a source is*. Binding force measures *whether it obliges the reader* — a different axis. A regulator's FAQ is a highly reliable T1 document that binds nobody; a rarely-read statute binds absolutely. Conflating the two produces the worst error a normative brief can make: a "Mandatory" badge on something that is merely advice.

| Rank | Instrument class | Binding force | Highest obligation badge it can justify |
|------|------------------|---------------|------------------------------------------|
| N1 | Constitution / primary legislation (law, code, statute) | Binds directly | `must` / `mustnot` |
| N2 | Regulation, decree, statutory instrument made under N1 | Binds within its enabling law | `must` / `mustnot` |
| N3 | Communiqué, by-law, binding regulator decision (board decision with sanction power) | Binds its addressees | `must` / `mustnot` |
| N4 | Binding case law (precedent-setting / unification-of-jurisprudence rulings) | Binds lower courts; predicts outcomes | `must` / `mustnot`, stated as settled interpretation |
| N5 | Non-precedential rulings, regulator guidance, FAQ, handbook | Persuasive, not binding | `should` at most |
| N6 | Recitals / preambles / explanatory memoranda | Interpretive aid, **not operative** | `should` at most — never `must` |
| N7 | Commentary, law-firm articles, trade press | No force | `should` / context only; never the sole basis for an obligation |

Rules that follow from the ladder:

- **An obligation badge cites its own rank.** `must` requires an N1-N4 citation. A `must` whose only support is N5-N7 is a failed validation — downgrade the badge or find the operative provision.
- **Recital ≠ article.** GDPR-style recitals, preambles, and explanatory notes are quoted as interpretation, never rendered as the rule itself. When a brief compares two regimes, an obligation present only in a recital on one side is a *difference*, not a match.
- **Guidance that restates law** carries the underlying provision as its citation; the guidance is the secondary chip beside it.
- **Two instruments conflict** → the higher rank wins, and the conflict is shown (the reader is often being told the wrong thing by a lower-ranked but more readable source).
- **Every normative claim also passes the currency gate** ([verification.md](verification.md) Rule 11): current consolidated text, amendments and annulments explicitly checked, in-force status stated.
- **Year-indexed amounts** (fines, thresholds, caps subject to annual revaluation) carry their index year and the revaluation mechanism. An amount without its year is a stale number waiting to happen.

## Confidence Levels

Bands are computed from the HIGH gate in [verification.md](verification.md) § Confidence, not judged. Summary of what each band means for the reader:

| Condition | Level |
|-----------|-------|
| Every HIGH-gate line passes — ≥95% double-confirmed, **every load-bearing datum on a primary source from the issuing authority**, clean source records, no dead links, no unresolved contradictions, derived claims premised, provisions register-checked, authority registers swept, every reader situation probed, thresholds double-read, red team clean, corpus fully accounted, saturation stop | HIGH |
| Gate passes on most lines; the named blockers are non-load-bearing single-source datums | MEDIUM — **a work state, not a shipping state**: run the escalation rounds first |
| Mixed sources, unresolved conflicts on load-bearing datums, thin coverage | LOW |

Never report HIGH without cross-verification, and never present a band without its plain-language sentence (verification.md § Confidence).

## Contradiction Resolution

Order: **Security/legal authority override > T1 overrides all > Newer wins (same tier) > Higher engagement > Note unresolved.** Resolution picks a `winner` by argmax(trustScore) but the disagreement is preserved and shown in the report (both candidates, with tier + URL) — never silently dropped.

## §Security/Legal Authority Override

For queries about CVEs, secure coding, threat models, cryptography, **or binding legal/regulatory text**, T1 authoritative sources (OWASP, NIST, CVE/NVD, vendor security advisories, the official law text / gazette / regulator) ALWAYS rank above T3+ blogs regardless of CRAAP+ delta. Authoritative truth is not democratic. A secondary source may explain; only the primary source establishes.

**Source of this methodology:** OWASP Secure Coding Practices (https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/); NIST SP 800-218; CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose — California State University, Chico). AEO modifiers: CXL AEO Guide (2026), Ahrefs AI Search Traffic Study (2025).

## Quality Gate (before report build)

Verify: ≥2 source categories present, ≥1 band-A source, no unsupported claim in the SSOT, every datum either ≥2-independent-confirmed or flagged, every obligation badge backed by a citation of sufficient rank (N1-N4 for `must`/`mustnot`), every cited provision version-checked, every derived claim premised. Gate fails → run the escalation rounds; still failing → report the honest band with explicit blockers and gaps in "Unknowns / Uncertainties" rather than presenting thin evidence as reliable.
