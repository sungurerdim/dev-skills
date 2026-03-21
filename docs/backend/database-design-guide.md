# Database Design Guide

Practical database design reference for solo developers and small teams. Covers selection, schema, migrations, indexing, query optimization, backups, privacy, and testing.

---

## Database Selection

Choose the simplest database that meets your concurrency and feature requirements.

### Decision Matrix

| Criteria | SQLite | PostgreSQL | MySQL |
|---|---|---|---|
| **Setup complexity** | Zero (single file) | Moderate (server) | Moderate (server) |
| **Concurrent writers** | 1 (WAL helps reads) | Hundreds+ (MVCC) | Hundreds+ (InnoDB) |
| **Max practical size** | ~1 TB | Petabytes | Petabytes |
| **JSON support** | Basic (`json_extract`) | Advanced (JSONB, indexable) | JSON type (limited) |
| **Full-text search** | FTS5 (built-in) | `tsvector`/`tsquery` | FULLTEXT index |
| **Geospatial** | Extension required | PostGIS (industry standard) | Basic spatial index |
| **Replication** | Litestream / Turso / LiteFS | Streaming, logical | Built-in primary-replica |
| **Extensions** | Limited | Rich (pg_trgm, etc.) | Plugins, limited |
| **Cost (managed)** | Free / Turso free tier | $5-15/mo (Supabase, Neon) | $5-15/mo (PlanetScale) |
| **Best fit** | Mobile, edge, CLI, prototypes | Web apps, APIs, analytics | Legacy, WordPress, shared hosting |

### Quick Selection

- **Prototype / side project**, < 100 users, low writes: SQLite.
- **Production web app** with transactions or complex queries: PostgreSQL.
- **Existing MySQL stack** or shared hosting: MySQL.
- **Mobile / desktop app** with local-first data: SQLite.
- **Edge** (Cloudflare Workers, Fly.io): SQLite via Turso / D1 / LiteFS.

---

## Schema Design

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Tables | `snake_case`, plural | `user_accounts`, `order_items` |
| Columns | `snake_case`, singular | `created_at`, `email_address` |
| Primary keys | `id` or `<table>_id` | `id`, `user_account_id` |
| Foreign keys | `<ref_table_singular>_id` | `order_id`, `user_id` |
| Indexes | `idx_<table>_<columns>` | `idx_orders_user_id_created_at` |
| Constraints | `<type>_<table>_<column>` | `uq_users_email`, `chk_orders_total` |
| Booleans | `is_` or `has_` prefix | `is_active`, `has_verified_email` |
| Timestamps | `_at` suffix | `created_at`, `deleted_at` |

Pick one convention and enforce it project-wide. Consistency matters more than which style.

### Normalization vs Denormalization

**Start normalized (3NF).** Denormalize only with measured evidence of a performance problem.

| Situation | Approach |
|---|---|
| Unknown or evolving requirements | Normalize (3NF) |
| Frequent joins on hot path | Materialized view or computed column |
| Reporting / analytics queries | Denormalized read replica or materialized views |
| Audit trail or event log | Append-only normalized table |
| Caching aggregates | Counter cache column + trigger or app update |

### Data Types

- **IDs:** `BIGINT GENERATED ALWAYS AS IDENTITY` (PG) or `UUID` via `gen_random_uuid()` for distributed/non-guessable IDs.
- **Money:** `INTEGER` (store cents) or `NUMERIC(19,4)`. Never `FLOAT`.
- **Timestamps:** `TIMESTAMPTZ` (PG, always UTC). ISO 8601 strings or Unix epoch in SQLite.
- **Text:** `TEXT` with `CHECK(length(col) <= N)` over `VARCHAR(N)` in PG — identical performance.
- **Enums:** `CHECK` constraints or lookup table. Avoid DB-level `ENUM` (hard to migrate).
- **JSON:** `JSONB` in PG (indexable). `json_extract` in SQLite. Don't store relational data as JSON.

### Constraints

Define constraints at the database level — application validation is not a substitute.

