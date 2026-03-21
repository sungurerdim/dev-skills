# Marketing Strategy Guide

Solo-dev optimized, budget-conscious, privacy-respectful marketing playbook for indie app launches.

---

## 1. App Store Optimization (ASO)

### Title and Subtitle Optimization

| Element | iOS | Google Play |
|---------|-----|-------------|
| Title | 30 chars, front-load primary keyword | 30 chars, primary keyword + brand |
| Subtitle | 30 chars, secondary keywords | N/A (use short description) |
| Short description | N/A | 80 chars, action-oriented hook |
| Keyword field | 100 chars (hidden, comma-separated) | N/A (index from description) |

Rules: no keyword stuffing, use digits not spelled numbers, singular vs. plural tested individually, no prepositions wasting character budget. Placing a keyword in the title alone improves ranking for that term by roughly 10%.

### Keyword Research Process

1. Seed list: brainstorm 30+ terms from your value proposition and competitor names.
2. Expand: use AppTweak, Sensor Tower free tier, or Apple Search Ads keyword suggestions.
3. Score: rank by `(search volume x relevance) / competition`. Prioritize long-tail, intent-based queries.
4. Deploy: distribute across title, subtitle, keyword field (iOS) or title + description (Play).
5. Iterate: review rankings monthly, swap underperformers, test new terms quarterly.

### Screenshot Strategy

- First 3 screenshots decide the install. Lead with your core value proposition, not a splash screen.
- Build a narrative: problem, solution, delight.
- Add short text overlays with benefit-driven captions (these now contribute to keyword indexing).
- Platform-specific: do not reuse iOS screenshots on Play. Adjust order, framing, and captions per platform.
- Refresh screenshots with every major feature update or seasonal moment.
- The "ugly ad" trend: raw, authentic-looking screenshots outperform polished studio materials for many categories.

### A/B Testing

- Google Play: use Store Listing Experiments (built into Play Console) to test icons, screenshots, and descriptions.
- iOS: use Apple's Product Page Optimization (PPO) for up to 3 treatment variants.
- Even a 3-5% conversion lift compounds significantly over months of organic traffic.

### Localization

Go beyond translation. Adapt keywords, screenshot captions, and value propositions to regional search behavior. Prioritize markets where your category has low competition but growing smartphone adoption. Even localizing metadata for 5 languages can double your addressable market.

### Ratings and Reviews

- Prompt for rating after a positive in-app moment (completed task, achievement unlocked), not on first launch.
- Use the native `SKStoreReviewController` (iOS) or `ReviewManager` (Android) -- max 3 prompts per year on iOS.
- Respond to every 1-3 star review within 48 hours. A thoughtful response can prompt users to revise upward.
- Target: maintain 4.0+ stars. Apps below 4.0 see measurably lower conversion rates.

---

## 2. Launch Strategy

### Pre-Launch: 60-Day Timeline

| Day | Action |
|-----|--------|
| 60 | Finalize app name, ASO keyword research, create "Coming Soon" page on Product Hunt |
| 55 | Set up landing page with email capture, basic analytics (privacy-respecting: Plausible or Umami) |
| 50 | Begin posting build-in-public content on Twitter/X and relevant communities |
| 45 | Submit to BetaList, create TestFlight / open beta on Play |
| 40 | Collect beta feedback, iterate on onboarding flow |
| 35 | Prepare press kit (see Section 7), draft press release |
| 30 | Start Product Hunt community engagement (upvote, comment on other products) |
| 25 | Finalize screenshot set, app preview video (15-30 seconds) |
| 20 | Send early access to 10-20 journalists/bloggers with personalized pitch |
| 15 | Prepare launch day email blast, social media posts, coordinate with beta testers |
| 10 | Submit app for App Store review (allow buffer for rejection) |
| 5 | Final QA pass, confirm analytics tracking, prepare server scaling |
| 1 | Schedule Product Hunt launch for 12:01 AM PST, queue social posts |

### Launch Day Checklist

- [ ] Product Hunt listing live at 12:01 AM PST
- [ ] Send email blast to waitlist within first hour
- [ ] Post on Twitter/X, LinkedIn, relevant subreddits, Hacker News (Show HN)
- [ ] Respond to every Product Hunt comment within 30 minutes
- [ ] Monitor crash reports and server health. Stagger outreach in waves, not blasts
- [ ] Track installs, conversion rate, and traffic sources hourly

### Post-Launch: Week 1 and Month 1

