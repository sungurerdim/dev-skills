# Rules: Pricing Method, Channels & Unit Economics

Deep-pricing rules — price-metric selection, willingness-to-pay research, competitor price mapping, channel/commission fit, revenue projection, trial design, price changes, discount discipline. Loaded for the `pricing` scope alongside [rules-monetization.md](rules-monetization.md) (MON/PRC — model + billing integrity + packaging surface). Benchmarks researched 2026-07-17 (≥2 independent sources unless tagged `[single-source]`; contested values carry both sides — never hard-code a contested number into findings).

## PLD-01 [HIGH] Price metric chosen after the fact (or never)
Pricing model and tiers designed before a value metric was selected.
- **Detect:** Tiers/prices exist but no stated value metric (what unit customers pay more for as they get more value); metric fails Stripe's four properties — (1) flexible with customer value, (2) understandable without explanation, (3) hard to game, (4) aligned with how customers budget.
- **Fix:** Sequence is value metric → pricing model → tier structure → measurement (Stripe SaaS pricing guide). Pick the metric that scales with delivered value (seats, usage units, outcomes), then build the ladder on it.
- **Impact:** Stripe: "Your value metric is what customers pay for as they grow. Getting it wrong can be a costly mistake."
- **Source:** Stripe — A Guide to SaaS Pricing and Packaging.

## PLD-02 [MEDIUM] Ladder shape breaks self-serve comprehension
Public pricing page with more than 3-4 plans or more than two pricing axes.
- **Detect:** 5+ public tiers; pricing requiring a calculator or sales conversation for the common purchase; tiers differentiated by raw feature count instead of buyer maturity/journey.
- **Fix:** Good-Better-Best (3, max 4 public tiers), one or two pricing axes, tier boundaries mapped to buyer maturity (starter → pro → enterprise pattern). Complexity beyond that belongs in a sales-assisted tier, not the public page.
- **Source:** Stripe pricing guide; GBB packaging practice (2026).

