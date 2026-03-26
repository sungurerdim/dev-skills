# /ds-test

AI-generated tests often mock everything, assert nothing useful, and break on the first refactor. This skill generates tests that follow your project's patterns and verifies they actually pass.

**Universal Test Skill** — Generate, update, run, and fix tests for any stack.

## Triggers

- User runs `/ds-test`
- User asks to write tests, add tests, generate tests, or improve test coverage
- User asks to run tests and fix failures
- User asks to add E2E tests, integration tests, or unit tests
- User asks "why is this test failing" or "update tests after refactor"
- After a refactor or feature change, suggest updating affected tests

## Contract

- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- Every finding receives a disposition in the summary — zero silent drops (FRC)
- Generates tests that follow the project's existing test patterns and conventions
- Preserves existing passing tests — only overwrites with explicit confirmation
- Always runs generated tests to verify they pass before declaring done
- Uses the project's existing test framework — never introduces a new framework unless none exists
- Test files go in the project's established test directory (auto-detected)
- Does NOT fix application code to make tests pass — fixes the TEST if the test is wrong, or reports the app bug if the app is wrong

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Interactive mode selection |
| `--generate` | Generate tests for uncovered code |
| `--update` | Update existing tests to match current source code |
| `--run` | Run tests, analyze failures, fix what's possible |
| `--e2e` | Generate or run E2E/integration tests |
| `--coverage` | Analyze coverage gaps and fill them |
| `--setup` | Set up test framework and infrastructure |
| `--prune` | Find and delete low-value tests, replace with meaningful ones |
| `--scope=<path>` | Limit to specific file, directory, or module |
| `--auto` | No questions, generate + run + fix cycle |

## Scopes

| Scope | What It Covers |
|-------|---------------|
| `unit` | Single function/method tests, isolated with mocks |
| `integration` | Multi-module tests, real dependencies where possible |
| `e2e` | End-to-end tests via browser/UI automation or API calls |
| `snapshot` | Snapshot/golden tests for UI components or serialized output |
| `fixture` | Test data setup, factories, builders, seed files |

Default: `unit` + `integration`. E2E and snapshot require explicit `--e2e` or `--scope`.

## Execution Flow

Setup → [Generate / Update / Run+Fix] → Verify → Summary

### Phase 1: Setup

1. **Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, read findings with `testing` scope. Use them to prioritize which modules need tests (skip own coverage analysis for covered scopes). If no findings file or stale, run own full analysis.
2. **Upstream check:** Search for `## Blueprint Profile` in known instruction files. If found:
   - **Ideal Metrics.Coverage** → set coverage threshold target
   - **Project Map.Toolchain** → skip test framework detection, use stated framework
   - **Current Scores.Testing** → if low, prioritize coverage gaps over new features
   - **Type + Stack** → skip own project detection
3. **Detect test framework** from project config and dependencies. See `references/frameworks.md` for the detection table.
4. **Detect test conventions:**
   - Test directory: `test/`, `tests/`, `__tests__/`, `spec/`, `src/**/*.test.*`
   - Naming pattern: `*_test.go`, `*.test.ts`, `*.spec.rb`, `test_*.py`
   - Helper/fixture locations: `fixtures/`, `factories/`, `support/`, `conftest.py`
   - Mock patterns: what mocking library is used, how are mocks structured
5. **Read 2-3 existing test files** to learn the project's test style:
   - Import conventions, assertion style (expect vs assert), describe/it vs test()
   - How mocks and fixtures are used
   - Setup/teardown patterns (beforeEach, setUp, etc.)
6. If no test framework found and `--setup` flag: proceed to Framework Setup (see below).
7. If no test framework found and no `--setup` flag: suggest running with `--setup` first.

**Gate:** Test framework detected or `--setup` mode.

### Phase 2a: Generate [--generate or --coverage]

For each uncovered source file (or scoped path):

1. Read the source file — understand its public interface (exported functions, class methods, API endpoints)
2. Identify test-worthy targets:
   - Public functions/methods with logic (not simple getters)
   - Edge cases: null inputs, empty arrays, boundary values, error paths
   - Branches: every if/else, switch case, try/catch
