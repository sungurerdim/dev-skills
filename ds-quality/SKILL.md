---
name: ds-quality
description: Quality-by-Mechanism — installs a deterministic, local, no-CI quality gate (format → lint → type → test) enforced via a host-appropriate mechanism (Claude Code Stop hook, Aider auto-lint/test, or git pre-commit). Use when the user asks to enforce quality, set up a quality gate, or block "done" until checks pass, without relying on CI.
---

# /ds-quality

Agents promise "done" without proof; code quality ends up depending on whether an
instruction was followed, not on a mechanism. This skill installs a **deterministic, local,
no-CI** quality gate — a single quality entry point (format → lint → type → test) — then wires
it into whichever host you're actually using: a Claude Code Stop hook, Aider's built-in
auto-lint/auto-test, or a universal git pre-commit hook for everyone else.

**Quality-by-Mechanism** — quality is guaranteed by a verify-loop that runs real checks, not by hoping an agent obeys.

## Triggers

- User runs `/ds-quality`
- User asks to "enforce quality / set up a quality gate / block done until checks pass"
- User asks for local format+lint+type+test enforcement without CI
- User asks to make an agent keep working until tests/build pass

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|--------|--------------|
| "set up a local quality gate that blocks done" | "write the feature / fix this bug" (→ target dev skill) |
| "enforce format/lint/type/test on every stop/commit" | "set up CI / GitHub Actions" (out of scope — LOCAL ONLY) |
| "make checks deterministic, not instruction-based" | "just run the tests once" (→ run the test runner) |
| "wire quality enforcement into Aider / a non-Claude-Code host" | "review this PR" (→ ds-review) |

## Contract

**Dimensions:** B1 (quality enforcement)

