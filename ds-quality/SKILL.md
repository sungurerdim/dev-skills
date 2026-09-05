---
name: ds-quality
description: Installs a deterministic, local, no-CI quality gate (format/lint/type/test) wired into a host-appropriate hook, plus --invariant mode turning any described invariant into a red-proven, chain-wired check. Use to enforce quality, block "done" without CI, or mechanize an invariant.
---

# /ds-quality

Agents promise "done" without proof — quality depends on whether an instruction was followed, not on a mechanism. This skill installs a **deterministic, local, no-CI** quality gate — one entry point (format → lint → type → test) — then wires it into whichever host you use (Phase 4). `--invariant` mode extends the same principle past the toolchain: any invariant the user can describe becomes a generated, red-proven, chain-wired check (see Invariant Mode).

**Quality-by-Mechanism** — guaranteed by a verify-loop that runs real checks, not by hoping an agent obeys.

**Install per host:** Claude Code — `/ds-quality --install` (once); other hosts — `--arm {codex|gemini|copilot|aider|git-hook}`; no flag bootstraps missing tooling first, then auto-selects and wires the host's arm — see Phase 4.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-quality`
- User asks to "enforce quality / set up a quality gate / block done until checks pass"
- User asks for local format+lint+type+test enforcement without CI
- User asks to make an agent keep working until tests/build pass
- User describes an invariant and asks for it to be mechanically enforced ("these two constants must stay equal", "X must never come back", "this generated file must match its source") → `--invariant`

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|--------|--------------|
| "set up a local quality gate that blocks done" | "write the feature / fix this bug" (→ target dev skill) |
| "enforce format/lint/type/test on every stop/commit" | "set up CI / GitHub Actions" (out of scope — LOCAL ONLY) |
| "make checks deterministic, not instruction-based" | "just run the tests once" (→ run the test runner) |
| "wire quality enforcement into Aider / a non-Claude-Code host" | "review this PR" (→ ds-review) |
| "make this invariant mechanically enforced" (`--invariant`) | "run the audits that already exist" (→ `--run`) |

## Contract

**Dimensions:** B1 (quality enforcement)

