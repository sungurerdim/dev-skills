---
name: ds-test
description: Universal test skill — generate, update, run, and fix tests for any stack. Use when writing, repairing, or running tests, or improving coverage.
---

# /ds-test

AI-generated tests often mock everything, assert nothing useful, and break on the first refactor. Skill generates tests that follow project's patterns and verifies they actually pass.

**Universal Test Skill** — Generate, update, run, and fix tests for any stack.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-test`
- User asks to write, add, generate tests, or improve test coverage
- User asks to run tests and fix failures
- User asks to add E2E, integration, or unit tests
- User asks "why is this test failing" or "update tests after refactor"
- After a refactor or feature change, suggest updating affected tests

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "write tests for this function", "improve test coverage" | "framework setup decisions for greenfield" (→ ds-init or ds-research) |
| "generate E2E tests", "update tests after refactor" | "audit test discipline at architecture level" (→ ds-review --strategic --scope=testing) |
| "why is this test failing — fix the test" | "fix the code so the test passes" (→ ds-fix or manual) |
| "add regression test for this bug" | "audit functional completeness" (→ ds-review --strategic) |
| "capture current behavior before I refactor this", "baseline this module" | "refactor the module" (→ ds-fix or manual after baseline is green) |

## Contract

**Dimensions:** B3

- Generates tests that follow project's existing test patterns and conventions; preserves existing passing tests — overwrites only with explicit confirmation
- Always runs generated tests to verify they pass before declaring done
- Uses project's existing test framework — never introduces a new framework unless none exists; test files go in project's established test directory (auto-detected)
- Does NOT fix application code to make tests pass — fixes the TEST if test is wrong, or reports app bug if app is wrong
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- Writes `ds/audit/findings.md` only when a test run confirms an application bug (scope `app-bugs`) or files a critical-flow-wiring gap (scope `testing`) — never for test-quality-only observations; verifies `ds/audit/` is in `.gitignore` before the first write, appending the line when absent.
- **State-exempt:** generated/updated test files on disk are the progress record; re-running naturally resumes.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Show mode menu below |
| `--generate` | Generate tests for uncovered code |
| `--update` | Update existing tests to match current source code |
| `--run` | Run tests, analyze failures, fix what's possible |
| `--e2e` | Generate or run E2E / integration tests |
| `--coverage` | Analyze coverage gaps and fill them |
| `--setup` | Set up test framework and infrastructure |
| `--prune` | Find and delete low-value tests, replace with meaningful ones |
| `--scope={path}` | Limit to specific file, directory, or module |
| `--baseline[=path]` | Characterization baseline: capture current actual behavior of a legacy module before refactoring; tests assert what the code DOES today, not what it should do. Optional `=path` narrows to a specific file, directory, or module. |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

### Mode Resolution (no mode flag)

| Repo state | Resolved mode |
|------------|---------------|
| Request names baseline / prune / coverage / E2E intent explicitly | That mode, regardless of the rows below |
| No test framework detected | Setup (2d) |
| No tests exist for the target scope | Generate (2a) |
| Tests exist and the suite is currently red | Run + Fix (2c) |
| Tests exist, suite green, source changed since the test file's last touch | Update (2b) |
| Both — some target files untested AND the existing suite is red | Run + Fix (2c) first to establish true failures, then decide: fix the failures, generate for the files still uncovered |

Default: the table above resolves the mode from repo state and the request; the choice is recorded in the summary — the resolved mode enters the matching phase (2a-2e) as if its flag were passed. `--ask`: show the mode menu below instead of resolving silently. Any mode flag (`--generate`, `--update`, `--run`, `--e2e`, `--coverage`, `--setup`, `--prune`, `--baseline`) overrides both and skips straight to its phase. No two phases claim the same input: the table above is the single tie-breaker when no flag is passed.

### Mode Menu (`--ask`, no mode flag)

| Mode | What it does |
|------|--------------|
| Generate (recommended) | Generate tests for uncovered code |
| Update | Update existing tests to match current source |
| Run + Fix | Run tests, analyze failures, fix what's possible |
| E2E | Generate or run E2E / integration tests |
| Coverage | Analyze coverage gaps and fill them |
| Setup | Set up test framework and infrastructure |
| Prune | Find and delete low-value tests, replace with meaningful ones |
| Baseline | Characterize a legacy module's current behavior before refactoring |
| Full lifecycle (all) | Generate, then run + fix, in one pass |
| (Cancel) | Exit, no changes |

## Scopes

| Scope | What It Covers |
|-------|---------------|
| `unit` | Single function/method tests; mock only external boundaries (network, filesystem, time), never internal modules |
| `integration` | Multi-module tests, real dependencies where possible |
| `e2e` | End-to-end via browser/UI automation or API calls |
| `snapshot` | Snapshot/golden tests for UI components or serialized output |
| `fixture` | Test data setup, factories, builders, seed files |
| `contract` | API-boundary contract tests — fails on schema drift (OpenAPI/GraphQL/protobuf/JSON Schema for events) |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| `unit` | any source | — |
| `integration` | any source | — |
| `e2e` | `ui`≠`none` or `api`≠`none`, requested via `--e2e`/`--scope=e2e` | N/A — no UI/API surface, or not requested |
| `snapshot` | `ui` in {web, ios, android, desktop} | N/A — no UI surface |
| `fixture` | any source | — |
| `contract` | OpenAPI/Swagger file, GraphQL schema, protobuf, or JSON Schema for events detected | N/A — no API boundary artifact |

`--scope=` overrides the table for the named scopes; `--ask` shows the resolved table before running.

| Reference | Loaded when |
|-----------|-------------|
| [references/generate-detail.md](references/generate-detail.md) | Phase 2a runs |
| [references/gates-value-and-prune.md](references/gates-value-and-prune.md) | Phase 2a runs, or `--prune` mode runs |
| [references/rules-testing.md](references/rules-testing.md) | `contract` scope resolves to run |
| [references/baseline-mode.md](references/baseline-mode.md) | `--baseline` mode runs |

## Delegation

**Owns:** test-generation, test-run-fix, coverage, test-regression, e2e, contract | **Delegates:** none | **Receives:** ds-deps → post-upgrade test run; ds-issue → regression-test generation; ds-tune → per-experiment test validation; ds-ship → Phase 2 rule audit; ds-quality → starter-suite generation when the project has zero tests. Verified consumer of ds-blueprint findings (testing, functional-completeness): generates/fixes tests from them, does not re-produce scan findings.; ds-freeze → kept-set aggregate green check; ds-build → red-proven regression tests for fix-type units; ds-debug → regression-test red-proof for a localized bug

## Execution Flow

Setup → [Generate / Update / Run+Fix / Baseline] → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → read findings with `testing` scope; use to prioritize which modules need tests (skip own coverage analysis for covered scopes). Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
2. **Upstream artifacts:** Profile → {Ideal Metrics.Coverage, Project Map.Toolchain, Current Scores.Testing, Type + Stack}. Findings({testing}) → verify + use. Absent → own analysis.
3. **Detect test framework** from project config + dependencies. See [../core/toolchains.md](../core/toolchains.md).
4. **Detect test conventions:** test directory (`test/`, `tests/`, `__tests__/`, `spec/`, `src/**/*.test.*`); naming pattern (`*_test.go`, `*.test.ts`, `*.spec.rb`, `test_*.py`); helper/fixture locations (`fixtures/`, `factories/`, `support/`, `conftest.py`); mock patterns (mocking library + structure).
5. **Read 2-3 existing test files** to learn project style: imports, assertion style (`expect` vs `assert`), `describe`/`it` vs `test()`, mock + fixture usage, setup/teardown patterns.
6. No framework + `--setup` → proceed to Framework Setup (Phase 2d). No framework + no `--setup` → suggest running with `--setup`.
7. **Checkpoint pre-gate (before the first file write):** `git status --porcelain` — clean, or every planned write is disjoint from dirty paths → proceed; a planned write targets a dirty path → skip that file, record `only you can do: uncommitted changes in {file}`. Full protocol (the `--ask` menu, stop conditions): [../core/checkpoint-protocol.md](../core/checkpoint-protocol.md). Never run a bulk test rewrite over uncommitted unrelated changes in the same files.

**Gate:** Test framework detected or `--setup` mode. If fails → no framework + no `--setup` → "No test framework detected. Re-run with --setup to install one, or specify your framework." Exit with WARN; do not attempt generation without a framework.

### Phase 2a: Generate [--generate or --coverage]

Per uncovered source file (or scoped path):

1. Read source — understand public interface (exported functions, class methods, API endpoints).
2. Identify test-worthy targets: public functions/methods with logic (not simple getters); edge cases (null, empty arrays, boundary values, error paths); branches (every if/else, switch case, try/catch).
3. Generate test file following project conventions: match naming, import style, assertion library; group by function/method using `describe`/`context`; include happy path + edge cases + error cases; per test: clear name describing **behavior**, not implementation.
4. **Integration tests:** identify cross-module interactions, test integration points with minimal mocking. **E2E tests (`--e2e`):** identify user flows, generate browser/API test scenarios — E2E framework detection in [../core/toolchains.md](../core/toolchains.md).

**Test naming rule:** describe WHAT the behavior is, not HOW it's implemented — `"returns empty array when no items match filter"` (good, behavior) vs `"test filterItems function"` (bad, implementation); `"rejects login with expired token"` vs `"test authentication"`.

**Client-side test scenarios** (mobile/web SPA/desktop: layout, font scaling, theme, accessibility) **and test ratio guideline** (unit/integration/E2E distribution by project type): [references/generate-detail.md](references/generate-detail.md).

**Contract tests (`contract` scope):** API boundary artifact detected (OpenAPI/Swagger, GraphQL schema, protobuf, JSON Schema for events) → generate a schema-drift test per [references/rules-testing.md](references/rules-testing.md) TST-01. Same red-proof gate + flaky procedure as every other generated test (Phase 3 Verify).

**Gate:** Test files generated covering happy path + edge cases + error cases per target. If fails → source file has no testable public interface or unreadable → skip, note `{ file, status: "skipped", reason: "no public interface" }` for the summary, continue with remaining files.

### Phase 2b: Update [--update]

1. Identify changed source files (`git diff --name-only HEAD` plus staged, or user-specified scope); per changed file, find its corresponding test file.
2. Compare source changes: new params, renamed methods, changed return types, removed functions.
3. Update test file: new params → update calls, add tests for new param edge cases; renamed method → update references; changed return type → update assertions; new function → generate new tests (per Phase 2a). Removed function — default: remove its tests automatically (reversible via git), recorded in the summary. `--ask`: confirm before removing, else mark `skipped` with TODO.
4. Run updated tests to verify passing.

**Gate:** Updated tests pass; no previously passing tests regressed. If fails → previously passing test now fails → do not weaken assertion; revert test file via `git checkout -- {test-file}`, note `{ test, reason: "regression after update", disposition: "reverted" }` for the summary, write a finding to `ds/audit/findings.md` with scope `app-bugs` identifying the source change that broke the test.

### Phase 2c: Run + Fix [--run]

1. Execute test suite (or scoped subset): detect and run test command from [../core/toolchains.md](../core/toolchains.md). Parse output: extract failures, errors, skipped.
2. Per failure, classify:

| Classification | Action |
|---------------|--------|
| **Test is wrong** (assertion outdated, mock stale, fixture missing) | Fix the test |
| **App is wrong** (source bug causing failure) | Report as app bug — write the finding; the test stays failing at full strength (it now pins the regression). Never modify test or source to force green |
| **Environment issue** (missing dep, config, DB not running) | Report with setup instructions |
| **Flaky test** (timing, ordering — passes sometimes) | Re-run 3× isolated + 1× shuffled-order before quarantine (see Phase 3 gate) |

3. Fix test-side issues automatically. For app bugs, write a finding to `ds/audit/findings.md` with scope `app-bugs` (NOT `testing` — `testing` scope is reserved for code-quality findings about coverage and test quality).
4. Re-run to verify fixes. Max 3 fix-run iterations.

**Critical rule:** passing-before/failing-after a source change signals a regression in the source, not the test — never weaken the assertion to reach green.

**Gate:** Test-side fixes verified passing or app bugs written to `ds/audit/findings.md`. If fails → test-side fix did not pass after 3 iterations → mark `failed (unfixable test-side issue)` for the summary, leave test in best-attempt state, write app-bug finding to `ds/audit/findings.md` with captured output, continue to Phase 3.

### Phase 2d: Framework Setup [--setup]

If no test framework exists:

1. Detect stack from manifests; recommend canonical framework for stack (see [../core/toolchains.md](../core/toolchains.md)). Default: the recommended canonical framework is selected automatically, recorded in the summary. `--ask`: confirm the framework choice before installing.
2. Install + create config: add test dependency to manifest (`package.json`, `pyproject.toml`, etc.); create test config (`jest.config.ts`, `pytest.ini`, etc.); create test directory with example test; add test script to manifest (`"test": "vitest"` in `package.json` etc.); add test step to CI config if it exists.
3. Run example test to verify setup works.

**Gate:** Example test passes with installed framework. If fails → install succeeded but example fails → collect runner error, surface "Framework installed but example test failed: {error}. Check {framework} configuration or run {test-command} manually to diagnose." Exit with WARN — do not generate tests over a broken setup.

### Phase 2e: Baseline [--baseline]

Capture current actual behavior of a legacy module as a characterization baseline before any refactoring begins. Tests assert what the code DOES today; correctness is assessed separately. Full steps (identify surface, generate characterization tests, run to green, report coverage %) and the assertion-weakening distinction: [references/baseline-mode.md](references/baseline-mode.md).

**Gate:** All characterization tests green AND surface-coverage % reported. If a characterization test fails to reach green after 3 iterations (e.g., output is stateful or side-effectful in an unresolvable way) → note `{ test, status: "unresolvable", reason }` for the summary, write a Category B finding describing the untestable surface, continue with remaining members.

### Phase 3: Verify

| Input state | Action | Verify signal |
|--------------|--------|---------------|
| Uncovered source targeted | generate | New tests pass; zero regressions; coverage delta reported when a coverage tool is configured |
| Source changed since the test file's last touch | update | Updated tests pass; zero regressions |
| Suite executed | run | Every failure classified (test-wrong / app-wrong / environment / flaky) |
| Test-side failure classified | fix | Fix re-run passes within 3 iterations, or reverted with disposition `failed (mechanical gate)` |
| Low-value test flagged | prune | Suite green after deletion; a replacement test (when generated) passes |
| Coverage gap identified | coverage | New tests targeting the gap pass; coverage delta reported |

Every row also requires: **Mechanical Done Gate** — touched test files pass the project's lint/type checks; resolve `{check-cmd}` from the ds-quality enforcement arm when installed (stop-hook / pre-commit hook / auto-lint), else stack-native lint/type commands ([../core/toolchains.md](../core/toolchains.md)); a test that passes but breaks the lint/type gate blocks "done" the same as a failing test (≤3 fix attempts, then revert via `git checkout -- {test-file}`, disposition `failed (mechanical gate)`). The full-suite run's exact command + observed output is the Completion Evidence; a red that predates this run is reported red-at-baseline, never inherited as green. **Critical-flow wiring check** ([../core/principles.md §7](../core/principles.md)): identify flows tagged critical — money-moving, auth-gating, data-deleting — from the blueprint profile's `Data:`/`Regulations:` signals when available, else path/name heuristics (`payment`, `refund`, `billing`, `charge`, `checkout`, `login`, `auth`, `token`, `permission`, `delete`, `purge`, `drop`). Per critical flow, confirm at least one test exercises its real dispatch/registry/facade (no mock of that internal layer) — a critical flow with zero such tests is a HIGH finding (`scope: testing`) written to `ds/audit/findings.md`, never silently passed. Baseline (`--baseline`) verifies through its own gate (Phase 2e).

**Gate:** Every row's verify signal observed for the action(s) taken; zero regressions; every detected critical flow has ≥1 mock-free wiring test or a corresponding HIGH finding; every generated regression test was observed red against the unfixed code before green, both outputs captured; a test suspected flaky has 3 isolated runs + 1 shuffled-order run before quarantine. If fails → collect runner output per failing test, classify (test wrong / app wrong / environment / flaky); fix test-side inline (max 3 iterations per test); app-bug failures → write to `ds/audit/findings.md` with scope `app-bugs`; environment → surface setup instructions; a regression test never observed red → rewrite it before marking the app-bug resolved; a flaky test quarantined without the 4 runs → run them now, then quarantine with a linked issue (`/ds-issue` when present, else `only you can do: file and link a tracking issue`), never delete or retry-until-green. Do not commit failing tests — note as `failing` for the summary, report count in summary.

### Phase 4: Needs-Approval Review [needs_approval > 0]

**Default:** every item resolves automatically using the same impact/effort/risk reasoning an approval block would show, recorded in the summary; items matching the publish/irreversible exception list are skipped and recorded `only you can do` instead. **`--ask`:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → unresolved → mark `skipped (no response)` and proceed.

### Phase 5: Summary

```
ds-test: {OK|WARN|FAIL} | Generated: {n} | Updated: {n} | Fixed: {n} | Skipped: {n} | Failing: {n}

