---
name: ds-debug
description: Bug hunter — reproduce the failure as an observed red, localize it (bisect, logs, tracing), test at most three hypotheses, land the minimal fix behind a red-proven regression test, and prove it with the project's own check. Use when something is broken and the cause is not yet known.
---

# /ds-debug

"Fix the bug" without a reproduction produces a plausible edit that fixes nothing, a test written after the fact that never went red, and a second incident a week later. This skill starts from an observed failure, narrows it mechanically, tries at most three hypotheses, and ships the smallest fix that turns the regression test from red to green.

**Bug Hunter** — reproduce → localize → hypothesize (≤ 3) → minimal fix → red-proven regression test → done gate.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-debug`
- User reports a failure: "this test fails", "X returns the wrong value", "it crashes when…", "fix bug #N"
- A ds-build unit stays red after its approaches are exhausted and hands the diagnosis here
- CI or a check is red and the cause is unknown

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "why does parseMoney('1,234') return NaN — fix it" | "review the code for bugs in general" (→ ds-review) |
| "the test suite went red after the last commit" | "make the tests pass" by editing assertions (never — that is test weakening) |
| "reproduce and fix issue #7" | "implement feature #8" (→ ds-build) |
| "flaky test in CI" | "optimize this slow function" (→ ds-review --perf or ds-tune) |
| "crash on startup in production" | "set up error monitoring" (→ ds-deploy) |

## Contract

**Dimensions:** none (carrier)

- Fixes the observed failure and nothing else; unrelated defects found on the way become findings with a disposition, never silent edits.
- Standalone. Reads the repo, its tests, logs and git history; web lookups only under `--research` (ds-research when present, inline search otherwise), each fact cited.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **The red comes first.** No edit before the failure is reproduced by a command whose output is pasted; a report that cannot be reproduced ends as `not reproduced` with what was tried — never as a speculative fix.
- **Tests are never weakened.** The regression test asserts the intended behavior from the report; an existing test that encodes the bug is corrected to the intended behavior and the change is stated. Assertion strength, expected values and coverage of the failing path never shrink.
- **Checkpoint** ([../core/checkpoint-protocol.md](../core/checkpoint-protocol.md)): `git status --porcelain` before the first write; a dirty path the fix would touch → `needs-human` (commit or stash first); experiments are reverted per file with `git checkout -- {file}`, never a tree-wide reset. `git bisect` runs only on a clean tree and always ends with `git bisect reset`.
- **Mechanical Done Gate:** `{check-cmd}` (ds-quality arm when installed, else the stack-native chain from [../core/toolchains.md](../core/toolchains.md)) captured at baseline, re-run after the fix and once before close; new red → fix ≤ 3 attempts, then revert and record; baseline red reported red-at-baseline; no tooling → Verification-Infrastructure Gap surfaced.
- **Hypothesis budget:** at most three hypotheses, each with a prediction, the test that would falsify it, and the observed result; a fourth is not tried — the run reports the three falsifications and stops with options.
- Publishing (push, PR, release) is never done here — `needs-human` with the command ([../core/ask-exception-list.md](../core/ask-exception-list.md)). State-exempt: the failing test, the commit and the issue are the durable record.

## Arguments

| Flag | Effect |
|------|--------|
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `needs-human`. |
| `--issue=#N` | Take the bug report from a GitHub issue (`gh issue view N`); the fix commit references it and the closure evidence is written into the body |
| `--test={id}` | Start from a named failing test instead of a report |
| `--bisect` | Force `git bisect run {signal}` for localization when a last-known-good commit exists (default: bisect only when the red is newer than the last tag or the report names a regression) |
| `--research` | Allow web lookups for library/platform behavior (ds-research when present; inline otherwise); default off |
| `--preview` | Reproduce + localize + hypotheses; no fix, no test written |

Without flags: reproduce, localize, fix, test, gate, commit locally — every choice by best judgment and recorded. `--ask`: confirm the reproduction recipe, the chosen hypothesis and the fix before it lands.

## Delegation

