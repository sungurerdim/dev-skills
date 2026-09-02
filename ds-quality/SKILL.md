---
name: ds-quality
description: Quality-by-Mechanism — installs a deterministic, local, no-CI quality gate (format → lint → type → test) enforced via a host-appropriate mechanism (Claude Code / Codex CLI / Gemini CLI stop-time hooks, Copilot commit-deny hook, Aider auto-lint/test, or git pre-commit). `--invariant` builds a custom gate from a plain-language invariant description (mirror constants stay equal, pattern X never reappears, generated file stays in sync, inventory never drops below N, docs match code, two implementations agree) — delivered red-proven, chain-wired, scope-declared. Use when the user asks to enforce quality, set up a quality gate, block "done" until checks pass without relying on CI, or turn a described invariant into a mechanical check.
---

# /ds-quality

Agents promise "done" without proof; quality ends up depending on whether an
instruction was followed, not on a mechanism. This skill installs a **deterministic, local,
no-CI** quality gate — one entry point (format → lint → type → test) — then wires
it into whichever host you use: a Claude Code Stop hook, Aider's auto-lint/auto-test,
or a universal git pre-commit hook. Its `--invariant` mode extends the same principle
past the toolchain: any invariant the user can describe becomes a generated, red-proven,
chain-wired check (see Invariant Mode).

**Quality-by-Mechanism** — quality is guaranteed by a verify-loop that runs real checks, not by hoping an agent obeys.

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

