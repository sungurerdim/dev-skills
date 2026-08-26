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

**Output:** a one-line verdict per anchor (`confirmed @ path:line` / `stale — code reads X` / `not found`) and an overall reproduced / not-reproduced / pure-decision. A successful reproduction is **captured as a recipe** (exact command/steps + observed vs expected + anchor verdicts) and written into the body's Repro block — the evidence that justified creating the issue is the same evidence the executor re-runs at `--do`, not a discovery to repeat.

## Current state vs target state (intake) [GATE]

These are two different claims and the body keeps them in two different blocks. Collapsing them is how an issue ends up describing a wish as if it were a finding.

| Block | Claim | Standard of proof |
|-------|-------|-------------------|
| Current state | what the code does **today** | `file:line` read this run, or a command with its observed output pasted |
| Target state | what will be true when the issue is done | observable — a command that will print something different, or an effect someone can see |
| Delta | Target − Current | derived from the two above; every Step and every Done item traces to one Delta line |

A Current-state line with no anchor and no command output is an assertion, not a finding — re-read the code or drop the line. A Target-state line that cannot be checked from outside the implementer's head ("the module is cleaner") is not a target — restate it as the signal that would change.

## Gate baselines (intake) [GATE]

Every gate the issue names is **run at intake** and its output recorded as the baseline, before any work starts. Without the baseline the executor cannot answer the only question that matters when a gate goes red: *was it already red?* An inherited red silently becomes the executor's problem, or worse, gets reported as caused-by-this-change.

Record command, expected string, and the value observed today, with the date. A gate that cannot be run at intake (needs a credential, needs hardware) is recorded as `baseline unmeasured — <reason>`, never as green.

## Done-from-code audit (Phase 5, `--status`)

For each open + recently-closed issue, prove done-ness from the codebase — never from the closed flag or a "done ✅" comment.

1. **Read the issue's Done block and its Gates table.** They list machine-checkable signals (a command, an audit, a test) with expected values and baselines. No machine-checkable Done, or a closed issue with no `## Closure` block → it cannot be verified → bucket `claimed-done-but-unproven`. A criterion or decision found only in a comment is a body defect: record it, and promote it into the body at the next `--do`.
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
2. Reproduce the symptom — body carries an Evidence/repro recipe → run it first; absent → derive one (faulty path for a bug; genuine absence by exhaustive search for a missing feature; current ≠ expected for a regression).
3. Check it isn't already done — another change may have resolved it; read the change site, run the Done-signal.
4. Decide: still open + reproduced → proceed to impact map; already resolved → close as completed with that evidence, skip implementation; stale (anchors don't match, problem moved/gone) → **stop**, report what you read and why it no longer holds. Never fabricate a fix for a non-problem. The issue body is a claim, not ground truth.

### Per-unit verify (after each bounded unit)

1. Run the unit's named signal — the test it adds, the build, the lint, an observed effect. Self-assessment is not proof.
2. After modifying an interface, re-check the impact-map callers for that symbol.
3. Signal red → fix within the unit before advancing; un-fixable in-unit → record a concrete blocker (API-contract change / cross-module scope / needs user knowledge / regulated change) and escalate. "Pre-existing" / "out of scope" are not blockers.

### Red proof (fix-type) [GATE]

A regression test written after the fix proves the code compiles, not that the bug is caught. The order is fixed:

1. Write the test against the **unfixed** code. Run it. It must fail — paste the observed failure into the body's Done block.
2. Apply the fix. Run the same test. Paste the observed pass.
3. The test never went red → it does not exercise the bug. Rewrite it; do not proceed.

### Gate mutation proof (gate-adding issues) [GATE]

An issue that adds or changes a mechanical gate proves the gate can go red. Three gates in these repos passed while protecting nothing — a pin gate blind to half its family, a metadata gate reading its evidence from a comment line, 46 of 82 gates whose own correctness was never checked. A gate never seen red is not known to work.

1. Introduce the realistic deviation the gate exists to catch — not a syntax error, the actual drift.
2. Run the gate. It must go red — paste the output.
3. Revert the deviation (`git checkout -- <files>`), re-run, paste the green.
4. Gate stayed green through step 2 → the gate is blind. Fix the gate before the issue closes.

### Aggregate verify (before close) [GATE]

1. Run every row of the body's Gates table — green required, and no row below its recorded baseline; per-unit greens can compose into a red.
2. Fix-type issue → the red-proven regression test exists for the fixed path; absent → add it (delegate to ds-test) with its red proof before close.
3. Re-read the diff: only task-required lines, no drive-by reformatting, affected-set callers intact. Red aggregate → fix and re-run; never close red.

### Close evidence — written into the body

The evidence goes in the body's `## Closure` block, not in a comment ([github-features.md](github-features.md) § Body is the record). It proves done-ness from code, mirroring what a later `--status` audit re-verifies independently:

- **One evidence line per Done-set item** — the Done set is the body's Done list *after* requirement promotion, so promoted comment criteria are covered like any body item. Each line: the signal run + its observed output + the change site `file:line`. A Done-set item without its evidence line is uncovered, and an uncovered item means the issue does not close.
- Each Gates row: command → observed output, against its baseline.
- The doctrine-lockstep note (which rule/ADR/SSOT row added/extended/referenced, or "not needed: <reason>").
- A `## Log` line dated with the closure.
- Any item that did **not** get done and moved elsewhere → a `## Handoffs — Deferred to #K` line, and the same line written into `#K`'s body in the same run. A deferral recorded on one side only is a dropped item.

A closure asserting "done" without a runnable signal will be bucketed `claimed-done-but-unproven` — so make it provable.
