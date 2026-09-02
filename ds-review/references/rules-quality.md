# Rules: Architecture & Testing

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action. Severity, confidence, score, and skip patterns: one home — [`../../core/severity-score-categories.md`](../../core/severity-score-categories.md).

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Architecture & Code Quality** | ARC-01–15 (12 HIGH, 3 MEDIUM) | ~12 |
| **Testing** | TST-01–14 (1 CRITICAL, 8 HIGH, 5 MEDIUM) | ~145 |

---

## Architecture & Code Quality

### ARC-01 [HIGH] Layered Architecture
Separation between handlers/controllers (entry), services/use cases (logic), and repositories/adapters (data). Dependencies inward only.
- **Detect:**
  - Business logic (if/else decisions, calculations, validation) in route handlers/controllers/API endpoints
  - Database queries in handler/controller layer
  - Circular dependencies between layers
  - Search: `prisma.`, `db.`, `mongoose.`, `sqlalchemy`, `SELECT`, `INSERT` in handler/controller files
- **Fix:** Extract logic to service/use-case layer. Create repository interfaces for data access. Handlers only parse request, call service, format response
- **Platform:**
  - Node/Express: routes -> services -> repositories
  - NestJS: controllers -> services -> repositories (built-in)
  - FastAPI: routers -> services -> repositories
  - Django: views -> services -> models/managers
  - Go: handlers -> services -> repositories
- **Impact:** Business logic in handlers can't be reused or unit-tested without spinning up the transport layer, and every route reimplements its own version of the same rule.
- **Source:** Clean Architecture, Hexagonal Architecture

### ARC-02 [HIGH] Unidirectional Data Flow
State flows in one direction. Single source of truth per data type.
- **Detect:** State modified from multiple locations. Shared mutable state without clear ownership. Two-way binding causing update cycles
- **Fix:** Define clear state ownership. UI sends events, state holder processes and emits new state
- **Platform:**
  - React: Zustand/Redux for global, useState for local. Never mutate state directly
  - Vue: Pinia for global, reactive() for local
  - Backend: Request -> Service -> Response (no shared mutable state between requests)
- **Impact:** Bidirectional/shared mutable state multiplies update-cycle bugs and makes state transitions untraceable
- **Source:** Flux Architecture, React docs

### ARC-03 [HIGH] Immutable Data Models
Data models use immutable patterns. No in-place mutation.
- **Detect:** Mutable objects passed between layers. In-place mutation of shared data. Missing equals/hashCode
- **Fix:**
  - TypeScript: `readonly` + spread operator or Immer
  - Python: `@dataclass(frozen=True)` or Pydantic `model_config = ConfigDict(frozen=True)`
  - Go: return new structs instead of mutating
  - Rust: ownership model (default immutable)
- **Impact:** In-place mutation of shared data creates action-at-a-distance bugs — a change made through one reference silently corrupts state another layer still holds.
- **Source:** Eric Evans — Domain-Driven Design (Value Objects), Effective Java (Item 17: Minimize Mutability)

### ARC-04 [HIGH] Dependency Injection
Constructor injection preferred. DI container for lifecycle management.
- **Detect:** Direct instantiation of dependencies in business logic (`new Service()`, hardcoded imports). Global singletons without injection. Tight coupling to implementations
- **Fix:**
  - NestJS: built-in DI (providers, modules)
  - Express: manual constructor injection or tsyringe/inversify
  - FastAPI: `Depends()` for dependency injection
  - Django: explicit service instantiation in views/factories
  - Go: constructor injection (idiomatic)
  - Spring: `@Autowired` / constructor injection
- **Impact:** Direct instantiation of dependencies inside business logic makes the code untestable without the real service and locks the module to one implementation.
- **Source:** SOLID Dependency Inversion Principle

### ARC-05 [HIGH] No Business Logic in Entry Points
Zero business rules in route handlers, controllers, or CLI commands. Entry points = parse input + call service + format output.
- **Detect:** if/else business decisions in route handlers. Data transformation in controllers. Validation logic mixed with handling
- **Fix:** Move to service layer. Entry points: parse request, validate input shape, call service, format response
- **Impact:** Business rules embedded in entry points can't be reused across transports (HTTP, CLI, queue) and are exercised only by end-to-end tests.
- **Source:** Clean Architecture, SOLID SRP

