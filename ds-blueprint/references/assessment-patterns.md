# Assessment Patterns (Phase 3)

Detector catalog for the Assess phase: which scopes each dimension owns, what patterns to scan for, the behavioral hotspot pass, and the false-positive guard every signal must clear. Loaded when Phase 3 runs.

**Dimension → Scope mapping:**

| Dimension | Findings Scope(s) |
|-----------|------------------|
| Security & Privacy | `security`, `privacy` |
| Code Quality | `hygiene`, `types`, `simplify`, `ai-hygiene`, `doc-sync` |
| Architecture | `architecture`, `patterns`, `cross-cutting`, `maintainability`, `ai-architecture`, `contract-consistency` |
| Performance | `performance` |
| Resilience | `robustness`, `production-readiness` |
| Testing | `testing`, `functional-completeness` |
| Stack Health | `stack`, `stack-fitness` |
| DX | `dx`, `external-tooling` |
| Documentation | `docs`, `spec-alignment` |

**Assessment method per dimension:**

| Dimension | Scan | Patterns |
|-----------|------|----------|
| Security & Privacy | All source | Hardcoded secrets ({api-key-shape}, {token-shape}, password literals), `eval()`/`Function()` with dynamic input, SQL string concat, missing parameterized queries, missing auth middleware on protected routes, PII in log statements, weak crypto (MD5, SHA1, DES, ECB), missing HTTPS, CORS wildcard, missing CSRF, missing input validation, missing rate limiting |
| Code Quality | All source | Unused imports/vars/functions, missing type annotations on public APIs, nesting >3, duplicated blocks >10 lines, dead code, magic numbers, functions >50 lines, files >500 lines, empty catch, stale TODO/FIXME/HACK >30 days. **ai-hygiene:** AI boilerplate (verbose wrappers, unnecessary abstractions), placeholder comments ("This function does X"), redundant error layers, hallucinated APIs (calls to nonexistent methods/imports), dead feature flags, stale mocks left in production paths. **doc-sync:** inline doc contradicts signature, stale param descriptions, wrong return type. |
| Architecture | Import graph + structure | **SOLID violations ([principles.md §2](../../core/principles.md)):** SRP (module changes for >1 reason), OCP (new behavior added by editing stable code), LSP (subtype narrows postcondition or throws unhandled), ISP (consumer forced to depend on unused members), DIP (high-level imports concrete low-level). **GRASP:** Information Expert (logic away from data), Low Coupling (>7 unrelated peer imports), High Cohesion (unrelated exports same module). Plus: circular deps, god classes (>10 public methods or >300 lines), feature envy, layer violations, missing DI, inconsistent error handling, inconsistent naming. **maintainability:** change coupling, shotgun surgery (single change requires 5+ file edits), missing abstraction boundaries, churn×complexity hotspots (behavioral pass below). **ai-architecture:** prompt templates scattered (should be centralized), missing retry/fallback for AI API, hardcoded model names, missing token budget; product-facing LLM features: untrusted input concatenated into prompts (injection surface), model output consumed without schema/shape validation, no eval or regression set for prompt changes, no per-call cost/usage tracking. **contract-consistency:** same concept → same name (one verb per operation class: not fetch/get/load mixed for the same action; domain terms uniform across layers — not user/account/member for one entity), same word → same meaning everywhere, analogous functions share parameter order + options shape, consistent units/formats (time units, ID types, date/serialization casing at boundaries), one return/error shape per layer (throw vs Result vs null never mixed within a layer), same operation exposed with divergent signatures across modules. 3+ examples before flagging a lexicon pattern as systemic. |
| Performance | All source | N+1 queries (DB call in loop), blocking calls in async, missing pagination on lists, missing DB indexes, large file reads without streaming, missing caching, unbounded collection growth, synchronous I/O in hot paths |
| Resilience | Source + config | Missing error handling on external calls, missing timeout config, missing retry-with-backoff, no graceful shutdown, no health check, unbounded queue/buffer, missing circuit breaker, no fallback for failed deps, missing input size limits. **production-readiness:** missing structured logging, debug endpoints exposed, missing rate limiting, no graceful degradation under load, missing deployment health checks. |
| Testing | Tests + config | **Test discipline ([principles.md §7](../../core/principles.md)):** Test Pyramid signal (unit-heavy / integration-medium / E2E-light — inverted pyramid = HIGH); AAA structure absent; non-behavior test names (`test_1` vs `should_reject_negative_quantity`); unrealistic data (`a@b.c`, `$1`, length-1 collections); coverage configured as goal (target %) rather than diagnostic. Plus: test count vs source ratio, missing runner config, missing coverage config, untested modules, missing negative/boundary cases (empty, null, max-size, concurrent, locale, timezone, Unicode, leap-day), test isolation (shared mutable state), flaky indicators (sleep/delay, time-dependent assertions). **functional-completeness:** missing error paths, missing input validation edge cases, TODO/FIXME markers for unfinished, stub/placeholder implementations. |
| Stack Health | Manifests + lockfiles | Missing lockfile, outdated deps (major versions behind), deprecated packages, known CVEs in deps (run audit), missing `.nvmrc`/`.tool-versions`, inconsistent dep versions across workspace. **stack-fitness:** every major dep evaluated vs stated goal — obsolete (unmaintained, archived, last release >24 months), oversized-for-purpose (enterprise framework for 2-module project), duplicate (two libraries serving same purpose, e.g. {alt-1} + {alt-2}), misaligned (server-side library pulled into browser-only project). Cite goal from `Priorities:`. |
| DX | Root files + config | Missing/incomplete README, missing CONTRIBUTING.md, missing CI config, missing env.example, missing setup/dev scripts, missing Makefile/Taskfile, missing .editorconfig, inconsistent config formats. **external-tooling:** GitHub Actions workflows, PR automations (auto-merge bots, reviewer assignment), CI scripts, pre-commit hooks, release automation — each evaluated for goal-fitness. Unused workflows, workflows referencing deleted actions, duplicate workflows (two paths to same target), automations added by templates but never triggered, goal-misaligned (e.g. iOS signing workflow on non-iOS project). |
| Documentation | Doc files + source | Missing doc files vs ideal for type, README sections missing (install, usage, API, contributing), API doc gaps (undocumented public endpoints/functions), doc↔code drift (stale paths, renamed functions, changed defaults, removed features still documented), broken internal links, outdated version refs, stale dep version claims, architectural claims that don't match code. **spec-alignment:** promise census — extract every concrete capability promised in README / SPEC.md / docs/ / AI instruction file (per host — see [detection.md](detection.md) § Instruction Files) / blueprint profile. For each promise, search source for implementation. Classify: **promised-not-implemented** (doc mentions feature X; grep shows no module/function/endpoint), **implemented-not-documented** (code has X but no doc mentions), **drift** (both exist but behavior diverges — default changed, signature changed, flag removed). |

