# Monetization Patterns

Solo-dev-optimized guide to app and SaaS monetization. Platform-agnostic unless noted.
Benchmarks sourced from RevenueCat SOSA 2026, Recurly 2025, and industry reports.

---

## Monetization Model Comparison

| Model | Conversion Rate | Revenue Predictability | Best For |
|---|---|---|---|
| **Freemium** | 2.1% median (top 10%: 8.2%) | Medium | Large user base, network effects |
| **Hard Paywall** | 10.7% median (top 10%: 38.7%) | High | Utility apps, productivity tools |
| **Subscription** | 3-8% trial-to-paid | High | Content, SaaS, ongoing-value apps |
| **One-Time Purchase** | 1-5% of visitors | Low (no recurring) | Simple tools, games, niche utilities |
| **Ads (CPM/CPC)** | N/A | Low-Medium | High-DAU, casual/free apps |
| **Hybrid** | Varies | Medium-High | AI apps, variable-cost products |

**Key insight (2026):** Hard paywall apps generate 8-9x higher revenue per install than freemium apps. D14 median RPI: $2.32 (hard paywall) vs $0.27 (freemium). Retention at 12 months is nearly identical between models, meaning freemium does not retain better -- it just converts worse.

**Hybrid is growing:** 35% of subscription apps now mix subscriptions with consumables or lifetime purchases. Gaming (61.7%) and social/lifestyle (39.4%) lead adoption. AI apps drive this trend due to variable per-unit costs that pure subscriptions cannot absorb.

---

## In-App Purchase Implementation

### Purchase Types

| Type | Description | Restore on New Device | Example |
|---|---|---|---|
| **Consumable** | Used once, can repurchase | No | AI credits, virtual currency |
| **Non-Consumable** | Permanent unlock | Yes | Premium filters, level packs |
| **Auto-Renewable Sub** | Recurring billing | Yes | Pro tier, content access |
| **Non-Renewing Sub** | Fixed period, no auto-renew | Yes | Season pass, annual report |

### StoreKit 2 (iOS 15+)

StoreKit 2 replaces the legacy receipt-based system with modern Swift concurrency APIs.

- **Fetch products:** `Product.products(for: productIDs)` -- async/await, off-main-thread
- **Purchase:** `product.purchase()` returns a `Transaction` with JWS-signed verification
- **Entitlement check:** `Transaction.currentEntitlements` replaces manual receipt parsing
- **SwiftUI views:** `StoreView`, `ProductView`, `SubscriptionStoreView` -- one-line merchandising
- **iOS 18.4+ additions:** `AppTransaction.appTransactionID` (unique per Apple Account, back-deployed to iOS 15), `SubscriptionOfferView` for promotional merchandising

### Google Play Billing Library 7 (Android)

**Deadline:** All new apps and updates must use Billing Library v7+ by August 31, 2025.

- **Installment subscriptions:** Available in Brazil, France, Italy, Spain
- **`ReplacementMode` API:** Replaces deprecated `ProrationMode` for subscription upgrades/downgrades
- **Pending transactions for subscriptions:** Handle delayed payment confirmation
- **User Choice Billing:** `enableUserChoiceBilling()` for alternative payment options

### Cross-Platform Tip

IAPs generated $150B+ in 2025. Subscriptions account for 60% of IAP revenue. Always sandbox-test both platforms -- 70% of launch issues stem from untested edge cases.

---

## Subscription Design

### Tier Structure

| Tier | Purpose | Typical Pricing |
|---|---|---|
| **Free** | Acquisition funnel, product demo | $0 |
| **Standard / Pro** | Core value, target tier | $4.99-14.99/mo |
| **Premium / Teams** | Power users, higher limits | $19.99-49.99/mo |

The **decoy tier** (see Pricing Psychology) should make your target tier look like the best value. Two tiers is fine for solo dev; three is optimal for decoy effect.

### Trial Periods

| Trial Length | Median Trial-to-Paid | Notes |
|---|---|---|
| 3 days | 55-65% | High urgency, high conversion, low engagement |
| 7 days | 45-55% | Most common balance point |
| 14 days | 35-45% | Better for complex products |
| 30 days | 25-35% | Highest engagement, lowest conversion |