- Days 1-2: respond to all comments, send thank-yous, hotfix critical bugs.
- Days 3-7: analyze traffic sources, double down on what worked, write launch retrospective.
- Week 2: implement top-requested feature. Week 3: submit to directories, pitch newsletters.
- Week 4: first ASO iteration based on real keyword data, plan content calendar.

---

## 3. Social Media

### Platform Selection Matrix

| App Type | Primary | Secondary | Skip |
|----------|---------|-----------|------|
| Productivity | Twitter/X, LinkedIn | Reddit, Mastodon | TikTok |
| Consumer/Fun | TikTok, Instagram | Twitter/X, YouTube Shorts | LinkedIn |
| Developer tool | Twitter/X, Reddit | Hacker News, Mastodon | Instagram |
| Health/Fitness | Instagram, TikTok | YouTube, Twitter/X | LinkedIn |
| B2B/Enterprise | LinkedIn, Twitter/X | YouTube | TikTok |

### 3-2-1 Content Framework (per week)

- **3 value posts**: tips, tutorials, insights related to your app's problem space.
- **2 engagement posts**: polls, questions, behind-the-scenes, build-in-public updates.
- **1 promotional post**: feature highlight, testimonial, or download CTA.

### Automation Stack (Solo-Dev Friendly)

| Tool | Purpose | Cost |
|------|---------|------|
| Buffer (free tier) | Schedule posts across platforms | $0 |
| Typefully | Twitter/X thread drafting and scheduling | Free tier available |
| Canva (free tier) | Quick social graphics and screenshot mockups | $0 |
| IFTTT or Zapier (free) | Cross-post triggers (e.g., blog post to Twitter) | $0 |

### Content Ideas

- Build-in-public milestones and metrics (transparent numbers build trust)
- "How I built X feature" breakdowns, before/after comparisons, user story spotlights
- Seasonal tie-ins, trending topic replies with genuine niche insight

---

## 4. Content Marketing

### Dev Blog Strategy

Publish 2-4 posts per month on your domain (/blog path for SEO value). Content pillars:
1. **Problem/Solution**: "How to [solve X problem] with [your approach]"
2. **Behind the scenes**: architecture decisions, indie dev lessons, revenue transparency
3. **Category education**: teach users about your app's space
4. **Comparison/Alternative**: "Best apps for X" (include yours honestly)

### SEO Fundamentals

- Target long-tail keywords with clear intent. One primary keyword per page (title, H1, first paragraph, meta).
- Internal linking between posts, external links to authoritative sources.
- Page speed: sub-2s load times, WebP images, lazy loading. Min 800 words; 1500+ for pillars.

### Answer Engine Optimization (AEO)

AI search (ChatGPT, Perplexity, Google AI Overviews) drives significant discovery. Zero-click searches reached 69% in 2025. Optimize to be cited:

- **Structure for extraction**: one idea per paragraph, clear H2/H3 hierarchy, self-contained sections.
- **Q&A and listicle formats**: listicles = 32% of all AI citations (SEOMator). Implement Schema.org (FAQ, HowTo).
- **Freshness + E-E-A-T**: update quarterly, include current year in titles, author bios with credentials.
- **Platform-specific**: Reddit dominates Perplexity citations (46.7% of top sources). Maintain genuine Reddit presence.

---

## 5. Ad Budget Planning

### Budget Ladder: $0 to $2,000/month

| Tier | Monthly Budget | Allocation |
|------|---------------|------------|
| Bootstrap | $0 | Organic only: ASO, content, social, directories |
| Seed | $100-300 | Apple Search Ads Advanced: exact-match branded + competitor keywords |
| Growth | $300-800 | Add Google App Campaigns ($200-400) + Apple Search Ads expansion |
| Scale | $800-2,000 | Add social ads (Reddit Ads or Twitter Ads) + retargeting |

### Apple Search Ads

- Average CPI: ~$1.80 globally, ~$4.06 in the US. Use **Advanced** (Basic requires $5K min).
- Start: daily cap $5-20, exact-match on brand name + top 5 competitor names. CR: ~66%.
- Cost-efficient categories: Utilities ($2.90), Productivity ($3.13). Expensive: Finance ($8.23).

### Google App Campaigns

- Lower CPI than Apple but less intent-driven. Start $10-15/day, install volume target.
- Let algorithm optimize 2 weeks before judging.

### Social Ads

- Reddit Ads: strong for dev tools and niche communities, CPC $0.50-2.00. Twitter/X: good for B2B.
- Rule: never spend on ads until your store page converts organically (ASO first, ads second).

---

## 6. Organic Growth

### Referral Programs

