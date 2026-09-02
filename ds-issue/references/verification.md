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

Core rule: [core execution loop](../../core/execution-loop.md) § Anti-sycophancy. Issue-specific addition: a `claimed-done-but-unproven` verdict is not softened to "done" because the issue is closed — the closed flag is a claim, the code is the evidence.

## Execution verification (`--do`)

The three checkpoints (root-cause re-verify, per-unit verify, aggregate verify), red proof, and gate mutation proof follow [core execution loop](../../core/execution-loop.md) §§1, 4-7 exactly — `/ds-build` runs them when present (SKILL.md Phase 6). This section carries only what ds-issue binds on top when `/ds-build` is absent and the loop runs inline:

- **Root-cause re-verify** — the recorded recipe lives in the body's Repro block (run it first; absent → derive one, per core §1); "already resolved" is judged against the Done set from requirement promotion; a stale verdict stops with what was read and why it no longer holds — the issue body is a claim, not ground truth.
- **Per-unit verify** — the unit's signal is the one named in the issue's Steps; callers re-checked are the impact-surface map's affected-set; an un-fixable blocker is recorded per [core principles §11](../../core/principles.md) (never "pre-existing" or "out of scope").
- **Red proof** — the observed failure and the observed pass both get pasted into the body's Done block, not just the terminal.
- **Gate mutation proof** — three gates in these repos passed while protecting nothing (a pin gate blind to half its family, a metadata gate reading its evidence from a comment line, 46 of 82 gates whose own correctness was never checked) — a gate never seen red is not known to work. Fix the gate before the issue closes.
- **Aggregate verify** — runs every row of the body's Gates table against its recorded baseline; a fix-type issue missing its red-proven regression test gets one added — `/ds-test` present → delegate; absent → write it inline — with its own red proof, before close.

### Close evidence — written into the body

The evidence goes in the body's `## Closure` block, not a comment ([github-features.md](github-features.md) § Body is the record) — the same shape [core execution loop §8](../../core/execution-loop.md) names for a GitHub issue. One addition: **the Done set is the body's Done list after requirement promotion**, so a promoted comment criterion is covered exactly like any body item, and an uncovered Done-set item keeps the issue open. A closure asserting "done" without a runnable signal is `claimed-done-but-unproven` — make it provable.