**Opt-in vs opt-out trials:**
- **Opt-out** (card upfront): 2-3x higher conversion than opt-in, but higher refund/dispute rates
- **Opt-in** (no card): Lower conversion but higher-quality subscribers and lower churn
- 52% of all trials in 2024 were 5-9 days (up from 48.5% in 2023)

**Emerging trend (2026):** Money-back guarantees replacing free trials. User pays upfront, refund within N days if unsatisfied. Filters out low-intent users.

### Annual vs Monthly

- **Annual discount:** Typically 30-40% off monthly equivalent (e.g., $9.99/mo or $59.99/yr)
- Annual subscribers have higher LTV but 30% cancel in the first month -- onboarding is critical
- Higher-priced apps: median $62.19 LTV/year vs $10.69 for low-priced. But lower-priced retain better (36% vs 23% at 12 months)
- Top-quartile apps are pricing higher, with upper-quartile annual prices up ~5% YoY

---

## Pricing Psychology

### Anchoring

Present a high-priced option first so subsequent options feel like deals.

- Show the $299 "Pro" plan first; $99 "Standard" then feels affordable
- **Documented impact:** Anchoring increases perceived value by 32%
- **Cautionary example:** JCPenney removed anchoring (eliminated sales for "fair pricing") in 2012 -- sales dropped 25%

### Decoy Pricing

Add a strategically inferior option to nudge users toward your target.

- **The Economist example:** Digital-only $59, Print-only $125, Digital+Print $125. Print-only is the decoy -- nobody picks it, but it makes the combo look like a steal
- **App adaptation:** Basic $4.99/mo, Plus $11.99/mo, Pro $12.99/mo. Plus is the decoy; Pro feels like a no-brainer for $1 more

### Charm Pricing

Prices ending in 9 exploit left-digit bias (brain reads $9.99 as "$9-something").

- Charm pricing increases sales by at least 24%
- 60.7% of retail prices end in 9
- **Exception:** Premium/luxury positioning benefits from round numbers ($200 not $199.99)
- App stores display $X.99 by convention; breaking this pattern can signal premium but risks appearing overpriced

### Price Framing

- **Per-day framing:** "$0.33/day" instead of "$9.99/month" -- reduces perceived cost
- **Savings framing:** "Save $48/year" on annual plan -- anchors against monthly total
- **Comparison framing:** "Less than a coffee" -- normalizes the price against familiar spending

---

## App Store Commission Structures

### Standard Rates

| Store | Standard | Small Business | Subscription Year 2+ |
|---|---|---|---|
| **Apple App Store** | 30% | 15% (<$1M/yr proceeds) | 15% (after 1yr continuous) |
| **Google Play** | 30% | 15% (first $1M/yr revenue) | 15% (after 1yr continuous) |

### Apple Small Business Program

- Developers earning up to $1M in proceeds in the prior calendar year qualify
- Commission drops from 30% to 15% on all paid apps and IAPs
- If you exceed $1M during the year, standard rate applies to future sales that year
- Must re-qualify annually

### EU Digital Markets Act (DMA) -- 2025/2026

Apple's EU-specific alternative business terms:

| Fee Component | Rate | Notes |
|---|---|---|
| **Base commission** | 13% (10% for Small Business) | On digital goods/services |
| **Core Technology Commission** | 5% | On sales promoted in-app |
| **New user acquisition fee** | 2% | First 6 months per user (SBP exempt) |

- Combined fees can reach ~20% under the new system vs 30% standard
- Apple fined EUR 500M (April 2025) for DMA non-compliance on anti-steering
- External payment links allowed in the US (StoreKit External Purchase Link Entitlement optional in US, required elsewhere)

### Practical Impact for Solo Devs

At $500K annual revenue with Small Business Program:
- **Standard (15%):** $75K to Apple, $425K net
- **EU alternative terms:** Up to ~20% combined, but external payment option possible
- **Web checkout bypass:** 0% store commission but you handle payments/tax

---

## RevenueCat vs Native SDKs

### Feature Comparison