## PLD-03 [MEDIUM] Seat-only pricing on an AI-agent product
Product where AI does work autonomously (one seat produces multi-human output) priced purely per seat.
- **Detect:** Agentic/automation product with per-seat-only pricing; no usage/outcome component.
- **Fix:** Hybrid (base + metered) — Bessemer's 2026 tracking has pure per-seat falling 21%→15% of SaaS companies while seat+usage hybrid rose 27%→41% `[single-source for exact percentages]`. Per-seat stays valid when AI behaves as a copilot inside an existing per-user workflow. GitHub Copilot's 2026 move to layered usage billing is the reference case (transition date contested: April vs June 2026 — recorded, don't cite a specific date).
- **Caution:** The circulating "Gartner: 70% prefer usage-based by 2026" stat does not trace to a locatable primary Gartner document (likely conflation of separate IDC/Gartner forecasts) — never cite it in findings.
- **Source:** Bessemer AI pricing tracking; Stripe/Paddle hybrid-model guidance; MON-01 (hybrid default).

## WTP-01 [MEDIUM] Price set with zero willingness-to-pay evidence
Prices invented without any structured WTP input.
- **Detect:** No WTP research artifact (survey, interview notes, conjoint output) and no documented rationale tying price to customer value.
- **Fix:** New-to-market product with no established price reference → Van Westendorp PSM: four questions (too cheap / bargain / getting expensive / too expensive), cumulative-curve intersections give the acceptable range (PMC–PME) and optimal point (OPP). Established product, tiered/bundled offer, or feature-tradeoff question → conjoint analysis (handles multi-attribute tradeoffs, produces willingness-to-pay per feature — the accepted method where Van Westendorp can't reach). Sample floor: ~100-200 respondents per analyzed segment; 300-400 for solid precision; B2B guidance runs ~200 minimum.
- **Impact:** Without WTP evidence, the first real pricing signal is churn — the most expensive way to learn.
- **Source:** Sawtooth Software (Van Westendorp + conjoint method docs); practitioner sample-size convergence.

## CPR-01 [MEDIUM] No competitor price map
Pricing set without a structured scan of the competitive price landscape.
- **Detect:** No competitor pricing inventory (plans, price points, fences, terms, monetization metrics) in docs/plan; own price fences (seat caps, usage walls, feature gates) chosen without reference to the category's norms.
- **Fix:** Repeatable sequence — identify direct/indirect competitors → inventory plans/prices/fences/terms → normalize to per-unit economics (per seat / per 1k events / per GB) → benchmark own ladder → revisit at least annually. Delegate the scan to ds-benchmark when present (advisory-handoff: absent → inline scan of top 3-5 public pricing pages). Caveat: published list prices diverge from negotiated deal prices (a cited Fortune-500 case found a ~20-point gap `[single-source]`) — treat pricing pages as rack rate, not market truth, in enterprise segments.
- **Source:** Competitor pricing-analysis methodology (Aqute et al.).

## CHN-01 [MEDIUM] Sales motion mismatched to ACV
Self-serve-only at enterprise price points, or a sales team touching sub-$5K deals.
- **Detect:** ACV vs motion mismatch — pure self-serve/PLG generally fits below ~$5K ACV; hybrid PLG+sales in the mid range; sales-led above roughly $25K-$50K (exact breakpoint contested across sources — treat as a range, adjust for time-to-value and buying-committee size, which can override ACV alone).
- **Fix:** Match motion to CAC-payback math (at $50K ACV a $15K CAC pays back in months; at $5K ACV the same CAC takes years). Bessemer's primary metric is CAC payback against gross-margin-adjusted ARR — averaging ~15 months at the $1-10M ARR stage; the popular 12/18/24-month SMB/mid/enterprise thresholds are `[single-source]` (not on the primary Bessemer page — don't cite as Bessemer).
- **Source:** PLG-vs-sales decision frameworks (2026); Bessemer Scaling to $100 Million (CAC payback).

## CHN-02 [HIGH] Channel commission math stale or unclaimed
Margin planning built on outdated store/marketplace/processor rates.
- **Detect:** Plan/docs citing Play's old 15%/30% split for post-June-2026 revenue; Apple SBP unclaimed under $1M proceeds; marketplace fees assumed uniform.
- **Fix:** Use current rates and re-verify at plan time (all fees drift):
  - **Apple:** 30% standard; 15% via Small Business Program (proceeds ≤ $1M prior + current year — exceeding mid-year reverts future sales); any subscriber past 12 paid months → 15%; EU alternative-terms SBP after year one → 10%.
  - **Google Play:** pre-existing 15% (first $1M) / 30% replaced from **30 Jun 2026** (US/UK/EEA first, phased elsewhere through 2027 `[single-source for full intl timeline]`) by 10% base + 5% Play-Billing fee (~15% effective on subscriptions); 20%/25% on non-recurring transactions by install type — post-Epic-settlement structure.
  - **Stripe (US standard):** 2.9% + 30¢ domestic; +1.5% international card, +1% currency conversion, +0.5% keyed entry (blended worst case ~5.4% + 30¢).
  - **AWS Marketplace:** 3% public SaaS listing (20% AMI/container/ML); private offers scale 3% → 1.5% (≥$10M TCV/renewals); professional services 0.5% (Jun 2026); regional surcharges stack. **Azure/GCP:** reported ~3% flat — `[single-source, not verified against vendor primary — verify-current]`.
- **Impact:** Commission points are pure margin; stale rate tables mis-price the entire channel decision.
- **Source:** Apple SBP terms; Play Console service-fees page; Stripe pricing page; AWS Marketplace listing-fee docs. All rates verify-current at audit time.

## PRJ-01 [MEDIUM] Revenue projection without unit-economics anchors
MRR/ARR projections with no benchmark-grounded assumptions.
- **Detect:** Projections assuming flat-SaaS gross margins on an AI-native product; churn assumed uniform across segments; LTV:CAC treated as an early-stage target.
- **Fix:** Anchor assumptions to segment-correct benchmarks and cite them in the plan:
  - **LTV:CAC ≥ 3:1** is David Skok's minimum-viability floor for companies with a repeatable growth motion — not an aspirational target and not meaningful pre-product-market-fit; top performers run ~5x.
  - **NRR:** 100% good / 110% better / 120%+ best (Bessemer State of the Cloud framing; stage- and segment-dependent).
  - **Gross margin:** blended SaaS ~79-81%; AI-features-on-SaaS 60-79%; AI-native ~52% (ICONIQ Jan 2026) vs ~65% (Bessemer) — **contradiction recorded, present as a range, never a point estimate**; model inference runs ~23% of revenue at scaling stage for AI B2B (ICONIQ + independent corroboration).
  - **Churn (B2B monthly logo):** SMB ~2-5%, mid-market ~1.5-3%, enterprise ~1-2% (best-in-class <0.5-1%); aggregate ~3.5%/mo splitting ~2.6% voluntary + ~0.8% involuntary. Directional: ~70% of churn lands in the first 90 days — onboarding is a revenue lever `[single-source, directional]`.
- **Impact:** Projections built on blended averages overstate AI-native margins by 15-30 points and understate SMB churn several-fold — break-even math inherits every error.
- **Source:** ICONIQ State of AI (Jan 2026); Bessemer; Recurly-derived churn benchmarks; Skok/SaaStr (LTV:CAC origin).

## TRL-01 [MEDIUM] Trial design ignores the strongest levers
Trial configured on folklore (length-only) rather than the levers benchmarks support.
- **Detect:** Trial length chosen with no rationale; no decision recorded on card-upfront vs opt-in; freemium conversion judged against a made-up bar; reverse trial adopted on the strength of a single quoted lift figure.
- **Fix:** Decide with the 2026 evidence: 14 days is the modal length (62% of products) but length is a weak direct lever — onboarding quality drives most of the observed gains from shortening. Card-upfront (opt-out) trials convert ~30% vs ~8.9% opt-in — a >5x gap and the single strongest configuration lever (at the cost of top-of-funnel volume). Freemium→paid: 3-5% good / 8-12% great, distribution is bimodal (a quarter of products sit below 2.5%). Reverse trials: originator claim of 10-40% lift (Verna) vs 2026 ChartMogul benchmark of 4-12% — **contradiction recorded; treat the upside as unproven**, mechanism (loss aversion) is real but magnitude contested.
- **Source:** ChartMogul/ProductLed 2026 Conversion Report; Elena Verna (reverse trials); First Page Sage vertical data.

## CHG-01 [HIGH] Price increase without notice/consent mechanics
Price change planned without checking contract clauses and consumer-law notice duties.
- **Detect:** Planned increase with no price-adjustment clause check on existing contracts; consumer subscriptions auto-renewing at a new price without conspicuous notice; no notice-period decision recorded.
- **Fix:** B2B: a mid-term increase without a contract price-adjustment clause is a breach absent consent — check the clause first. Notice norms (no universal statute): ~30 days floor (monthly), 45-60 days (annual), 60-90+ days for large changes. Consumer: auto-renewal laws (California ARL, NY GBL §527, EU/UK equivalents) impose independent disclosure/notice duties — Spotify's $38M ARL class-action settlement is the reference risk `[single-source]`. Cross-ref MON-07/MON-08 for the disclosure/cancellation surfaces.
- **Source:** SaaS pricing-terms legal analyses; state ARL statutes.

## CHG-02 [MEDIUM] Grandfathering without a sunset
Legacy pricing kept open-ended "to be nice."
- **Detect:** Existing customers left on old pricing indefinitely with no sunset date; grandfathering applied to trivial increases.
- **Fix:** Cap grandfathering with an explicit sunset — commonly 6-12 months tied to next renewal; reserve grandfathering/phased migration for increases exceeding roughly 15-20% `[single-source threshold]`; long-standing customers moving off legacy terms warrant the longest notice (12-18 months per practitioner guidance — aligns with MON-13's migration safety window). Indefinite grandfathered tiers compound into pricing debt across cycles.
- **Source:** Grandfathering/pricing-migration practice guides; MON-13.

## DSC-01 [MEDIUM] Discount discipline absent
Ad-hoc discounting with no ceiling or tracking.
- **Detect:** Discounts granted per-deal with no policy; discounts >20% routine; discount-attracted cohorts not tracked separately.
- **Fix:** Paddle/ProfitWell: discounting lowers SaaS LTV by ~30% (discount-acquired customers churn more, expand less — note: underlying study published 2022, still the standard citation). Proposal-level data (Cacheflow, 10K proposals `[single-source, vendor discontinued]`): 1-20% discounts produced the best deal-size/close-speed outcomes; >40% correlated with smaller, slower deals. Set a ceiling (≤20%), require approval above it, and track discounted-cohort LTV separately. **Exception:** the standard annual-prepay discount is value-additive, not value-destructive — it buys twelve months of zero churn.
- **Source:** Paddle discounting study (2022, flagged); Cacheflow proposal study; SaaStr.

## DSC-02 [LOW] Annual discount outside segment norm
Annual-prepay discount set without segment context.
- **Detect:** B2B SaaS discounting annual at 30-40% (overpaying for commitment); consumer subscription app offering <15% (under-motivating the switch).
- **Fix:** B2B SaaS norm: 15-20%, with 16.7% ("2 months free") the single most common figure; consumer subscription apps: 30-40% (RevenueCat SOSA — PRC-02). A 20% annual discount already implies a 44%+ cost of capital for the upfront cash — going deeper needs an explicit reason.
- **Source:** SaaStr; Subscription Index; RevenueCat SOSA (segment split with PRC-02).