| Action    | Count | Details                                  |
|-----------|-------|------------------------------------------|
| Generated | {n}   | {n} unit, {n} integration                |
| Updated   | {n}   | matched source changes                   |
| Fixed     | {n}   | {n} assertion, {n} mock                  |
| Failing   | {n}   | app bugs (see ds/audit/findings.md)      |
| Critical-flow wiring | {n}/{n} | flows verified mock-free (see ds/audit/findings.md for gaps) |
```

Disposition accounting — totals balance. Closing shape (`Decided without asking` lines, every `only you can do` item in full): [../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md).

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} tests generated covering {n} previously-untested branches — coverage rose from {before}% to {after}% on {scope}`
- `{n} flaky tests fixed (sleep-based → event-based, time-dependent → fixed-clock) — CI failure rate from non-determinism eliminated`
- `{n} regression tests added (one per bug-fix) — same defect can no longer reach main twice`
- `Test Pyramid restored: {n} E2E tests replaced by faster unit + integration equivalents — total suite runtime dropped from {before}s to {after}s`

Audit-only run: `{n} test-quality findings (missing AAA, unrealistic data, no boundary cases) — actionable list returned, no tests modified`.

**Gate:** Summary table + Effect rendered; every action has a disposition; accounting verified. If fails → undisposed action or imbalanced counts → assign `failed (disposition missing)`, recompute totals, reprint with corrected counts, set status WARN.

