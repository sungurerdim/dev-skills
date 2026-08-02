# Phase 0 Default Plan — Stage and Type Routing

The default skill sequence per stage signal, the three stage-independent branches (feature-planning, monetization, scope-freeze), and the per-project-type overrides. Loaded when Phase 0 builds the plan.

| Stage signal | Default sequence |
|--------------|------------------|
| idea | ds-research → ds-benchmark → ds-init |
| spec-only | ds-init → ds-blueprint → ds-benchmark |
| scaffold | ds-blueprint → ds-init → ds-fix |
| implementation | ds-blueprint → ds-review → ds-test → ds-simplify → ds-fix |
| review-pending | ds-review → ds-compliance OR ds-mobile → ds-frontend + ds-backend (per project type) → ds-simplify |
| pre-launch | ds-devops → ds-deploy → ds-launch → ds-repo (--oss-ready on public intent) |
| launched | ds-tune → ds-deps (periodic hygiene) |
| frozen | ds-blueprint → ds-deps (security-only) |

**Feature-planning branch (independent of stage):** if the user's immediate ask is a new feature whose design is still open (no `specs/{feature}/spec.md` or equivalent plan exists) → route the planning leg to `/ds-pipeline {idea}` first, ahead of any implementation-oriented skill in the default sequence; resume the stage's default sequence once `specs/{feature}/tasks.md` exists.

**Monetization branch (independent of stage):** if paid-product intent holds (stated in the Phase 0 ambiguity block, or billing/paywall surfaces detected in source) → insert `/ds-productize --audit` into Phase 2 after the stack-specific skills; no billing surface yet (greenfield) → `/ds-productize --plan` instead. Free/internal intent → skip entirely.

**Scope-Freeze branch (independent of stage):** if the user's ask signals release scope reduction (e.g. "simplify the release", "cut this down to an MVP", "too much to perfect every detail before we ship") → insert `/ds-freeze` as the very first delegation, before Phase 1 Ideal-vs-Current Gap. Wait for its manifest. The frozen `ship` set becomes the working scope for every later phase: Phase 1's gap table, Phase 2's audits, and Phase 5's launch gates all operate against the narrowed manifest, not the full backlog — `defer-backlog`/`defer-hidden` items are excluded entirely (they already carry their own tracking issue from ds-freeze). No scope-reduction signal → skip entirely, ds-ship's own Phase 1 gap-closing runs against the full feature set as usual.

| Project type | Additional rules |
|--------------|------------------|
| mobile | ds-mobile authoritative for security/privacy/regulatory; ds-frontend only for UI/UX where applicable; skip ds-compliance on scopes ds-mobile owns |
| web (SSR/SPA) | ds-frontend + ds-backend + ds-compliance all run |
| backend-only | ds-backend + ds-devops + ds-deploy; skip ds-frontend |
| library | ds-test (high coverage) + ds-docs (API-heavy) + ds-repo --oss-ready; skip ds-launch |
| CLI | ds-test + ds-docs + ds-repo; skip ds-frontend, ds-launch |
| paid product / SaaS intent | ds-productize joins Phase 2 per the Monetization branch; store execution stays with ds-launch, canonical privacy with ds-compliance |

