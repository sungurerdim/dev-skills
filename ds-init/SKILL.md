---
name: ds-init
description: Project scaffolding — generate production-ready project structure for any stack. Use when starting a new project or bootstrapping a repo skeleton.
---

# /ds-init

New projects start with no CI, no test setup, no linting, and inconsistent structure. This skill scaffolds all of it from day one.

**Project Scaffolding** — Generate production-ready project structure for any stack.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

User runs `/ds-init`, or asks to scaffold/bootstrap/initialize a new or greenfield project.

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "scaffold a new {framework} project" | "audit existing project for health" (→ ds-blueprint) |
| "create CI / Docker / test boilerplate from zero" | "deploy the app" (→ ds-deploy) |
| "initialize project structure for {type}" | "add a feature to existing app" (→ implement directly) |
| "bootstrap this repo's tooling configs" | "set up my machine's AI toolset" (→ ds-rig) |
| "bootstrap with sensible defaults" | "research which framework to pick" (→ ds-research) |

## Contract

**Dimensions:** none (carrier)

- Generates project structure, a local quality gate, test setup, Docker stubs, editor config, env templates
- Detects intent (web / api / mobile / cli / library / monorepo) from input or codebase signals
- Generates only files relevant to detected type — no unnecessary boilerplate
- Respects existing files — overwrites only with explicit user confirmation
- Standalone. Uses blueprint when available to select scaffold template; asks user when absent.
- Minimal liability + minimum deps + maximum automation: well-known config patterns, no custom security code, minimal starting deps (rationale documented), lint/format/type/test wired from day one via a local quality gate. Prefer stdlib and established minimal libraries.
- Local gate first: wires a local quality gate by default (advisory handoff to `/ds-quality`; absent → a generated `scripts/quality.sh`-style chain from `../core/toolchains.md`) instead of CI; CI workflow files generate only under `--full`. A privacy-policy stub + data-inventory file generate only when `pii=yes`; otherwise skipped with a one-line note.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Exempt from state protocol:** idempotent scaffolding — re-running on the same project naturally resumes because existing files are skipped. No `ds/audit/init.json`.

## Arguments

| Flag | Effect |
|------|--------|
| `--type={type}` | Project type: web, api, mobile, cli, library, monorepo, desktop |
| `--stack={stack}` | Technology stack: next, react, vue, svelte, astro, flutter, expo, fastapi, express, hono, bun, go, rust (detection/init/gate chain per stack: [references/rules-scaffold.md](references/rules-scaffold.md) § Stack Scaffold Commands) |
| `--minimal` | Bare minimum structure only |
| `--full` | Full production structure — adds CI workflow files, Docker, docs on top of the default (quality gate, tests, editor/lint/type configs always generate; CI files only under this flag) |
| `--research` | Look up comparable scaffolds and current framework/tool versions before generating. Default: scaffold from `../core/toolchains.md` only, no network calls. |
| `--preview` | Show what would be created without writing files |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Default: type resolves from existing signals when present, else the lowest-blast-radius fallback (both Phase 1) — recorded in the summary. `--type` skips resolution entirely. `--ask`: the menu below (question: "What type of project are you scaffolding?", no `(recommended)` — type is user-driven).

| Option | What it does |
|--------|--------------|
| Web App | React / Next.js / Vue / Svelte frontend |
| API | REST / GraphQL backend service |
| Mobile | Flutter / React Native mobile app |
| CLI | Command-line tool |
| Library | Reusable package / module |
| Monorepo | Multi-package workspace |
| Desktop | Electron / Tauri desktop app |
| (Cancel) | Exit without action |

## Scopes

Exactly one type scaffolds per run — types are mutually exclusive, unlike an audit skill's independently-triggered scopes. `unknown` (empty, signal-less directory) never excludes — it falls to `--ask`'s menu or the default's boring-technology/library resolution (Phase 1).

