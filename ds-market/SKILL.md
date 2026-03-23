# /ds-market

Solo developers build great products but can't get anyone to notice. This skill generates the positioning, copy, and growth playbook to change that.

**Marketing & Growth** — Positioning, copy generation, and growth tactics for indie and solo-dev products.

## Triggers

- User runs `/ds-market`
- User asks about marketing strategy, growth tactics, or user acquisition
- User asks "how do I market my app" or "write marketing copy"
- User asks about launch strategy, social media, or landing page

## Contract

- Strategic guidance skill — produces plans, copy, and checklists, not code
- Fully standalone — no dependency on other skills
- **Minimal liability:** recommends established marketing patterns, no dark patterns
- **Maximum privacy:** no invasive tracking recommendations, no manipulative UX
- **Maximum efficiency:** automation-first tactics, time-efficient for solo devs
- **Minimum dependencies:** free and low-cost strategies first, paid as scale option

## Arguments

| Flag | Effect |
|------|--------|
| `--strategy` | Full marketing plan: positioning, channels, timeline |
| `--copy` | Generate marketing text: taglines, descriptions, social posts |
| `--growth` | Growth tactics: referral, organic, community, content |
| `--auto` | Run strategy + copy + growth sequentially |

Without flags: present interactive mode selection.

## Scopes

### Strategy Scope

| Area | What It Covers |
|------|---------------|
| Positioning | Competitor analysis, differentiators, unique value proposition |
| User persona | BAG+JTBD framework: Behaviors, Attitudes, Goals, Jobs To Be Done, context triggers |
| Channel selection | Which channels for your audience (organic, paid, community) |
| Timeline | Pre-launch (8 weeks), launch day, post-launch (week 1, month 1, month 3) |
| Budget | Budget ladder: $0 (organic) → $100-300 (Apple Search Ads) → $300-800 (+ Google App Campaigns) → $800-2,000 (+ social, retargeting) |

### Copy Scope

| Type | What It Generates |
|------|------------------|
| Taglines | 5 options across 3 proven formulas (see Copy Formulas below) |
| App description | Short (80 chars) + long (4000 chars) store descriptions — pain-first opening sentence |
| Social posts | Platform-specific posts (X/Twitter, LinkedIn, Reddit, Product Hunt) |
| Landing page | Hero + proof (demo/metric) + philosophy (beliefs) + features + social proof + CTA |
| Email sequences | Welcome, onboarding, retention, win-back |
| Press kit | Product description, founder bio, screenshots, media contact |

#### Copy Formulas

Every tagline, description, and social post must use one of these proven formulas:

**Formula 1 — Contrarian Hook** (highest virality for dev tools):
`"[Status quo] is broken/dead. [Product] is what actually works."`
Example: "Most AI coding skills are 50-line rule snippets. Here's what happens when you treat them as real software."

**Formula 2 — Pain-First (PAS)** (highest conversion for landing pages):
`"You've tried [common approach]. It [specific failure]. [Product] [specific fix]."`
Example: "You've tried Word for your CV. ATS rejects it. ds-cv generates one that passes every tracking system."

**Formula 3 — Philosophy Statement** (strongest long-term positioning):
`"We believe [sharp belief]. That's why [product] [specific design decision]."`
Example: "We believe every dependency is a future breaking change. That's why dev-skills has zero runtime dependencies."

**Formula 4 — Metric Proof** (highest credibility):
`"[Before number] → [After number]. [Implication]."`
Example: "1,625 lines → 183 lines. Same functionality, 89% less context bloat."

Rules: Every tagline set must include at least 1 contrarian and 1 metric-proof option. Store descriptions must open with pain or outcome, never with feature list.

#### Voice Rules

**Allowed power words:** prevents, eliminates, enforces, catches, verifies, reduces, automates, replaces, ships.

**Forbidden words:** leverage, empower, unlock, seamlessly, cutting-edge, next-generation, world-class, robust (unless about actual robustness testing), comprehensive (unless quantified), innovative, holistic, synergy.

**Tone:** Confident, opinionated, technically precise. Not salesy, not humble, not academic. Short sentences. Active voice. Imperative mood. Developer language, not marketing language.

Full copy formulas, voice rules, anti-patterns, landing page structure, growth playbook, and AEO tactics in [references/copy-and-growth-playbook.md](references/copy-and-growth-playbook.md).

### Growth Scope

| Tactic | What It Covers |
|--------|---------------|
| Organic | SEO, content marketing, dev blog |
| Build-in-public | Milestone posts with metrics, iteration transparency, revenue/star sharing. Structured updates (weekly/milestone), not daily noise. Pieter Levels pattern: transparency *as* positioning |
| AEO | Answer Engine Optimization (AI search grew 357% YoY, 2025). ChatGPT ~55-60%, Perplexity ~18-22%, Gemini ~10-14% of AI search. Tactics: answer-first content (40-60 word direct answers per section), Schema.org (FAQ, HowTo, Article), citation density (stats every 150-200 words with linked sources), content freshness (AI engines favor 25.7% fresher sources), Q&A formats (listicles = 32% of all AI citations). Reddit presence critical (46.7% of Perplexity top sources) |
| Referral | Referral program design, bilateral incentive, reward < 50% CAC |
| Community | Reddit, Discord, Twitter, developer communities |
| Content | 3-2-1 framework: 3 value, 2 engagement, 1 promo per week. Format ROI ranking: short-form video (highest, 2.5x engagement) > technical blogs (67% more leads) > code samples (direct activation) > infographics (high shareability) > documentation (credibility signal) |
| Product Hunt | Multi-launch strategy compounds visibility (Supabase: 16 launches in 4 years, Cursor: 5x in 2025). Tactics: external hunter partnership (2-3 weeks pre-launch), 12:01 AM PT timing (first 4 hours = algorithm positioning), visual-first gallery (5-7 images: positioning→workflow→outcome), pre-written maker comment (<800 chars, personal + actionable), weekend launches better for dev tools. PH = 2.7M monthly visitors; optimize for conversion rate, not ranking |
| Directories | AlternativeTo, SaaSHub, BetaList, awesome-* GitHub lists, SetApp (Mac), G2/Capterra (B2B) |
| Email | 14-day onboarding sequence, retention emails, churn prevention triggers |
| Partnerships | Cross-promotion, integration partnerships |
| Metrics | DAU/MAU, Day 1/7/30 retention targets, viral coefficient (K), CAC/LTV ratio |