```sql
CREATE TABLE orders (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status      TEXT NOT NULL CHECK (status IN ('pending','confirmed','shipped','delivered','cancelled')),
    total_cents INTEGER NOT NULL CHECK (total_cents >= 0),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

- Every table gets a primary key.
- Every FK gets an explicit `ON DELETE` (`CASCADE`, `SET NULL`, or `RESTRICT`).
- Use `NOT NULL` by default; allow `NULL` only when absence has genuine meaning.
- Add `CHECK` constraints for domain rules (positive amounts, valid statuses).

---

## Migration Strategies

### Versioned Migrations

Store migrations as numbered SQL files in version control (`001_create_users.up.sql` / `.down.sql`). Tools: `golang-migrate`, `Flyway`, `Alembic`, `Knex`, `Prisma Migrate`, `dbmate`.

Rules:
- Migrations are immutable once applied to a shared environment.
- Every `up` has a corresponding `down` (rollback). Test both in CI.
- Never edit a migration that has been applied to staging or production.

### Zero-Downtime Expand-Contract Pattern

1. **Expand:** Add new column/table alongside the old. Deploy code that writes to both.
2. **Migrate data:** Backfill existing rows.
3. **Switch reads:** Update application to read from the new structure.
4. **Contract:** Drop the old column/table.

### Safe vs Dangerous Operations

| Operation | Safe? | Notes |
|---|---|---|
| `ADD COLUMN` (nullable, no default) | Safe | Metadata-only in PG |
| `ADD COLUMN ... DEFAULT x` | Safe (PG 11+) | Rewrites table in older PG and SQLite |
| `DROP COLUMN` | Dangerous | Data loss; use expand-contract |
| `ALTER COLUMN TYPE` | Dangerous | May rewrite and lock table |
| `RENAME COLUMN` | Moderate | Safe in DB, breaks app code |
| `CREATE INDEX` | Dangerous | Use `CONCURRENTLY` in PG |
| `ADD NOT NULL` | Dangerous | Fails if NULLs exist; add CHECK first |
| `DROP TABLE` | Dangerous | Irreversible |

### Rollback

- Keep rollback scripts tested. Take a backup before destructive operations.
- PG DDL is transactional (auto-rollback on failure). SQLite and MySQL are not — plan accordingly.

---

## Indexing

### Index Types

| Type | Engine | Best For | Example |
|---|---|---|---|
| **B-tree** | All | Equality, range, sorting | `CREATE INDEX idx_orders_date ON orders(created_at)` |
| **Hash** | PG | Exact equality only | `USING hash(email)` |
| **GIN** | PG | JSONB, arrays, full-text | `USING gin(tags)` |
| **GiST** | PG | Geospatial, range types | `USING gist(coordinates)` |
| **BRIN** | PG | Large naturally-ordered tables | `USING brin(created_at)` |
| **Partial** | PG, SQLite | Queries on a known subset | `WHERE status = 'pending'` |
| **Composite** | All | Multi-column lookups | `(user_id, created_at DESC)` |

### Guidelines

- Index columns in `WHERE`, `JOIN`, `ORDER BY`, `GROUP BY`.
- **Column order matters** in composite indexes — high-selectivity first. Left-prefix queries are served.
- **Partial indexes** shrink index size for subset queries.
- **BRIN** for append-only tables (logs) — 100-1000x smaller than B-tree.
- **Covering indexes** (`INCLUDE` in PG) avoid table lookups entirely.
- Don't over-index — each index slows writes. Monitor with `pg_stat_user_indexes`.

```sql
-- Composite: serves user_id or user_id + created_at queries
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);

-- Partial: only indexes rows you query
CREATE INDEX idx_orders_active ON orders(user_id, created_at)
    WHERE status NOT IN ('cancelled', 'delivered');

-- BRIN for time-series (tiny index, huge table)
CREATE INDEX idx_events_ts ON events USING brin(created_at) WITH (pages_per_range = 32);

