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
- **State-exempt:** generated/updated test files on disk are the progress record; re-running naturally resumes.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

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
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

### Mode Menu (no mode flag passed)

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
| Full lifecycle (all) | Generate + run + fix in one autonomous pass (`--auto`) |
| (Cancel) | Exit, no changes |

Shown only when no mode flag is passed — any flag above (`--generate`, `--update`, `--run`, `--e2e`, `--coverage`, `--setup`, `--prune`, `--baseline`, `--auto`) disambiguates and skips the menu.

## Scopes

| Scope | What It Covers |
|-------|---------------|
| `unit` | Single function/method tests; mock only external boundaries (network, filesystem, time), never internal modules |
| `integration` | Multi-module tests, real dependencies where possible |
| `e2e` | End-to-end via browser/UI automation or API calls |
| `snapshot` | Snapshot/golden tests for UI components or serialized output |
| `fixture` | Test data setup, factories, builders, seed files |

Default: `unit` + `integration`. E2E and snapshot require explicit `--e2e` or `--scope`.

## Delegation

**Owns:** test-generation, test-run-fix, coverage, test-regression, e2e | **Delegates:** none | **Receives:** ds-deps → post-upgrade test run; ds-issue → regression-test generation; ds-tune → per-experiment test validation; ds-ship → Phase 2 rule audit. Verified consumer of ds-blueprint findings (testing, functional-completeness): generates/fixes tests from them, does not re-produce scan findings.; ds-freeze → kept-set aggregate green check

## Execution Flow

Setup → [Generate / Update / Run+Fix / Baseline] → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → read findings with `testing` scope; use to prioritize which modules need tests (skip own coverage analysis for covered scopes). Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
2. **IDU:** Profile → {Ideal Metrics.Coverage, Project Map.Toolchain, Current Scores.Testing, Type + Stack}. Findings({testing}) → verify + use. Absent → own analysis.
3. **Detect test framework** from project config + dependencies. See [references/frameworks.md](references/frameworks.md).
4. **Detect test conventions:** test directory (`test/`, `tests/`, `__tests__/`, `spec/`, `src/**/*.test.*`); naming pattern (`*_test.go`, `*.test.ts`, `*.spec.rb`, `test_*.py`); helper/fixture locations (`fixtures/`, `factories/`, `support/`, `conftest.py`); mock patterns (mocking library + structure).
5. **Read 2-3 existing test files** to learn project style: imports, assertion style (`expect` vs `assert`), `describe`/`it` vs `test()`, mock + fixture usage, setup/teardown patterns.
6. No framework + `--setup` → proceed to Framework Setup (Phase 2d). No framework + no `--setup` → suggest running with `--setup`.

**Gate:** Test framework detected or `--setup` mode. If fails → no framework + no `--setup` → "No test framework detected. Re-run with --setup to install one, or specify your framework." Exit with WARN; do not attempt generation without a framework.

### Phase 2a: Generate [--generate or --coverage]

Per uncovered source file (or scoped path):

1. Read source — understand public interface (exported functions, class methods, API endpoints).
2. Identify test-worthy targets: public functions/methods with logic (not simple getters); edge cases (null, empty arrays, boundary values, error paths); branches (every if/else, switch case, try/catch).
3. Generate test file following project conventions: match naming, import style, assertion library; group by function/method using `describe`/`context`; include happy path + edge cases + error cases; per test: clear name describing **behavior**, not implementation.
4. **Integration tests:** identify cross-module interactions, test integration points with minimal mocking. **E2E tests (`--e2e`):** identify user flows, generate browser/API test scenarios — E2E framework detection in [references/frameworks.md](references/frameworks.md).

**Test naming rule:** describe WHAT the behavior is, not HOW it's implemented — `"returns empty array when no items match filter"` (good, behavior) vs `"test filterItems function"` (bad, implementation); `"rejects login with expired token"` vs `"test authentication"`.

