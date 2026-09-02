# Data Breach Notification Procedure Template

**{APP_NAME} — Incident Response Plan**

| Field | Value |
|-------|-------|
| Version | {VERSION} |
| Date | {DATE} |
| Owner | {TEAM_NAME} |
| Review Due | {DATE + 1 year} |

---

## 1. Scope

This procedure covers the detection, assessment, containment, notification, and remediation of personal data breaches affecting {APP_NAME} users. It applies to all data processed by the {APP_NAME} application and backend infrastructure.

---

## 2. Regulatory Timelines

| Regulation | Authority Notification | User Notification | Conditions |
|-----------|----------------------|-------------------|------------|
| GDPR (EU) | 72 hours from awareness | Without undue delay | If breach likely results in high risk to rights/freedoms |
| KVKK (Turkey) | 72 hours from awareness | As soon as possible | All breaches involving personal data |
| CCPA (California) | N/A (no authority notification) | Most expedient time possible | If unencrypted personal information is involved |
| LGPD (Brazil) | Reasonable timeframe | Reasonable timeframe | If breach may cause significant risk or damage |
| UK GDPR | 72 hours from awareness | Without undue delay | If breach likely results in high risk to rights/freedoms |

**Binding target:** 72 hours from breach awareness to authority notification (strictest common deadline).

---

## 3. Breach Severity Classification

| Level | Criteria | Examples | Response |
|-------|----------|----------|----------|
| P1 — Critical | Active data exfiltration, auth bypass, unencrypted PII exposed | Server compromise, token leak, database dump | Immediate containment, 24h authority notification |
| P2 — High | Potential access to personal data, encrypted data exposed | Certificate bypass, API vulnerability, encrypted backup exposed | Containment within 4h, 48h authority notification |
| P3 — Medium | Limited exposure, no evidence of access | Misconfigured logging exposing PII, error reporting redaction failure | Containment within 24h, 72h authority notification |
| P4 — Low | No personal data involved | Service outage, non-PII config exposure | Document and review, no external notification required |

---

## 4. Response Procedure

### Phase 1: Detection & Triage (0–1 hour)

1. **Detect** — Breach identified via monitoring, user report, security researcher, or internal audit.
2. **Triage** — Assign severity level (P1–P4) based on classification above.
3. **Assemble** — Notify incident response team:
   - Engineering lead
   - Data Protection Officer (DPO)
   - Legal counsel (P1/P2)
4. **Document** — Create incident record with:
   - Timestamp of detection
   - Nature of breach (what data, how many users, attack vector)
   - Initial severity assessment

### Phase 2: Containment (1–4 hours)

1. **Isolate** — Revoke compromised credentials, rotate API keys, disable affected endpoints.
2. **Preserve** — Capture logs and forensic evidence before remediation.
3. **Assess scope** — Determine:
   - Number of affected users
   - Types of data exposed
   - Geographic distribution of affected users (determines applicable regulations)
   - Whether data was encrypted at rest/in transit
4. **Mitigate** — Apply immediate fixes (patch vulnerability, block attack vector).

### Phase 3: Authority Notification (within 72 hours)

**GDPR (EU DPA):**
- Notify lead supervisory authority via official breach notification form.
- Include: nature of breach, categories/approximate number of data subjects, DPO contact, likely consequences, measures taken.
- If full details unavailable within 72h, provide initial notification and supplement later.

**KVKK (Turkey — KVKK Board):**
- Notify via the Data Breach Notification System.
- Include: breach description, affected data categories, number of affected persons, measures taken, contact details.

**CCPA (California):**
- No authority notification required unless >500 California residents affected (then notify CA Attorney General).
- Ensure user notification complies with Cal. Civ. Code § 1798.82.

**LGPD (Brazil — ANPD):**
- Notify within reasonable timeframe.
- Include: nature of affected data, affected data subjects, technical measures, risks, measures adopted.

### Phase 4: User Notification

**When required** (high risk to rights/freedoms, or unencrypted PII exposed):

1. **Channel:** In-app notification + email to affected users.
2. **Content:**
   - Plain language description of what happened
   - Types of data involved
   - What you have done to address the breach
   - What users should do (e.g., change passwords, rotate tokens)
   - Contact information for questions
3. **Language:** Notification in user's preferred app language.
4. **Timeline:** Without undue delay after containment, and within regulatory deadlines.

**Template:**

> **Security Notice**
>
> We detected {brief description} on {date}. This may have affected {data types}. We have {actions taken}. As a precaution, we recommend {user actions}. For questions, contact {SECURITY_EMAIL}.

### Phase 5: Remediation & Review (1–4 weeks)

1. **Root cause analysis** — Identify underlying vulnerability and how it was exploited.
2. **Permanent fix** — Deploy code/infrastructure changes to prevent recurrence.
3. **Verify** — Confirm fix effectiveness through testing.
4. **Update documentation** — Revise DPIA, security docs, and this procedure if needed.
5. **Post-incident report** — Document lessons learned, timeline, and improvements.
6. **Regulatory follow-up** — Provide supplementary information to authorities if requested.

---

## 5. App-Specific Considerations

Document factors that affect your breach assessment:

| Factor | Impact on Breach Assessment |
|--------|---------------------------|
| {Data processing model — RAM-only, persistent, etc.} | {How this reduces/increases risk} |
| {Encryption at rest} | {Encrypted data breach may not require user notification per GDPR Art. 34(3)(a)} |
| {Transport security} | {Certificate pinning, TLS version} |
| {PII redaction in logs} | {Breach of logs exposes only redacted data} |
| {Payment data handling} | {Whether payment data is stored or delegated to platform} |

---

## 6. Contact Information

| Role | Contact |
|------|---------|
| Security Team | {SECURITY_EMAIL} |
| Data Protection Officer | {DPO_EMAIL} |
| Privacy Inquiries | {PRIVACY_EMAIL} |

---

## 7. Review Log

| Date | Reviewer | Changes |
|------|----------|---------|
| {Date} | {Name} | Breach notification procedure created |

---

*Template — customize for your specific app's infrastructure and data processing. This is not legal advice.*
