# Data Breach Notification Procedure Template

**{APP_NAME} — Incident Response Plan**

| Field | Value |
|-------|-------|
| Version | {VERSION} |
| Date | {DATE} |
| Owner | {OWNER} |
| Review due | {DATE + 1 year} |

## 1. Scope

Detection, assessment, containment, notification and remediation of personal data breaches affecting {APP_NAME} users, across the application, its infrastructure and its processors.

## 2. Deadlines

Keep only the rows for the jurisdictions the product serves; re-check each against the live official source when adopting this plan.

| Regime | Authority | Individuals | Trigger |
|--------|-----------|-------------|---------|
| GDPR / UK GDPR | 72 hours from awareness (Art. 33) | Without undue delay (Art. 34) | Authority: unless unlikely to result in risk. Individuals: high risk |
| KVKK (Turkey) | 72 hours (Art. 12(5) as set by Board decision 2019/10) | As soon as possible after identifying them | Any breach of personal data |
| US states (e.g. California) | State attorney general above a resident threshold (CA: more than 500) | Most expedient time possible (Cal. Civ. Code §1798.82) | Unencrypted personal information acquired |
| LGPD (Brazil) | Within the period ANPD's regulation sets | Same | Risk or relevant damage to data subjects |
| Others | {deadline} | {deadline} | {trigger} |

**Binding target:** the shortest deadline among the rows kept. When the assessment cannot finish in time, notify with what is known and follow up in phases (GDPR Art. 33(4)) — never hold the notification for completeness.

## 3. Severity

Classify upward under uncertainty: "unknown whether personal data was accessed" is at least High.

| Level | Criteria | Notification |
|-------|----------|--------------|
| Critical | Confirmed access to or exfiltration of personal data; auth bypass | Authority per §2; individuals when risk is high |
| High | Possible access; encrypted data exposed with key status unknown | Authority per §2 unless risk is assessed as unlikely, with the reasoning recorded |
| Medium | Exposure with evidence of no access | Record; authority if the assessment changes |
| Low | No personal data involved | Record only |

## 4. Response

1. **Detect and record** — time of awareness, source of the report, what data, how many people, which systems.
2. **Contain** — revoke and rotate exposed credentials, disable the affected path, preserve logs and evidence before fixing.
3. **Assess** — data categories, number and location of people affected (decides the regimes in §2), whether data was encrypted and the key safe, likely consequences.
4. **Notify the authority** — nature of the breach, categories and approximate numbers of people and records, contact point, likely consequences, measures taken or proposed.
5. **Notify individuals** (when required) — plain language, in the user's language: what happened, what data, what was done, what they should do, whom to contact.

   > **Security notice** — On {date} we found {what happened}. It may have affected {data types}. We have {actions taken}. We recommend you {user actions}. Questions: {CONTACT}.

6. **Remediate and review** — root cause, permanent fix, verification, updates to the DPIA and this plan, a post-incident report.
7. **Register** — every incident goes in the breach register, including those not notified, with the reasoning (GDPR Art. 33(5)).

## 5. Factors that change the assessment

| Factor | Effect |
|--------|--------|
| {Encryption at rest and key custody} | {Data encrypted with an uncompromised key may not need individual notice — GDPR Art. 34(3)(a)} |
| {What logs and backups hold} | {Whether a log or backup leak exposes personal data} |
| {Processors involved} | {Their contractual duty and deadline to tell you} |
| {Payment data handling} | {Stored, or delegated to the payment provider} |

## 6. Contacts

| Role | Contact |
|------|---------|
| Incident owner | {CONTACT} |
| Data protection officer or privacy contact | {DPO_CONTACT} |
| Legal counsel | {LEGAL_CONTACT} |

## 7. Review log

| Date | Reviewer | Change |
|------|----------|--------|
| {DATE} | {NAME} | Procedure created |

*Template — adapt to the product's infrastructure and jurisdictions. Not legal advice.*
