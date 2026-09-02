# Invariant patterns — the catalog Invariant Mode classifies against

Consumed by SKILL.md **Invariant Mode** steps 2 (classify) and 4 (generate). Nine patterns,
every one distilled from a gate running in a production repo (verified 2026-08-12; sources
named per pattern — project + file, so the skeleton can be traced to a live original).
Each entry: **when** it applies · **skeleton** the generated gate follows · **red-proof**
form · **wiring** point. The cross-cutting rules at the end apply to every pattern.

## Classification table

Match the user's description to the FIRST row whose shape fits; two rows fitting → the
more specific one (P8 before P9, P1 before P6).

| Description shape | Pattern |
|-------------------|---------|
| "these two constants/values must stay equal across layers" | P1 mirror-constant equality |
| "X was removed and must never come back" / "pattern X must never appear under Y" | P2 absence invariant |
| "this generated file must stay in sync with its source" | P3 generated-file sync |
| "token/style X is forbidden in user-facing text" | P4 denylist |
| "this discovered set must never fall below N" | P5 inventory floor |
| "what the docs declare must equal what the code does" | P6 declaration↔reality match |
| "the suite must pass regardless of execution order" | P7 order-independence |
| "these two implementations must produce identical output" | P8 parity |
| "every implementation of this interface passes the same tests" | P9 shared contract suite |

## P1 — Mirror-constant equality

- **When:** one value is duplicated in two layers that cannot import each other (client
  constant ↔ server copy, config ↔ code, two build targets) and silent divergence is the
  failure.
- **Skeleton:** a test (not a script — the value pair is usually reachable from the test
  runner) that reads BOTH definitions from their real files — parse or regex the source,
  never re-declare the expected value in the test — and asserts equality. Re-declaring the
  value creates a third copy, which is the disease, not the cure.
- **Red-proof:** change one copy in a fixture/scratch tree → test red; revert → green.
- **Wiring:** lands in the suite the entry point already runs — wiring is inherited.
- **Live source:** akis #494 — `DEFAULT_SLOT_MINUTES` duplicated in client JS and Apps
  Script; an equality test pinned the pair after they drifted.

## P2 — Absence invariant

- **When:** a capability/dependency/pattern was deliberately removed and can seep back one
  file at a time (a dependency reinstalled, a config key re-added). A removed capability
  does not lose its test — the test becomes an absence invariant.
- **Skeleton:** two failure shapes, both blocking: **structural** (forbidden files exist,
  forbidden manifest keys/deps present — exact paths and keys enumerated in the gate) and
  **textual** (forbidden marker strings in live files). Markers are deliberately narrow —
  name something only the removed chain produces, never a bare word that substring-matches
  innocent code. Historical records (changelogs, archives) are exempt **by name, with the
  reason stated in the gate** — provenance must stay readable.
- **Red-proof:** re-create one forbidden file (or re-add the manifest key) in a scratch
  worktree → red. Assemble the violation payload at runtime (`${'FORBIDDEN'}+${'_KEY'}`) —
  a literal payload in a repo-wide-scanned fixture file trips the gate on a clean tree.
- **Wiring:** the repo's aggregate audit command, else the quality entry point.
- **Live source:** akis `scripts/audit-no-ota.mjs` — the dismantled OTA update chain
  (10 removed layers) held out of the tree by one gate wired into `audit:all`.

## P3 — Generated-file sync

- **When:** a committed artifact is produced by a generator from a source file
  (localizations from ARB, a panel from TOML, an SRI manifest from dist) and editing the
  source without regenerating is silent — the build stays green, the output is stale.
- **Skeleton:** run the real generator against the current source, diff the result against
  the committed copy, restore the tree on exit (non-destructive: the gate reports staleness,
  never fixes it). Accept the compare-target directory as an argument so the same script
  serves production runs and red-proof fixtures.
- **Red-proof:** point the gate at a fixture copy with one stale line → red. Strongest
  form: a suite test that does this on every run, so the catch is re-proven continuously.
