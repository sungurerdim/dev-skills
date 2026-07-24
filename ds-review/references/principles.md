# Engineering Principles (skill-bundled reference)

This file is bundled with every skill that depends on these principles, so the skill works standalone — even when the user installs only this one skill without the rest of the suite or the SKILL-SPEC. Every claim cites the source it came from; verify upstream when in doubt.

The eight sub-sections below cover only the principles that touch this skill's behavior. The full catalog (110 principles, 24 sources) is at https://github.com/sungurerdim/dev-skills/blob/main/references/software-best-practices.md.

---

## §1 — Seven Cross-Cutting Themes

| # | Theme | One-line rule | How this skill applies it |
|---|-------|--------------|---------------------------|
| 1 | **Single Source of Truth (SSOT)** | Every fact has exactly one authoritative location. | Findings file is one. Project profile is one. Conventions live in code, not duplicated in docs. |
| 2 | **Make change cheap** | Optimize for adaptability over perfection — requirements always change. | Skills propose minimal Category A fixes by default. Architecture changes are Category B (approval-gated). |
| 3 | **Feedback speed** | Time-to-discovery of a defect dominates total cost. | Phase gates fail loudly. Quality gates run on every commit/PR, not weekly. |
| 4 | **Fail fast and loudly** | A loud, early failure beats a silent, late one every time. | Skills surface blockers — never bypass with `--no-verify`, `reset --hard`, or hidden retries. Stop after 3 repeated failures. |
| 5 | **Locality of change** | Modular boundaries control blast radius — one requirement = one place. | Each skill owns a scope; cross-skill writes go through the shared findings file. |
| 6 | **Automate everything repeatable** | If a human does it more than twice, a machine should do it instead. | Skills are the automation. Resumable state means no manual re-running. |
| 7 | **Environment parity & reproducibility** | What runs in production must be deterministically reproducible from version control. | Skills detect missing lockfiles, env.example, dev/prod divergence. Artifact-producing skills write deterministic output. |