3. Generate test file following the project's existing conventions:
   - Match naming pattern, import style, assertion library
   - Group by function/method using describe/context blocks
   - Include: happy path, edge cases, error cases
   - For each test: clear name describing the behavior, not the implementation
4. **For integration tests:** identify cross-module interactions, test the integration points with minimal mocking
5. **For E2E tests (`--e2e`):** identify user flows, generate browser/API test scenarios. See `references/frameworks.md` for E2E framework detection.

**Test naming rule:** Test names describe WHAT the behavior is, not HOW it's implemented.

| Good | Bad |
|------|-----|
| "returns empty array when no items match filter" | "test filterItems function" |
| "rejects login with expired token" | "test authentication" |
| "creates order with correct total when discount applied" | "test createOrder" |

**Client-side test scenarios (when platform = mobile, web SPA, or desktop):**

When generating tests for client-side projects, include these additional scenario categories:

**Responsive layout tests:**
- Test at viewport profiles: 320dp, 375dp, 412dp, 744dp, 1024dp (minimum)
- Verify no layout overflow errors at each profile
- Test both portrait and landscape orientations

**Font scaling tests:**
- Test at 0.8×, 1.0×, 1.3× system font scale
- Verify text remains readable and layouts stay intact

**Theme tests:**
- All screens render correctly in both light and dark mode
- No hardcoded colors bypassing theme system

**Accessibility tests:**
- Screen reader (TalkBack / VoiceOver / Narrator / NVDA) traversal of all interactive elements
- All interactive elements have accessibility labels
- Error states announced to screen readers

**Test ratio targets (by project type):**

| Type | Unit | Component/Integration | E2E |
|------|------|-----------------------|-----|
| Mobile | 70%+ | 20%+ | 10%+ |
| Web SPA | 60%+ | 25%+ | 15%+ |
| API | 60%+ | 30%+ | 10%+ |
| Library | 80%+ | 15%+ | 5%+ |

**Gate:** Test files generated covering happy path, edge cases, and error cases for each target.

### Phase 2b: Update [--update]

When source code changed and tests need updating:

1. Identify changed source files (from git diff or user-specified scope)
2. For each changed file, find its corresponding test file
3. Compare: what changed in the source? New params, renamed methods, changed return types, removed functions?
4. Update test file to match:
   - New params → update test calls, add tests for new param edge cases
   - Renamed method → update test references
   - Changed return type → update assertions
   - Removed function → remove tests (with confirmation) or mark as skipped with TODO
   - New function → generate new tests (as in Phase 2a)
5. Run updated tests to verify they pass

**Gate:** Updated tests pass and no previously passing tests regressed.

### Phase 2c: Run + Fix [--run]

1. Execute the test suite (or scoped subset): detect and run the appropriate test command from `references/frameworks.md`
2. Parse test output: extract failures, errors, skipped tests
3. For each failure, classify:

| Classification | Action |
|---------------|--------|
| **Test is wrong** (assertion outdated, mock stale, fixture missing) | Fix the test |
| **App is wrong** (source code bug causing test failure) | Report as app bug — fix the test, not the source code |
| **Environment issue** (missing dep, config, database not running) | Report with setup instructions |
| **Flaky test** (passes sometimes, fails others — timing, ordering) | Flag as flaky, suggest fix approach |

4. Fix test-side issues automatically. For app bugs, write a finding to `.ds-findings.md` with scope `testing`.
5. Re-run to verify fixes. Max 3 fix-run iterations.

**Critical rule:** If a test was passing before and now fails after source change, the SOURCE is likely wrong (regression), not the test. Keep assertions at full strength — fix the test logic or report the app bug.

**Gate:** Test-side fixes verified passing or app bugs written to .ds-findings.md.

### Phase 2d: Framework Setup [--setup]

If no test framework exists:

1. Detect stack from manifests
2. Recommend the canonical test framework for the stack (see `references/frameworks.md`)
3. Ask user to confirm framework choice
4. Install framework and create config:
   - Add test dependency to manifest (package.json, pyproject.toml, etc.)
   - Create test config file (jest.config.ts, pytest.ini, etc.)
   - Create test directory with example test
   - Add test script to manifest (e.g., `"test": "vitest"` in package.json)
   - Add test step to CI config if it exists
