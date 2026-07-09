# Rules: Data Pipeline

Ingest → clean → merge → store → serve. Applies to batch jobs, schedulers, queue/stream consumers, and script-driven ETL alike. Canonical privacy/regulatory detail belongs to ds-compliance; these rules audit the mechanics.

## DP-01 [HIGH] Unvalidated ingest boundary
External data enters the pipeline without schema/contract validation.
- **Detect:** Ingest job/consumer parses external payloads (API pull, file drop, webhook, queue message) straight into transforms — no schema check, no type coercion rules.
- **Fix:** Validate against an explicit schema at the boundary; reject or quarantine on mismatch. Fail-fast beats corrupt-downstream.
- **Impact:** One malformed upstream batch silently poisons every derived table.
- **Source:** 12-Factor-adjacent boundary validation; OWASP input validation.

## DP-02 [CRITICAL] Non-idempotent job with retry semantics
A job that can be re-run (scheduler retry, manual re-trigger, at-least-once delivery) mutates state additively.
- **Detect:** INSERT-without-key patterns, append-on-rerun, counters incremented per run, no dedup key on queue consumers.
- **Fix:** Upsert on deterministic keys, transactional batch markers, or dedup table keyed on event/batch ID. Verify by running the job twice.
- **Impact:** Every retry duplicates data; totals drift and are near-impossible to repair post hoc.
- **Source:** Idempotency discipline (exactly-once is a lie; dedup is the contract).

## DP-03 [HIGH] Silent record dropping
Bad records are skipped with no trace.
- **Detect:** `try/except: continue` (or equivalent) around per-record processing with no counter, log, or quarantine sink.
- **Fix:** Quarantine path (dead-letter table/topic/dir) + per-run dropped-count in job output. Zero-silent-drop policy.
- **Impact:** Data loss invisible until a consumer notices totals are wrong — weeks later.
- **Source:** Error-ownership principle (W11 applied to data).

## DP-04 [MEDIUM] Missing data-quality checks between stages
Clean → merge transition with no null/duplicate/range assertions.
- **Detect:** Transform chain with no assertion layer; no row-count comparison between stage inputs and outputs.
- **Fix:** Minimal quality gate per critical stage: null-rate threshold, duplicate-key check, value-range check; fail the run loudly on breach.
- **Impact:** Garbage propagates to serving layer and user-facing numbers.
- **Source:** Data-quality gate patterns (assert-early).

## DP-05 [MEDIUM] Order-dependent or non-deterministic merge
Merging sources without deterministic keys/conflict policy.
- **Detect:** Merge relying on processing order, wall-clock arrival, or "last write wins" without a stated tiebreaker.
- **Fix:** Deterministic merge keys + explicit conflict policy (source priority, latest-by-event-time); same inputs → same output, any order.
- **Impact:** Reruns produce different results; debugging becomes archaeology.
- **Source:** Deterministic-output principle (spec §10.4 analog for data).

## DP-06 [MEDIUM] Full reload where increments fit
Every run reprocesses the entire source.
- **Detect:** No watermark/cursor/high-water-mark; job runtime grows linearly with total history.
- **Fix:** Incremental loads on a watermark column/offset; keep a bounded backfill path and a full-reload escape hatch for corruption recovery.
- **Impact:** Runtime and cost grow unboundedly; the job that took minutes takes hours by year two.
- **Source:** Incremental-load patterns.

## DP-07 [HIGH] No retention policy on stored data
Raw/intermediate/derived stores grow forever, PII included.
- **Detect:** No TTL, archival job, or retention statement per store; PII columns replicated into intermediate tables that outlive their purpose.
- **Fix:** Retention policy per store (raw vs derived separated); PII minimized in intermediates — collect nothing you don't need. Canonical GDPR/KVKK erasure handling → ds-compliance.
- **Impact:** Storage cost + breach blast radius + right-to-erasure becomes technically impossible.
- **Source:** Data-minimization principle; GDPR storage-limitation.

## DP-08 [MEDIUM] Unobservable jobs
Pipeline failures discovered by users, not alerts.
- **Detect:** No structured per-job logs, no failure alerting, no freshness/row-count check on critical sinks.
- **Fix:** Structured log line per run (job, duration, rows in/out, status), alert on failure AND on missed schedule, freshness check on serving tables.
- **Impact:** A dead nightly job serves week-old data before anyone notices.
- **Source:** SRE observability baseline.

## DP-09 [LOW] Untraceable lineage
No way to answer "where did this number come from".
- **Detect:** Transforms scattered across scripts with no naming convention, docs, or self-describing structure linking source → transform → sink.
- **Fix:** One lineage statement per sink (sources + transform entry point) in code comments, a README table, or tool-native lineage.
- **Impact:** Every incident starts with re-reverse-engineering the pipeline.
- **Source:** Data-lineage practice.

## DP-10 [HIGH] Backfill without bounds or dry-run
Historical reprocessing that can stampede production stores.
- **Detect:** Backfill scripts with no date-range bounds, no batch size, no dry-run flag, writing directly to serving tables.
- **Fix:** Bounded ranges + batch sizing + dry-run mode + write-to-staging-then-swap for serving tables.
- **Impact:** One backfill saturates the DB and takes the product down with it.
- **Source:** Safe-migration patterns (expand-contract applied to data loads).
