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
{skill-name}: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Needs-human: N | Total: N
```

| Status | Meaning |
|--------|---------|
| **OK** | No failures, no unresolved CRITICAL |
| **WARN** | Some failures or skips, no unresolved CRITICAL |
| **FAIL** | Unresolved CRITICAL, or an execution error |

**Accounting:** `fixed + failed + skipped + needs-human + needs-approval + not-applicable + reverted = total`. A summary that does not balance is a bug in the run, not a rounding note. Skills with a domain-specific line (`Commits: N`, `Removed: N`, `Generated: N`) keep their extra fields and still balance. Every `skipped`/`needs-human` reason passes the reject list (`principles.md` §11).

**Scope resolution line** (skills with a scope table): `Scopes: {ran: a, b} · {N/A: c — reason} · {mode-excluded: d}` — every declared scope appears once.

## 4. Value Delivered

Preamble (verbatim prefix in every SKILL.md):

```markdown
**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):
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

```
Task: {what was asked, restated so a reader returning from other work re-anchors instantly}
Done: {what was actually done, in plain words}
Gain: {the concrete effect — what got better and why it matters; never an activity count}
```

Then, when any exist:

```
Assumed: {default chosen without asking — one line each; "flag if wrong"}
Needs-human: {each open item in full: what it is, what acting or not acting changes, the recommendation and its reason}
```

An open item is never a bare title. Under `--ask` the same block closes the run; the difference is only that decisions were confirmed rather than assumed.

## 6. Orchestrator report (`ds/audit/report.md`, ds-ship only)

Per delegate: pre-note (expected findings/cost) → summary line → verify-echo → dispositions. Aggregate: mode, scope resolution across delegates (`ran` / `N/A` / `mode-excluded` / `signal-absent`), missing skills, findings by severity, measured instruction-token line, recommended human actions (advisory vs mandated blocker), Outcome Report. Overwritten per run; history lives in `git log`.
