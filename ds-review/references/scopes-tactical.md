# Optimize Scopes

For concrete Detect/Fix patterns: performance scope uses `rules-performance.md`. Other scopes use pattern-matching described in Focus column — search for those specific patterns in codebase.

Tactical, file-level analysis scopes. 8 scopes, 109 checks.

## Scope Groups

| Group | Scopes |
|-------|--------|
| Security & Privacy | security, robustness, privacy |
| Code Quality | hygiene, types |
| Performance | performance |
| AI Cleanup | ai-hygiene, doc-sync |

## Scope Definitions

| Scope | ID Range | Focus |
|-------|----------|-------|
| security | ds-compliance:SEC-01 to SEC-12 | Secrets, injection, unsafe deserialization, eval, debug endpoints, weak crypto, CORS misconfiguration, path traversal, SSRF, auth bypass |
| hygiene | HYG-01 to HYG-20 | Unused imports/vars/functions, dead code, orphan files, duplicates, stale TODOs, comment quality |
| types | TYP-01 to TYP-10 | Type errors, missing annotations, untyped args, type:ignore without reason, Any in API |
| performance | PRF-01 to PRF-16, NET-01 to NET-09, COST-01 to COST-08 | Response-time/startup targets, bundle size, lazy loading, N+1/pagination, memory leaks, bounded concurrency/pooling, UI rebuild + animation efficiency, cold start (details: rules-performance.md) |
| ai-hygiene | AIH-01 to AIH-08 | Hallucinated APIs, orphan abstractions, over-documented trivial code, dead feature flags, stale mocks |
| robustness | ROB-01 to ROB-10 | Missing timeout/retry, unbounded collections, implicit coercion, missing null checks, resource cleanup |
| privacy | ds-compliance:PRV-01 to PRV-08 | PII exposure/logging, missing masking/consent/retention/audit, insecure PII storage |
| doc-sync | ds-docs:DOC-01 to DOC-08 | README drift, API signature mismatch, deprecated refs in docs, broken links, changelog gaps |

**Delegated scope.** `simplify` (deep nesting, duplicate similar code, unnecessary abstractions, single-use wrappers, complex booleans, test bloat) is not scanned here — ds-simplify present → delegate; absent → one inline dead-export grep (zero cross-file references via a full-text/LSP search) with the gap-note `[simplify] not analyzed — requires ds-simplify`.

## Security — Scanner Augmentation

`gitleaks` present → run `gitleaks detect --no-git -v` and consume its findings; `semgrep` present → run `semgrep --config auto --json` and consume its findings; both present → run both, merge with the SEC-* pass by `file:line`, keep the highest severity on overlap. Neither present → the inline regex pass from [`../../core/secret-patterns.md`](../../core/secret-patterns.md) stands alone (zero-dependency baseline). Never a hard dependency on either tool — absence is noted once in the run summary, not per-finding.

## Check IDs (per scope)

Every scope's checks are individually identified so a run can report exactly which ran. `security` / `privacy` / `doc-sync` list their checks in the owning skill's own rules file (ds-compliance / ds-docs) — cited by ID range in the table above, not restated here. `performance` lists its checks in `rules-performance.md` (PRF-*). The four scopes ds-review owns outright enumerate below; IDs beyond the last row of each table are reserved headroom in the declared range — not yet split into an individually named check, so they fall back to the Focus description above until split out.

### hygiene (HYG-01 to HYG-20)

| ID | Severity | Check |
|----|----------|-------|
| HYG-01 | LOW | Unused imports |
| HYG-02 | LOW | Unused variables |
| HYG-03 | MEDIUM | Unused functions |
| HYG-04 | MEDIUM | Dead code |
| HYG-05 | LOW | Orphan files |
| HYG-06 | MEDIUM | Duplicated code |
| HYG-07 | LOW | Stale TODOs |
| HYG-08 | LOW | Comment quality |

### types (TYP-01 to TYP-10)

| ID | Severity | Check |
|----|----------|-------|
| TYP-01 | HIGH | Type errors |
| TYP-02 | MEDIUM | Missing annotations |
| TYP-03 | MEDIUM | Untyped arguments |
| TYP-04 | LOW | `type: ignore` without a stated reason |
| TYP-05 | MEDIUM | `Any` in public API |

### ai-hygiene (AIH-01 to AIH-08)

| ID | Severity | Check |
|----|----------|-------|
| AIH-01 | HIGH | Hallucinated APIs |
| AIH-02 | MEDIUM | Orphan abstractions |
| AIH-03 | LOW | Over-documented trivial code |
| AIH-04 | MEDIUM | Dead feature flags |
| AIH-05 | MEDIUM | Stale mocks |

### robustness (ROB-01 to ROB-10)

| ID | Severity | Check |
|----|----------|-------|
| ROB-01 | HIGH | Missing timeout |
| ROB-02 | HIGH | Missing retry |
| ROB-03 | MEDIUM | Unbounded collections |
| ROB-04 | MEDIUM | Implicit coercion |
| ROB-05 | HIGH | Missing null checks |
| ROB-06 | MEDIUM | Resource cleanup |

## Score Calculation, Severity & Skip Patterns

One home: [`../../core/severity-score-categories.md`](../../core/severity-score-categories.md). Evidence discipline: every finding cites `file:line`, read actual code before reporting; 3+ examples before concluding a systemic pattern.