-- GIN for JSONB containment
CREATE INDEX idx_settings ON user_settings USING gin(preferences jsonb_path_ops);
```

---

## ORM Patterns

### N+1 Detection and Prevention

The N+1 problem: 1 query for a list, then N queries for related data per item.

**Detection:** Enable query logging in dev. Use `django-debug-toolbar`, `bullet` (Ruby), `laravel-query-detector`, or `sqlcommenter`. Monitor `pg_stat_statements` for high-frequency low-cost queries.

**Prevention:** Eager loading (`JOIN`, `includes()`, `prefetch_related()`, `with()`). DataLoader for GraphQL. Batch with `WHERE id IN (...)`. Use raw SQL for complex aggregations.

### Repository Pattern

Isolate DB access behind a repository interface (`findById`, `create`, `update`, `delete`, `list`). Benefits: testable, ORM-agnostic, single place to optimize queries.

### Connection Pooling

| Setting | SQLite | PostgreSQL (solo) | PostgreSQL (prod) |
|---|---|---|---|
| Pool size | 1 write, N read | 5-10 | 10-25 per instance |
| Idle timeout | N/A | 30s | 10-30s |
| Connection lifetime | N/A | 30 min | 30 min |
| Pooler | N/A | Optional PgBouncer | PgBouncer transaction mode |

Pool size rule of thumb: `(2 * CPU cores) + 1` for NVMe. Keep total connections under `max_connections - 10`.

---

## Query Optimization

### EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders
    WHERE user_id = 42 AND status = 'pending'
    ORDER BY created_at DESC LIMIT 10;
```

Watch for: **Seq Scan** on large tables (missing index), **Nested Loop** with high rows (needs index or hash join), high **Buffers shared read** (data not cached).

### pg_stat_statements

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
```

Review weekly. Optimize by total time, not slowest individual execution.

### Slow Query Log

- **PostgreSQL:** `log_min_duration_statement = 200` in `postgresql.conf`.
- **SQLite:** Instrument at application layer (no built-in support).
- **MySQL:** `slow_query_log = 1`, `long_query_time = 0.2`.

### Common Fixes

- Add missing indexes (most frequent fix).
- Replace `SELECT *` with specific columns. Add `LIMIT` to unbounded queries.
- Replace correlated subqueries with `JOIN` or `EXISTS`.
- Batch inserts (`INSERT ... VALUES (...), (...)` or `COPY`).

---

## Backup and Recovery

### The 3-2-1 Rule

**3** copies, **2** storage types, **1** offsite.

| Copy | Storage | Example |
|---|---|---|
| Primary | Production DB | Managed PG (Supabase, Neon, RDS) |
| Local backup | Same cloud, different service | `pg_dump` to S3 same region |
| Offsite | Different provider/region | S3 cross-region or Backblaze B2 |

### Backup Methods

- **`pg_dump`:** Logical. Good for < 100 GB. Portable across PG versions.
- **`pg_basebackup` + WAL archiving:** Physical. PITR to any second.
- **SQLite:** `sqlite3 mydb.sqlite ".backup 'backup.sqlite'"` or Litestream for continuous replication.

```bash
# PostgreSQL daily backup
pg_dump -Fc --compress=zstd:3 -f "backup_$(date +%Y%m%d_%H%M%S).dump" "$DATABASE_URL"