**Client-side test scenarios (platform = mobile / web SPA / desktop):**

| Category | Required scenarios |
|----------|-------------------|
| Responsive layout | Viewport profiles 320dp / 375dp / 412dp / 744dp / 1024dp (minimum); portrait + landscape; no layout overflow |
| Font scaling | 0.8× / 1.0× / 1.3× system font scale; text readable, layouts intact |
| Theme | Light + dark mode render correctly; no hardcoded colors bypassing theme system |
| Accessibility | Screen reader (TalkBack / VoiceOver / Narrator / NVDA) traversal; all interactive elements have a11y labels; error states announced |

**Test ratio guideline (approximate distribution by project type — not simultaneous minimums):**

| Type | Unit | Component/Integration | E2E |
|------|------|-----------------------|-----|
| Mobile | ~70% | ~20% | ~10% |
| Web SPA | ~60% | ~25% | ~15% |
| API | ~60% | ~30% | ~10% |
| Library | ~80% | ~15% | ~5% |

**Gate:** Test files generated covering happy path + edge cases + error cases per target. If fails → source file has no testable public interface or unreadable → skip, note `{ file, status: "skipped", reason: "no public interface" }` for the summary, continue with remaining files.

### Phase 2b: Update [--update]

1. Identify changed source files (from `git diff` or user-specified scope); per changed file, find its corresponding test file.
2. Compare source changes: new params, renamed methods, changed return types, removed functions.
3. Update test file: new params → update calls, add tests for new param edge cases; renamed method → update references; changed return type → update assertions; removed function → remove tests (with confirmation) or mark `skipped` with TODO; new function → generate new tests (per Phase 2a). Under `--auto`: skip the confirmation — removed-function tests are removed automatically (reversible via git), recorded in the summary.
4. Run updated tests to verify passing.

**Gate:** Updated tests pass; no previously passing tests regressed. If fails → previously passing test now fails → do not weaken assertion; revert test file via `git checkout -- {test-file}`, note `{ test, reason: "regression after update", disposition: "reverted" }` for the summary, write a finding to `ds/audit/findings.md` with scope `app-bugs` identifying the source change that broke the test.

### Phase 2c: Run + Fix [--run]

1. Execute test suite (or scoped subset): detect and run test command from [references/frameworks.md](references/frameworks.md). Parse output: extract failures, errors, skipped.
2. Per failure, classify:

| Classification | Action |
|---------------|--------|
| **Test is wrong** (assertion outdated, mock stale, fixture missing) | Fix the test |
| **App is wrong** (source bug causing failure) | Report as app bug — write the finding; the test stays failing at full strength (it now pins the regression). Never modify test or source to force green |
| **Environment issue** (missing dep, config, DB not running) | Report with setup instructions |
| **Flaky test** (timing, ordering — passes sometimes) | Flag as flaky, suggest fix approach |

3. Fix test-side issues automatically. For app bugs, write a finding to `ds/audit/findings.md` with scope `app-bugs` (NOT `testing` — `testing` scope is reserved for code-quality findings about coverage and test quality).
4. Re-run to verify fixes. Max 3 fix-run iterations.

**Critical rule:** test was passing before, fails after source change → SOURCE is likely wrong (regression), not the test. Keep assertions at full strength — fix test logic or report app bug.

**Gate:** Test-side fixes verified passing or app bugs written to `ds/audit/findings.md`. If fails → test-side fix did not pass after 3 iterations → mark `failed (unfixable test-side issue)` for the summary, leave test in best-attempt state, write app-bug finding to `ds/audit/findings.md` with captured output, continue to Phase 3.

### Phase 2d: Framework Setup [--setup]

If no test framework exists:

