# Engineering Principles — shared core

**Consumers:** every `ds-*` skill that audits, fixes, generates, tests, or commits code. A skill loads only the section its phase names (`§2` for an architecture pass, `§7` for a test pass). Installed as `core/principles.md` beside the skill directories — `install.sh` ships `core/` on every install, including a single-skill install, so the link `../core/principles.md` always resolves.

Every row carries either a **Detect** signal a skill can run mechanically or the tag **judgment** — a call the executor makes from evidence and must state in the finding. Every section names its sources; sources are primary (author, standard, or maintainer) — no blog restatements. Verify upstream when in doubt. The full curated catalog (110 principles, 24 sources) is `software-best-practices.md` in this directory; this file holds only the operative subset.

---

## §1 — Seven Cross-Cutting Themes

| # | Theme | Rule | Detect |
|---|-------|------|--------|
| 1 | **Single Source of Truth (SSOT)** | Every fact has exactly one authoritative location. | Two files carry the same constant, threshold, list, or schema → grep the literal across the tree; count > 1 outside a generated file = finding. |
| 2 | **Make change cheap** | Optimize for adaptability over perfection — requirements always change. | judgment — prefer the smaller, reversible change (Category A) over the architectural one (Category B); state the alternative rejected. |
| 3 | **Feedback speed** | Time-to-discovery of a defect dominates total cost. | No format/lint/type/test check runs on commit or PR (no hook, no CI job, no `scripts/quality*`) = finding. |
| 4 | **Fail fast and loudly** | A loud, early failure beats a silent, late one. | `--no-verify`, `reset --hard` over uncommitted work, swallowed exceptions (`except: pass`, empty `catch`), retries without a cap = finding. Stop after 3 repeated failures of the same action. |
| 5 | **Locality of change** | One requirement = one place; modular boundaries bound the blast radius. | A single requirement change touches > 3 modules → finding on the coupling, not on the change. |
| 6 | **Automate everything repeatable** | A human doing it more than twice → a machine does it. | A README step run by hand on every release/commit (manual version bump, manual copy of generated output) = finding. |
| 7 | **Environment parity & reproducibility** | Production is deterministically reproducible from version control. | Missing lockfile, missing `.env.example` while env vars are read, dev-only backing service that differs from prod, non-deterministic build output (timestamps in artifacts) = finding. |

