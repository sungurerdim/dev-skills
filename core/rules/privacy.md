# Privacy — personal data in code and config

Loaded when the product handles personal data (`pii=yes`). Every rule here is an engineering control the code or config shows; legal duties are the owner's. Personal data in logs is SAR-02, access audit trails SAR-01, object and tenant access AUTH-11, transport encryption SEC-04, column encryption DB-24, backup encryption DEP-31, card data SEC-26, app-store tracking and age signals STO (mobile).

### PRV-01 [CRITICAL] Consent not enforced, versioned or withdrawable in code
- **Detect:** non-essential cookies, tracking, analytics, ads or crash SDKs initialized before a stored choice; reject harder than accept, pre-ticked or bundled purposes, a dismissed banner treated as consent; a `Sec-GPC: 1` request header ignored; consent kept only as a current boolean with no append-only record of grant, change and withdrawal (time, purposes, method, text version); consent text changed without a version bump; no per-purpose withdrawal, or withdrawal that does not stop processing.
- **Mech:** T `git grep -nIiE 'consent|cookie.?banner|onetrust|cookiebot|usercentrics|klaro|didomi|Sec-GPC|globalPrivacyControl' -- ':!*.md' ':!*lock*'`
- **Fix:** gate every non-essential SDK on the stored per-purpose choice; accept and reject equal in weight and steps; read GPC as an opt-out; write a consent event per change through the SAR-01 audit helper; bump the version on every text or scope change and re-ask users below it; one settings action withdraws a purpose and stops its processing at once.
- **Impact:** tracking starts without a choice, and "did this user agree to this, and when" has no answer in the data.
- **Source:** Secure / private by default; GDPR Art. 7; ePrivacy Directive Art. 5(3); Global Privacy Control specification (W3C Privacy CG).

### PRV-03 [CRITICAL] More personal data than the feature needs
- **Detect:** collected fields or columns no code reads; device fingerprinting or persistent device IDs used without need; raw email, phone or national ID used as join keys in analytics or derived tables; a pseudonym mapping kept beside the pseudonymized data; identifiers kept for abuse prevention in raw form.
- **Mech:** T `git grep -nIiE 'fingerprint|getUniqueId|ANDROID_ID|identifierForVendor|advertisingId|IDFA' -- ':!*.md' ':!*lock*'`
- **Fix:** drop what has no consuming feature; use surrogate IDs or keyed hashes in analytics and keep the mapping in a separately controlled store; hash identifiers that are only matched; minimize at the schema, not in a policy.
- **Impact:** every unneeded field widens the breach and is a liability however well it is secured.
- **Source:** Secure / private by default; GDPR Art. 25; NIST SP 800-122.

### PRV-04 [CRITICAL] Users cannot get, export or erase their data
- **Detect:** no self-service or request path for access, export and deletion; deletion that only disables the account or leaves rows in other tables, files, search indexes, caches, analytics or processors (PRV-15); several deletion paths with diverging key lists; dropped data still in storage pages or backups with no expiry; no identity check on requests; no record of requests and outcomes; export not machine-readable.
- **Mech:** T `git grep -nIiE 'delete.?account|deleteUser|account.?deletion|erasure|data.?export|export.?(my|user).?data|download.?my.?data|dsar' -- ':!*.md'`
- **Fix:** one deletion routine covering every store and every PRV-15 recipient (their delete API called, backups expire on a set schedule, storage compacted after drops); export as JSON or CSV; verify the requester; record each request with type, time and outcome; a test deletes a seeded user and finds nothing left.
- **Impact:** a user cannot leave or see their data, and "deleted" data stays exposed to the next breach.
- **Source:** DRY / single source of truth; GDPR Art. 15, 17, 20; SIM-06 (one deletion list).

### PRV-27 [HIGH] Retention stated but not enforced
- **Detect:** retention periods in docs or config with no TTL, scheduled purge or lifecycle rule implementing them; personal data in tables, logs, intermediates or object stores with no expiry; one blanket period where data types differ (raw events, aggregates, recordings, crash data).
- **Mech:** T `git grep -nIiE 'ttl|expireAfterSeconds|expires?_at|retention|purge|lifecycle_?rule|LifecycleConfiguration' -- ':!*.md' ':!*lock*'`
- **Fix:** a retention period per data class in config, enforced by TTL indexes, scheduled purge jobs or storage lifecycle rules, with the job's result logged.
- **Impact:** data is kept exactly as long as nobody remembers to delete it, which in practice means forever.
- **Source:** Secure / private by default; GDPR Art. 5(1)(e); NIST SP 800-122.