- **Wiring:** pre-commit for the cheap diff; the entry point for the full regenerate.
- **Live source:** SafeScribeAI/app `tool/check_l10n_fresh.sh` — ARB ↔ generated
  `app_localizations*.dart`, restore-on-exit, fixture-dir mode exercised by
  `test/gates_test.dart` on every suite run.

## P4 — Denylist

- **When:** a specific token/character/claim is banned from a defined surface (em-dash in
  UI strings, a once-shipped false marketing claim, a banned API call). A permanent
  known-false-claims denylist scanned at commit/push time by whichever enforcement arm is
  wired (XR-094) is the claims-specific instance of this pattern.
- **Skeleton:** grep the declared scope for each denylist entry; every entry carries its
  rationale as a comment beside it ("separate entries go here, each with its reason"); the
  failure message names the fix, not just the hit. The list only grows — an entry is
  removed only with the owner decision that added it reversed.
- **Red-proof:** fixture file containing exactly one banned token, scanned via the
  parameterized scope argument → red.
- **Wiring:** the before-commit arm (fast, staged files) plus the entry point (full scope).
- **Live source:** SafeScribeAI/app `tool/check_text_style.sh` — U+2014 banned in ARB
  strings, rationale in-file, fixture-dir mode proven by `test/gates_test.dart`.

## P5 — Inventory floor

- **When:** a gate DISCOVERS its input set by walking the tree (bindings, modules, keys,
  registered checks) — and a broken walk returns an empty set that every assertion
  trivially passes. Green-over-nothing is this pattern's target failure.
- **Skeleton:** after discovery, assert `count >= FLOOR` where FLOOR = today's known count,
  stated with its date in a comment. The floor is a tripwire for a broken walk, not a
  target — raise it when inventory legitimately grows; a red floor means "the walk broke
  or something was deleted: look", never "delete the assertion".
- **Red-proof:** point the discovery at an empty/renamed directory → red on the floor,
  proving the gate cannot pass over nothing.
- **Wiring:** inline inside the discovering gate itself — the floor is not a separate
  check but a mandatory property of every discovery-based gate (see cross-cutting rules).
