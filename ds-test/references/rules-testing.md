# Rules: Contract Testing

Detect/fix patterns for API-boundary contract drift. Loaded when Phase 2a Generate resolves the `contract` scope.

### TST-01 [MEDIUM] API boundary contract drift

An API boundary artifact (OpenAPI/Swagger file, GraphQL schema, protobuf definition, JSON Schema for an event) exists but no test fails when the implementation drifts from it — the contract silently rots and consumers break without warning.

- **Detect:** repo contains an OpenAPI/Swagger file (`openapi.yaml`, `swagger.json`, etc.), a GraphQL schema (`schema.graphql`, `*.graphqls`), a protobuf definition (`*.proto`), or a JSON Schema for an event/message payload — AND the test suite has no test that validates the live implementation (request/response, resolver, message payload) against that artifact.
- **Fix:** generate a contract test that fails on schema drift. Preference order: the stack's dedicated contract-testing tool when installed (schemathesis for OpenAPI/Python stacks, Pact for consumer-driven contracts, the stack's native schema validator for GraphQL/protobuf/JSON Schema) → else an inline schema-load-and-validate test (load the artifact, validate a live request/response or payload sample against it, assert zero violations). The test follows the same red-proof gate and flaky procedure (3× isolated + 1× shuffled) as every other generated test (Phase 3 Verify) — never a weaker bar for contract tests.
- **Impact:** without a drift-detecting test, a backend/frontend or producer/consumer pair can silently desync — the documented contract stops matching the shipped behavior, and the first signal is a consumer's runtime failure in production, not a red test in CI.
- **Source:** [OpenAPI Specification](https://spec.openapis.org/oas/latest.html); [Pact — consumer-driven contract testing](https://docs.pact.io/); [schemathesis](https://schemathesis.readthedocs.io/).