## Execution Flow

Setup → Research → Generate → Review → Summary

### Phase 1: Setup

**Goal:** Understand the product and market.

1. If flags provided, proceed directly
2. If no flags, present interactive menu
3. Gather context:
   - What does the app do? (read README, project description)
   - What platform? (mobile, web, desktop)
   - What stage? (pre-launch, just launched, growing)
   - Who is the target user?
   - What is the monetization model?
4. If context is insufficient, ask user for: one-line description, target audience, top 3 competitors

**Gate:** Product context sufficient to generate relevant strategy.

### Phase 2: Research [--strategy]

**Goal:** Analyze market and competition.

1. Identify 3-5 direct competitors from user input or web search
2. Analyze competitor positioning: taglines, feature emphasis, pricing
3. Identify differentiation opportunities

**Gate:** Competitive landscape understood.

### Phase 3: Generate

**Goal:** Produce marketing artifacts.

**Strategy mode:**
1. Generate positioning statement using the best-fit template:
   - **Standard:** "For {audience} who {need}, {APP_NAME} is {category} that {key benefit}. Unlike {alternative}, {APP_NAME} {differentiator}."
   - **Contrarian:** "{APP_NAME} exists because {status quo} is broken. {One sentence on what it does differently}."
   - **Philosophy-first:** "We believe {sharp belief}. {APP_NAME} is built around that — {how belief shapes the product}."
   Pick the template that matches the product's strongest angle: standard for B2B/enterprise, contrarian for developer tools, philosophy-first for opinionated products.
2. Generate user persona (1-2 personas)
3. Generate channel strategy with priorities (high/medium/low effort vs impact)
4. Generate timeline: pre-launch (4 weeks) → launch day → week 1 → month 1
5. Generate budget breakdown: $0/mo (organic), $50/mo (starter paid), $200/mo (growth)

**Copy mode:**
1. Generate 5 tagline options using formulas from [references/copy-and-growth-playbook.md](references/copy-and-growth-playbook.md) (min 1 contrarian hook + 1 metric proof)
2. Generate store descriptions (short + long) — first sentence must be pain-first or outcome-first, never feature-first
3. Generate 5 social media posts per platform
4. Generate landing page copy: hero + proof layer (demo video/GIF/metric) + philosophy (3-5 sharp beliefs) + features + social proof + CTA
5. Generate press kit content
6. Apply Voice Rules to all generated copy (forbidden words check, tone verification)

**Growth mode:**
1. Generate top 10 growth tactics ranked by effort/impact for solo dev
2. Generate content calendar (4 weeks)
3. Generate referral program design
4. Generate community engagement plan

**Gate:** All requested artifacts generated.

### Phase 4: Review

**Goal:** Quality check generated content.

1. Verify copy is accurate (no false claims about features)
2. Verify no dark patterns (manipulative urgency, hidden costs, confusing opt-outs)
3. Verify accessibility (alt text suggestions for images, readable contrast)
4. Verify all store listing content meets platform character limits

**Gate:** All content passes review.

### Phase 5: Summary

```
ds-market: OK | Mode: {strategy|copy|growth} | Generated: N artifacts

Artifacts:
- {artifact 1}: {brief description}
- {artifact 2}: {brief description}

Next steps:
1. {most important action}
2. {second action}
3. {third action}
```

## Quality Gates

- No false claims about features the app doesn't have
- No dark patterns: no fake urgency, hidden costs, or manipulative copy
- All store listing text within platform character limits
- Budget recommendations start from $0 (free tactics first)
- Growth tactics are ethical and privacy-respecting
- All generated copy passes Voice Rules: zero forbidden words, pain-first or contrarian opening, no feature-first descriptions
- Every tagline set includes at least 1 contrarian hook and 1 metric-proof option
- Store descriptions open with pain/outcome, never feature list
- Landing page structure includes proof layer (demo/metric) and philosophy section (beliefs)

## Error Recovery

| Situation | Action |
|-----------|--------|
| No product context | Ask user for one-line description and target audience |
| Unknown competitor landscape | Generate generic positioning, recommend user research |
| Platform not specified | Generate multi-platform strategy, flag platform-specific items |
| Copy tone unclear | Ask: professional / casual / technical / friendly |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| B2B product | Adjust channels (LinkedIn > Instagram), enterprise positioning |
| Open source project | README as landing page (4x stars for comprehensive README), contrarian hook positioning, build-in-public milestones, multi-channel launch (HN 300-1K stars, Reddit 200-500, PH 200-800), AEO for AI search citation |
| Pre-revenue / free app | Focus on user acquisition, community, future monetization prep |
| Niche market (<10K TAM) | Focus on community depth over broad reach |
| Regulated industry (health, finance) | Flag marketing compliance requirements |