Design principles: two-sided rewards (both referrer and invitee get value), low friction (native share sheet, unique link), tiered rewards at 3/5/10 referrals, visible progress in-app, no dark patterns (never auto-send or access contacts without consent).

### Community Building Phases

| Phase | Timeline | Focus |
|-------|----------|-------|
| Seed | Pre-launch to 100 users | Direct conversations, beta group (Discord or TestFlight), personal onboarding |
| Nurture | 100-1,000 users | User-generated content, feature request voting, weekly updates |
| Scale | 1,000-10,000 users | Ambassadors/power users, self-service community, documentation |
| Sustain | 10,000+ users | Community moderators, user events, ecosystem (plugins, integrations) |

### Directory Submissions

Submit within the first month: Product Hunt, AlternativeTo, Slant, SaaSHub, IndieHackers, SetApp (Mac), awesome-ios/awesome-android GitHub lists, G2/Capterra (if B2B).

### Word-of-Mouth Acceleration

- Delight moments: unexpected micro-interactions that make users smile and share.
- Shareworthy outputs: branded, easy-to-share results. "Powered by [App]" watermark (removable on paid).
- In-app prompts after high-value actions: "Know someone who'd find this useful?"

---

## 7. Press Kit

### Contents Checklist

- [ ] App icon in multiple sizes (1024x1024, 512x512, 256x256) as PNG
- [ ] 5-8 high-resolution screenshots (both platforms)
- [ ] App preview video (30 seconds, no audio dependency)
- [ ] Developer headshot and bio (2-3 sentences)
- [ ] One-paragraph app description (50 words)
- [ ] One-page app description (200 words) with key features bulleted
- [ ] Company/developer fact sheet (founding date, team size, location, notable stats)
- [ ] Brand assets: logo, color codes, font names
- [ ] Press release (see template below)
- [ ] Contact email for press inquiries

### Hosting

Host at `yourapp.com/press` (public, no login). Single ZIP download of all assets, under 50MB total.

### Press Release Template

```
FOR IMMEDIATE RELEASE
[App Name] Launches to [Solve X Problem] for [Target Audience]

[City, Date] -- [Developer Name] today announced [App Name], a [category]
app that [one-sentence value proposition].

[2-3 sentences on the problem and differentiated solution.]

Key features: [Feature 1] / [Feature 2] / [Feature 3]

Available on [platforms] for [pricing]. Press assets: [yourapp.com/press]
Contact: [name], [email]
```

### Journalist Pitching Formula

1. **Subject line**: "[App Name]: [specific angle relevant to their beat]" (under 60 chars)
2. **Opening**: one sentence on why this is relevant to their audience.
3. **Pitch**: 2-3 sentences on what the app does and what makes it different.
4. **Proof**: one metric, testimonial, or notable fact.
5. **Ask**: "Would you be interested in [a review copy / a quick demo / covering this]?"
6. **Assets**: link to press kit, not attachments. Under 150 words total. Personalize every pitch.

---

## 8. Landing Page

### Conversion-Optimized Structure

1. **Hero**: headline + subheadline + primary CTA + app screenshot/mockup
2. **Social proof**: ratings badge, download count, press logos, or testimonial
3. **Features**: 3-4 key benefits with icons (benefits, not features)
4. **How it works**: 3-step visual flow
5. **Testimonials/Pricing/FAQ**: social proof, clear pricing, 4-6 objections answered
6. **Final CTA**: repeated download/signup button

### Headline Formulas

- **Direct**: "[Action verb] your [noun] with [App Name]"
- **Problem-agitate**: "Tired of [pain point]? [App Name] [solution]."
- **Outcome**: "[Desired outcome] without [common frustration]"

### CTA Patterns

- Primary: "Download Free" or "Start Free Trial" (action + value). Secondary: "See How It Works."
- One primary CTA color, above the fold, repeated after each section. Mobile: sticky bottom bar.

### Performance Requirements

| Metric | Target |
|--------|--------|
| First Contentful Paint | < 1.5s |
| Largest Contentful Paint | < 2.5s |
| Cumulative Layout Shift | < 0.1 |
| Total page weight | < 1MB |
| Mobile PageSpeed score | > 90 |

---

## 9. Email Campaign Strategy

### List Building

- Landing page: email capture with clear value exchange ("Get early access" or "Get launch pricing").
- In-app: optional email at onboarding (never required for core functionality).
- Privacy-respecting providers: Buttondown, Listmonk (self-hosted), or Mailchimp free tier.

### 14-Day Onboarding Sequence

