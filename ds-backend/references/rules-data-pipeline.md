# Rules: Data Pipeline

Ingest → clean → merge → store → serve. Applies to batch jobs, schedulers, queue/stream consumers, and script-driven ETL alike. Canonical privacy/regulatory detail belongs to ds-compliance; these rules audit the mechanics.

## Data Pipeline

### DP-01 [HIGH] Unvalidated ingest boundary
External data enters the pipeline without schema/contract validation.
- **Detect:** Ingest job/consumer parses external payloads (API pull, file drop, webhook, queue message) straight into transforms — no schema check, no type coercion rules.
- **Fix:** Validate against an explicit schema at the boundary; reject or quarantine on mismatch. Fail-fast beats corrupt-downstream.
- **Impact:** One malformed upstream batch silently poisons every derived table.
- **Source:** 12-Factor-adjacent boundary validation; OWASP input validation.

### DP-02 [CRITICAL] Non-idempotent job with retry semantics
A job that can be re-run (scheduler retry, manual re-trigger, at-least-once delivery) mutates state additively.
- **Detect:** INSERT-without-key patterns, append-on-rerun, counters incremented per run, no dedup key on queue consumers.
- **Fix:** Upsert on deterministic keys, transactional batch markers, or dedup table keyed on event/batch ID. Verify by running the job twice.
- **Impact:** Every retry duplicates data; totals drift and are near-impossible to repair post hoc.
- **Source:** Idempotency discipline (exactly-once is a lie; dedup is the contract).

### DP-03 [HIGH] Silent record dropping
Bad records are skipped with no trace.
- **Detect:** `try/except: continue` (or equivalent) around per-record processing with no counter, log, or quarantine sink.
- **Fix:** Quarantine path (dead-letter table/topic/dir) + per-run dropped-count in job output. Zero-silent-drop policy.
- **Impact:** Data loss invisible until a consumer notices totals are wrong — weeks later.
- **Source:** Error-ownership principle (W11 applied to data).

### DP-04 [MEDIUM] Missing data-quality checks between stages
Clean → merge transition with no null/duplicate/range assertions.
- **Detect:** Transform chain with no assertion layer; no row-count comparison between stage inputs and outputs.
- **Fix:** Minimal quality gate per critical stage: null-rate threshold, duplicate-key check, value-range check; fail the run loudly on breach.
- **Impact:** Garbage propagates to serving layer and user-facing numbers.
- **Source:** Data-quality gate patterns (assert-early).

### DP-05 [MEDIUM] Order-dependent or non-deterministic merge
Merging sources without deterministic keys/conflict policy.
- **Detect:** Merge relying on processing order, wall-clock arrival, or "last write wins" without a stated tiebreaker.
- **Fix:** Deterministic merge keys + explicit conflict policy (source priority, latest-by-event-time); same inputs → same output, any order.
- **Impact:** Reruns produce different results; debugging becomes archaeology.
- **Source:** Deterministic-output principle (spec §10.4 analog for data).

### DP-06 [MEDIUM] Full reload where increments fit
Every run reprocesses the entire source.
- **Detect:** No watermark/cursor/high-water-mark; job runtime grows linearly with total history.
- **Fix:** Incremental loads on a watermark column/offset; keep a bounded backfill path and a full-reload escape hatch for corruption recovery.
- **Impact:** Runtime and cost grow unboundedly; the job that took minutes takes hours by year two.
- **Source:** Incremental-load patterns.

### DP-07 [HIGH] No retention policy on stored data
Raw/intermediate/derived stores grow forever, PII included.
- **Detect:** No TTL, archival job, or retention statement per store; PII columns replicated into intermediate tables that outlive their purpose.
- **Fix:** Retention policy per store (raw vs derived separated); PII minimized in intermediates — collect nothing you don't need. Canonical GDPR/KVKK erasure handling → ds-compliance.
- **Impact:** Storage cost + breach blast radius + right-to-erasure becomes technically impossible.
- **Source:** Data-minimization principle; GDPR storage-limitation.

### DP-08 [MEDIUM] Unobservable jobs
Pipeline failures discovered by users, not alerts.
- **Detect:** No structured per-job logs, no failure alerting, no freshness/row-count check on critical sinks.
- **Fix:** Structured log line per run (job, duration, rows in/out, status), alert on failure AND on missed schedule, freshness check on serving tables.
- **Impact:** A dead nightly job serves week-old data before anyone notices.
- **Source:** SRE observability baseline.

