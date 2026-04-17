# Rules: Architecture & Testing

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Architecture & Code Quality** | ARC-01–10 (3 CRITICAL, 6 MAJOR, 1 MINOR) | ~12 |
| **Testing** | TST-01–06 (1 CRITICAL, 5 MAJOR) | ~105 |

---

## Architecture & Code Quality

### ARC-01 [CRITICAL] Layered Architecture
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
- **Source:** Clean Architecture, Hexagonal Architecture

### ARC-02 [CRITICAL] Unidirectional Data Flow
State flows in one direction. Single source of truth per data type.
- **Detect:** State modified from multiple locations. Shared mutable state without clear ownership. Two-way binding causing update cycles
- **Fix:** Define clear state ownership. UI sends events, state holder processes and emits new state
- **Platform:**
  - React: Zustand/Redux for global, useState for local. Never mutate state directly
  - Vue: Pinia for global, reactive() for local
  - Backend: Request -> Service -> Response (no shared mutable state between requests)
- **Impact:** 40% faster feature delivery vs bidirectional state
- **Source:** Flux Architecture, React docs

### ARC-03 [MAJOR] Immutable Data Models
Data models use immutable patterns. No in-place mutation.
- **Detect:** Mutable objects passed between layers. In-place mutation of shared data. Missing equals/hashCode
- **Fix:**
  - TypeScript: `readonly` + spread operator or Immer
  - Python: `@dataclass(frozen=True)` or Pydantic `model_config = ConfigDict(frozen=True)`
  - Go: return new structs instead of mutating
  - Rust: ownership model (default immutable)
- **Source:** Eric Evans — Domain-Driven Design (Value Objects), Effective Java (Item 17: Minimize Mutability)

### ARC-04 [MAJOR] Dependency Injection
Constructor injection preferred. DI container for lifecycle management.
- **Detect:** Direct instantiation of dependencies in business logic (`new Service()`, hardcoded imports). Global singletons without injection. Tight coupling to implementations
- **Fix:**
  - NestJS: built-in DI (providers, modules)
  - Express: manual constructor injection or tsyringe/inversify
  - FastAPI: `Depends()` for dependency injection
  - Django: explicit service instantiation in views/factories
  - Go: constructor injection (idiomatic)
  - Spring: `@Autowired` / constructor injection
- **Source:** SOLID Dependency Inversion Principle

### ARC-05 [CRITICAL] No Business Logic in Entry Points
Zero business rules in route handlers, controllers, or CLI commands. Entry points = parse input + call service + format output.
- **Detect:** if/else business decisions in route handlers. Data transformation in controllers. Validation logic mixed with handling
- **Fix:** Move to service layer. Entry points: parse request, validate input shape, call service, format response
- **Source:** Clean Architecture, SOLID SRP

### ARC-06 [MAJOR] Consistent Error Handling Strategy
Single error handling pattern across codebase. Errors categorized and handled per type.
- **Detect:**
  - Mixed error handling: some try-catch, some .catch(), some unhandled
  - Generic catch-all without specific handling
  - Error types not categorized (validation vs business vs infrastructure)
  - Search: empty catch blocks, `catch (e) {}`, `except: pass`, `_ = err`
- **Fix:** Define error hierarchy (ValidationError, NotFoundError, AuthError, InternalError). Global error handler middleware. Map errors to HTTP status codes. Log infrastructure errors, return safe messages to clients
- **Source:** Microsoft Error Handling Guidelines, Go Error Handling (Effective Go), Node.js Error Handling Best Practices

### ARC-07 [MAJOR] Feature Modularization
Feature modules with clear boundaries. No circular dependencies.
- **Detect:** Single flat directory with everything. Feature coupling. Imports crossing module boundaries without clear API
- **Fix:** Group by feature (not by type). Each feature exposes public API. Shared module for common utilities. Clear dependency direction
- **Source:** Modular Architecture Patterns

### ARC-08 [MAJOR] Typed Error Results
Typed results for recoverable errors. Exceptions for exceptional cases only.
- **Detect:** try-catch for expected errors (validation, not-found). Null as error signal. Untyped error propagation
- **Fix:**
  - TypeScript: discriminated unions `{ success: true, data } | { success: false, error }`
  - Python: Result pattern or explicit exception types
  - Go: `(value, error)` return pattern (idiomatic)
  - Rust: `Result<T, E>` (built-in)
