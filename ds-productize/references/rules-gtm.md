# Rules: Go-to-Market Baseline

GTM readiness rules — positioning, conversion surface, funnel instrumentation, launch plan. Store-listing execution (ASO, screenshots, review prep) belongs to ds-launch; regulatory privacy belongs to ds-compliance. This scope audits that the *business learning loop* exists before money is asked for.

## GTM-01 [HIGH] No durable value proposition
No one-paragraph concrete promise findable in README, landing copy, or plan docs — or the promise contradicts what the code ships.
- **Detect:** Grep README/landing/docs for a claim of who-gets-what-outcome; cross-check against blueprint `spec-alignment` findings when fresh.
- **Fix:** Write the promise once, durably; a promised-not-implemented *paid* feature escalates to CRITICAL (selling what does not exist).
- **Impact:** Every downstream asset (pricing page, ads, listing) inherits vagueness from a missing promise.
- **Source:** Positioning practice (persona/JTBD frameworks).

## GTM-02 [LOW] Persona/JTBD not written down
Target user and job-to-be-done exist only in the founder's head.
- **Detect:** No persona/JTBD statement in README, docs, or plan.
- **Fix:** One lightweight persona: who, trigger moment, job-to-be-done, current alternative, willingness-to-pay signal.
- **Impact:** Unwritten personas drift; copy and pricing decisions stop compounding.
- **Source:** BAG + JTBD lightweight framework.

## GTM-03 [MEDIUM] No conversion surface
No landing page (web) or store listing (mobile) with headline, social-proof slot, and a single primary CTA.
- **Detect:** No landing route/file; or landing present with multiple competing CTAs / no headline hierarchy.
- **Fix:** Minimum viable landing: outcome headline, one primary CTA, social-proof slot, pricing link. Store-listing optimization itself → ds-launch.
- **Impact:** Traffic with nowhere to convert; ads and launch spikes evaporate unmeasured.
- **Source:** Landing conversion-structure patterns.

## GTM-04 [MEDIUM] Funnel not instrumented
No acquisition→activation→revenue→retention events, or events carry PII.
- **Detect:** No analytics events on signup/activation/purchase/churn paths; or event properties containing email/name/free-text.
- **Fix:** Object-action event taxonomy on the AARRR checkpoints; privacy-first (no PII in properties, consent-gated where law requires); trial_started / trial_converted / subscription_cancelled as a minimum revenue set.
- **Impact:** Paywall/pricing changes become guesses; PII in events creates the exposure ds-compliance then has to flag.
- **Source:** Privacy-first analytics guides; AARRR funnel definition.

## GTM-05 [MEDIUM] Revenue metrics not computable
MRR, churn, and trial-to-paid cannot be derived from existing data.
- **Detect:** No provider dashboard access noted, no metrics doc, no events from which MRR/churn/trial-to-paid derive.
- **Fix:** Adopt provider analytics or define the 3-metric minimum: MRR, monthly churn (voluntary + involuntary split), trial-to-paid. Reality anchor: only 17.3% of new subscription apps reach $1K MRR within 2 years — measure early, iterate on evidence.
- **Impact:** LTV:CAC is uncomputable, so paid acquisition cannot be evaluated. Nuance: 3:1 is Skok's minimum-viability floor for a repeatable growth motion (top performers ~5x) — it is not an early-stage target and is not meaningful pre-product-market-fit ([rules-pricing.md](rules-pricing.md) PRJ-01).
- **Source:** RevenueCat SOSA 2026 revenue benchmarks; Skok/SaaStr (LTV:CAC origin).

## GTM-06 [LOW] No launch plan
Ship date approaching with no pre-launch checklist.
- **Detect:** No launch/announcement checklist in docs or plan; no waitlist/beta channel; no press-kit basics.
- **Fix:** Minimal plan: announcement channels list, waitlist or beta cohort, press-kit page (screenshots, one-liner, contact), staged-rollout note.
- **Impact:** Launch attention is a one-time spike; unprepared launches spend it with no capture mechanism.
- **Source:** 60-day pre-launch timeline patterns.