| Scope | Runs when (signal) | Otherwise | Core Structure | CI | Docker | Test Setup |
|-------|---------------------|-----------|----------------|----|----|-----------|
| web | `ui=web` detected, or selects Web App | N/A | `src/`, `public/`, `pages/` | lint + test + build | Multi-stage nginx | Jest/Vitest + Playwright |
| api | `api≠none` detected, or selects API | N/A | `src/routes/`, `src/services/` | lint + test + build | Multi-stage runtime | pytest/Jest + integration |
| mobile | `mobile≠none` or `platforms` includes ios/android, or selects Mobile | N/A | `lib/features/`, `test/` | lint + test + build (AAB/IPA) | N/A | Unit + widget + integration |
| cli | `platforms` includes cli, or selects CLI | N/A | `src/commands/`, `bin/` | lint + test + build | Single-stage | Unit + integration |
| library | `platforms` includes library, or selects Library | N/A | `src/lib/`, `examples/` | lint + test + build + publish | N/A | Unit + integration |
| monorepo | workspace manifest detected (`lerna.json`/`nx.json`/`turbo.json`/multiple `package.json`), or selects Monorepo | N/A | `packages/`, `apps/` | per-package + affected detection | Per-package | Per-package + E2E |
| desktop | Electron/Tauri/Flutter-desktop target detected, or selects Desktop | N/A | `src/` (+ `src-tauri/` for Tauri) | lint + test + build + package | N/A | Unit + E2E (Playwright/WebdriverIO) |

## Delegation

**Owns:** scaffolding, project-init, ci-bootstrap, editor-config | **Delegates:** none | **Receives:** ds-ship → scaffold-stage sequencing

## Execution Flow

Setup → Detect → Generate → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

**Upstream artifacts:** Profile → Type + Stack, Toolchain. Findings() → verify + use. Absent → own analysis.

1. `--type` and `--stack` provided → proceed directly, skip resolution below.
2. Profile has `Type`/`Stack` → use them. Absent → existing files → scan for signals (`package.json`, `pubspec.yaml`, `go.mod`, `Cargo.toml`).
3. Profile `Signals: pii=` → use it; absent → detect (`../core/signal-inventory.md`: fields named email/phone/address/dob/ssn/national_id/ip, a user table, an analytics SDK, a contact form, or stated in the request) → `pii=yes`/`pii=no`/`unknown`, recorded for Phase 3's privacy-stub step.

**Default:** type and stack resolve from existing signals when present (step 2); a genuinely empty, signal-less directory with no `--type`/`--stack` has no evidence to judge from, so it resolves to the lowest-blast-radius default — `library`, boring-technology stack for the detected language, or `Decided without asking — say if wrong: type=library` when even the language is unknown — recorded in the summary. `--minimal`/`--full` resolves to its stated default (`full`). **Boring-technology default (advisory):** absent an explicit stack choice, resolve to proven mainstream over novel — every company has roughly three "innovation tokens" to spend on unproven tech (McKinley); "boring" ≠ "bad".

**`--ask`:** empty directory or no signals → interactive type-selection menu (question: "What type of project are you scaffolding?", no `(recommended)` — type is user-driven). Ask for stack choice within the selected type — the boring-technology default still applies with no preference; an explicit choice always wins without debate. Ask `--minimal` or `--full`? (`full` marked `(recommended)`).

**Gate:** Project type and stack confirmed. If fails → under `--ask`, no response after two attempts: exit cleanly with "ds-init: ABORTED — project type required", generate no files; the default path never hits this — it always resolves a type per the Default paragraph.

### Phase 2: Detect Existing Setup

1. Scan for existing config files (`.eslintrc`, `tsconfig`, `Dockerfile`, `.github/workflows`, etc.) → mark SKIP.
2. Report: "Found {n} existing config files — these will be preserved."
3. **Checkpoint:** directory is a git repo (`git rev-parse --is-inside-work-tree` → `true`) → `git status --porcelain`. Non-empty: Default proceeds only when the pre-existing dirty state stays untouched by this skill's writes — otherwise stop, record `only you can do`; never scaffold over uncommitted unrelated changes silently. `--ask`: ask **Commit first (recommended) / Stash / Proceed anyway** (risk: scaffold writes interleave with uncommitted work, single-command rollback is lost). Not a repo, or clean tree → proceed either way.