**Sources:** Pragmatic Programmer (DRY, ETC), 12-Factor App (https://12factor.net/), Google SRE Book (https://sre.google/sre-book/), DORA capabilities (https://docs.cloud.google.com/architecture/devops/technical), Martin Fowler — Continuous Integration (https://martinfowler.com/articles/continuousIntegration.html).

---

## §2 — SOLID + GRASP Architecture Heuristics

Architecture-auditing skills MUST evaluate code against these. Cite the principle by name in every finding title.

| Principle | Detection signal | Severity if violated |
|-----------|-----------------|---------------------|
| **Single Responsibility (SRP)** | Class/module changes for >1 reason; >1 export with unrelated concerns | HIGH |
| **Open/Closed (OCP)** | New behavior requires editing existing stable code (vs extending) | MEDIUM |
| **Liskov Substitution (LSP)** | Subtype violates parent's contract (postcondition narrowed, exception added) | HIGH |
| **Interface Segregation (ISP)** | Consumers forced to depend on members they don't use | LOW |
| **Dependency Inversion (DIP)** | High-level module depends directly on low-level concrete | MEDIUM |
| **Information Expert (GRASP)** | Logic placed away from its data | LOW |
| **Low Coupling (GRASP)** | Module imports >7 unrelated peers | MEDIUM |
| **High Cohesion (GRASP)** | Module exports unrelated functions | MEDIUM |

**Sources:** Robert C. Martin — *Clean Architecture* / *Agile Software Development* (SOLID); Craig Larman — *Applying UML and Patterns* (GRASP); ByteByteGo — 10 Coding Principles (https://bytebytego.com/guides/10-good-coding-principles-to-improve-code-quality/); Medium — 20 Principles (https://medium.com/@techievinay01/the-20-essential-principles-of-software-development-lod-soc-solid-and-beyond-6fd50774f994).

---

## §3 — Twelve-Factor Adherence

Operational and scaffolding skills MUST check:

| Factor | Rule |
|--------|------|
| 1. Codebase | One repo per app, many deploys |
| 2. Dependencies | Explicit declaration + lockfile |
| 3. Config | In environment, never in code |
| 4. Backing services | Attached as resources via URL |
| 5. Build / Release / Run | Strict separation; release is immutable |
| 6. Processes | Stateless, share-nothing |
| 7. Port binding | App exports HTTP via port; no embedded server runtime |
| 8. Concurrency | Scale out via process model |
| 9. Disposability | Fast startup, graceful shutdown |
| 10. Dev/prod parity | Same backing services in all environments |
| 11. Logs | Stdout streams; no log file management |
| 12. Admin processes | Run as one-off processes against the same code |

**Source:** *The Twelve-Factor App* by Adam Wiggins (https://12factor.net/) — every factor at its own URL; see linked sub-pages for rationale.

---

## §4 — Reliability Patterns

Production-bound code MUST have:

- **Timeouts** on every external call (no infinite waits)
- **Retry with exponential backoff** on transient failures (idempotent operations only)
- **Circuit breaker** between services with high call volume
- **Health checks** (liveness + readiness) on long-running processes
- **Idempotency keys** on write endpoints exposed externally
- **Graceful shutdown** handler (drain → close → exit)
- **Structured logging** (JSON or kv-pair, never raw `print`/`console.log` in production code)
- **Fail-fast input validation** at every system boundary

**Sources:** Google SRE Book — chapters on SLOs, Embracing Risk, Postmortem Culture (https://sre.google/sre-book/table-of-contents/); Martin Fowler — *Patterns of Enterprise Application Architecture*; Michael Nygard — *Release It!* (Stability Patterns).

---

## §5 — Security Baseline

Adopted from OWASP Secure Coding Practices and reinforces standard injection-mitigation practice. Applies to every skill that mutates code, generates artifacts, or scans source.

- **Validate at every system boundary** — user input, external APIs, file system reads, deserialization. Reject by default.
- **Least privilege** — every credential, token, role: minimum scope to do the job.
- **No secrets in source, configs committed to git, logs, error messages, URLs, or AI training data.** Scan every commit; scan every audit.
- **Defense in depth** — never rely on a single control. Auth + authz + input validation + output encoding + audit logging.
- **Crypto: never roll your own.** Use the platform's vetted library. Approved algorithms only (no MD5/SHA1/DES/ECB).
- **Quote every file path in shell.** Reject shell metacharacters in dynamic values.

**Sources:** OWASP Secure Coding Practices Quick Reference Guide (https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/); OWASP Top 10 (https://owasp.org/www-project-top-ten/); NIST SP 800-218 (Secure Software Development Framework).

---

## §6 — Pragmatic Process Rules

| Rule | Practical interpretation |
|------|-------------------------|
| **YAGNI** | Propose only what's needed for the stated goal — never speculate on hypothetical future needs. |
| **DRY** | Detect duplication and propose extraction. Never tolerate >3 instances of the same logic. |
| **KISS** | When two solutions both satisfy requirements, the simpler one wins. Complexity must earn its place with measurable benefit. |
| **Boy Scout Rule (bounded)** | Within the file you're editing, fix obvious adjacent issues. Outside that file → record as a finding, do not silently fix. (Bounded version that respects scope-creep prevention.) |
| **Conventional Commits** | Every commit type matches the litmus test (`feat`/`fix` only when end-user impact is real). |
| **Small frequent commits** | Atomic, reversible, one logical change per commit. |
| **Code review before merge** | Automated review precedes human review, not replaces it. |
| **Refactor mercilessly** | Treat dead code, single-caller helpers, and premature abstractions as findings every run. |
| **Profile before optimizing** | Require a measurable metric and baseline before any performance experiment. |
| **Breaking-first (XR-199)** | Default to the root-clean change: unpublished product, zero external consumers, or provably harmless → break directly; compat layers (shims, re-exports, dual models, redirect residue) are forbidden. Backward compatibility only on proven need (real consumer, live migration window, contract). Risk plausible but unproven → ask the owner, never assume. |

**Sources:** *The Pragmatic Programmer* by Andy Hunt & Dave Thomas (https://www.pragprog.com/tips/); Martin Fowler — YAGNI (https://martinfowler.com/bliki/Yagni.html), Refactoring (https://martinfowler.com/articles/refactoring-2nd-ed.html); Conventional Commits (https://www.conventionalcommits.org/).

---

## §7 — Testing Discipline

Skills that touch tests MUST honor:

- **Test Pyramid** — unit-heavy, integration-medium, E2E-light. Never invert.
- **Test realism** — real OS paths, production-equivalent layouts, realistic data (`user@example.com`, not `a@b.c`). No mocks for code you own — test the real thing.
- **Boundary conditions** — every test suite covers empty, null, max-size, concurrent, locale, timezone, Unicode, leap-day where applicable.
- **AAA pattern** — Arrange / Act / Assert. One concept per test.
- **Coverage as diagnostic, not goal** — low coverage signals risk; high coverage does not signal quality. Don't chase 100%.
- **Test names describe behavior** — `should_reject_negative_quantity_on_decrement`, not `test_cart_1`.
- **Tests fail loudly** — actionable error messages: what was expected, what was received, how to reproduce.
- **Regression tests for every bug fix** — written before the fix lands.

**Sources:** Martin Fowler — Practical Test Pyramid (https://martinfowler.com/articles/practical-test-pyramid.html), Test Coverage (https://martinfowler.com/bliki/TestCoverage.html); Kent Beck — *Test-Driven Development by Example* (AAA pattern); Robert C. Martin — *Clean Code* chapter on testing.

---

## §8 — Configuration & Secrets Discipline

Skills that produce or touch configuration MUST:

- Configuration **externalized** to environment, config files, or a secrets manager — never hardcoded in source.
- `.env.example` (or stack equivalent) MUST exist when any environment variable is consumed.
- Strict separation between **secrets** (never committed, never logged), **config** (committed but environment-overridable), and **constants** (committed, immutable).
- Production secrets rotated on detection of any leak. The skill surfaces the leak; rotation is the user's action.

**Sources:** *The Twelve-Factor App* — Factor III: Config (https://12factor.net/config); OWASP Secrets Management Cheat Sheet (https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html); NIST SP 800-57 (Key Management).

---

## §10 — Anti-Overengineering Guard (3-gate)

Every potential finding (whether from tactical, strategic, perf, or meta-quality mode) is screened before being reported: report only when AT LEAST ONE harm signal is present; no signal → silent discard.

1. **Breaks:** it breaks something — now, or on a predictable path (e.g. drift between duplicated sources).
2. **Misleads:** it misleads a future reader (human or AI) about what is live, canonical, or intended.
3. **Not worth its keep:** the complexity costs more to keep than the value it adds.

A finding with no harm signal on any axis is noise — this filter suppresses what would otherwise dominate output on mature codebases. This wording is canonical — identical in SKILL.md and meta-quality-scopes.md.

**Calibration:** When in doubt about signal 3 (is the complexity worth it?), treat it as worth its keep — the signal does not fire. The user can always lower the bar by widening scope; a noisy report wastes more attention than a missed nice-to-have.

**Sources:** Hunt & Thomas — Pragmatic Programmer (KISS / YAGNI tension); John Ousterhout — *A Philosophy of Software Design* (deep modules); Brooks — *No Silver Bullet*.

---

## §11 — Cross-Scope Deduplication

When multiple detectors flag the same site, apply these rules before emitting findings:

1. **Same file:line** → merge into one finding. Concatenate the matched scope names. Keep the highest severity.
2. **Within 10 lines** → merge if the underlying issue is the same (the user perceives it as one fix). Cite the leading line:column.
3. **Contradictory findings** (one says "delete", another says "extract") → keep the higher-confidence finding, discard the other. If tied, prefer the less destructive proposal.

Apply this pass after Phase 2 Analyze and again after Phase 3a Analyze-Principles (`--meta-quality` mode). The output of either phase must not contain duplicates by these rules.

**Why:** Repeated reporting of the same site under different scope labels inflates counts, exhausts user attention, and breaks the FRC+DSC accounting (the same site cannot have two final dispositions).

---

## §12 — Needs-Approval Reason Discipline

Every `needs-approval` and `skipped` finding MUST cite a concrete blocker. The blocker is parsed against an explicit reject list — match → reason is rejected → finding is re-routed.

**Concrete blocker examples (accepted):**

- "API-contract change — caller `foo()` in `pkg/x` expects the old signature"
- "Cross-module dependency — `mod_a` consumed by 7 unrelated callers; refactor exceeds review scope"
- "Runtime behavior uncertainty — timezone handling depends on host OS, needs user input"
- "Regulated change — schema migration on user table, requires compliance review"

**Rejected reasons (rewrite or fix inline):**

| Rejected pattern | Why rejected | What to do instead |
|------------------|--------------|-------------------|
| `already existed`, `pre-existing` | Not a blocker — Error Ownership Gate (W11) applies | Fix inline or cite concrete blocker |
| `not my change`, `unrelated to task` | Boy-Scout rule (bounded) covers same-file fixes | Fix in current file; flag out-of-file as separate finding |
| `out of scope` | Vague — define the actual scope edge | Cite which scope: "exceeds `--scope=hygiene` boundary into `architecture`" |
| `too hard`, `complex`, `will do later` | Difficulty is not a blocker | Cite the specific obstacle (API contract, dependency, runtime uncertainty) |
| `not sure how` | Uncertainty is research, not deferral | Either research and decide, or invoke `/ds-research`; do not park |

**Enforcement:** Before writing a finding's disposition, the skill parses the reason against the reject list. Match → either (a) downgrade `needs-approval` to `apply` and fix inline, (b) escalate to user with a concrete-blocker prompt, or (c) rewrite the reason. The skill MUST NOT report status `OK` while any disposition still carries a rejected reason.

**Source:** dev-rules.md — Error Ownership Gate (W11).

---

## §9 — Authoritative Source URLs (consolidated)

| Source | URL |
|--------|-----|
| Twelve-Factor App | https://12factor.net/ |
| OWASP Top 10 | https://owasp.org/www-project-top-ten/ |
| OWASP Secure Coding Practices | https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/ |
| OWASP Secrets Management Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html |
| Google SRE Book | https://sre.google/sre-book/table-of-contents/ |
| Martin Fowler — Continuous Integration | https://martinfowler.com/articles/continuousIntegration.html |
| Martin Fowler — Practical Test Pyramid | https://martinfowler.com/articles/practical-test-pyramid.html |
| Martin Fowler — Test Coverage | https://martinfowler.com/bliki/TestCoverage.html |
| Martin Fowler — YAGNI | https://martinfowler.com/bliki/Yagni.html |
| Martin Fowler — Refactoring | https://martinfowler.com/articles/refactoring-2nd-ed.html |
| Martin Fowler — Domain-Driven Design | https://martinfowler.com/bliki/DomainDrivenDesign.html |
| Conventional Commits | https://www.conventionalcommits.org/ |
| ByteByteGo — 10 Coding Principles | https://bytebytego.com/guides/10-good-coding-principles-to-improve-code-quality/ |
| 20 Essential Principles (SOLID + GRASP + LoD + SoC) | https://medium.com/@techievinay01/the-20-essential-principles-of-software-development-lod-soc-solid-and-beyond-6fd50774f994 |
| Pragmatic Programmer 100 Tips | https://www.pragprog.com/tips/ |
| Refactoring.Guru | https://refactoring.guru/refactoring |
| DORA Capabilities | https://docs.cloud.google.com/architecture/devops/technical |
| NIST SP 800-218 (SSDF) | https://csrc.nist.gov/Projects/ssdf |
| Software Best Practices (full curated catalog, 110 principles) | https://github.com/sungurerdim/dev-skills/blob/main/references/software-best-practices.md |
