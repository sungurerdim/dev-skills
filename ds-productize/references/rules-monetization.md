# Rules: Monetization & Pricing

Benchmarks sourced from RevenueCat State of Subscription Apps 2025/2026, Recurly 2025, and jurisdiction-specific subscription law summaries. MON = monetization model + billing integrity. PRC = pricing + packaging.

## MON-01 [HIGH] Model does not fit cost structure
Product with variable per-unit cost (AI inference, media processing, API passthrough) sold on a flat subscription.
- **Detect:** Per-request paid compute in code paths gated only by a flat-price subscription; no usage caps, credits, or metering.
- **Fix:** Hybrid model — subscription + consumable credits or metered usage caps. 35% of subscription apps already mix models; AI apps lead adoption. Default-recommend hybrid (base + metered) over pure usage-based: 46% of companies run a hybrid approach vs 15% largely usage-based/PAYG (2026) — never chase the usage-based narrative uncritically.
- **Impact:** Heavy users make unit economics negative; flat pricing cannot absorb variable cost.
- **Source:** RevenueCat SOSA 2026, hybrid monetization trend data.

## MON-02 [MEDIUM] Freemium chosen where hard paywall converts better
Utility/productivity product with a generous free tier and no data justifying it.
- **Detect:** Free tier covers the entire core loop; no network effect or virality rationale stated.
- **Fix:** Evaluate hard paywall or metered gate. Hard paywall median conversion 10.7% vs freemium 2.1%; D14 revenue-per-install $2.32 vs $0.27 — retention at 12 months is nearly identical between models.
- **Impact:** 8-9x revenue-per-install gap with no retention benefit in return.
- **Source:** RevenueCat SOSA 2026.

## MON-03 [CRITICAL] Client-only entitlement enforcement
Paid capability gated in UI/client code only.
- **Detect:** Feature flag / tier check present in client bundle with no corresponding server-side check on the API that serves the paid capability.
- **Fix:** Enforce entitlement on the server route or backend function; client check is UX, server check is the gate.
- **Impact:** Anyone with devtools or a modified client gets paid features free.
- **Source:** OWASP API Top 10 — broken function-level authorization.

## MON-04 [CRITICAL] Payment webhook accepted without signature verification
Billing provider webhook handler processes events unverified.
- **Detect:** Webhook route parses provider payload without verifying the provider signature header / signing secret; or event handler mutates state with no processed-event dedup.
- **Fix:** Verify signature before any state change; reject on mismatch. Audit the two idempotency layers separately — they are distinct, commonly conflated checks:
  1. **API-request idempotency** (client → provider): `Idempotency-Key` header with a V4 UUID / high-entropy string (≤255 chars); the provider replays the first result for ≥24h and errors on parameter mismatch.
  2. **Webhook event idempotency** (provider → handler): delivery is at-least-once, never exactly-once — store each processed event ID under a UNIQUE constraint and short-circuit before mutating state; respond 2xx within 10 seconds (failed deliveries retry with exponential backoff over ~3 days).
- **Impact:** Forged webhook grants subscriptions or refunds without payment; missing event dedup double-applies retried deliveries (double credits, double emails).
- **Source:** Provider security docs (Stripe/Paddle webhook signing); Stripe idempotent-requests API reference; at-least-once webhook delivery guidance 2026.

## MON-05 [CRITICAL] Card data touches own servers
PAN/CVC handled or logged by first-party code.
- **Detect:** Request bodies, logs, or DB columns carrying card number/CVC shapes; forms posting card fields to own endpoints instead of provider tokenization.
- **Fix:** Provider-hosted checkout or tokenizing elements; card data never transits own infrastructure.
- **Impact:** Full PCI-DSS scope, breach liability, processor termination.
- **Source:** PCI-DSS SAQ-A boundary.

