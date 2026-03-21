# Data Processor Registry Template

**{APP_NAME} — Sub-Processor and Third-Party Service Registry**

| Field | Value |
|-------|-------|
| Version | {VERSION} |
| Date | {DATE} |
| Owner | {TEAM_NAME} |
| Review Due | {DATE + 1 year} |

---

## 1. Purpose

This registry lists all third-party services (sub-processors) that process personal data on behalf of {APP_NAME}, as required by GDPR Article 28, KVKK Article 12, and other applicable data protection regulations. Each entry documents the service, data processed, legal basis, and safeguards.

---

## 2. Processor Registry

### Template Entry

For each sub-processor, document:

| Field | Detail |
|-------|--------|
| Service | {What the service does} |
| Entity | {Legal entity name} |
| Location | {Country/Region} |
| Data Processed | {Specific data types processed} |
| Data NOT Processed | {Explicitly excluded data types} |
| Legal Basis (GDPR) | {Art. 6(1)(a/b/f)} |
| Legal Basis (KVKK) | {Turkish legal basis} |
| User Control | {Opt-out, consent, etc.} |
| DPA Status | {Signed / Pending / N/A} |
| Transfer Mechanism | {SCCs, DPF, adequacy, consent} |
| Retention | {Retention policy} |
| Safeguards | {PII redaction, encryption, etc.} |

---

### Common Processor Types

#### Crash Reporting Service (e.g., Sentry, Crashlytics)

| Field | Detail |
|-------|--------|
| Service | Crash reporting and error monitoring |
| Data Processed | PII-redacted crash reports, error stack traces, device metadata |
| Data NOT Processed | User content, authentication tokens, email addresses (redacted) |
| Legal Basis (GDPR) | Art. 6(1)(f) Legitimate interest (app stability) |
| User Control | Opt-out available in privacy settings |
| Safeguards | Client-side PII redaction before transmission |

#### Authentication Provider (e.g., Google Sign-In, Apple Sign-In)

| Field | Detail |
|-------|--------|
| Service | Authentication (OpenID Connect) |
| Data Processed | Account ID, email address, display name (for OIDC token issuance) |
| Data NOT Processed | Contacts, calendars, browsing history, location |
| Legal Basis (GDPR) | Art. 6(1)(b) Contract performance (authentication) |
| User Control | User chooses sign-in method; can sign out and delete account |
| Scope | `openid`, `email`, `profile` scopes only |

#### Payment Processor (e.g., App Store IAP, Stripe)

| Field | Detail |
|-------|--------|
| Service | Payment processing |
| Data Processed | Purchase receipts, product IDs, transaction IDs |
| Data NOT Processed | Credit card numbers, payment method details, billing address |
| Legal Basis (GDPR) | Art. 6(1)(b) Contract performance (billing) |
| User Control | Purchases managed through platform account |
| Your App Receives | Purchase receipt token only (for server-side validation) |

#### Analytics Service (e.g., Plausible, PostHog, GA4)

| Field | Detail |
|-------|--------|
| Service | Usage analytics |
| Data Processed | {Anonymized events, page views, etc.} |
| Data NOT Processed | {PII, precise location, etc.} |
| Legal Basis (GDPR) | Art. 6(1)(a) Consent |
| User Control | Opt-in/opt-out in privacy settings |
| Safeguards | {IP anonymization, no cross-site tracking, etc.} |

---

## 3. Data Flow Diagram Template

```
User Device                    Your Server                    Third Parties
─────────────                  ──────────────────             ─────────────

[User Input]
    │
    ▼
[Local Processing]
    │ (TLS encrypted)
    ▼
    ├──────────────────────► [Server Processing]
    │                            │
    │                            ▼
    │◄──────────────────── [Result + Checksum]
    │                            │
    ▼                            ▼
[ACK] ────────────────────► [Delete processed data]

[Auth tokens] ◄──────────────────────────────────── [Auth Provider]
[Purchase receipts] ◄─────────────────────────────── [Payment Platform]
[PII-redacted errors] ────────────────────────────► [Crash Reporting]
[Anonymized events] ──────────────────────────────► [Analytics]
```

---

## 4. Processor Change Notification

Per GDPR Article 28(2), {APP_NAME} will:

1. Maintain this registry as a living document.
2. Notify users of new sub-processors via in-app notice or privacy policy update.
3. Allow users to object to new processors by providing an account deletion option.
4. Require DPA/SCC coverage for any new processor handling personal data.

---

## 5. Annual Review Checklist

- [ ] All processors still in active use
- [ ] DPA/SCC status current for each processor
- [ ] Transfer mechanisms still valid (check adequacy decisions)
- [ ] Data minimization verified (no scope creep)
- [ ] User opt-out controls functional
- [ ] Retention policies aligned with current practices

---

## 6. Review Log

| Date | Reviewer | Changes |
|------|----------|---------|
| {Date} | {Name} | Processor registry created with {N} sub-processors |

---

*Template — customize for your specific app's processor relationships. This is not legal advice.*