**Gate:** Existing-config scan reported ("Found {n} existing config files"); every conflict carries an overwrite/skip decision. If fails → default SKIP for that file (preserve existing), announce, continue scanning — same safe default whether resolved silently (default) or via no-response under `--ask`; re-run after resolving conflicts.

### Phase 3: Generate Structure

Per [references/rules-scaffold.md](references/rules-scaffold.md). Generate independent files in parallel. `--research`: look up comparable scaffolds and current versions first, prefer their findings. Default: generate from `../core/toolchains.md` and the steps below only — zero network calls.

1. **Directory structure** for selected type (see Scopes table above).
2. **Generated files per stack:** editor config (`.editorconfig`, optional `.vscode/settings.json`); linter/formatter/type-checker configs — tool choice and check/fix commands per stack: `../core/toolchains.md` Default column (existing config or lockfile entry always wins); type config (`tsconfig.json` node, `pyproject.toml [tool.mypy]` python, etc.) matching the chosen type-checker; `.gitignore` (comprehensive per stack); `.env.example` with documented variables — NEVER `.env` with real values.
3. **Local quality gate:** `/ds-quality` present → delegate, note in the generated README that it wires the gate on first run; absent → generate an executable `scripts/quality.sh` chaining the stack's `{check-cmd}` from `../core/toolchains.md` (format → lint → type → test, fail-fast), documented as "run before every commit".
4. **Privacy stub** `[pii=yes]`: generate a privacy-policy stub (data categories, purpose, retention, third-party sharing, contact — placeholder values) and a data-inventory file (field | source | purpose | retention | legal basis). `[pii=no or unknown]`: skip, one-line note ("Privacy stub skipped — no personal-data signal detected").
5. **CI workflow** `[--full]`: Lint → Test → Build pipeline, SHA-pinned actions — exact shape in [references/rules-scaffold.md § Generation Detail](references/rules-scaffold.md).
6. **Docker files** (if `--full` or API/web type): Dockerfile + compose files — exact shape in [references/rules-scaffold.md § Generation Detail](references/rules-scaffold.md).
7. **Test setup:** test runner config + example test file (pattern demonstration) + coverage config.
8. **Documentation stubs:** `README.md` (project name, setup, scripts, quality-gate usage); `CONTRIBUTING.md` stub (if `--full`); `LICENSE` file prompt.

**Gate:** All files created. If fails → per-file write error: skip that file, record `failed (write error)`, surface the error, continue with remaining files; re-run after resolving permissions (idempotent — existing files preserved).

### Phase 4: Post-Generate Verification

1. Generated files syntactically valid: each `.json` parses (`python3 -m json.tool < {file}` → exit 0), each `.yml`/`.yaml` parses (`python3 -c 'import yaml,sys;yaml.safe_load(sys.stdin)' < {file}` → exit 0); parser unavailable → mark that file `unverified (no parser)`.
2. `.gitignore` coverage: `grep -F '{pattern}' .gitignore` → match, once per required pattern (`.env`, `node_modules`/build artifacts, `coverage/`, OS/IDE files).
3. `.env.example` has no real secrets: scan against `../core/secret-patterns.md`'s content regexes → no match. Unmatched but suspicious (long high-entropy string assigned to a var) → flag `unverified — manual check`.
4. CI workflow (when generated, `--full`) references correct paths and commands (judgment review against the generated structure).
5. **Twelve-Factor checks** ([../core/principles.md §3](../core/principles.md)): `Dockerfile` logs to stdout (`grep -n 'logfile' Dockerfile` → no output), binds via `$PORT` (no hardcoded ports), non-root `USER` with `HEALTHCHECK` (`grep -cE '^(USER|HEALTHCHECK)' Dockerfile` → `2`); `docker-compose.yml` uses `restart: unless-stopped`, externalizes config via `environment:` from `.env`; every CI action SHA-pinned (`grep -nE '@(v[0-9]+|main|master)' .github/workflows/*.yml` → no output).
6. **Mechanical Done Gate:** the scaffold's own toolchain is `{check-cmd}` — the exact format/lint/type/test commands the generated configs define. Deps installed (or installable with one approved command) → run `{check-cmd}` once; example test + lint passing green proves the scaffold works. Red → fix the file, re-run the same command (≤3 attempts); still red → record `failed (mechanical gate)` with the captured error, surface HIGH. Not runnable here (no install approval, offline) → mark every config `unverified — {check-cmd} not run`, list the commands under Next steps, never claim the scaffold verified.

