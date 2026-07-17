# Rules: Meta-Quality Scopes

Principle-based detection scopes for `/ds-review --meta-quality`. Each scope defines: detector rule, threshold, false-positive guard, skip patterns.

## SSOT-ARCHITECTURAL [HIGH] Same fact in 2+ authoritative locations

Single Source of Truth violation — a configuration value, business rule, constant, or domain decision exists in two or more modules with the same semantic intent.

- **Detect:** identical constant value OR equivalent business rule (e.g., same validation threshold, same regex, same enum mapping) declared in 2+ files. Compare by literal value AND by semantic role (variable name + adjacent context).
- **Fix:** consolidate to a single owning module; replace duplicates with imports.
- **Threshold:** ≥2 authoritative locations. One module + one test fixture does not count.
- **Skip:** test fixtures, generated files (`*.g.dart`, `*.gen.go`, `*.pb.go`), platform-conditional code (e.g., Windows/macOS variants), framework-required signatures.
- **Confidence:** HIGH only if both literal value and semantic role match. Otherwise MEDIUM.
- **Impact:** Drift between locations causes silent business-rule divergence; refactors miss one location.
- **Source:** [Pragmatic Programmer §11](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/) — DRY at the knowledge level, not just the syntactic level.

## DRY-PATTERN [MEDIUM] Same code pattern in 3+ places

Don't Repeat Yourself violation — the same control-flow structure (loop + branch + I/O, or repeated try/catch/log/return shape) appears in three or more sites.

- **Detect:** AST/token-based similarity ≥85% across ≥3 distinct locations. Match by structural shape (statement sequence, branching pattern, identifier role), not by string equality.
- **Fix:** extract a shared helper function or strategy/decorator pattern.
- **Threshold:** ≥3 occurrences with ≥85% AST similarity. Two occurrences = note, not a finding.
- **Skip:** simple data-structure literals (struct/dict initializers), framework-required boilerplate (e.g., per-route handler setup that the framework demands), test fixtures with intentional parallel structure.
- **Confidence:** HIGH at 4+ matches with 90%+ similarity; MEDIUM at 3 matches with 85-90%.
- **Impact:** N×bug-cost when a defect is fixed in one site but not the others.
- **Source:** Hunt & Thomas, Pragmatic Programmer.

## KISS-FIT [MEDIUM] Complexity exceeds problem size

Keep It Simple, Stupid — the solution's complexity is disproportionate to the problem being solved.

- **Detect:** cyclomatic complexity > 12 on a function serving a single use-case AND no anticipated extension point. Combine with: parameter count > 4, branching depth > 3, helper-class count > 2 for a single feature.
- **Fix:** propose a flatter alternative; show before/after complexity numbers.
- **Threshold:** cyclomatic > 12 plus at least one additional signal (params, depth, helpers).
- **Metric note:** when a configured tool reports **cognitive complexity** (SonarSource metric), prefer it over cyclomatic for this scope — cyclomatic counts execution paths (a testability measure), cognitive complexity penalizes nesting and flow-breaking constructs (an understandability measure, which is what KISS is about); SonarSource's default threshold is 15. A `switch` with 20 flat cases is high-cyclomatic but low-cognitive — not a KISS finding.
- **Skip:** inherently complex domains — cryptography, numerical analysis, parser generators, regex compilers, lock-free algorithms. Cite the domain as the skip reason.
- **Confidence:** HIGH when complexity > 20; MEDIUM at 12-20.
- **Impact:** Reading cost compounds for every future maintainer.
- **Source:** Brooks, Mythical Man-Month; Kernighan, Programming Style.

## YAGNI-USAGE [HIGH] Defined but never used

You Aren't Gonna Need It — a feature, function, parameter, flag, or config field is declared but has zero references in source or tests.

- **Detect:** symbol declared (function, class, parameter, env var, flag, feature toggle) with 0 callers found via LSP `findReferences` or full-text grep.
- **Fix:** delete the unused declaration; if it's an exposed contract, mark as `needs_approval` (potentially called externally).
- **Threshold:** 0 in-repo references.
- **Skip:** public API of a library (exported from `index.*` / package manifest), CLI entry points, framework lifecycle hooks (`onMount`, `componentDidMount`, etc.), `_` prefix unused params, `TYPE_CHECKING` imports, plugin entry points declared in manifests.
- **Confidence:** HIGH for internal helpers with 0 callers; MEDIUM for parameters (might be required by an interface contract).
- **Impact:** Dead code drains context budget on every model read and confuses contributors about what's live.
- **Source:** XP / Beck, Extreme Programming.

## SOC-ISOLATION [MEDIUM] Responsibility scattered across 3+ modules

Separation of Concerns — a single conceptual responsibility (input validation, currency formatting, retry/backoff logic, etc.) is implemented in three or more modules independently.

- **Detect:** same semantic responsibility (matched by role keywords + similar function signatures) found in 3+ modules that are not co-located. Each site has its own variant rather than a shared utility.
- **Fix:** propose a single owner module; route all sites through it.
- **Threshold:** ≥3 distinct modules implementing the same responsibility.
- **Skip:** cross-cutting concerns intentionally embedded at each call site (e.g., logging, auth checks) — those are part of the platform pattern, not a violation.
- **Confidence:** MEDIUM by default; promote to HIGH when the variants differ in behavior (e.g., 3 different retry-backoff curves).
- **Impact:** Inconsistent behavior across the codebase; bug fixes apply only to one variant.
- **Source:** Dijkstra, On the role of scientific thought; SRP / SOLID.

