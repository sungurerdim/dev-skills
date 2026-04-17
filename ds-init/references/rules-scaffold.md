# Rules: Project Scaffolding

Rules for initial project structure, configuration, and tooling setup. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Structure** | SCF-01–04 (2 HIGH, 2 MEDIUM) | ~12 |
| **Configuration** | SCF-05–08 (2 HIGH, 1 MEDIUM, 1 LOW) | ~58 |

---

## Structure

### SCF-01 [HIGH] Standard Directory Layout
Project follows platform-conventional directory structure. Reviewers and tools expect standard layouts.
- **Detect:**
  - Flat structure without source/test separation
  - Source files mixed with configuration files at root
  - Test files co-located without clear convention
  - Platform conventions violated (e.g., Go code not in cmd/internal/pkg)
- **Fix:** Apply platform-specific layout:
  - **Node/TypeScript:** src/ for source, test/ or __tests__/ for tests, dist/ for output
  - **Python:** src/package_name/ for source, tests/ for tests, pyproject.toml at root
  - **Go:** cmd/ for entrypoints, internal/ for private, pkg/ for public libraries
  - **Flutter/Dart:** lib/ for source, test/ for tests, assets/ for resources
  - **Rust:** src/ for source, tests/ for integration tests, benches/ for benchmarks
- **Source:** Platform project templates, official documentation

### SCF-02 [HIGH] CI From Day One
CI pipeline configured in initial commit. Catches issues before they accumulate.
- **Detect:**
  - No .github/workflows/, .gitlab-ci.yml, or equivalent CI config
  - CI config exists but does not run on pull requests
  - CI missing lint, test, or build steps
- **Fix:** Add CI pipeline triggered on PR to default branch. Minimum steps: install dependencies, lint, type-check (if applicable), test, build. Start simple, expand later
- **Platform:**
  - GitHub: .github/workflows/ci.yml with on: pull_request
  - GitLab: .gitlab-ci.yml with merge_request_pipelines
- **Source:** GitHub Actions documentation

### SCF-03 [MEDIUM] Editor Config
Consistent formatting across editors regardless of individual developer settings.
- **Detect:**
  - No .editorconfig file in project root
  - Inconsistent indentation across files (tabs vs spaces mixed)
  - Different line endings across files
- **Fix:** Add .editorconfig with: root = true, indent_style (space or tab per platform convention), indent_size, end_of_line = lf, charset = utf-8, trim_trailing_whitespace = true, insert_final_newline = true
- **Source:** editorconfig.org

### SCF-04 [MEDIUM] Gitignore Completeness
OS artifacts, IDE files, build outputs, and dependency directories excluded from version control.
- **Detect:**
  - No .gitignore file
  - Missing entries for: OS files (.DS_Store, Thumbs.db), IDE (.idea/, .vscode/), dependencies (node_modules/, venv/), build output (dist/, build/, *.pyc)
  - Generated files tracked in git
- **Fix:** Use gitignore.io or github/gitignore templates for project stack. Combine OS + IDE + language + framework ignores. Verify with `git status` that no generated files are tracked
- **Source:** github/gitignore repository

---

## Configuration

### SCF-05 [HIGH] Dependency Lock
Lockfile committed from first install. → reproducible builds across environments.
- **Detect:**
  - Lockfile listed in .gitignore
  - Lockfile missing from repository
  - Lockfile not updated after dependency changes
- **Fix:** Commit appropriate lockfile:
  - **npm:** package-lock.json
  - **yarn:** yarn.lock
  - **pnpm:** pnpm-lock.yaml
  - **Python/Poetry:** poetry.lock
  - **Python/pip:** requirements.txt (pinned) or pip-compile output
  - **Rust:** Cargo.lock (for binaries; libraries may exclude)
  - **Flutter/Dart:** pubspec.lock
  - **Go:** go.sum
- **Source:** Package manager documentation, 12-Factor App

### SCF-06 [HIGH] Environment Template
.env.example documents all required environment variables with placeholder values. Real .env never committed.
- **Detect:**
  - .env file tracked in git (secrets exposed)
  - No .env.example or equivalent template
  - .env.example missing variables that code references
  - Real secrets in .env.example
- **Fix:** Create .env.example with every required variable using placeholder values (DATABASE_URL=postgresql://user:pass@localhost:5432/dbname). Add .env to .gitignore. Document which variables are required vs optional
- **Source:** 12-Factor App (III. Config)

### SCF-07 [MEDIUM] README From Day One
README communicates project purpose, quick start, and contribution guide. Projects with quality READMEs receive significantly more engagement.
- **Detect:**
  - No README.md or empty/default README
  - README missing: purpose statement, install instructions, run command, test command
  - README contains only auto-generated boilerplate
- **Fix:** Minimum sections: project purpose (1-2 sentences), prerequisites, install, run, test. Add contribution guide for open source. Keep concise — link to docs/ for details
- **Impact:** Projects with structured READMEs receive 4x more engagement
- **Source:** GitHub research on README impact

### SCF-08 [LOW] License File
LICENSE file in repository root. Required for open source; clarifies terms for private projects.
- **Detect:**
  - No LICENSE or LICENSE.md file in root
  - License referenced in README but file missing
  - License type incompatible with dependencies
- **Fix:** Add LICENSE file. Common choices: MIT (permissive, libraries), Apache-2.0 (permissive + patent grant), GPL-3.0 (copyleft), AGPL-3.0 (copyleft + network use). Match license to project goals and dependency licenses
- **Source:** choosealicense.com, OSI approved licenses
