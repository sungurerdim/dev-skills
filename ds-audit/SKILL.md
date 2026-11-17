---
name: ds-audit
description: Audit and improve a project to production quality in five phases — lean (cut what the purpose does not need, review recorded rules with the owner), build, safe, surface, ship — each mechanical first, with fixes committed locally and one report. Use to review and fix what the current branch changes (the default), for an end-to-end audit with `all` ("make this production ready", "this has grown too big"), or for a phase or named areas such as `lean` or `sec a11y`.
argument-hint: '[all] [lean|build|safe|surface|ship] [rules|lean|sec|privacy|auth|api|db|arch|code|test|perf|web|a11y|ux|i18n|mobile|store|money|ci|ops|docs|repo ...] [dry] [ask|auto] [<path>]'
---

# /ds-audit

Audit what the branch changes (or, with `all`, the whole project) phase by phase, fix what is safe, prove it with the project's own checks, and leave one report. Every step follows [kernel.md](../core/kernel.md) — read it first. The contract every phase shares — steps, ledger columns, lean procedure, error table — is [references/phases.md](references/phases.md); read it before the first phase.

## Input

| Word | Effect |
|------|--------|
| *(none)* | Changed scope (below): every phase whose areas load, in one invocation |
| `all` | The whole project, one phase at a time: the weekly, pre-release or "it has grown too big" audit |
| phase word | That phase alone: `lean` `build` `safe` `surface` `ship` |
| area words | Only those areas, each runnable alone, even where its signal says N/A ([rules/README.md](../core/rules/README.md)): `rules` `lean` `arch` `code` `test` `perf` `sec` `privacy` `auth` `api` `db` `web` `a11y` `ux` `i18n` `mobile` `store` `money` `ci` `ops` `docs` `repo` |
| `dry` | Detect and plan only; no file changes, no commits, no branch |
| `ask` | Each decision point becomes a question with a recommended option (kernel §5) |
| `auto` | No question at all, lean's included: every decision taken from purpose, evidence and standards, recorded as `decided:`; the review branch (below) makes it one review and one merge, or one branch delete |
| `<path>` | One package of a monorepo; without it, each package with its own manifest is a unit |

**Changed scope** — files changed in `{base}...HEAD` plus uncommitted and untracked ones; findings only on changed lines or code they break; checks still run whole-project. lean runs the code-level rules (dead code, copies — SIM-*) on the changed lines, and `lean-check` when `SCOPE.md` exists; the recorded-rules review and the unit tiering need `lean`, `rules` or `all`.

## Mechanics

`A = python3 {this skill}/assets/audit.py` (stdlib; `--root DIR`, default the current directory). It does every countable step; never redo by hand what it reports.

| Command | Does |
|---------|------|
| `A init [words]` | Fetch, fast-forward when safe, scope, signals, check command, phase plan; resumes an open run (back on `ds/audit`, the open phase's rows, run-written vs your uncommitted files) |
| `A signal KEY VALUE [why]` | Confirm or correct a judged signal (`?` in the Signals line); re-plans phases not started; notes it as `decided:` |
| `A check CMD` | Sets the check command explicitly, noted as `decided:` (init takes the ds-gate marker, else the gate the project's agent docs name, else stack defaults) |
| `A checks baseline\|now` | Runs each check step, records pass / fail / timeout |
| `A scan PHASE` | Runs the `Mech:` commands of the phase's loaded rules |
| `A validate` | Ledger schema, rule IDs, `file:line` exists, commits real and after the start |
| `A phase PHASE done\|blocked "reason"` | Closes a phase; `done` refuses open rows, a red validate or a red `lean-check`, pushes `ds/audit` and prints the push result and the next phase |
| `A report` | Rewrites the report's Closing and Phases, writes `report.html`, prints the closing message |
| `A probe -- CMD…` | The only way a project program is run to see what it does (kernel §3): temp HOME/XDG/`CLAUDE_CONFIG_DIR`/TMPDIR, no network, writes confined where the OS allows; prints exit code, output and files it created |
| `A lean` · `A lean-check` · `A rules` | lean inventory · `SCOPE.md` check · recorded rules with blame date, reason, citation count |
| `A contrast FG BG` | WCAG contrast ratio of two hex colours (AXE-03 without a browser); exit 1 below 4.5:1 |

## Done when

`A validate` green; every phase in the plan `done` (or `blocked` with a concrete reason, which makes the run INCOMPLETE); `A checks now` no redder than baseline, shown by its output; `A report` printed the closing message.

## Steps

1. **Start** — `A init {words}`. Read its JSON: `next` phase, plan, signals, check command, notes. Read the project's rules in one batch (`AGENTS.md`, `CLAUDE.md`, `README*`, `CONTRIBUTING*`, ADRs, specs); they override this file and the rule files where they differ.
2. **Signals** — confirm every `?` value by reading the code it rests on; wrong → `A signal KEY VALUE`.
3. **Baseline** — read the check command and `check_from` (kernel §3: never run what you have not read); wrong → `A check CMD`. Then `A checks baseline` once per run (a resumed run keeps its baseline).
4. **Phases** — for the `next` phase and each after it, follow [phases.md](references/phases.md): inventory → detect → decide → apply → verify → `A phase {p} done`. One context runs them all; a subagent per phase only for `size=large` or a context running short (handoff in phases.md).
5. **Report** — `A report`; print its closing message as the last output (kernel §6).

## Notes

- `size=large` → order each phase's reading by hotspots (`git log --since=1.year --name-only --format=`, commits × size); stop an area when new findings stop appearing.
- No commit-time or stop-time gate in the project → a finding in the `ci` area; the `ds-gate` skill installs one. The budget in `SCOPE.md` can become a gate with `/ds-gate inv "audit.py lean-check passes"`.
- The run leaves `ds/audit/report.md` (the ledger) and `ds/audit/report.html` (the same report for people: one self-contained page, any screen size, light/dark, printable), both git-excluded (a new run keeps the previous pair as `report-{started}.*`, one generation, and carries its open rows), plus what the owner keeps: commits, `SCOPE.md`, the `ds/audit` branch until merged.
- **Branch**: `all`, phase and area runs commit on `ds/audit` (created or resumed by `A init`; your branch is not touched) and push it, without force, after each phase; changed-scope runs commit on the current branch and never push. Merging, PRs and deleting the branch are yours (the report prints the commands).
- Publishing, other pushes, releases and anything needing a human-only value stay `Only you can do` with the exact command (kernel §5).
