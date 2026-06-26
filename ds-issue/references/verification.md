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
