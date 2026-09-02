# CRAAP+ Source Reliability — the shared scoring method

**Consumers:** ds-research, ds-brief, ds-benchmark, ds-productize (pricing benchmarks), ds-debug and ds-build (`--research`), the shared `ds-research-agent`. ds-brief adds its own stricter HIGH gate and independence test in its verification reference; everything scored here is the floor.

## Source tiers

| Tier | Score | Type |
|------|-------|------|
| T1 | 95-100 | Official / authoritative — law text, gazette, RFC, standards body, vendor docs (MDN, platform docs) |
| T2 | 85-94 | Official repo or primary record — releases, CHANGELOG, registry, court ruling, regulator circular |
| T3 | 70-84 | Recognized experts — core contributors, named domain authorities, academic PDF |
| T4 | 55-69 | Community curated — high-vote Stack Overflow, established trade press |
| T5 | 40-54 | General community — blogs, Reddit, forums |
| T6 | 0-39 | Unverified — AI-generated, undated, anonymous, > 12 months on a volatile topic |

**Tier ≠ primary.** T1 measures how authoritative a document is; *primary* asks whether the authority that **issued this specific rule** published it on its own domain. A load-bearing datum (a threshold, a price, an obligation) needs a primary source, not merely a T1 one.

## Modifiers

| Condition | Effect |
|-----------|--------|
| Published within 3 months | +10 |
| Core maintainer / domain authority / named author | +10 |
| Cross-verified by an independent source (different organization, not a mirror) | +10 |
| Cited by ≥ 2 AI search engines independently | +15 (findability signal, not accuracy — triangulation still applies) |
| High engagement | +5 |
| Dated > 12 months on a volatile topic | −15 |
| Sponsored / paid content | −15 |
| Vendor self-promotion | −5 |
| Anonymous / no author attribution | −10 |
| AI-generated without human review | −20 (−5 when expert-verified and triangulated) |
| AI-hallucinated package, API, paper, or URL (confirmed non-existent) | discard |

## Dimensions

| Dimension | Weight | Scoring |
|-----------|--------|---------|
| Currency | 20% | < 3 mo: 100 · 3-12 mo: 70 · 1-2 y: 40 · > 2 y: 10. **Normative text scores on consolidation, not age** — the current consolidated version is 100 regardless of enactment year; an un-versioned reprint is 10 however recent |
| Relevance | 25% | Direct: 100 · Related: 70 · Tangential: 30 |
| Authority | 25% | T1: 100 · T2: 85 · T3: 70 · T4: 50 · T5: 30 |
| Accuracy | 20% | Cross-verified: 100 · Single: 60 · Unverified: 30 |
| Purpose | 10% | Educational: 100 · Informational: 80 · Commercial: 40 |

## Bands

| Band | Score | Use |
|------|-------|-----|
| [A] Primary | 85-100 | Core evidence |
| [B] Supporting | 70-84 | Corroborating |
| [C] Background | 50-69 | Context only |
| [WARN] | < 50 | Replace; keep only with a visible `[unverified]` caveat and no datum depending on it |

Irrelevant → discard. Duplicate or mirror → skip; it never counts toward independence. Outdated > 2 years on a volatile topic → flag and seek newer.

## Verification rules

1. **Triangulation** — no datum enters a synthesis unless confirmed by ≥ 2 independent sources; a single-source datum is kept only with a visible "single source" badge, never silently.
2. **Citation** — every claim cites ≥ 1 source whose URL resolves; a dead link is marked, not dropped.
3. **Recency** — statistics, prices, market or tech claims whose newest source is > 12 months old are flagged "potentially outdated".
4. **Diversity** — ≥ 2 source categories (official/institutional, academic, expert/practitioner, community); single-category → confidence downgrade.
5. **Bias** — flag commercial interest in the conclusion; apply the vendor modifier.
6. **Dating** — every source record carries a publication date and an access date; undated → `pubDate: unknown`, stated visibly, never inferred.
7. **AI output is T6 until verified** — a generator never reviews its own output; a second model or a human verifies; every AI-cited package, API, paper, or URL is resolved before inclusion.

## Normative source ladder — legal, regulatory, standards topics

Tier measures reliability; binding force is a different axis. A regulator's FAQ is T1 and binds nobody; a statute binds absolutely.

| Rank | Instrument | Highest obligation badge it justifies |
|------|-----------|----------------------------------------|
| N1 | Constitution / primary legislation | `must` / `must not` |
| N2 | Regulation, decree, statutory instrument under N1 | `must` / `must not` |
| N3 | Communiqué, by-law, binding regulator decision with sanction power | `must` / `must not` |
| N4 | Binding case law | `must` / `must not`, stated as settled interpretation |
| N5 | Non-precedential rulings, regulator guidance, FAQ, handbook | `should` at most |
| N6 | Recitals, preambles, explanatory memoranda — interpretive, not operative | `should` at most |
| N7 | Commentary, law-firm articles, trade press | context only; never the sole basis for an obligation |

A `must` cites N1-N4; supported only by N5-N7 → downgrade or find the operative provision. Recital ≠ article. Guidance restating law cites the underlying provision. Conflicting instruments → the higher rank wins and the conflict is shown. Year-indexed amounts (fines, thresholds) carry their index year and revaluation mechanism.

## Confidence

| Condition | Level |
|-----------|-------|
| ≥ 2 T1 agree, triangulated, no contradictions | HIGH |
| T1-T2 majority, minor contradictions resolved | MEDIUM |
| Mixed sources, unresolved conflicts, thin coverage | LOW |

Never report HIGH without cross-verification. **Contradiction resolution order:** security/legal authority override → T1 overrides all → newer wins within a tier → higher engagement → note unresolved. The disagreement is preserved and shown (both candidates, tier, URL), never silently dropped. For CVEs, secure coding, cryptography, and binding legal text, T1 authorities (OWASP, NIST, NVD, vendor advisories, the official gazette) always outrank T3+ regardless of score delta — a secondary source may explain; only the primary establishes.

## Quality gate — before any output

≥ 2 source categories · ≥ 1 band-A source · no unsupported claim · every datum ≥ 2-confirmed or flagged · every obligation badge backed by sufficient rank · every cited provision version-checked. Gate fails → report the honest band with explicit gaps rather than presenting thin evidence as reliable.

## Deep mode and dependency lookups

**Iterative deepening:** seed (5 parallel searches, 10-15 sources) → backward snowball (references of T1-T2 sources) → forward snowball (newer sources citing them) → keyword expansion. Stop at saturation: the last 3 sources repeat themes or overlap ≥ 80%.

**Registry endpoints** (version, deprecation, CVE): PyPI `pypi.org/pypi/{pkg}/json` · npm `registry.npmjs.org/{pkg}` · crates `crates.io/api/v1/crates/{pkg}` · Go `pkg.go.dev/{pkg}?tab=versions` · advisories `osv.dev`. Flow: latest → SemVer compare → changelog on major → CVE → deprecation. A package must exist in the registry with non-trivial age and download history and not be deprecated; a near-miss or cross-ecosystem name is a suspected typosquat until proven otherwise.

**Sources of this method:** CRAAP test (Blakeslee, Meriam Library, California State University, Chico — https://library.csuchico.edu/help/source-or-information-good); OWASP Secure Coding Practices (https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/); NIST SP 800-218 (https://csrc.nist.gov/Projects/ssdf).