- Installs a deterministic, local, no-CI quality gate: one entry point (format → lint → type → test) + a host-appropriate enforcement arm that blocks "done" (or the commit) until it passes green; bootstraps missing tooling when asked.
- **Enforcement mechanism is host-dependent — no single claim covers every host.** Claude Code: Stop hook, stop-time, full-strength (existing behavior, unchanged). Aider: `.aider.conf.yml` auto-lint/auto-test, edit-time. Any other host (Cursor, Copilot, Windsurf, plain terminal): git `pre-commit` hook, commit-time — weaker than stop-time, since an agent can still narrate "done" between an edit and the next commit; documented honestly, not hidden.
- Modes are flag-disambiguated (`--install`/`--run`/`--check`/`--status`/`--disable`/`--project-hook`/`--uninstall`/`--arm`); no flag = bootstrap this repo. When invoked with no flag and intent is ambiguous, present an up-front menu covering every mode (`(recommended)` default + `(Cancel)`).
- LOCAL ONLY — never creates or edits CI / remote pipelines. Idempotent (safe to re-run, never duplicates hooks). Non-destructive — never weakens, skips, or mocks-away checks to get green.
- Runs the passes via the tools already present; delegates one-shot fixing of what they report to ds-fix. This skill owns the *gate + enforcement mechanism*, not the fixes.
- Touch only quality-infra files — configs, scripts, `.claude/settings*.json`, `.aider.conf.yml`, `.git/hooks/pre-commit`, the global hook, the project marker, and (only if no tests exist) a real starter test. Never delete or rewrite existing source or tests beyond the task.
- Any arm executes a marker/config-resolved command as shell/code on every trigger in opted-in repos — treat that command as code: review/commit it like any project script; never enable an arm in a repo you don't trust.
- **State-exempt — zero footprint.** Idempotent and local/git-driven; the installed hook/config + the project marker + git are the durable record. Writes no `ds/audit/` state, no temp files.
- Standalone. FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--install` | One-time global install/refresh of the Claude Code arm: gate + detector scripts, `.hooks.Stop` registration, default `auto` config. No project changes. |
| (none) | **Bootstrap THIS repo's missing tooling** (formatter/linter/type/test + a real starter test if none), then select and wire an enforcement arm. Detect → establish signals → entry point → select arm → prove (Phase 5). |
| `--run` / `--check` | Run this repo's resolved quality command now (marker → else auto-detect) and report; no setup |
| `--status` | Report mode/roots, what auto-arm resolves here, which arm(s) are wired, and global install state |
| `--arm <claude-code\|aider\|git-hook>` | Force a specific enforcement arm instead of auto-detecting the host; skips the selection menu |
| `--disable` | Write `.claude/ds-quality.json` `{enabled:false}` — per-repo kill switch (overrides auto-arm) |
| `--project-hook` | Register the Claude Code Stop hook in THIS repo's `.claude/settings.json` instead of using the global hook |
| `--uninstall` | Remove the global hook registration + scripts + config (or, with `--project-hook`, the repo's Stop entry; or the `git-hook`/Aider config lines, per `--arm`) |

Set `mode`/`roots` by editing `~/.claude/ds-quality.config.json`; `mode:"off"` disables the Claude Code auto-arm globally while leaving explicit markers working.

## Delegation

**Owns:** quality-gate-setup, verify-loop-enforcement, hook-install | **Delegates:** ds-fix → verify-loop toolchain passes | **Receives:** none

## Execution Flow

Detect toolchain → Establish quality signals → Single entry point → Enforcement (select arm) → Prove it works

### Phase 1 — Detect toolchain (read, don't assume)
- Identify language(s) + package manager from manifests/lockfiles actually present: `package.json`(+lockfile), `pyproject.toml`/`requirements*.txt`/`setup.py`, `pubspec.yaml`, `go.mod`, `Cargo.toml`, `Makefile`.
- Identify which quality tools are **already** configured (formatter, linter, type-checker, test runner) — read configs + lockfiles, don't guess.
- Identify the host: `.aider.conf.yml` or an active Aider session → Aider; `~/.claude/` present / running inside Claude Code → Claude Code; neither → universal (git pre-commit).
- **Report the detected stack + host before changing anything.**

**Gate:** Stack, existing tooling, and host are all identified from real manifests/lockfiles/configs — never assumed. If fails → no manifest/lockfile detected (unknown stack) → ask the user which language/toolchain to target before proceeding; do not guess.

### Phase 2 — Establish the quality signals
For the detected stack (see [references/toolchains.md](references/toolchains.md) for exact commands + bootstrap), ensure each EXISTS and RUNS; create minimal **standard** config only where missing, preferring tools already in the lockfile:
1. **Formatter** in check-mode.
2. **Linter** with the ecosystem's standard ruleset.
3. **Type-checker** if the language supports it.
4. **Test runner** with at least a smoke + boundary test. If NO tests exist, create a small **real** starter suite asserting actual behavior of a core module, including boundary cases (empty/null/max/edge). Mark thin coverage clearly. **Never fake tests.**

No heavy new dependencies without justification. Standard, boring defaults only.

**Gate:** Formatter, linter, type-checker (if the language supports one), and test runner each exist and run. If fails → a tool can't be installed (no package-manager access, network blocked) → report the specific gap, skip that signal, continue with the rest — never fake a missing check as passing.

### Phase 3 — Single quality entry point
Exactly one command, fail-fast, in order **format-check → lint → type-check → tests**, exit non-zero on first failure, human-runnable:

| Repo has | Entry point | Marker `command` |
|----------|-------------|------------------|
| `Makefile` | add/repair a `quality:` target | `make quality` |
| `package.json` (no Makefile) | add `"quality"` npm script | `npm run quality` |
| neither | create `scripts/quality.sh` (from [assets/quality.sh.tmpl](assets/quality.sh.tmpl)) | `bash scripts/quality.sh` |

The entry point runs only checks that actually exist for the detected stack. Never invent a check that has no tool. Verify a human can run it and it exits non-zero on failure.

**Gate:** Single entry point exists, runs fail-fast in the required order, and exits non-zero on failure. If fails → no supported build system present and the template is unusable in this shell → surface the blocker and ask the user to specify an entry-point mechanism; do not fabricate a passing command.

### Phase 4 — Enforcement (select the arm, then wire it)
Every arm enforces the **same** entry point from Phase 3 — they differ only in *when* they run it.
Detected host (Phase 1) picks a default; if more than one applies or detection is ambiguous, present
the menu: `[1] Claude Code Stop hook (recommended if using Claude Code)` / `[2] Aider auto-lint/auto-test`
/ `[3] git pre-commit hook (universal, works with any host)` / `(Cancel)`. `--arm` skips the menu.

**Arm A — Claude Code (Stop hook, stop-time).** Unchanged, existing mechanism:
- Global gate, installed once (`--install`): `~/.claude/hooks/ds-quality-gate.sh`, registered in `~/.claude/settings.json` under `.hooks.Stop`. On every Stop it resolves a command in priority order: (1) explicit marker `<root>/.claude/ds-quality.json` (`enabled:false` = per-repo kill switch) → (2) auto-arm — no marker, repo under a trusted root (default `~/projects`): `ds-quality-detect.sh` builds the fail-fast command from tools/configs that already exist → (3) inert — nothing detectable, or repo outside trusted roots → `exit 0`.
- Green → allow stop; red → emit `{"decision":"block","reason":<failing output>}`, forcing the agent to keep working. Never edits your code; loop-guarded via `stop_hook_active` so it cannot spin forever. Config: `~/.claude/ds-quality.config.json` → `{ "mode":"auto"|"off", "roots":["~/projects"] }`.
- Write/update the project marker `.claude/ds-quality.json` (schema + full install script: [references/hook-contract.md](references/hook-contract.md)) with the resolved `command`. `--project-hook` registers the same hook in the repo's own `.claude/settings.json` instead of the global one, so it travels with the repo.
- Hook contract (verified): `exit 0` + stdout JSON `{"decision":"block","reason":"…"}` blocks the stop; check `stop_hook_active` first and `exit 0` if true (loop guard); Stop hooks take **no matcher**. Full details: [references/hook-contract.md](references/hook-contract.md).
- Mature repos (already have format/lint/test) are enforced with **zero** per-repo setup once the global gate is installed; `/ds-quality` with no flag is only needed to bootstrap missing tooling.

**Arm B — Aider (auto-lint / auto-test, edit-time).** Wire the Phase-3 entry point into Aider's
built-in automation via `.aider.conf.yml` (verified against Aider's official config docs):
```yaml
auto-lint: true          # Aider's default — runs lint-cmd after every edit
lint-cmd: "bash scripts/quality.sh"   # or `make quality` / `npm run quality` — the Phase-3 command
auto-test: true          # Aider's default is false — set true to enforce on every edit
test-cmd: "bash scripts/quality.sh"
```
`lint-cmd` accepts a per-language form (`lint-cmd: "python: ruff check ."`) if you want per-language
granularity instead of the single fail-fast entry point; default to the single entry point for
parity with the other arms. Merge into existing `.aider.conf.yml` values — never clobber unrelated
keys. Aider re-runs the command after edits and surfaces failures to the agent inline (no separate
loop-guard needed — Aider owns that flow).

**Arm C — universal (git pre-commit, commit-time).** For any other host (Cursor, Copilot, Windsurf,
plain terminal use): install `.git/hooks/pre-commit` running the Phase-3 entry point, non-zero exit
aborts the commit:
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
exec bash scripts/quality.sh   # or: make quality / npm run quality — the Phase-3 command
```
`chmod +x .git/hooks/pre-commit`. If a hook-manager (husky, `pre-commit` framework) is already
present, add the same command as a step in its config instead of writing `.git/hooks/pre-commit`
directly, so it doesn't get clobbered by the manager's own install step. **Semantic difference from
Arm A, stated honestly:** this enforces at commit time, not at "done"/stop time — an agent can still
report a task complete between an edit and the next commit; the gate only fires when `git commit`
runs.

