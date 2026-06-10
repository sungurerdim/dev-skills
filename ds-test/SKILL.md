# /ds-test

AI-generated tests often mock everything, assert nothing useful, and break on the first refactor. Skill generates tests that follow project's patterns and verifies they actually pass.

**Universal Test Skill** — Generate, update, run, and fix tests for any stack.

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

- Generates tests that follow project's existing test patterns and conventions
- Preserves existing passing tests — overwrites only with explicit confirmation
- Always runs generated tests to verify they pass before declaring done
- Uses project's existing test framework — never introduces a new framework unless none exists
- Test files go in project's established test directory (auto-detected)
- Does NOT fix application code to make tests pass — fixes the TEST if test is wrong, or reports app bug if app is wrong
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Interactive mode selection |
| `--generate` | Generate tests for uncovered code |
| `--update` | Update existing tests to match current source code |
| `--run` | Run tests, analyze failures, fix what's possible |
| `--e2e` | Generate or run E2E / integration tests |
| `--coverage` | Analyze coverage gaps and fill them |
| `--setup` | Set up test framework and infrastructure |
| `--prune` | Find and delete low-value tests, replace with meaningful ones |
| `--scope={path}` | Limit to specific file, directory, or module |
| `--baseline[=path]` | Characterization baseline: capture current actual behavior of a legacy module before refactoring; tests assert what the code DOES today, not what it should do. Optional `=path` narrows to a specific file, directory, or module. |
| `--auto` | No questions, generate + run + fix cycle |
| `--resume` | Resume from `ds/audit/test.json` without prompting |
| `--clean` | Delete existing state and start fresh |

## Scopes

| Scope | What It Covers |
|-------|---------------|
| `unit` | Single function/method tests, isolated with mocks |
| `integration` | Multi-module tests, real dependencies where possible |
| `e2e` | End-to-end via browser/UI automation or API calls |
| `snapshot` | Snapshot/golden tests for UI components or serialized output |
| `fixture` | Test data setup, factories, builders, seed files |

Default: `unit` + `integration`. E2E and snapshot require explicit `--e2e` or `--scope`.

## Delegation

**Owns:** testing, coverage, test-generation, test-regression, e2e, functional-completeness (test side) | **Delegates:** none | **Receives:** ds-deps → post-upgrade test run; ds-review → test generation for findings; ds-tune → per-experiment test validation

## Execution Flow

Setup → [Generate / Update / Run+Fix / Baseline] → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

