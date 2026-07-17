# Rules: Database Design & Operations

Rules for audit/design/spec modes. Each rule: ID, severity, detect pattern, fix action, source.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Database** | DB-01 to DB-10 (2 CRITICAL, 4 HIGH, 3 MEDIUM, 1 LOW) | ~12 |

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

**Source:** [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html), database-design-guide.md Schema Design section

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

**Source:** [Use The Index, Luke](https://use-the-index-luke.com/), database-design-guide.md Indexing section

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

**Source:** [Zero-Downtime PostgreSQL Migrations](https://www.braintreepayments.com/blog/safe-operations-for-high-volume-postgresql/), [Squawk](https://squawkhq.com/), [Atlas](https://atlasgo.io/versioned/lint), database-design-guide.md Migration Strategies section

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

**Source:** [PgBouncer docs](https://www.pgbouncer.org/), [HikariCP](https://github.com/brettwooldridge/HikariCP), database-design-guide.md ORM Patterns section

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

**Source:** [PostgreSQL naming conventions](https://www.postgresql.org/docs/current/sql-syntax-lexical.html), database-design-guide.md Schema Design section

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

**Source:** ORM documentation (Django, SQLAlchemy, ActiveRecord, JPA), database-design-guide.md ORM Patterns section

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

**Source:** [AWS RDS backup docs](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html), [pg_dump best practices](https://www.postgresql.org/docs/current/app-pgdump.html), database-design-guide.md Backup and Recovery section

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

**Source:** [DB-Engines comparison](https://db-engines.com/en/system/MySQL%3BPostgreSQL%3BSQLite), database-design-guide.md Database Selection section

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

**Source:** [OWASP: Insecure Direct Object References](https://owasp.org/www-community/attacks/Insecure_Direct_Object_Reference), [PostgreSQL Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html), database-design-guide.md Schema Design section

### DB-10 Schema-Level Data Minimization & PII Log Hygiene [HIGH]

**Detect:** PII columns (email, phone, address, birth date, national ID, free-text notes) with no consuming feature — cross-check each PII column against actual reads in application code. Raw identifiers (email/phone) used as join keys across analytics or derived tables. Logging middleware/ORM echo that writes full row payloads (including PII columns) into application logs. PII scanning implemented as regex-only and treated as complete.

**Fix:** Drop or never add PII columns without a consuming feature — minimization is enforced at the schema, not in a policy document (GDPR Art. 5(1)(c) makes it a legal obligation). Join/analytics keys: use surrogate IDs or pseudonymous tokens, never raw identifiers (mapping table in a separate access-controlled store — see ds-compliance PRV-26). Logging: redact at field level before write; know the tooling limits — regex catches structured PII only (emails, IPs, cards), unstructured PII (names, locations, free text) needs ML/NER-based scanning, and for LLM interactions exclude message content from logs entirely rather than trusting scrubbing.

**Why:** Every PII column that exists without a purpose is breach surface plus regulatory liability at rest; PII that leaks into logs escapes every access control the database enforced.

**Source:** GDPR Art. 5(1)(c); Elastic PII-detection guidance (regex limits); Pydantic Logfire LLM-logging guidance
