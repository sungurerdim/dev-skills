# Privacy — personal data in code, product and paperwork

Loaded when the product handles personal data (`pii=yes`). Law-specific duties are in the jurisdiction slices [privacy-eu.md](privacy-eu.md), [privacy-us.md](privacy-us.md) and [privacy-intl.md](privacy-intl.md); the documents a fix writes start from the templates [dpia](../templates/dpia.md), [breach-notification](../templates/breach-notification.md), [privacy-policy](../templates/privacy-policy.md) and [processor-registry](../templates/processor-registry.md). Personal data in logs is SAR-02, audit trails SAR-01, column encryption DB-24, accessibility law AXE (a11y), card data MON (money), app-store tracking and age rules STO (mobile).

### PRV-01 [CRITICAL] Consent not freely given or not as easy to withdraw
- **Detect:** non-essential cookies, tracking, analytics, ads or crash SDKs initialized before a recorded choice; reject harder than accept (smaller, hidden, extra steps); pre-ticked or bundled purposes; a dismissed banner treated as consent; re-prompts after a refusal; no per-purpose setting to withdraw later, or withdrawal that does not stop processing.
- **Mech:** T `git grep -nIiE 'consent|cookie.?banner|onetrust|cookiebot|usercentrics|klaro|didomi' -- ':!*.md' ':!*lock*'`
- **Fix:** gate every non-essential SDK on the stored per-purpose choice; accept and reject equal in weight and steps; dismissal means no; a settings page withdraws each purpose in one action and processing stops at once.
- **Impact:** consent obtained by design pressure is invalid, so every processing act that rests on it is unlawful.
- **Source:** GDPR Art. 4(11), 7(3); ePrivacy Directive 2002/58/EC Art. 5(3); EDPB Guidelines 03/2022 on deceptive design patterns; Cal. Civ. Code §1798.140(h).

### PRV-59 [HIGH] Consent not provable per user and version
- **Detect:** consent kept only as a current boolean; no append-only record of grant, change and withdrawal with time, purposes, method and the text version shown; consent text or purposes changed without a version bump; users on an older version not asked again.
- **Mech:** T `git grep -nIiE 'consent_?(version|log|event|history|record)|consentVersion|consented_at' -- ':!*.md'`
- **Fix:** store a consent event per change (time, purposes, method, version) through the SAR-01 audit mechanism; bump the version on every text or scope change and re-ask users below it before processing continues.
- **Impact:** "show that this user consented to this on this date" has no answer, and consent to old terms silently covers new purposes.
- **Source:** GDPR Art. 7(1); ICO guidance on consent records.

### PRV-02 [CRITICAL] Privacy notice missing, incomplete or untrue
applies_when: pii=yes or audience=public
- **Detect:** no notice reachable from the app, site or store listing; a notice missing controller identity and contact, purposes and legal basis per activity, data categories, recipients and processors (including AI providers), transfers, retention, the rights and how to use them, the right to complain, automated decision-making and a last-updated date; claims the code contradicts ("end-to-end encrypted" over TLS plus at-rest encryption, "no copies remain" while backups exist, "we never share" next to an ads SDK).
- **Mech:** T `git ls-files | grep -iE 'privacy|gizlilik|datenschutz|confidentialit'` · `git grep -nIiE 'privacy.?policy|/privacy' -- ':!*.md'`
- **Fix:** write it from [privacy-policy](../templates/privacy-policy.md), link it where data is collected, and check every claim against the code and the processor list.
- **Impact:** a missing or untrue notice is a transparency violation on its own and a misleading commercial claim when checked by a regulator or researcher.
- **Source:** GDPR Art. 12–14; Cal. Civ. Code §1798.100; FTC Act §5 (deceptive claims).

### PRV-56 [HIGH] Terms of service missing what the product does
applies_when: audience=public
- **Detect:** no terms reachable; terms missing acceptance, licence and restrictions, user obligations, termination with a data-export window, liability, governing law, changes and contact; subscription with no renewal and cancellation terms; user content with no content licence or takedown procedure; marketplace with no party responsibilities; AI features with no output disclaimer or prohibited uses.
- **Mech:** T `git ls-files | grep -iE '(^|/)(terms|tos|eula|legal)[^/]*'`
- **Fix:** baseline clauses plus the set matching the product's features; link it beside the privacy notice.
- **Impact:** a missing cancellation disclosure is an enforcement target, and a missing takedown procedure forfeits safe-harbour protection for user content.
- **Source:** FTC Negative Option Rule; 17 U.S.C. §512 (DMCA safe harbor).

### PRV-03 [CRITICAL] More personal data than the feature needs
- **Detect:** collected fields or columns no code reads; device fingerprinting or persistent device IDs used without need; raw email, phone or national ID used as join keys in analytics or derived tables; a pseudonym mapping kept beside the pseudonymized data; identifiers kept for abuse prevention in raw form.
- **Mech:** T `git grep -nIiE 'fingerprint|getUniqueId|ANDROID_ID|identifierForVendor|advertisingId|IDFA' -- ':!*.md' ':!*lock*'`
- **Fix:** drop what has no consuming feature; use surrogate IDs or keyed hashes in analytics and keep the mapping in a separately controlled store; hash identifiers that are only matched; minimize at the schema, not in a policy.
- **Impact:** every unneeded field widens the breach and is unlawful to hold regardless of how well it is secured.
- **Source:** GDPR Art. 5(1)(c), 25, 4(5); NIST SP 800-122.