### ARC-06 [HIGH] Consistent Error Handling Strategy
Single error handling pattern across codebase. Errors categorized and handled per type.
- **Detect:**
  - Mixed error handling: some try-catch, some .catch(), some unhandled
  - Generic catch-all without specific handling
  - Error types not categorized (validation vs business vs infrastructure)
  - Search: empty catch blocks, `catch (e) {}`, `except: pass`, `_ = err`; business logic catching the language's broadest exception type (`catch (Object)`, bare `except:`); error types outside a central sealed hierarchy
- **Fix:** Define error hierarchy (ValidationError, NotFoundError, AuthError, InternalError). Global error handler middleware. Map errors to HTTP status codes. Log infrastructure errors, return safe messages to clients. Structure errors as one central, sealed (closed-variant) exception hierarchy; business logic catches specific members, never the universal supertype; every caught error logs at warning or above — the combination makes 'silently swallowed' unrepresentable. (XR-078)
- **Impact:** Mixed error-handling styles mean some failures are logged and some vanish silently, and callers can't rely on one error shape.
- **Source:** Microsoft Error Handling Guidelines, Go Error Handling (Effective Go), Node.js Error Handling Best Practices

### ARC-07 [HIGH] Feature Modularization
Feature modules with clear boundaries. No circular dependencies.
- **Detect:** Single flat directory with everything. Feature coupling. Imports crossing module boundaries without clear API
- **Fix:** Group by feature (not by type). Each feature exposes public API. Shared module for common utilities. Clear dependency direction
- **Impact:** A flat, uncoupled-by-feature layout means one feature change requires scanning the whole tree to find every affected file.
- **Source:** Modular Architecture Patterns

### ARC-08 [HIGH] Typed Error Results
Typed results for recoverable errors. Exceptions for exceptional cases only.
- **Detect:** try-catch for expected errors (validation, not-found). Null as error signal. Untyped error propagation
- **Fix:**
  - TypeScript: discriminated unions `{ success: true, data } | { success: false, error }`
  - Python: Result pattern or explicit exception types
  - Go: `(value, error)` return pattern (idiomatic)
  - Rust: `Result<T, E>` (built-in)
- **Impact:** Using exceptions for expected, recoverable outcomes forces callers to guess which errors are exceptional via try/catch, and untyped propagation hides what a function can actually fail with.
- **Source:** Rust Error Handling (The Rust Programming Language), TypeScript Discriminated Unions, Go (value, error) Pattern

### ARC-09 [HIGH] Defensive External Data Parsing
Validate all external data at boundaries. No trust for API responses, user input, or file contents.
- **Detect:** Force-casting external data. No schema validation on API responses. Unvalidated file uploads
- **Fix:** Validate with schemas at boundaries: Zod (TS), Pydantic (Python), serde (Rust). Handle malformed data gracefully. Never trust external shape
- **Impact:** Trusting external shape without validation lets malformed API responses or uploads crash the process or corrupt downstream state.
- **Source:** Postel's Law, Secure by Design

### ARC-10 [MEDIUM] Complexity Limits
Cyclomatic complexity <= 15. Function <= 50 lines. Nesting <= 3. Parameters <= 4.
- **Detect:** Functions exceeding limits. Deep nesting. Long parameter lists
- **Fix:** Extract functions. Early returns. Parameter objects. Composed functions
- **Impact:** Functions past these limits take measurably longer to review correctly and hide more defects per line.
- **Source:** SonarQube, ESLint complexity rules

