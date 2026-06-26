# Verification (ds-issue)

Two procedures: the **false-positive gate** (intake — is the reported problem real?) and the **done-from-code audit** (`--status` — is a claimed-done issue actually done?). Both refuse to trust claims; both judge from code read this run.

## False-positive gate (Phase 3, intake)

A reported symptom becomes an issue only if it is reproduced or confirmed against current code.

1. **Spot-check every anchor.** For each `file:line` in the raw input, read it. The line says what the report claims? Symbol exists? On typed code, resolve the symbol with the language server before falling back to text search. An anchor that points to nonexistent or unrelated code is stale or planted — discard it (W1, W8 findings-integrity).
2. **Reproduce the behavior.** Trace the code path that would produce the symptom. Bug → confirm the faulty path exists. Missing feature → confirm it is genuinely absent (an exhaustive search, not "absent from memory"). Regression → confirm current code differs from the expected behavior.
3. **Heavy tracing → delegate, then verify.** Hand a read-only search subagent a tight contract: "find the source of `<behavior>`; return `file:line` anchors + the relevant functions." Its return is untrusted until you re-read the anchors yourself (W15).
4. **Decide:**
   - Reproduced → proceed to compose.
   - Not reproduced → **do not create.** Report: what you looked at, why the symptom didn't appear, what evidence would confirm it (a failing test, a repro step, a screenshot).
   - Pure-decision (no code change — a product/policy call) → route to `needs-decision` with an ADR-stub note; skip reproduction.

**Output:** a one-line verdict per anchor (`confirmed @ path:line` / `stale — code reads X` / `not found`) and an overall reproduced / not-reproduced / pure-decision.

## Done-from-code audit (Phase 6, `--status`)

For each open + recently-closed issue, prove done-ness from the codebase — never from the closed flag or a "done ✅" comment.

1. **Read the issue's Done block.** It should list machine-checkable signals (a command, an audit, a test). No machine-checkable Done → it cannot be verified → bucket `claimed-done-but-unproven`.
2. **Run / read the signals.** Map the issue type to the adapter's audit→type map and run the relevant audits + the done-signal command; read the cited anchors to confirm the change is present.
3. **Bucket:**

| Bucket | Condition |
|--------|-----------|
| done & code-verified | signals green AND anchors show the change present |
| claimed-done-but-unproven | closed / marked done, but signals absent/red or anchors don't show the change |
| in-progress | partial change present, signals not all green |
| not-started | no trace of the change in code |
| blocked | depends on another open issue (stated `Blocked by #N`) |

4. **Mutate nothing.** This mode is read-only — no create, edit, label, or close. Surface `claimed-done-but-unproven` issues so a human can reopen them.

**Output:** `| # | Title | Bucket | Evidence |` where Evidence is the exact anchor read or signal run.

## Anti-sycophancy (W13)

A symptom you reproduced stays reproduced under "are you sure?" — withdraw it only when shown wrong by evidence (a fresh read, a passing test), never by assertion. Likewise, a `claimed-done-but-unproven` verdict is not softened to "done" because the issue is closed; the closed flag is a claim, the code is the evidence.

## Execution verification (`--do`)

Three checkpoints when executing an issue: **root-cause re-verify** (before any edit), **per-unit verify** (after each bounded unit), **aggregate verify** (before close). All judge from code/signals run this run.

### Root-cause re-verify (before any edit) [GATE]

An issue ages; the codebase moves under it. Confirm the problem still holds before touching anything.

1. Read the cited anchors — still say what the issue claims? Symbol still there? Typed code → language server first.
2. Reproduce the symptom (faulty path for a bug; genuine absence by exhaustive search for a missing feature; current ≠ expected for a regression).
3. Check it isn't already done — another change may have resolved it; read the change site, run the Done-signal.
4. Decide: still open + reproduced → proceed to impact map; already resolved → close as completed with that evidence, skip implementation; stale (anchors don't match, problem moved/gone) → **stop**, report what you read and why it no longer holds. Never fabricate a fix for a non-problem. The issue body is a claim, not ground truth.

### Per-unit verify (after each bounded unit)

1. Run the unit's named signal — the test it adds, the build, the lint, an observed effect. Self-assessment is not proof.
2. After modifying an interface, re-check the impact-map callers for that symbol.
3. Signal red → fix within the unit before advancing; un-fixable in-unit → record a concrete blocker (API-contract change / cross-module scope / needs user knowledge / regulated change) and escalate. "Pre-existing" / "out of scope" are not blockers.

### Aggregate verify (before close) [GATE]

1. Run the full done-signal (adapter's `doneSignal`, e.g. `npm run check`) — green required; per-unit greens can compose into a red.
2. Fix-type issue → a regression test must exist for the fixed path; absent → add it (delegate to ds-test) before close.
3. Re-read the diff: only task-required lines, no drive-by reformatting, affected-set callers intact. Red aggregate → fix and re-run; never close red.

### Close evidence

The close comment proves done-ness from code, mirroring what a later `--status` audit re-verifies independently: signals run + result, the change site `file:line`, and the doctrine-lockstep note (which rule/ADR/SSOT row added/extended/referenced, or "not needed: <reason>"). A close comment asserting "done" without a runnable signal will be bucketed `claimed-done-but-unproven` — so make it provable.