## MON-06 [HIGH] No involuntary-churn defense
Failed renewals terminate access immediately with no recovery flow.
- **Detect:** No grace period configuration, no dunning email sequence, no card-updater usage; subscription state flips on first failed charge.
- **Fix:** Grace period (7-16 days; Apple provides 60 days billing retry), 3-5 step dunning sequence, provider card-updater.
- **Impact:** Involuntary churn is 0.8-1.1% monthly — often 25-30% of total churn, recoverable with mechanics not persuasion.
- **Source:** Recurly 2025 churn benchmarks; RevenueCat SOSA.

## MON-07 [HIGH] Trial terms not disclosed before purchase
Opt-out trial converts to paid without clear pre-purchase disclosure or renewal reminder.
- **Detect:** Trial CTA without visible price-after-trial, renewal date, or cancellation path; no reminder before first charge.
- **Fix:** Disclose price, renewal timing, and cancellation before consent; send pre-renewal reminders (required in several US states).
- **Impact:** ROSCA/state auto-renewal law exposure; FTC's Amazon settlement ($2.5B, Sept 2025) set the enforcement bar.
- **Source:** ROSCA; California AB 2863; FTC v. Amazon 2025.

## MON-08 [HIGH] Cancellation harder than subscription
Cancel path longer than sign-up path, or requires contact/login hurdles sign-up did not.
- **Detect:** Count steps: subscribe vs cancel. Cancel requiring support contact, hidden menu, or confirm-shaming copy.
- **Fix:** Cancellation reachable in the same number of steps as subscription; Germany requires a no-login cancellation button; dark patterns (roach motel, misdirection) are actionable in EU (DSA/GDPR) and multiple US states.
- **Impact:** Legal exposure + refund/chargeback spikes + 1-star review pressure.
- **Source:** State auto-renewal laws 2025-2026; EU DSA dark-pattern prohibitions.

## MON-09 [MEDIUM] Missing restore-purchases path
Store-distributed app without purchase restore.
- **Detect:** IAP present, no restore entry point (StoreKit `Transaction.currentEntitlements` / Billing `queryPurchases` unused in any UI flow).
- **Fix:** Restore button on the paywall (Apple requires it); entitlements re-derived from store, not local flags.
- **Impact:** Store rejection risk; device-migration users locked out of paid content.
- **Source:** App Store Review Guidelines 3.1.1.

## MON-10 [MEDIUM] Hand-rolled billing where managed layer fits revenue stage
Custom receipt validation / subscription state machine at a stage where a managed provider is free or ~1%.
- **Detect:** First-party receipt validation servers, hand-written renewal state machines, at pre-scale revenue.
- **Fix:** Managed layer (free tiers exist below ~$2.5K-10K MTR; ~1% above) until single-platform revenue justifies reclaiming the fee.
- **Impact:** Weeks of maintenance on undifferentiated plumbing; edge-case bugs in grace/renewal handling.
- **Source:** RevenueCat/Adapty/Qonversion pricing tiers 2026.

## MON-11 [MEDIUM] Wrong tax posture for global web sales
Selling globally with a bare payment processor and no tax handling.
- **Detect:** Web checkout via raw processor, customers in multiple jurisdictions, no tax product or MoR.
- **Fix:** Below ~$10K/mo → Merchant of Record (tax/VAT handled as legal seller); above ~$50K/mo → processor + tax product does the math.
- **Impact:** Unremitted VAT/sales-tax liability accrues silently per jurisdiction.
- **Source:** MoR decision-path comparisons 2026 (Paddle / Lemon Squeezy / Stripe Tax).

## MON-12 [LOW] Store small-business commission unclaimed or stale-rate math
Eligible store revenue paying 30% where 15% applies, or margin planning on outdated Play rates.
- **Detect:** Store-distributed app, prior-year proceeds under $1M, small-business program not enrolled; plan/docs citing Play's 15%/30% split for revenue after 30 Jun 2026.
- **Fix:** Enroll (Apple Small Business Program — also 15% for any subscriber past 12 paid months; re-qualify annually). Google Play: from 30 Jun 2026 (US/UK/EEA first, phased globally) the 15%/30% split is replaced by 10% base + 5% Play-Billing fee (~15% effective on subscriptions) — full rate table + Apple/Stripe/marketplace rates in [rules-pricing.md](rules-pricing.md) CHN-02.
- **Impact:** 15 points of margin left on the table; stale rate tables mis-price the channel.
- **Source:** Apple SBP terms; Play Console service-fees page (post-Epic-settlement structure).

