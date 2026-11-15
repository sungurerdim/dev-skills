# Engineering rules — project-wide detect signals

Loaded by `ds-audit` for every project with source code. Reliability, security, testing and secrets rules live in their domain files (`README.md`). Each row carries a **Detect** signal or the tag **judgment**; process rules for the run itself live in [kernel](../kernel.md).

## Seven Cross-Cutting Themes

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

## SOLID + GRASP Architecture Heuristics

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

## Twelve-Factor Adherence

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

## Design Rules

| Rule | Interpretation | Detect |
|------|----------------|--------|
| **YAGNI** | Propose only what the stated goal needs; never speculate on future needs. | Abstraction, config option, or parameter with exactly one consumer and no second caller anywhere = finding (kernel §4: report only what breaks, misleads or costs more than it gives) |
| **DRY** | Detect duplication and propose extraction. | ≥ 3 instances of the same logic (same token sequence ≥ 6 lines, or same regex/constant) = finding |
| **KISS** | Two solutions satisfy the requirement → the simpler wins; complexity earns its place with measured benefit. | judgment — record the measured benefit that justifies the complex form, or propose the simple one |
| **Refactor mercilessly** | Dead code, single-caller helpers, premature abstractions are findings every run. | Export with 0 callers; helper with 1 caller and < 10 lines; interface with one implementation |
| **Profile before optimizing** | A measurable metric and a baseline precede any performance change. | Performance-labelled change without a before/after measurement in the commit/PR/summary |
| **Breaking-first** | Default to the root-clean change: unpublished product, zero external consumers, or provably harmless → break directly. Compat layers (shims, re-exports, dual models, redirect residue) only on proven need — a real consumer, a live migration window, a contract — and time-boxed. Risk plausible but unproven → ask the owner; never assume compat is wanted. | Shim, `_unused` rename, `// removed` comment, or re-export added without a named consumer = finding |

**Sources:** Hunt & Thomas — *The Pragmatic Programmer* (https://pragprog.com/tips/); Fowler — *Yagni* (https://martinfowler.com/bliki/Yagni.html), *Refactoring* 2nd ed. (https://martinfowler.com/articles/refactoring-2nd-ed.html); *Conventional Commits* 1.0.0 (https://www.conventionalcommits.org/en/v1.0.0/).

## Source Index

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

Books cited without a URL (Martin, Larman, Nygard, Fowler *PoEAA*, Beck, Ousterhout, Brooks, Hunt & Thomas) are print sources; cite by title and chapter.
