# Issue body templates + rubrics + self-check (ds-issue)

**The body is the issue.** Every decision, criterion, gate, deferral and scope change lives in the body and is written there with `gh issue edit --body-file -`. A comment is not a place to put information (see [github-features.md](github-features.md) § Body is the record). Three templates follow: standard · epic · sub-issue.

**Body language** follows the repo's existing issue and commit language — read one recent issue before composing. The heading names below are the English default; translate the headings, keep the block set.

**Self-contained brief.** Another agent, with no access to this conversation, opens the issue and works it. Everything that agent needs is in the body: what is true today with `file:line` proof, what must be true when done, which commands prove it, and what their values are before the work starts. A body that requires reading a comment, a sibling issue, or a chat log to act on is incomplete.

## Standard body template (conditional blocks)

Fill only the blocks the issue needs — a one-line fix keeps Current/Target/Done/Gates; a feature keeps all. Forbidden: prose restating the title, "context"/"background" filler, speculative scope, dead anchors.

````markdown
## Current state                  <!-- what is true in the code TODAY -->
- <fact> — `path:line` (read <date>)
- <fact> — `command` → `<observed output>`

## Target state                   <!-- what is true when this is done — observable -->
- <statement an outsider can check by running something or seeing an effect>

## Delta                          <!-- Target − Current = the work; one line per gap -->
- <gap 1> · <gap 2>

## Repro                          <!-- required for fix-type: the Phase-3 reproduction, captured -->
- Command: <exact command / steps>
- Observed: <what happens> · Expected: <what should happen>
- Anchors: confirmed @ `path:line` · <verdict per anchor>

## Scope
- In: <what this issue changes>
- Non-goals: <explicitly out>          <!-- always include -->

## Steps                          <!-- omit for a trivial one-line fix; map 1:1 to `--do` units -->
1. <step> — verify: `<command>` → `<expected>`

## Gates                          <!-- always include; the machine checks that decide done -->
| Gate | Command | Expected | Baseline (measured <date>) |
|------|---------|----------|-----------------------------|
| test suite | `npm test` | `Tests 5908 passed` | `5908 passed, 0 failed` |
| audits | `npm run audit:all` | `all 88 passed` | `88 passed` |
| mutation | `node scripts/audit-mutation-test.mjs` | `103/103` | `103/103` |

## Done (machine-checkable)
- [ ] <criterion — behavioral (feat/fix) as EARS: `WHEN / IF … THE SYSTEM SHALL …`> → `<command>` → `<expected>`
- [ ] regression test red before the fix, green after   <!-- fix-type: required, both outputs pasted below -->
- [ ] every Gates row green, no row below its baseline

## Open decision                  <!-- include while an owner call blocks progress -->
- Question: <the one thing that cannot be decided from the code>
- Options: **A** <what it is> — <consequence> · **B** <what it is> — <consequence>
- Recommendation: <A|B> — <reason>
- **Resolved <date>: <chosen option> — <reason>.**   <!-- written HERE on decision, never in a comment -->

## Handoffs                       <!-- include when work crosses an issue boundary -->
- Received from #<M>: <item> — <why it landed here>
- Deferred to #<K>: <item> — <why it left>          <!-- the same line must exist in #K's body -->

## Dedup evidence                 <!-- the search that was actually run, with its real output -->
```
$ gh issue list --repo <slug> --state all --limit 1000 --json number --jq 'length'
7
$ gh search issues "<keywords>" --repo <slug> --limit 1000 --json number,title,state
[]
```
Verdict: net-new — no open or closed issue covers <topic>.

## Impact surface                 <!-- include when the change touches shared interfaces/sync/schema -->
<callers / consumers / sync paths / schema / i18n / a11y / compliance likely affected — every entry anchored (read this run); intake hints only, re-derived fresh at `--do`>

## Doctrine lockstep               <!-- include when the project tracks rules/ADRs -->
<Add new rule · Extend rule/ADR #N · Reference existing · Not needed: "<reason>">

## Suggested execution
Agent: <none | search | general | architect> · Capability tier: <fast | mid | top> · Why: <…>

## Closure                        <!-- written into the body at close, not posted as a comment -->
- Closed <date> as <completed | not planned>.
- Evidence, one line per Done item: <item> → `<command>` → `<observed output>` @ `path:line`
- Superseded by #<K>.             <!-- only when the scope changed out from under this issue -->

## Log                            <!-- append-only; newest last -->
- <date> opened — <one line>
- <date> scope cut: <what left, to where>
- <date> closed: <reason + the evidence block below>
````

Map the abstract capability tier to a concrete model via the project adapter or host convention; the generic body stays tool-neutral. Security/payments/crypto/migration work → always top tier + a line-by-line-review note.

### Why the body carries a Log

The issue body is not versioned in any read an agent performs. `gh issue view <n> --json body` returns the current text and nothing else; the edit history exists only behind a separate GraphQL call that returns raw diffs, not reasons:

```bash
gh api graphql -f query='query{repository(owner:"<owner>",name:"<repo>"){issue(number:<n>){userContentEdits(first:20){totalCount nodes{editedAt diff}}}}}'
```

Nobody reads that during work, and a diff does not say *why*. So the body carries its own change record: one dated line per material change — scope cut, decision resolved, item deferred, closure. Cosmetic rewording gets no line.