5. Run example test to verify setup works

**Gate:** Example test passes with the installed framework.

### Phase 3: Verify

After any generate/update/fix operation:

1. Run the full test suite (or scoped subset)
2. All generated/modified tests must pass
3. No previously passing test should now fail (regression check)
4. Report coverage delta if coverage tool is configured

**Gate:** All generated tests pass. Zero regressions.

### Phase 4: Summary

```
ds-test: {OK|WARN|FAIL} | Generated: N | Updated: N | Fixed: N | Skipped: N | Failing: N

| Action    | Count | Details              |
|-----------|-------|----------------------|
| Generated |  {n}  | {n} unit, {n} integration|
| Updated   |  {n}  | matched source changes|
| Fixed     |  {n}  | {n} assertion, {n} mock|
| Failing   |  {n}  | app bugs (see .ds-findings.md) |
```

**Gate:** Summary table rendered with generated/updated/fixed/failing counts. Every finding/action has a disposition. Accounting verified.

## Quality Gates

### Value Rule (most important)

Every test must justify its existence by addressing a **concrete, specific risk**. Before writing any test, answer: "What bug would this catch?" If the answer is vague or "none really", skip the test.

| Write this test | Skip — this test validates... |
|----------------|----------------------|
| "Catches division by zero when quantity is 0" | "Tests that constructor sets properties" |
| "Verifies auth rejects expired JWT tokens" | "Tests that getter returns the field value" |
| "Catches SQL injection via unsanitized user input" | "Tests that `add(2, 3)` returns `5` for a trivial wrapper" |
| "Verifies race condition in concurrent balance update" | "Tests that config file loads correctly" (if framework handles this) |
| "Ensures discount calculation rounds correctly at boundary" | "Tests that logger logs a message" |

**Prune phase (`--prune` or part of `--auto`):**

When analyzing existing tests, flag tests that provide no concrete value:

1. Search for tests that only assert: constructor/getter/setter behavior, trivial pass-through, framework-guaranteed behavior, or 1:1 reimplementation of the source code
2. Present flagged tests to the user with reason:
   ```
   | # | Test | File:Line | Reason | Action |
   |---|------|-----------|--------|--------|
   | {n} | {test name} | {file}:{line} | {reason} | Delete |
   ```
3. Ask user: **Delete all** / **Review each** / **Keep all**
4. In `--auto` mode: delete silently, report count in summary

**Replacement rule:** After deleting a low-value test, check if the file/module now has meaningful untested logic. If yes, generate a valuable replacement test targeting a real risk.

### Other Gates

- Generated tests must pass before declaring done — never commit failing tests
- Keep assertions at full strength — fix the test logic or report the app bug instead of weakening checks
- Test names describe behavior, not implementation
- No test should depend on execution order — each test must be independently runnable
- Mocks must be minimal — only mock external dependencies (network, filesystem, time), not internal modules
- Generated test matches project's existing style — no style drift
- Every finding gets a disposition in the summary — zero silent drops (FRC)

## Error Recovery

| Situation | Action |
|-----------|--------|
| Test framework not detected | Ask user which framework to use |
| Generated test fails on first run | Read error, fix test logic (fix the test, not the source) |
| Source file has no testable public interface | Skip with note: "No public API to test" |
| Coverage tool unavailable | Skip coverage report, generate tests based on source analysis |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No test framework installed | Suggest `--setup`, or skip with warning |
| No existing tests to learn from | Use canonical conventions for the detected stack |
| Source file has no testable public API | Skip with note "no public interface to test" |
| Test framework not recognized | Ask user for test command, proceed with manual config |
| Monorepo with multiple test frameworks | Detect per-package, run each package's framework |
| E2E requires running server | Check for dev server script, start it, run tests, stop it |
| Coverage tool not configured | Skip coverage analysis, suggest setup |
| `--auto` mode with failing app tests | Write findings to `.ds-findings.md`, fix the test, not the source code |