- **Source:** Rust Error Handling (The Rust Programming Language), TypeScript Discriminated Unions, Go (value, error) Pattern

### ARC-09 [MAJOR] Defensive External Data Parsing
Validate all external data at boundaries. No trust for API responses, user input, or file contents.
- **Detect:** Force-casting external data. No schema validation on API responses. Unvalidated file uploads
- **Fix:** Validate with schemas at boundaries: Zod (TS), Pydantic (Python), serde (Rust). Handle malformed data gracefully. Never trust external shape
- **Source:** Postel's Law, Secure by Design

### ARC-10 [MINOR] Complexity Limits
Cyclomatic complexity <= 15. Function <= 50 lines. Nesting <= 3. Parameters <= 4.
- **Detect:** Functions exceeding limits. Deep nesting. Long parameter lists
- **Fix:** Extract functions. Early returns. Parameter objects. Composed functions
- **Source:** SonarQube, ESLint complexity rules

---

## Testing

### TST-01 [MAJOR] Test Pyramid 70/20/10
70% unit (services/logic), 20% integration (layer interactions, DB), 10% E2E (critical flows).
- **Detect:** Inverted pyramid. No integration tests. Only E2E tests. Untested services
- **Fix:** Unit test every public service/use-case method. Integration with test DB. E2E for critical user journeys
- **Platform:**
  - Node: Jest/Vitest (unit), Supertest (integration), Playwright/Cypress (E2E)
  - Python: pytest (unit+integration), Playwright (E2E)
  - Go: testing package (unit), testcontainers (integration)
- **Impact:** 4x faster releases with proper pyramid
- **Source:** Martin Fowler — Test Pyramid, Google Testing Blog — Testing on the Toilet

### TST-02 [MAJOR] >= 80% Meaningful Coverage
Quality over quantity. Branch coverage for critical paths.
- **Detect:** Coverage < 80%. Tests without assertions. Happy-path-only tests
- **Fix:** CI coverage gate. Test edge cases and error paths. Branch coverage for business logic
- **Note:** 80% meaningful > 95% superficial
- **Source:** Martin Fowler — Test Coverage, Google Testing Blog — Code Coverage Best Practices

### TST-03 [MAJOR] Fakes Over Mocks
Deterministic fake implementations. Mocks only for interaction verification.
- **Detect:** Mocks verifying implementation details. Tests breaking on refactor. External deps in unit tests
- **Fix:** In-memory fake repositories/services. Fakes simulate real behavior. Mocks only for verifying calls were made
- **Impact:** 80% faster tests, refactor-resistant
- **Source:** Google Testing Blog

### TST-04 [MAJOR] Integration Tests with Real Dependencies
Test with real databases and services using containers.
- **Detect:** Integration tests mocking the database. No test database setup. API tests without real server
- **Fix:**
  - Use testcontainers for DB (PostgreSQL, Redis, MongoDB)
  - Supertest/httptest for API integration
  - Seed test data, clean up after each test
  - Separate test config from production
- **Source:** Testcontainers, Integration Testing Patterns

### TST-05 [CRITICAL] No Weakened Assertions
Never skip, mock away, or relax assertions to make tests pass.
- **Detect:** `skip` on failing tests. Assertions changed to match bugs. Mocks replacing the tested unit
- **Fix:** Fix code or fix test to validate correct behavior. Every bug fix = regression test
- **Source:** Kent Beck — Test-Driven Development: By Example, Google Testing Blog

### TST-06 [MAJOR] Static Analysis
Linter + type checker must pass.
- **Detect:** No linter configured. Type errors ignored. Suppressed warnings without justification
- **Fix:**
  - TypeScript: `strict: true` in tsconfig, ESLint with recommended rules
  - Python: mypy strict + ruff/flake8
  - Go: `go vet` + `golangci-lint`
  - Rust: `clippy` (default)
- **Source:** TypeScript Strict Mode Documentation, mypy Documentation, golangci-lint, Rust Clippy
