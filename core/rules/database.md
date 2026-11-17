# DB — schema, queries, migrations, datastore exposure, data jobs

Loaded when the project has a datastore (`db≠none`); jobs, queues and ETL have no signal of their own and ride on the same one. SQL rules carry `applies_when` on a SQL engine. Tenant and object isolation (including row-level security) is AUTH-11; pool sizing NWK-09; backups and their encryption DEP-31; personal-data minimization and retention PRV-03 and PRV-27; HTTP idempotency keys API-07.

### DB-01 [CRITICAL] SQL built from strings
applies_when: db∋postgres or db∋mysql or db∋sqlite or db∋other
- **Detect:** query text assembled by concatenation, `%`/`.format`/f-strings, template literals or `sprintf` with any value not a compile-time constant; ORM raw-query escape hatches (`raw`, `$queryRawUnsafe`, `execute(text(...))`, `whereRaw`) fed with input; identifiers (column, sort order) taken from input without an allow-list.
- **Mech:** T `git grep -nIiE '(execute|query|raw|exec)[a-z_]*\(f.(SELECT|INSERT|UPDATE|DELETE|WITH)|(SELECT|INSERT INTO|UPDATE|DELETE FROM)[^;]*("[[:space:]]*\+|\+[[:space:]]*"|%s?"[[:space:]]*%|\.format\(|\$\{|f")|queryRawUnsafe|executeRawUnsafe|whereRaw\(|Sprintf\("(SELECT|INSERT|UPDATE|DELETE)' -- ':!*.md' ':!*test*'`
- **Fix:** bound parameters for every value; identifiers chosen from an allow-list; the ORM's parameterized API instead of raw strings.
- **Impact:** one injectable query exposes or destroys the whole database.
- **Source:** OWASP A05:2025; OWASP SQL Injection Prevention Cheat Sheet; CWE-89.

### DB-25 [CRITICAL] Datastore reachable or over-privileged
- **Detect:** the application connects as a superuser or owner role (`postgres`, `root`, `sa`, `admin`) or one role does migrations and runtime; credentials with DDL rights used by request handlers; a database, Redis, Mongo or Elasticsearch port bound to `0.0.0.0` or published with no auth (`protected-mode no`, no `requirepass`, `bind_ip_all` without auth); TLS disabled to a database across a network (`sslmode=disable`, `ssl=false`); Firestore or Storage rules with `allow read, write: if true`.
- **Mech:** T `git grep -nIiE '(postgres(ql)?|mysql|mongodb(\+srv)?|redis)://(postgres|root|sa|admin)[:@]|sslmode=disable|ssl[_-]?mode[[:space:]]*[:=][[:space:]]*.?disable|ssl[[:space:]]*[:=][[:space:]]*false|protected-mode no|bind_ip_all|User Id=sa;|allow read, write: if true' -- ':!*.md'` · `git grep -nIE '"?(5432|3306|6379|27017|9200):(5432|3306|6379|27017|9200)' -- '*compose*.y*ml'`
- **Fix:** a runtime role with only the DML rights it needs and a separate migration role; datastores on a private network or loopback with authentication on; TLS with verification for any hop that leaves the host; deny-by-default rules for client-reachable stores.
- **Impact:** an injection or leaked credential becomes full control of the data, and an exposed unauthenticated store is found and wiped by internet scanners within hours.
- **Source:** Least privilege; OWASP Database Security Cheat Sheet; CIS Benchmarks (PostgreSQL, MySQL, MongoDB); CWE-250, CWE-306.

