# Rules: Release Scope Triage

Supporting detail for [SKILL.md](../SKILL.md): the full flag-gating table, error recovery, and edge cases. Loaded when a flag combination, failure, or boundary condition needs the exact behavior.

## Table of Contents

| Section | Line |
|---------|------|
| **Flag-Gate Contract** | ~12 |
| **Error Recovery** | ~26 |
| **Edge Cases** | ~36 |

---

## Flag-Gate Contract

Every flag's effect on phase execution, stated in full — no phase runs unless this table allows it.

| Flag | Phases enabled | Phases disabled |
|------|-----------------|-------------------|
| (none) — default | 1–7, every decision resolved by best judgment and recorded | — |
| `--ask` | 1–7, with menus/questions at every decision point | — |
| `--preview` | 1–2 only | 3–7 |
| `--skip-implement` | 1–4, 6–7 | 5 (Implement Kept Set) |
| `--resume={#N}` | 1 re-reads the tracking issue instead of starting fresh; 2–7 unchanged | — |
| `--milestone={name}` | modifier only — labels the manifest in Phase 1 step 2; no phase gating | — |
| `--scope={area}` | modifier only — restricts Phase 2's candidate set; no phase gating | — |

---

## Error Recovery

| Situation | Action |
|-----------|--------|
| Flag-gate delegate (ds-backend/ds-frontend/ds-review) unavailable | Default: falls back to the advisory-handoff pattern used elsewhere (inline-patch a bounded gate if one is safely reachable this run, else gap-note); never silently ships an item marked `defer-hidden`. `--ask`: escalate the `defer-hidden` item to the user — ship as-is or manual gate instruction. |
| `gh` unavailable for the whole run | Fall back to `docs/release/{milestone}-scope.md` tracking file end to end; Milestone check (Phase 4 step 1a) is skipped, labels-only if issues are still filed |
| Delegated implementation (`/ds-build` or `/ds-issue --do #N`) fails | Record `failed` with the blocker, continue to the next item, never mark a `ship` item done without evidence |

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| User defers everything | Manifest still written; report `Ship: 0` and flag WARN — an empty release scope is a signal, not silently accepted |
| Item spans multiple domains | List once under its primary domain, cross-reference the others in its description |
| `defer-hidden` item has no clean flag point (tightly coupled) | Default: resolves automatically to the least-invasive hide (route/nav removal) — respects the triage disposition; not on the irreversible-exception list, so never left `only you can do`. `--ask`: escalate as `needs-approval` — least-invasive hide (route/nav removal) or leave as `ship`, never silently leave it exposed. |
| `/ds-issue --do --all`-style bulk implementation requested | Not supported — Phase 5 runs the ship set one kept item at a time (`/ds-build`, then `/ds-issue --do #N`, then the inline loop); a curated subset, not the whole backlog |
