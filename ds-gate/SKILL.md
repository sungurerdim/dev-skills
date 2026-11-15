---
name: ds-gate
description: Install a local quality gate that blocks "done" (or the commit) until format, lint, type and test checks pass — one entry point, wired into the host's hook. Also builds a gate for one custom invariant (inv). Use when checks should be enforced by a machine, not remembered.
---

# /ds-gate

Make the project's checks a machine signal: one entry point, run automatically before the agent may stop or commit. Follows [kernel.md](../core/kernel.md); this file adds only the gate specifics. Owns the gate, not the fixes — a red gate is fixed at its cause, never weakened.

## Input

| Word | Effect |
|------|--------|
| *(none)* | Full setup of this repo: steps 1-5 below |
| `checks` | Steps 1-2 only: make sure each check exists and runs |
| `arm [name]` | Steps 3-4 only: entry point (written if missing) and the host's arm; a name forces one: `claude-code` · `codex` · `gemini` · `aider` · `git-hook` |
| `prove` | Step 5 only: show the wired arm block on a failing probe file and pass after it is deleted |
| `run` | Run this repo's entry point now and report; no setup |
| `status` | Report the marker, what the gate resolves here, which arms are wired |
| `off` / `on` | Set `"enabled"` in `.claude/ds-gate.json` (per-repo kill switch) |
| `install` | One-time global install of the Claude Code Stop hook (`ds-gate.py install --register`) |
| `uninstall` | Remove the global hook entry and file, or this repo's arm |
| `inv "<text>"` | Build a gate for one invariant no tool ships (below) |
| `ask` | Questions with a recommended option at each decision (kernel §5) |

Every part runs alone: it does step 1's detection itself and reads the marker when it needs the entry point. The gate always runs the whole project's checks, never only changed files: a local change can break a check anywhere.

`{py}` below = the absolute path of a Python ≥ 3.8 interpreter; `{gate}` = `~/.claude/hooks/ds-gate.py` after `install`, else `assets/ds-gate.py` beside this file. Stdlib only, same on macOS, Linux and Windows; no shell launcher.

## Done when

The entry point runs green; the wired arm is shown blocking on a failing probe file and passing after it is deleted; `git status` matches its state before the run apart from the setup's own files; every existing repo check is wired or listed excluded-with-reason.

## Steps

1. **Detect** stack and tooling from one `git ls-files` inventory (manifests, lockfiles, configs, test dirs; [toolchains.md](../core/toolchains.md)); the host from one listing of what is installed (`~/.claude/`, `~/.codex/`, `~/.gemini/`, `.aider.conf.yml`). Print both before changing anything. Unknown stack → `Only you can do: name the toolchain`.
2. **Checks exist and run** — formatter (check mode), linter, type checker where the language has one, test runner. Run each once and read the exit code; never infer from config. Missing → add the ecosystem default that is already in the lockfile, else the toolchains.md default. No tests at all → a small real starter suite (one core behavior + boundary cases), marked thin. Never a fake test.
3. **One entry point**, fail-fast in the order format → lint → type → test, exit non-zero on the first failure:

   | Repo has | Entry point |
   |----------|-------------|
   | `Makefile` | `quality:` target → `make quality` |
   | `package.json` | `"quality"` script → `npm run quality` |
   | neither | the `&&`-chained command itself |

   Write it to the marker `.claude/ds-gate.json` as `{"command": "...", "timeout": 270}` (`timeout` in seconds; `enabled:false` disables). Coverage, both mechanical: every existing check (`scripts/`, package scripts, Makefile targets, `.pre-commit-config.yaml`, test dirs the runner misses) is called by the entry point or listed excluded with the condition under which it runs; every step names the file set it scans, and zero files matched fails.
4. **Wire the arm** — strongest available for the host; merge, never clobber; back up a config before editing it:

   | Arm | When it blocks | Wiring |
   |-----|----------------|--------|
   | `claude-code` | before done | `{py} {gate} install --register` → Stop hook `"{py}" "{gate}" gate` in `~/.claude/settings.json`; auto-detects trusted repos (`roots` in `~/.claude/ds-gate.config.json`) |
   | `codex` | before done | `~/.codex/hooks.json` → `hooks.Stop[].hooks[] = {"type":"command","command":"\"{py}\" \"{gate}\" gate"}` (same block JSON) |
   | `gemini` | before done | `~/.gemini/settings.json` → `hooks.AfterAgent[]` with command `"{py}" "{gate}" gate --exit2` (exit 2 + reason) |
   | `aider` | on edit | `.aider.conf.yml`: `lint-cmd` and `test-cmd` = `"{py}" "{gate}" run`, `auto-lint: true`, `auto-test: true` |
   | `git-hook` | before commit (Copilot, Cursor, Windsurf, terminal) | `.git/hooks/pre-commit`: `#!/bin/sh` + `exec "{py}" "{gate}" run`; a hook manager (husky, pre-commit) present → add it as a step there instead |

   Aider skips git hooks by default (`git-commit-verify: false`), so it needs its own arm. Before-commit arms are weaker than before-done ones: the report says which one was installed, never more.
5. **Prove** — run the entry point (green) → add one new file the checks reject (a failing test, or a lint error in a new source file; never an edit to an existing file, kernel §3) → drive the arm directly and show it block (`"{py}" -c "import json,os; print(json.dumps({'cwd': os.getcwd()}))" | "{py}" "{gate}" gate`, the same on every shell; or run the pre-commit hook) → delete the file → show it pass. An arm not seen blocking is reported `wired, unproven`.

## Invariant mode

For one rule no tool checks (parity, absence, generated-file sync, count floor, declaration ↔ code match, mirror constants, contract suite):

1. Restate it as one falsifiable sentence naming the exact files or symbols. Ambiguous target → `Only you can do: name the target`.
2. Pick the pattern from [invariant-patterns.md](references/invariant-patterns.md) (P1-P9); none fits → nearest skeleton, gap recorded.
3. Copy the repo's existing gate shape (language, exit codes, registration); none → the skeleton.
4. Generate: scope named, red on zero files matched, exemptions with a reason, reports and never rewrites.
5. Red-proof: inject the exact violation, in a new file when the scope admits one, else in a file with no user changes → non-zero shown → undo it (kernel §3) → green shown.
6. Wire into the entry point and prove the chain red then green; no chain → deliver it unwired and say so.

All four — gate, red-proof, wiring (or stated unwired), scope note — or the run is `INCOMPLETE`.

## Report

`ds-gate: OK|WARN|FAIL|INCOMPLETE | stack {s} · host {h} · arm {a} {installed|present|unproven} · proof green→red→green`, then: each check existed/added, the entry-point command, checks wired vs excluded-with-reason, gaps, and the closing block of kernel §6.

## Limits

- Local only: never creates or edits CI pipelines.
- Every arm runs the marker command as code on each trigger — never enable one in a repo you do not trust. Outside the trusted roots the Claude Code gate is inert.
- The gate never edits code; it blocks so the fix gets made. A green result is cached per tree state (`.git/ds-gate.green`); a timeout is a block, never a pass.
- Hook formats drift — re-check the host's live hook docs before wiring; [hook-contract.md](references/hook-contract.md) holds the verified contracts.