| Feature | RevenueCat | Native StoreKit 2 / Billing v7 |
|---|---|---|
| **Setup time** | Hours | Days to weeks |
| **Cross-platform** | Single SDK (iOS, Android, Web) | Separate implementations |
| **Receipt validation** | Server-side, automatic | Build your own server |
| **Analytics dashboard** | MRR, churn, LTV, trials built-in | Build or integrate third-party |
| **Paywall templates** | No-code, A/B testable | Build from scratch |
| **Subscription lifecycle** | Managed (renewals, grace, billing) | Manual state machine |
| **Integrations** | Amplitude, Mixpanel, Adjust, etc. | Manual webhook plumbing |
| **Price** | Free <$2,500 MTR; 1% above | Free SDK; server costs on you |
| **Control** | Abstracted | Full |
| **Stripe web support** | Yes, unified dashboard | Separate system |

### Pricing Tiers (2026)

| Provider | Free Tier | Paid Rate |
|---|---|---|
| **RevenueCat** | $2,500 MTR | 1% of MTR |
| **Adapty** | $5,000 MTR | 1% of MTR |
| **Qonversion** | $10,000 MTR | 0.6% of MTR |

### Decision Matrix

| Scenario | Recommendation |
|---|---|
| Solo dev, <$2,500 MTR | RevenueCat (free, fastest integration) |
| Solo dev, $2,500-$30K MTR | RevenueCat (1% fee justified by time saved) |
| Revenue >$30K MTR, single platform | Consider native SDK to reclaim the 1% |
| Cross-platform, any revenue | RevenueCat or Adapty (unified management) |
| Budget-constrained, early stage | Qonversion ($10K free tier) |

---

## Paywalls and Conversion Optimization

### Paywall Types

| Type | Description | Median Conversion |
|---|---|---|
| **Hard paywall** | Must pay to use the app at all | 10.7% |
| **Soft paywall** | Free core, pay for premium features | 2.1% |
| **Metered paywall** | N free uses, then pay | 3-5% |
| **Feature gate** | Specific features locked | 2-4% |
| **Freemium + upsell** | In-context upgrade prompts | 1-3% |

### High-Converting Paywall Checklist

1. **Show value before asking for money** -- demonstrate the premium feature, then gate it
2. **Social proof** -- "Join 50,000+ users" or app store rating badge
3. **Benefit-first copy** -- list outcomes, not features ("Save 2 hours/week" not "Advanced analytics")
4. **Limited choices** -- 2-3 options maximum; decision paralysis kills conversion
5. **Highlight recommended plan** -- visual emphasis on target tier
6. **Annual savings badge** -- "Save 40%" callout on yearly plan
7. **Trial CTA clarity** -- "Start free trial" outperforms "Subscribe" by 15-20%
8. **Restore purchases button** -- required by Apple, builds trust
9. **Close button visible** -- hidden close buttons increase complaints, not revenue

### A/B Testing Priority (highest impact first)

1. **Price point** -- test $4.99 vs $6.99 vs $9.99
2. **Trial length** -- 3-day vs 7-day
3. **Paywall timing** -- on first launch vs after value moment
4. **Copy and framing** -- benefit-oriented vs feature list
5. **Plan presentation** -- annual-first vs monthly-first
6. **Visual design** -- minimal vs feature-rich paywall

A/B testing paywalls lifts conversions ~25%. Personalized offers add ~15% on top.

---

## Free Tier Design

### What to Give Away

- **Core value loop** -- enough to demonstrate the product's key benefit
- **Time-limited premium** -- 3 uses of the premium feature, then gate
- **Read-only access** -- view but not export, analyze but not act
- **Single-player features** -- collaboration and sharing behind paywall

### Gating Mechanisms

| Mechanism | When to Use |
|---|---|
| **Usage limits** | AI credits, exports, API calls |
| **Feature locks** | Advanced tools, integrations |
| **Time limits** | Full access for N days |
| **Quality gates** | Basic output free, HD/premium output paid |
| **Capacity limits** | 3 projects free, unlimited paid |

### Anti-Patterns (Avoid These)

- **Too generous free tier:** No reason to upgrade. If free users are happy, your gate is wrong
- **Too restrictive free tier:** Users cannot experience value, so they leave instead of upgrading
- **Gating table stakes:** If competitors offer a feature for free, gating it drives users away
- **Bait and switch:** Removing free features after building habits destroys trust and generates 1-star reviews
- **Nagware:** Excessive upgrade prompts cause uninstalls. Limit to contextual, value-aligned moments

