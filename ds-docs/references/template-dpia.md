# Data Protection Impact Assessment (DPIA) Template

**{APP_NAME} — {SERVICE_DESCRIPTION}**

| Field | Value |
|-------|-------|
| Version | {VERSION} |
| Date | {DATE} |
| Owner | {TEAM_NAME} |
| Review Due | {DATE + 1 year} |
| Status | Active |

---

## 1. Processing Description

### 1.1 Nature of Processing

{APP_NAME} processes {describe data types} through {describe processing method}. The processing flow is:

1. User {initiates action} on their device.
2. Data is {preprocessed locally if applicable}.
3. Data is uploaded to {APP_NAME} servers over TLS {with certificate pinning if applicable}.
4. Server processes data {in RAM / with persistent storage — specify}.
5. Result is returned to the client {with integrity verification if applicable}.
6. Client acknowledges receipt; server {deletes / retains — specify} data.
7. Result is stored locally on-device {with encryption details}.

### 1.2 Scope of Processing

| Data Category | Collected | Retained Server-Side | Retained Client-Side |
|---------------|-----------|---------------------|---------------------|
| {Category 1} | {Yes/No} | {Duration/Policy} | {Duration/Policy} |
| {Category 2} | {Yes/No} | {Duration/Policy} | {Duration/Policy} |
| Authentication ID | {Yes/No} | {Duration} | {Storage method} |
| Email address | {Yes/No} | {Storage policy} | {Storage policy} |
| Purchase receipts | {Yes/No} | {Storage policy} | {Storage policy} |
| Crash reports | {Yes/No} | {Retention policy} | Not stored |
| IP addresses | Transit only | {Logged/Not logged} | Not stored |

### 1.3 Context of Processing

- **Data subjects:** {End users, employees, etc.} ({age rating if applicable})
- **Relationship:** {Direct B2C / B2B / etc.}, users provide informed consent before first use
- **Technology:** {AI/ML model, database, etc.}
- **Data volume:** {Individual/batch processing description}
- **Geographic scope:** {Regions of availability, server locations}

### 1.4 Purpose of Processing

- Primary: {Core service purpose}
- Secondary: {Billing, analytics, etc.}

---

## 2. Necessity and Proportionality Assessment

### 2.1 Lawful Basis

| Processing Activity | Legal Basis (GDPR) | KVKK Basis | CCPA Category |
|--------------------|--------------------|------------|---------------|
| {Core processing} | Art. 6(1)(b) Contract | {Basis} | Service delivery |
| Authentication | Art. 6(1)(b) Contract | {Basis} | Service delivery |
| Billing | Art. 6(1)(b) Contract | {Basis} | Service delivery |
| Crash reporting | Art. 6(1)(f) Legitimate interest | {Basis} | Business purpose |
| Analytics | Art. 6(1)(a) Consent | {Basis} | Business purpose |

### 2.2 Necessity

- {Processing 1} is strictly necessary for {reason — why no less-invasive alternative}.
- {Processing 2} is necessary for {reason}.
- {Processing 3} is necessary for {reason}; PII is {redacted/minimized} before transmission.

### 2.3 Proportionality

- {Data minimization measure 1}
- {Data minimization measure 2}
- No data retained for model training or improvement {if applicable}
- Users can delete all local data at any time

### 2.4 Data Subject Rights

| Right | Implementation |
|-------|---------------|
| Access (Art. 15) | {How users access their data} |
| Rectification (Art. 16) | {How users correct their data} |
| Erasure (Art. 17) | {Account/data deletion mechanism} |
| Restriction (Art. 18) | {How users restrict processing} |
| Portability (Art. 20) | {Data export mechanism} |
| Object (Art. 21) | {Opt-out mechanisms} |
| Withdraw consent | {How users withdraw consent} |

---

## 3. Risk Assessment

### 3.1 Identified Risks

| # | Risk | Likelihood | Severity | Inherent Risk |
|---|------|-----------|----------|---------------|
| R1 | {Data contains sensitive information} | {L/M/H} | {L/M/H} | {L/M/H} |
| R2 | {Unauthorized access in transit} | {L/M/H} | {L/M/H} | {L/M/H} |
| R3 | {Server-side data breach} | {L/M/H} | {L/M/H} | {L/M/H} |
| R4 | {Unauthorized access to local storage} | {L/M/H} | {L/M/H} | {L/M/H} |
| R5 | {PII leakage through logs/diagnostics} | {L/M/H} | {L/M/H} | {L/M/H} |
| R6 | {Cross-border data transfer} | {L/M/H} | {L/M/H} | {L/M/H} |
| R7 | {AI/ML accuracy risks} | {L/M/H} | {L/M/H} | {L/M/H} |

### 3.2 Mitigations

| # | Mitigation | Controls | Residual Risk |
|---|-----------|----------|---------------|
| R1 | {Mitigation description} | {Specific controls} | {L/M/H} |
| R2 | {Transport encryption details} | {TLS version, pinning, etc.} | {L/M/H} |
| R3 | {Access control measures} | {Specific controls} | {L/M/H} |
| R4 | {Encryption at rest} | {Algorithm, key storage} | {L/M/H} |
| R5 | {PII redaction pipeline} | {What is redacted, when} | {L/M/H} |
| R6 | {Transfer mechanisms} | {SCCs, DPF, consent} | {L/M/H} |
| R7 | {Accuracy safeguards} | {Human review, disclaimers} | {L/M/H} |

---

## 4. Consultation

### 4.1 Data Subjects

- Users are informed of processing via {consent screen, privacy policy, etc.}.
- {Specific disclosures about technology used}
- Users can withdraw consent and delete their account at any time.

### 4.2 DPO / Legal

- This DPIA should be reviewed by the designated Data Protection Officer.
- Annual review cycle or upon significant processing changes.

---

## 5. Decision

Based on the assessment above, the residual risks are **{Low/Medium/High}** after mitigations are applied. {Decision: proceed / proceed with conditions / do not proceed}.

| Approved By | Date | Next Review |
|-------------|------|-------------|
| {DPO Name} | {Date} | {Review date} |

---

## 6. Review Log

| Date | Reviewer | Changes |
|------|----------|---------|
| {Date} | {Name} | DPIA created covering {scope description} |

---

*Template — customize for your specific app's data processing activities. This is not legal advice — consult with a data protection professional.*
