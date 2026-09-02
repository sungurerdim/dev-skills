# Execution Loop — from a source of work to a code-proven close

**Consumers:** ds-build (primary executor — issues, `specs/*/tasks.md`, plain requests), ds-issue `--do` (inline fallback when ds-build is absent), ds-debug (the fix step), ds-freeze (implementing the kept set), ds-tune and ds-deps (per-batch verify).

Input: one unit of work with a stated done-signal. Output: the change, its evidence, and a disposition. The loop is the same whatever the source; only the intake step differs.

## 0. Intake — normalize the source

| Source | Done set | Verify contract |
|--------|----------|-----------------|
| GitHub issue | Body's Done list after comment-criteria promotion (each comment-borne criterion promoted into the body or rejected with a follow-up reference) | Body's Gates table with baselines; absent → measure now |
| `specs/{feature}/tasks.md` | Every unchecked task | Each task's `— verify:` command → expected signal |
| Plain request | Restated as `→ [goal] \| [files] \| done: [criteria]`; ambiguous done criteria → state the assumption in the summary | Stack-native `{check-cmd}` from `toolchains.md` |

A done-set item with no verify signal gets one before any edit; "looks right" is not a signal.

## 1. Re-verify root cause [GATE] — before any edit

1. Read the cited anchors — do they still say what the source claims? Symbol still present? Typed code → language server first.
2. Reproduce the symptom: run the recorded recipe; none → derive one (the faulty path for a bug; exhaustive search proving absence for a missing feature; current ≠ expected for a regression). **Observe the red.**
3. Check it is not already done — another change may have resolved it; run the done-signal.
4. Decide: still open + reproduced → continue; already resolved → close with that evidence, skip implementation; stale (anchors gone, problem moved) → **stop and report** what was read and why it no longer holds. Never fabricate a fix for a non-problem; the source is a claim, the code is the evidence.

## 2. Impact map [GATE]

Enumerate touched · linked · affected files across: callers/importers, implementors, configs and env vars, docs and examples, tests, generated artifacts. Each hazard is `affected — {path}` or `N/A — {reason}`. The explicit affected-set is what step 4 re-checks after every interface change.

## 3. Plan — bounded units

≤ ~5 files and ≤ ~25 tool calls per unit; each unit names the gap it closes and its verify signal; every done-set item maps to ≥ 1 unit (an unowned item means the plan is incomplete). Files exceed 2× the estimate → stop, report actual scope, re-confirm. `--preview` → write the plan and change nothing.

## 4. Implement + verify each unit

0. Checkpoint pre-gate before the first write (`checkpoint-protocol.md`).
1. Modify only task-required lines.
2. Run the unit's signal; self-assessment is not proof.
3. Interface changed → re-check the impact-map callers for that symbol.
4. Red → fix inside the unit, ≤ 3 attempts, same command each time; still red → revert the unit's files, record `reverted` with the captured error, continue with the next unit. Un-fixable in-unit → a concrete blocker (`principles.md` §11), never "pre-existing" or "out of scope".
5. Every detected error — in the unit's files or found on the way — gets a disposition.

**Budgeted backtracking** (hard problems): a unit that fails 3 attempts on one approach tries the next alternative; ≤ 3 alternatives per unit; all exhausted → mark the unit `blocked` with the recorded root causes and their shared pattern, and re-plan the affected units rather than retrying the same tactic. Every failed attempt records `{approach} failed because {root cause}` — the next alternative addresses the cause or states why it is exempt.

## 5. Red proof — fix-type work [GATE]

1. Write the regression test against the **unfixed** code; run it; it must fail — paste the failure.
2. Apply the fix; run the same test; paste the pass.
3. A test that was never red does not exercise the bug — rewrite it; do not proceed.

## 6. Gate mutation proof — gate-adding work [GATE]

1. Introduce the realistic deviation the gate exists to catch (the actual drift, not a syntax error).
2. Run the gate; it must go red — paste the output.
3. Revert the deviation; re-run; paste the green.
4. Stayed green → the gate is blind; fix the gate before closing.

## 7. Aggregate gate — Mechanical Done Gate [GATE]

`{check-cmd}` resolution (once, at setup): ds-quality enforcement arm installed → its gate command; else stack-native format + lint + type + test from `toolchains.md` (tests alone are not the gate); none detectable → Verification-Infrastructure Gap: report it, offer `/ds-quality`, record the decision — never silently skip. Capture the baseline before the first change; baseline red → done condition is "no *new* red", reported red-at-baseline.

Before close: run the full `{check-cmd}` once (per-unit greens compose into reds); run every recorded gate row against its baseline; fix-type → the red-proven regression test exists; re-read the diff — task-required lines only, no drive-by reformatting, affected-set callers intact. New red → fix and re-run ≤ 3 attempts, then revert the offending unit and record `red`; never close red.

## 8. Close — evidence written into the record, then closed

| Record | Where the evidence goes |
|--------|------------------------|
| GitHub issue | The **body** (never a comment): each Done item ticked with its observed output; a `## Closure` block — one evidence line per done-set item (signal run + result + `file:line`), each gate row's command → output vs baseline, the doctrine note (rule/ADR/SSOT row added, or "not needed: reason"); `Handoffs — Deferred to #K` lines with the counterpart written into `#K` in the same run; a dated `## Log` line. Then `gh issue close --reason completed`. |
| `tasks.md` | Each task ticked with its verify output on the same line; the file is deleted when every task is ticked (the commits are the record). |
| Plain request | The Outcome Report (`report-and-outcome-templates.md` §5) with the verify-echo. |

An uncovered done-set item, a one-sided handoff, or a gate row below baseline keeps the record open. A closure asserting "done" with no runnable signal is `claimed-done-but-unproven` — make it provable instead.

## Anti-sycophancy

A reproduced symptom stays reproduced under "are you sure?" — withdraw it only on evidence (a fresh read, a passing run), never on assertion. A closed flag is a claim; the code is the evidence.