1. Detect stack from manifests; recommend canonical framework for stack (see [references/frameworks.md](references/frameworks.md)); ask user to confirm framework choice. Under `--auto`: skip the question — the recommended canonical framework is selected automatically.
2. Install + create config: add test dependency to manifest (`package.json`, `pyproject.toml`, etc.); create test config (`jest.config.ts`, `pytest.ini`, etc.); create test directory with example test; add test script to manifest (`"test": "vitest"` in `package.json` etc.); add test step to CI config if it exists.
3. Run example test to verify setup works.

**Gate:** Example test passes with installed framework. If fails → install succeeded but example fails → collect runner error, surface "Framework installed but example test failed: {error}. Check {framework} configuration or run {test-command} manually to diagnose." Exit with WARN — do not generate tests over a broken setup.

### Phase 2e: Baseline [--baseline]

Capture current actual behavior of a legacy module as a characterization baseline before any refactoring begins. Tests assert what the code DOES today; correctness is assessed separately.

1. **Identify surface:** collect the target module's public interface (exported functions, class/struct methods, CLI commands, API endpoints). `=path` provided → narrow to that path only; otherwise use the directory or module containing the changed code.
2. **Generate characterization tests:** drive each surface member with realistic inputs including boundary cases (empty, null, max-size, unicode, boundary numerics). Record the ACTUAL outputs — whatever the code returns today — as expected values. When current behavior appears incorrect (e.g., off-by-one, wrong default, silent swallow of an error), STILL assert it; tag the test with the comment `// characterization: documents current behavior, not intent` and raise a Category B finding (`needs-approval`) so the user decides fix-vs-keep before refactoring.
3. **Run to green:** a failing characterization test means the captured expectation is wrong — fix the TEST to match actual output, never modify the source. Repeat until all pass.
4. **Report:** surface-coverage % (ratio of public surface members with at least one characterization test) + list of oddities raised as Category B findings.

**Note — not assertion-weakening:** asserting observed behavior (even when it looks incorrect) with a `characterization: documents current behavior, not intent` tag and a Category B finding is the correct pattern — documented capture + user decision gate, never silent acceptance of a relaxed assertion.

**Gate:** All characterization tests green AND surface-coverage % reported. If a characterization test fails to reach green after 3 iterations (e.g., output is stateful or side-effectful in an unresolvable way) → note `{ test, status: "unresolvable", reason }` for the summary, write a Category B finding describing the untestable surface, continue with remaining members.

### Phase 3: Verify

After any generate/update/fix: (1) run full test suite (or scoped subset); (2) all generated/modified tests must pass; (3) no previously passing test should now fail (regression check); (4) report coverage delta if coverage tool is configured; (5) **Mechanical Done Gate (SKILL-SPEC §4):** generated/modified test files pass the project's lint/type checks too — resolve `{check-cmd}` from the ds-quality enforcement arm when installed (stop-hook / pre-commit hook / auto-lint), else stack-native lint/type commands, and run it on the touched test files; a test that passes but breaks the lint/type gate blocks "done" the same as a failing test (≤3 fix attempts, then revert the test file via `git checkout -- {test-file}`, disposition `failed (mechanical gate)`). The full-suite run's exact command + observed output is the Completion Evidence; a red that predates this run is reported red-at-baseline, never inherited as green.

**Gate:** All generated tests pass; zero regressions. If fails → collect runner output per failing test, classify (test wrong / app wrong / environment / flaky). Fix test-side inline (max 3 iterations per test). App-bug failures → write to `ds/audit/findings.md` with scope `app-bugs`. Environment → surface setup instructions. Do not commit failing tests — note as `failing` for the summary, report count in summary.

### Phase 4: Needs-Approval Review [needs_approval > 0]

**Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set. **Under `--auto`:** no review step is shown — every item resolves automatically using the same impact/effort/risk reasoning the interactive block would show, recorded in the summary; items matching the Unattended Mode rule-4 exception list are skipped and recorded `needs-human` instead.

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
```

**Value Delivered:** 1-5 concrete bullets, real test outcomes only. Example shapes (placeholders, not literal):

- `{n} tests generated covering {n} previously-untested branches — coverage rose from {before}% to {after}% on {scope}`
- `{n} flaky tests fixed (sleep-based → event-based, time-dependent → fixed-clock) — CI failure rate from non-determinism eliminated`
- `{n} regression tests added (one per bug-fix) — same defect can no longer reach main twice`
- `Test Pyramid restored: {n} E2E tests replaced by faster unit + integration equivalents — total suite runtime dropped from {before}s to {after}s`

Audit-only run: `{n} test-quality findings (missing AAA, unrealistic data, no boundary cases) — actionable list returned, no tests modified`.

**Gate:** Summary table + Value Delivered rendered; every action has a disposition; accounting verified. If fails → undisposed action or imbalanced counts → assign `failed (disposition missing)`, recompute totals, reprint with corrected counts, set status WARN.

## Quality Gates

### Value Rule (most important) — W12 (anti reward-hacking)

Every test MUST justify its existence by addressing a **concrete, specific risk**. Before writing any test, answer: "What bug would this catch?" If the answer is vague or "none really", skip the test.

| Write this test | Skip — this test validates… |
|----------------|----------------------|
| `"Catches division by zero when quantity is 0"` | `"Tests that constructor sets properties"` |
| `"Verifies auth rejects expired JWT tokens"` | `"Tests that getter returns the field value"` |
| `"Verifies race condition in concurrent balance update"` | `"Tests that add(2,3) returns 5 for a trivial wrapper"` |

**Rationalization table (W12):** these excuses never override the Value Rule or the gates below — rebut and proceed:

| Excuse | Rebuttal |
|--------|----------|
| "Too simple to test" | Simple code breaks; the test costs seconds |
| "I'll test after it settles" | A test that passes on first run proves nothing about failure detection |
| "Already manually verified" | Ad-hoc checks are not re-runnable; regressions return silently |
| "Coverage is already high" | Coverage proves execution, not assertion strength — run the mutation check below |
| "Deleting untested code wastes the hours spent writing it" | Sunk cost; unverified code is debt, not progress |
| "Weakening this assertion turns the suite green" | A green suite that stops constraining behavior is the W12 failure itself |

**Prune phase (`--prune` or part of `--auto`):** flag existing tests that provide no concrete value:

1. Search for tests asserting only: constructor/getter/setter behavior, trivial pass-through, framework-guaranteed behavior, 1:1 reimplementation of source code, or oversized snapshots (>100 lines — assert everything, verify nothing). Flag as CRITICAL (reward-hacking class, not merely low-value): assertions hard-coding expected outputs for special-cased known inputs, and test edits that weaken or bypass assertions to reach green.
2. Present flagged tests as table `| # | Test | File:Line | Reason | Action |` grouped by Reason with counts; state the question (`Delete these N tests?`). Ask: **Delete all** / **Delete all <reason>** (per-reason bulk alongside the total) / **Review each** / **Keep all**. "All" = exactly the displayed set. Under `--auto`: no question shown — resolves automatically to delete all flagged tests (reversible via git), reported with reasons in the summary.
3. **Replacement rule:** after deleting a low-value test, check if file/module now has meaningful untested logic. Yes → generate a valuable replacement test targeting a real risk.
4. **Mutation check (advisory):** stack's mutation tool available (per-stack table in [references/frameworks.md §Mutation Testing](references/frameworks.md)) → run it on the scoped module, report mutation score beside line coverage, treat every surviving mutant as a weak-assertion finding, and feed each into `--generate`/`--update` as a targeted instruction (`mutant at {file}:{line} survived — add the assertion that kills it`) instead of regenerating whole files. Tool absent → gap-note `mutation tool unavailable — assertion quality verified by pattern review only`, apply the step-1 pattern list as the fallback detector. Coverage alone is not proof: a documented real-world suite reported 93% line coverage against a 58.62% mutation score — a 34-point gap of assertions that constrain nothing.

