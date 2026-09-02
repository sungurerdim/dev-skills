# Rules: Database Design & Operations

Rules for audit/design/spec modes. Each rule: ID, severity, detect pattern, fix action, source.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Database** | DB-01 to DB-19 (3 CRITICAL, 6 HIGH, 9 MEDIUM, 1 LOW) | ~12 |

---

## Database

### DB-01 SQL Injection Prevention [CRITICAL]

**Detect:** String concatenation or template literals used to build SQL queries. Raw user input interpolated into query strings.

```
# Vulnerable patterns
query = "SELECT * FROM users WHERE id = " + user_id
query = f"SELECT * FROM users WHERE email = '{email}'"
db.query(`SELECT * FROM users WHERE name = '${name}'`)
```

**Fix:** Use parameterized queries or prepared statements exclusively. ORMs handle this by default.

**Multi-stack examples:**

- **Node:** `db.query('SELECT * FROM users WHERE id = $1', [userId])` (pg), Knex/Prisma/Drizzle
- **Python:** `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`, SQLAlchemy ORM
- **Go:** `db.Query("SELECT * FROM users WHERE id = $1", userID)` (database/sql)
- **Java/Spring:** `JdbcTemplate.query("SELECT * FROM users WHERE id = ?", userId)`, JPA/Hibernate
- **Ruby/Rails:** `User.where(id: user_id)` (ActiveRecord parameterizes automatically)
- **PHP/Laravel:** `DB::select('SELECT * FROM users WHERE id = ?', [$userId])`, Eloquent ORM

**Why:** SQL injection remains top-3 web vulnerability (OWASP Top 10). Single unparameterized query can expose or destroy entire database.

**Source:** [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html), [database-design-guide.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/database-design-guide.md) Schema Design section

---

### DB-02 Index Strategy [HIGH]

**Detect:** Queries filtering, sorting, or joining on unindexed columns. `EXPLAIN ANALYZE` shows `Seq Scan` on large tables. Missing composite indexes for multi-column WHERE clauses.

**Fix:** Add indexes matching `WHERE`, `ORDER BY`, `JOIN`, and `GROUP BY` patterns.

| Index Type | Best For | Example |
|------------|----------|---------|
| B-tree | Equality, range, sorting | `CREATE INDEX idx_orders_date ON orders(created_at)` |
| Composite | Multi-column lookups | `(user_id, created_at DESC)` — high selectivity first |
| Partial | Subset queries | `WHERE status NOT IN ('cancelled', 'delivered')` |
| GIN (PG) | JSONB, arrays, full-text | `USING gin(tags)` |
| BRIN (PG) | Append-only time-series | 100-1000x smaller than B-tree |
| Covering | Index-only scans | `INCLUDE (name, email)` avoids table lookups |

Column order matters in composite indexes: leftmost prefix queries are served. Monitor unused indexes via `pg_stat_user_indexes` and remove to reduce write overhead.

**Why:** Missing indexes are most common cause of slow queries. Single index addition can reduce query time from seconds to milliseconds.

