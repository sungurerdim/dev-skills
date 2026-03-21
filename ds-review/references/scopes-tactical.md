# Optimize Scopes

For concrete Detect/Fix patterns: performance scope uses `rules-performance.md`. Other scopes use pattern-matching described in the Focus column — the model searches for those specific patterns in the codebase.

Tactical, file-level analysis scopes. 9 scopes, 97 checks.

## Scope Definitions

| Scope | ID Range | Focus |
|-------|----------|-------|
| security | SEC-01 to SEC-12 | Secrets, injection, unsafe deserialization, eval, debug endpoints, weak crypto, CORS misconfiguration, path traversal, SSRF, auth bypass |
| hygiene | HYG-01 to HYG-20 | Unused imports/vars/functions, dead code, orphan files, duplicates, stale TODOs, comment quality |
| types | TYP-01 to TYP-10 | Type errors, missing annotations, untyped args, type:ignore without reason, Any in API |
| performance | PRF-01 to PRF-10 | N+1 queries, blocking in async, large file reads, missing pagination/cache/pool |
| ai-hygiene | AIH-01 to AIH-08 | Hallucinated APIs, orphan abstractions, over-documented trivial code, dead feature flags, stale mocks |
| robustness | ROB-01 to ROB-10 | Missing timeout/retry, unbounded collections, implicit coercion, missing null checks, resource cleanup |
| privacy | PRV-01 to PRV-08 | PII exposure/logging, missing masking/consent/retention/audit, insecure PII storage |
| doc-sync | DOC-01 to DOC-08 | README drift, API signature mismatch, deprecated refs in docs, broken links, changelog gaps |
| simplify | SIM-01 to SIM-11 | Deep nesting (>3), duplicate similar code, unnecessary abstractions, single-use wrappers, complex booleans, test bloat |

## Score Calculation

```
base_score = 100
penalty_per_CRITICAL = -25
penalty_per_HIGH = -10
penalty_per_MEDIUM = -3
penalty_per_LOW = -1

scope_score = max(0, base_score + sum(penalties))
```

Cap rules:
- Any CRITICAL finding → scope score max 40
- 3+ HIGH findings → scope score max 60
- Score never goes below 0

## Severity Levels

| Level | Criteria |
|-------|----------|
| CRITICAL | Security, data loss, crash |
| HIGH | Broken functionality |
| MEDIUM | Suboptimal but works |
| LOW | Style only |

When uncertain, choose lower severity.

## Judgment Rules

| Rule | Detail |
|------|--------|
| Evidence | Every finding cites `file:line`. Read actual code before reporting. |
| Conservative | Uncertain → lower severity. Style → max LOW. Single occurrence → max MEDIUM (except security). |
| Pattern threshold | 3+ examples before concluding systemic pattern. |
| CRITICAL validation | Analyze as "this is a bug" AND "this might be intentional". Both agree → include. Disagree → downgrade. |
| High-severity gate | Before finalizing CRITICAL/HIGH: (1) re-read the file section, (2) check skip patterns, (3) verify not test/mock/fixture context. Any check fails → downgrade one severity level. |

## Skip Patterns

Never flag intentionally marked code: `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING` blocks, platform guards, test fixtures.
