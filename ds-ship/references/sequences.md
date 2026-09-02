# Phase 0 Default Plan — Mode, Signals, Stage and Type Routing

Loaded when Phase 0 builds the plan. Order of precedence: **mode** decides which legs exist at all → **signals** decide which skills inside a leg have a scope here → the **stage matrix** orders what remains → **type rules** resolve exclusivity. A skill excluded at any step carries that step's reason in the report (`mode-excluded`, `signal-absent — key=value`, `project-type-exclusivity`, `user-trimmed`).

## Modes and their legs

| Mode | Legs that run | Legs that are `mode-excluded` |
|------|---------------|-------------------------------|
| harden | P2 rule audit (blueprint bootstrap, review, stack-specific, compliance/mobile, test, fix) · P3 simplify · P4 docs | P1 benchmark · productize · P5 release chain · launch legs · Ship-ready verdict (reports `Health:`) |
| release | harden + P5 release chain: devops → deploy → release → repo; productize when `billing ≠ none` | P1 benchmark · ds-launch · OSS readiness · store legs |
| launch | release + P1 benchmark · ds-launch (store / web / library publish readiness) · ds-repo --oss-ready when `audience=public` · productize when `billing ≠ none` or paid intent | — |
| maintain | blueprint diff · ds-deps · ds-tune when a metric loop exists · ds-fix · ds-test | P1 benchmark · P3 simplify unless `size=large` · P5 chain · launch legs |

## Signal justification per skill

| Skill | Runs when (signal) | Otherwise |
|-------|--------------------|-----------|
| ds-blueprint | findings absent, stale (hash ≠ HEAD), lacking `Signals:`, or `--refresh-findings` | skipped (findings fresh at HEAD) |
| ds-review --strategic | `size ≠ small` | signal-absent — size=small (tactical pass covers it) |
| ds-review --tactical, ds-test, ds-fix | any source | signal-absent — no source |
| ds-backend | `api ≠ none` or `db ≠ none` | signal-absent — api=none, db=none |
| ds-frontend | `ui ∈ {web, desktop}` | signal-absent — ui=none |
| ds-mobile | `mobile ≠ none` | signal-absent — mobile=none |
| ds-compliance | `pii=yes` or `auth ≠ none` or `ui=web`; not when ds-mobile owns the overlapping scopes | signal-absent / project-type-exclusivity |
| ds-productize | `billing ≠ none` or paid intent (release/launch modes) | signal-absent — billing=none |
| ds-simplify | any source | — |
| ds-docs | any docs or README | — |
| ds-deps | maintain mode, or `stack` scope reports outdated majors | signal-absent — stack current |
| ds-devops | release/launch (`ci=none` is itself the finding) | mode-excluded |
| ds-deploy | release/launch and `deploy ∉ {none, store}` | signal-absent — deploy=none / store |
| ds-release | release/launch | mode-excluded |
| ds-repo | release/launch and (`public_repo ≠ no` or team signals) | signal-absent |
| ds-launch | launch and (`platforms ∩ {ios, android}` or `ui=web` with `deploy ≠ none` or `platforms=library`) | signal-absent |
| ds-repo --oss-ready | launch and `audience=public` or `public_repo=yes` | signal-absent — audience≠public |
| ds-benchmark | launch | mode-excluded |
| ds-tune | maintain and a `ds/tune/` loop or a measurable metric exists | signal-absent |

## Stage default order (within the legs the mode allows)

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

