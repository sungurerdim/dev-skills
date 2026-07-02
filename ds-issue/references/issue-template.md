# Issue body template + priority rubric + self-check (ds-issue)

## Body template (conditional blocks)

Fill only the blocks the issue needs — a one-line fix issue keeps Problem + Done; a feature keeps all. Forbidden: prose that restates the title, "context"/"background" filler, speculative scope, dead anchors.

```markdown
## Problem / root cause
<what + why, with anchors verified this run: `path:line`>

## Evidence / repro               <!-- required for fix-type: the Phase-3 reproduction, captured -->
- Repro: <exact command / steps that show the symptom>
- Observed: <what happens> · Expected: <what should happen>
- Anchors: <false-positive-gate verdicts: confirmed @ path:line>

## Scope
- In: <what this issue changes>
- Non-goals: <explicitly out — prevents scope creep>   <!-- always include -->

## Steps                          <!-- omit for a trivial one-line fix -->
<concrete steps; each closes a named gap and carries `— verify: <command> → <expected>`; steps map 1:1 to `--do` bounded units>

## Impact surface                 <!-- include when the change touches shared interfaces/sync/schema -->
<callers / consumers / sync paths / schema / i18n / a11y / compliance likely affected — every entry anchored (read this run); intake hints only, re-derived fresh at `--do`>

## Done (machine-checkable)
- [ ] <criterion — behavioral (feat/fix) criteria as EARS sentences: `WHEN / IF … THE SYSTEM SHALL …`> → <signal: command → expected>
- [ ] regression test added       <!-- required for fix-type issues -->
- [ ] <project done-signal> green  <!-- e.g. the adapter's doneSignal command -->

## Doctrine lockstep               <!-- include when the project tracks rules/ADRs -->
<Add new rule · Extend rule/ADR #N · Reference existing · Not needed: "<reason>">

## Suggested execution
Agent: <none | search | general | architect> · Capability tier: <fast | mid | top> · Why: <…>
```

Map the abstract capability tier to a concrete model via the project adapter or host convention; the generic body stays tool-neutral. Security/payments/crypto/migration work → always top tier + a line-by-line-review note.

## Priority rubric (exactly one)

| Priority | When |
|----------|------|
| **P1** | Launch-blocker · data loss · security · false legal/compliance claim |
| **P2** | User-facing correctness or quality — wrong behavior, broken UX, missing expected feature |
| **P3** | Polish — style, minor DX, nice-to-have |

Uncertain between two → pick the lower (W5).

## Type (exactly one)

From the adapter's taxonomy; absent → conventional-commit types: `feat` (user can do something new) · `fix` (broken thing now works) · `refactor` (behavior unchanged) · `docs` · `chore` · `test` · `ci` · `tooling`. CI/docs/test/tooling are never `feat`/`fix`.

Optional status label: `needs-decision` (owner call required) · `blocked` (state `Blocked by #N` in body).

## Self-check gate (Phase 4, before create)

Every box must be yes — otherwise revise, don't create:

- [ ] Every `file:line`/symbol/version in the body was read this run (no memory claims)
- [ ] Dedup sweep ran over **all** states + history; candidate is net-new or has a disposition
- [ ] Symptom reproduced (or confirmed pure-decision)
- [ ] Done is machine-checkable (a command/audit/observed effect — not "looks good"); every signal states command → expected
- [ ] Behavioral (feat/fix) Done criteria are EARS sentences — expected behavior unambiguous without reading the executor's mind
- [ ] Fix-type issue carries the Evidence/repro block (the false-positive-gate reproduction, not a paraphrase)
- [ ] Every Steps entry carries a `— verify:` signal
- [ ] Non-goals present; no scope creep
- [ ] Fix-type issue has a regression-test Done item
- [ ] Exactly 1 type + 1 priority (+ status only if it applies), all from the live label set
- [ ] No verbose/dead content; nothing restates the title
- [ ] Estimate within the bounded-task threshold, or split into sub-issues
- [ ] User confirmed the draft
