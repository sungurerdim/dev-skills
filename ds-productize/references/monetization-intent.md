# Reference: Monetization-Intent Block

Consumer: ds-productize Phase 1 step 3. Four questions, each with a signal-derived `(recommended)` default — resolved from the blueprint profile's `billing` / `platforms` / `audience` signals ([../../core/signal-inventory.md](../../core/signal-inventory.md)).

| Question | Recommended default |
|----------|---------------------|
| Current/target model | `billing=none` → freemium/undecided; `billing=store-iap` → store subscription; `billing∈{stripe,paddle,lemonsqueezy,revenuecat,other}` → subscription |
| Target price range | Existing price literals or store listing when found, else `not-stated` |
| B2B vs B2C vs prosumer | `audience=public` → B2C/prosumer; `audience=internal` → B2B; `audience=developers` → B2B |
| Platforms — store IAP vs web checkout vs both | `platforms∩{ios,android}≠∅` → store IAP; `platforms∋web` → web checkout; both present → both |

Default: apply every recommended default and record each as `Decided without asking — say if wrong: {question} = {value}`; a signal that resolves to `unknown` records that question `not-stated` rather than guessing. `--ask`: ask the block once, only the unknowns.
