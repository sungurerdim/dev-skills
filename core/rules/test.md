# Test — does the suite catch the bugs that matter, and do the gates run?

Per-stack runners, property-based and mutation tools: [toolchains.md](../toolchains.md). A bug fix lands behind a test seen red first (kernel §3).

### TST-01 [HIGH] Test pyramid missing or inverted
- **Detect:** no tracked test files; end-to-end tests outnumber integration and unit tests; core logic reachable only through end-to-end tests; public services or use cases with no unit test.
- **Mech:** S `git ls-files | grep -qiE '(^|/)(tests?|spec|__tests__)/|[._-](test|spec)\.|_test\.' || echo 'no test files tracked'`
- **Fix:** unit tests for each public service or use case; integration tests at real boundaries; a few end-to-end tests for the critical journeys.
- **Impact:** an inverted suite is slow and flaky, so feedback arrives too late to be cheap.
- **Source:** Vocke, "The Practical Test Pyramid" (https://martinfowler.com/articles/practical-test-pyramid.html); Cohn, *Succeeding with Agile*.

### TST-02 [HIGH] Critical path untested, or tested without real assertions
- **Detect:** critical code (auth, payments, data mutations, core rules) with no branch or error-path test; a route, screen or command no smoke test reaches; boundary cases (empty, null, maximum size, concurrent, time zone, Unicode) never exercised; tests that assert nothing, only getters or constructors, or a snapshot over ~100 lines; an assertion listing today's members of a growing set instead of the rule that decides membership; a coverage percentage used as a gate target.
- **Mech:** T `git grep -nE 'fail_under|cov-fail-under|coverageThreshold|minimum_coverage|jacocoTestCoverageVerification' -- ':!*.md'` · `git ls-files '*.snap' | xargs wc -l 2>/dev/null | awk '$1 > 100 && $2 != "total"'`
- **Fix:** add branch and error-path tests on critical code first; replace padding tests with one that names the bug it catches; read coverage as a risk map, not a score; on touched critical code run the stack's mutation tool and kill each surviving mutant with an assertion.
- **Impact:** the costliest paths fail silently in production while a high coverage number says they are tested.
- **Source:** Fowler, TestCoverage (https://martinfowler.com/bliki/TestCoverage.html); mutation testing (Stryker, PIT).

### TST-03 [HIGH] Tests mock internals instead of faking the boundary
- **Detect:** mocks of the unit's own modules; assertions on call order or arguments of internals; patches of deep internal paths that break when a file moves; mocks whose interface no longer matches the real one.
- **Mech:** T `git grep -nIE "patch\(['\"][a-z_]+(\.[a-z_]+){3,}|(jest|vi)\.mock\(['\"]\.\.?/" -- ':!*.md'`
- **Fix:** in-memory fakes for owned boundaries (repository, clock, queue); mocks only for external I/O or when the interaction is the behavior; patch at the seam the code imports from.
- **Impact:** the suite fails on every refactor while behavior is unchanged, and passes when the real interface has moved on.
- **Source:** Fowler, "Mocks Aren't Stubs"; Google Testing Blog, "Testing on the Toilet: Don't Overuse Mocks".

### TST-04 [HIGH] Integration test that mocks what it integrates
- **Detect:** tests named or placed as integration that mock the database, queue or HTTP server they claim to cover; no test database setup at all while queries and migrations exist.
- **Mech:** M
- **Fix:** run the real dependency in a container (Testcontainers) or its embedded engine; seed and clean per test; test config separate from production.
- **Impact:** the test certifies nothing about the real query, migration or driver behavior it claims to cover.
- **Source:** Testcontainers (https://testcontainers.com/); Vocke, "The Practical Test Pyramid".

### TST-05 [CRITICAL] Weakened, skipped or focused tests
- **Detect:** a skip or expected-failure marker on a failing test without a linked issue; a committed focus (`.only`) that silently drops every other test; assertions changed to match a bug; the unit under test replaced by a mock.
- **Mech:** T `git grep -nIE '\.(skip|only)\(|\bx(it|describe)\(|@(Ignore|Disabled)\b|t\.Skip\(|pytest\.mark\.(skip|xfail)|#\[ignore\]' -- ':!*.md'`
- **Fix:** fix the code or the test so it checks the correct behavior; a temporary skip names its issue on the same line; every bug fix adds its regression test.
- **Impact:** a red test turned green without a fix lets the next regression on that path ship unnoticed.
- **Source:** Beck, *Test-Driven Development: By Example*.

### TST-08 [MEDIUM] Pixel-exact visual tests not pinned to one platform
applies_when: ui≠none
- **Detect:** screenshot or golden tests that fail on developer machines because rendering differs from CI; baselines updated from whichever machine ran last; goldens in a local gate with no platform pin.
- **Mech:** M
- **Fix:** name the one platform that owns the baselines; run and update goldens only there (CI or a container); exclude them from other local runs by tag with the reason in code.
- **Impact:** developers conclude the tests are broken and regenerate goldens on their own machines, replacing the reference silently.
- **Source:** Playwright, Visual comparisons — screenshots differ between browsers and platforms (https://playwright.dev/docs/test-snapshots).

### TST-11 [HIGH] Check never seen failing
- **Detect:** a lint, audit or gate with no fixture or test that turns it red; a gate said to enforce a rule while the code visibly breaks that rule and the gate stays green; removing the rule under test changes no result.
- **Mech:** M
- **Fix:** pair every gate with a fixture that violates exactly what it claims to catch, asserted to fail in the same suite; a gate that cannot be made to fail is documented as advisory until it can.
- **Impact:** a non-enforcing gate turns an unchecked rule into one everybody believes is checked, so nobody looks again.
- **Source:** kernel §3 (a check is proven by injecting its defect); DeMillo, Lipton & Sayward, "Hints on Test Data Selection" (1978, mutation testing).

### TST-12 [MEDIUM] Placeholder committed as data
- **Detect:** committed structured files (registries, manifests, config, fixtures read as data) holding unresolved tokens such as `TBD`, `FIXME`, `<fill>`, `assign at apply`, `next free ID` in a field consumers read as a value.
- **Mech:** S `git grep -nIE '\b(TBD|FIXME)\b|<fill[^>]*>|assign at apply|next free ID' -- '*.json' '*.yaml' '*.yml' '*.toml' '*.csv'`
- **Fix:** resolve it now; when it must wait, model it as an explicit null or pending state the consumer handles, and fail the gate on the token.
- **Impact:** the placeholder passes every structural check and flows into reports and counts as if it were real.
- **Source:** fail fast (Shore, "Fail Fast", *IEEE Software*, 2004).

### TST-13 [HIGH] Check scans less than it claims
- **Detect:** a check whose file set comes from an implicit default (the current directory, a hard-coded list, a glob one level too deep); a gate that exits green over an empty input set; a scan list written when the tree was smaller; a generated artifact users see (exported site, report, widget) that no gate checks while the app's own gate does.
- **Mech:** M
- **Fix:** name the scanned set explicitly, assert it is non-empty, and compare repo-wide rules against `git ls-files` so a new directory joins the scan or fails the gate; a deliberate exclusion is declared beside the scope with its reason.
- **Impact:** a scope-blind gate is green for the same reason an empty one is, and the narrower the scope drifts the greener it gets.
- **Source:** kernel §3 (a gate that stays green is blind); fitness functions (Ford, Parsons, Kua).

### TST-14 [HIGH] Check nothing calls
- **Detect:** a script under `scripts/`, `tools/` or `bin/` that no task runner, hook or pipeline invokes; a test file outside the runner's discovery pattern; a caller that discards the check's exit code; docs saying "we lint with X" where nothing runs X.
- **Mech:** T `git ls-files 'scripts/*' 'tools/*' 'bin/*' | while read -r f; do git grep -qF "${f##*/}" -- ":!$f" || echo "$f"; done`
- **Fix:** wire it into the single entry point that gates "done", or delete it; an intentional exclusion is named at that entry point with the condition under which it runs; prove the path by breaking a fixture and running the entry point.
- **Impact:** the rule looks enforced, so nobody looks again, and the first real enforcement happens in production.
- **Source:** Fowler, Continuous Integration (one command runs every check).

### TST-15 [HIGH] Test depends on time, randomness, network or order
- **Detect:** in test files: real clock reads, sleeps, unseeded random values, real network calls; process-global caches or singletons not reset between tests; tests that pass alone and fail in the suite (or the reverse); reruns used to get green.
- **Mech:** T `git grep -nIE 'sleep\(|Date\.now\(|new Date\(\)|datetime\.now\(|time\.Now\(|Math\.random\(|random\.random\(|requests\.(get|post)\(' -- '*test*' '*spec*'`
- **Fix:** inject the clock and the seed; fake the network; reset every process-global cache in one before-each fixture; run the suite shuffled (pytest-randomly, `go test -shuffle=on`, Jest `--randomize`, Vitest `sequence.shuffle`); quarantine a flaky test with an issue, never a silent retry.
- **Impact:** a suite that fails at random is rerun until green, and then its real failures are rerun away too.
- **Source:** Luo et al., "An Empirical Analysis of Flaky Tests" (FSE 2014); Google Testing Blog, "Flaky Tests at Google and How We Mitigate Them" (2016).

### TST-30 [MEDIUM] Public contract can drift unseen
- **Detect:** an OpenAPI, GraphQL, protobuf or JSON Schema artifact with no test that validates the implementation against it; a library whose release has no public-API diff against the last published version.
- **Mech:** T `git ls-files '*openapi*' '*swagger*' '*.proto' '*.graphql' '*.graphqls' '*.schema.json'`
- **Fix:** a contract test that fails on drift (schemathesis, Pact, the stack's schema validator); for libraries an API diff in the release check (cargo-semver-checks, japicmp, api-extractor, apidiff) and a MAJOR bump on a break.
- **Impact:** producer and consumer desync silently, and the first signal is a consumer failing in production.
- **Source:** OpenAPI Specification; Pact (https://docs.pact.io/); Semantic Versioning 2.0.0 (https://semver.org/).
