# Launch Research — Strategy, Voice & Positioning

Repository-level reference. Captures the case studies and 2026 verification data that informed the dev-skills suite's voice, positioning, and structural choices. Treat this as the "why" behind decisions documented in `SKILL-SPEC.md`, the root `README.md`, and `ds-launch`.

When this file says a pattern was "applied", check the corresponding skill or doc to verify the live implementation — case studies become stale faster than the patterns they validate.

Last updated: 2026-03-23

**How this fits the suite:**
- `ds-launch` — operationalizes Part 3 ASO updates (screenshot caption indexing, CPP expansion, portrait video, intent-driven discovery).
- `README.md` (root) + per-skill READMEs — apply Part 4 voice rules (forbidden words, allowed power words) and structure (hook → one-liner → proof → quick start → philosophy → curated overview).
- `SKILL-SPEC.md` §2 (Skill Voice) — codifies Part 4 voice rules as a spec-level constraint every skill must satisfy.
- Each `ds-*/SKILL.md` opening line — pain-first hook per Part 1 anti-pattern #1 (every skill audited 2026-04-25).

---

## Part 1: Case Study — Zara Zhang & frontend-slides

### Profile (Verified March 2026)

| Data Point | Value | Source |
|-----------|-------|--------|
| GitHub stars | 10.9k (803 forks, 6 contributors) | [github.com/zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) |
| X/Twitter followers | ~51.2k (@zarazhangrui) | X profile |
| GitHub followers | 1.3k | GitHub profile |
| Location | San Jose, CA | GitHub profile |
| Current role | ByteDance — AI products | [zarazhang.com/about](https://zarazhang.com/about/) |
| Background | Harvard, Psychology; trilingual (CN/EN/JP) | Personal website |
| Growth trajectory | 1k → 7.8k → 10k → 10.9k (Jan–Mar 2026) | X milestone posts |

### Other Claude Code Skills

| Project | Stars | What It Does | Pattern |
|---------|-------|-------------|---------|
| youtube-to-ebook | 297 | YouTube transcripts → EPUB ebooks | code → single file output |
| follow-builders | 345 | AI digest: top builders on X + YouTube | code → curated content |
| codebase-to-course | 8 (new, Mar 23 2026) | Any codebase → interactive HTML educational course for "vibe coders" | code → single HTML output |

**Consistent pattern across all 4 skills:** Same niche (code → beautiful single-file output), different use cases (presentations, ebooks, digests, education). Each skill is opinionated, philosophy-first, zero dependencies.

**"Vibe coder" audience (new, codebase-to-course):** People who build with AI but don't understand the underlying code. Growing demographic. Zara's positioning: "Build first, understand later" — inverts traditional CS education. This audience is different from dev-skills' target (professional developers who want AI quality guardrails).

### Why frontend-slides Worked

1. **Opinionated product self-distributes.** People share because they agree with the philosophy ("bye PowerPoint"), not because they were marketed to.
2. **Pain point → emotional outcome.** "Non-designers trapped by design vocabulary" → "stunning presentations without design knowledge."
3. **Show, don't tell.** Demo video proving output quality replaced 1,000 words.
4. **Founder-product alignment.** She uses it herself, publicly. Authenticity = trust signal.
5. **Progressive disclosure architecture.** 1,625 lines → 183 lines (89% reduction) — same functionality, less context bloat. Shared the metric publicly → validated iteration.
6. **Zero-dependency philosophy.** Single HTML files with inline CSS/JS. No build step, no npm.

### Key Patterns (Observed)

| Pattern | Example | Why It Works |
|---------|---------|-------------|
| **Contrarian hook** | "The world hasn't woken up to the fact that code can create better slides than PPT" | Appeals to early adopters, creates belonging |
| **Pain before solution** | Describe what sucks → then present the fix | Reader nods first, then is receptive |
| **Philosophy > features** | "Bye-bye, purple gradients on white" | Can't be commoditized, invites agreement |
| **Curated options** | 12 named presets, not "infinite customization" | Reduces choice paralysis, signals taste |
| **Metric storytelling** | "1,625 lines → 183 lines, 89% reduction" | Quantification validates iteration |
| **Milestone transparency** | "1K stars" → "7.8K stars — here's what I changed" | Builds parasocial connection |
| **Actionable insights** | "Treat your instruction file like a table of contents" | Gives away value → builds goodwill |

### Anti-Patterns

| Anti-Pattern | Problem |
|-------------|---------|
| Feature-focused opening | "Our product has X, Y, Z" — nobody cares yet |
| Abstract principles first | "Maximum efficiency" — too vague to feel |
| Overwhelming options | 19 items in 7 tables — choice paralysis |
| Long install process | Clone + copy + remove = friction |
| Documentation in README | Reference docs list = noise for first-time visitors |
| Jargon-heavy description | "Orchestrated execution systems" — intimidating |

---

## Part 2: Expert & Data Verification (March 2026)

### Pattern 1: Contrarian Hook — CONFIRMED

**Linear:** Founder explicitly chose "one right way" positioning against Jira's infinite flexibility. Published "The Linear Method" as manifesto before heavy feature work. Result: unicorn status, 100 employees, driven by engineers who hated alternatives. ([aakashg.com](https://www.news.aakashg.com/p/how-linear-grows))

**Pieter Levels (@levelsio):** Uses PHP (not trendy) deliberately. Contrarian message: "framework developers rely too much on trendy, marketed tools." Built $3M/year ARR solo, validating "simplicity over hype." ([fast-saas.com](https://www.fast-saas.com/blog/pieter-levels-success-story/))

**Confidence:** MEDIUM-HIGH — Pattern observed in multiple successful products. No quantitative A/B data on contrarian vs non-contrarian hooks, but case evidence strong.

### Pattern 2: Pain Before Solution (PAS) — CONFIRMED with nuance

PAS (Problem-Agitate-Solve) remains "time-tested" framework. One case study: 37% conversion rate. 2026 consensus: "persuasion trumps traffic volume; reframe around specific user problems." ([saasfunnellab.com](https://www.saasfunnellab.com/essay/pas-copywriting-framework/), [Medium](https://medium.com/@dragualin/5-copywriting-trends-predictions-for-2026-must-know-41141d51b507))

**Nuance for dev tools:** FAB (Features-Advantages-Benefits) may outperform PAS for technical products where developers already know the pain and want proof of solution quality.

**Ideal approach:** **Hybrid PAS+FAB** — Open with pain (PAS), then prove solution with technical depth (FAB). Don't dwell on agitation for developer audience; they know the problem, they want the fix fast.

**Confidence:** MEDIUM — Framework validated broadly; dev-tool-specific quantitative data absent.

### Pattern 3: Philosophy > Features — STRONGLY CONFIRMED

**Linear:** Published methodology manifesto *before* feature marketing. Philosophy = competitive moat. ([aakashg.com](https://www.news.aakashg.com/p/how-linear-grows))

**Tailwind CSS:** Fastest-growing CSS framework. "Utility-first" is a philosophy, not a feature. Eliminated CSS naming debates team-wide. ([mux.com](https://www.mux.com/blog/tailwind-is-the-worst-form-of-css-except-for-all-the-others))

**Rails:** "Convention over Configuration" drove massive adoption vs competitors requiring decisions at every layer.

**Emerging tools (2026):** Temporal Cloud ("durable execution"), Pkl ("eliminating configuration errors"), Grafana Faro ("eliminating friction") — all lead with philosophy, not features. ([dev.to](https://dev.to/thebitforge/top-5-emerging-developer-tools-to-watch-in-2026-12pl))

**Why opinionated wins:** Reduces decision fatigue, forces team alignment by default, accelerates onboarding, fewer config decisions = faster shipping. Works when defaults match 70%+ of user needs.

**Confidence:** HIGH — Multiple independent case studies, industry consensus.

### Pattern 4: Build in Public — PARTIALLY CONFIRMED

**Open source participation ROI:** 2-5x across all engagement forms; code contributions yield 3.6x ROI. ([Linux Foundation](https://www.linuxfoundation.org/blog/the-state-of-open-source-software-in-2025))

**Pieter Levels:** Openly shares revenue numbers on social media; transparency *is* the positioning.

**Gap:** No 2025-2026 quantitative study comparing "build in public" vs stealth launch effectiveness. No saturation data found.

**Practical takeaway:** Build-in-public works when transparency is authentic and structured (milestone posts with metrics, not daily noise). It's a positioning choice, not a guaranteed growth hack.

**Confidence:** MEDIUM — ROI data for open source participation exists; "build in public" as specific tactic lacks dedicated research.

### Pattern 5: Show Don't Tell / Demo Video — STRONGLY CONFIRMED

**Conversion data (2025):**

| Format | Conversion Rate | Source |
|--------|----------------|--------|
| Static text description | ~1% baseline | — |
| Demo video | 3.21% avg | [RevenueHero](https://www.revenuehero.io/blog/the-state-of-demo-conversion-rates-in-2025/) |
| Interactive demo | 23% (7.2x vs video) | RevenueHero |
| Interactive (user-controlled) | 38% (+111% vs generic screenshare) | RevenueHero |

**Engagement multipliers:**
- Video: +80% engagement vs text
- Buyers: 2.3x more likely to purchase after watching demo
- Captions: +41% watch time, +89% social shares
- Speed-ramped demos: 63% higher retention

**Product Hunt:** "Create self-explanatory gallery images — developers scan images before reading copy." ([hackmamba.io](https://hackmamba.io/developer-marketing/how-to-launch-on-product-hunt/))

**Confidence:** HIGH — Hard data from 1M+ form submissions, multiple independent sources.

### Pattern 6: README as Landing Page — CONFIRMED (qualitative)

**Impact:** Repos with comprehensive READMEs receive 4x more stars, 6x more contributors. ([rivereditor.com](https://rivereditor.com/blogs/write-perfect-readme-github-repo))

**Effective README structure:**
- One-line hook: ≤10 words
- Visual proof: screenshots increase stars ~42%; GIFs demonstrate workflow
- 3-5 problem/solution pairs before feature lists
- Quick Start: ≤5 commands, under 10 minutes
- 4-7 badges max (build, coverage, version, license); >7 = cluttered
- Ideal length: 1,500-2,000 words; longer → separate docs
- GitHub auto-generates TOC from headings; no manual TOC needed

**Gap:** No empirical conversion rate data connecting README quality directly to adoption metrics.

**Confidence:** MEDIUM — Best practices documented; impact metrics are aggregate, not controlled studies.

### Pattern 7: Milestone Transparency — PARTIALLY CONFIRMED

**GitHub stars as social proof:**
- High star count (36K+): immediate credibility with enterprise decision-makers
- GitHub discovery algorithm heavily weights stars in search → compounding visibility
- AFFiNE case study: 0→6K (7 days via HN+Reddit), 6K→15K (3 months, content+community), 15K→33K (12 months, word-of-mouth)

**Star yields per launch channel:**

| Channel | Expected Stars | Reach |
|---------|---------------|-------|
| Hacker News | 300-1,000 | Tech decision-makers |
| Reddit r/programming | 200-500 | Developers |
| Twitter/X | 100-300 | Network followers |
| Dev.to | 50-200 | Developer community |

**Caveat:** Artificial stars = zero impact on package downloads. Stars are social proof for humans, not a ranking signal.

**Confidence:** MEDIUM-HIGH — Real case data exists; limited formal causal studies.

---

## Part 3: Additional Verified Tactics (2026)

### Answer Engine Optimization (AEO) — NEW, CRITICAL

AI search referrals grew **357% YoY** (1.13B visits in June 2025). 65-69% of Google searches are zero-click; 25%+ show AI Overviews. By end 2026, Gartner predicts 25% of organic search traffic shifts to AI chatbots. ([CXL](https://cxl.com/blog/answer-engine-optimization-aeo-the-comprehensive-guide/), [Frase.io](https://www.frase.io/blog/what-is-answer-engine-optimization-the-complete-guide-to-getting-cited-by-ai))

**Developer AI search split:**
- ChatGPT: 55-60% dominant
- Perplexity: 18-22% (preferred for technical research, better citations)
- Google Gemini: 10-14%
- Microsoft Copilot: 6-9%

**Optimization tactics:**
1. Answer-first content: 40-60 word direct answers leading each section
2. Semantic structure: clear H2/H3 hierarchy, self-contained sections
3. Citation density: stats every 150-200 words with linked sources
4. Schema markup: Article + FAQPage microdata
5. Content freshness: AI engines favor 25.7% fresher sources than traditional search
6. Reddit presence: Perplexity draws 46.7% of top sources from Reddit

### ASO Algorithm Changes (2025-2026)

**Apple:**
- Screenshot captions now index in search (June 2025)
- Custom Product Pages: 35 → 70 per app, keyword-linkable for organic search
- Search result diversity: intent variety instead of clustering
- Additional ads in search results (March 2026 rollout: UK→Japan→Global Q2)

**Google Play:**
- Battery optimization as core vital (5% threshold; non-compliant apps excluded from discovery, March 2026)
- Engagement/retention signals outweigh raw downloads (2:1 redownload ratio)
- "Ask Play" Gemini AI chatbot for guided search (rolling out 2026)
- Portrait video: 7% higher watch time, 5% better conversion vs landscape

**Cross-platform shift:** Both stores moving from keyword-matching to semantic/intent-driven discovery.

([AppTweak](https://www.apptweak.com/en/aso-blog/app-store-optimization-news-app-store-updates), [Phiture](https://phiture.com/blog/aso-trends-in-2026/))

### Product Hunt (2026 Status)

Still effective: 2.7M monthly unique visitors. Top-4 ranking ≈ 1,500 daily visitors.

**Winning tactics:**
- External hunter partnership (2-3 weeks pre-launch)
- 12:01 AM PT launch; first 4 hours = algorithm positioning
- Visual-first gallery: 5-7 images (positioning→workflow→outcome)
- Pre-written everything: FAQs, maker comment (<800 chars), social posts
- Weekend launches better for dev tools
- Multi-launch strategy compounds: Supabase 16 times in 4 years, Cursor 5x in 2025

**Key insight:** Ranking ≠ revenue. Optimize for conversion rate, not ranking position.

([hackmamba.io](https://hackmamba.io/developer-marketing/how-to-launch-on-product-hunt/), [rocketdevs.com](https://rocketdevs.com/blog/how-to-launch-on-product-hunt))

### Content Marketing for Dev Tools (2026)

| Format | ROI | Best For |
|--------|-----|----------|
| Short-form video | Highest; 2.5x engagement vs long-form | Demos, tutorials, quick wins |
| Technical blog posts | 67% more leads; 434% more indexed pages | SEO, authority, depth |
| Code samples/templates | Direct activation | Integration guides, copy-paste |
| Infographics | High shareability; 51% good results | Architecture diagrams, comparisons |
| Documentation | Credibility signal; missing = deal-breaker | Official guides, troubleshooting |

**2026 shift:** Content clusters (topic ownership) > random blog posts. AI makes content cheaper → human-created content becomes more valuable (not less). 91% of content marketers use video; 78% increasing production.

### GitHub Stars Growth Playbook

Stars = credibility lever, not growth hack. 36K+ signals legitimacy to enterprise buyers.

**Channel ROI for launch:**

| Channel | Stars Yield | Peak Window |
|---------|-------------|-------------|
| Hacker News | 300-1,000 | 2-4 hours |
| Reddit r/programming | 200-500 | 24-48 hours |
| Product Hunt | 200-800 | 24 hours |
| Twitter/X | 100-300 | Sustained |
| Dev.to | 50-200 | 48+ hours |

**Growth phases (AFFiNE pattern):** Burst (HN+Reddit, 0→6K, 1 week) → Content (community+blog, 6K→15K, 3 months) → Organic (word-of-mouth, 15K→33K, 12 months).

---

## Part 4: Ideal Voice & Structure Framework

### The Ideal Voice (Synthesized)

Based on all research, the voice that converts for developer tools in 2026:

**Tone:** Confident + opinionated + technically precise. Not salesy, not humble, not academic.

**Characteristics:**

| Do | Don't |
|----|-------|
| State beliefs as beliefs ("We believe X") | Abstract principles ("Maximum efficiency") |
| Name the pain specifically ("ATS rejects 75% of Word CVs") | Generic pain ("Many people struggle with...") |
| Show proof with numbers ("1,625 → 183 lines, 89% reduction") | Claim without evidence ("Best in class") |
| Be contrarian when authentic ("20 deep skills > 1,000 shallow playbooks") | Be contrarian for shock value |
| Use developer language, not marketing language | "Leverage", "empower", "unlock", "seamlessly" |
| Curate (12 presets, not infinite customization) | Overwhelm with options |
| Lead with "why", follow with "what", end with "how" | Lead with feature list |
| Short sentences. Active voice. Imperative mood. | Passive constructions, hedging language |

**Forbidden words/phrases:** leverage, empower, unlock, seamlessly, cutting-edge, next-generation, world-class, robust (unless describing actual robustness testing), comprehensive (unless quantified), innovative.

**Allowed power words:** prevents, eliminates, enforces, catches, verifies, reduces, automates, replaces, ships.

### The Ideal Structure (README / Landing / Store Listing)

```
Line 1:      HOOK — Pain point or contrarian statement (≤10 words)
Line 2-3:    ONE-LINER — What it does in plain language
Line 4-6:    PROOF — Demo GIF/video or metric ("X → Y, Z% improvement")
Line 7-10:   QUICK START — ≤5 commands, under 10 minutes
Line 11-20:  PHILOSOPHY — 3-5 sharp beliefs (not abstract principles)
Line 21-30:  CURATED OVERVIEW — One table or pipeline, not 7 category tables
Below fold:  Technical details, full docs, contributing, license
```

**Comparison with Zara's original formula:**

| Zara's Formula | Ideal (Updated) | Change |
|----------------|-----------------|--------|
| Hook → One-liner → Quick start → Philosophy → Overview | Hook → One-liner → **Proof** → Quick start → Philosophy → Overview | Added PROOF before quick start (demo video +80% engagement, interactive +7.2x conversion) |
| Philosophy as "worldview" | Philosophy as **sharp beliefs with metrics** | Research confirms: quantified beliefs > abstract worldview |
| Compact overview | **Curated overview with pipeline visualization** | Reduces choice paralysis (Zara's 12 presets principle applied to skill listing) |

### The Ideal Copy Framework

**Level 1: Hook (Contrarian or Pain-First)**
- Contrarian: "[Status quo] is broken. Here's what actually works."
- Pain-first: "You've tried [common approach]. It [specific failure]. [Product] [specific fix]."
- Metric: "[Before number] → [After number]. [Implication]."

**Level 2: Philosophy Statement**
- Template: "We believe [sharp belief]. That's why [product] [specific design decision]."
- Example: "We believe every dependency is a future breaking change. That's why dev-skills has zero runtime dependencies."
- Rules: 3-5 beliefs max. Each must be falsifiable. Each must imply a design decision.

**Level 3: Proof**
- Demo video (30-60s, silent, sped-up processing)
- Before/after comparison
- Specific metric with calculation proof
- User testimonial (when available)

**Level 4: Call to Action**
- Single primary CTA above the fold
- Repeated after each major section
- Action + value: "Install in 2 commands" not "Get started"

### The Ideal Skill Description Format

**Current pattern (all skills):**
```
# /ds-{name}

**{Category}** — {Feature description}.
```

**Ideal pattern:**
```
# /ds-{name}

{Pain point or contrarian statement in one sentence.}

**{Category}** — {What it does, framed as outcome, not feature}.
```

**Examples:**

| Skill | Current Opening | Ideal Opening |
|-------|----------------|---------------|
| ds-launch | "Store & Release Management — Store submission, listing optimization..." | "75% of app store rejections are preventable. This skill catches them before you submit." |

---

## Part 5: Gap Analysis — Ideal vs Current Skills

### ds-launch/SKILL.md

| Gap | Severity | Detail |
|-----|----------|--------|
| Store description voice | MEDIUM | Listing scope covers limits/formatting but not pain-first or philosophy-driven copy |
| Screenshot narrative missing | MEDIUM | "problem → solution → delight" narrative not in screenshot scope |
| ASO algorithm updates | MEDIUM | Screenshot text indexing (June 2025), CPP expansion, intent-driven search not reflected |
| Portrait video optimization | LOW | Google Play: 7% higher watch time for portrait; not mentioned |
| Multi-launch PH strategy | LOW | Not in scope but relevant for post-launch growth |

### docs/business/marketing-strategy-guide.md

| Gap | Severity | Detail |
|-----|----------|--------|
| Neutral/academic tone throughout | MEDIUM | Comprehensive content but reads as textbook, not as opinionated guide |
| Missing contrarian hook formula | MEDIUM | Headline formulas are standard; no contrarian/philosophy patterns |
| AEO section could expand | LOW | Already has AEO; could add AI search split data and freshness signals |
| ASO section needs 2025-2026 algorithm updates | LOW | Screenshot indexing, CPP, intent-driven search |

---

## Part 6: Sources

### Zara Zhang / frontend-slides
- [GitHub - zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) — 10.9k stars verified
- [GitHub - zarazhangrui profile](https://github.com/zarazhangrui) — 7 repos, 1.3k followers
- [zarazhang.com/about](https://zarazhang.com/about/) — ByteDance, Harvard, Psychology
- [X - 10k stars milestone](https://x.com/zarazhangrui/status/2034331675363279338)
- [X - 7.8k stars + progressive disclosure](https://x.com/zarazhangrui/status/2029092514435932647)
- [X - 1k stars milestone](https://x.com/zarazhangrui/status/2025798415154921961)
- [GitHub - youtube-to-ebook](https://github.com/zarazhangrui/youtube-to-ebook) — 297 stars
- [GitHub - follow-builders](https://github.com/zarazhangrui/follow-builders) — 345 stars
- [GitHub - codebase-to-course](https://github.com/zarazhangrui/codebase-to-course) — new (Mar 23 2026)
- [X thread - codebase-to-course announcement](https://x.com/zarazhangrui/status/2035962536474837019)

### Expert Opinions & Case Studies
- [Linear Growth Strategy — Aakash Gupta](https://www.news.aakashg.com/p/how-linear-grows)
- [Pieter Levels Success Story — FastSaaS](https://www.fast-saas.com/blog/pieter-levels-success-story/)
- [Simon Willison LLM Predictions 2026](https://simonwillison.net/2026/Jan/8/llm-predictions-for-2026/)
- [Tailwind Philosophy — Mux](https://www.mux.com/blog/tailwind-is-the-worst-form-of-css-except-for-all-the-others)
- [Emerging Dev Tools 2026 — DEV Community](https://dev.to/thebitforge/top-5-emerging-developer-tools-to-watch-in-2026-12pl)

### Copywriting & Marketing Frameworks
- [PAS Framework 2025 — SaaS Funnel Lab](https://www.saasfunnellab.com/essay/pas-copywriting-framework/)
- [Copywriting Trends 2026 — Medium](https://medium.com/@dragualin/5-copywriting-trends-predictions-for-2026-must-know-41141d51b507)
- [Content Marketing 2026 — Idealogic](https://idealogic.dev/blog/future-content-marketing-2026-guide)
- [Content Marketing Trends 2026 — WordStream](https://www.wordstream.com/blog/2026-content-marketing-trends)
- [Content Marketing — Backlinko](https://backlinko.com/content-marketing-this-year)

### Demo & Conversion Data
- [Demo Conversion Rates 2025 — RevenueHero](https://www.revenuehero.io/blog/the-state-of-demo-conversion-rates-in-2025/) — 1M+ forms dataset
- [Product Hunt Developer Launch — HackMamba](https://hackmamba.io/developer-marketing/how-to-launch-on-product-hunt/)
- [Product Hunt Strategy — RocketDevs](https://rocketdevs.com/blog/how-to-launch-on-product-hunt)
- [Product Hunt Guide 2026 — CalmOps](https://calmops.com/indie-hackers/product-hunt-launch-guide/)

### ASO & App Store
- [ASO News & Updates 2026 — AppTweak](https://www.apptweak.com/en/aso-blog/app-store-optimization-news-app-store-updates)
- [ASO Trends 2026 — Phiture](https://phiture.com/blog/aso-trends-in-2026/)
- [ASO Trends to Watch 2026 — AppTweak](https://www.apptweak.com/en/aso-blog/aso-trends-to-watch-in-2026)

### AEO & AI Search
- [AEO Comprehensive Guide 2026 — CXL](https://cxl.com/blog/answer-engine-optimization-aeo-the-comprehensive-guide/)
- [AEO Getting Cited by AI — Frase.io](https://www.frase.io/blog/what-is-answer-engine-optimization-the-complete-guide-to-getting-cited-by-ai)
- [AEO Guide 2026 — LLMrefs](https://llmrefs.com/answer-engine-optimization)
- [Perplexity Statistics — Index.dev](https://www.index.dev/blog/perplexity-statistics)
- [AI Traffic Share Report 2026 — upGrowth](https://upgrowth.in/ai-traffic-share-report-2026/)

### GitHub & Open Source
- [GitHub Stars Guide 2026 — ToolJet](https://blog.tooljet.com/github-stars-guide/)
- [Star Growth 10K in 18 Months — DEV](https://dev.to/iris1031/github-star-growth-10k-stars-in-18-months-real-data-4d04)
- [Open Source Launch Playbook — DEV](https://dev.to/iris1031/github-star-growth-a-battle-tested-open-source-launch-playbook-35a0)
- [State of Open Source 2025 — Linux Foundation](https://www.linuxfoundation.org/blog/the-state-of-open-source-software-in-2025)
- [README Best Practices — Hatica](https://www.hatica.io/blog/best-practices-for-github-readme/)
- [README Template — River Editor](https://rivereditor.com/blogs/write-perfect-readme-github-repo)
