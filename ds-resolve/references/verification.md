# Verification (ds-resolve)

Three checkpoints: **root-cause re-verify** (before any edit), **per-unit verify** (after each bounded unit), and **aggregate verify** (before close). All three judge from code/signals run this run — never from the issue text or a self-declared "done".

## Root-cause re-verify (Phase 2) [GATE]

An issue ages; the codebase moves under it. Confirm the problem still holds before touching anything.

1. **Read the cited anchors.** The `file:line` the issue points to still says what the issue claims? Symbol still there? Typed code → resolve with the language server first.
2. **Reproduce the symptom.** Trace the faulty path (bug), confirm genuine absence (missing feature, exhaustive search not memory), or confirm current ≠ expected (regression).
3. **Check it isn't already done.** Another change may have resolved it — read the change site, run the issue's Done-signal.
4. **Decide:**
   - Still open and reproduced → proceed to impact map.
   - Already resolved → close as completed with that evidence; skip implementation.
   - Stale (problem moved/gone, anchors don't match) → **stop**; report what you read and why it no longer holds. Do not fabricate a fix for a non-problem.

A triage/issue body is a claim, not ground truth — verify it (W1, W13). Stale-anchor recurrence is the exact failure this gate exists to stop.

## Per-unit verify (Phase 5)

Each bounded unit is proven the instant it completes, before the next starts:

1. Run the unit's named signal — the test it adds, the build, the lint, or an observed effect.
2. After modifying an interface, re-check the impact-map callers for that symbol (W2).
3. Signal red → fix within the unit before advancing; un-fixable in-unit → record a concrete blocker (API-contract change / cross-module scope / needs user knowledge / regulated change) and escalate. "Pre-existing" / "out of scope" are not blockers (W11).

Self-assessment is not proof — a signal must have passed.

## Aggregate verify (Phase 6) [GATE]

Per-unit greens can still compose into a red.

1. Run the full done-signal (the adapter's `doneSignal`, e.g. `npm run check`). Green required to close.
2. Fix-type issue → a regression test must exist for the fixed path; absent → add it before close (delegate generation if a test skill is available).
3. Re-read the diff: only task-required lines changed, no drive-by reformatting, affected-set callers intact.

Red aggregate → fix and re-run; never close on red.

## Close evidence (Phase 7)

The close comment proves done-ness from code, mirroring what `ds-issue --status` will independently re-verify:

- signals run + their result (`npm run check` green; `audit:X` green; new test name)
- the change site (`file:line` of the fix)
- the doctrine-lockstep note: which rule/ADR/SSOT row was added/extended/referenced, or "not needed: <reason>"

A close comment that asserts "done" without a runnable signal will be bucketed `claimed-done-but-unproven` by the status audit — so make it provable.
