# Severity, Confidence, Score & Categories — the one home

**Consumers:** every skill that produces or consumes findings. No skill re-derives a local scale; two skills labelling a finding CRITICAL under different criteria is the drift this file exists to prevent. Rule files (`references/rules-*.md`) use exactly the vocabulary below.

## Severity

| Level | Meaning | Examples |
|-------|---------|---------|
| **CRITICAL** | Security breach, data loss, or crash in production; legal exposure with a citable mandate | Hardcoded live secret, SQL/command injection, unhandled null on the payment path, PII stored without a lawful basis |
| **HIGH** | Broken or incorrect behavior users hit | Missing authz check, wrong calculation, broken API contract, no timeout on an external call |
| **MEDIUM** | Functional but suboptimal; a predictable future failure | Missing error handling, no pagination, redundant logic, retry without backoff |
| **LOW** | Style, convention, minor improvement | Naming inconsistency, missing comment, formatting |

Extended vocabulary allowed in rule files only: `BLOCKER` (a mandated ship blocker — cites law, store guideline number, or platform requirement inline), `ADVISORY` and `INFO` (never counted toward a score). `MAJOR`/`MINOR` are banned — map to HIGH/MEDIUM.

**CRITICAL requires a second pass.** Before reporting CRITICAL, re-read the site ±20 lines, check skip patterns (below), test fixtures, generated files, env-loader patterns. Insufficient evidence → HIGH. CRITICAL is reserved for confirmed exposure.

## Confidence

Every finding records confidence beside severity.

| Level | Score | Basis |
|-------|-------|-------|
| HIGH | 80-100 | Verified by file read, ≥ 2 evidence points |
| MEDIUM | 50-79 | Pattern match, single evidence point |
| LOW | 0-49 | Heuristic, indirect evidence |

Non-CRITICAL findings below confidence 80 go to a `low-confidence` rollup (count + one-line list in the summary), excluded from the default fix set; the user promotes items individually. CRITICAL below 80 → the second pass above, never dropped.

## Score

```
score = max(0, 100 − 25·CRITICAL − 10·HIGH − 3·MEDIUM − 1·LOW)
Caps: any CRITICAL → max 40; 3+ HIGH → max 60
```

## Skip patterns — never flagged

| Pattern | Meaning |
|---------|---------|
| `# noqa`, `// eslint-disable`, `#[allow(...)]`, `@SuppressWarnings` | Intentional suppression (respect only when the line carries a reason or a rule id) |
| `# intentional`, `# safe:` | Deliberate choice / acknowledged risk |
| `_` prefix on an unused variable | Intentional discard |
| `TYPE_CHECKING` / `if TYPE_CHECKING:` blocks | Type-only imports |
| Platform guards (`if sys.platform`, `#ifdef _WIN32`, `Platform.isIOS`) | OS/env conditional code |
| Test fixtures, snapshot files, recorded cassettes | Test-specific setup |
| Generated files (`generated/`, `*.g.dart`, `*.gen.go`, `*.pb.go`, `*_pb2.py`, auto-generated headers) | Not hand-maintained |

## False-positive prevention

1. Exclude test paths (`test/`, `tests/`, `__tests__/`, `*_test.*`, `*.spec.*`, `*.test.*`) from production-only rules.
2. Read the matching line — a hit inside a comment or a string literal describing the pattern is not a finding.
3. Read 3 lines of context around every match before recording.
4. Honor the skip patterns above.
5. Domain-specific rules add their own exclusions in their rule file.

## Categories

**Fix category** — every action a skill takes on a finding is classified honestly; A is never promoted to B to avoid work, B is never compressed into A to avoid asking.

| Category | Meaning | Default mode | `--ask` |
|----------|---------|--------------|---------|
| **A** (conforms) | Fix conforms to the current agreed architecture/plan — a missing piece, a bug, a violation of a rule the codebase already enforces | Apply | Apply without asking |
| **B** (changes the plan) | Changes architecture, scope, capability, a user-facing promise, or adds/removes a dependency | Apply using the same impact/effort/risk reasoning an approval block would show; record it in the summary; items on the ask-exception list become `needs-human` | One batched approval block: current → proposed, reason, impact, effort, risk, rollback path |

**Finding category** — CAT-1 (conformance: violates a rule, auto-fixable) · CAT-2 (enhancement: user decides). Uncertain → CAT-2.

## Disposition vocabulary

`fixed` · `failed` · `skipped (reason)` · `needs-human (concrete action)` · `needs-approval` (`--ask` only) · `not-applicable (reason)` · `reverted (captured error)` · `low-confidence` · `discarded (no harm signal)`. The summary balances: `fixed + failed + skipped + needs-human + needs-approval + not-applicable + reverted = total`. Every `skipped`/`needs-human` reason passes the reject list in `principles.md` §11.