| Day | Email | Purpose |
|-----|-------|---------|
| 0 | Welcome | Thank them, set expectations, one quick-start action |
| 1 | Quick win | Guide to completing their first meaningful task |
| 3 | Feature spotlight | Introduce the feature that drives retention |
| 5 | Social proof | Share a user story or testimonial |
| 7 | Tip/trick | Power-user technique they likely missed |
| 10 | Feedback ask | "How's it going?" with a 1-question survey |
| 14 | Upgrade nudge | Highlight premium value, offer limited-time discount |

Rules: plain text preferred, one-click unsubscribe, respect timezones, max one email per 2 days.

### Retention Emails

- **Re-engagement** (7 days inactive): "We miss you -- here's what's new"
- **Milestone celebration**: "[X] completed! Here's your next step"
- **Feature announcement**: major releases only, max 1/month. **Annual recap**: personalized usage stats.

### Churn Prevention

- Trigger on churn signals (3 days inactive after 14+ active days): "Is something not working? Reply and I'll personally help."
- Cancellation flow: ask reason (1-click multiple choice), offer pause instead of cancel, provide data export.

---

## 10. Competitor Positioning

### Analysis Process

1. **Identify**: find 5-10 competitors via App Store search, AlternativeTo, G2, and Google.
2. **Map features**: spreadsheet with feature rows, competitor columns, checkmarks.
3. **Mine reviews**: 1-2 star competitor reviews reveal unmet needs.
4. **Position**: map on price vs. feature-richness matrix. Monitor via Google Alerts quarterly.

### Differentiation Strategies for Solo Devs

| Strategy | When to Use | Example |
|----------|-------------|---------|
| Privacy-first | Competitors collect excessive data | "No account required, no tracking, your data stays on-device" |
| Simplicity | Competitors are bloated | "Does one thing, does it well" |
| Price | Competitors overcharge | "One-time purchase, no subscription" |
| Personal touch | Competitors are faceless corporations | "Built and supported by one developer who uses it daily" |
| Platform-native | Competitors use cross-platform frameworks | "Built with SwiftUI, feels like it belongs on your device" |
| Speed | Competitors are slow | "Launches in under 1 second, no loading screens" |

---

## 11. User Persona

### Lightweight BAG + JTBD Framework

**BAG** = Behaviors, Attitudes, Goals. **JTBD** = Jobs To Be Done.

Answers: Who uses this? What do they believe? What are they hiring your app to do?

### Template

```
PERSONA: [Name]
---
Behaviors:
- [How they currently solve the problem]
- [Tools and platforms they use daily]
- [Frequency of the need your app addresses]

Attitudes:
- [What they value: privacy, speed, simplicity, power?]
- [What frustrates them about current solutions]
- [Willingness to pay and price sensitivity]

Goals:
- [Primary outcome they want]
- [Secondary benefit they'd appreciate]

Job To Be Done:
"When I [situation], I want to [motivation], so I can [expected outcome]."

Context triggers:
- [When/where does the need arise?]
- [What prompts them to search for a solution?]
```

### Validation Methods

- 5-10 user interviews (video call or async survey) before building.
- Mine competitor reviews for real user language -- copy their words into your marketing.
- Post-launch: tag support tickets by persona. In-app survey: 3 questions max, after 7+ days.

---

## 12. Demand Management

### Waitlist Strategy with Viral Mechanics

- Landing page with email capture and live waitlist count: "Join [X] others waiting for [App Name]."
- Viral mechanic: "Share your unique link to move up. Each signup moves you up [X] spots."
- Referral dashboard: position, referral count, estimated access date.

### Rate Limiting UX

- Show clear explanation, estimated wait time, and email notification option. Never silently fail.
- Consider geographic or timezone-based rolling access to flatten load curves.

### Staged Rollout

| Stage | Audience | Duration | Goal |
|-------|----------|----------|------|
| Alpha | 10-50 hand-picked testers | 2-4 weeks | Core flow validation, crash-free |
| Beta | 50-500 waitlist users | 2-4 weeks | Onboarding optimization, retention signal |
| Soft launch | 500-5,000 (single market) | 2-4 weeks | Unit economics validation, server load |
| General availability | All markets | Ongoing | Growth and iteration |

---

## 13. Overflow Management

### CDN Configuration

- Serve static assets from CDN (Cloudflare free tier, BunnyCDN, or Vercel Edge).
- Cache headers: immutable assets 1yr TTL, HTML 5min TTL. Brotli compression, responsive `srcset` images.

### Scaling Tiers