**Source:** [Use The Index, Luke](https://use-the-index-luke.com/), [database-design-guide.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/database-design-guide.md) Indexing section

---

### DB-03 Migration Safety [HIGH]

**Detect:** Column drops, renames, or type changes deployed without safety period. Migrations that acquire exclusive locks on large tables.

**Fix:** Use expand-contract pattern for all destructive changes:

1. **Expand:** Add new column/table alongside old. Deploy code that writes to both.
2. **Migrate data:** Backfill existing rows.
3. **Switch reads:** Update application to read from new structure.
4. **Contract:** Drop old column/table after verification period.

| Operation | Safe? | Notes |
|-----------|-------|-------|
| `ADD COLUMN` (nullable, no default) | Safe | Metadata-only in PG |
| `ADD COLUMN ... DEFAULT x` | Safe (PG 11+) | Rewrites table in older PG/SQLite |
| `DROP COLUMN` | Dangerous | Use expand-contract |
| `ALTER COLUMN TYPE` | Dangerous | May rewrite and lock table |
| `CREATE INDEX` | Dangerous | Use `CONCURRENTLY` in PG |
| `ADD NOT NULL` | Dangerous | Fails if NULLs exist; add CHECK first |

Migrations immutable once applied to shared environment. Every `up` has corresponding `down`. PG DDL is transactional; MySQL and SQLite are not.

Lint migrations in CI: **Squawk** — free Postgres migration linter (flags `CREATE INDEX` without `CONCURRENTLY`, column adds with volatile defaults, other lock hazards). Alternative: **Atlas** schema-as-code with 50+ built-in analyzers — `atlas migrate lint` moved out of the free tier in October 2025; verify current licensing before adopting, or stay on Squawk.

**Why:** Unsafe migrations cause downtime, data loss, or long-held table locks that block all queries.

**Source:** [Zero-Downtime PostgreSQL Migrations](https://www.braintreepayments.com/blog/safe-operations-for-high-volume-postgresql/), [Squawk](https://squawkhq.com/), [Atlas](https://atlasgo.io/versioned/lint), [database-design-guide.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/database-design-guide.md) Migration Strategies section

---

### DB-04 Connection Pooling [HIGH]

**Detect:** Application creates new database connection per request. Connection count approaches or exceeds `max_connections`. `pg_stat_activity` shows many idle connections.

**Fix:** Use bounded connection pool with appropriate min/max/idle settings.

| Setting | Solo/Dev | Production |
|---------|----------|------------|
| Pool size | 5-10 | 10-25 per instance |
| Idle timeout | 30s | 10-30s |
| Connection lifetime | 30 min | 30 min |
| External pooler | Optional | PgBouncer (transaction mode) |

Pool size rule of thumb: `(2 * CPU cores) + 1` for NVMe storage. Keep total connections under `max_connections - 10`.

**Multi-stack examples:**

- **Node:** `pg` pool with `max: 10, idleTimeoutMillis: 30000`, or Prisma connection pool
- **Python:** SQLAlchemy `create_engine(pool_size=10, max_overflow=5, pool_recycle=1800)`
- **Go:** `sql.DB` with `SetMaxOpenConns(25)`, `SetMaxIdleConns(10)`, `SetConnMaxLifetime(30m)`
- **Java/Spring:** HikariCP with `maximumPoolSize=25`, `idleTimeout=30000`

**Why:** Unbounded connections exhaust database resources and cause cascading failures under load.

**Source:** [PgBouncer docs](https://www.pgbouncer.org/), [HikariCP](https://github.com/brettwooldridge/HikariCP), [database-design-guide.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/database-design-guide.md) ORM Patterns section

---

### DB-05 Schema Naming [MEDIUM]

**Detect:** Mixed naming conventions: camelCase and snake_case in same schema, mixed singular/plural table names, inconsistent FK naming.

**Fix:** Adopt and enforce one convention project-wide:

| Element | Convention | Example |
|---------|-----------|---------|
| Tables | `snake_case`, plural | `user_accounts`, `order_items` |
| Columns | `snake_case`, singular | `created_at`, `email_address` |
| Primary keys | `id` or `<table>_id` | `id`, `user_account_id` |
| Foreign keys | `<ref_table_singular>_id` | `order_id`, `user_id` |
| Indexes | `idx_<table>_<columns>` | `idx_orders_user_id_created_at` |
| Constraints | `<type>_<table>_<column>` | `uq_users_email`, `chk_orders_total` |
| Booleans | `is_` or `has_` prefix | `is_active`, `has_verified_email` |
| Timestamps | `_at` suffix | `created_at`, `deleted_at` |

Consistency matters more than which specific style is chosen.

**Why:** Inconsistent naming increases cognitive load, causes ORM mapping bugs, and makes schema exploration harder.

**Source:** [PostgreSQL naming conventions](https://www.postgresql.org/docs/current/sql-syntax-lexical.html), [database-design-guide.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/database-design-guide.md) Schema Design section

---

### DB-06 N+1 Prevention [MEDIUM]

**Detect:** Query logging shows 1 query for list followed by N queries for related data (one per item). `pg_stat_statements` reveals high-frequency, low-cost queries with same pattern.

**Fix:** Use eager loading, JOINs, or batch queries to fetch related data in one round trip.

**Multi-stack examples:**

- **Node/Prisma:** `include: { posts: true }` or `findMany` with relations
- **Node/GraphQL:** `DataLoader` for batched resolution per request
- **Python/Django:** `select_related()` (FK JOIN) and `prefetch_related()` (separate batch query)
- **Python/SQLAlchemy:** `joinedload()` or `selectinload()` relationship options
- **Ruby/Rails:** `includes(:posts)` (auto-selects strategy) or `eager_load(:posts)` (LEFT JOIN)
- **Java/JPA:** `@EntityGraph` or `JOIN FETCH` in JPQL
- **Go:** Raw SQL with `JOIN` or batch `WHERE id IN (...)`

Detection tools: `django-debug-toolbar`, `bullet` (Ruby), `laravel-query-detector`, `sqlcommenter`.

**Why:** N+1 queries turn single page load into hundreds of database round trips, degrading response time linearly with data size.

**Source:** ORM documentation (Django, SQLAlchemy, ActiveRecord, JPA), [database-design-guide.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/database-design-guide.md) ORM Patterns section

---

### DB-07 Backup Strategy [MEDIUM]

**Detect:** Production database without automated backup configuration. Backups that have never been test-restored.

**Fix:** Implement 3-2-1 rule: **3** copies, **2** storage types, **1** offsite.

| Frequency | Method | Retention |
|-----------|--------|-----------|
| Continuous | WAL archiving (PG) / Litestream (SQLite) | 7 days |
| Daily | `pg_dump` or `.backup` | 30 days |
| Weekly | Full backup offsite | 90 days |
| Before migration | Manual snapshot | Until verified |

Backup commands:
```bash
# PostgreSQL daily backup
pg_dump -Fc --compress=zstd:3 -f "backup_$(date +%Y%m%d).dump" "$DATABASE_URL"

# SQLite continuous replication
litestream replicate mydb.sqlite s3://my-bucket/mydb
```

Automate everything. Test restores monthly. Take backup before any destructive migration.

**Why:** Untested backups = no backups. Data loss from hardware failure, migration errors, or accidental deletion requires proven restore procedures.

**Source:** [AWS RDS backup docs](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html), [pg_dump best practices](https://www.postgresql.org/docs/current/app-pgdump.html), [database-design-guide.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/database-design-guide.md) Backup and Recovery section

---

### DB-08 Database Selection [LOW]

**Detect:** Database chosen without evaluating requirements, or PostgreSQL/MySQL used where SQLite suffices (or vice versa).

**Fix:** Use this decision matrix:

| Scenario | Recommended DB | Rationale |
|----------|---------------|-----------|
| Prototype, side project, < 100 users | SQLite | Zero setup, single file, sufficient for low concurrency |
| Production web app, transactions, complex queries | PostgreSQL | MVCC, JSONB, extensions, PostGIS, streaming replication |
| Existing MySQL stack, shared hosting | MySQL | Compatibility, ecosystem |
| Mobile/desktop app, local-first data | SQLite | Embedded, no server needed |
| Edge (Cloudflare Workers, Fly.io) | SQLite via Turso/D1/LiteFS | Edge-native, low latency |

| Criteria | SQLite | PostgreSQL | MySQL |
|----------|--------|------------|-------|
| Concurrent writers | 1 (WAL helps reads) | Hundreds+ (MVCC) | Hundreds+ (InnoDB) |
| Max practical size | ~1 TB | Petabytes | Petabytes |
| JSON support | Basic | Advanced (JSONB, indexable) | Limited |
| Managed cost | Free / Turso free tier | $5-15/mo | $5-15/mo |

Migrate from SQLite to PostgreSQL when: frequent `SQLITE_BUSY`, file size > 10 GB, multi-server writes, or row-level security requirements.

**Why:** Choosing right database avoids premature complexity (over-engineering) or painful migrations later (under-engineering).

**Source:** [DB-Engines comparison](https://db-engines.com/en/system/MySQL%3BPostgreSQL%3BSQLite), [database-design-guide.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/database-design-guide.md) Database Selection section

---

### DB-09 Multi-Tenant Data Isolation [CRITICAL]

**Detect:** Multi-tenant schema (shared tables with `tenant_id`/`org_id`/`account_id` column) where queries against tenant-scoped tables omit the tenant filter — hand-written `WHERE` clauses missing `tenant_id = ?`, ORM default scopes without a tenant guard, or row-level security (RLS) not enabled on tenant-scoped tables in Postgres.

```
# Vulnerable: no tenant filter, relies only on the primary key
SELECT * FROM invoices WHERE id = $1

# Vulnerable: ORM query built without tenant scope
Invoice.find(params[:id])
```

**Fix:** Scope every query on a shared tenant-owned table by `tenant_id` — either enforce it in application code (ORM default scope / repository layer that always injects `tenant_id`) or enable Postgres row-level security as a defense-in-depth backstop:

```sql
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON invoices
  USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

Never trust a client-supplied `tenant_id`; derive it from the authenticated session/JWT claim server-side.

**Why:** A missing tenant filter lets one tenant read or modify another tenant's rows via a guessable/enumerable ID (IDOR at the data layer) — a full cross-tenant data breach, the most damaging class of bug in multi-tenant SaaS.

**Source:** [OWASP: Insecure Direct Object References](https://owasp.org/www-community/attacks/Insecure_Direct_Object_Reference), [PostgreSQL Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html), [database-design-guide.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/database-design-guide.md) Schema Design section

### DB-10 Schema-Level Data Minimization & PII Log Hygiene [HIGH]

**Detect:** PII columns (email, phone, address, birth date, national ID, free-text notes) with no consuming feature — cross-check each PII column against actual reads in application code. Raw identifiers (email/phone) used as join keys across analytics or derived tables. Logging middleware/ORM echo that writes full row payloads (including PII columns) into application logs. PII scanning implemented as regex-only and treated as complete.

**Fix:** Drop or never add PII columns without a consuming feature — minimization is enforced at the schema, not in a policy document (GDPR Art. 5(1)(c) makes it a legal obligation). Join/analytics keys: use surrogate IDs or pseudonymous tokens, never raw identifiers (mapping table in a separate access-controlled store — see ds-compliance PRV-26). Logging: redact at field level before write; know the tooling limits — regex catches structured PII only (emails, IPs, cards), unstructured PII (names, locations, free text) needs ML/NER-based scanning, and for LLM interactions exclude message content from logs entirely rather than trusting scrubbing.

**Why:** Every PII column that exists without a purpose is breach surface plus regulatory liability at rest; PII that leaks into logs escapes every access control the database enforced.

**Source:** GDPR Art. 5(1)(c); Elastic PII-detection guidance (regex limits); Pydantic Logfire LLM-logging guidance

### DB-11 Declared Duplicate-Prevention Strategy Registry [MEDIUM]

**Detect:** Multiple entity types each carrying their own hand-rolled duplicate-prevention logic (email-match-and-prompt for one, a deterministic composite key for another, TOCTOU self-heal for a third) with no shared registry connecting them. A new create-capable entity type added to the schema with no corresponding duplicate-prevention decision recorded anywhere, and no mechanical check that would fail on that omission.

**Fix:** Define one declarative registry — `{entityType, strategy, rationale}` — where `strategy` is one of `match-and-prompt` / `deterministic-id` / `toctou-heal` / `not-applicable (reason)`. Don't force every entity onto the same strategy (shapes differ too much for that to be anything but a YAGNI violation); require only that each declares one. Add a gate that fails when a create path exists with no registry entry, mirroring how a reconstructibility or nullability-completeness registry gates schema changes elsewhere in the codebase.

**Why:** Without a registry-backed gate, a newly added entity type can ship with zero duplicate protection and nothing fails — the record just silently duplicates in production, a regression class invisible to code review because there's no shared place reviewers check.

**Source:** Declarative-registry-plus-gate pattern generalized from schema-completeness/exhaustiveness checking (same shape as an SSOT-registry for any per-entity axis — data-classification, migration-safety, or duplicate-prevention)

### DB-12 Retained Identifiers Stored as Salted Hashes and Physically Purged [HIGH]
Device/user identifiers kept for abuse prevention are stored only as salted hashes, expire on schedule, and legacy raw values are physically removed.

**Detect:** Raw device IDs, IP addresses, or user identifiers persisted for fraud/abuse purposes; retention with no purge date; a schema migration that dropped a raw-identifier column without compacting the underlying store.

**Fix:** Store salted SHA-256 hashes (salt server-side, not per-row-guessable), attach a retention deadline with automated purge, and after removing legacy raw columns run the store's physical cleanup (VACUUM/compaction) so dropped data is actually gone.

**Impact:** Raw retained identifiers turn an abuse-prevention table into a PII breach surface; "dropped" columns that survive in storage pages fail deletion-right audits.

**Source:** XR-023 — cross-project experience registry (2026).

### DB-13 Single-Writer Embedded DB Tuned: WAL Plus a Matching Partial Index [MEDIUM]
A single-writer, read-heavy embedded database (SQLite-class) runs WAL mode with deliberate pragmas, and the hottest recurring query gets an exactly-matching partial index.

**Detect:** Embedded DB on defaults (journal_mode=DELETE, tiny page cache); the most frequent background query scanning without an index whose predicate matches its WHERE clause.

**Fix:** Set `journal_mode=WAL`, `synchronous=NORMAL`, a sized page cache, `temp_store=MEMORY`, and tuned mmap; add a partial index exactly matching the hottest query's WHERE clause. Relax these only against a concrete measured failure, never speculatively.

**Impact:** Default journal mode serializes readers behind the writer — the app freezes during every background write; the partial index turns the hottest scan into a point lookup.

**Source:** XR-026 — cross-project experience registry (2026).

### DB-14 Workspace/Tenant Identity Is a Permanent Opaque UUID [MEDIUM]
Workspace/tenant identity is a permanent ASCII UUID, immune to renames.

**Detect:** Workspace identified by its display name, folder name, or email; rename flows that touch identity references; identity strings containing user-controlled or locale-sensitive characters.

**Fix:** Mint a permanent ASCII UUID at workspace creation and use it in every reference (storage paths, ACLs, sync state, audit); treat display names as mutable presentation only.

**Impact:** Name-based identity means a rename orphans storage paths, ACLs, and sync state simultaneously — an unrecoverable-looking outage triggered by a cosmetic action.

**Source:** XR-141 — cross-project experience registry (2026).

### DB-15 Taxonomies and Labels Live in One Admin-Managed Canonical Registry [HIGH]
Role, category, and label taxonomies come from one canonical registry (id/label/icon/storeKey); user-visible domain labels are admin-editable data, never hardcoded, while the system runs on fixed semantic roles underneath.

**Detect:** User-facing domain labels ("expert", "client", "room") hardcoded in components or scattered enums; the same taxonomy manually duplicated in a second surface; generated/derived surfaces (exports, reports, satellite sites) inventing their own field/category names; label changes that propagate to some screens but not all.

**Fix:** Keep every taxonomy in one canonical registry (id, label, icon, storeKey) backed by the DB with i18n fallback; make labels admin-editable and propagate changes system-wide; keep internal logic on fixed semantic role IDs (service-provider, service-recipient, intermediary, staff) so the label layer is pure presentation; derived surfaces read the registry and never define their own vocabulary.

**Impact:** Hardcoded labels lock the product to one industry's jargon and make every terminology change a code deploy; duplicated taxonomies drift into contradictory vocabularies across screens.

**Source:** XR-143 + XR-008 — cross-project experience registry (2026).

### DB-16 No Path Deletes User Data Without an Explicit User Request [CRITICAL]
No background job, sync routine, or maintenance task implicitly deletes user data; deletion happens only on explicit user request.

**Detect:** Cleanup/compaction/sync-reconciliation code paths that remove user records as a side effect; "orphan removal" heuristics acting on user content; TTL expiry applied to user-created data without user-facing contract.

**Fix:** Restrict hard deletion of user data to explicitly user-initiated flows (plus regulatory erasure); make background routines archive, flag, or quarantine instead of delete; require any automated removal to be contractually visible to the user (stated retention rule) — never an implementation side effect.

**Impact:** Implicit deletion is indistinguishable from data loss; a single overzealous reconciliation pass can destroy months of user work with no recovery path and no explanation.

**Source:** XR-145 — cross-project experience registry (2026).

### DB-17 Down-Migrations Document Their Loss Boundary [MEDIUM]
Every up-migration has a down counterpart, and each down-migration states in code what it can and cannot restore.

**Detect:** Migrations without down steps; a down-migration that silently restores schema shape while the data (hashed, scrubbed, aggregated) is unrecoverable; operators assuming rollback returns original values.

**Fix:** Ship a down for every up. Where a step is data-destructive (one-way hash, privacy scrub, column drop), write the boundary into the migration itself: "down restores schema only; recovering data beyond this point requires restore from full backup." Keep the note beside the code, not in a wiki.

**Impact:** An operator who trusts a schema-only rollback to restore scrubbed data makes recovery decisions on false premises — during an incident, when it hurts most.

**Source:** XR-021 — cross-project experience registry (2026).

### DB-18 Bulk Mutations Carry Single-Edit Audit and Undo Guarantees [MEDIUM]
Bulk operations over selected records are grouped under a batch ID, fully audited, and reversible in one step.

**Detect:** Bulk-edit paths that skip the audit trail individual edits write; bulk changes with no grouping identifier; no way to revert a bulk operation except record-by-record.

**Fix:** Record every bulk mutation with a shared batch ID in the same audit trail as single edits (per-record old→new), and implement one-step revert of the whole batch. Any field editable singly should be bulk-editable under these same guarantees.

**Impact:** An unaudited bulk edit is the fastest way to corrupt a dataset beyond reconstruction — one mis-scoped filter, hundreds of silent changes, no undo.

**Source:** XR-103 — cross-project experience registry (2026).

### DB-19 Storage Access Flows Through One Abstraction Layer [MEDIUM]
All persistence goes through a single storage abstraction; raw low-level store calls outside it are forbidden.

**Detect:** Direct `localStorage`/file/DB-driver calls scattered outside the designated storage layer; serialization or key-naming logic duplicated at call sites.

**Fix:** Route every read/write through one storage abstraction owning keys, serialization, versioning, and error handling; lint or grep-gate raw store calls outside it.

**Impact:** Scattered raw access makes migrations, encryption, and quota handling impossible to retrofit — every storage policy change becomes a full-codebase hunt.

**Source:** XR-010 — cross-project experience registry (2026).