**Owns:** debugging, root-cause | **Delegates:** ds-test → regression test red-proof when a test suite exists (absent → inline test in the project's runner, red pasted); ds-commit → the fix commit (absent → inline `git commit -m "fix({scope}): {what} (#N)"`); ds-research → `--research` lookups (absent → inline search, cited) | **Receives:** ds-build → a unit whose signal stays red after its approaches; ds-issue → bug-type issue execution

## Execution Flow

Reproduce → Localize → Hypothesize → Fix → Regression test → Done gate → Close → Summary

### Phase 1: Reproduce [GATE]

1. Read the report (`--issue`, `--test`, or the request): expected vs observed, the input, the environment.
2. Derive a reproduction command: an existing failing test (`{runner} {test}`), a one-line script against the function (`node -e`, `python -c`, `go test -run`), or the app's failing path. Run it. **Paste the red output.**
3. Not reproducible → try the report's exact input and environment (Node/Python version, locale, timezone, OS path separators) once each; still green → status `not reproduced`, list what was tried, stop before any edit.
4. Resolve `{check-cmd}` and capture the baseline; run the Checkpoint pre-gate.

**Gate:** A command whose observed output shows the failure. If fails → `not reproduced` reported with the attempts and the environment differences; `--ask` → ask for the missing input; default → `needs-human: provide a reproducing input or environment`.

### Phase 2: Localize

| Signal available | Method |
|------------------|--------|
| Red is newer than a known-good commit or tag | `git bisect start && git bisect bad && git bisect good {ref} && git bisect run {reproduction command}` → the first bad commit; then `git bisect reset` |
| Stack trace / error message | Walk the trace to the first frame inside the repo; read ±30 lines |
| Wrong value, no trace | Add temporary structured logging (or a debugger breakpoint) at the boundaries of the suspect path; remove it before the fix commit |
| Flaky | Run the test 3× isolated and 1× with shuffled order; a pass/fail split → shared state, time, ordering or network dependence — record which |
| Environment-dependent | Diff the two environments (versions, locale, TZ, path separators, line endings); reproduce in the failing one |

Record the localized site as `file:line` plus the mechanism (what the code does vs what the report expects).

**Gate:** A `file:line` site and a mechanism statement. If fails → site not found within the report's path → widen to callers of the failing symbol once; still unknown → hypothesize directly on the observed values (Phase 3) with the localization gap recorded.

### Phase 3: Hypothesize (≤ 3)

For each hypothesis: `H{n}: {cause} → predicts {observable}; falsified by {command}; result: {observed}`. Test the cheapest falsification first. A hypothesis that survives its falsification test is the working cause; three falsified → stop, report the three with their evidence, propose 2–3 next options (`--research` when off, a maintainer question, a deeper bisect) — never a fourth guess.

**Gate:** One surviving hypothesis with its evidence, or a recorded three-strike stop. If fails → contradictory evidence between two hypotheses → re-run both falsification commands on a clean tree and record the raw outputs.

### Phase 4: Minimal fix

1. Write (or correct) the regression test first, asserting the intended behavior from the report; run it → **paste the red**.
2. Apply the smallest change at the localized site that makes the test green without changing unrelated behavior; no drive-by refactor, no formatting of untouched code.
3. Run the regression test → paste the green; run the touched-scope `{check-cmd}`.
4. Remove temporary logging/breakpoints; `git diff` shows only the fix and the test.

**Gate:** Regression test observed red then green; touched-scope check green; diff minimal. If fails → the fix needs an interface change → record the impact (callers, configs) and treat it as a bounded unit with the same signals; a broader change is warranted → stop and hand the plan to ds-build with the diagnosis.

### Phase 5: Done gate + Close

1. Full `{check-cmd}` once → green (or no new red vs a red baseline); new red → fix ≤ 3 attempts, then revert the fix and record `reverted` with the error.
2. Commit locally (`fix({scope}): {what} (#N)` when an issue exists) via ds-commit or inline; hooks are never bypassed.
3. `--issue` → write the evidence into the body (reproduction command + red, fix `file:line`, regression test red→green, `{check-cmd}` output) and close it with `gh issue close --reason completed` (`--ask` confirms).
4. Related defects noticed on the way → findings with a disposition (`fixed inline` when same-file and trivial, else `filed`/`needs-human`), never silent edits.

**Gate:** Aggregate green, commit present, record written. If fails → hook rejects the commit → fix what it names and retry (≤ 3); `gh` unavailable → print the closure block for manual paste.

### Phase 6: Summary

```
ds-debug: {OK|WARN|FAIL} | Reproduced: {yes|no} | Cause: {file:line — mechanism} | Hypotheses: {tried}/3 | Fix: {commit} | Regression test: {red→green | absent} | Needs-human: {n}
```

Then the verify-echo (reproduction command + red, test red→green, `{check-cmd}` output), `Decided without asking` lines, every `needs-human` item in full ([../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md)). Status: OK (fixed + red-proven + gate green), WARN (fixed but a related finding or a flaky-quarantine remains), FAIL (not reproduced, three hypotheses falsified, or gate red).

**Gate:** Summary printed with the outputs. If fails → any output missing → re-run that command and paste it.

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `Bug {id} fixed at {file:line} and pinned by a test that was seen failing first — the same failure cannot ship again unnoticed`
- `Root cause localized to commit {hash} by bisect in {n} steps — the fix touched {n} lines, not a rewrite`
- `Flaky test traced to {shared state | ordering | time} — quarantined with a linked issue instead of a retry loop`

Zero-change run: `Not reproduced — {attempts}; no edit made`.

## Quality Gates

- No edit before an observed red; no "done" before an observed green on the same test and the aggregate check
- Assertions, expected values and the failing path's coverage never shrink
- Temporary instrumentation is gone before the commit (`git diff` is fix + test only)
- W9: state-exempt — the failing test, the commit and the issue are the durable record. W10: a fresh `ds/audit/findings.md` row for the same site is consumed as context, never re-detected. W13: a reproduced failure stays reproduced under "are you sure?" — withdrawn only on evidence.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| No test runner in the repo | Reproduce with a one-line script in the project's language; the regression test uses the runner from `../core/toolchains.md` § the stack's section (zero-dependency runner when none is installed) |
| `git bisect` cannot run (dirty tree, shallow clone) | Skip bisect, localize by trace/logging, record `bisect: unavailable — {reason}` |
| Fix requires a credential or a production-only input | `needs-human` with the exact question; the diagnosis and the test are still committed |
| Same failure after the fix in a second environment | Re-open Phase 1 in that environment; the first fix stays, the second cause gets its own hypothesis budget |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Report describes intended behavior that contradicts an existing test | Treat the existing test as the suspect: verify against docs/spec; correct the test only with that evidence stated |
| Bug is in a dependency | Pin or upgrade with a changelog citation (ds-deps when present); a local patch is `needs-human` |
| Heisenbug (vanishes under instrumentation) | Use non-invasive signals (exit codes, file outputs, timing) and record the instrumentation effect |
| Multiple independent bugs in one report | One reproduction + fix cycle per bug, each with its own regression test and commit |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