## MON-13 [MEDIUM] Pricing-model migration without a safety window
Pricing-model change (e.g., per-seat → usage/hybrid) planned as a hard cutover for all customers at once.
- **Detect:** Model change planned or announced with no grandfather clause for existing customers and no metering period before billing switches.
- **Fix:** Grandfather existing customers on the old model for 12-18 months while new customers go straight to the new model; run a shadow-billing period metering usage on the new model for 60-90 days before cutover.
- **Impact:** Hard cutovers turn pricing changes into churn events; shadow billing surfaces bill-shock cases before they invoice.
- **Source:** Usage-based-pricing migration patterns 2026 (grandfathering + shadow billing, cited consistently across pricing-transition guides).

## PRC-01 [MEDIUM] No target tier / decoy logic in packaging
Tier list where every option competes equally.
- **Detect:** 2+ tiers, none visually recommended; or 4+ tiers (decision paralysis).
- **Fix:** 2-3 tiers, one marked recommended; decoy priced to make the target tier obviously better value.
- **Impact:** Decision paralysis suppresses conversion; unguided choice skews to the cheapest tier.
- **Source:** Decoy-effect pricing research (Economist digital+print case).

## PRC-02 [MEDIUM] No annual option or weak annual framing
Monthly-only pricing, or annual priced without a savings anchor — or discounted outside the segment norm.
- **Detect:** Single monthly price; or annual present without "save {n}%" framing; or annual discount mismatched to segment (segment norms differ — do not apply one number to both).
- **Fix:** Add annual with a savings badge at the segment norm — consumer subscription apps: 30-40% off monthly-equivalent (RevenueCat SOSA); B2B SaaS: 15-20%, most commonly 16.7% ("2 months free") — see [rules-pricing.md](rules-pricing.md) DSC-02. Onboard annual subscribers hard — 30% cancel in the first month.
- **Impact:** Annual subscribers carry higher LTV and smooth revenue; absence caps LTV at monthly churn; over-discounting B2B annual gives away ~15 points for commitment the 16.7% norm already buys.
- **Source:** RevenueCat SOSA (consumer); SaaStr / Subscription Index (B2B norm).

## PRC-03 [LOW] Price presentation fights positioning
Charm pricing on a premium product, or round pricing on a mass-market one.
- **Detect:** $199.99-style endings on luxury positioning; $200-style on value positioning.
- **Fix:** Value/mass-market → charm ($X.99, +24% sales effect); premium → round numbers.
- **Impact:** Presentation mismatch erodes the intended perception.
- **Source:** Pricing-psychology statistics (left-digit bias).

## PRC-04 [HIGH] Prices hardcoded in client builds
Price literals compiled into app/frontend.
- **Detect:** Currency-formatted literals in client source matching checkout amounts; price changes requiring redeploy/store review.
- **Fix:** Prices from provider products / remote config; client renders what the provider returns.
- **Impact:** A/B tests and price changes blocked by release cycles; store price drift shows wrong numbers.
- **Source:** Provider product-catalog patterns (StoreKit products, Billing SKUs, Stripe Prices).

## PRC-05 [MEDIUM] Pricing page lists features, not outcomes
Packaging copy enumerates capabilities without user outcomes.
- **Detect:** Tier bullets naming internals ("advanced analytics") with no outcome framing ("know which feature churns users").
- **Fix:** Benefit-first bullets; social-proof slot; trial CTA phrased "Start free trial" (outperforms "Subscribe" by 15-20%).
- **Impact:** Outcome framing is the highest-leverage copy change on the conversion path after price itself.
- **Source:** Paywall conversion checklists, A/B benchmark data (paywall tests lift ~25%).