# SQLite continuous replication
litestream replicate mydb.sqlite s3://my-bucket/mydb
```

### Schedule (Solo Dev)

| Frequency | Method | Retention |
|---|---|---|
| Continuous | WAL archiving (PG) / Litestream (SQLite) | 7 days |
| Daily | `pg_dump` or `.backup` | 30 days |
| Weekly | Full backup offsite | 90 days |
| Before migration | Manual snapshot | Until verified |

Automate everything. Test restores monthly.

---

## Data Privacy

### PII Classification

| Category | Examples | Handling |
|---|---|---|
| **Direct identifiers** | Name, email, phone, SSN | Encrypt at rest, minimize collection |
| **Indirect identifiers** | IP, device ID, geolocation | Pseudonymize where possible |
| **Sensitive** | Health, financial, biometric | Separate storage, audit logging |
| **Non-personal** | Aggregated stats, anonymized | Standard handling |

### Encryption at Rest

- **PostgreSQL:** `pgcrypto` for column-level encryption. Cloud disk encryption for full DB.
- **SQLite:** SQLCipher for AES-256 full-database encryption.
- **Application-level:** Encrypt before storage; manage keys outside the database.

### GDPR Practices

- **Right to access:** Export all user data across tables.
- **Right to deletion:** Hard delete or crypto-shredding (delete the key).
- **Data minimization:** Collect only what you need. Review quarterly.
- **Consent tracking:** Store records with timestamps and scope.
- **Breach notification:** Documented process; 72-hour requirement.

### Retention Policies

Define per-table retention. Automate with scheduled jobs:

```sql
DELETE FROM users WHERE deleted_at < now() - INTERVAL '90 days';
DELETE FROM access_logs WHERE created_at < now() - INTERVAL '365 days';
```

---

## SQLite for Mobile and Edge

### WAL Mode

Always enable WAL for concurrent reads. Set at every connection open:

```sql
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=-20000;       -- 20MB
PRAGMA foreign_keys=ON;         -- Off by default in SQLite
```

### Write Concurrency

SQLite allows **one writer at a time**. Concurrent writes wait (up to `busy_timeout`), then fail with `SQLITE_BUSY`.

Mitigations: batch writes into transactions, keep write transactions < 50 ms, use an application-level write queue.

### When to Migrate to PostgreSQL

| Signal | Threshold |
|---|---|
| Write contention | Frequent `SQLITE_BUSY` despite tuning |
| File size | > 10 GB and growing |
| Complex queries | FTS + joins + aggregations on large data |
| Multi-server writes | More than one app server writing |
| Row-level security | Any multi-tenant requirement |
| Replication needs | Beyond Litestream / LiteFS |

Migration path: `.dump` from SQLite, transform syntax (data types, auto-increment), import via `psql` or `pgloader`.

---

## Database Testing

### Testcontainers

Spin up a real database per test suite (Java, Python, Node.js, Go, .NET):

```python
from testcontainers.postgres import PostgresContainer

def test_user_creation():
    with PostgresContainer("postgres:16") as pg:
        engine = create_engine(pg.get_connection_url())
        run_migrations(engine)
        user = UserRepository(engine).create({"email": "test@example.com"})
        assert user.id is not None
```

### Fixtures and Seeding

- Factory functions over static SQL dumps.
- Each test creates own data, cleans up via transaction rollback.
- Never assert on row IDs — not stable across runs.

### Migration Testing in CI

On every PR touching migrations: start empty DB, apply all UP migrations, verify schema, apply all DOWN in reverse, verify empty state, re-apply UP (proves idempotent rollback).

### SQLite Testing

Test against real SQLite with production PRAGMAs — not an in-memory substitute for PostgreSQL.

---

## Sources

- [9 Key Database Design Best Practices for 2025 — Nerdify](https://getnerdify.com/blog/database-design-best-practices)
- [Top 10 PostgreSQL Best Practices for 2025 — Instaclustr](https://www.instaclustr.com/education/postgresql/top-10-postgresql-best-practices-for-2025/)
- [PostgreSQL vs SQLite: Choosing the "Wrong" Database — Medium](https://medium.com/the-software-journal/postgresql-vs-sqlite-when-you-should-choose-the-wrong-database-70860f36bfad)
- [SQLite vs MySQL vs PostgreSQL Comparison — RunCloud](https://runcloud.io/blog/sqlite-vs-mysql-vs-postgresql)
- [The SQLite Renaissance in 2026 — DEV Community](https://dev.to/pockit_tools/the-sqlite-renaissance-why-the-worlds-most-deployed-database-is-taking-over-production-in-2026-3jcc)
- [Guide to PostgreSQL Database Design — Tiger Data](https://www.tigerdata.com/learn/guide-to-postgresql-database-design)
- [Designing Robust Relational Databases — DEV Community](https://dev.to/pedrohgoncalves/designing-robust-and-scalable-relational-databases-a-series-of-best-practices-1i20)
- [PostgreSQL EXPLAIN Documentation](https://www.postgresql.org/docs/current/sql-explain.html)
- [PostgreSQL pg_stat_statements](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [Testcontainers](https://testcontainers.com/)
- [Litestream — SQLite Replication](https://litestream.io/)