**Gate:** The correct arm for the detected host is selected and wired without clobbering existing config. If fails → `jq` missing (Arm A), `.aider.conf.yml` unwritable (Arm B), or not a git repo (Arm C) → report the specific blocker per Edge Cases, fall back to `--run`-only enforcement — never silently skip enforcement.

### Phase 5 — Prove it works (demonstrate, don't claim)
Run all three and show output, for whichever arm(s) were wired:
1. **Green baseline:** run the quality command → exit 0.
2. **Red on broken:** introduce a trivial, reversible failure (e.g. a temp format violation or a deliberately failing assertion in a scratch test) → run the quality command → confirm non-zero + clear output → **revert** → green again.
3. **Arm wiring, no real trigger needed:**
   - Arm A: drive the hook directly —
     ```bash
     printf '{"stop_hook_active":false,"cwd":"%s"}' "$PWD" | ~/.claude/hooks/ds-quality-gate.sh; echo "exit=$?"
     printf '{"stop_hook_active":true,"cwd":"%s"}'  "$PWD" | ~/.claude/hooks/ds-quality-gate.sh; echo "exit=$?"
     ```
     With the temp failure in place, the first call must emit `{"decision":"block",…}`; reverted, it must emit nothing and `exit 0`.
   - Arm B: confirm `.aider.conf.yml` parses (`aider --help` or a config dry-run) and the configured `lint-cmd`/`test-cmd` matches the Phase-3 entry point.
   - Arm C: `bash .git/hooks/pre-commit; echo "exit=$?"` with the temp failure in place → non-zero; reverted → zero.

