# Optimize Scopes

For concrete Detect/Fix patterns: performance scope uses `rules-performance.md`. Other scopes use pattern-matching described in Focus column — search for those specific patterns in codebase.

Tactical, file-level analysis scopes. 8 scopes, 86 checks.

## Scope Definitions

| Scope | ID Range | Focus |
|-------|----------|-------|
| security | ds-compliance:SEC-01 to SEC-12 | Secrets, injection, unsafe deserialization, eval, debug endpoints, weak crypto, CORS misconfiguration, path traversal, SSRF, auth bypass |
| hygiene | HYG-01 to HYG-20 | Unused imports/vars/functions, dead code, orphan files, duplicates, stale TODOs, comment quality |
| types | TYP-01 to TYP-10 | Type errors, missing annotations, untyped args, type:ignore without reason, Any in API |
| performance | PRF-01 to PRF-10 | Response-time/startup targets, bundle size, lazy loading, N+1/pagination, memory leaks, bounded concurrency/pooling, UI rebuild + animation efficiency, cold start (details: rules-performance.md) |
| ai-hygiene | AIH-01 to AIH-08 | Hallucinated APIs, orphan abstractions, over-documented trivial code, dead feature flags, stale mocks |
| robustness | ROB-01 to ROB-10 | Missing timeout/retry, unbounded collections, implicit coercion, missing null checks, resource cleanup |
| privacy | ds-compliance:PRV-01 to PRV-08 | PII exposure/logging, missing masking/consent/retention/audit, insecure PII storage |
| doc-sync | ds-docs:DOC-01 to DOC-08 | README drift, API signature mismatch, deprecated refs in docs, broken links, changelog gaps |

**Delegated scope.** `simplify` (deep nesting, duplicate similar code, unnecessary abstractions, single-use wrappers, complex booleans, test bloat) is not scanned here — ds-simplify present → delegate; absent → one inline dead-export grep (zero cross-file references via a full-text/LSP search) with the gap-note `[simplify] not analyzed — requires ds-simplify`.

## Score Calculation, Severity & Skip Patterns

One home: [`../../core/severity-score-categories.md`](../../core/severity-score-categories.md). Evidence discipline: every finding cites `file:line`, read actual code before reporting; 3+ examples before concluding a systemic pattern.
