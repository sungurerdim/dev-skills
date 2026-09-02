---
name: ds-devops
description: DevOps audit — CI/CD pipelines, code signing, dependency management, deployment config for any stack. Use when auditing or setting up CI/CD and release infrastructure.
---

# /ds-devops

Broken CI pipelines, unsigned builds, and outdated dependencies silently erode release quality. This skill audits your entire DevOps setup and flags what needs fixing.

**DevOps Audit** — CI/CD pipelines, code signing, dependency management, and deployment configuration for any project type.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-devops`
- User asks to audit or review CI/CD, pipelines, deployment, or DevOps setup
- User asks about dependency management, code signing, or CI quality gates
- User asks why CI is failing or how to set up CI for a project

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "audit CI/CD pipeline", "review GitHub Actions workflows" | "deploy the app to infra" (→ ds-deploy) |
| "set up code signing for releases" | "configure VPS / containers / SSL" (→ ds-deploy) |
| "audit release pipeline + version bump workflow" | "audit repo settings / branch protection" (→ ds-repo) |
| "dependency audit gate in CI" | "monitoring, alerting, SLOs" (→ ds-deploy) |

## Contract

**Dimensions:** D6, C1 (CI/CD security)
**Framework alignment (advisory):** DORA (D6), OWASP ASVS (C1).

- Every finding cites file and line — never infer or assume.
- Only audits CI/CD, signing, dependencies, release pipelines.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- State-exempt: audit is regenerable; generated configs/fixes land in the working tree — git is the durable record.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode={x}` | `audit`, `audit+fix`, `quick-fix` |
| `--scope={x}` | Comma-separated: ci, signing, deps, release-pipeline, or `all` |
| `--preview` | Dry run — show what would be checked without loading rules or scanning |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `needs-human`. |

Without flags: mode resolves to `audit+fix` and scope resolves to `all`, both by best judgment and recorded in the summary. `--ask`: present the mode + scope selection menu.

## Scopes

35 rules across 13 domains, loaded per scope from `references/rules-*.md`.