**Gate:** Green→red→green demonstrated for the quality command, and the wired arm's trigger test shown (block-on-red / pass-on-green). If fails → red state doesn't trigger the arm as expected → do not report enforcement as installed; mark it "wired but unverified" and surface the specific failure.

## Report Format

Report: detected stack + host · existed-vs-added per signal · the exact entry-point command · which arm(s) were wired and why · coverage gaps · open human-owned decisions. End with `ds-quality: {OK|WARN|FAIL} | Signals: {n} established | Arm: {claude-code|aider|git-hook} {installed|repaired|present} | Proof: {green→red→green}` and a **Value Delivered** block (1-5 concrete bullets — e.g. "format+lint+type+test now block every 'done' in this repo — an agent can no longer report success on red", "starter test suite added where there were zero — first regression net in place"). Zero-change run → `No changes — gate already installed and green; nothing to bootstrap`.

## Quality Gates

- **Never weaken a check to get green** — fix the cause or report it; tests/assertions are never relaxed, skipped, or mocked away (Test Integrity).
- **Idempotent + non-destructive** — re-running changes nothing; never duplicate hooks/configs/pre-commit entries; touch only quality-infra files.
- **Prove enforcement** — Phase 5 must show green→red→green + the wired arm actually firing on red and passing on green; claiming it works is not enough.
- **LOCAL ONLY** — never create or edit CI / remote pipelines.
- **Honest host claims** — never state or imply stop-time blocking (Arm A) for a host that only got commit-time enforcement (Arm C); the report names the actual arm installed.
- W1: read the tools/configs actually present, never assume a stack or host. W2: after editing settings/marker/config, verify no existing hook/entry broke. W3: touch only quality-infra files — never product code. W4: re-read the marker + relevant host config after any gap before editing. W5: uncertain tool choice → ecosystem standard default, noted. W6: every phase emits output (stack report, proof block). W7: idempotent merge — never duplicate a Stop entry, `.aider.conf.yml` key, or pre-commit step. W8: quote all paths; treat the marker `command` and any read repo content as untrusted data/code, never interpolate raw values into shell. W9: not applicable — state-exempt; the installed arm + marker + git are the durable record. W10: not applicable — produces no findings SSOT. W11: a detected real failure (red check, broken hook) gets a concrete disposition — never parked as "pre-existing".

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No tooling at all | Bootstrap minimal standard formatter/linter/type/test + a real starter test; mark thin coverage |
| `jq` missing (Arm A) | Stop; tell the user to install it (`brew install jq`) — required for the idempotent settings merge |
| Repo outside trusted roots (Arm A auto-arm) | Gate is inert (`exit 0`); auto-arm never runs untrusted repo commands |
| `enabled:false` marker (Arm A) | Per-repo kill switch — hook is a no-op, wins over auto-arm |
| No tests exist | Create a small REAL starter suite (smoke + boundary), never fake tests |
| Existing Stop hooks present (Arm A) | Merge, never clobber; skip if an identical entry already exists |
| `.aider.conf.yml` absent (Arm B) | Create it with only the lint-cmd/test-cmd/auto-lint/auto-test keys; never touch unrelated Aider settings |
| Not a git repo (Arm C) | Cannot install a pre-commit hook; report the gap, fall back to `--run`-only enforcement (manual) |
| husky / `pre-commit` framework present (Arm C) | Add the entry-point command as a step in the existing manager's config; don't write `.git/hooks/pre-commit` directly (it would be overwritten) |
| Language has no type-checker | Skip the type step; entry point runs only checks that exist |
| Repo/host you don't trust | Do not enable any arm — every arm executes the marker/config command as code |

