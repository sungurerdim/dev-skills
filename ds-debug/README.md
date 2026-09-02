# ds-debug

"Fix the bug" without a reproduction produces a plausible edit that fixes nothing and a test that never went red.

**Bug hunter — reproduce the red, localize (bisect, trace, logs), ≤3 hypotheses, minimal fix behind a red-proven regression test, project check green.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git && cd dev-skills && ./install.sh
```

Any Agent Skills host: `./install.sh --target <that host's skills dir>` (ships `core/` beside the skill).

## Use

```bash
/ds-debug                          # from the failure described in the request
/ds-debug --issue=#7               # from a GitHub issue; closure evidence written into its body
/ds-debug --test=test/money.test.js
/ds-debug --bisect                 # force git bisect run against a last-known-good ref
/ds-debug --preview                # reproduce + localize + hypotheses only, no fix
/ds-debug --research               # allow web lookups for library/platform behavior
/ds-debug --ask                    # confirm the reproduction, the hypothesis and the fix
```

## Flow

1. Reproduce — a command whose output shows the failure (pasted); not reproducible → stop, no edit
2. Localize — bisect when a known-good ref exists, else trace / temporary logging / flaky split (3× isolated + 1× shuffled)
3. Hypothesize — at most three, each with a prediction and the command that falsifies it
4. Minimal fix — regression test written first and seen red, smallest change, seen green
5. Done gate + close — full project check, local commit, issue body evidence
6. Summary — cause `file:line`, hypotheses tried, test red→green, check output

## Features

- **Red first** — no speculative fixes; "not reproduced" is an honest outcome
- **Tests never weakened** — expected values and coverage of the failing path never shrink
- **Hypothesis budget** — three falsifications, then a stop with options, never a fourth guess
- **Checkpoint-safe** — bisect only on a clean tree, always `git bisect reset`, per-file reverts
- **Mechanical Done Gate** — the project's own check chain decides "fixed"
- **Hands off publishing** — commits are local; push and PR are reported with the command
