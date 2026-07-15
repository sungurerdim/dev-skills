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
| "dependency audit gate in CI" | "perform the dep upgrades" (→ ds-deps) |

## Contract

**Dimensions:** D6, C1 (CI/CD security)
**Framework alignment (advisory):** DORA (D6), OWASP ASVS (C1) — sourced references in SKILL-SPEC Dimension Coverage Map.

- Every finding cites file and line — never infer or assume.
- Only audits CI/CD, signing, dependencies, release pipelines.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- State-exempt: audit is regenerable; generated configs/fixes land in the working tree — git is the durable record.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode={x}` | `audit`, `audit+fix`, `quick-fix` |
| `--scope={x}` | Comma-separated: ci, signing, deps, release-pipeline, or `all` |
| `--auto` | All scopes, no questions, single-line summary |
| `--preview` | Dry run — show what would be checked without loading rules or scanning |

Without flags: present mode + scope selection to the user.

## Scopes

| Scope | What It Checks |
|-------|---------------|
| ci | CI/CD pipeline presence, quality gates, format / analyze / test / build stages |
| signing | Code signing automation, certificate management, keystore security, build provenance / artifact attestation |
| deps | Dependency audit gate, outdated detection, cross-dependency compatibility, breaking changes |
| release-pipeline | Release automation, version bump workflow |

## Delegation

**Owns:** ci, signing, deps-audit, pipeline-structure | **Delegates:** ds-deps → deps-upgrade-execution; ds-deploy → infra / container / TLS / monitoring | **Receives:** ds-deploy → CI pipeline structure verification; ds-ship → Phase 5 infra chain

## Execution Flow

Detect → Configure → Scan → Report → [Fix] → [Needs-Approval] → Summary

### Phase 1: Detect

1. **IDU:** Profile → Project Map.Toolchain, Type + Stack, Config.deploy. Findings(ci, signing, deps, release-pipeline) → verify + use. Absent → own analysis.

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
5. **Mode selection.** No `--mode` → present the full menu: Full Audit (recommended) — scan + report, no changes / Audit & Fix — scan + review + fix / Quick Fix — scan + auto-fix, summary only / (Cancel). A disambiguating flag skips the menu.
6. **Scope selection.** No `--scope` → ask which scopes to audit (default: all).

**Gate:** Project type + CI platform identified; mode and scope confirmed. If fails → undetermined type → "What type of project? (Flutter / Node / Python / Go / Rust / Java / iOS / Android / Monorepo)"; undetected CI platform → "Which CI platform do you use?"; unconfirmed mode/scope after prompt → default Full Audit / all scopes, announce.

### Phase 2: Rule Loading

Load [references/rules-devops.md](references/rules-devops.md). Rules are project-type-aware — skip rules that don't apply to detected stack.

**Gate:** Rules file loaded + filtered to detected project type; inapplicable rules excluded. If fails → rules file unreadable → WARN "rules file unavailable — proceeding with built-in heuristics only", continue scan using embedded rules; do not abort.

### Phase 3: Scan

1. **Findings file check:** `ds/audit/findings.md` fresh `git_hash` → read findings matching scopes (ci, signing, deps, release-pipeline). Per match: verify still valid (re-read `{file}:{line}`); uncovered scopes → run full analysis.

For each scope:

2. Search for relevant config + build files.
3. Search contents for violation patterns.
4. Read files to verify findings in context.
5. Skip rules that cannot be verified.

**Twelve-Factor pipeline checks ([references/principles.md §3](references/principles.md)):**

| Factor | Check | Flag when |
|--------|-------|-----------|
| 5 Build/Release/Run | Build artifact immutable; same artifact promoted across environments | CI rebuilds from source per environment |
| 12 Admin processes | Migrations / seeds / backfills run as isolated one-off commands against the same release artifact | Embedded in the deploy job or run on dev workstations |

**Confidence:** HIGH = match + context verified. MEDIUM = pattern match, ambiguous. LOW = heuristic.

**Skip patterns:** `# noqa`, `# intentional`, `# safe:`, test fixtures.

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

| Mode | Behavior |
|------|----------|
| `audit` | Ask: Fix all / CRITICAL+HIGH only / Review each / Report only |
| `audit+fix` | Auto-transition to fix |
| `quick-fix` | Auto-apply all, summary only |

**Gate:** User selected post-report action; mode-specific next step determined. If fails → no response / dismissed prompt → default "Report only" (no fixes), announce default, proceed to Summary.

**Approval-menu convention (Phases 6-7):** present each item on one compact line (`[severity] title — file:line`), grouped by severity with counts; state the question; offer `Apply all` plus per-severity bulk (`Apply all HIGH`) alongside the total (CRITICAL bulk still confirms per item); `approve-all` excludes CRITICAL; `all` = exactly the displayed set.

### Phase 6: Fix [SKIP if audit-only or --preview]

1. Present fix plan per the approval-menu convention — one line per fix (rule, `[severity]`, file:line, action); question `Apply these N fixes?`.
2. Confirmation: quick-fix proceeds; audit+fix asks Apply all / per-severity bulk / proceed / cancel.
3. Apply fixes grouped by file.
4. Present fix summary.

```
ds-devops: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

**Gate:** `fixed + skipped + failed = total`; every modified file re-read and verified; every finding/action has a disposition. If fails → undisposed finding → `skipped (accounting gap)`; un-re-readable modified file → mark fix `failed (verify error)`, revert file change; counts imbalanced → status `WARN`.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** apply the approval-menu convention (question `Approve these N items?`); ask Apply all / per-severity bulk / Review Each / Skip All.

**Gate:** All items resolved. If fails → unresolved → mark `skipped (no decision)`, continue; do not retry.

**Value Delivered:** 1-5 concrete bullets, real pipeline outcomes only. Example shapes (placeholders, not literal):

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
5. **Shell quoting ([references/principles.md §5](references/principles.md)):** every shell line in generated CI configs uses double-quoted variable references (`"$VAR"`, `"${VAR}"`). Reject metacharacter injection in dynamic values. Flag unquoted user-data interpolation as CRITICAL.
6. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: state-exempt — audit is regenerable, working tree + git are the durable record. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Error Recovery

| Situation | Action |
|-----------|--------|
| CI platform not detected | Ask user which CI platform they use |
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

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
