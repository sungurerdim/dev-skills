# /ds-market

**Marketing & Growth** — Strategy, copy generation, and growth tactics.

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

Without flags: present interactive menu to the user.

**Interactive menu (no flags):**
```
What marketing area do you need help with?
- [Strategy] — full marketing plan with positioning and channels
- [Copy] — generate marketing text (taglines, social posts, landing page)
- [Growth] — growth tactics (referral, organic, community)
- [Full Plan] — strategy + copy + growth sequentially
```

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
| Taglines | 3-5 options with different angles (benefit, problem, emotion) |
| App description | Short (80 chars) + long (4000 chars) store descriptions |
| Social posts | Platform-specific posts (X/Twitter, LinkedIn, Reddit, Product Hunt) |
| Landing page | Hero section, features, social proof, CTA |
| Email sequences | Welcome, onboarding, retention, win-back |
| Press kit | Product description, founder bio, screenshots, media contact |

### Growth Scope

| Tactic | What It Covers |
|--------|---------------|
| Organic | SEO, content marketing, dev blog, building in public |
| AEO | Answer Engine Optimization: Schema.org markup, Q&A formats, AI citation optimization |
| Referral | Referral program design, bilateral incentive, reward < 50% CAC |
| Community | Reddit, Discord, Twitter, developer communities |
| Content | 3-2-1 framework: 3 value, 2 engagement, 1 promo per week |
| Directories | Product Hunt, AlternativeTo, SaaSHub, BetaList submission list |
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
1. Generate positioning statement: "For {audience} who {need}, {APP_NAME} is {category} that {key benefit}. Unlike {alternative}, {APP_NAME} {differentiator}."
2. Generate user persona (1-2 personas)
3. Generate channel strategy with priorities (high/medium/low effort vs impact)
4. Generate timeline: pre-launch (4 weeks) → launch day → week 1 → month 1
5. Generate budget breakdown: $0/mo (organic), $50/mo (starter paid), $200/mo (growth)

**Copy mode:**
1. Generate 5 tagline options
2. Generate store descriptions (short + long)
3. Generate 5 social media posts per platform
4. Generate landing page copy structure
5. Generate press kit content

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
| Open source project | Focus on GitHub stars, dev community, documentation marketing |
| Pre-revenue / free app | Focus on user acquisition, community, future monetization prep |
| Niche market (<10K TAM) | Focus on community depth over broad reach |
| Regulated industry (health, finance) | Flag marketing compliance requirements |