**Recovery check:** DETECT `ds/audit/test.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read source files referenced by pending generations, re-check generated test files exist), skip `done` phases, announce `[TST] Resuming from Phase {N}: {name}.` On Summary success, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start.

**State `data`:** `{ mode, framework, files_queued[], files_processed[{file, tests_generated, status}], failures[{test, reason, disposition}], coverage_before, coverage_after }`.

1. **Findings file check:** `ds/audit/findings.md` fresh `git_hash` → read findings with `testing` scope. Use to prioritize which modules need tests (skip own coverage analysis for covered scopes). Stale or absent → run own full analysis.
2. **IDU:** Profile → {Ideal Metrics.Coverage, Project Map.Toolchain, Current Scores.Testing, Type + Stack}. Findings({testing}) → verify + use. Absent → own analysis.
3. **Detect test framework** from project config + dependencies. See [references/frameworks.md](references/frameworks.md).
4. **Detect test conventions:**
   - Test directory: `test/`, `tests/`, `__tests__/`, `spec/`, `src/**/*.test.*`
   - Naming pattern: `*_test.go`, `*.test.ts`, `*.spec.rb`, `test_*.py`
   - Helper/fixture locations: `fixtures/`, `factories/`, `support/`, `conftest.py`
   - Mock patterns: mocking library + structure
5. **Read 2-3 existing test files** to learn project style: imports, assertion style (`expect` vs `assert`), `describe`/`it` vs `test()`, mock + fixture usage, setup/teardown patterns.
6. No framework + `--setup` → proceed to Framework Setup (Phase 2d).
7. No framework + no `--setup` → suggest running with `--setup`.

**Gate:** Test framework detected or `--setup` mode. If fails → no framework + no `--setup` → "No test framework detected. Re-run with --setup to install one, or specify your framework." Exit with WARN; do not attempt generation without a framework.

### Phase 2a: Generate [--generate or --coverage]

Per uncovered source file (or scoped path):

1. Read source — understand public interface (exported functions, class methods, API endpoints).
2. Identify test-worthy targets: public functions/methods with logic (not simple getters); edge cases (null, empty arrays, boundary values, error paths); branches (every if/else, switch case, try/catch).
3. Generate test file following project conventions: match naming, import style, assertion library; group by function/method using `describe`/`context`; include happy path + edge cases + error cases; per test: clear name describing **behavior**, not implementation.
4. **Integration tests:** identify cross-module interactions, test integration points with minimal mocking.
5. **E2E tests (`--e2e`):** identify user flows, generate browser/API test scenarios. See [references/frameworks.md](references/frameworks.md) for E2E framework detection.

**Test naming rule:** describe WHAT the behavior is, not HOW it's implemented.

| Good (behavior) | Bad (implementation) |
|----------------|----------------------|
| `"returns empty array when no items match filter"` | `"test filterItems function"` |
| `"rejects login with expired token"` | `"test authentication"` |
| `"creates order with correct total when discount applied"` | `"test createOrder"` |

**Client-side test scenarios (platform = mobile / web SPA / desktop):**

| Category | Required scenarios |
|----------|-------------------|
| Responsive layout | Viewport profiles 320dp / 375dp / 412dp / 744dp / 1024dp (minimum); portrait + landscape; no layout overflow |
| Font scaling | 0.8× / 1.0× / 1.3× system font scale; text readable, layouts intact |
| Theme | Light + dark mode render correctly; no hardcoded colors bypassing theme system |
| Accessibility | Screen reader (TalkBack / VoiceOver / Narrator / NVDA) traversal; all interactive elements have a11y labels; error states announced |

**Test ratio targets (by project type):**

| Type | Unit | Component/Integration | E2E |
|------|------|-----------------------|-----|
| Mobile | 70%+ | 20%+ | 10%+ |
| Web SPA | 60%+ | 25%+ | 15%+ |
| API | 60%+ | 30%+ | 10%+ |
| Library | 80%+ | 15%+ | 5%+ |

**Gate:** Test files generated covering happy path + edge cases + error cases per target. If fails → source file has no testable public interface or unreadable → skip, record `{ file, status: "skipped", reason: "no public interface" }` in state.data.files_processed, continue with remaining files.

### Phase 2b: Update [--update]

When source changed and tests need updating:

1. Identify changed source files (from `git diff` or user-specified scope).
2. Per changed file, find its corresponding test file.
3. Compare source changes: new params, renamed methods, changed return types, removed functions.
4. Update test file:
   - New params → update calls, add tests for new param edge cases.
   - Renamed method → update references.
   - Changed return type → update assertions.
   - Removed function → remove tests (with confirmation) or mark `skipped` with TODO.
   - New function → generate new tests (per Phase 2a).
5. Run updated tests to verify passing.

**Gate:** Updated tests pass; no previously passing tests regressed. If fails → previously passing test now fails → do not weaken assertion; revert test file via `git checkout -- {test-file}`, record `{ test, reason: "regression after update", disposition: "reverted" }` in state.data.failures, write a finding to `ds/audit/findings.md` with scope `app-bugs` identifying the source change that broke the test.

### Phase 2c: Run + Fix [--run]

1. Execute test suite (or scoped subset): detect and run test command from [references/frameworks.md](references/frameworks.md).
2. Parse output: extract failures, errors, skipped.
3. Per failure, classify:

| Classification | Action |
|---------------|--------|
| **Test is wrong** (assertion outdated, mock stale, fixture missing) | Fix the test |
| **App is wrong** (source bug causing failure) | Report as app bug — fix the test, not the source |
| **Environment issue** (missing dep, config, DB not running) | Report with setup instructions |
| **Flaky test** (timing, ordering — passes sometimes) | Flag as flaky, suggest fix approach |

4. Fix test-side issues automatically. For app bugs, write a finding to `ds/audit/findings.md` with scope `app-bugs` (NOT `testing` — `testing` scope is reserved for code-quality findings about coverage and test quality).
5. Re-run to verify fixes. Max 3 fix-run iterations.

**Critical rule:** test was passing before, fails after source change → SOURCE is likely wrong (regression), not the test. Keep assertions at full strength — fix test logic or report app bug.

**Gate:** Test-side fixes verified passing or app bugs written to `ds/audit/findings.md`. If fails → test-side fix did not pass after 3 iterations → mark `failed (unfixable test-side issue)` in state.data.failures, leave test in best-attempt state, write app-bug finding to `ds/audit/findings.md` with captured output, continue to Phase 3.

### Phase 2d: Framework Setup [--setup]

If no test framework exists:

1. Detect stack from manifests.
2. Recommend canonical framework for stack (see [references/frameworks.md](references/frameworks.md)).
3. Ask user to confirm framework choice.
4. Install + create config:
   - Add test dependency to manifest (`package.json`, `pyproject.toml`, etc.)
   - Create test config (`jest.config.ts`, `pytest.ini`, etc.)
   - Create test directory with example test
   - Add test script to manifest (`"test": "vitest"` in `package.json` etc.)
   - Add test step to CI config if it exists
5. Run example test to verify setup works.

**Gate:** Example test passes with installed framework. If fails → install succeeded but example fails → collect runner error, surface "Framework installed but example test failed: {error}. Check {framework} configuration or run {test-command} manually to diagnose." Exit with WARN — do not generate tests over a broken setup.

### Phase 2e: Baseline [--baseline]

Capture current actual behavior of a legacy module as a characterization baseline before any refactoring begins. Tests assert what the code DOES today; correctness is assessed separately.

1. **Identify surface:** collect the target module's public interface (exported functions, class/struct methods, CLI commands, API endpoints). If `=path` provided, narrow to that path only; otherwise use the directory or module that contains the changed code.
2. **Generate characterization tests:** for each surface member, drive it with realistic inputs including boundary cases (empty, null, max-size, unicode, boundary numerics). Record the ACTUAL outputs — whatever the code returns today — as expected values in the assertions. When current behavior appears incorrect (e.g., off-by-one, wrong default, silent swallow of an error), STILL assert it; tag the test with the comment `// characterization: documents current behavior, not intent` and raise a Category B finding (`needs-approval`) so the user decides fix-vs-keep before refactoring.
3. **Run to green:** execute the characterization suite. A failing characterization test means the captured expectation is wrong — fix the TEST to match actual output, never modify the source. Repeat until all characterization tests pass.
4. **Report:** surface-coverage % (ratio of public surface members with at least one characterization test) + a list of oddities raised as Category B findings.

