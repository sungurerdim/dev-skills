# Findings File & Blueprint Profile — the two shared artifacts

**Consumers:** every skill that reads or writes `ds/audit/findings.md` or the `## Blueprint Profile` block. ds-blueprint is the profile's only writer; any analyzer may write findings.

Both artifacts are optimizations, never requirements: a skill with neither present runs its own complete analysis and produces identical-quality output.

## 1. Findings file — `ds/audit/findings.md`

Exactly one per project, under the gitignored `ds/audit/` directory (`.gitignore` carries the line `ds/audit/`).

```markdown
<!-- findings-meta
git_hash: {HEAD}
timestamp: {ISO 8601}
source: {skill-name[, skill-name…]}
scopes: {comma-separated list of analyzed scopes}
signals: {optional — the Signals line the analyzer resolved, see signal-inventory.md}
-->

## Findings

| ID | Severity | Category | File | Line | Scope | Title |
|----|----------|----------|------|------|-------|-------|
| {id} | {severity} | {A|B} | {file} | {line} | {scope} | {title} |
```

| Rule | Detail |
|------|--------|
| **Freshness** | `git_hash` = HEAD → fresh, reuse as is. Otherwise measure the drift before deciding how much to redo — the answer is graded, never a coin flip, and never a question for the user. **Full re-analysis** (detection, `Signals:`, every scope, `Scores:`) when any of: `git merge-base --is-ancestor {git_hash} HEAD` fails (history rewritten, or the findings came from another branch) · the diff touches a manifest, lockfile, CI workflow, container file or framework entry point (`git diff --name-only {git_hash}..HEAD` matching `package.json`, `pnpm-lock.yaml`, `pyproject.toml`, `poetry.lock`, `go.mod`, `Cargo.toml`, `pubspec.yaml`, `*.csproj`, `composer.json`, `Gemfile*`, `.github/workflows/*`, `Dockerfile*`) — type, stack or signals may have moved · the change is large: `git rev-list --count {git_hash}..HEAD` ≥ 40, or changed source files ≥ 25% of `git ls-files` , or `git diff --shortstat` ≥ 500 changed lines. **Incremental** otherwise: re-analyze only the scopes whose files appear in the diff, keep the other scopes' rows, refresh `git_hash`. Either way the run states which branch it took and the numbers that decided it. A full-codebase analyzer overwrites the file; a partial analyzer overwrites only its own scopes. |
| **Scopes** | Lists every scope analyzed, including scopes with zero findings — "checked and clean" is distinguishable from "never analyzed". Consumer: scope listed → verify each row by re-reading `file:line`, use verified rows, skip its own scan; scope absent → own scan. |
| **Category** | A = conforms to the agreed plan (apply); B = changes architecture/scope/promise/dependency (approval-gated under `--ask`, reasoned and recorded by default). |
| **Line 0** | File-level finding. |
| **Signals, not analyses** | The title is a short description ("Hardcoded API secret"), never a rule id alone; the consumer reads the site to act. |
| **Write semantics** | Absent → create. Present, same hash → scoped overwrite (rewrite your scopes' rows; preserve other scopes; add your scopes to `scopes`; same `file:line` from another scope → keep the higher severity). Present, different hash → stale (see Freshness). |
| **Consumption** | A fixer removes the rows it resolved; a scope fully resolved leaves the `scopes` list; zero rows → delete the file; `ds/audit/` empty → remove the directory. |
| **Producer priority** | ds-blueprint's rows win for scopes it covers (whole-codebase scan); other producers merge only uncovered scopes. |
| **Dedup** | Same `file:line` → merge, highest severity; within 10 lines and same issue → merge, cite the leading line. |
| **Never** | Append cumulatively, date-stamp copies, or keep a second findings file. |

**Standard scope tokens** (lowercase kebab-case; a skill's `Owns:` line uses the same tokens): `security`, `privacy`, `regulatory`, `hygiene`, `types`, `simplify`, `ai-hygiene`, `doc-sync`, `performance`, `perf-profiling`, `robustness`, `production-readiness`, `architecture`, `patterns`, `cross-cutting`, `maintainability`, `ai-architecture`, `contract-consistency`, `testing`, `functional-completeness`, `stack`, `stack-fitness`, `dx`, `external-tooling`, `docs`, `spec-alignment`, `ideal-gap`, `format`, `lint`, `typecheck`, `ci`, `signing`, `deps`, `deps-upgrade`, `deploy`, `deployment`, `infra`, `monitoring`, `api`, `db`, `auth`, `data-pipeline`, `monetization`, `pricing`, `gtm`, `store`, `release`, `privacy-labels`, `perf-budget`, `scaffolding`, `tokens`, `components`, `states`, `a11y`, `responsive`, `theming`, `oss-readiness`, `adr`, plus each mobile domain token owned by ds-mobile.

## 2. Blueprint profile — `## Blueprint Profile` … `## End Blueprint Profile`

Lives in the host's context-loaded instruction file (Claude Code `CLAUDE.md`, Codex `AGENTS.md`, Cursor `.cursor/rules/*.md`, Copilot `.github/copilot-instructions.md`, Windsurf/Devin `.windsurf/rules/`, Aider `.aider.conf.yml` pointer). Key-value lines only — no prose, headers, tables, or bullets — so every consumer reads its line in O(1).

**Hard ceiling: 25 lines.** Every line passes the Dev-Value Gate: *would an AI assistant reading this line on every turn for six months do meaningfully better engineering on this codebase because of it?* No → it does not belong here.

| Line | Shape | Consumers |
|------|-------|-----------|
| `Type:` · `Stack:` · `Target:` | `Type: {app|library|service|cli|monorepo} \| Stack: {langs/frameworks} \| Target: {prototype|production|enterprise}` | all — detection skip, severity calibration |
| `Mission:` | one sentence | ds-docs tone, ds-ship stage classification |
| `Signals:` | `has_ui=… has_api=… …` — see `signal-inventory.md` | every skill's scope-resolution table; ds-ship delegation |
| `Priorities:` · `Constraints:` · `Red lines:` | comma lists; red lines are hard NOs no consumer crosses without explicit override | scope ordering, keep-constraints, refusal of proposals |
| `Data:` · `Regulations:` · `Jurisdiction:` | PII types / frameworks / regions | ds-compliance, ds-backend, ds-mobile, ds-productize |
| `Audience:` · `Deploy:` · `Platforms:` | `public\|internal\|developers` / target / `web,ios,android,desktop,cli` | ds-docs, ds-launch, ds-deploy, ds-devops, ds-mobile, ds-frontend |
| `Integrations:` | `none` or comma list (`stripe,sentry,firebase`) | conditional rule blocks in backend/compliance/frontend/mobile/launch/productize |
| `Entry:` · `Modules:` · `Data Flow:` · `External:` · `Toolchain:` | `;`-separated per concern, one line each | architectural awareness; ds-fix/ds-test/ds-devops/ds-quality read `Toolchain:` instead of re-detecting |
| `Ideal:` | `coupling= cohesion= complexity= coverage=` | gap reference |
| `Scores:` | `sec= quality= arch= perf= resil= test= stack= dx= docs= overall= model=` | ds-ship delegation order (lowest first); ds-review/ds-mobile/ds-frontend focus |

**Forbidden lines** (they fail the gate): timestamps, run dates, score deltas or histories, owner/maintainer info, pitch/tagline, onboarding steps, TODO lists, philosophy quotes, CI/deploy commands, file-by-file notes, vendor changelogs. They go to `git log`, `README.md`, `ds/audit/findings.md`, or `CHANGELOG.md`.

**Read/write rules**

1. Detect first: standard headings → update in place; legacy markers (HTML comment pairs, variant headings containing "Blueprint Profile") → leave the legacy block untouched, write a standard block, report what the legacy block holds that the new one does not; none → append at end of file; the file does not exist → create it with the profile only.
2. Never write a second standard profile into a file that has one.
3. Update = rewrite only `Scores:` and `Signals:`; every other line changes only on `--refresh` (re-detection) or through the Foundation pass (`--init`/`--ask`, per-line confirmation for `Mission`, `Target`, `Priorities`, `Constraints`, `Red lines`).
4. Nothing outside the two headings is ever modified.
5. After every write: count the block's lines; > 25 → merge multi-key lines, drop `External` entries without a purpose, drop `Modules` entries with zero files; still > 25 → WARN in the summary with the offending line indices.

**Consumers read the profile before their own detection** — `Type`/`Stack`/`Toolchain` skip re-detection; `Target` calibrates severity (prototype lenient, enterprise strict); `Priorities` order scopes; `Constraints`/`Red lines` turn conflicting proposals into `only you can do`; `Scores` focus effort on the lowest dimensions; `Signals` resolve which scopes apply at all.
