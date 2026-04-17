# /ds-devops

Broken CI pipelines, unsigned builds, and outdated dependencies silently erode release quality. This skill audits your entire DevOps setup and flags what needs fixing.

**DevOps Audit** — CI/CD pipelines, code signing, dependency management, and deployment configuration for any project type.

## Triggers

- User runs `/ds-devops`
- User asks to audit or review CI/CD, pipelines, deployment, or DevOps setup
- User asks about dependency management, code signing, or CI quality gates
- User asks why CI is failing or how to set up CI for a project

## Contract

- Every finding cites file and line — never infer or assume
- Only audits CI/CD, signing, dependencies, and release pipelines
- Standalone. Uses blueprint/.ds-findings.md when available; own analysis when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode=<mode>` | `audit`, `audit+fix`, `quick-fix` |
| `--scope=<domains>` | Comma-separated: ci, signing, deps, release-pipeline, or `all` |
| `--auto` | All scopes, no questions, single-line summary |
| `--preview` | Dry run — show what would be checked without loading rules or scanning |

Without flags: present mode and scope selection to the user.

## Scopes

| Scope | What It Checks |
|-------|---------------|
| ci | CI/CD pipeline presence, quality gates, format/analyze/test/build stages |
| signing | Code signing automation, certificate management, keystore security |
| deps | Dependency audit gate, outdated detection, cross-dependency compatibility, breaking changes |
| release-pipeline | Release automation, version bump workflow |

---

## Execution Flow

Detect → Configure → Scan → Report → [Fix] → [Needs-Approval] → Summary

### Phase 1: Detect

1. **IDU:** Profile → Project Map.Toolchain, Type+Stack, Config.deploy. Findings(ci, signing, deps, release-pipeline) → verify + use. Absent → own analysis.
2. **Project type detection.** Search for config files:

| Type | Detection |
|------|-----------|
| Flutter/Dart | `pubspec.yaml` with `flutter:` |
| Node.js | `package.json` |
| Python | `pyproject.toml`, `setup.py`, `requirements.txt` |
| Go | `go.mod` |
| Rust | `Cargo.toml` |
| Java/Kotlin | `build.gradle`, `pom.xml` |
| iOS | `*.xcodeproj`, `Package.swift` |
| Android | `build.gradle` with `android {}` |
| Monorepo | `lerna.json`, `nx.json`, `turbo.json`, workspace config |

3. **CI detection.** Search for CI config files: `.github/workflows/`, `.gitlab-ci.yml`, `bitrise.yml`, `Jenkinsfile`, `.circleci/`, `azure-pipelines.yml`, `codemagic.yaml`.

4. **Dependency tooling.** Detect: `dependabot.yml`, `renovate.json`, lockfiles, `.nvmrc`, `.tool-versions`.

5. **Mode selection.** No `--mode` flag → ask user:
   - **Full Audit** — scan all scopes, report findings
   - **Audit & Fix** — scan, review findings, then fix
   - **Quick Fix** — scan and auto-fix, minimal review

6. **Scope selection.** No `--scope` flag → ask which scopes to audit (default: all).

**Gate:** Project type identified, CI platform detected, mode and scope confirmed.

### Phase 2: Rule Loading

Load [rules-devops.md](references/rules-devops.md). Rules are project-type-aware — skip rules that don't apply to detected stack.

**Gate:** Rules file loaded and filtered to detected project type; inapplicable rules excluded.

### Phase 3: Scan

1. **Findings file check:** `.ds-findings.md` with fresh `git_hash` → read findings matching scopes (ci, signing, deps, release-pipeline). For each match: verify still valid (re-read file:line), skip own analysis for verified scopes. Uncovered scopes → run full analysis.

For each scope, scan codebase:

2. Search for relevant config and build files
3. Search contents for violation patterns
4. Read files to verify findings in context
5. Skip rules that cannot be verified

**Confidence:** HIGH = match + context verified. MEDIUM = pattern match, ambiguous. LOW = heuristic.

**Skip patterns:** `# noqa`, `# intentional`, `# safe:`, test fixtures.

**Findings verification** (audit and audit+fix modes, skip for quick-fix):
- HIGH: auto-include
- MEDIUM: present for review
- LOW: shown as potential issues

**Gate:** Every in-scope domain scanned, all findings recorded with severity and confidence.

### Phase 4: Report

```
## DevOps Audit Report — [project_name]
Type: [project_type] | CI: [ci_platform] | Date: [today]

### Findings
| # | Rule | Sev | File:Line | Issue | Impact | Fix | Conf |

### Potential Issues (LOW confidence)
| # | Rule | File:Line | Issue | Suggested Fix |

### Summary
| Scope | CRITICAL | HIGH | MEDIUM | LOW | Total |
```

**Severity:** CRITICAL > HIGH > MEDIUM > LOW. Uncertain → choose lower.

**Gate:** Report presented to user with all findings, severities, and summary table.

### Phase 5: Post-Report

| Mode | Behavior |
|------|----------|
| `audit` | Ask: Fix all / CRITICAL+HIGH only / Review each / Report only |
| `audit+fix` | Auto-transition to fix |
| `quick-fix` | Auto-apply all, summary only |

**Gate:** User selected post-report action; mode-specific next step determined.

### Phase 6: Fix [SKIP if audit-only or --preview]

1. Present fix plan (rule, severity, file, action, dependencies)
2. Confirmation: quick-fix = proceed, audit+fix = ask
3. Apply fixes grouped by file
4. Present fix summary

```
ds-devops: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N
```

**Gate:** Fixed + skipped + failed = total findings; every modified file re-read and verified. Every finding/action has a disposition. Accounting verified.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

## Quality Gates

1. No cascading breakage after fixes
2. Format preservation (indentation, config style)
3. Scope boundary (only touch required lines)
4. Stack consistency (correct CI syntax, valid config)
5. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

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