### PRV-04 [CRITICAL] Users cannot get, export or erase their data
- **Detect:** no self-service or documented request path for access, export and deletion; deletion that only disables the account or leaves rows in other tables, files, search indexes, caches, analytics or processors; several deletion paths with diverging key lists (a SIM-06 copy); dropped data still in storage pages or backups with no expiry; no identity check on requests; no log of requests and answers; export not machine-readable.
- **Mech:** T `git grep -nIiE 'delete.?account|deleteUser|account.?deletion|erasure|data.?export|export.?(my|user).?data|download.?my.?data|dsar' -- ':!*.md'`
- **Fix:** one deletion routine covering every store and processor (backups expire on a stated schedule, storage compacted after drops); export in JSON or CSV; verify the requester; log each request with type, time and outcome so the statutory deadline is provable.
- **Impact:** a right the law grants cannot be exercised, and "deleted" data stays exposed to the next breach.
- **Source:** GDPR Art. 12(3), 15, 17, 20; Cal. Civ. Code §1798.105–.110; SIM-06 (one deletion list).

### PRV-27 [HIGH] Retention stated but not enforced
- **Detect:** retention periods in a notice or policy with no TTL, scheduled purge or lifecycle rule implementing them; personal data in tables, logs, intermediates or object stores with no expiry; one blanket period where data types differ (raw events, aggregates, recordings, crash data); compliance records with no period.
- **Mech:** T `git grep -nIiE 'ttl|expireAfterSeconds|expires?_at|retention|purge|lifecycle_?rule|LifecycleConfiguration' -- ':!*.md' ':!*lock*'`
- **Fix:** a retention period per data class in config, enforced by TTL indexes, scheduled purge jobs or storage lifecycle rules, with the job's result logged.
- **Impact:** data is kept exactly as long as nobody remembers to delete it, which in practice means forever.
- **Source:** GDPR Art. 5(1)(e); NIST SP 800-122.

### PRV-28 [HIGH] Analytics or crash reporting below the privacy floor
applies_when: pii=yes or integrations≠none
- **Detect:** analytics, session replay or crash SDKs started regardless of consent (server-side tagging included); session replay without input masking; full IP addresses stored when only coarse location is used; user IDs, emails, request bodies or tokens in events, URLs or crash payloads; dashboards or exports showing cohorts small enough to identify people.
- **Mech:** T `git grep -nIiE 'gtag\(|googletagmanager|mixpanel|amplitude|segment\.(io|com)|posthog|Sentry\.init|sentry_sdk\.init|crashlytics|firebase.?analytics|hotjar|fullstory|clarity\.ms|datadogRum' -- ':!*.md' ':!*lock*'`
- **Fix:** start these SDKs through PRV-01's gate; mask inputs in replay; truncate IPs (IPv4 /24, IPv6 /64) before storage; strip identifiers and bodies with the SDK's before-send hook; suppress small cohorts with a documented minimum.
- **Impact:** a debugging or growth tool becomes an unconsented personal-data pipeline into a third party.
- **Source:** GDPR Art. 5(1)(c); CJEU C-582/14 *Breyer* (IP addresses are personal data); ePrivacy Directive Art. 5(3).

### PRV-31 [CRITICAL] Special-category data sent to a third party
- **Detect:** health, biometric, genetic, religious, ethnic, sexual-life or political data, or national ID numbers, present in payloads to sync providers, analytics, AI model APIs, email or support tools; outbound field lists that grow automatically with the schema; no test that these fields never leave.
- **Mech:** T `git grep -nIiE '(health|diagnos|medical|biometric|religio|ethnic|sexual|national_?id|tc_?kimlik|ssn)[a-z_]*' -- ':!*.md' ':!*test*' ':!*lock*'`
- **Fix:** allow-list mappers for every outbound payload (unlisted fields cannot leave); keep special-category data in the primary store with need-to-know access; a negative test fails the build if such a field appears in an outbound payload; where a third party must receive it, record the explicit legal basis and the contract.
- **Impact:** one accidental mapping sends sensitive data of every user to a party that cannot be made to delete it.
- **Source:** GDPR Art. 9, 28; KVKK Art. 6.

### PRV-30 [HIGH] A stated data-location promise broken by a side path
- **Detect:** a promise in docs or the notice ("data stays in the EU", "nothing leaves your device", "stored only in your account") that holds for the main store while exports, integrations, admin tools, backups, AI calls or crash reports send the same data elsewhere; exports that write to an API's default location instead of a named target.
- **Mech:** M (every write, export and outbound call against the stated promise)
- **Fix:** move the side path inside the promise, replace it with a local alternative, or narrow the promise and record the exception with its control; name the target of every export explicitly.
- **Impact:** a promise true for one path and false for another is the first thing an audit or breach investigation finds.
- **Source:** GDPR Art. 5(2) (accountability), Art. 30, 44.

### PRV-17 [CRITICAL] No breach response that meets the deadlines
- **Detect:** no incident and breach procedure; no named contact or decision owner; the procedure waits for a complete investigation before notifying; no record kept of every incident including those not notified; deadlines for the product's jurisdictions not written down.
- **Mech:** T `git ls-files | grep -iE 'incident|breach|runbook|postmortem|SECURITY\.md'`
- **Fix:** write the procedure from [breach-notification](../templates/breach-notification.md): detect, contain, assess, notify the authority within the shortest applicable deadline with what is known and follow up in phases, tell affected users when the risk is high, record every incident.
- **Impact:** a late notification is a separate violation on top of the breach.
- **Source:** GDPR Art. 33–34; ENISA, Recommendations for a methodology of the assessment of severity of personal data breaches.