## Epic template (multi-step work)

An epic owns **the whole's state and the binding order**. It never restates a sub-issue's steps, gates, or Done list — that duplication is what goes stale. A sub-issue never restates the epic's rationale beyond one context sentence.

```markdown
> **Epic.** Sub-issues carry the work. This body carries the whole's state and the order.

## Whole: current state
- <what is true across the whole surface today> — `path:line`
- Progress: <n>/<N> sub-issues closed (`gh issue view <n> --json subIssuesSummary`)

## Whole: target state
- <what is true when every sub-issue is closed — observable at the whole level>

## Sub-issues, in binding order
1. #<A> — <title> — no prerequisite
2. #<B> — <title> — **after #A** (<why the order binds: shared interface / migration ordering>)
3. #<C> — <title> — **after #A** (parallel with #B)

## Whole-level gates                <!-- only what no single sub-issue can satisfy alone -->
| Gate | Command | Expected | Baseline (measured <date>) |
|------|---------|----------|-----------------------------|
| full suite | `tool/pre_commit.sh` | `9/9` | `9/9` |

## Open decisions (epic-level)
- <question + options + recommendation, per the standard block; resolved in place>

## Log
- <date> …
```

Wire the hierarchy natively, not only in prose — `gh issue create --parent <epic>` / `gh issue edit <child> --parent <epic>`, and `gh issue edit <B> --add-blocked-by <A>` for the binding order ([github-features.md](github-features.md) § Hierarchy). The prose order and the native links must agree; the native links are what `--status` and `--sweep` read.

## Sub-issue template

A sub-issue is a standard body plus two lines at the top. It is worked without opening the epic.

```markdown
> Parent: #<E>. <One sentence: what the whole is for, enough to work this issue blind.>
> Blocked by: #<A>   <!-- omit when nothing blocks it -->

<… standard template from Current state onward …>
```

## Gate quality: a new gate proves itself

An issue that **adds or changes a mechanical gate** carries this Done item. Three gates in these repos passed while protecting nothing — a pin gate blind to half its family, a metadata gate reading its evidence from a comment line, 46 of 82 gates never checked for their own correctness. A gate that has never been seen red is not known to work.

```markdown
- [ ] new gate proven by mutation: introduced `<the deviation that must trip it>` → gate red (`<command>` → `<observed red output>`); reverted → gate green (`<observed green output>`)
```

The deviation is the realistic one the gate exists to catch, not a syntax error. Paste both observed outputs.

## Red proof: a regression test fails first

A fix-type issue carries the red proof, not a promise of one. Write the test, run it against the **unfixed** code, paste the failure; then fix, run again, paste the pass.

```markdown
- [ ] regression test red before the fix: `<command>` → `<observed failure>`
- [ ] same test green after the fix: `<command>` → `<observed pass>`
```

A test that was never red proves nothing about the bug.

## Priority rubric (exactly one)

| Priority | When |
|----------|------|
| **P1** | Launch-blocker · data loss · security · false legal/compliance claim |
| **P2** | User-facing correctness or quality — wrong behavior, broken UX, missing expected feature |
| **P3** | Polish — style, minor DX, nice-to-have |

Uncertain between two → pick the lower (W5).

## Type (exactly one)

From the adapter's taxonomy; absent → conventional-commit types: `feat` (user can do something new) · `fix` (broken thing now works) · `refactor` (behavior unchanged) · `docs` · `chore` · `test` · `ci` · `tooling`. CI/docs/test/tooling are never `feat`/`fix`.

Optional status label: `needs-decision` (an Open decision block is unresolved) · `blocked` (native `--add-blocked-by`, plus the `Blocked by: #N` line).

## Self-check gate (Phase 4, before create)

Every box must be yes — otherwise revise, don't create:

- [ ] Every `file:line`/symbol/version/command output in the body was read or run this run (no memory claims)
- [ ] Current state and Target state are separate blocks; Current carries `file:line` or command-output proof, Target is observable
- [ ] Dedup search was **executed**, and its real command + real output are pasted in the Dedup evidence block
- [ ] Symptom reproduced (or confirmed pure-decision); fix-type carries the Repro block
- [ ] Gates table present: each row has command + expected + a baseline measured this run
- [ ] Every Done item resolves to a command's output or an observed effect — no "improved", "reviewed", "cleaned up", "made better"
- [ ] Behavioral (feat/fix) Done criteria are EARS sentences
- [ ] Fix-type carries the red-proof Done items; gate-adding issue carries the mutation-proof Done item
- [ ] Every Steps entry carries a `— verify:` signal
- [ ] Non-goals present; no scope creep
- [ ] An owner call is needed → Open decision block with question + options + recommendation
- [ ] An item crosses an issue boundary → Handoffs block, and the counterpart body says the same
- [ ] Epic → sub-issues listed in binding order, native `--parent` links set, no sub-issue content copied in
- [ ] Sub-issue → self-contained: workable without opening the parent
- [ ] Exactly 1 type + 1 priority (+ status only if it applies), all from the live label set
- [ ] Log block has its opening line
- [ ] No verbose/dead content; nothing restates the title
- [ ] Estimate within the bounded-task threshold, or split into an epic + sub-issues
- [ ] User confirmed the draft
