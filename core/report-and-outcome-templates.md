# Report & Outcome Templates — the shared closing shape

**Consumers:** every skill's Summary phase; orchestrators reuse the same blocks per delegate and once in aggregate.

## 1. Completion Evidence band (opening, verbatim)

```markdown
> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*
```

Portable installs also carry the closing copy as the file's last block:

```markdown
> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
```

## 2. Verify-echo (before the summary line)

For every gate that ran: the exact command string, then its observed output (or exit code and the relevant lines). Same command, same scope as the plan or phase named — a broader suite's green never substitutes for the contracted check. A baseline that was red at setup is reported **red-at-baseline**, measured, never inherited as green.

```
$ {check-cmd}
{observed output}
(exit {code})
```

## 3. Summary line

```
{skill-name}: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Only you can do: N | Total: N
```

| Status | Meaning |
|--------|---------|
| **OK** | No failures, no unresolved CRITICAL |
| **WARN** | Some failures or skips, no unresolved CRITICAL |
| **FAIL** | Unresolved CRITICAL, or an execution error |

**Accounting:** `fixed + failed + skipped + only you can do + not applicable + reverted = total`. A summary that does not balance is a bug in the run, not a rounding note. Skills with a domain-specific line (`Commits: N`, `Removed: N`, `Generated: N`) keep their extra fields and still balance. Every `skipped`/`only you can do` reason passes the reject list (`principles.md` §11).

**Scope resolution line** (skills with a scope table): `Scopes: {ran: a, b} · {N/A: c — reason} · {skipped — not part of this mode: d}` — every declared scope appears once.

## 4. Effect

Preamble (verbatim prefix in every SKILL.md):

```markdown
**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):
```

| Rule | Detail |
|------|--------|
| 1-5 bullets | The ones that matter; no padding |
| Real changes only | No speculative benefit ("you might catch bugs faster") |
| Effect, not activity | "3 hardcoded API keys removed from `src/config/*.ts` — credentials no longer leak into git history", not "applied secret rule 3 times" |
| Concrete units | Lines, files, tests, vulnerabilities, latency, hours — no marketing words |
| Zero-change run | One bullet: `No changes applied — codebase is clean on {scopes}` or `Preview only — {n} findings would be fixed; re-run without --preview to apply.` |
| Severity-weighted order | CRITICAL/HIGH wins first |
| Plain-language effect clause | A reader who has never seen the codebase understands what got better and why it matters; identifiers may name the location, never the benefit |

## 5. Outcome Report (the last block of every run)

Owner: the always-on rules layer (dev-rules › Outcome Report and Decision Framing) when one is installed — the lean and claude profiles strip the copy below at install time and that layer's own rule closes the run. Portable installs carry the copy here so a host without such a layer closes every run the same way. The two texts stay identical through dev-rules' `check-cross-repo.sh` anchors, which this repo's gate runs whenever the sibling checkout exists.

<!-- portable-only:start -->
Labels exactly as written, technical detail above the block, never inside it; a line with nothing to say is omitted:

```
Asked: {what was requested, restated so a reader returning from other work re-anchors instantly}
Done: {what actually changed, in plain words}
Effect: {what got better and why it matters — never an activity count ("fixed y in x files")}
Decided without asking — say if wrong: {each default chosen by judgment that the user might want to reverse}
Only you can do: {each open human-owned action, stated in full — what it is, what changes if it is or isn't done, the recommendation and its reason}
```

The accounting's `only you can do` dispositions feed `Only you can do:`; every decision made by judgment feeds `Decided without asking — say if wrong:`. Under `--ask` the same block closes the run; the difference is only that decisions were confirmed rather than decided.

**Presenting options** — an `--ask` menu, an open-items list, an offer of next steps: recommendation first, with its reason; then every option in the same shape — **name** — what it is in one plain sentence — what happens if it is picked. Written for a reader who remembers nothing of the session: an option explained earlier is explained again in full, never named by reference. Genuinely no recommendation → say why the options are balanced. Several inputs needed → one batched ask, a second round only when an answer depends on a prior one.
<!-- portable-only:end -->

## 6. Orchestrator report (`ds/audit/report.md`, ds-ship only)

Per delegate: pre-note (expected findings/cost) → summary line → verify-echo → dispositions. Aggregate: mode, scope resolution across delegates (`ran` / `N/A` / `skipped — not part of this mode` / `skipped — no signal`), missing skills, findings by severity, measured instruction-token line, recommended human actions (advisory vs mandated blocker), Outcome Report. Overwritten per run; history lives in `git log`.