| Load | Infra Response |
|------|---------------|
| Baseline (< 100 RPM) | Single server, SQLite or managed Postgres |
| Moderate (100-1,000 RPM) | Add CDN, connection pooling, read replicas |
| High (1,000-10,000 RPM) | Horizontal scaling, queue-based processing, rate limiting |
| Viral spike (10,000+ RPM) | Auto-scaling, circuit breakers, static fallback pages |

### Queue Management UX

- Show real-time position and estimated wait. Provide "notify me" option for long waits.
- Never show blank loading screens -- use skeleton UI or progress indicators.

### Load Testing

- Use k6 (open source) or Artillery to simulate 3x expected launch traffic across the full path (landing page, API, database, payment).
- Run at least 1 week before launch. Fix bottlenecks before they become outages.

---

## 14. Growth Metrics

### Core Metrics Dashboard

| Metric | Formula | Healthy Target |
|--------|---------|----------------|
| DAU/MAU ratio | Daily active / Monthly active | > 20% (good), > 50% (excellent) |
| Day 1 retention | Users returning day after install / installs | > 40% |
| Day 7 retention | Users returning 7 days after install / installs | > 20% |
| Day 30 retention | Users returning 30 days after install / installs | > 10% |

### Retention Curve Analysis

- Plot retention by weekly install cohort. Healthy apps flatten above 10-15% at day 30 (product-market fit signal).
- If the curve approaches zero, fix onboarding and core value delivery before spending on acquisition.

### Viral Coefficient (K)

`K = i x c` where i = avg invitations per user, c = invite conversion rate.

- K < 1: need paid acquisition (most apps). K = 1: self-sustaining. K > 1: viral (rare).
- Measure **viral cycle time**: 7-day cycles grow 4x faster than 30-day cycles.
- K stays below 0.3 after 4-6 weeks? Shift to performance ads if CAC < 40% of 12-month LTV.

### CAC and LTV Calculation

`CAC = Total marketing spend / New customers acquired`
`LTV = ARPU x Avg lifespan (months)` or `ARPU / Monthly churn rate`

| Ratio | Interpretation |
|-------|---------------|
| LTV:CAC > 3:1 | Healthy, room to invest |
| LTV:CAC 1:1-3:1 | Sustainable, optimize |
| LTV:CAC < 1:1 | Losing money, stop spending |

Freemium: calculate LTV on paying users, multiply by free-to-paid rate for blended LTV per install.

---

## 15. Sources

- [ASO Complete Guide 2025 - ASOMobile](https://asomobile.net/en/blog/aso-in-2025-the-complete-guide-to-app-optimization/)
- [ASO Strategy Framework 2026 - AppTweak](https://www.apptweak.com/en/aso-blog/aso-strategy)
- [ASO Strategies 2025 - Business of Apps](https://www.businessofapps.com/marketplace/app-store-optimization/research/app-store-optimization-strategies/)
- [Screenshots Guide 2025 - ASOMobile](https://asomobile.net/en/blog/screenshots-for-app-store-and-google-play-in-2025-a-complete-guide/)
- [Product Launch Checklist 2026 - OpenHunts](https://openhunts.com/blog/product-launch-checklist-2025)
- [Product Hunt Launch Guide 2026 - CalmOps](https://calmops.com/indie-hackers/product-hunt-launch-guide/)
- [Product Hunt Prep to Monetization 2026 - Innmind](https://blog.innmind.com/how-to-launch-on-product-hunt-in-2026/)
- [Apple Search Ads Costs 2026 - Business of Apps](https://www.businessofapps.com/marketplace/apple-search-ads/research/apple-search-ads-costs/)
- [Apple Ads Benchmarks 2025 - AppTweak](https://www.apptweak.com/en/aso-blog/apple-ads-benchmarks)
- [Apple Search Ads Benchmarks 2025 - Admiral Media](https://admiral.media/apple-search-ads-benchmarks/)
- [How to Lower CPI - App Masters](https://appmasters.com/blogs/lower-cost-per-install-apple-search-ads/)
- [K-Factor for Apps - Udonis](https://www.blog.udonis.co/mobile-marketing/mobile-games/k-factor)
- [Viral Coefficient Formula - Wall Street Prep](https://www.wallstreetprep.com/knowledge/viral-coefficient/)
- [AEO Guide 2025 - Profound](https://www.tryprofound.com/resources/articles/answer-engine-optimization-aeo-guide-for-marketers-2025)
- [AEO Comprehensive Guide 2026 - CXL](https://cxl.com/blog/answer-engine-optimization-aeo-the-comprehensive-guide/)