**Note — not assertion-weakening:** asserting observed (possibly wrong) behavior with a `characterization: documents current behavior, not intent` tag and a Category B finding is the correct pattern. It is NOT the same as silently relaxing an assertion to pass. The intent is documented capture + user decision gate, never silent acceptance.

**Gate:** All characterization tests green AND surface-coverage % reported. If any characterization test cannot be made green after 3 iterations (e.g., output is stateful or side-effectful in an unresolvable way) → record `{ test, status: "unresolvable", reason }` in state.data.failures, write a Category B finding describing the untestable surface, continue with remaining members.

### Phase 3: Verify

After any generate/update/fix:

1. Run full test suite (or scoped subset).
2. All generated/modified tests must pass.
3. No previously passing test should now fail (regression check).
4. Report coverage delta if coverage tool is configured.

**Gate:** All generated tests pass; zero regressions. If fails → collect runner output per failing test, classify (test wrong / app wrong / environment / flaky). Fix test-side inline (max 3 iterations per test). App-bug failures → write to `ds/audit/findings.md` with scope `app-bugs`. Environment → surface setup instructions. Do not commit failing tests — record as `failing` in state.data.failures, report count in summary.

### Phase 4: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

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
| `"Catches SQL injection via unsanitized user input"` | `"Tests that add(2,3) returns 5 for a trivial wrapper"` |
| `"Verifies race condition in concurrent balance update"` | `"Tests that config file loads correctly"` (if framework handles this) |
| `"Ensures discount calculation rounds correctly at boundary"` | `"Tests that logger logs a message"` |

