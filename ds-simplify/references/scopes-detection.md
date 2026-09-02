# Scope Detection — ds-simplify Phase 2

Per-scope detection steps, evidence format, and proposal for each of ds-simplify's 8 scopes. Loaded when Phase 2 runs.

**Deterministic detector preference (advisory):** for `dead-code` / `orphan` / `single-caller` on JS/TS, Knip binary or config present → run it and use its module-graph output (entry-point-aware, framework-plugin coverage) as the primary evidence; absent → LSP/grep detectors below. Repo configured with ts-prune but not Knip → still run it, but note in the report that ts-prune is officially in maintenance mode and recommend migrating to Knip (~150 framework plugins, entry-point-aware). For Python `dead-code`, Vulture present → run with `--min-confidence 80`; findings at ≥80 confidence enter the table directly, below 80 → flag with confidence noted and hold for Review Each; absent → LSP/grep detectors below. Tool output still passes false-positive prevention and the Phase 4 approval batch — the tool upgrades the detector, never bypasses the gate.

## dead-code

1. Collect all exported symbols (language-specific: `export`, `module.exports`, `pub fn`, `public`, Dart `public` by default).
2. For each export, count references via LSP `findReferences` or `git grep -w {name}`.
3. **String-literal confirmation:** a `git grep` hit inside a comment, a doc (`.md`/`.txt`), or a quoted string literal is not a code reference. Re-run `git grep -w {name} -- '*.{ext}' ':!*.md' ':!*.txt'` and read each match's line — a symbol whose only remaining hits sit inside string literals, comments, or docs is still dead, not a false negative.
4. Reference count (code references only, after step 3) = 0 → finding. Include file:line of export + "zero references" evidence.
5. Skip exports in public API manifests (`exports` in `package.json`, Dart `lib/` public re-exports, `__all__` in Python).
6. **Dead/mismatched parameters:** for each function definition, collect its signature (param names + types); diff against every call site — unused params, extra args at call site, wrong-order params (type-checked only if LSP) → finding with function file:line + caller file:line. A param nothing calls with is dead code at the signature level.

## single-caller

1. Collect internal exports (not in public API).
2. Count references (same string-literal confirmation as dead-code step 3). Count = 1 → finding with caller file:line + "1 reference at {file}:{line}" evidence.
3. Propose: inline at caller, remove export.
4. Skip: recursive helpers, classes with subclasses, trait implementations.

## fallback

Dead/unreachable branches from two sources — backward-compat residue and feature flags whose value never varies. Both end up as the same finding shape (a branch that never executes); scanned together under one scope.

1. **Compat residue:** scan patterns `// @deprecated`, `// backward compat`, `// legacy`, `if ({old-version-check})`, `catch { return null }` with no re-throw, feature detection where feature is guaranteed by minimum runtime version. Each match → finding with file:line + evidence snippet + proposal.
2. **Pre-release residue discipline:** While a product is unreleased with no external consumers, backward-compat shims, redirect residue, and dual-model retention are never required — prefer the cleanest single-canonical resolution; the "breaking change" constraint is void. Shims/redirects genuinely forced during a transition are explicitly time-boxed and removed in the next release. Where tooling exists, seal the no-residue discipline with a mechanical gate (unused-code/knip-class audit) so residue can't re-accumulate. (XR-116; see also Breaking-first in [../../core/principles.md §6](../../core/principles.md))
3. **Dead feature-flag branches:** grep feature-flag references (`process.env.{FLAG}`, `flags.{x}`, `if (config.{x})`). Statically resolvable flags only: the flag's value is a constant across every config source (all env files/`.env.example`, config files, deployment manifests set the same literal; no runtime setter/toggle mechanism exists) → the never-selected branch is dead → finding, evidence = flag name + each config source file:line showing the constant value + "no runtime setter found". Flag value not statically resolvable (remote config, per-tenant, runtime toggle) → skip, never guess runtime behavior.
4. **Stale-flag governance (advisory):** flags are a distinct compounding debt class — for each flag found in step 3, check for lifecycle metadata (owner + expiry date in the flag registry/config/comment; temporary-vs-permanent designation). Temporary flag with no owner/expiry, or whose value has been constant since a git-blame date older than 90 days → advisory finding "stale flag — assign owner+expiry or remove" (industry practice: owner + expiration set at creation, removal automated — Uber's Piranha removed ~2,000 stale flags this way). Advisory only; never delete a flag whose branch is not provably dead under step 3.

## premature-abstraction

1. Find generic containers, base classes, wrappers, higher-order hooks, render props with ≤3 concrete usages.
2. Evidence: abstraction file:line + usage count + file:line of each usage.
3. Proposal: inline usages, drop abstraction.

## quarantine

1. Grep: `// removed`, `// legacy`, `// deprecated`, `// TODO: delete`, `// kill this`, `// unused`, variable `_unused{name}`.
2. Each match → finding with context.

## test-realism (advisory handoff, no local detector)

`/ds-test` present → delegate: emit no local finding for this scope; note in the Phase 3 report `test-realism: covered by /ds-test — run it for fixture-realism analysis`. Absent → gap-note: `test-realism not analyzed — requires /ds-test`.

## ssot-violation

1. Build constant map: string/number literals ≥3 chars appearing in 2+ source files.
2. Filter: exclude test fixtures + framework-expected literals (config keys, HTTP status codes, well-known MIME types).
3. Remaining duplicates → finding. Evidence: each occurrence file:line.
4. Propose: single export location.

## orphan

1. Collect: source files, images, JSON, CSS/SCSS, `.md` files under `docs/` or repo root.
2. Per file, `git grep -n` across tracked files for the filename (with + without extension) and relative path patterns.
3. Zero inbound references → finding.
4. Skip: entry points, config files named by convention (`.eslintrc*`, `tsconfig.json`, etc.), `README.md`, `LICENSE`, `CHANGELOG.md`.
