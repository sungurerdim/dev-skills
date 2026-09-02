# Rules: Release Scope Triage

Supporting detail for [SKILL.md](../SKILL.md): error recovery and edge cases. Loaded when a failure or boundary condition needs the exact behavior.

## Table of Contents

| Section | Line |
|---------|------|
| **Error Recovery** | ~12 |
| **Edge Cases** | ~22 |

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
