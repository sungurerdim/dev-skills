# core/ — the shared references every skill links to

`core/` holds the references more than one skill depends on. It ships on **every** install — `./install.sh`, `--skills ds-review`, `--target <dir>`, and the plugin marketplace all place it beside the skill directories — so a link of the form `../core/<file>.md` resolves in a single-skill install exactly as it does in the repo. There is no `SKILL.md` here; no host lists `core` as a command.

| File | What it is the single home of | Consumers |
|------|-------------------------------|-----------|
| `principles.md` | Engineering principles with detection signals: themes, SOLID/GRASP, 12-factor, reliability, security, process, testing, config/secrets/data, anti-overengineering guard, cross-scope dedup, needs-approval reason discipline | every auditing, fixing, testing, committing skill |
| `severity-score-categories.md` | Severity levels, confidence, score formula, skip patterns, false-positive prevention, fix categories A/B, disposition vocabulary | every finding producer and consumer |
| `findings-and-profile-format.md` | `ds/audit/findings.md` schema and write semantics; `## Blueprint Profile` line set, 25-line ceiling, read/write rules | every skill that reads or writes either artifact |
| `signal-inventory.md` | The `Signals:` keys, their detection, and the scope-resolution table every multi-scope skill carries | ds-blueprint (producer), every skill's setup phase, ds-ship delegation |
| `ask-exception-list.md` | The only decisions an autonomous run does not make: irreversible and publishing actions; what `--ask` changes | every skill; orchestrators forward it |
| `checkpoint-protocol.md` | Clean-tree pre-gate before the first write, unit-level revert rules, stop-hard flows | every bulk-modifying skill |
| `execution-loop.md` | Intake → re-verify → impact map → bounded units → red proof → mutation proof → aggregate gate → code-proven close | ds-build, ds-issue `--do`, ds-debug, ds-freeze |
| `report-and-outcome-templates.md` | Completion Evidence bands, verify-echo, summary line and accounting, Effect, Outcome Report, orchestrator report | every Summary phase |
| `secret-patterns.md` | Filename exclusion set and content regexes; never-auto-fix rule; scanner augmentation | ds-commit, ds-pr, ds-fix, ds-review, ds-compliance, ds-issue, ds-build |
| `toolchains.md` | Per-stack detect / format / lint / type / test / audit commands, the composed `{check-cmd}`, bootstrap-if-missing, property and mutation testing tools | ds-fix, ds-quality, ds-test, ds-init, ds-build, ds-debug, every Mechanical Done Gate |
| `craap.md` | Source tiers, modifiers, dimensions, bands, verification rules, normative ladder, confidence, contradiction resolution | ds-research, ds-brief, ds-benchmark, ds-productize, `--research` modes, ds-research-agent |
| `software-best-practices.md` | The full curated catalog (110 principles, 24 sources) that `principles.md` distills | provenance for principles.md; ds-benchmark ideal synthesis |
| `experience-rules.md` | Experience-derived rules (XR-nnn) with their coverage map into skill rule files | authoring-time coverage audit; rule files cite `XR-nnn` |

## Rules

1. A skill links here with a relative path (`[principles](../core/principles.md)`), never with a repo URL and never by copying the text. The consistency gate resolves every such link.
2. A file here names its consumers in its first lines. A file with no consumer is deleted.
3. Content lives in exactly one place: here, or in one skill — never both. A skill that needs a local restatement carries at most a one-line pointer.
4. Repo-level authoring guidance (the spec, methodology, research) stays out of `core/`; only runtime-loaded references belong here.
