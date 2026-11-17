# Money — paywall, checkout and subscription screens

Loaded when the product takes payments (`billing≠none`). Server-side entitlement, webhook, card-data, refund and receipt checks are in the safe phase (SAR-07, API-20, SEC-26–SEC-28); store purchase handling is in [store.md](store.md) (STO-05, STO-21, LCH-11).

### PRC-04 [HIGH] Prices hard-coded in the client
- **Detect:** currency-formatted amounts or price IDs written into client source or copy instead of read from the billing provider's product catalogue (StoreKit products, Play Billing product details, Stripe Prices, Paddle prices); a price change that needs a redeploy or store review. Detector of SIM-06.
- **Mech:** T `git grep -nIE '[$€£¥₺][[:space:]]*[0-9]+([.,][0-9]{2})?|[0-9]+([.,][0-9]{2})?[[:space:]]*(USD|EUR|GBP|TRY|€)|price_[A-Za-z0-9]{8,}' -- ':!*test*' ':!*.md' ':!*.json'`
- **Fix:** render the price, currency and period the provider returns for the user's storefront or region; keep product IDs in one config.
- **Impact:** the screen shows one price and the store charges another, in the wrong currency for most countries.
- **Source:** DRY / single source of truth; Apple StoreKit, `Product.displayPrice`; Google Play Billing, `ProductDetails`; Stripe, Prices API; SIM-06.

### UX-DP-03 [HIGH] Charge terms hidden on the purchase screen
- **Detect:** a paywall or checkout that does not show, before the buy action, the price, the billing period, the auto-renewal, the trial length with the price after it, and links to terms and privacy; mandatory fees first shown at the last step; per-day or comparison prices without the billed amount at equal weight; countdowns or scarcity not backed by data; no reminder before a trial converts.
- **Mech:** T `git grep -nIiE 'paywall|subscribe|subscription|free.?trial|per day|/day|only [0-9]+ left|countdown' -- ':!*test*' ':!*.md'`
- **Fix:** price, period, renewal and trial terms next to the buy button; every mandatory fee in the first price shown; real numbers only; a reminder before the first charge.
- **Impact:** surprise charges become refunds, chargebacks and store complaints.
- **Source:** Apple App Review Guideline 3.1.2; deceptive.design (hidden costs, fake scarcity); FTC Negative Option Rule (16 CFR 425).

### UX-DP-02 [HIGH] Cancelling is harder than subscribing
- **Detect:** sign-up online but cancellation only by email, phone or chat; more steps to cancel than to subscribe; retention screens beyond one skippable offer; no in-app route to manage the subscription (`showManageSubscriptions`, the Play subscriptions deep link, the provider's customer portal); unsubscribe links that require login.
- **Mech:** T `git grep -nIE 'showManageSubscriptions|manageSubscriptionsSheet|play\.google\.com/store/account/subscriptions|billingPortal|customer_portal|cancel_at_period_end' -- ':!*.md'`
- **Fix:** a cancel or manage-subscription entry in account settings that completes in as many steps as sign-up; at most one optional retention offer.
- **Impact:** users who cannot leave dispute the charge with their bank or store, which costs more than the lost subscription.
- **Source:** deceptive.design (hard to cancel); Apple, `showManageSubscriptions(in:)`; Google Play, Let users manage their subscriptions.
