# Testing: value rule, prune and discipline gates

Loaded when tests are written, pruned or audited.

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

**Prune phase (`--prune`):** flag existing tests that provide no concrete value:

1. Search for tests asserting only: constructor/getter/setter behavior, trivial pass-through, framework-guaranteed behavior, 1:1 reimplementation of source code, or oversized snapshots (>100 lines — assert everything, verify nothing). Flag as CRITICAL (reward-hacking class, not merely low-value): assertions hard-coding expected outputs for special-cased known inputs, and test edits that weaken or bypass assertions to reach green.
   - **Enumerating assertion** (HIGH) — a test that pins *today's members of a set* instead of the rule that decides membership: the five package names currently exported, the three enum cases, the four config keys, the two allowed hosts. It passes green when a sixth member appears, so the contract it advertises silently widens exactly when it should fail. Detect: an assertion listing literal members of a collection the source computes or that grows over time. Replace with the rule — assert the predicate every member must satisfy, or compare against the generator's output — and keep a literal list only where the set is genuinely closed by specification, with that specification cited in the test.
2. Present flagged tests as table `| # | Test | File:Line | Reason | Action |` grouped by Reason with counts. Default: resolves automatically to delete all flagged tests (reversible via git), reported with reasons in the summary. `ask`: state the question (`Delete these N tests?`); ask **Delete all** / **Delete all <reason>** (per-reason bulk alongside the total) / **Review each** / **Keep all**. "All" = exactly the displayed set.
3. **Replacement rule:** after deleting a low-value test, check if file/module now has meaningful untested logic. Yes → generate a valuable replacement test targeting a real risk.
4. **Mutation check (advisory):** stack's mutation tool available (per-stack table in [toolchains.md](../toolchains.md) § Mutation testing) → run it on the scoped module, report mutation score beside line coverage, treat every surviving mutant as a weak-assertion finding, and feed each into `--generate`/`--update` as a targeted instruction (`mutant at {file}:{line} survived — add the assertion that kills it`) instead of regenerating whole files. Tool absent → gap-note `mutation tool unavailable — assertion quality verified by pattern review only`, apply the step-1 pattern list as the fallback detector. Coverage alone is not proof: a documented real-world suite reported 93% line coverage against a 58.62% mutation score — a 34-point gap of assertions that constrain nothing.

### Other Gates

Discipline rules below (Test Pyramid, Boundary conditions, AAA structure, Regression-before-fix, Coverage-as-diagnostic) derive from [engineering](engineering.md) — Testing Discipline.

- Generated tests must pass before declaring done — never commit failing tests.
- Keep assertions at full strength — fix the test logic or report the app bug instead of weakening checks.
- Test names describe behavior, not implementation. No test depends on execution order — each independently runnable.
- Mocks minimal — only mock external dependencies (network, filesystem, time), not internal modules. Generated test matches project's existing style — no style drift.
- **Test Pyramid:** unit-heavy, integration-medium, E2E-light. Detect inverted pyramid (E2E > integration > unit) → flag HIGH before generating more E2E.
- **Boundary conditions:** every generated test suite covers empty, null, max-size, concurrent, locale, timezone, Unicode, leap-day where applicable.
- **Scale-envelope fixture pattern (D1/B3, advisory):** for the project's critical flows, generate a synthetic max-size fixture (e.g. 50k records) and measure those flows against it — this is the *measured, documented* extension of the max-size boundary case above, not a replacement for it. No documented scale limit exists for a critical flow → advisory finding "no declared scale envelope — measure against a synthetic max-size fixture and document the limit" (never a blocker, cross-links to the Scale Envelope check in [review-performance.md](review-performance.md)).
- **AAA structure:** every generated test body has visible Arrange / Act / Assert separation — comments or whitespace lines, never one-shot expressions.
- **Regression-before-fix:** when an app bug is found, generate the regression test FIRST (failing), confirm it fails, then propose the source fix — red proof required (kernel.md §3).
- **Unreproduced bug ≠ speculative test (W12):** when a reported bug can't be reproduced after a genuine investigation (no plausible mechanism found, existing boundary-condition tests already cover the likely cause, no matching historical fix) — record what was checked and the exact repro conditions needed if it recurs; do NOT add a regression test for a symptom that was never actually observed or triggered. A test with no concrete triggering condition is a coverage-padding test (W12), not a safety net — it asserts nothing real and just adds maintenance weight.
- **Coverage as diagnostic:** never write a coverage target into generated test configs; configure coverage as a reporter only. The diagnostic is "what did we miss?", not "did we hit X%?".
- **Property-based tests (advisory):** target is a pure function with an algebraic property (roundtrip encode/decode, idempotence, commutativity, invariant preservation) AND the stack's property-testing library is already in the project deps (per-stack table in [../../core/toolchains.md §Property-based testing](../toolchains.md)) → offer a property test for the boundary-condition class instead of hand-enumerating cases; library absent → hand-enumerated boundary cases stand, gap-note the option once.
- **Snapshot discipline:** snapshot tests only for small, stable serialized output (a component's props contract, a config artifact) — a full-page or >100-line snapshot asserts everything and verifies nothing; flag existing ones as low-value in `--prune` step 1.

**Critical-flow wiring check (B3):** full detection mechanism and Gate wording are applied when tests are verified. Rationale for the no-mock rule: mocking the dispatch/registry/facade layer can hide a handler that was written but never registered — invisible to both a unit test of the handler and an integration test that mocks the facade it should be routed through. Detection + rationale: [engineering](engineering.md) — Testing Discipline.

### TST-30 [MEDIUM] API boundary contract drift

An API boundary artifact (OpenAPI/Swagger file, GraphQL schema, protobuf definition, JSON Schema for an event) exists but no test fails when the implementation drifts from it — the contract silently rots and consumers break without warning.

- **Detect:** repo contains an OpenAPI/Swagger file (`openapi.yaml`, `swagger.json`, etc.), a GraphQL schema (`schema.graphql`, `*.graphqls`), a protobuf definition (`*.proto`), or a JSON Schema for an event/message payload — AND the test suite has no test that validates the live implementation (request/response, resolver, message payload) against that artifact.
- **Fix:** generate a contract test that fails on schema drift. Preference order: the stack's dedicated contract-testing tool when installed (schemathesis for OpenAPI/Python stacks, Pact for consumer-driven contracts, the stack's native schema validator for GraphQL/protobuf/JSON Schema) → else an inline schema-load-and-validate test (load the artifact, validate a live request/response or payload sample against it, assert zero violations). The test follows the same red-proof gate and flaky procedure (3× isolated + 1× shuffled) as every other generated test — never a weaker bar for contract tests.
- **Impact:** without a drift-detecting test, a backend/frontend or producer/consumer pair can silently desync — the documented contract stops matching the shipped behavior, and the first signal is a consumer's runtime failure in production, not a red test in CI.
- **Source:** [OpenAPI Specification](https://spec.openapis.org/oas/latest.html); [Pact — consumer-driven contract testing](https://docs.pact.io/); [schemathesis](https://schemathesis.readthedocs.io/).