### PRV-28 [HIGH] Analytics or crash reporting carries personal data
applies_when: pii=yes or integrations≠none
- **Detect:** analytics, session replay or crash SDKs started regardless of consent (server-side tagging included); session replay without input masking; full IP addresses stored when only coarse location is used; user IDs, emails, request bodies or tokens in events, URLs or crash payloads; dashboards or exports showing cohorts small enough to identify people.
- **Mech:** T `git grep -nIiE 'gtag\(|googletagmanager|mixpanel|amplitude|segment\.(io|com)|posthog|Sentry\.init|sentry_sdk\.init|crashlytics|firebase.?analytics|hotjar|fullstory|clarity\.ms|datadogRum' -- ':!*.md' ':!*lock*'`
- **Fix:** start these SDKs through PRV-01's gate; mask inputs in replay; truncate IPs (IPv4 /24, IPv6 /64) before storage; strip identifiers and bodies with the SDK's before-send hook; suppress small cohorts with a documented minimum.
- **Impact:** a debugging or growth tool becomes an unconsented personal-data pipeline into a third party.
- **Source:** Secure / private by default; GDPR Art. 5(1)(c); OWASP Logging Cheat Sheet.

### PRV-15 [HIGH] Third parties receiving personal data not inventoried
- **Detect:** dependencies, SDKs or service clients that receive personal data (hosting, email, analytics, crash reporting, AI APIs, support, payment) with no list in the repo naming each recipient and the fields it gets; the list not updated in the change that adds or removes such a dependency; recipients the deletion routine (PRV-04) does not reach.
- **Mech:** T `git grep -nIiE 'sentry|datadog|mixpanel|amplitude|segment|posthog|sendgrid|mailgun|postmark|twilio|intercom|zendesk|openai|anthropic|stripe' -- '*.json' '*.toml' '*.txt' '*.gradle*' '*.yaml' '*.yml' '*.mod' ':!*lock*'`
- **Fix:** one data-flow file (recipient, fields sent, purpose, region, delete path) derived from the manifests and integration code; review it in every change to dependencies or outbound payloads.
- **Impact:** nobody can say where a user's data went, so deletion, a promise to users or a breach investigation misses recipients.
- **Source:** GDPR Art. 28, 30; NIST SP 800-122.

### PRV-31 [CRITICAL] Special-category data sent to a third party
- **Detect:** health, biometric, genetic, religious, ethnic, sexual-life or political data, or national ID numbers, present in payloads to sync providers, analytics, AI model APIs, email or support tools; outbound field lists that grow automatically with the schema; no test that these fields never leave.
- **Mech:** T `git grep -nIiE '(health|diagnos|medical|biometric|religio|ethnic|sexual|national_?id|tc_?kimlik|ssn)[a-z_]*' -- ':!*.md' ':!*test*' ':!*lock*'`
- **Fix:** allow-list mappers for every outbound payload (unlisted fields cannot leave); keep such data in the primary store with need-to-know access (AUTH-11, SAR-01); a negative test fails the build if such a field appears in an outbound payload.
- **Impact:** one accidental mapping sends sensitive data of every user to a party that cannot be made to delete it.
- **Source:** Secure / private by default; GDPR Art. 9; OWASP API Security Top 10 API3:2023.

### PRV-30 [HIGH] A privacy claim the code contradicts
- **Detect:** a promise in docs, UI copy or the published notice ("data stays in the EU", "nothing leaves your device", "end-to-end encrypted", "no copies remain", "we never share") that holds for the main path while exports, integrations, admin tools, backups, AI calls, crash reports or an ads SDK break it; exports that write to an API's default location instead of a named target.
- **Mech:** M (every write, export and outbound call, and the PRV-15 list, against each stated claim)
- **Fix:** move the side path inside the claim, replace it with a local alternative, or narrow the claim to what the code does; name the target of every export explicitly.
- **Impact:** a claim true for one path and false for another misleads users and is the first thing a breach investigation finds.
- **Source:** GDPR Art. 5(2); FTC Act §5.

### PRV-48 [CRITICAL] Children reach the product with adult defaults
applies_when: audience=public
- **Detect:** a product aimed at or likely used by children with no age gate before data collection; adult defaults for them (public profiles, geolocation on, sharing nudges, ad profiling); third-party SDKs (PRV-15) active for users under the gate's threshold; the age threshold hard-coded where it should be config.
- **Mech:** T `git grep -nIiE 'age.?gate|date.?of.?birth|birth_?date|dob|is_?minor|age_?verif|parental' -- ':!*.md'`
- **Fix:** an age gate before collection, the threshold in config; high-privacy defaults and no nudges below it; ads and analytics SDKs off below it; a parental-consent flow where the product needs one. Store age signals are STO-07.
- **Impact:** children's data flows to ad and analytics vendors on adult terms.
- **Source:** Secure / private by default; GDPR Art. 8; COPPA (16 CFR 312); ICO Age Appropriate Design Code.