---

## B2B vs B2C Pricing Strategies

### Comparison

| Dimension | B2C | B2B |
|---|---|---|
| **Price range** | $2.99-$14.99/mo | $29-$499/mo (SMB); $1K+/mo (enterprise) |
| **Monthly churn** | 6-8% | 3.5% average (SMB 3-5%, enterprise <1%) |
| **Sales cycle** | Instant (self-serve) | Days to months |
| **Decision maker** | Individual | Committee / budget holder |
| **Payment method** | Card, IAP | Invoice, PO, wire |
| **Retention driver** | Habit, delight | ROI, integration depth, switching cost |
| **LTV** | $30-$150 typical | $500-$10K+ |
| **Support expectation** | Self-serve, FAQ | Email at minimum, often live chat/call |

### Solo Dev Recommendations

**Start with B2C if:**
- You want fast validation and self-serve revenue
- Your product solves a personal pain point
- You can reach users via app stores or content marketing

**Start with B2B if:**
- You can charge $50+/mo and need fewer customers
- The problem has clear ROI (time/money saved for a business)
- You can tolerate longer sales cycles

**The math:** 1,000 B2C users at $9.99/mo = $9,990 MRR. 20 B2B users at $499/mo = $9,980 MRR. B2B needs 50x fewer customers but requires more support and sales effort.

**Prosumer sweet spot for solo devs:** B2C pricing ($9.99-$29.99/mo) targeting professionals who expense it. Self-serve acquisition, B2B-adjacent retention. Examples: Notion, Superhuman early days.

---

## Revenue Metrics

### Core Formulas

| Metric | Formula | 2025-2026 Benchmark |
|---|---|---|
| **MRR** | Sum of all monthly subscription revenue | Median: $8.3K for apps >1yr old |
| **ARR** | MRR x 12 | -- |
| **ARPU** | Total revenue / active users | Varies widely by category |
| **LTV** | ARPU / monthly churn rate | High-price: $62.19/yr; low-price: $10.69/yr |
| **CAC** | Total acquisition cost / new customers | Healthy: LTV:CAC > 3:1 |
| **Monthly churn** | Lost subscribers / start-of-month subscribers | SaaS avg: 4.1% (3.0% voluntary + 1.1% involuntary) |
| **Revenue churn** | Lost MRR / start-of-month MRR | Median: 12.5% annual |
| **Trial-to-Paid** | Paid conversions / trial starts | 40-60% (opt-out); 15-25% (opt-in) |

### Involuntary Churn

Involuntary churn (payment failures) accounts for 0.8-1.1% monthly -- often 25-30% of total churn.

**Mitigation strategies:**
- **Dunning emails:** 3-5 email sequence before and after failed charge
- **Grace periods:** 7-16 day retry window (Apple provides 60 days of billing retry)
- **Card updater services:** Stripe and RevenueCat auto-update expired cards
- **In-app messaging:** Alert users about billing issues before access is revoked

### Reality Check for New Apps (2026)

- Only 17.3% of new subscription apps reach $1K MRR within 2 years
- Only 4.6% reach $10K MRR within 2 years
- Apps launched before 2020 still generate 69% of all subscription revenue
- Top 25% of apps grew MRR by 80% YoY; bottom 25% dropped 33%
- New app launches hit 14,700/month by January 2026 (7x increase from 2022)

---

## Payment Processing for Web

### Stripe vs Paddle vs Lemon Squeezy

| Feature | Stripe | Paddle | Lemon Squeezy |
|---|---|---|---|
| **Model** | Payment processor | Merchant of Record | Merchant of Record |
| **Base fee** | 2.9% + $0.30 | 5% + $0.50 | 5% + $0.50 (+1.5% intl.) |
| **Sales tax handling** | You handle (or +Stripe Tax) | Included | Included |
| **VAT/GST compliance** | Your responsibility | They are the seller | They are the seller |
| **Invoicing** | Built-in | Built-in (strong B2B) | Basic |
| **Subscription billing** | Excellent | Excellent | Good |
| **Checkout UX** | Stripe Checkout / Elements | Paddle.js overlay | Hosted / overlay |
| **Payout frequency** | Rolling 2-day | Monthly | Bi-weekly |
| **Developer API** | Best-in-class | Good | Adequate |
| **Ecosystem** | Largest (hundreds of integrations) | Growing | Limited |