**Sources:** Hunt & Thomas — *The Pragmatic Programmer* (DRY, ETC); Wiggins — *The Twelve-Factor App* (https://12factor.net/); Beyer et al. — *Site Reliability Engineering* (https://sre.google/sre-book/table-of-contents/); DORA — technical capabilities (https://dora.dev/capabilities/); Fowler — *Continuous Integration* (https://martinfowler.com/articles/continuousIntegration.html).

---

## §2 — SOLID + GRASP Architecture Heuristics

Architecture-auditing passes evaluate against these and cite the principle by name in the finding title.

| Principle | Detect | Severity if violated |
|-----------|--------|---------------------|
| **Single Responsibility (SRP)** | Module changes for > 1 reason; > 1 export with unrelated concerns (git log of the file shows commits from unrelated features) | HIGH |
| **Open/Closed (OCP)** | Adding a variant requires editing an existing `switch`/`if` chain rather than adding a case/implementation | MEDIUM |
| **Liskov Substitution (LSP)** | Subtype narrows a postcondition, throws where the parent does not, or stubs a parent method (`raise NotImplementedError`, `throw new Error('unsupported')`) | HIGH |
| **Interface Segregation (ISP)** | Consumers import an interface and use < 30% of its members; implementors stub members they do not need | LOW |
| **Dependency Inversion (DIP)** | Business-logic module imports a concrete driver/client directly (`import psycopg2`, `new StripeClient(...)` inside domain code) | MEDIUM |
| **Information Expert (GRASP)** | Logic that reads ≥ 3 fields of one object lives outside that object's module | LOW |
| **Low Coupling (GRASP)** | Module imports > 7 unrelated peers | MEDIUM |
| **High Cohesion (GRASP)** | Module's exports share no nouns and no callers | MEDIUM |

**Sources:** Martin — *Agile Software Development: Principles, Patterns, and Practices* (SOLID) and *Clean Architecture*; Larman — *Applying UML and Patterns* (GRASP).

---

## §3 — Twelve-Factor Adherence

Operational and scaffolding passes check each factor; a factor with no Detect column is judgment against the app's deploy target.

| Factor | Rule | Detect |
|--------|------|--------|
| 1. Codebase | One repo per app, many deploys | Two apps share one repo without a workspace/monorepo manifest, or one app is split across repos with copied code |
| 2. Dependencies | Explicit declaration + lockfile | Manifest without lockfile; lockfile not committed; system packages assumed (`apt install` in README, not in a container/build file) |
| 3. Config | In environment, never in code | Hostnames, ports, feature flags, credentials as literals outside `*.example`/test fixtures |
| 4. Backing services | Attached as resources via URL | DB/cache/queue connection built from hard-coded parts instead of one `*_URL` |
| 5. Build / Release / Run | Strict separation; release immutable | Build step mutates source, or runtime step compiles/installs |
| 6. Processes | Stateless, share-nothing | In-process session store, local-disk uploads, in-memory cache treated as durable |
| 7. Port binding | App exports HTTP via a port | Port hard-coded; no `PORT` (or stack-equivalent) env read |
| 8. Concurrency | Scale out via process model | judgment |
| 9. Disposability | Fast startup, graceful shutdown | No SIGTERM/SIGINT handler that drains in-flight work |
| 10. Dev/prod parity | Same backing services everywhere | SQLite in dev, Postgres in prod; mocked queue in dev |
| 11. Logs | Stdout streams; no log-file management | App opens/rotates its own log files |
| 12. Admin processes | One-off processes against the same code | Migrations or maintenance tasks run through a separate codebase or by hand |

**Source:** Wiggins — *The Twelve-Factor App* (https://12factor.net/), one page per factor.

---

## §4 — Reliability Patterns

Production-bound code has each of these; absence is a finding at the listed severity.

| Pattern | Detect | Severity |
|---------|--------|----------|
| **Timeouts** on every external call | HTTP/DB/queue client constructed without a timeout argument or config | HIGH |
| **Retry with exponential backoff + jitter**, idempotent operations only | Retry loop without backoff, without a cap, or around a non-idempotent write | MEDIUM |
| **Circuit breaker** between high-volume services | judgment — required when a downstream outage would cascade (fan-out ≥ 3 callers) | MEDIUM |
| **Rate limiting + backpressure** at every ingress and every queue consumer | Public endpoint with no limiter middleware/config; unbounded in-memory queue or channel; producer never checks consumer lag | HIGH |
| **Health checks** (liveness + readiness) on long-running processes | No `/health`/`/ready` (or stack equivalent) route; readiness identical to liveness while the app has dependencies | MEDIUM |
| **Idempotency keys** on externally exposed write endpoints | POST that creates a resource accepts no idempotency key header/field | HIGH (payments) / MEDIUM (other) |
| **Graceful shutdown** (drain → close → exit) | No signal handler; server `close()` never awaited | MEDIUM |
| **Structured logging** | `print`/`console.log` in non-test production paths; log lines without level or without a stable key set | LOW |
| **Fail-fast input validation** at every system boundary | Request body used before schema validation; env var read without presence check | HIGH |
| **SLOs with error budgets** for user-facing services | judgment — no stated availability/latency objective and no alert tied to it = finding for a service with users | MEDIUM |

**Sources:** Beyer et al. — *Site Reliability Engineering*, chapters *Service Level Objectives*, *Handling Overload*, *Addressing Cascading Failures* (https://sre.google/sre-book/table-of-contents/); Nygard — *Release It!* (stability patterns: timeouts, circuit breaker, bulkheads, backpressure); Fowler — *Patterns of Enterprise Application Architecture*.

---

## §5 — Security Baseline

Applies to every pass that mutates code, generates artifacts, or scans source.

| Rule | Detect | Severity |
|------|--------|----------|
| **Validate at every system boundary** — user input, external APIs, file reads, deserialization; reject by default | Unvalidated request/param reaches a query, shell, file path, or deserializer | CRITICAL (injection path) / HIGH |
| **Least privilege** — every credential, token, role carries minimum scope | Wildcard IAM/OAuth scope; DB user with superuser; token with write scope used read-only | HIGH |
| **No secrets in source, committed config, logs, error messages, URLs** | `secret-patterns.md` content regexes and filename set; secret in query string; secret echoed in a log/exception | CRITICAL |
| **Defense in depth** — auth + authz + validation + output encoding + audit log | Route with authn but no authz check; template renders unescaped user content | HIGH |
| **Crypto: never roll your own; approved algorithms only** | MD5/SHA1 for integrity or passwords, DES/RC4/ECB, custom cipher/hash code, password stored without a slow salted KDF (argon2id/scrypt/bcrypt) | CRITICAL |
| **Supply chain** — pinned, lockfile-verified dependencies with provenance | Unpinned `latest`/`*`/floating major; lockfile ignored in CI (`npm install` instead of `npm ci`); install script from an unversioned URL; no dependency review on PRs; release without attestation/signature | HIGH |
| **Shell safety** — quote every path; reject metacharacters in dynamic values | Unquoted `$var` path in a script; user-derived string interpolated into a shell command | HIGH |

**Sources:** OWASP — *Secure Coding Practices Quick Reference Guide* (https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/); OWASP — *Top 10* (https://owasp.org/www-project-top-ten/); OWASP — *Password Storage Cheat Sheet* (https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html); NIST SP 800-218 — *Secure Software Development Framework* (https://csrc.nist.gov/Projects/ssdf); OpenSSF — *SLSA* supply-chain levels (https://slsa.dev/).

---

## §6 — Pragmatic Process Rules

| Rule | Interpretation | Detect |
|------|----------------|--------|
| **YAGNI** | Propose only what the stated goal needs; never speculate on future needs. | Abstraction, config option, or parameter with exactly one consumer and no second caller anywhere = finding (see §9) |
| **DRY** | Detect duplication and propose extraction. | ≥ 3 instances of the same logic (same token sequence ≥ 6 lines, or same regex/constant) = finding |
| **KISS** | Two solutions satisfy the requirement → the simpler wins; complexity earns its place with measured benefit. | judgment — record the measured benefit that justifies the complex form, or propose the simple one |
| **Boy Scout Rule (bounded)** | Inside the file being edited, fix obvious adjacent issues; outside it, record a finding, never silently fix. | Diff touches lines outside the task's files → scope violation |
| **Conventional Commits** | `feat`/`fix` only when end-user impact is real; everything else its own type. | Commit title fails `^(feat\|fix\|docs\|test\|chore\|refactor\|perf\|style\|build\|ci\|revert)(\([a-z0-9./-]+\))?!?: [a-z]` |
| **Small frequent commits** | Atomic, reversible, one logical change per commit. | A commit mixes an unrelated concern (e.g. `.gitignore` chore inside a feature) |
| **Code review before merge** | Automated review precedes human review; never replaces it. | judgment |
| **Refactor mercilessly** | Dead code, single-caller helpers, premature abstractions are findings every run. | Export with 0 callers; helper with 1 caller and < 10 lines; interface with one implementation |
| **Profile before optimizing** | A measurable metric and a baseline precede any performance change. | Performance-labelled change without a before/after measurement in the commit/PR/summary |
| **Breaking-first** | Default to the root-clean change: unpublished product, zero external consumers, or provably harmless → break directly. Compat layers (shims, re-exports, dual models, redirect residue) only on proven need — a real consumer, a live migration window, a contract — and time-boxed. Risk plausible but unproven → ask the owner; never assume compat is wanted. | Shim, `_unused` rename, `// removed` comment, or re-export added without a named consumer = finding |

**Sources:** Hunt & Thomas — *The Pragmatic Programmer* (https://pragprog.com/tips/); Fowler — *Yagni* (https://martinfowler.com/bliki/Yagni.html), *Refactoring* 2nd ed. (https://martinfowler.com/articles/refactoring-2nd-ed.html); *Conventional Commits* 1.0.0 (https://www.conventionalcommits.org/en/v1.0.0/).

---

## §7 — Testing Discipline

Passes that touch tests honor every row; a generated or repaired test that violates one is not done.

| Rule | Detect |
|------|--------|
| **Test pyramid** — unit-heavy, integration-medium, E2E-light; never inverted | E2E count ≥ unit count in a repo with unit-testable modules |
| **Test realism** — real OS paths, production-equivalent layouts, realistic data (`user@example.com`, `$99.99`) | Literal `a@b.c`, `foo`/`bar` domain data, `$1`, hand-rolled temp paths outside the OS temp API |
| **No mocks for code you own** — test the real thing; mock only true external boundaries (network, third-party API, filesystem, time) | Mock/stub target resolves to a module inside the repo |
| **Critical-flow wiring check** — money-moving, auth-gating, or data-deleting flows have ≥ 1 test exercising the real dispatch/registry/facade production traffic runs through | Every test of such a flow mocks the internal dispatch layer → the handler-never-registered bug is invisible |
| **Red proof** — a regression or bug-fix test is observed red against the unfixed code before it is observed green | No recorded red run for the test (Mechanical Done Gate red-proof) |
| **Boundary conditions** — empty, null, max-size, concurrent, locale, timezone, Unicode, leap-day where applicable | Suite for a function with a numeric/collection/string input has no empty/zero/max case |
| **AAA pattern** — Arrange / Act / Assert; one concept per test | Test body asserts on > 1 unrelated behavior |
| **Coverage as diagnostic, not goal** — low coverage signals risk; high coverage does not signal quality | Assertion-free test, tautological assertion (`expect(x).toBe(x)`), hard-coded expected output equal to the implementation's literal |
| **Names describe behavior** | `test_1`, `testCart`, `it('works')` |
| **Tests fail loudly** — expected vs received, how to reproduce | Bare `assert cond` without message on a non-trivial condition |
| **Regression test for every bug fix**, written before the fix lands | Fix-type commit without a test change |
| **Flaky procedure** — a test that fails intermittently is quarantined with a linked issue after 3 isolated runs + 1 shuffled-order run, never deleted or retried-until-green | Retry wrapper or `@flaky` decorator without a linked issue |

**Sources:** Fowler — *Practical Test Pyramid* (https://martinfowler.com/articles/practical-test-pyramid.html), *Test Coverage* (https://martinfowler.com/bliki/TestCoverage.html), *Mocks Aren't Stubs* (https://martinfowler.com/articles/mocksArentStubs.html); Beck — *Test-Driven Development: By Example*; Martin — *Clean Code*, ch. 9.

---

## §8 — Configuration, Secrets & Data Discipline

| Rule | Detect | Severity |
|------|--------|----------|
| Configuration **externalized** — environment, config file, or secrets manager; never hard-coded | Literal host/port/key in source outside `*.example` and tests | HIGH |
| `.env.example` (or stack equivalent) exists when any env var is consumed | `process.env.X` / `os.environ["X"]` / `System.getenv` read with no `.env.example` line for `X` | MEDIUM |
| Strict separation: **secrets** (never committed, never logged) · **config** (committed, env-overridable) · **constants** (committed, immutable) | Secret-named key in a committed config file; constant read from env | HIGH |
| Leaked secret → **rotate on detection**; the skill surfaces, the owner rotates | `secret-patterns.md` hit in the working tree or history | CRITICAL |
| **Key-rotation policy** — every long-lived credential has a documented rotation interval and an automated or runbook'd path | Credential age unknown or > 1 year with no rotation record; no runbook for rotating it | MEDIUM |
| **Data retention** — every store of personal data has a stated retention period and a deletion path | PII table/collection with no TTL, purge job, or documented retention; backups with no expiry | HIGH (regulated data) / MEDIUM |

**Sources:** Wiggins — *The Twelve-Factor App*, III. Config (https://12factor.net/config); OWASP — *Secrets Management Cheat Sheet* (https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html); NIST SP 800-57 Part 1 — *Recommendation for Key Management* (https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final); GDPR Art. 5(1)(e) storage limitation (https://eur-lex.europa.eu/eli/reg/2016/679/oj).

---

## §9 — Anti-Overengineering Guard (3-gate)

Every potential finding — tactical, strategic, performance, meta-quality, simplification — is screened before it is reported. Report only when **at least one** harm signal is present; no signal → silent discard, counted in the summary as `discarded (no harm signal): n`.

| Gate | Signal present when |
|------|--------------------|
| 1. **Breaks** | It breaks something now, or on a predictable path (drift between duplicated sources, a caller that will receive the wrong shape). |
| 2. **Misleads** | A future reader (human or AI) would conclude something false about what is live, canonical, or intended. |
| 3. **Not worth its keep** | The construct costs more to keep (maintenance, reading time, risk) than the value it adds. |

**Calibration:** doubt about gate 3 resolves to *worth its keep* — the signal does not fire. The user can widen scope; a noisy report costs more attention than a missed nice-to-have. This section is the canonical statement; a skill's SKILL.md carries at most a one-line pointer.

**Sources:** Hunt & Thomas — *The Pragmatic Programmer* (KISS/YAGNI tension); Ousterhout — *A Philosophy of Software Design* (deep modules); Brooks — *No Silver Bullet*.

---

## §10 — Cross-Scope Deduplication

Apply after every analysis pass and again after any second-stage pass, before findings are emitted.

| Rule | Action |
|------|--------|
| Same `file:line` from multiple detectors | Merge into one finding; concatenate scope names; keep the highest severity. |
| Within 10 lines, same underlying issue | Merge; cite the leading `line:column`. |
| Contradictory proposals (delete vs extract) | Keep the higher-confidence finding; tie → the less destructive proposal. |

**Why:** repeated reporting of one site under several labels inflates counts, exhausts attention, and breaks disposition accounting — one site cannot carry two final dispositions.

---

## §11 — Needs-Approval Reason Discipline

Every `needs-approval` and `skipped` disposition cites a concrete blocker. The reason is parsed against the reject list; a match means the reason is rejected and the finding is re-routed.

**Accepted (concrete blocker) examples:** "API-contract change — caller `foo()` in `pkg/x` expects the old signature" · "Cross-module dependency — `mod_a` consumed by 7 unrelated callers; exceeds this run's scope" · "Runtime behavior uncertainty — timezone handling depends on host OS; needs owner input" · "Regulated change — schema migration on the user table needs compliance review".

| Rejected pattern | Why | Instead |
|------------------|-----|---------|
| `already existed`, `pre-existing` | Not a blocker — every detected error gets a disposition (Error Ownership) | Fix inline or cite a concrete blocker |
| `not my change`, `unrelated to task` | Boy Scout Rule (bounded) covers same-file fixes | Fix in the current file; out-of-file → its own finding |
| `out of scope` | Vague — the scope edge is undefined | Name the edge: "exceeds `--scope=hygiene` into `architecture`" |
| `too hard`, `complex`, `will do later` | Difficulty is not a blocker | Cite the obstacle: contract, dependency, runtime uncertainty |
| `not sure how` | Uncertainty is research, not deferral | Research and decide, or hand to a research pass; never park |

**Enforcement:** before writing a disposition, parse the reason against the table. Match → (a) downgrade `needs-approval` to apply and fix inline, (b) escalate with a concrete-blocker prompt, or (c) rewrite the reason. Status `OK` is never reported while any disposition carries a rejected reason.

---

## §12 — Source Index

| Source | URL |
|--------|-----|
| The Twelve-Factor App | https://12factor.net/ |
| OWASP Top 10 | https://owasp.org/www-project-top-ten/ |
| OWASP Secure Coding Practices | https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/ |
| OWASP Secrets Management Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html |
| OWASP Password Storage Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html |
| Google SRE Book | https://sre.google/sre-book/table-of-contents/ |
| DORA capabilities | https://dora.dev/capabilities/ |
| Martin Fowler — Continuous Integration | https://martinfowler.com/articles/continuousIntegration.html |
| Martin Fowler — Practical Test Pyramid | https://martinfowler.com/articles/practical-test-pyramid.html |
| Martin Fowler — Test Coverage | https://martinfowler.com/bliki/TestCoverage.html |
| Martin Fowler — Mocks Aren't Stubs | https://martinfowler.com/articles/mocksArentStubs.html |
| Martin Fowler — Yagni | https://martinfowler.com/bliki/Yagni.html |
| Martin Fowler — Refactoring, 2nd ed. | https://martinfowler.com/articles/refactoring-2nd-ed.html |
| Conventional Commits 1.0.0 | https://www.conventionalcommits.org/en/v1.0.0/ |
| Pragmatic Programmer — tips | https://pragprog.com/tips/ |
| NIST SP 800-218 (SSDF) | https://csrc.nist.gov/Projects/ssdf |
| NIST SP 800-57 Part 1 (Key Management) | https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final |
| OpenSSF SLSA | https://slsa.dev/ |
| GDPR (Regulation 2016/679) | https://eur-lex.europa.eu/eli/reg/2016/679/oj |
| Full curated catalog (110 principles, 24 sources) | `software-best-practices.md` (this directory) |

Books cited without a URL (Martin, Larman, Nygard, Fowler *PoEAA*, Beck, Ousterhout, Brooks, Hunt & Thomas) are print sources; cite by title and chapter.