### DP-09 [LOW] Untraceable lineage
No way to answer "where did this number come from".
- **Detect:** Transforms scattered across scripts with no naming convention, docs, or self-describing structure linking source → transform → sink.
- **Fix:** One lineage statement per sink (sources + transform entry point) in code comments, a README table, or tool-native lineage.
- **Impact:** Every incident starts with re-reverse-engineering the pipeline.
- **Source:** Data-lineage practice.

### DP-10 [HIGH] Backfill without bounds or dry-run
Historical reprocessing that can stampede production stores.
- **Detect:** Backfill scripts with no date-range bounds, no batch size, no dry-run flag, writing directly to serving tables.
- **Fix:** Bounded ranges + batch sizing + dry-run mode + write-to-staging-then-swap for serving tables.
- **Impact:** One backfill saturates the DB and takes the product down with it.
- **Source:** Safe-migration patterns (expand-contract applied to data loads).

### DP-11 [HIGH] Terminal-state guard under at-least-once delivery
State machine driven by an at-least-once queue applies transitions without checking for a prior terminal state.
- **Detect:** Queue/webhook consumer applies state transitions directly; no check whether the job already reached a terminal state (done/error/refunded); duplicate deliveries crash with "invalid state transition".
- **Fix:** Before applying any transition, load current state and skip (no-op, log at debug) if it is already terminal. Treat duplicate and out-of-order deliveries as normal input, not exceptions.
- **Impact:** The first redelivered message after an error state crashes the consumer — and because the message re-queues, it crash-loops.
- **Source:** XR-174 — cross-project experience registry (2026).

### DP-12 [MEDIUM] Queue job resolution survives entry-module aliasing
String-path job resolution (e.g. `main.func`) breaks when the service's entry module isn't named `main` at runtime.
- **Detect:** Queue runner resolves job functions from string module paths; the service can start via different entry points (direct run, WSGI, container cmd) under different module names; new consumer services added without updating the queue-name/job-function contracts SSOT.
- **Fix:** At every service startup, register both the alias (`main`) and the fully-qualified module name in the module registry (`sys.modules` or equivalent) before consuming; keep queue names and job-function strings in one contracts file, updated in the same change that adds any new consumer.
- **Impact:** Jobs enqueue successfully but every dequeue fails module resolution — a silent full-pipeline stall that only appears under the alternate launch mode.
- **Source:** XR-080 — cross-project experience registry (2026).

### DP-13 [MEDIUM] Duplicate-workspace merge: manual canonical pick, documented winner, lock, pairwise
When duplicate canonical roots/workspaces exist, merging follows a fixed policy instead of ad-hoc reconciliation.
- **Detect:** Merge code that auto-picks a canonical workspace; conflicting records resolved by wall-clock or undocumented precedence; concurrent merges unguarded; N-way merges attempted in one pass.
- **Fix:** (1) The owner picks the canonical workspace manually, with the UI showing enough context to decide (created date, record/contact/booking counts, last activity). (2) Conflicting records resolve by one consistent documented policy (cloud-wins / server ordering). (3) Concurrent merge attempts are rejected via a simple lock. (4) Merge scope is strictly pairwise (one canonical + one source); 3+ duplicates resolve through successive pairwise rounds.
- **Impact:** Auto-picked canonicals and N-way merges are how duplicate data becomes silently lost data — unrecoverable and unattributable afterward.
- **Source:** XR-130 — cross-project experience registry (2026).

### DP-14 [HIGH] Client-side retry/work queues bounded by size, retries, and age
Local persistent queues (resubmission, offline work) enforce three bounds to survive crash loops.
- **Detect:** Client-held queue with unbounded item count; items retried without a retry cap; no max-age expiry; expired items' owned resource files never cleaned.
- **Fix:** Enforce (1) max pending items with oldest-first eviction when full, (2) max retry count per item, (3) max item age with pruning — and delete owned resource files during pruning. Log evictions at warning.
- **Impact:** An unbounded queue in a repeated-failure loop is a slow storage leak that eventually kills the app on the user's device.
- **Source:** XR-074 — cross-project experience registry (2026).

### DP-15 [HIGH] Expensive-resource jobs rejected by input cap before retry
Job types consuming scarce resources (GPU, large memory) enforce a fixed input ceiling, rejected as permanently failed before entering retry.
- **Detect:** No input-size ceiling (duration, bytes, rows) on resource-heavy job types; oversized inputs failing with OOM and re-entering the retry loop.
- **Fix:** Define a hard input cap per expensive job type; validate BEFORE the job starts and reject violations with a permanent, non-retryable error stating expected limit vs received size.
- **Impact:** One oversized input in a retry loop re-triggers resource exhaustion on every attempt — a single request can take down the worker fleet repeatedly.
- **Source:** XR-075 — cross-project experience registry (2026).