### ARC-11 [HIGH] Duplication Drift
Reused logic lives in one place. AI-assisted churn drove copy/pasted lines from 8.3% to 12.3% while "moved" (refactored) lines fell from 24.1% to 9.5% (2020→2024) — regenerating beats reusing by default.
- **Detect:** Near-identical functions or blocks differing only in literals. A new helper that duplicates an existing one. Code rewritten within two weeks of being added (high churn). Search: clone detectors `jscpd`, `pmd cpd`, or LSP "find similar".
- **Fix:** Reuse or extend the existing implementation instead of regenerating. Consolidate clones to a single source of truth. Three similar lines are fine; a fourth copy means extract.
- **Impact:** A duplicated block fixed in one copy and missed in the others reintroduces the same bug, and the miss rate rises with every additional copy.
- **Source:** GitClear — AI Copilot Code Quality 2025 (https://www.gitclear.com/ai_assistant_code_quality_2025_research)

### ARC-12 [HIGH] God-Module Decomposition via Strangler-Fig Phases
A "god module" (a file re-exporting dozens of symbols that most of the codebase imports through, commonly anchoring a circular-dependency chain) is decomposed in ordered, independently-shippable phases — never a single big-bang rewrite.
- **Detect:** A module with dozens of re-exported symbols that a large fraction of the codebase imports through; a circular-dependency chain anchored on that module; a "god object" (single module/class merging many unrelated domains) proposed for a one-pass rewrite, or for replacement by N smaller per-layer god modules (a non-fix that doesn't address the root cause).
- **Fix:** Phase 1 — migrate simple/leaf dependents (constants, pure utilities) to their canonical source instead of through the god module. Phase 2 — break any *real* remaining circular dependency via event-bus/inversion-of-control (one module emits an event instead of calling the other directly). Phase 3 — decompose any remaining god-object into domain-namespaced sub-modules, migrating call sites last (touches the most call sites, so it goes last). Preserve backward-compatible re-exports throughout every phase; remove them only once every consumer has migrated.
- **Impact:** A single big-bang rewrite of a heavily-imported god module is high-risk and hard to review incrementally; the phased strangler-fig approach ships independently-verifiable steps and never leaves the codebase in a half-migrated, harder-to-reason-about state.
- **Source:** Martin Fowler — StranglerFigApplication (https://martinfowler.com/bliki/StranglerFigApplication.html); event-driven inversion-of-control pattern for breaking circular dependencies

### ARC-13 [MEDIUM] Native Platform Capability Documented Before Building an Integration Surface
Before building a new integration/exposure surface (webhook, feed, sharing infrastructure), the underlying platform is checked for a native equivalent; when one exists, it is documented and used instead of custom code.
- **Detect:** Custom webhook/feed/sharing code duplicating a capability the platform already exposes natively; no recorded check of the platform's native options predating the build decision.
- **Fix:** Record the native-capability check as the first step of any new integration surface: what the platform offers, whether it satisfies the need, and — when it does — a doc pointing users at the native path instead of shipping custom code (YAGNI: no new surface without proven need).
- **Impact:** Every custom surface duplicating a native capability is permanent maintenance debt purchased for zero user value — the platform's version is monitored, patched, and documented by someone else.
- **Source:** XR-118 — cross-project experience registry (2026).

### ARC-14 [MEDIUM] One Supported Model Per Concern; Parallel Modes Rejected and the Rejection Recorded
When choosing a storage/integration model, one supported model serves everyone — even where a second mode would be technically superior for a user subset; the rejected alternative is recorded with rationale in the decision log.
- **Detect:** Two parallel modes serving the same concern (e.g. personal-share storage AND shared-drive storage) each with partial edge-case handling; mode-conditional branches multiplying through sync/auth/quota code; no record of why the losing mode was rejected.
- **Fix:** Pick one supported model per concern and hold it everywhere; document the rejected alternative and its rationale in the decision log (pairs with the decision-lock rule) so the debate doesn't reopen without new evidence. Diversity of modes multiplies the maintenance surface and breeds unnoticed edge-case divergence.
- **Impact:** Every parallel mode doubles the test matrix and halves the attention each path gets — the second mode's edge cases are where data-loss bugs live.
- **Source:** XR-119 — cross-project experience registry (2026).

### ARC-15 [HIGH] Functional Parity Baseline: Routes Render, Settings Round-Trip, Shared Assets Single-Sourced, Primary Actions Scoped
A functional floor holds across the app: every route passes a render smoke test, every settings surface round-trips (save→reload→verify), every shared asset reads from one SSOT, and every primary action carries an explicit scope decision.
- **Detect:** Routes that crash or blank on direct load; settings that save but read back stale/default; the same asset/constant loaded from multiple sources; primary actions whose effective scope (this item? this view? everything?) is undefined or accidental.
- **Fix:** Enforce the four-part baseline mechanically where possible: route render-smoke tests in the suite; settings round-trip tests per surface; shared-asset reads traced to one SSOT; each primary action's scope stated and reviewed. Gaps are findings even when no user has complained yet.
- **Impact:** These four floors are where "works in the demo" diverges from "works" — each gap is a whole class of user-facing breakage with no error signal.
- **Source:** XR-181 — cross-project experience registry (2026).

---

## Testing

### TST-01 [HIGH] Test Pyramid 70/20/10
70% unit (services/logic), 20% integration (layer interactions, DB), 10% E2E (critical flows).
- **Detect:** Inverted pyramid. No integration tests. Only E2E tests. Untested services
- **Fix:** Unit test every public service/use-case method. Integration with test DB. E2E for critical user journeys
- **Platform:**
  - Node: Jest/Vitest (unit), Supertest (integration), Playwright/Cypress (E2E)
  - Python: pytest (unit+integration), Playwright (E2E)
  - Go: testing package (unit), testcontainers (integration)
- **Impact:** Inverted pyramids make suites slow and flaky — feedback arrives too late to be cheap
- **Source:** Martin Fowler — Test Pyramid, Google Testing Blog — Testing on the Toilet

### TST-02 [HIGH] Coverage as Diagnostic, Critical Paths Covered
Coverage is a diagnostic signal, never a target — low coverage on a critical path signals risk; a blanket percentage gate invites coverage-padding tests.
- **Detect:** Critical-path modules (auth, payments, data mutations, core business logic) with low or zero branch coverage. Tests without assertions. Happy-path-only tests. Coverage-padding: tests that execute code but assert nothing meaningful
- **Fix:** Add branch-covering tests for critical paths and error paths first. Treat a coverage report as a risk map, not a scoreboard — no blanket percentage gate
- **Note:** 80% meaningful beats 95% superficial; chasing the number produces the superficial kind
- **Impact:** An untested critical path (auth, payments, data mutation) fails silently in production exactly where the cost of a bug is highest.
- **Source:** Martin Fowler — Test Coverage (coverage as diagnostic), Google Testing Blog — Code Coverage Best Practices

### TST-03 [HIGH] Fakes Over Mocks
Deterministic fake implementations. Mocks only for interaction verification.
- **Detect:** Mocks verifying implementation details. Tests breaking on refactor. External deps in unit tests
- **Fix:** In-memory fake repositories/services. Fakes simulate real behavior. Mocks only for verifying calls were made
- **Impact:** Mock-heavy suites break on refactor even when behavior is unchanged; fakes keep tests fast and behavior-anchored
- **Source:** Google Testing Blog

### TST-04 [HIGH] Integration Tests with Real Dependencies
Test with real databases and services using containers.
- **Detect:** Integration tests mocking the database. No test database setup. API tests without real server
- **Fix:**
  - Use testcontainers for DB (PostgreSQL, Redis, MongoDB)
  - Supertest/httptest for API integration
  - Seed test data, clean up after each test
  - Separate test config from production
- **Impact:** Mocking the database in an “integration” test certifies nothing about the real query, migration, or driver behavior it claims to cover.
- **Source:** Testcontainers, Integration Testing Patterns

### TST-05 [CRITICAL] No Weakened Assertions
Never skip, mock away, or relax assertions to make tests pass.
- **Detect:** `skip` on failing tests. Assertions changed to match bugs. Mocks replacing the tested unit
- **Fix:** Fix code or fix test to validate correct behavior. Every bug fix = regression test
- **Impact:** A weakened or skipped assertion turns a red test green without fixing the underlying defect, and the next regression on that path ships unnoticed.
- **Source:** Kent Beck — Test-Driven Development: By Example, Google Testing Blog

### TST-06 [HIGH] Static Analysis
Linter + type checker must pass.
- **Detect:** No linter configured. Type errors ignored. Suppressed warnings without justification
- **Fix:**
  - TypeScript: `strict: true` in tsconfig, ESLint with recommended rules
  - Python: mypy strict + ruff/flake8
  - Go: `go vet` + `golangci-lint`
  - Rust: `clippy` (default)
- **Impact:** Without an enforced linter/type-checker, a whole class of defects (unreachable code, type mismatches, unused values) reaches review only if a human happens to spot it.
- **Source:** TypeScript Strict Mode Documentation, mypy Documentation, golangci-lint, Rust Clippy

### TST-07 [MEDIUM] Generated End-User-Facing Output Gets Its Own Quality Gate
When the project generates a separate artifact meant for someone else's end users — a customer-facing static site, an exported report/PDF, an embeddable widget — rather than serving its own routes, that artifact carries its own performance/accessibility/quality gate. A drift-check that only verifies the *template* stayed in sync with its source is not a substitute for verifying the *generated output* itself.
- **Detect:** A project's performance/a11y/Lighthouse CI config targets only the app's own routes; a separately-produced generated artifact (customer site, exported document, embeddable widget) has no equivalent gate. An existing check named like a quality gate (`template:check`, `export:verify`) actually only asserts template-source drift, not output quality — a name that reads as coverage but isn't.
- **Fix:** Add a dedicated gate for the generated artifact using the same baseline thresholds as the main app's gate, run against representative generated output — not just the template source. Rename any drift-only check so its name doesn't imply broader coverage than it has.
- **Impact:** A generated artifact with no dedicated gate can regress in performance or accessibility while the app's own gate stays green, and nobody notices until an end user does.
- **Source:** Extends TST-02 (coverage as diagnostic) to artifact-level coverage — the gate must reach every surface real users see, not only the surfaces the app itself renders

### TST-08 [MEDIUM] Platform-Pinned Golden Tests: Excluded Locally, Run Fully in CI
Pixel-exact golden/visual-regression tests pin one source-of-truth render platform; local gates exclude them by tag with an in-code reason; they run unfiltered only where the platform matches (CI).
- **Detect:** Golden tests failing on developer machines because the render engine differs from CI; developers updating golden files from the wrong platform; goldens in the local pre-push gate with no platform pin.
- **Fix:** Declare the golden source-of-truth platform explicitly; tag-exclude golden tests from local gates with a documented in-code reason; run them unfiltered on the pinned platform only. Golden updates happen only from the pinned platform.
- **Impact:** Without the pin, developers conclude "tests are broken" and regenerate goldens on their own machines — quietly replacing the source of truth with whichever laptop ran last.
- **Source:** XR-092 — cross-project experience registry (2026).

### TST-09 [MEDIUM] Tests Patch at Entry-Point Re-Exports, Not Source Modules
Tests patch dependencies at a stable location re-exported by the application's entry point; new patchable dependencies get a re-export line there.
- **Detect:** Tests patching deep source-module paths (`patch('app.services.internal.x')`) that break on every file move; refactors failing dozens of tests that assert nothing about behavior.
- **Fix:** Re-export patchable dependencies from the entry point (or a designated seam module); tests patch only that stable location; adding a testable dependency means adding one re-export line. Refactors then move code freely without touching tests.
- **Impact:** Deep-path patching welds tests to the file layout — the suite punishes refactoring, which is the opposite of its job.
- **Source:** XR-182 — cross-project experience registry (2026).

### TST-10 [MEDIUM] Process-Global Caches Reset by an Autouse Fixture Before Every Test
Suites touching process-global memoized singletons (settings, connections, compiled-query caches) reset them all via an automatic (autouse) fixture before each test.
- **Detect:** Memoized globals leaking state between tests; tests passing alone but failing in suite (or vice versa); order-dependent flakes traced to a cached singleton.
- **Fix:** Enumerate every process-global cache and clear them in one autouse fixture that runs before each test; new caches join the fixture in the same change that introduces them.
- **Impact:** Cache leakage is the classic order-dependent flake generator — the suite's trustworthiness dies one "re-run it, it's fine" at a time.
- **Source:** XR-183 — cross-project experience registry (2026).

### TST-11 [HIGH] Every Gate Proves Itself Against a Known-Bad Fixture
A check is only enforcing something if a fixture exists that makes it fail.
- **Detect:** A lint/audit/gate with no test that turns it red; a gate documented as enforcing a requirement while the corpus visibly violates that requirement and the gate stays green; a suite where removing the rule under test changes no result.
- **Fix:** Pair every gate with a fixture that violates exactly what it claims to catch, run in the same suite, asserted to fail. A gate that cannot be made to fail enforces nothing — reclassify it doc-only until it can, rather than leaving it as false assurance.
- **Impact:** A silently non-enforcing gate is worse than no gate: it converts an unchecked rule into a rule everyone believes is checked, so nobody looks again.
- **Source:** XR-206 — cross-project experience registry (2026).

### TST-12 [MEDIUM] Unresolved Placeholders Never Survive Into a Committed Artifact
Intent tokens left for a later step never reach a committed data field.
- **Detect:** Committed structured artifacts (registries, pointer maps, manifests, config) carrying unresolved tokens — `TBD`, `TODO`, `assign at apply`, `next free ID`, `<fill>`, `XXX` — in fields consumers read as data rather than prose.
- **Fix:** Scan committed artifacts for the placeholder vocabulary and fail the gate on a hit inside a data field. Resolve at apply time; when resolution genuinely must wait, model it as an explicit null/pending state the consumer handles, never as free text that reads like a value.
- **Impact:** A placeholder in a data field passes every structural check and propagates into reports and counts as if it were real — it surfaces only when someone hand-traces a broken reference, long after the trail is cold.
- **Source:** XR-207 — cross-project experience registry (2026).

### TST-13 [HIGH] Every Gate Declares the Set It Scans, and the Declaration Is Verified
A check states which files it covers, and something proves that declaration against the repo's real file set — an unstated scope is an unbounded claim over whatever the check happened to reach.
- **Detect:** scope arriving from an implicit default (the directory the check is invoked from, a hardcoded two-file list, a glob rooted one level too deep so the repo root is never read); a gate that exits green over an empty or nonexistent input set; a scope list written when the tree was smaller and never revisited, so directories added since are unscanned; a rule claimed as enforced while the corpus violates it outside the scanned subtree.
- **Fix:** name the scanned set explicitly (a `SCAN_DIRS`-style variable, a manifest, or a printed file count in the check's own output), assert it is non-empty, and — for a rule that is meant to be repo-wide — compare it against the tracked file list (`git ls-files`) so a new directory either joins the scan or fails the gate. Zero files matched is reported as a failure, never as a pass. Deliberate narrowing stays legal: it is declared next to the scope with the reason.
- **Impact:** A scope-blind gate is green for the same reason an empty one is — it found nothing to object to. The narrower the scope drifts, the greener and more useless the signal, and nobody re-reads a check that has been passing for a year.
- **Source:** Sibling of TST-11 — TST-11 proves a gate *can* go red, this one proves it is looking at everything it claims to cover.

### TST-14 [HIGH] A Check Nothing Calls Counts as Absent
Every check, audit, or test in the repo is reachable from the entry point that gates "done", or it is deleted; an uncalled check enforces nothing while reading as coverage.
- **Detect:** a script under `scripts/`/`tools/` that no task runner, hook, or pipeline invokes (grep the runner config for its name); a test file outside the runner's discovery pattern; a suite excluded from the aggregate command whose results are still quoted as coverage; a caller that discards the check's exit code (`run_checks(); echo done`) so failure cannot propagate; documentation stating "we lint with X" where nothing executes X.
- **Fix:** wire it into the single entry point, or delete it. A check excluded on purpose (platform-pinned goldens per TST-08, a slow suite moved to pre-push) is named at the entry point beside its exclusion, with the condition under which it does run — silence is not an exclusion record. After wiring, prove the path end-to-end: break the fixture, run the *entry point* (not the check directly), see red.
- **Impact:** Dead-lettered checks are the cheapest possible false assurance: the rule looks enforced, so nobody looks again, and the first real enforcement happens in production.
- **Source:** Sibling of TST-11 — TST-11 covers the gate that fires and proves nothing; this covers the gate that never fires at all.