- **Live source:** akis `scripts/audit-kv-disclosure.mjs` (`MIN_BINDINGS = 3` — "a broken
  walk cannot report 'all disclosed' over an empty set"); same guard in the repo's
  `audit-yaml.mjs` and `audit-csp-completeness.mjs`.

## P6 — Declaration↔reality match

- **When:** a human-facing document declares a list of facts the code embodies (privacy
  disclosures naming data stores, README naming supported platforms, a compliance doc
  naming scopes) and the two drift independently. Highest stakes when downstream documents
  are BUILT from the declaration.
- **Skeleton:** derive the reality side from code — never type it into the gate (whatever
  the code dereferences is what exists) — then check BOTH directions: every real item is
  declared in every listed document (coverage), and every declared item is real (no
  orphans — a stale declaration is its own false statement). Add per-item content rules
  when the declaration has legal shape (e.g. each mention must carry a retention period).
- **Red-proof:** two mutations, one per direction: add a code-side item the docs miss →
  red; add a doc-side item the code lacks → red.
- **Wiring:** aggregate audit command; if the docs feed a build, also the build.
- **Live source:** akis `scripts/audit-kv-disclosure.mjs` — three Cloudflare KV namespaces
  vs six disclosure documents, coverage + no-orphans + retention-on-the-same-line, list
  derived from `env.KV_*` dereferences under `functions/`.

## P7 — Order-independence

- **When:** tests share process state (module caches, memoized globals, singletons) and
  pass only in discovery order — the classic source of "re-run it, it's fine" flakes.
- **Skeleton:** run the SAME discovery the normal suite uses, reversed (or shuffled with a
  printed seed) — same tests, only the order differs, so a red is attributable to order
  alone. Pair with a central state-reset registry: every known cache/global registered in
  one place, cleared around each test; a new cache joins the registry in the change that
  introduces it (an inventory-floor guard on the registry keeps it complete, per P5).
- **Red-proof:** a fixture pair where test A poisons a cache test B reads → reversed run
  red, normal run green.
- **Wiring:** the entry point's test step, or pre-push when the double run is slow —
  a documented-but-manual reversed run is unwired and counts as absent (ds-review TST-14).
- **Live source:** trade `tests/onbellek.py --ters` — reversed `unittest` discovery over
  the identical test set, plus the `ONBELLEKLER` central cache registry.

## P8 — Parity

- **When:** two implementations of the same computation coexist (optimized vs reference,
  numba vs pure Python, new vs legacy during migration) and the fast path silently
  diverging from the truth path is the failure.
- **Skeleton:** run both implementations over the FULL declared input matrix (every
  combination, not a sample — name the matrix in the gate) and compare output at the
  strictest level the domain allows: byte-for-byte first, documented tolerance only with
  the reason beside it. Default flags ≠ full matrix: a parity gate that runs one
  configuration certifies one configuration.
- **Red-proof:** perturb one branch of one implementation in a scratch copy → red.
- **Wiring:** first step of the run/release pipeline — parity gates the expensive work.
- **Live source:** trade `scripts/parity_gate.py --all` — 3 symbols × all exits × all
  entries, byte-level, wired as step 1 of `run_v5.py`.

## P9 — Shared contract suite

- **When:** N implementations stand behind one abstraction (adapters, strategies, storage
  backends) and each has drifted toward its own copied-and-loosened test set. P8 parity is
  the N=2, whole-output special case of this pattern.
- **Skeleton:** ONE test set encoding the abstraction's behavioral contract, parameterized
  over implementations; every implementation passes it **unchanged** — a per-implementation
  copy or a relaxed variant is not a contract. Adding an implementation means passing the
  existing suite, never widening it; an implementation that cannot pass does not go behind
  the abstraction.
- **Red-proof:** a deliberately non-conforming stub implementation run through the suite →
  red, proving the contract binds.
- **Wiring:** the entry point's test step; the parameterization list is discovery-based
  where possible, with a P5 floor so a dropped implementation cannot silently leave.
- **Live source:** trade `scripts/parity_gate.py` + `tests/test_numba_parity.py` as the
  N=2 instance; the general form is this catalog's extrapolation of it (no wider live
  instance yet — say so if asked, per Grounded Specifics).

## Cross-cutting rules (every generated gate)

1. **Scope is declared and non-empty** (ds-review TST-13): the gate names the set it scans
   (explicit paths/globs, or a printed file count), exits red on zero files matched, and —
   for repo-wide rules — compares its scope against `git ls-files` so new directories join
   the scan or break the gate. Deliberate narrowing is stated beside the scope with its
   reason.
2. **Discovery gets a floor** (P5 applies inside every other pattern): any gate that walks
   the tree to find its inputs asserts a minimum count.
3. **Exemptions by name, with reason, in the gate file** — never a bare skip.
4. **Non-destructive:** a gate reports; it never rewrites the tree it scans (restore-on-exit
   when it must touch files, as P3 does).
5. **Red-proof forms, strongest first** (ds-review TST-11 — a gate is only enforcing
   something if a fixture exists that makes it fail):
   - **parameterized scope** — the gate accepts its scan target as an argument and a suite
     test aims it at a violating fixture on every run (SafeScribeAI/app `test/gates_test.dart`);
   - **mutation registry** — one violation spec per gate, applied to a throwaway
     worktree/copy by a runner that requires non-zero exit; a spec that no longer applies
     is a hard error, never a skip (akis `scripts/audit-mutations.mjs`); assemble payloads
     at runtime so the registry file cannot trip the gates it feeds;
   - **one-time green→red→green** at delivery (SKILL.md Phase 5 form) — the floor, used
     only when neither standing mechanism exists in the repo.
6. **Exit code propagates** (ds-review TST-14): the chain step that calls the gate fails
   when the gate fails; a discarded return value is an unwired gate.