- Installs a deterministic, local, no-CI quality gate: one entry point (format → lint → type → test) + a host-appropriate enforcement arm that blocks "done" (or the commit) until it passes green; bootstraps missing tooling when asked.
- **Enforcement mechanism is host-dependent — no single claim covers every host.** Stop-time (full strength — blocks "done" itself): Claude Code Stop hook (existing, unchanged) · Codex CLI `Stop` hook · Gemini CLI `AfterAgent` hook. Edit-time: Aider `.aider.conf.yml` auto-lint/auto-test. Commit-time (weaker — an agent can still narrate "done" between an edit and the next commit; documented honestly, not hidden): GitHub Copilot `preToolUse` commit-deny hook · git `pre-commit` hook (universal fallback for Cursor, Windsurf, plain terminal).
- Modes are flag-disambiguated (`--install`/`--run`/`--check`/`--status`/`--disable`/`--project-hook`/`--uninstall`/`--arm`/`--auto`/`--invariant`); no flag = bootstrap this repo. When invoked with no flag and intent is ambiguous, present an up-front menu covering every mode (`(recommended)` default + `(Cancel)`). `--auto` skips this menu too — selects the skill's best-judgment default (bootstrap this repo, i.e. the no-flag behavior) without prompting.
- LOCAL ONLY — never creates or edits CI / remote pipelines. Idempotent (safe to re-run, never duplicates hooks). Non-destructive — never weakens, skips, or mocks-away checks to get green.
- Runs the passes via the tools already present; delegates one-shot fixing of what they report to ds-fix. This skill owns the *gate + enforcement mechanism*, not the fixes.
- `--invariant "<description>"` turns ONE described invariant into four inseparable deliverables: the gate (script or test, in the repo's incumbent gate format), a red-proof (the gate observed non-zero on an injected violation, green on revert), chain wiring (or an explicit unwired statement — never implied enforcement), and a scope declaration (what it scans, what it exempts, its blind spots). Delivery missing any of the four is reported `INCOMPLETE`, never `OK`.
- Touch only quality-infra files — configs, scripts, `.claude/settings*.json`, `.aider.conf.yml`, `.git/hooks/pre-commit`, the global hook, the project marker, gates generated by `--invariant` (a script/test file + its chain registration), and (only if no tests exist) a real starter test. Never delete or rewrite existing source or tests beyond the task.
- Any arm executes a marker/config-resolved command as shell/code on every trigger in opted-in repos — treat that command as code: review/commit it like any project script; never enable an arm in a repo you don't trust.
- **State-exempt — zero footprint.** Idempotent and local/git-driven; the installed hook/config + the project marker + git are the durable record. Writes no `ds/audit/` state, no temp files.
- Standalone. Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->

## Arguments

| Flag | Effect |
|------|--------|
| `--install` | One-time global install/refresh of the Claude Code arm: gate + detector scripts, `.hooks.Stop` registration, default `auto` config. No project changes. |
| (none) | **Bootstrap THIS repo's missing tooling** (formatter/linter/type/test + a real starter test if none), then select and wire an enforcement arm. Detect → establish signals → entry point → select arm → prove (Phase 5). |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |
| `--run` / `--check` | Run this repo's resolved quality command now (marker → else auto-detect) and report; no setup |
| `--status` | Report mode/roots, what auto-arm resolves here, which arm(s) are wired, and global install state |
| `--arm <claude-code\|aider\|git-hook\|copilot\|gemini\|codex>` | Force a specific enforcement arm instead of auto-detecting the host; skips the selection menu |
| `--invariant "<description>"` | Build a custom gate from a plain-language invariant description: classify against the pattern catalog → copy the repo's own gate precedent → generate → red-proof → wire into the chain → declare scope. See Invariant Mode |
| `--disable` | Write `.claude/ds-quality.json` `{enabled:false}` — per-repo kill switch (overrides auto-arm) |
| `--project-hook` | Register the Claude Code Stop hook in THIS repo's `.claude/settings.json` instead of using the global hook |
| `--uninstall` | Remove the global hook registration + scripts + config (or, with `--project-hook`, the repo's Stop entry; or the `git-hook`/Aider config lines, per `--arm`) |

Set `mode`/`roots` by editing `~/.claude/ds-quality.config.json`; `mode:"off"` disables the Claude Code auto-arm globally while leaving explicit markers working.

## Delegation

**Owns:** quality-gate-setup, verify-loop-enforcement, hook-install | **Delegates:** ds-fix → verify-loop toolchain passes; ds-test → starter-suite generation when the project has zero tests | **Receives:** ds-rig → quality-gate wiring after rig setup

## Execution Flow

Detect toolchain → Establish quality signals → Single entry point → Enforcement (select arm) → Prove it works

### Phase 1 — Detect toolchain (read, don't assume)
- Identify language(s) + package manager from manifests/lockfiles actually present: `package.json`(+lockfile), `pyproject.toml`/`requirements*.txt`/`setup.py`, `pubspec.yaml`, `go.mod`, `Cargo.toml`, `Makefile`.
- Identify which quality tools are **already** configured (formatter, linter, type-checker, test runner) — read configs + lockfiles, don't guess.
- Identify the host: `.aider.conf.yml` or an active Aider session → Aider; `~/.claude/` present / running inside Claude Code → Claude Code; `.codex/` or `~/.codex/` → Codex CLI; `.gemini/` or `~/.gemini/` → Gemini CLI; `.github/hooks/` or `~/.copilot/` → Copilot; none → universal (git pre-commit).
- **Report the detected stack + host before changing anything.**

**Gate:** Stack, existing tooling, and host are all identified from real manifests/lockfiles/configs — never assumed. If fails → no manifest/lockfile detected (unknown stack) → ask the user which language/toolchain to target before proceeding; do not guess. **Under `--auto`:** this blocker matches the publish/irreversible exception list (no value inferable from the repo) — skip the ask, stop this phase, and record `needs-human: unknown stack — specify language/toolchain`.

### Phase 2 — Establish the quality signals
For the detected stack (see [references/toolchains.md](references/toolchains.md) for exact commands + bootstrap), ensure each EXISTS and RUNS — run each tool's check command once and observe the exit code, never infer from config presence; create minimal **standard** config only where missing, preferring tools already in the lockfile:
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

The entry point runs only checks that actually exist for the detected stack. Never invent a check that has no tool. Its runnability and non-zero-on-failure behavior are proven by Phase 5's green→red→green run — that run's observed output is the evidence; no separate verification here.

**Entry-point coverage (run before wiring the arm).** Two properties, both mechanical:

1. **Every check in the repo is called by the entry point.** Enumerate what already exists — `scripts/`+`tools/` executables, `package.json` scripts, `Makefile` targets, `.pre-commit-config.yaml` hooks, audit/verify scripts, test directories the runner's discovery pattern does not reach — and grep the entry point for each by name. Uncalled → wire it in, or record it as a deliberate exclusion **at the entry point** with the condition under which it does run (platform-pinned goldens, a slow suite moved to pre-push). A check nothing calls counts as absent, however green it looks when run by hand (ds-review TST-14). Callers must propagate the exit code — a step whose result is discarded is uncalled in effect.
2. **Every check declares the file set it scans.** Each wired step passes an explicit path/glob (or prints the file count it processed) instead of relying on the invocation directory; a step that matches zero files fails rather than passes, and a repo-wide rule's scope is compared against `git ls-files` once, so a directory added later joins the scan or breaks the gate (ds-review TST-13).

Report both lists — wired / excluded-with-reason — in the run report; they are the entire coverage claim this skill is allowed to make.

**Gate:** Single entry point exists, encodes the fail-fast order format-check → lint → type-check → tests (non-zero-on-failure is proven by Phase 5, not re-tested here), and every pre-existing check is either called by it or listed as an excluded-with-reason line. If fails → no supported build system present and the template is unusable in this shell → surface the blocker and ask the user to specify an entry-point mechanism; do not fabricate a passing command. **Under `--auto`:** same exception-list case as Phase 1 — record `needs-human: no entry-point mechanism available` instead of asking, and stop this phase without fabricating a command.

### Phase 4 — Enforcement (select the arm, then wire it)
Every arm enforces the **same** entry point from Phase 3 — they differ only in *when* they run it.
Detected host (Phase 1) picks a default; if more than one applies or detection is ambiguous, present
the menu: `[1] Claude Code Stop hook (stop-time; recommended if using Claude Code)` / `[2] Aider auto-lint/auto-test (edit-time)`
/ `[3] git pre-commit hook (commit-time, universal — works with any host)` / `[4] Copilot hooks (commit-deny + stop report)`
/ `[5] Gemini CLI AfterAgent hook (stop-time)` / `[6] Codex CLI Stop hook (stop-time)` / `(Cancel)`. `--arm` skips the menu. `--auto` also skips the menu — when detection is ambiguous, picks the best-judgment default (Claude Code Stop hook if running inside Claude Code, else the first-detected host in Arm A→F order, else Arm C git pre-commit as the universal fallback), recording the choice in the summary.

**Two-tier local hooks (design refinement).** Where the arm supports staged-vs-full scope, split by cost: pre-commit runs fast checks on staged files only (format, lint, l10n, secret scan); pre-push mirrors CI — full project + full test suite. **Hook reuse + version sync:** release/automation scripts reuse these hooks instead of re-coding them, and verify the installed hook version matches the versioned source at each run — `.git/hooks/` isn't committed and silently goes stale. (XR-083)

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

**Arm D — GitHub Copilot (preToolUse commit-deny + agentStop report, commit-time).** Repo-level
`.github/hooks/ds-quality.json` (user-level alternative: `~/.copilot/hooks/`), format `{"version":1,"hooks":{...}}`:
- `preToolUse` entry: script reads stdin JSON, inspects `toolName`/`toolArgs` (`toolArgs` is a JSON *string* — parse it), and when the tool call is a `git commit`, runs the Phase-3 entry point; red → output decision `deny` with the failing output as reason, green → `allow`. `preToolUse` is Copilot's only blocking event.
- `agentStop` entry: runs the entry point and surfaces failures as a report — **cannot block** "done" on Copilot; stated honestly in the install report.
- Provide both `bash` and `powershell` keys so the hook runs on macOS/Linux/Windows. No matcher support — filter inside the script.

**Arm E — Gemini CLI (AfterAgent hook, stop-time).** Project `.gemini/settings.json` (user-level: `~/.gemini/settings.json`), schema `hooks.AfterAgent[].hooks[] = {name, type:"command", command, timeout}`:
- Script runs the Phase-3 entry point when the agent loop ends. Green → exit 0, no output. Red → block per the exit-code contract: exit 2 with the failing output on stderr (aborts the stop), or exit 0 + `{"decision":"deny","reason":…}` JSON.
- Re-verify the hook schema against the official hooks doc at install time (Gemini CLI is mid-transition to Antigravity CLI for unpaid tiers, 2026-06-18 notice — the config surface may move).

**Arm F — Codex CLI (Stop hook, stop-time).** `<repo>/.codex/hooks.json` (project layer loads only in trusted projects; user-level: `~/.codex/hooks.json`), schema `hooks.Stop[].hooks[] = {type:"command", command, statusMessage}`:
- Script contract mirrors Arm A: read stdin JSON; `stop_hook_active` true → exit 0 (loop guard); run the entry point; green → exit 0 with no output; red → stdout `{"decision":"block","reason":<failing output>}` — Codex keeps working, using the reason as the continuation prompt. Plain-text stdout is invalid for `Stop`; emit JSON only.

**Arm G — optional, project-conditional (known-false-claims denylist).** When a shipped user-visible claim (marketing/docs/UI copy) has once been wrong, add it as multilingual regex to a permanent denylist scanned at commit/push time by whichever arm is wired; the same falsehood must not re-enter through another locale or PR — the list only grows. (XR-094)

**Gate:** The correct arm for the detected host is selected and wired without clobbering existing config. If fails → `jq` missing (Arm A/D/F), `.aider.conf.yml` unwritable (Arm B), not a git repo (Arm C), or untrusted project layer (Arm F) → report the specific blocker per Edge Cases, fall back to `--run`-only enforcement — never silently skip enforcement.

### Phase 5 — Prove it works (demonstrate, don't claim)
Run all three and show output, for whichever arm(s) were wired:
1. **Green baseline:** run the Phase-3 entry point → exit 0.
2. **Red on broken:** introduce a trivial, reversible failure (e.g. a temp format violation or a deliberately failing assertion in a scratch test) → run the Phase-3 entry point → confirm non-zero + clear output → **revert** → green again.
3. **Arm wiring, no real trigger needed:**
   - Arm A: drive the hook directly —
     ```bash
     printf '{"stop_hook_active":false,"cwd":"%s"}' "$PWD" | ~/.claude/hooks/ds-quality-gate.sh; echo "exit=$?"
     printf '{"stop_hook_active":true,"cwd":"%s"}'  "$PWD" | ~/.claude/hooks/ds-quality-gate.sh; echo "exit=$?"
     ```
     With the temp failure in place, the first call must emit `{"decision":"block",…}`; reverted, it must emit nothing and `exit 0`.
   - Arm B: confirm `.aider.conf.yml` parses (`aider --help` or a config dry-run) and the configured `lint-cmd`/`test-cmd` matches the Phase-3 entry point.
   - Arm C: `bash .git/hooks/pre-commit; echo "exit=$?"` with the temp failure in place → non-zero; reverted → zero.
   - Arm D: pipe a synthetic `preToolUse` stdin JSON (a `git commit` tool call) into the hook script → with the temp failure: decision `deny`; reverted: `allow`.
   - Arm E: run the AfterAgent hook script directly → with the temp failure: exit 2 (or deny JSON) + reason; reverted: exit 0, silent.
   - Arm F: pipe `{"stop_hook_active":false,…}` into the Stop hook script → with the temp failure: `{"decision":"block",…}` JSON; with `stop_hook_active:true`: exit 0 silent (loop guard); reverted: exit 0 silent.

**Gate:** Green→red→green demonstrated for the Phase-3 entry point, and the wired arm's trigger test shown (block-on-red / pass-on-green). If fails → red state doesn't trigger the arm as expected → do not report enforcement as installed; mark it "wired but unverified" and surface the specific failure.

## Invariant Mode (`--invariant "<description>"`)

Phases 1–5 enforce what the toolchain already checks; this mode builds a gate for an
invariant no toolchain ships — parity, absence, generated-file sync, inventory floor,
declaration↔code match, order-independence, mirror constants, contract suites. Input: one
invariant described in plain language. Output: the four deliverables the Contract names
(gate + red-proof + wiring-or-explicit-unwired + scope declaration).

1. **Restate** the invariant as one falsifiable sentence naming the exact artifacts it
   binds (files, symbols, constants, directories). Target ambiguous (which two constants?
   which directory?) → ask before generating anything; under `--auto` → record
   `needs-human: invariant target ambiguous` and stop.
2. **Classify** against the table in [references/invariant-patterns.md](references/invariant-patterns.md)
   (nine patterns, P1–P9). No pattern fits → use the nearest skeleton and record the gap
   in the report; never refuse solely for lack of a catalog match.
3. **Precedent** — read the repo's existing gate corpus (`scripts/`, `tool/`, the audit
   runner's registration list, the test suite's conventions) and copy the incumbent shape:
   language, header/comment convention, exit-code contract, registration mechanism. A repo
   with an audit chain gets a new audit in that chain's own format; a repo whose gates are
   tests gets a test. No corpus exists → follow the pattern skeleton directly.
4. **Generate** the gate per the pattern skeleton, with the catalog's cross-cutting rules:
   scope named in the gate and red on zero files matched (ds-review TST-13), discovered
   inputs carry a count floor, exemptions listed by name with a reason, non-destructive
   (report, never rewrite), derived-not-typed inputs where the pattern calls for them.
5. **Red-proof** — inject the exact violation the gate claims to catch (scratch
   worktree/copy, or the gate's parameterized scan target aimed at a fixture), run the
   gate, show the observed non-zero output; revert, show green (ds-review TST-11). Prefer
   the repo's standing proof mechanism (mutation registry, fixture-dir suite test) so the
   proof re-runs on every gate run; the one-time green→red→green is the floor when no such
   mechanism exists. A gate without an observed red is not delivered.
6. **Wire** — register the gate in the chain that gates "done": the Phase-3 entry point,
   the repo's aggregate audit/verify command, or the installed arm's hook, with the exit
   code propagating (ds-review TST-14). Prove the wiring by running the *chain* (not the
   gate directly) with the violation in place → red, reverted → green. No wireable chain
   exists → deliver the gate unwired, state that explicitly in the report, and offer the
   no-flag bootstrap to create the missing entry point.
7. **Declare** — the report states what the gate scans, what it exempts and why, and the
   blind spots it knowingly leaves.

**Gate:** All four deliverables observed — gate file runs; red-proof output shown (non-zero on the injected violation, green after revert); chain run shown red-then-green (or the unwired statement present); scope declaration present in both the gate and the report. If fails → any deliverable missing → report `INCOMPLETE` naming exactly what is missing; a gate without a demonstrated red, or with silently-implied wiring, is never reported as enforcing.

## Report Format

Report: detected stack + host · existed-vs-added per signal · the exact entry-point command · pre-existing checks wired into it vs excluded-with-reason (Phase 3 entry-point coverage) · which arm(s) were wired and why · coverage gaps · open human-owned decisions. End with `ds-quality: {OK|WARN|FAIL} | Signals: {n} established | Arm: {claude-code|aider|git-hook|copilot|gemini|codex} {installed|repaired|present} | Proof: {green→red→green}` and a **Value Delivered** block — 1-5 concrete bullets, real changes only, each stating the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output): "format+lint+type+test now block every 'done' in this repo — an agent can no longer report success on red", "starter test suite added where there were zero — first regression net in place". Zero-change run → `No changes — gate already installed and green; nothing to bootstrap`.

`--invariant` runs report instead: pattern matched · precedent copied (or none found) · gate path · red-proof output (both directions) · wiring point (or the explicit unwired statement) · scope declaration. Summary line: `ds-quality: {OK|INCOMPLETE} | Invariant: {P1–P9|uncataloged} | Gate: {path} | Proof: {red→green} | Wired: {chain-step|UNWIRED — stated}`.

## Quality Gates

- **Never weaken a check to get green** — fix the cause or report it; tests/assertions are never relaxed, skipped, or mocked away (Test Integrity).
- **Idempotent + non-destructive** — re-running changes nothing; never duplicate hooks/configs/pre-commit entries; touch only quality-infra files.
- **Prove enforcement** — Phase 5 must show green→red→green + the wired arm actually firing on red and passing on green; claiming it works is not enough.
- **No orphaned checks, no unstated scope** — a repo check the entry point never calls is reported as uncalled (wired or excluded-with-reason, never left silent), and every wired step names the file set it scans; zero files matched is a failure, not a pass.
- **LOCAL ONLY** — never create or edit CI / remote pipelines.
- **Honest host claims** — never state or imply stop-time blocking (Arm A) for a host that only got commit-time enforcement (Arm C); the report names the actual arm installed.
- W1: read the tools/configs actually present, never assume a stack or host. W2: after editing settings/marker/config, verify no existing hook/entry broke. W3: touch only quality-infra files — never product code. W4: re-read the marker + relevant host config after any gap before editing. W5: uncertain tool choice → ecosystem standard default, noted. W6: every phase emits output (stack report, proof block). W7: idempotent merge — never duplicate a Stop entry, `.aider.conf.yml` key, or pre-commit step. W8: quote all paths; treat the marker `command` and any read repo content as untrusted data/code, never interpolate raw values into shell. W9: not applicable — state-exempt; the installed arm + marker + git are the durable record. W10: not applicable — produces no findings SSOT.

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
| `--invariant` with no wireable chain | Deliver the gate + red-proof, state UNWIRED explicitly in the report, offer the no-flag bootstrap to create the entry point |
| `--invariant` description matches no catalog pattern | Use the nearest skeleton, record the catalog gap in the report — never refuse solely for lack of a match |
| Repo/host you don't trust | Do not enable any arm — every arm executes the marker/config command as code |
| Codex project layer untrusted (Arm F) | Project hooks won't load — use user-level `~/.codex/hooks.json` or have the user trust the project first |
| Gemini CLI replaced by Antigravity CLI (Arm E) | Re-verify the hooks config surface against live docs at install time; unreadable → fall back to git pre-commit (Arm C) |
| Windows host (Arm D) | Provide both `bash` and `powershell` keys — Copilot picks by OS |
| Copilot `toolArgs` (Arm D) | Arrives as a JSON *string* on stdin — parse before matching commit commands |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