## Quality Gates

**Value Rule (most important, W12 anti reward-hacking):** every test MUST justify its existence against a concrete, specific risk — before writing any test, answer "what bug would this catch?"; vague or "none really" → skip the test. Full detail — rationalization-rebuttal table, `--prune` phase (detect/approve/delete/replace low-value tests, advisory mutation check), discipline rules (Test Pyramid, boundary conditions, critical-flow rationale, scale-envelope fixture, AAA structure, regression-before-fix, unreproduced-bug handling, coverage-as-diagnostic, property-based tests, snapshot discipline): [references/gates-value-and-prune.md](references/gates-value-and-prune.md).

- Generated tests must pass before declaring done — never commit failing tests. Keep assertions at full strength — fix the test logic or report the app bug instead of weakening checks.
- Test names describe behavior, not implementation. No test depends on execution order — each independently runnable. Mocks minimal — only mock external dependencies (network, filesystem, time), not internal modules.
- **Critical-flow wiring check (B3):** detection mechanism and Gate wording live in Phase 3 Verify. Rationale: mocking the dispatch/registry/facade layer can hide a handler that was written but never registered — invisible to both a unit test of the handler and a facade-mocked integration test.

- W9: state-exempt — generated/updated test files on disk are the progress record; re-running naturally resumes. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W12: every test verifies described intent + a case beyond the given suite — never special-case known inputs or assert hard-coded outputs to pass.
- W1: cite file:line; never assume. W2: check consumers after modify. W3: touch only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| Test framework not detected | Ask user which framework to use |
| Generated test fails on first run | Read error, fix test logic (fix the test, not the source) |
| Source file has no testable public interface | Skip with note "No public API to test" |
| Coverage tool unavailable | Skip coverage report, generate tests based on source analysis |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No test framework installed | Suggest `--setup`, or skip with warning |
| No existing tests to learn from | Use canonical conventions for detected stack |
| Source file has no testable public API | Skip with note "no public interface to test" |
| Test framework not recognized | Ask user for test command, proceed with manual config |
| Monorepo with multiple test frameworks | Detect per-package, run each package's framework |
| E2E requires running server | Check for dev server script, start it, run tests, stop it |
| Coverage tool not configured | Skip coverage analysis, suggest setup |
| Default run with failing app tests | Write findings to `ds/audit/findings.md`; fix test-side failures only — app-bug tests stay failing at full strength |
| `--baseline` and output is nondeterministic (time, random, UUID) | Inject/freeze seams (fixed clock, seeded RNG, mocked UUID) before capturing; unavailable → assert invariant properties (type, range, non-null) instead of exact values, tagged `// characterization:` |
| `--baseline` and source module has no public interface (all private/internal) | Report as Category B finding: "No public surface to baseline — refactoring this module without tests is high-risk"; suggest making key behaviors accessible for testing or adding internal test hooks |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