### DP-16 [MEDIUM] Worker self-restarts after native resource exhaustion
A long-lived single-process worker hitting native/GPU memory exhaustion terminates gracefully after cleanup and lets the process manager restart it clean.
- **Detect:** CUDA/native OOM handled by resetting internal state only; worker continues in a runtime whose fragmented memory is never reliably reclaimed; no `restart: always` (or equivalent) supervision.
- **Fix:** After recovery/cleanup from native resource exhaustion, exit gracefully and rely on the supervisor to start a fresh process with a clean runtime context. When full per-job process forking is too expensive (model reload cost), this restart-on-exhaustion is the preferred middle ground.
- **Impact:** A "recovered" worker on a fragmented native heap fails unpredictably on subsequent jobs — the failure detaches from its cause and becomes undebuggable.
- **Source:** XR-076 — cross-project experience registry (2026).

### DP-17 [HIGH] Sync fidelity: lossless bidirectional field mapping, proven by round-trip
Every field synced with an external system has an internal write path, outbound mapping, inbound mapping, and a schema constant — proven lossless by a round-trip regression test.
- **Detect:** Synced fields missing from the schema/field-list constant; outbound mapping without its inbound counterpart (or vice versa); multi-valued fields (several phones/emails) collapsed to one; no round-trip test (write → sync out → reload → sync in → verify).
- **Fix:** For each synced field, wire all four elements (internal write path, outbound map, inbound map, schema-constant entry) and pin them with a round-trip regression test asserting zero loss in both directions; use the provider's native fields maximally and preserve multi-valued fields.
- **Impact:** A half-mapped field silently truncates user data on every sync cycle — the loss compounds and is usually discovered months later, unrecoverable.
- **Source:** XR-002 — cross-project experience registry (2026).

### DP-18 [HIGH] Concurrent edits reconcile; shared entities derive from one SSOT
Concurrent multi-user edits are reconciled, never silently overwritten, and any shared entity written to multiple targets derives from one canonical SSOT.
- **Detect:** Last-write-wins on concurrent edits with no conflict surfacing; a shared entity (e.g. per-member mirrors of a shared calendar) written to several targets with no designated canonical source.
- **Fix:** Reconcile concurrent edits via server-side ordering (ETag/If-Match/revision) with explicit conflict handling; when an entity fans out to multiple read targets, designate exactly one canonical SSOT and derive all mirrors from it.
- **Impact:** Silent overwrites destroy one user's work whenever two people touch the same record; multi-target writes without a canonical source diverge into contradictory copies.
- **Source:** XR-134 — cross-project experience registry (2026).