**Prune phase (`--prune` or part of `--auto`):**

When analyzing existing tests, flag those that provide no concrete value:

1. Search for tests asserting only: constructor/getter/setter behavior, trivial pass-through, framework-guaranteed behavior, or 1:1 reimplementation of source code.
2. Present flagged tests with reason:

   ```
   | # | Test         | File:Line       | Reason   | Action |
   |---|--------------|-----------------|----------|--------|
   | {n}| {test-name} | {file}:{line}   | {reason} | Delete |
   ```

3. Ask: **Delete all** / **Review each** / **Keep all**.
4. `--auto`: delete silently, report count in summary.

**Replacement rule:** after deleting a low-value test, check if file/module now has meaningful untested logic. Yes → generate a valuable replacement test targeting a real risk.

### Other Gates

- Generated tests must pass before declaring done — never commit failing tests.
- Keep assertions at full strength — fix the test logic or report the app bug instead of weakening checks.
- Test names describe behavior, not implementation.
- No test depends on execution order — each independently runnable.
- Mocks minimal — only mock external dependencies (network, filesystem, time), not internal modules.
- Generated test matches project's existing style — no style drift.
- **Test Pyramid ([references/principles.md §7](references/principles.md)):** unit-heavy, integration-medium, E2E-light. Detect inverted pyramid (E2E > integration > unit) → flag HIGH before generating more E2E.
- **Boundary conditions ([references/principles.md §7](references/principles.md)):** every generated test suite covers empty, null, max-size, concurrent, locale, timezone, Unicode, leap-day where applicable.
- **AAA structure ([references/principles.md §7](references/principles.md)):** every generated test body has visible Arrange / Act / Assert separation — comments or whitespace lines, never one-shot expressions.
- **Regression-before-fix ([references/principles.md §7](references/principles.md)):** in `--run` mode, when an app bug is found, generate the regression test FIRST (failing), confirm it fails, then propose the source fix.
- **Coverage as diagnostic ([references/principles.md §7](references/principles.md)):** never write a coverage target into generated test configs; configure coverage as a reporter only. The diagnostic is "what did we miss?", not "did we hit X%?".
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/test.json` updated per file processed, gitignored, deleted on successful Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W12: every test verifies described intent + a case beyond the given suite — never special-case known inputs or assert hard-coded outputs to pass.

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
| `--auto` with failing app tests | Write findings to `ds/audit/findings.md`, fix the test, not the source code |
| `--baseline` and output is nondeterministic (time, random, UUID) | Inject/freeze seams (fixed clock, seeded RNG, mocked UUID) before capturing; if seams are unavailable, assert invariant properties (type, range, non-null) instead of exact values — document the invariant-only assertion with the `// characterization:` tag |
| `--baseline` and source module has no public interface (all private/internal) | Report as Category B finding: "No public surface to baseline — refactoring this module without tests is high-risk"; suggest making key behaviors accessible for testing or adding internal test hooks |