**Note:** Stripe acquired Lemon Squeezy (July 2024). Stripe is beta-testing its own MoR solution (~6.4% + $0.30 estimated). Lemon Squeezy's long-term roadmap is uncertain.

### Merchant of Record (MoR) Explained

With a MoR (Paddle, Lemon Squeezy), the platform is the legal seller. They handle:
- Sales tax calculation, collection, and remittance in every jurisdiction
- VAT invoicing and compliance
- Refund liability
- Currency conversion

Without MoR (Stripe alone), you are the seller and must handle tax compliance yourself.

### Decision Path

```
Do you sell globally?
├── No (US only) → Stripe (lowest fees, simplest)
├── Yes
    ├── Revenue < $10K/mo → Lemon Squeezy or Paddle (tax handled, worth the fee premium)
    ├── Revenue $10K-$50K/mo → Paddle (robust, reliable MoR)
    └── Revenue > $50K/mo → Stripe + Stripe Tax (savings justify tax complexity)
        └── Or wait for Stripe MoR GA
```

### Alternatives Worth Watching (2026)

- **Polar:** Developer-focused MoR, open-source friendly
- **Dodo Payments:** Low-cost MoR targeting indie hackers

---

## Legal Considerations

### Auto-Renewal Laws (US)

The legal landscape is fragmented after the Eighth Circuit vacated the FTC's "Click-to-Cancel" rule (July 2025). Key requirements across jurisdictions:

| Requirement | Federal (ROSCA) | California (AB 2863) | New York |
|---|---|---|---|
| **Clear disclosure** | Yes | Yes | Yes |
| **Affirmative consent** | Yes | Yes | Yes |
| **Easy cancellation** | Yes (FTC enforces) | Yes (dark patterns banned) | Yes |
| **Price increase consent** | Not specified | Not specified | 14-day cancel right |
| **Effective date** | Ongoing | July 1, 2025 | Active |

Additional state laws: Minnesota, Utah (Jan 2025), Colorado (Aug 2025 / Feb 2026), Maine (Jan 2026), Maryland (Jun 2026).

**Amazon warning:** FTC secured a $2.5B settlement against Amazon (Sept 2025) for deceptive Prime sign-up and difficult cancellation -- the largest civil penalty of its kind.

### EU Requirements

- **GDPR:** Consent must be freely given; dark patterns invalidate consent
- **DSA/DMA:** Prohibit dark patterns on all digital services; gatekeepers face stricter rules
- **Germany:** Online subscriptions must include a cancellation button accessible without login
- **Proposed Digital Fairness Act:** Addresses difficult cancellations, auto-renewals without reminders, unclear terms

### App Store Refund Policies

- **Apple:** Users can request refunds via reportaproblem.apple.com. Developers notified but cannot block refunds. Apple makes the decision
- **Google Play:** 48-hour refund window for most purchases (automatic). Beyond that, developer-managed or Google-reviewed
- **Subscription refunds:** Pro-rated refunds vary by store policy and jurisdiction

### Dark Pattern Prohibitions

Practices now illegal or actionable in multiple jurisdictions:

- **Roach motel:** Easy to subscribe, hard to cancel
- **Confirm-shaming:** "No thanks, I don't want to save money"
- **Hidden costs:** Revealing fees only at checkout
- **Forced continuity:** Charging after trial with no clear notice
- **Misdirection:** Visual design that steers users away from cancellation

### Compliance Checklist for Solo Devs

1. Disclose subscription terms clearly before purchase
2. Obtain affirmative consent (not pre-checked boxes)
3. Provide cancellation as easy as sign-up (same number of steps)
4. Send renewal reminders before each charge (required in many states)
5. Honor refund requests within platform policy windows
6. Display total cost prominently, not just per-day framing
7. Include clear terms of service and privacy policy links

---

## Sources