**Churn × complexity hotspot pass (Architecture · `maintainability`)** — behavioral signal from plain git history (git is already required; zero new dependencies):

| Step | Action |
|------|--------|
| 1 Churn | Rank files by change frequency: `git log --format=format: --name-only --since=12.month \| egrep -v '^$' \| sort \| uniq -c \| sort -nr \| head -50` |
| 2 Complexity | Rank the same files by the complexity signals already collected (nesting, function/file length); a deterministic cross-language counter available in-session (e.g. `scc --by-file -s complexity`) → use its per-file ranking instead |
| 3 Hotspot | File in the upper half of BOTH rankings → `maintainability` finding (hotspot) — prioritize above equally-complex but rarely-changed files |
| 4 Fallback | No usable history (fresh repo, shallow clone, empty log) → skip pass, note `churn signal unavailable — static-only maintainability scan`, static signals stand alone |

**External hygiene cross-check (advisory):** project is a public OSS repo AND a repo-scorecard tool (e.g. OpenSSF Scorecard) is available in-session → run once; fold per-check results into Security & Privacy and Stack Health as MEDIUM-confidence signals (heuristic cross-check, not ground truth). Tool absent → skip; no gate depends on it.

**False-positive prevention (mandatory for every signal)** — count a pattern match only if it passes ALL applicable:
- **Exclude tests:** skip matches in `test/`, `tests/`, `__tests__/`, `*_test.*`, `*.spec.*`, `*.test.*`
- **Exclude comments:** pattern inside comment (`//`, `#`, `/* */`, `<!-- -->`), skip
- **Exclude string literals in tests:** secret patterns in test fixtures or example data, skip
- **Exclude generated:** skip files in `generated/`, `*.g.dart`, `*.gen.go`, `*.pb.go`, auto-generated headers
- **Skip patterns:** `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING` blocks, test fixtures, generated files
- **Verify context:** for security signals, read 3 lines around match — value from env/config/vault → skip

**Confidence:** HIGH = match + context confirmed (full signal). MEDIUM = pattern, ambiguous context (0.5 signal). LOW = heuristic (skip). Only HIGH + MEDIUM written to `ds/audit/findings.md`.

**User-facing project gate (`ui` ≠ `none`):** additionally check i18n setup (framework-native catalog, ≥1 locale file); default locales configured (minimum: en + project owner's locale); a11y basics (semantic labels on interactive elements, contrast ratio, screen-reader support); responsive layout (breakpoints or adaptive layout). Missing item → HIGH severity. `ui=none` → N/A.