### DB-02 [HIGH] Slow queries not found or not indexed
applies_when: db∋postgres or db∋mysql or db∋sqlite or db∋other
- **Detect:** filters, joins and sorts on unindexed columns of large tables; composite indexes in the wrong column order; `SELECT *` on wide tables in hot paths; no slow-query log or query statistics reviewed (`pg_stat_statements`, MySQL slow log, `EXPLAIN QUERY PLAN` in SQLite); indexes nothing uses.
- **Mech:** M (`EXPLAIN` plans or the engine's query statistics)
- **Fix:** index the columns of the costliest queries by total time (equality columns first, then range or sort); select only used columns; enable the slow-query log at a threshold under the latency budget; drop unused indexes.
- **Impact:** one missing index turns a millisecond lookup into a full scan that grows with the table.
- **Source:** Make it work, right, fast; Winand, *Use The Index, Luke* (use-the-index-luke.com); PostgreSQL docs, Using EXPLAIN.

### DB-06 [HIGH] One query per item (N+1)
- **Detect:** a list query followed by one query per row for related data — lazy relations accessed in a loop, a repository call inside `for`/`map`, GraphQL resolvers without batching; the query log shows the same statement repeated with different IDs.
- **Mech:** M (query log of one list request, or the ORM's N+1 detector: Bullet, nplusone, django-debug-toolbar)
- **Fix:** eager loading (`select_related`/`prefetch_related`, `includes`, `JOIN FETCH`, `include`), one `IN (...)` batch, or a per-request DataLoader.
- **Impact:** response time and database load grow linearly with list length.
- **Source:** Django, SQLAlchemy, Rails and JPA documentation on eager loading.

### DB-03 [HIGH] Migration that locks, loses data or cannot roll back
applies_when: db∋postgres or db∋mysql or db∋sqlite or db∋other
- **Detect:** column drops, renames or type changes shipped in one step while old code still runs; index creation that blocks writes (Postgres without `CONCURRENTLY`); `NOT NULL` or a volatile default added to a large table in one statement; applied migrations edited; no down step, or a down step that silently cannot restore dropped, hashed or scrubbed data and does not say so; schema changed outside the migration tool; a hand-run schema script that fails or duplicates on a second run (`CREATE` without `IF NOT EXISTS`).
- **Mech:** T `find . -path ./node_modules -prune -o -path '*migrat*' -name '*.sql' -print -exec squawk {} +` · `git grep -nIiE '^[[:space:]]*CREATE[[:space:]]+(UNIQUE[[:space:]]+)?(TABLE|INDEX)' -- '*.sql' | grep -viE 'if not exists'`
- **Fix:** expand → backfill → switch reads → contract across releases; engine-safe forms (concurrent index builds, `NOT VALID` then `VALIDATE` constraints); never edit an applied migration; every down step states what it cannot restore; the gate applies all migrations up, down and up again on an empty database.
- **Impact:** a deploy takes the database offline, or a rollback restores the schema while the data is gone.
- **Source:** Reversibility; Idempotency; expand/contract (Fowler, ParallelChange); Squawk (squawkhq.com); PostgreSQL docs, CREATE INDEX CONCURRENTLY.

### DB-20 [HIGH] Wrong data types for money and time
applies_when: db∋postgres or db∋mysql or db∋sqlite or db∋other
- **Detect:** money in `FLOAT`/`DOUBLE`/`REAL`; timestamps without a time zone (`TIMESTAMP` in Postgres, naive datetimes) or with no documented UTC convention; database `ENUM` types for value sets that grow; related records with their own keys stored inside a JSON blob.
- **Mech:** T `git grep -nIiE '(price|amount|total|cost|balance|money|fee)[a-z_]*.{0,30}(float|double|real)([^a-z]|$)|timestamp without time zone|TIMESTAMP[[:space:]]*(,|NOT|NULL|DEFAULT|$)' -- ':!*.md'`
- **Fix:** integer minor units or `NUMERIC`/`DECIMAL` for money; time-zone-aware types or UTC with the convention written in the schema; a lookup table or `CHECK` for growing value sets; normalized tables for related data.
- **Impact:** totals stop matching their line items, and times shift by hours as soon as a second time zone appears.
- **Source:** PostgreSQL docs, Numeric Types and Date/Time Types; Fowler, Money pattern (*PoEAA*).

### DB-21 [HIGH] Invariants enforced only in application code
applies_when: db∋postgres or db∋mysql or db∋sqlite or db∋other
- **Detect:** tables without a primary key; relationships with no foreign key constraint or with an engine-default `ON DELETE`; nullable columns where null has no meaning; uniqueness or ranges the code assumes with no `UNIQUE` or `CHECK`.
- **Mech:** M (schema or migration files)
- **Fix:** a primary key everywhere; declared foreign keys with a deliberate `ON DELETE`; `NOT NULL` by default; `UNIQUE` and `CHECK` constraints for every invariant the code relies on.
- **Impact:** scripts, admin consoles, second services and races write data the application assumes cannot exist.
- **Source:** Defense in depth; PostgreSQL docs, Constraints; CWE-362 (check-then-insert races that a unique constraint closes).

### DB-05 [MEDIUM] Mixed schema naming
applies_when: db∋postgres or db∋mysql or db∋sqlite or db∋other
- **Detect:** camelCase and snake_case mixed in one schema; singular and plural table names mixed; foreign keys not named after the table they reference.
- **Mech:** M (schema or migration files)
- **Fix:** one convention (for example snake_case, plural tables, `<table>_id` foreign keys, `_at` timestamps), applied to new objects and migrated for old ones when touched.
- **Impact:** inconsistent names cause ORM mapping bugs and slow every reader of the schema.
- **Source:** Least astonishment; PostgreSQL docs, Lexical Structure (unquoted identifiers fold to lower case).

### DB-23 [MEDIUM] SQLite left on default pragmas
applies_when: db∋sqlite
- **Detect:** connections opened without `PRAGMA foreign_keys=ON` (foreign keys are not enforced by default, per connection); no `busy_timeout`, so concurrent writers fail with `SQLITE_BUSY`; a concurrently read database still in rollback-journal mode instead of WAL.
- **Mech:** T `git grep -nIiE 'foreign_keys|busy_timeout|journal_mode|sqlite3?\.(connect|open)|openDatabase|new Database\(' -- ':!*.md'`
- **Fix:** on every connection: `foreign_keys=ON`, a `busy_timeout` of a few seconds, `journal_mode=WAL` with `synchronous=NORMAL` where readers and a writer overlap; further tuning only against a measurement.
- **Impact:** declared foreign keys silently do nothing, and readers stall or fail behind every write.
- **Source:** SQLite docs, Foreign Key Support §2; PRAGMA busy_timeout; Write-Ahead Logging.

### DB-24 [MEDIUM] Sensitive columns readable in plaintext
applies_when: pii=yes
- **Detect:** government IDs, financial account numbers, health or biometric data stored in plaintext with only disk encryption; encryption keys stored in the same database or repository as the ciphertext.
- **Mech:** T `git grep -nIiE '(ssn|national_id|tax_id|iban|account_number|diagnos|health|biometric)[a-z_]*' -- '*.sql' '*.prisma' '*models*' '*schema*' '*entity*' '*entities*'`
- **Fix:** application-level or database-function encryption for those columns, keys in a KMS or secret manager, access through a narrow role; hash instead when the value is only matched, never read back.
- **Impact:** disk encryption does not stop an injection, an over-privileged role or a careless dump from reading the values.
- **Source:** Defense in depth; OWASP Cryptographic Storage Cheat Sheet; GDPR Art. 32(1)(a); PostgreSQL pgcrypto.

### DB-16 [HIGH] User data changed or deleted by paths the user cannot see or undo
applies_when: pii=yes or ui≠none
- **Detect:** cleanup, sync reconciliation, orphan removal or TTL jobs that hard-delete user-created records without a stated retention rule; bulk edits or deletes that skip the audit trail single edits write, or that can only be reverted record by record.
- **Mech:** M (scheduled jobs, sync and bulk-operation code)
- **Fix:** hard deletion only on an explicit user request, a stated retention rule (PRV-27) or erasure; background routines archive or flag instead; bulk mutations share a batch ID in the audit trail and revert as one unit.
- **Impact:** an overzealous job or one mis-scoped bulk edit destroys user work with no record and no recovery.
- **Source:** Reversibility; GDPR Art. 5(1)(f) (protection against accidental loss); OWASP Logging Cheat Sheet (data changes).

### DP-02 [CRITICAL] Re-runnable job or consumer that is not idempotent
- **Detect:** jobs, consumers or webhook handlers that can run twice (scheduler retry, manual re-run, at-least-once delivery) and insert without a key, append, increment counters or apply state transitions without checking the current state; duplicate or out-of-order delivery crashing a consumer that then re-queues forever.
- **Mech:** T `git grep -nIiE 'consume|subscribe|on_message|@task|@job|worker|cron|schedule' -- ':!*.md' ':!*test*'`
- **Fix:** upsert on deterministic keys or a processed-event table keyed by event or batch ID; skip transitions out of a terminal state as a no-op; prove it by running the job twice on the same input.
- **Impact:** every retry duplicates data or crash-loops the consumer, and totals drift beyond repair.
- **Source:** Idempotency; Kleppmann, *Designing Data-Intensive Applications* (ch. 11, idempotence); AWS SQS docs, at-least-once delivery.

### DP-03 [HIGH] Bad records dropped silently
- **Detect:** per-record `try/except: continue` (or equivalent) with no counter, log or dead-letter sink; a job that reports success while skipping rows.
- **Mech:** T `git grep -nIE -A2 'except[^:]*:|catch[[:space:]]*\(' -- '*.py' '*.js' '*.ts' '*.java' '*.kt' '*.cs' | grep -E 'continue|pass$'`
- **Fix:** a quarantine (dead-letter table, topic or directory) and a dropped-count in the run's output; fail the run above a threshold.
- **Impact:** data loss stays invisible until a consumer notices wrong totals weeks later.
- **Source:** Fail fast; Enterprise Integration Patterns, Dead Letter Channel (Hohpe & Woolf).

### DP-15 [HIGH] Permanent failures retried
- **Detect:** jobs retried on errors that cannot succeed (input over a size cap, validation failure, out-of-memory on an oversized input); expensive job types with no input-size ceiling checked before start; no dead-letter queue after the retry limit.
- **Mech:** M (queue and retry configuration)
- **Fix:** classify errors as transient or permanent; check input size before an expensive job starts and fail permanently with expected vs received; cap retries and move failures to a dead-letter queue.
- **Impact:** one oversized input re-triggers resource exhaustion on every attempt and can take down the whole worker fleet.
- **Source:** Fail fast; CWE-770; AWS SQS docs, dead-letter queues.

### DP-14 [HIGH] Local work queue unbounded
applies_when: ui≠none
- **Detect:** a client-side persistent queue (offline writes, upload retries) with no maximum item count, retry cap or item age; files owned by expired items never deleted.
- **Mech:** M
- **Fix:** cap items (evict oldest with a warning), retries per item and item age; delete owned files when an item is pruned.
- **Impact:** a repeated-failure loop fills the device's storage until the app fails.
- **Source:** CWE-770 (allocation without limits).

### DP-18 [HIGH] Concurrent edits overwrite each other
applies_when: api≠none
- **Detect:** updates written last-write-wins with no revision check where two users or devices can edit one record; a record mirrored to several targets with no designated source of truth.
- **Mech:** T `git grep -nIiE 'If-Match|ETag|version[_ ]?(column|field)|optimistic|@Version|lock_version|rowversion' -- ':!*.md'`
- **Fix:** optimistic concurrency (a version column or `ETag`/`If-Match`, `412` on mismatch); on a mismatch caused by the client's own stale copy, refetch, reapply and retry, and surface a conflict only on real divergence; derive mirrors from one canonical record.
- **Impact:** one user's work silently disappears whenever two edits overlap.
- **Source:** DRY / single source of truth; RFC 9110 §13 (conditional requests); Fowler, Optimistic Offline Lock (*PoEAA*).

### DP-04 [MEDIUM] No data-quality check between stages
- **Detect:** transform chains with no null-rate, duplicate-key or range assertion and no row-count comparison between stage input and output.
- **Mech:** M
- **Fix:** a small assertion gate per critical stage (nulls, duplicates, ranges, counts) that fails the run loudly.
- **Impact:** bad data propagates into reports and user-facing numbers.
- **Source:** Fail fast; dbt docs, data tests; Great Expectations (expectations as assertions).

### DP-05 [MEDIUM] Merge result depends on processing order
- **Detect:** merges relying on arrival order, wall-clock time or last-write-wins with no stated tiebreaker.
- **Mech:** M
- **Fix:** deterministic merge keys and an explicit conflict policy (source priority, latest by event time); same inputs give the same output in any order.
- **Impact:** reruns produce different results and debugging becomes guesswork.
- **Source:** Kleppmann, *Designing Data-Intensive Applications* (ch. 5, conflict resolution).

### DP-06 [MEDIUM] Full reload where an increment fits
- **Detect:** every run reprocesses the whole source; no watermark, cursor or offset; runtime growing with total history.
- **Mech:** M (job code and run durations)
- **Fix:** incremental loads on a watermark, plus a bounded backfill path and a full-reload escape hatch for recovery.
- **Impact:** runtime and cost grow without bound.
- **Source:** Kimball Group, incremental ETL loading (change data capture).

### DP-10 [HIGH] Data-changing script without bounds, dry run or backup
- **Detect:** backfill, reprocessing, data-fix or cleanup scripts with no date range, no batch size, no dry-run mode, writing straight into serving tables, or updating or deleting rows with no backup, snapshot or reversible copy taken first.
- **Mech:** M
- **Fix:** bounded ranges, batching with pauses, a dry-run flag, write to staging and swap; snapshot or copy the affected rows before a destructive fix.
- **Impact:** one backfill saturates the database and takes the product down.
- **Source:** Reversibility; expand/contract applied to data loads (Fowler, ParallelChange).

### DP-08 [MEDIUM] Jobs fail without anyone noticing
- **Detect:** no per-run record (job, duration, rows in and out, status); no alert on failure or on a missed schedule; no freshness check on tables that users read.
- **Mech:** M
- **Fix:** one structured log line per run, an alert on failure and on a missed run (dead-man switch), a freshness check on serving tables.
- **Impact:** a dead nightly job serves stale data for days.
- **Source:** Fail fast; Google SRE Book, Monitoring Distributed Systems.

### DP-09 [LOW] Number with no traceable lineage
- **Detect:** no way to tell which sources and transforms produce a serving table or report figure.
- **Mech:** M
- **Fix:** one lineage statement per sink (sources and transform entry point) in code, a README table or the tool's lineage view.
- **Impact:** every data incident starts with reverse-engineering the pipeline.
- **Source:** OpenLineage specification (openlineage.io).