| Scope | What It Checks |
|-------|---------------|
| ci | CI/CD pipeline presence, quality gates, format / analyze / test / build stages, workflow lint layers (actionlint + zizmor), `pull_request_target` misuse, agent/tool security, CI-built container + cloud-auth hardening |
| signing | Code signing automation, certificate management, keystore security |
| deps | Dependency audit gate, outdated detection, cross-dependency compatibility, breaking changes, supply-chain provenance (SCA) |
| release-pipeline | Release automation, version bump workflow, registry publish auth (trusted publishing / OIDC — DOP-21), build provenance / artifact attestation, backup & DR posture |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| ci | any source — every project is checked for CI/CD presence and hygiene | — |
| signing | `platforms` intersects `{ios, android, desktop}` | N/A — no signable target detected |
| deps | a dependency manifest is present (`package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `Gemfile`, `pom.xml`/`build.gradle`, `Package.swift`, `*.csproj`, `mix.exs`, `composer.json`, …) | N/A — no dependency manifest found |
| release-pipeline | `deploy` ≠ `none`, or a registry-publish / release-automation config exists (release-please, semantic-release, a publish workflow) | N/A — no release or publish pipeline detected |

An `unknown` signal never excludes a scope; `--scope=` overrides the table for the named scopes; `--ask` shows the resolved table before running.

**Out of scope — delegated.** Monitoring, alerting, SLOs, and error-budget policy are ds-deploy's scope (already reflected in Delegation below): present → delegate; absent → gap-note `monitoring not analyzed — requires ds-deploy`. This skill audits the pipeline that ships the code, not the code's production behavior once shipped.

## Delegation

**Owns:** ci, signing, deps-audit, pipeline-structure | **Delegates:** ds-deps → deps-upgrade-execution; ds-deploy → infra / container / TLS / monitoring | **Receives:** ds-deploy → CI pipeline structure verification; ds-ship → Phase 5 infra chain; ds-release → CI run + attestation verification after a publish

## Execution Flow

Detect → Configure → Scan → Report → [Fix] → [Needs-Approval] → Summary

### Phase 1: Detect

1. **Upstream artifacts:** Profile → Project Map.Toolchain, Type + Stack, Config.deploy. Findings(ci, signing, deps, release-pipeline) → verify + use. Absent → own analysis.

2. **Project type detection:**

   | Type | Detection signal |
   |------|------------------|
   | Flutter / Dart | `pubspec.yaml` with `flutter:` |
   | Node.js | `package.json` |
   | Python | `pyproject.toml`, `setup.py`, `requirements.txt` |
   | Go | `go.mod` |
   | Rust | `Cargo.toml` |
   | Java / Kotlin | `build.gradle`, `pom.xml` |
   | iOS | `*.xcodeproj`, `Package.swift` |
   | Android | `build.gradle` with `android {}` |
   | Monorepo | `lerna.json`, `nx.json`, `turbo.json`, workspace config |

3. **CI detection.** Search for `.github/workflows/`, `.gitlab-ci.yml`, `bitrise.yml`, `Jenkinsfile`, `.circleci/`, `azure-pipelines.yml`, `codemagic.yaml`.
4. **Dependency tooling.** Detect `dependabot.yml`, `renovate.json`, lockfiles, `.nvmrc`, `.tool-versions`.
5. **Mode selection.** Default: `audit+fix` (best-judgment default: scan and fix autonomously) — no menu. `--ask`: present the full menu — Full Audit (recommended) — scan + report, no changes / Audit & Fix — scan + review + fix / Quick Fix — scan and auto-fix, summary only / (Cancel). A disambiguating `--mode` flag skips the menu in either case.
6. **Scope selection.** Default: `all` — no menu. `--ask`: ask which scopes to audit (default: all). A disambiguating `--scope` flag skips the menu in either case.

**Gate:** Project type matched to a detection signal (step 2) and a CI platform config file found (step 3); mode and scope confirmed. If fails → Default: undetermined type/platform resolves to whatever manifest signals are present, or "no CI configured" (an Edge Case, not a blocker) when truly absent — recorded in the summary, no prompt. `--ask`: undetermined type → ask "What type of project? (Flutter / Node / Python / Go / Rust / Java / iOS / Android / Monorepo)"; undetected CI platform → ask "Which CI platform do you use?"; unconfirmed mode/scope after prompt → default Full Audit / all scopes, announce.

### Phase 2: Rule Loading

Load the rules file for each scope the resolution table above marks `ran`: [references/rules-ci.md](references/rules-ci.md) (ci), [references/rules-signing.md](references/rules-signing.md) (signing), [references/rules-deps.md](references/rules-deps.md) (deps), [references/rules-release-pipeline.md](references/rules-release-pipeline.md) (release-pipeline). Rules are project-type-aware — skip rules that don't apply to detected stack.

**Gate:** Rules file(s) loaded + filtered to detected project type; inapplicable rules excluded. If fails → a scope's rules file is unreadable → WARN "rules file unavailable for {scope} — proceeding with built-in heuristics only", continue scan using embedded rules; do not abort.

### Phase 3: Scan

1. **Findings file check:** `ds/audit/findings.md` fresh (its meta `git_hash` equals `git rev-parse HEAD` output AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → read findings matching scopes (ci, signing, deps, release-pipeline). Per match: verify still valid (re-read `{file}:{line}`); uncovered scopes → run full analysis. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.

For each scope:

2. Search for relevant config + build files.
3. Search contents for violation patterns.
4. Read files to verify findings in context.
5. Skip rules that cannot be verified.

**Twelve-Factor pipeline checks ([../core/principles.md §3](../core/principles.md)):**

| Factor | Check | Flag when |
|--------|-------|-----------|
| 5 Build/Release/Run | Build artifact immutable; same artifact promoted across environments | CI rebuilds from source per environment |
| 12 Admin processes | Migrations / seeds / backfills run as isolated one-off commands against the same release artifact | Embedded in the deploy job or run on dev workstations |

**Workflow lint & security (ci scope, advisory tools):** actionlint (correctness) or zizmor (security anti-patterns) present → run it, merge findings into the report. `.github/workflows/` exists and either tool absent → HIGH finding "workflow lint layer missing — add actionlint + zizmor", with the prose rules ([references/rules-ci.md](references/rules-ci.md) DOP-19) as this run's fallback; never auto-install. `pull_request_target` combined with checkout/execution of untrusted PR code → CRITICAL (DOP-20 — the March 2026 trivy-action → LiteLLM supply-chain incident pattern).

**Confidence + skip patterns:** per [../core/severity-score-categories.md](../core/severity-score-categories.md).

**Findings verification** (audit / audit+fix modes; quick-fix skips): HIGH → auto-include · MEDIUM → present for review · LOW → shown as potential issue.

**Gate:** Every in-scope domain scanned; all findings recorded with severity + confidence. If fails → unscan-able scope (file unreadable, tool unavailable, unexpected format) → mark scope `partial`, record MEDIUM "scan incomplete for scope {scope} — {reason}", continue to Report; do not silently omit scope.

### Phase 4: Report

```
## DevOps Audit Report — {project-name}
Type: {project-type} | CI: {ci-platform} | Date: {today}

### Findings
| # | Rule        | Sev      | File:Line       | Issue    | Impact   | Fix      | Conf   |

### Potential Issues (LOW confidence)
| # | Rule        | File:Line       | Issue    | Suggested Fix     |

### Summary
| Scope | CRITICAL | HIGH | MEDIUM | LOW | Total |
```

**Severity:** CRITICAL > HIGH > MEDIUM > LOW. Uncertain → choose lower.

**Gate:** Report presented with all findings + severities + summary. If fails → missing scope row → re-read the collected findings, add row with recorded count (or `0 findings`), re-emit report; do not proceed to Phase 5 until table accounts for every selected scope.

### Phase 5: Post-Report

| Mode | Default (no prompt) | `--ask` |
|------|----------------------|---------|
| `audit` | Report only — honors the explicit audit-only mode choice | Ask: Fix all / CRITICAL+HIGH only / Review each / Report only |
| `audit+fix` | Auto-transition to fix | Auto-transition to fix (the mode already commits to fixing) |
| `quick-fix` | Auto-apply all, summary only | Auto-apply all, summary only (the mode already commits to fixing) |

**Gate:** Post-report action determined per the table above. If fails → no response under `--ask` → default to the row's Default cell, announce, proceed to Summary.

**Approval-menu convention (Phases 6-7):** under `--ask`, present each item on one compact line (`[severity] title — file:line`), grouped by severity with counts; state the question; offer `Apply all` plus per-severity bulk (`Apply all HIGH`) alongside the total (CRITICAL bulk still confirms per item); `approve-all` excludes CRITICAL; `all` = exactly the displayed set.

### Phase 6: Fix [SKIP if audit-only or --preview]

0. **Checkpoint pre-step** (before the first file write, [../core/checkpoint-protocol.md](../core/checkpoint-protocol.md)): `git status --porcelain` → non-empty → Default: proceed only when the pre-existing dirty files are disjoint from the planned fix targets; a fix targeting a dirty file resolves `needs-human` — no prompt. `--ask`: ask Commit first (recommended) / Stash / Proceed anyway (risk stated). Tree cannot be checkpointed → apply no fix over uncommitted unrelated changes; report the blocker.
1. Present fix plan per the approval-menu convention — one line per fix (rule, `[severity]`, file:line, action); question `Apply these N fixes?`.
2. Confirmation: quick-fix proceeds automatically. `audit+fix` — Default: resolves by best judgment, no confirmation shown. `--ask`: ask Apply all / per-severity bulk / proceed / cancel.
3. Apply fixes grouped by file.
4. Present fix summary.

```
ds-devops: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

**Gate:** `fixed + skipped + failed = total`; every modified file re-read and verified; every finding/action has a disposition. If fails → undisposed finding → `skipped (accounting gap)`; un-re-readable modified file → mark fix `failed (verify error)`, revert file change; counts imbalanced → status `WARN`.

### Phase 7: Needs-Approval Review [needs_approval > 0]

Default: items resolve by best judgment (`fixed` or `failed`), except items matching the publish/irreversible exception list, which become `skipped (needs-human)` — no review step shown. `--ask`: present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → unresolved → mark `skipped (no decision)`, continue; do not retry.

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `CI pipeline: {n} actions SHA-pinned (was `@v{x}` tag references) — supply-chain attack via action tag overwrite eliminated`
- `Quality gates wired (lint → typecheck → test → build) with `concurrency` and `permissions: read` — broken releases caught before they hit users`
- `Code signing automation: {n} secrets moved to GitHub Actions secret store — keystore no longer drifts between local + CI`
- `Dep audit gate added — CVE in a transitive dep now blocks merge instead of landing in production`

Zero-finding run: `CI/CD scope clean — pipeline meets reviewed checks`.

## Quality Gates

1. No cascading breakage after fixes
2. Format preservation (indentation, config style)
3. Scope boundary (only touch required lines)
4. Stack consistency (correct CI syntax, valid config)
5. **Shell quoting ([../core/principles.md §5](../core/principles.md)):** every shell line in generated CI configs uses double-quoted variable references (`"$VAR"`, `"${VAR}"`). Reject metacharacter injection in dynamic values. Flag unquoted user-data interpolation as CRITICAL.
6. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered.
7. **Mechanical Done Gate:** resolve `{check-cmd}` once at setup — the ds-quality enforcement arm when installed, else the stack-native chain from [../core/toolchains.md](../core/toolchains.md) plus the workflow-file linters this skill runs when `.github/workflows/` is present: `actionlint` (correctness — syntax, expression types, action inputs, embedded shell) and `zizmor .github/workflows/` (security anti-patterns) chained after the stack-native steps, plus `yamllint` when present. Either tool absent → gap-note "workflow lint layer missing — add actionlint + zizmor" in the aggregate result, never a silent skip; capture the baseline; re-run after each change batch and once in aggregate before reporting done. New red → fix (≤3 attempts, same command), then revert the offending change and record `reverted`; baseline red is reported red-at-baseline, never inherited; no tooling detectable at all → report the Verification-Infrastructure Gap, never skip silently.
8. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| CI platform not detected | Default: treated as "no CI configured", reported as a HIGH finding (Edge Cases) instead of blocking — no ask. `--ask`: ask user which CI platform they use. |
| Signing certificate expired or missing | Flag as CRITICAL, generate renewal checklist |
| Dependency audit tool unavailable | Skip dependency scope, warn in summary |
| Pipeline config syntax varies by CI platform | Detect platform first, generate platform-specific config |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No CI config found | Report as HIGH finding, suggest setup |
| Multiple CI platforms | Audit all, note which is primary |
| Monorepo | Check per-package CI config if applicable |
| No dependency lockfile | Report as HIGH, suggest committing lockfile |
| CLI tool not available | Skip that check, note in report |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