- Installs a deterministic, local, no-CI quality gate: one entry point (format → lint → type → test) + a host-appropriate arm that blocks "done" (or the commit) until it passes green; bootstraps missing tooling when asked.
- **Enforcement is host-dependent.** Before-done (full strength): Claude Code Stop hook · Codex CLI `Stop` hook · Gemini CLI `AfterAgent` hook. On-edit: Aider `.aider.conf.yml` auto-lint/auto-test. Before-commit (weaker — an agent can still narrate "done" between an edit and the next commit): GitHub Copilot `preToolUse` commit-deny hook · git `pre-commit` (universal fallback).
- Modes are flag-disambiguated (`--install`/`--run`/`--status`/`--disable`/`--project-hook`/`--uninstall`/`--arm`/`--invariant`); no flag = bootstrap this repo (default when ambiguous). `--ask` with no disambiguating flag → up-front menu covering every mode (`(recommended)` + `(Cancel)`).
- LOCAL ONLY, idempotent, non-destructive — detailed in Quality Gates below.
- Runs the passes via tools already present; delegates one-shot fixing to ds-fix. This skill owns the *gate + enforcement mechanism*, not the fixes.
- `--invariant "<description>"` turns ONE invariant into four inseparable deliverables: the gate (repo's incumbent format), a red-proof (non-zero on an injected violation, green on revert), chain wiring (or an explicit unwired statement — never implied), and a scope declaration (scans/exempts/blind spots). Missing any of the four is reported `INCOMPLETE`, never `OK`.
- Touch only quality-infra files — configs, scripts, `.claude/settings*.json`, `.aider.conf.yml`, `.git/hooks/pre-commit`, the global hook, the project marker, `--invariant`-generated gates (script/test + chain registration), and (only if no tests exist) a real starter test. Never delete or rewrite existing source or tests beyond the task.
- Any arm executes a marker/config-resolved command as shell/code on every trigger — treat it as code: review/commit like any project script; never enable an arm in a repo you don't trust.
- **State-exempt — zero footprint.** Idempotent, local/git-driven; installed hook/config + project marker + git are the durable record. Writes no `ds/audit/` state, no temp files.
- Standalone. Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->

## Arguments

| Flag | Effect |
|------|--------|
| `--install` | One-time global install/refresh of the Claude Code arm: gate + detector scripts, `.hooks.Stop` registration, default `auto` config. No project changes. |
| (none) | **Bootstrap THIS repo's missing tooling** (formatter/linter/type/test + starter test if none), then select and wire an arm. Detect → signals → entry point → arm → prove (Phase 5). |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |
| `--run` | Run this repo's resolved quality command now (marker → else auto-detect) and report; no setup |
| `--status` | Report mode/roots, what auto-arm resolves here, which arm(s) are wired, global install state |
| `--arm <claude-code\|aider\|git-hook\|copilot\|gemini\|codex>` | Force a specific arm instead of auto-detecting the host; skips the selection menu |
| `--invariant "<description>"` | Build a custom gate from a plain-language description: classify against the pattern catalog → copy the repo's gate precedent → generate → red-proof → wire into the chain → declare scope. See Invariant Mode |
| `--disable` | Write `.claude/ds-quality.json` `{enabled:false}` — per-repo kill switch (overrides auto-arm) |
| `--project-hook` | Register the Claude Code Stop hook in THIS repo's `.claude/settings.json` instead of using the global hook |
| `--uninstall` | Remove the global hook registration + scripts + config (or the repo's Stop entry with `--project-hook`; or the `git-hook`/Aider config lines per `--arm`) |

Set `mode`/`roots` via `~/.claude/ds-quality.config.json`; `mode:"off"` disables the Claude Code auto-arm globally while explicit markers keep working.

## Delegation

**Owns:** quality-gate-setup, verify-loop-enforcement, hook-install | **Delegates:** ds-fix → verify-loop toolchain passes; ds-test → starter-suite generation when project has zero tests | **Receives:** ds-rig → quality-gate wiring after rig setup; ds-build → enforcement-arm bootstrap when no gate exists

## Execution Flow

Detect toolchain → Establish quality signals → Single entry point → Enforcement (select arm) → Prove it works

### Phase 1 — Detect toolchain (read, don't assume)
- **Upstream:** fresh profile → reuse `Toolchain`/`Type`/`Stack`, skip re-detecting; still run each check in Phase 2 (a stale claim isn't proof). Absent, drifted, or missing a key → detect below.
- Identify language(s) + package manager from manifests/lockfiles actually present: `package.json`(+lockfile), `pyproject.toml`/`requirements*.txt`/`setup.py`, `pubspec.yaml`, `go.mod`, `Cargo.toml`, `Makefile`.
- Identify which quality tools are **already** configured (formatter, linter, type-checker, test runner) — read configs + lockfiles, don't guess.
- Identify the host: `.aider.conf.yml` or an active Aider session → Aider; `~/.claude/` present / running inside Claude Code → Claude Code; `.codex/` or `~/.codex/` → Codex CLI; `.gemini/` or `~/.gemini/` → Gemini CLI; `.github/hooks/` or `~/.copilot/` → Copilot; none → universal (git pre-commit).
- **Report the detected stack + host before changing anything.**

**Gate:** Stack, tooling, and host all identified from real manifests/lockfiles/configs — never assumed. If fails → no manifest/lockfile detected (unknown stack): matches the publish/irreversible exception list (no value inferable from the repo). Default: stop this phase, record `only you can do: unknown stack — specify language/toolchain`. `--ask`: ask the user which language/toolchain to target; do not guess.

### Phase 2 — Establish the quality signals
For the detected stack (see [`../core/toolchains.md`](../core/toolchains.md) for exact commands + bootstrap), ensure each EXISTS and RUNS — run each tool's check command once and observe the exit code, never infer from config presence; create minimal **standard** config only where missing, preferring tools already in the lockfile:
1. **Formatter** in check-mode.
2. **Linter** with the ecosystem's standard ruleset.
3. **Type-checker** if the language supports it.
4. **Test runner** with at least a smoke + boundary test. If NO tests exist: ds-test present → delegate starter-suite generation to it; absent → create a small **real** starter suite inline, asserting actual behavior of a core module, including boundary cases (empty/null/max/edge). Mark thin coverage clearly. **Never fake tests.**

No heavy new dependencies without justification. Standard, boring defaults only.

**Gate:** Formatter, linter, type-checker (if the language supports one), and test runner each exist and run. If fails → tool can't install (no package-manager access, network blocked) → report the gap, skip that signal, continue — never fake a missing check as passing.

### Phase 3 — Single quality entry point
Exactly one command, fail-fast, in order **format-check → lint → type-check → tests**, exit non-zero on first failure, human-runnable:

| Repo has | Entry point | Marker `command` |
|----------|-------------|------------------|
| `Makefile` | add/repair a `quality:` target | `make quality` |
| `package.json` (no Makefile) | add `"quality"` npm script | `npm run quality` |
| neither | create `scripts/quality.sh` (from [assets/quality.sh.tmpl](assets/quality.sh.tmpl)) | `bash scripts/quality.sh` |

The entry point runs only checks that actually exist for the detected stack. Never invent a check that has no tool. Its runnability and non-zero-on-failure behavior are proven by Phase 5's green→red→green run — that run's observed output is the evidence; no separate verification here.

**Entry-point coverage (run before wiring the arm).** Two mechanical properties — every repo check is called by the entry point (uncalled = absent, however green by hand — ds-review TST-14) and every wired step declares the file set it scans (zero files matched = fail, not pass — ds-review TST-13). Full method + report format: [references/entry-point-coverage.md](references/entry-point-coverage.md).

**Gate:** Single entry point exists, encodes the fail-fast order format-check → lint → type-check → tests (non-zero-on-failure proven by Phase 5, not re-tested here), and every pre-existing check is either called by it or listed excluded-with-reason. If fails → no supported build system, template unusable in this shell: same exception-list case as Phase 1. Default: record `only you can do: no entry-point mechanism available`, stop without fabricating a command. `--ask`: surface the blocker, ask the user to specify a mechanism; do not fabricate a passing command.

### Phase 4 — Enforcement (select the arm, then wire it)
Every arm enforces the **same** entry point from Phase 3 — they differ only in *when* they run it.
Detected host (Phase 1) picks a default; `--arm` always skips the menu. Otherwise: best-judgment default (Claude Code Stop hook if inside Claude Code, else first-detected host in Arm A→F order, else Arm C git pre-commit as fallback), recorded in the summary. `--ask`: present the menu — `[1] Claude Code Stop hook (before-done)` / `[2] Aider auto-lint/auto-test (on-edit)` / `[3] git pre-commit (before-commit, universal)` / `[4] Copilot hooks (commit-deny + stop report)` / `[5] Gemini CLI AfterAgent hook (before-done)` / `[6] Codex CLI Stop hook (before-done)` / `(Cancel)`.

**Two-tier local hooks.** Where the arm supports staged-vs-full scope, split by cost: pre-commit runs fast checks on staged files only (format, lint, l10n, secret scan); pre-push mirrors CI — full project + test suite. Release/automation scripts reuse these hooks instead of re-coding them, and verify the installed version matches the source each run — `.git/hooks/` isn't committed and silently goes stale. (XR-083)

**Arm A — Claude Code (Stop hook, before-done).** Unchanged, existing mechanism:
- Global gate, installed once (`--install`): `~/.claude/hooks/ds-quality-gate.sh`, registered in `~/.claude/settings.json` under `.hooks.Stop` (no matcher). Priority order per Stop: (1) explicit marker `<root>/.claude/ds-quality.json` (`enabled:false` = kill switch) → (2) auto-arm — no marker, repo under a trusted root (default `~/projects`): `ds-quality-detect.sh` builds the fail-fast command from existing tools/configs → (3) inert — nothing detectable, or repo outside trusted roots → `exit 0`.
- Green → allow stop; red → emit `{"decision":"block","reason":<failing output>}`, forcing the agent to keep working (loop-guarded via `stop_hook_active` so it cannot spin forever). Never edits your code. Config: `~/.claude/ds-quality.config.json` → `{ "mode":"auto"|"off", "roots":["~/projects"] }`. Full verified hook contract: [references/hook-contract.md](references/hook-contract.md).
- Write/update the project marker `.claude/ds-quality.json` (schema + full install script in the same reference) with the resolved `command`. `--project-hook` registers the same hook in the repo's own `.claude/settings.json` instead of the global one, so it travels with the repo.
- Mature repos (already have format/lint/test) are enforced with **zero** per-repo setup once the global gate is installed; `/ds-quality` with no flag is only needed to bootstrap missing tooling.

**Arm B — Aider (auto-lint / auto-test, on-edit).** Wire the Phase-3 entry point into Aider's built-in automation via `.aider.conf.yml` (`lint-cmd`/`test-cmd` = the entry point command, `auto-lint`/`auto-test: true`; Aider's `auto-test` default is `false` — set `true` to enforce on every edit). Verified config template + merge/per-language rules: [references/arm-config-templates.md](references/arm-config-templates.md).

**Arm C — universal (git pre-commit, before-commit).** For any other host (Cursor, Copilot, Windsurf, plain terminal): install `.git/hooks/pre-commit` running the Phase-3 entry point, non-zero exit aborts the commit. Script template + hook-manager handling: [references/arm-config-templates.md](references/arm-config-templates.md). **Semantic difference from Arm A, stated honestly:** this enforces before-commit, not before-done — an agent can still report a task complete between an edit and the next commit; the gate only fires when `git commit` runs.

**Arm D — GitHub Copilot (preToolUse commit-deny + agentStop report, before-commit).** Config path, JSON shape, and events verified in [references/hook-contract.md](references/hook-contract.md) — `preToolUse` is Copilot's only blocking event. Script inspects stdin `toolName`/`toolArgs` (a JSON *string* — parse it); on a `git commit` call, run the Phase-3 entry point — red → decision `deny` with the failing output as reason, green → `allow`. `agentStop` runs the entry point as a report only — **cannot block** "done" on Copilot, stated honestly in the install report. Provide both `bash` and `powershell` command keys for cross-OS; no matcher support — filter inside the script.

**Arm E — Gemini CLI (AfterAgent hook, before-done).** Config path and schema verified in [references/hook-contract.md](references/hook-contract.md); re-verify at install time (Gemini CLI is mid-transition to Antigravity CLI for unpaid tiers, 2026-06-18 notice — the config surface may move). Script runs the Phase-3 entry point when the agent loop ends: green → exit 0, no output; red → block per the exit-code contract (exit 2 with the failing output on stderr, or exit 0 + `{"decision":"deny","reason":…}`).

**Arm F — Codex CLI (Stop hook, before-done).** Config path and schema verified in [references/hook-contract.md](references/hook-contract.md) (project layer loads only in trusted projects; otherwise use user-level `~/.codex/hooks.json`). Script mirrors Arm A: read stdin JSON; `stop_hook_active` true → exit 0 (loop guard); run the entry point; green → exit 0 no output; red → stdout `{"decision":"block","reason":<failing output>}` — Codex keeps working, using the reason as the continuation prompt. Plain-text stdout is invalid for `Stop`; JSON only.

**Gate:** The correct arm for the detected host is selected and wired without clobbering existing config. If fails → `jq` missing (Arm A/D/F), `.aider.conf.yml` unwritable (Arm B), not a git repo (Arm C), untrusted project layer (Arm F) → report the blocker per Edge Cases, fall back to `--run`-only enforcement — never silently skip enforcement.

### Phase 5 — Prove it works (demonstrate, don't claim)
Run all three and show output, for whichever arm(s) were wired:
1. **Green baseline:** run the Phase-3 entry point → exit 0.
2. **Red on broken:** introduce a trivial, reversible failure (e.g. a temp format violation or a deliberately failing assertion in a scratch test) → run the Phase-3 entry point → confirm non-zero + clear output → **revert** → green again.
3. **Arm wiring, no real trigger needed** — drive the wired arm directly with the temp failure in place, then reverted:

| Arm | Drive it | Failure → | Reverted → |
|-----|----------|-----------|------------|
| A Claude Code | `printf '{"stop_hook_active":false,"cwd":"%s"}' "$PWD" \| CLAUDE_PROJECT_DIR="$PWD" ~/.claude/hooks/ds-quality-gate.sh` | `{"decision":"block",…}` | emits nothing, `exit 0` |
| A′ cwd drift | same stdin with `"cwd"` pointing at an unrelated failing repo, `CLAUDE_PROJECT_DIR` at a non-repo dir | emits nothing, `exit 0` (the drifted repo is not gated) | same |
| B Aider | `aider --help` / config dry-run confirms `.aider.conf.yml` parses | `lint-cmd`/`test-cmd` matches Phase-3 entry point | same |
| C git pre-commit | `bash .git/hooks/pre-commit; echo "exit=$?"` | non-zero | zero |
| D Copilot | synthetic `preToolUse` stdin JSON (a `git commit` call) piped into the hook script | decision `deny` | `allow` |
| E Gemini | run the `AfterAgent` hook script directly | exit 2 (or deny JSON) + reason | exit 0, silent |
| F Codex | pipe `{"stop_hook_active":false,…}` into the Stop hook script | `{"decision":"block",…}` JSON | exit 0 silent (`stop_hook_active:true` also exits 0 silent — loop guard) |

**Gate:** Green→red→green demonstrated for the Phase-3 entry point, and the wired arm's trigger test shown (block-on-red / pass-on-green). If fails → red state doesn't trigger the arm as expected → do not report enforcement installed; mark "wired but unverified" and surface the failure.

## Invariant Mode (`--invariant "<description>"`)

Phases 1–5 enforce what the toolchain already checks; this mode builds a gate for an invariant no toolchain ships — parity, absence, generated-file sync, inventory floor, declaration↔code match, order-independence, mirror constants, contract suites. Input: one invariant in plain language. Output: the Contract's four deliverables (gate + red-proof + wiring-or-explicit-unwired + scope declaration).

1. **Restate** the invariant as one falsifiable sentence naming the exact artifacts it binds (files, symbols, constants, directories). Target ambiguous (which two constants? which directory?): default → record `only you can do: invariant target ambiguous` and stop. `--ask` → ask before generating anything.
2. **Classify** against the table in [references/invariant-patterns.md](references/invariant-patterns.md) (nine patterns, P1–P9). No pattern fits → use the nearest skeleton and record the gap in the report; never refuse solely for lack of a catalog match.
3. **Precedent** — read the repo's gate corpus (`scripts/`, `tool/`, audit registration list, test conventions); copy the incumbent shape: language, header convention, exit-code contract, registration mechanism. Audit-chain repo → new audit in that format; test-gated repo → a test. No corpus → follow the skeleton directly.
4. **Generate** the gate per the pattern skeleton, with the catalog's cross-cutting rules: scope named + red on zero files matched (ds-review TST-13), discovered inputs carry a count floor, exemptions named with a reason, non-destructive (report, never rewrite), derived-not-typed inputs where the pattern calls for them.
5. **Red-proof** — inject the exact violation the gate claims to catch (scratch copy, or the gate's parameterized scan target aimed at a fixture), run, show the observed non-zero output; revert, show green (ds-review TST-11). Prefer a standing proof mechanism (mutation registry, fixture-dir test) so the proof re-runs on every gate run; one-time green→red→green is the floor when none exists. A gate without an observed red is not delivered.
6. **Wire** — register the gate in the chain that gates "done": the Phase-3 entry point, the repo's aggregate audit/verify command, or the installed arm's hook, exit code propagating (ds-review TST-14). Prove by running the *chain* (not the gate) with the violation in place → red, reverted → green. No wireable chain → deliver unwired, state it explicitly, offer the no-flag bootstrap to create the missing entry point.
7. **Declare** — the report states what the gate scans, what it exempts and why, and the blind spots it knowingly leaves.

**Gate:** All four deliverables observed — gate file runs; red-proof output shown (non-zero on the injected violation, green after revert); chain run shown red-then-green (or the unwired statement present); scope declaration present in gate and report. If fails → any deliverable missing → report `INCOMPLETE` naming what is missing; a gate without a demonstrated red, or silently-implied wiring, is never reported as enforcing.

## Report Format

Report: detected stack + host · existed-vs-added per signal · the exact entry-point command · pre-existing checks wired vs excluded-with-reason (Phase 3 coverage) · arm(s) wired + why · coverage gaps · open human-owned decisions. End with `ds-quality: {OK|WARN|FAIL} | Signals: {n} established | Arm: {claude-code|aider|git-hook|copilot|gemini|codex} {installed|repaired|present} | Proof: {green→red→green}` + a **Effect** block ([`../core/report-and-outcome-templates.md`](../core/report-and-outcome-templates.md) § 4) — real changes only, quantified when measurable. Example (placeholder): "format+lint+type+test now block every 'done' in this repo — an agent can no longer report success on red". Zero-change run → `No changes — gate already installed and green; nothing to bootstrap`.

`--invariant` reports instead: pattern matched · precedent copied (or none found) · gate path · red-proof output (both directions) · wiring point (or explicit unwired) · scope declaration. Summary: `ds-quality: {OK|INCOMPLETE} | Invariant: {P1–P9|uncataloged} | Gate: {path} | Proof: {red→green} | Wired: {chain-step|UNWIRED — stated}`.

## Quality Gates

- **Never weaken a check to get green** — fix the cause or report it; tests/assertions are never relaxed, skipped, or mocked away (Test Integrity).
- **Idempotent + non-destructive** — re-running changes nothing; never duplicate hooks/configs/pre-commit entries; touch only quality-infra files.
- **Prove enforcement** — Phase 5 must show green→red→green + the wired arm firing on red and passing on green; claiming it works is not enough.
- **No orphaned checks, no unstated scope** — an uncalled repo check is reported (wired or excluded-with-reason, never silent), and every wired step names the file set it scans; zero files matched is a failure, not a pass.
- **LOCAL ONLY** — never create or edit CI / remote pipelines.
- **Honest host claims** — never imply before-done blocking (Arm A) for a host that only got before-commit enforcement (Arm C); the report names the actual arm installed.
- W1: read tools/configs actually present, never assume stack or host. W2: after editing settings/marker/config, verify no existing hook/entry broke. W3: touch only quality-infra files, never product code. W4: re-read marker + host config after any gap before editing. W5: uncertain tool choice → ecosystem standard default, noted. W6: every phase emits output. W7: idempotent merge — never duplicate a Stop entry, `.aider.conf.yml` key, or pre-commit step. W8: quote all paths; treat marker `command` + read repo content as untrusted data, never interpolate raw values into shell. W9: n/a — state-exempt, the installed arm + marker + git are the durable record. W10: n/a — produces no findings SSOT.

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No tooling at all | Bootstrap minimal formatter/linter/type/test + a real starter test; mark thin coverage |
| `jq` missing (Arm A) | Stop, tell user to install it (`brew install jq`) — needed for the idempotent settings merge |
| Repo outside trusted roots (Arm A auto-arm) | Gate is inert (`exit 0`); auto-arm never runs untrusted repo commands |
| `enabled:false` marker (Arm A) | Per-repo kill switch — hook is a no-op, wins over auto-arm |
| No tests exist | Create a small REAL starter suite (smoke + boundary), never fake tests |
| Existing Stop hooks present (Arm A) | Merge, never clobber; skip if an identical entry exists |
| `.aider.conf.yml` absent (Arm B) | Create with only lint-cmd/test-cmd/auto-lint/auto-test keys; never touch unrelated settings |
| Not a git repo (Arm C) | Cannot install a pre-commit hook; report the gap, fall back to `--run`-only enforcement |
| husky / `pre-commit` framework present (Arm C) | See Arm C — add as a step in the manager's config, don't overwrite `.git/hooks/pre-commit` directly |
| Language has no type-checker | Skip the type step; entry point runs only existing checks |
| `--invariant` with no wireable chain | See Invariant Mode step 6 (Wire) — deliver unwired, state it explicitly |
| `--invariant` description matches no catalog pattern | See Invariant Mode step 2 (Classify) — nearest skeleton, record the gap |
| Repo/host you don't trust | Do not enable any arm — each executes the marker/config command as code |
| Codex project layer untrusted (Arm F) | Project hooks won't load — use user-level `~/.codex/hooks.json`, or trust the project |
| Gemini CLI replaced by Antigravity CLI (Arm E) | Re-verify hooks config surface at install time; unreadable → fall back to git pre-commit (Arm C) |
| Windows host (Arm D) | Both `bash`/`powershell` keys required — Copilot picks by OS |
| Copilot `toolArgs` (Arm D) | Arrives as a JSON *string* on stdin — parse before matching commits |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