- [RevenueCat State of Subscription Apps 2026](https://www.revenuecat.com/state-of-subscription-apps/)
- [RevenueCat State of Subscription Apps 2025](https://www.revenuecat.com/state-of-subscription-apps-2025/)
- [RevenueCat: 5 App Monetization Trends 2025](https://www.revenuecat.com/blog/growth/2025-app-monetization-trends/)
- [RevenueCat: Hybrid Monetization Techniques](https://www.revenuecat.com/blog/growth/hybrid-monetization-techniques/)
- [SaaStr: Top 10 Learnings From RevenueCat SOSA](https://www.saastr.com/the-top-10-learnings-from-revenuecats-state-of-subscription-apps-how-115000-mobile-apps-deliver-16b-in-revenue-whats-working-whats-quietly-killing-growth/)
- [Business of Apps: Subscription Trial Benchmarks 2026](https://www.businessofapps.com/data/app-subscription-trial-benchmarks/)
- [Apple App Store Small Business Program](https://developer.apple.com/app-store/small-business-program/)
- [Apple DMA and Apps in the EU](https://developer.apple.com/support/dma-and-apps-in-the-eu/)
- [Adapty: Apple EU Fee System 2025](https://adapty.io/blog/apple-eu-in-app-purchase-fee-system-2025/)
- [Adapty: App Store Small Business Program Guide 2026](https://adapty.io/blog/app-store-small-business-program/)
- [StoreKit 2 -- Apple Developer](https://developer.apple.com/storekit/)
- [WWDC 2025: What's New in StoreKit](https://dev.to/arshtechpro/wwdc-2025-whats-new-in-storekit-and-in-app-purchase-31if)
- [MetaCTO: Real Cost of RevenueCat](https://www.metacto.com/blogs/the-real-cost-of-revenuecat-what-app-publishers-need-to-know)
- [NativeLaunch: RevenueCat vs Native IAP](https://nativelaunch.dev/articles/compare/revenuecat-vs-native-iap)
- [Stripe vs Paddle vs Lemon Squeezy Comparison](https://medium.com/@muhammadwaniai/stripe-vs-paddle-vs-lemon-squeezy-i-processed-10k-through-each-heres-what-actually-matters-27ef04e4cb43)
- [Athenic: SaaS Billing for AI Products](https://getathenic.com/blog/stripe-vs-paddle-vs-lemon-squeezy-saas-billing)
- [UserJot: Payment Processor Fees Compared](https://userjot.com/blog/stripe-polar-lemon-squeezy-gumroad-transaction-fees)
- [Vitally: B2B SaaS Churn Rate Benchmarks 2025](https://www.vitally.io/post/saas-churn-benchmarks)
- [Churnkey: B2B vs B2C Churn Rates](https://churnkey.co/blog/the-difference-between-b2b-b2c-churn-rates/)
- [Paddle: SaaS Churn Rate](https://www.paddle.com/blog/saas-churn-rate)
- [Capital One Shopping: Pricing Psychology Statistics 2025](https://capitaloneshopping.com/research/pricing-psychology-statistics/)
- [ZwillGen: Auto-Renewal Legal Landscape 2025](https://www.zwillgen.com/practical-advice/auto-renewal-update-legal-landscape-imposes-complex-obligations-subscription-businesses/)
- [Terms.Law: Dark Patterns and Subscriptions 2025](https://www.terms.law/2025/12/05/dark-patterns-subscriptions-and-ai-designed-flows-where-the-law-draws-the-line-now/)
- [FTC Click-to-Cancel Rule Analysis](https://cookie-script.com/privacy-laws/dark-patterns-2026-the-ftc-new-click-to-cancel-rule)
- [Faegre Drinker: 2025 Auto-Renewal Law Developments](https://www.faegredrinker.com/en/insights/publications/2025/1/new-year-new-regulations-2025-brings-significant-developments-to-federal-and-state-automatic-renewal-laws)
- [EU Digital Fairness Act: Digital Subscriptions](https://www.insideprivacy.com/consumer-protection/digital-fairness-act-series-topic-4-digital-subscriptions/)
- [EU DMA: Commission Notifications from Apple](https://digital-markets-act.ec.europa.eu/commission-receives-notifications-apple-under-digital-markets-act-2025-11-27_en)
