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
- Fully functional standalone — uses `.findings.md` for optimization when available

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

Detect → Configure → Scan → Report → [Fix] → Summary

### Phase 1: Detect

1. **Project type detection.** Search for config files:

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

2. **CI detection.** Search for CI config files: `.github/workflows/`, `.gitlab-ci.yml`, `bitrise.yml`, `Jenkinsfile`, `.circleci/`, `azure-pipelines.yml`, `codemagic.yaml`.

3. **Dependency tooling.** Detect: `dependabot.yml`, `renovate.json`, lockfiles, `.nvmrc`, `.tool-versions`.

4. **Mode selection.** If no `--mode` flag, ask the user:
   - **Full Audit** — scan all scopes, report findings
   - **Audit & Fix** — scan, review findings, then fix
   - **Quick Fix** — scan and auto-fix, minimal review

5. **Scope selection.** If no `--scope` flag, ask which scopes to audit (default: all).

### Phase 2: Rule Loading

Load [rules-devops.md](references/rules-devops.md). Rules are project-type-aware — skip rules that don't apply to the detected stack.

### Phase 3: Scan

For each scope, scan the codebase:

1. Search for relevant config and build files
2. Search contents for violation patterns
3. Read files to verify findings in context
4. Skip rules that cannot be verified

**Confidence:** HIGH = match + context verified. MEDIUM = pattern match, ambiguous. LOW = heuristic.

**Skip patterns:** `# noqa`, `# intentional`, `# safe:`, test fixtures.

**Findings verification** (audit and audit+fix modes, skip for quick-fix):
- HIGH: auto-include
- MEDIUM: present for review
- LOW: shown as potential issues

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

**Severity:** CRITICAL > HIGH > MEDIUM > LOW. When uncertain, choose lower.

### Phase 5: Post-Report

| Mode | Behavior |
|------|----------|
| `audit` | Ask: Fix all / CRITICAL+HIGH only / Review each / Report only |
| `audit+fix` | Auto-transition to fix |
| `quick-fix` | Auto-apply all, summary only |

### Phase 6: Fix [SKIP if audit-only or --preview]

1. Present fix plan (rule, severity, file, action, dependencies)
2. Confirmation: quick-fix = proceed, audit+fix = ask
3. Apply fixes grouped by file
4. Present fix summary

```
ds-devops: {OK|WARN|FAIL} | Applied: N | Failed: N | Total: N
```

## Quality Gates

1. No cascading breakage after fixes
2. Format preservation (indentation, config style)
3. Scope boundary (only touch required lines)
4. Stack consistency (correct CI syntax, valid config)

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No CI config found | Report as HIGH finding, suggest setup |
| Multiple CI platforms | Audit all, note which is primary |
| Monorepo | Check per-package CI config if applicable |
| No dependency lockfile | Report as HIGH, suggest committing lockfile |
| CLI tool not available | Skip that check, note in report |