**Gate:** All verifications pass, and `{check-cmd}` ran green or every skipped check is explicitly marked `unverified`. If fails → fix inline (correct YAML, add missing `.gitignore` entry, remove hardcoded port), re-verify once; not auto-fixable (e.g. SHA-pin needs network lookup) → insert `# TODO: SHA-pin this action`, mark `partial`, surface HIGH — do not block summary.

### Phase 5: Needs-Approval Review [--ask, needs_approval > 0]

Default: every needs-approval item resolves inline by best judgment (`fixed`/`failed`) using the same impact/effort/risk reasoning an approval block would show; items matching the publish/irreversible exception list become `skipped (only you can do)` instead; this step does not display. `--ask`: present each item compactly (`[severity] title — file:line`) grouped by severity with counts, state the question (`Approve these N items?`), and ask Apply all / per-severity bulk (alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = the displayed set.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → under `--ask`, forced binary re-prompt per item, no response: mark `skipped (no response)`, proceed; the default path always resolves per the paragraph above.

### Phase 6: Summary

```
ds-init: {OK|WARN|FAIL} | Generated: {n} | Skipped: {n} | Failed: {n} | Total: {n}

{project-name}/
├── .gitignore
├── .editorconfig
├── .env.example
├── src/
├── test/
│   └── example.test.{ext}
├── README.md
└── {config files}  (+ Dockerfile, CI workflow when --full)

Next steps:
1. Copy `.env.example` to `.env` and fill in values
2. Install dependencies: {install-command}
3. Run tests: {test-command}
4. Start development: {dev-command}
```

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} config files generated — lint/format/typecheck run on every commit, no manual setup`
- `CI pipeline (lint → test → build) wired with SHA-pinned actions — supply chain hardening from day one`
- `.env.example documented + .env in .gitignore — no secret ever lands in git history`

**Gate:** Summary printed with file list + next steps + Effect. If fails → file missing from tree → re-read list and add; totals imbalanced (gen + skip + fail ≠ total) → assign unaccounted to `skipped (accounting gap)`, re-emit `WARN`; re-run skill to regenerate failed files.

## Quality Gates

Config validity, `.gitignore` coverage, secret-free `.env.example`, the quality-gate wiring, CI completeness, and the privacy stub are enforced in Phase 3/4's Gates above — not restated here.

- W9: N/A — exempt from state protocol (idempotent scaffolding). W10: defer to fresh `ds/audit/findings.md` — own scan only for uncovered scopes. W16: every scaffolded dependency exists in its registry (non-trivial age + downloads), pinned in the lockfile; hallucinated/typosquat names rejected.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| Unknown project type | Default: resolves per Phase 1's lowest-blast-radius fallback. `--ask`: present the type-selection menu. |
| Stack not recognized | Default: resolves to the boring-technology default for the detected type. `--ask`: list supported stacks, ask the user to choose. |
| File conflict detected | Default: resolves to skip (preserve existing), per Phase 2. `--ask`: show diff, ask overwrite / skip / merge. |
| Write permission denied | Report error, suggest checking permissions |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Non-empty directory | Scan existing files, only add missing pieces |
| Monorepo detected | Default: scaffolds the workspace root config only, notes per-package scaffolding as a follow-up. `--ask`: ask which package, respect workspace config. |
| Multiple stacks | Default: the stack with the most source files becomes primary, others noted as secondary. `--ask`: ask the user to choose primary. |
| Custom stack not listed | Generate generic structure with user-specified conventions |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