### Other Gates

Discipline rules below (Test Pyramid, Boundary conditions, AAA structure, Regression-before-fix, Coverage-as-diagnostic) derive from [references/principles.md §7](references/principles.md).

- Generated tests must pass before declaring done — never commit failing tests.
- Keep assertions at full strength — fix the test logic or report the app bug instead of weakening checks.
- Test names describe behavior, not implementation. No test depends on execution order — each independently runnable.
- Mocks minimal — only mock external dependencies (network, filesystem, time), not internal modules. Generated test matches project's existing style — no style drift.
- **Test Pyramid:** unit-heavy, integration-medium, E2E-light. Detect inverted pyramid (E2E > integration > unit) → flag HIGH before generating more E2E.
- **Boundary conditions:** every generated test suite covers empty, null, max-size, concurrent, locale, timezone, Unicode, leap-day where applicable.
- **Scale-envelope fixture pattern (D1/B3, advisory):** for the project's critical flows, generate a synthetic max-size fixture (e.g. 50k records) and measure those flows against it — this is the *measured, documented* extension of the max-size boundary case above, not a replacement for it. No documented scale limit exists for a critical flow → advisory finding "no declared scale envelope — measure against a synthetic max-size fixture and document the limit" (never a blocker, SKILL-SPEC §15; cross-links to ds-review --perf's Scale Envelope check — present → hand off the measured numbers to it; absent → this finding alone still stands).
- **AAA structure:** every generated test body has visible Arrange / Act / Assert separation — comments or whitespace lines, never one-shot expressions.
- **Regression-before-fix:** in `--run` mode, when an app bug is found, generate the regression test FIRST (failing), confirm it fails, then propose the source fix.
- **Coverage as diagnostic:** never write a coverage target into generated test configs; configure coverage as a reporter only. The diagnostic is "what did we miss?", not "did we hit X%?".
- **Property-based tests (advisory):** target is a pure function with an algebraic property (roundtrip encode/decode, idempotence, commutativity, invariant preservation) AND the stack's property-testing library is already in the project deps (per-stack table in [references/frameworks.md §Property-Based Testing](references/frameworks.md)) → offer a property test for the boundary-condition class instead of hand-enumerating cases; library absent → hand-enumerated boundary cases stand, gap-note the option once.
- **Snapshot discipline:** snapshot tests only for small, stable serialized output (a component's props contract, a config artifact) — a full-page or >100-line snapshot asserts everything and verifies nothing; flag existing ones as low-value in `--prune` step 1.

| Guard | Rule |
|-------|------|
| W1 | Cite file:line; never assume |
| W2 | Check consumers after modify |
| W3 | Touch only task-required lines |
| W4 | Re-read after gap |
| W5 | Uncertain → lower severity |
| W6 | Verify all phases output |
| W7 | Dedup file:line |
| W8 | No raw shell interpolation |
| W9 | State-exempt — generated/updated test files on disk are the progress record; re-running naturally resumes |
| W10 | Defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered |
| W11 | Every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason |
| W12 | Every test verifies described intent + a case beyond the given suite — never special-case known inputs or assert hard-coded outputs to pass |

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
| `--auto` with failing app tests | Write findings to `ds/audit/findings.md`; fix test-side failures only — app-bug tests stay failing at full strength |
| `--baseline` and output is nondeterministic (time, random, UUID) | Inject/freeze seams (fixed clock, seeded RNG, mocked UUID) before capturing; if seams are unavailable, assert invariant properties (type, range, non-null) instead of exact values — document the invariant-only assertion with the `// characterization:` tag |
| `--baseline` and source module has no public interface (all private/internal) | Report as Category B finding: "No public surface to baseline — refactoring this module without tests is high-risk"; suggest making key behaviors accessible for testing or adding internal test hooks |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