### DP-19 [MEDIUM] User intent preserved: stale-revision false conflicts auto-resolve
An explicit user action failing on a stale revision (from the app's own background pull) auto-resolves via refetch→reapply→retry; conflict escalation is reserved for true divergence.
- **Detect:** Explicit user mutations (drag-drop move, form save) surfacing "someone else changed this" errors caused by the client's own stale cached revision; every revision mismatch escalated to a conflict inbox regardless of field-level comparison.
- **Fix:** On revision mismatch after an explicit user action: refetch the current version, reapply the user's intended change, retry. Escalate to the conflict surface only when the remote change touches fields the user's intent actually conflicts with (true field divergence).
- **Impact:** False conflicts train users to ignore the conflict mechanism entirely — so real conflicts get dismissed too, and the reconciliation system loses all value.
- **Source:** XR-135 — cross-project experience registry (2026).

### DP-20 [MEDIUM] Domain objects map to provider-native objects
Every synced domain object (booking, contact, task) maps to a native equivalent in the provider's object model; extensions layer on top of the native core.
- **Detect:** Domain objects synced as opaque blobs or generic records where the provider offers a native type (calendar event, contact card, task); provider-native features (invitations, reminders, dedup) bypassed as a result.
- **Fix:** Map each domain object to the provider's native equivalent and sync to that; layer functionality the provider lacks on top (extended properties, sidecar records) — but keep the core object provider-native.
- **Impact:** Blob-synced objects are invisible to the provider's ecosystem — no native notifications, no cross-app visibility, no interop — quietly forfeiting the main reason to integrate with the provider at all.
- **Source:** XR-147 — cross-project experience registry (2026).

### DP-21 [MEDIUM] Direct provider integration; no broker middle layer
External-service integration (identity, storage, calendar, contacts) is direct per provider — no broker/aggregator layer in between.
- **Detect:** A third-party aggregation/broker service inserted between the app and providers it could integrate directly (unified-API vendors, sync brokers); credentials or user data transiting an intermediary that provides no capability the direct API lacks.
- **Fix:** Integrate each provider directly (e.g. storage to the shared owner store, auth via the provider's own PKCE flow); accept a broker only for a capability that is demonstrably impossible directly, and record that justification.
- **Impact:** A broker adds a second point of failure, a second data processor (privacy/DPA surface), and a dependency whose pricing/API changes can strand the whole integration — while typically lagging the provider's native API.
- **Source:** XR-001 — cross-project experience registry (2026).

### DP-22 [MEDIUM] Derived public surfaces render from the canonical store by reference
Generated customer-facing surfaces (company/marketing site, exports) read data AND assets from the canonical store by reference — no independent copies; the owner selects the displayed field subset.
- **Detect:** A generated site/export holding data absent from the core system; content copied at generation time and edited in place afterward; images/logos duplicated into the generated artifact instead of referenced from the central store; a fixed field set the owner cannot adjust.
- **Fix:** Source every displayed field and asset from the canonical store by reference (addresses resolved at deploy/render time); anything currently living only on the derived surface migrates into the core system; auto-include must-have fields but let the owner add/remove the optional display subset.
- **Impact:** Independently edited derived surfaces fork the truth — the marketing site advertises hours/prices the system no longer has, and nobody knows which is right.
- **Source:** XR-111 + XR-113 — cross-project experience registry (2026).

### DP-23 [MEDIUM] Local client store doubles as a restore source
The local client store (e.g. IndexedDB) is treated as a restore source: workspace data can be re-pushed outward from it after device or remote-store loss.
- **Detect:** Local store treated as disposable cache only; no path to rebuild remote state from a surviving client; restore scenarios assuming the remote store always survives.
- **Fix:** Keep the local store complete enough to re-export workspace data, and implement (and test) the re-push path so either side — device or remote store — can rebuild the other.
- **Impact:** When the remote store is lost (account deletion, provider incident), an intact local copy that cannot be re-exported is data the user can see but never recover.
- **Source:** XR-146 — cross-project experience registry (2026).

### DP-24 [MEDIUM] Schema extends for the concretely-planned future; no speculative integration code
The data model accommodates concretely planned capabilities now (fields, axes, adapter seams), but speculative integration calls stay unwritten until the capability actually starts.
- **Detect:** A concretely roadmapped capability (e.g. online booking + payments) whose schema prerequisites (confirmation axis, hold-until, deposit/currency/pay-link fields, adapter interfaces) are missing — guaranteeing a breaking migration later; OR dead speculative code calling gateways/APIs no feature uses yet.
- **Fix:** Model everything the planned architecture will need in the schema and interfaces today (cheap now, breaking later); implement zero speculative calls against it (YAGNI on behavior, not on shape). Document the boundary: shape is future-proofed, behavior lands with the feature.
- **Impact:** Missing schema seams turn a planned feature into a breaking migration of live data; speculative behavior code rots into untested liability — this rule prices both failure modes correctly.
- **Source:** XR-186 — cross-project experience registry (2026).

### DP-25 [HIGH] Privilege-bound runtimes reserved for privilege-requiring work
A constrained runtime that uniquely holds an ownership/privilege (e.g. scripts executing with owner authority) runs only work that genuinely requires that privilege; plain third-party proxying moves to a general-purpose runtime.
- **Detect:** Pure third-party API proxies (SMS, payment, invoicing) living inside the privileged runtime; the boundary between privileged and general work undocumented; migrations that quietly expand the privileged runtime's job list.
- **Fix:** Keep only privilege-requiring work in the constrained runtime; move privilege-free proxies to a general-purpose, firm-owned runtime (e.g. an edge worker). Lock the boundary with an ADR that also states what is explicitly out of scope (privilege-requiring jobs stay; the primary SSOT does not move).
- **Impact:** Every job added to the privileged runtime runs with authority it doesn't need — one injection or bug in a lowly SMS proxy becomes owner-level compromise.
- **Source:** XR-198 — cross-project experience registry (2026).

### DP-26 [MEDIUM] Singleton system files created only by the owner; drift healed
In a shared provider-store workspace, singleton system files are created exclusively by the owner role; member-created drift is healed in an owner session.
- **Detect:** Any member role able to create singleton system files (config roots, registries, index files); duplicate singletons observed; no integrity-heal step reconciling drift.
- **Fix:** Gate singleton creation to the owner role; members read or propose but never create; detect duplicates/drift and repair via an integrity-heal routine that runs in an owner session (only the owner has authority to consolidate).
- **Impact:** Member-created singletons fork the workspace's system state — two configs, two registries — and every client picks one at random until the workspace visibly splits.
- **Source:** XR-140 — cross-project experience registry (2026).