## API-SURFACE [MEDIUM] Export surface exceeds usage

Shallow-module detection (Ousterhout): a module's public interface is large relative to the functionality it provides, or exports exceed what consumers actually import.

- **Detect:** module exporting ≥10 symbols where external consumers import ≤ half of them (count via LSP `findReferences` / grep on import sites); internal modules imported via deep paths bypassing the package's public index; library `package.json` missing an `exports` field (every internal file is de-facto public API).
- **Fix:** narrow the surface — funnel access through a public `index.*`, mark the rest internal; on Node packages add a `package.json` `exports` field to lock down deep imports; propose lint enforcement where ESLint is configured (`no-restricted-exports`, `no-restricted-imports` for deep paths) so the budget holds mechanically.
- **Threshold:** ≥10 exports with ≤50% externally consumed, or any deep-path import bypassing an existing public index.
- **Skip:** published library entry points (their contract is external consumers — apply YAGNI-USAGE skip list), generated code, barrel files that ARE the public index.
- **Confidence:** HIGH for deep-path bypass of an existing index; MEDIUM for export-count ratios (consumers may exist out-of-repo).
- **Impact:** Every needless export is API contract you must maintain and a place complexity leaks; deep modules absorb complexity so consumers don't have to.
- **Source:** Ousterhout, A Philosophy of Software Design (deep modules); ESLint no-restricted-exports; Node package `exports` encapsulation.

## OVERENGINEERING [MEDIUM] Combined SSOT + KISS + YAGNI signals

Alias scope combining the three above. Activate when the user does not want to think about which sub-scope a finding belongs to.

- **Detect:** run SSOT-ARCHITECTURAL + KISS-FIT + YAGNI-USAGE detectors; report findings under the unified `overengineering` label.
- **Threshold:** same per-detector thresholds.
- **Fix:** route to the matching sub-scope's fix pattern.
- **Confidence:** inherit from underlying sub-detector.

## REDUNDANCY [LOW] DRY + duplicate constants

Alias scope combining `dry-pattern` + repeated literal constants (numbers, strings) appearing in ≥3 places without a shared name.

- **Detect:** literal string or numeric constant repeated 3+ times across the codebase.
- **Fix:** introduce a named constant in the owning module; replace all uses.
- **Threshold:** ≥3 occurrences of the same literal in source (excluding tests).
- **Skip:** trivial constants (0, 1, empty string, true, false), test fixture values, generated code.

## OBSOLETE [HIGH] Unreachable / legacy / deprecated paths

Code paths, exports, or APIs that no modern caller reaches.

- **Detect:** unreachable branches (statically provable), legacy import paths preserved for backwards-compat with no remaining caller, `@deprecated` annotations whose alternatives are used everywhere else.
- **Fix:** delete the obsolete path; if there's a published migration window, mark `needs_approval`.
- **Threshold:** unreachable OR 0 modern callers OR explicit `@deprecated` + 90+ days since deprecation.
- **Skip:** intentional fallbacks for platforms/browsers explicitly supported in the project's compat matrix.
- **Confidence:** HIGH for static-unreachable; MEDIUM for deprecated-but-still-imported.
- **Impact:** Maintainers waste time understanding code that is no longer load-bearing.

## DUPLICATE [MEDIUM] Function/module-level duplicate

Alias for `dry-pattern` applied at function or module granularity (rather than statement sequence).

- **Detect:** two or more functions with ≥80% body similarity AND identical/near-identical signatures.
- **Fix:** consolidate into one function with parameterized variants OR delete the redundant copy.
- **Threshold:** ≥2 functions with ≥80% body similarity.
- **Skip:** test helpers intentionally parallel for readability; platform-conditional implementations.
- **Confidence:** HIGH at 95%+ similarity; MEDIUM at 80-95%.

## Cross-scope deduplication

When a single file:line surfaces in multiple meta-quality scopes (e.g., a function flagged as both KISS and YAGNI), apply these rules before reporting:

1. **Same file:line** → merge into one finding, list all matched scopes, keep the highest severity.
2. **Within 10 lines** → merge if the underlying issue is the same (e.g., two adjacent duplicates).
3. **Contradictory findings** (one detector says "delete", another says "extract") → keep the higher-confidence finding, discard the other.

## Anti-overengineering 3-gate (every finding)

Report a finding only when AT LEAST ONE harm signal is present; no signal → silent discard, no flag.

1. **Breaks:** it breaks something — now, or on a predictable path (e.g. drift between duplicated sources).
2. **Misleads:** it misleads a future reader (human or AI) about what is live, canonical, or intended.
3. **Not worth its keep:** the complexity costs more to keep than the value it adds.

In doubt on signal 3 → treat the complexity as worth its keep (that signal does not fire). This wording is canonical — identical in SKILL.md and principles.md §10.

## Confidence-driven reporting

| Confidence | Action |
|------------|--------|
| HIGH | Report unconditionally |
| MEDIUM | Report with `(MEDIUM)` qualifier, route through Apply gate |
| LOW | Discard — do not flood the report with heuristic-only matches |
