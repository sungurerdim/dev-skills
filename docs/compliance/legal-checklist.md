# Legal Compliance Checklist

> **DISCLAIMER: THIS DOCUMENT DOES NOT CONSTITUTE LEGAL ADVICE.**
> This checklist is provided for informational and organizational purposes only. It is not a substitute for professional legal counsel. Laws and regulations change frequently. Consult a qualified attorney in {JURISDICTION} before making compliance decisions for {APP_NAME} operated by {COMPANY_NAME}. Last reviewed: 2026-03-20.

---

## Table of Contents

1. [Terms of Service](#1-terms-of-service)
2. [Privacy Policy](#2-privacy-policy)
3. [Cookie & Tracking Consent](#3-cookie--tracking-consent)
4. [Age Verification & COPPA](#4-age-verification--coppa)
5. [GDPR Compliance](#5-gdpr-compliance)
6. [CCPA/CPRA Compliance](#6-ccpacpra-compliance)
7. [Data Processing Agreements](#7-data-processing-agreements)
8. [International Data Transfers](#8-international-data-transfers)
9. [App Store Legal Requirements](#9-app-store-legal-requirements)
10. [Open Source License Compliance](#10-open-source-license-compliance)
11. [Accessibility Legal Requirements](#11-accessibility-legal-requirements)
12. [Record-Keeping & Audit Trail](#12-record-keeping--audit-trail)
13. [Sources](#13-sources)

---

## 1. Terms of Service

### Required Clauses

| Clause | Purpose | Notes |
|--------|---------|-------|
| Acceptance of terms | Binding agreement | Click-wrap or sign-in-wrap |
| License grant & restrictions | Scope of use | Non-exclusive, revocable |
| User obligations & conduct | Acceptable use | Prohibited activities list |
| Intellectual property | Ownership | {COMPANY_NAME} retains all IP |
| Limitation of liability | Cap on damages | Per {JURISDICTION} enforceability |
| Disclaimer of warranties | "As-is" provision | Must be conspicuous |
| Termination & suspension | Account closure | Notice period, data export window |
| Governing law & dispute resolution | Jurisdiction | Arbitration vs. litigation |
| Modification clause | Right to update | Reasonable notice requirement |
| Severability | Partial invalidity | Standard boilerplate |
| Contact information | Reachability | Physical address if required by law |

### App-Type Additions

- [ ] **SaaS/Subscription**: Auto-renewal terms, cancellation policy, refund policy
- [ ] **Marketplace**: Seller/buyer responsibilities, commission terms, dispute process
- [ ] **User-Generated Content**: Content license grant, DMCA/takedown procedure, moderation policy
- [ ] **Financial/Payment**: PCI-DSS reference, chargeback policy, payment processor terms
- [ ] **Health/Medical**: Medical disclaimer, not-a-doctor clause, regulatory compliance notice
- [ ] **AI/ML Features**: Output accuracy disclaimer, prohibited use cases, data usage for training

---

## 2. Privacy Policy

### Jurisdiction Requirements Matrix

| Requirement | GDPR (EU/EEA) | CCPA/CPRA (California) | KVKK (Turkey) | LGPD (Brazil) | PIPL (China) |
|-------------|---------------|----------------------|---------------|---------------|--------------|
| Legal basis for processing | Required (Art. 6) | Not required | Required (Art. 5) | Required (Art. 7) | Required (Art. 13) |
| Data categories disclosed | Required | Required | Required | Required | Required |
| Purpose limitation | Strict | Reasonable expectation | Strict | Strict | Strict |
| Data subject rights | Access, rectify, erase, port, restrict, object | Know, delete, correct, opt-out, limit SPI | Access, rectify, erase | Access, rectify, erase, port | Access, copy, rectify, erase, port |
| DPO/representative required | If core activity is processing | No | If core activity is processing | Yes (encarregado) | Yes (designated person) |
| Breach notification | 72 hours to DPA | "Without unreasonable delay" | 72 hours to KVK Board | Reasonable time to ANPD | Immediately to CAC |
| Cross-border transfer rules | SCCs/adequacy/BCRs | Contractual | Explicit consent or Board approval | Adequacy or safeguards | CAC security assessment |
| Children's data age threshold | 13-16 (varies by state) | Under 16 (opt-in for sale) | Parental consent required | Parental consent required | Under 14, parental consent |
| Fines (max) | EUR 20M or 4% revenue | $7,988/intentional violation | TRY 9.8M+ | 2% revenue (BRL 50M cap) | CNY 50M or 5% revenue |

### Privacy Policy Checklist

- [ ] Identity and contact details of {COMPANY_NAME} as controller
- [ ] Categories of personal data collected
- [ ] Purposes and legal basis for each processing activity
- [ ] Data retention periods or criteria
- [ ] Third parties and categories of recipients
- [ ] International transfer mechanisms
- [ ] Data subject rights and how to exercise them
- [ ] Right to lodge a complaint with supervisory authority
- [ ] Automated decision-making/profiling disclosure (if applicable)
- [ ] Date of last update prominently displayed

---

## 3. Cookie & Tracking Consent

### EU ePrivacy Requirements

- [ ] Obtain consent BEFORE setting non-essential cookies
- [ ] Provide granular consent options (not just "Accept All")
- [ ] "Reject All" must be equally prominent as "Accept All"
- [ ] No pre-ticked checkboxes
- [ ] Consent must be freely given, specific, informed, unambiguous
- [ ] Consent records stored with timestamp and scope
- [ ] Easy withdrawal mechanism accessible at all times
- [ ] Re-consent at reasonable intervals (12 months recommended)

### Cookie Categories

| Category | Consent Required | Examples |
|----------|-----------------|----------|
| Strictly necessary | No | Session, auth, security, load balancing |
| Functional/Preferences | Yes | Language, theme, region |
| Analytics/Performance | Yes | Google Analytics, Mixpanel, crash reporting |
| Advertising/Targeting | Yes | Ad networks, retargeting pixels, social media |

### US State Requirements

- [ ] **California (CCPA/CPRA)**: "Do Not Sell or Share My Personal Information" link on homepage
- [ ] **Colorado/Connecticut/Virginia**: Opt-out mechanism for targeted advertising
- [ ] **All applicable states**: Honor Global Privacy Control (GPC) browser signals
- [ ] No dark patterns in opt-out flows (asymmetric design is a violation)

### Mobile App Considerations

- [ ] No cookie banner needed for native mobile apps (cookies are a browser concept)
- [ ] SDK-based tracking (analytics, ad SDKs) still requires consent under GDPR
- [ ] Apple ATT prompt required before accessing IDFA (iOS 14.5+)
- [ ] Document all third-party SDKs and their data collection in privacy policy

---

## 4. Age Verification & COPPA

### COPPA 2025 Amended Rule (Compliance Deadline: April 22, 2026)

- [ ] Identify if {APP_NAME} is directed to children under 13 or is a "mixed audience" service
- [ ] Obtain verifiable parental consent (VPC) before collecting children's data
- [ ] Obtain **separate** VPC for targeted advertising using children's data
- [ ] Update definition of "personal information" to include biometric identifiers, geolocation, government IDs, phone numbers, audio recordings
- [ ] Create and maintain a **written data retention policy** for children's data
- [ ] Delete children's data when no longer needed for original purpose (no indefinite retention)
- [ ] Implement and annually review a **written information security program**
- [ ] Post a clear, comprehensive COPPA-compliant privacy policy
- [ ] Provide parents with access to, and ability to delete, their child's data
- [ ] If using "support for internal operations" exemption, comply with new restrictions

### US State App Store Accountability Acts (ASA Laws)

| State | Effective | Age Categories | Key Requirement |
|-------|-----------|---------------|-----------------|
| Texas (SB 2420) | Jan 1, 2026 | <13, 13-15, 16-17, 18+ | Age verification via platform API, parental consent for minors |
| Utah | May 6, 2026 | Similar tiers | Platform-level age assurance |
| Louisiana | Jul 1, 2026 | Similar tiers | Platform-level age assurance |

- [ ] Integrate Apple Declared Age Range API for iOS
- [ ] Integrate Google Play Age Signals API for Android
- [ ] Implement age-appropriate content filtering based on returned age category
- [ ] Obtain parental consent for significant app changes affecting minors

### EU Age Thresholds for Data Processing Consent (GDPR Art. 8)

| Country | Age of Digital Consent | Country | Age of Digital Consent |
|---------|----------------------|---------|----------------------|
| Austria | 14 | Ireland | 16 |
| Belgium | 13 | Italy | 14 |
| Denmark | 13 | Netherlands | 16 |
| Finland | 13 | Poland | 16 |
| France | 15 | Portugal | 13 |
| Germany | 16 | Spain | 14 |
| Greece | 15 | Sweden | 13 |
| Hungary | 16 | UK (post-Brexit) | 13 |

---

## 5. GDPR Compliance

### Data Mapping & Inventory

- [ ] Identify all personal data collected by {APP_NAME}
- [ ] Document data sources (direct collection, third-party, inferred)
- [ ] Map data flows: collection, storage, processing, sharing, deletion
- [ ] Classify data by sensitivity (standard PI vs. special category data)
- [ ] Identify all processors and sub-processors

### Records of Processing Activities (ROPA) — Art. 30

- [ ] Name and contact details of {COMPANY_NAME} as controller
- [ ] Purposes of processing for each activity
- [ ] Categories of data subjects and personal data
- [ ] Categories of recipients (including third countries)
- [ ] Transfer safeguards (SCCs, adequacy, etc.)
- [ ] Retention periods per category
- [ ] Technical and organizational security measures

### Legal Basis — Art. 6

- [ ] Document the legal basis for **each** processing activity
- [ ] Consent: Freely given, specific, informed, unambiguous; easy withdrawal
- [ ] Contract: Only data necessary for contract performance
- [ ] Legitimate interest: Document balancing test (LIA)
- [ ] Legal obligation: Identify the specific law
- [ ] Never rely on "legitimate interest" for special category data

### Data Subject Access Requests (DSARs)

- [ ] Process to receive and verify DSARs
- [ ] Respond within 30 days (extendable by 60 days for complex requests)
- [ ] Support rights: access, rectification, erasure, portability, restriction, objection
- [ ] Automated export in machine-readable format (JSON, CSV)
- [ ] Log all DSARs with timestamps and outcomes

### Privacy by Design & Default — Art. 25

- [ ] Collect minimum data necessary (data minimization)
- [ ] Pseudonymize or anonymize where possible
- [ ] Default settings are most privacy-protective
- [ ] Privacy considerations documented in feature specs/PRDs
- [ ] Security measures proportionate to data sensitivity

### Data Protection Impact Assessment (DPIA) — Art. 35

- [ ] Conduct DPIA for high-risk processing (profiling, large-scale monitoring, sensitive data)
- [ ] Document: necessity, proportionality, risks, mitigation measures
- [ ] Consult DPA if high residual risk remains after mitigation
- [ ] Review and update DPIA when processing changes materially

### Breach Response — Art. 33-34

- [ ] Incident response plan documented and tested
- [ ] Notify supervisory authority within **72 hours** of becoming aware
- [ ] Notify affected data subjects "without undue delay" if high risk
- [ ] Document all breaches in breach register (even those not reported)
- [ ] Include: nature of breach, categories/numbers affected, consequences, measures taken

---

## 6. CCPA/CPRA Compliance

### Consumer Rights

- [ ] Right to know: What PI is collected, used, shared
- [ ] Right to delete: Honor deletion requests within 45 days
- [ ] Right to correct: Allow correction of inaccurate PI
- [ ] Right to opt-out: Of sale/sharing of PI
- [ ] Right to limit: Use of sensitive personal information (SPI)
- [ ] Right to non-discrimination: No service degradation for exercising rights
- [ ] Provide at least two methods for submitting requests (e.g., web form + email)

### Opt-Out Requirements

- [ ] "Do Not Sell or Share My Personal Information" link on homepage
- [ ] Honor Global Privacy Control (GPC) signals as valid opt-out
- [ ] Process opt-out requests without requiring account creation
- [ ] No "dark patterns": opt-out must be as easy as opt-in
- [ ] "Reject All" and "Accept All" buttons must have equal visual prominence

### Dark Pattern Prohibitions (Effective Jan 1, 2026)

- [ ] No asymmetric choice architecture (making opt-out harder than opt-in)
- [ ] No confusing language designed to steer users toward data sharing
- [ ] Closing a consent banner without clicking does NOT equal consent
- [ ] No repeated prompts to reconsider after user opts out
- [ ] No bundled consent (separate choices for separate purposes)

### Risk Assessments (Effective Jan 1, 2026)

- [ ] Conduct risk assessment before high-risk processing activities
- [ ] Document: purpose, data categories, benefits, risks, mitigations
- [ ] Review and update every 3 years or within 45 days of material change
- [ ] Evaluate third-party vendors in risk assessments

### Key Upcoming Deadlines

| Deadline | Requirement |
|----------|-------------|
| Jan 1, 2026 | Risk assessment obligations begin; dark pattern rules effective |
| Jan 1, 2027 | ADMT pre-use notice requirements |
| Dec 31, 2027 | Pre-2026 processing activities must have completed risk assessments |
| Apr 1, 2028 | First risk assessment submissions due to CPPA |

---

## 7. Data Processing Agreements

### When Required

- [ ] Any third party processing personal data on behalf of {COMPANY_NAME}
- [ ] Cloud hosting providers (AWS, Azure, GCP, etc.)
- [ ] Analytics services, email providers, payment processors
- [ ] Customer support tools, CRM systems
- [ ] Any sub-processor used by your processor

### Required Clauses (GDPR Art. 28)

- [ ] Subject matter, duration, nature, and purpose of processing
- [ ] Types of personal data and categories of data subjects
- [ ] Obligations and rights of the controller
- [ ] Processor acts only on documented instructions from controller
- [ ] Confidentiality obligations for processing personnel
- [ ] Technical and organizational security measures
- [ ] Sub-processor engagement rules (prior authorization or general with notification)
- [ ] Assistance with DSARs and DPIAs
- [ ] Data return or deletion at end of engagement
- [ ] Audit rights for the controller

### DPA Template Structure

```
1. Definitions
2. Scope & Purpose of Processing
3. Controller Obligations
4. Processor Obligations
5. Sub-Processing
6. International Transfers
7. Security Measures (Annex)
8. Data Subject Rights Assistance
9. Breach Notification (within 48h to controller)
10. Audit & Inspection Rights
11. Term, Termination & Data Return
12. Liability
Annex A: Processing Details
Annex B: Technical & Organizational Measures
Annex C: Sub-Processor List
```

---

## 8. International Data Transfers

### Transfer Mechanisms

| Mechanism | Status (as of early 2026) | Use Case |
|-----------|--------------------------|----------|
| EU-US Data Privacy Framework (DPF) | Active; General Court upheld (Sep 2025); appeal pending at CJEU | US processors certified under DPF |
| Standard Contractual Clauses (SCCs) | Valid; use as primary or backup mechanism | Any third-country transfer |
| Binding Corporate Rules (BCRs) | Valid; lengthy approval | Intra-group transfers |
| Adequacy decisions | 15 countries + UK (extended to 2031) + Brazil (forthcoming) | Countries deemed adequate by EC |
| Derogations (Art. 49) | Limited; not for systematic transfers | Explicit consent, contract necessity |

### Transfer Checklist

- [ ] Identify all transfers of personal data outside EEA
- [ ] Verify if destination country has an adequacy decision
- [ ] For US transfers: verify processor is DPF-certified **and** maintain SCCs as fallback
- [ ] Execute SCCs (2021 version) for non-adequate countries
- [ ] Conduct Transfer Impact Assessment (TIA) for each transfer
- [ ] Document supplementary measures if TIA identifies risks
- [ ] Monitor DPF stability (CJEU appeal, PCLOB status, EO 14086 integrity)
- [ ] Review UK adequacy status (extended to 2031, monitor divergence)
- [ ] Re-assess transfers annually or upon legal/political changes

---

## 9. App Store Legal Requirements

### Apple App Store

- [ ] **Privacy Nutrition Labels**: Accurately declare all data collection in App Store Connect
- [ ] **App Tracking Transparency (ATT)**: Request permission via ATT prompt before accessing IDFA
- [ ] **Purpose strings**: Provide clear NSUsageDescription for camera, location, microphone, etc.
- [ ] **Declared Age Range API**: Integrate to receive user age category where required by law
- [ ] **Age ratings**: Select appropriate age rating (4+, 9+, 13+, 16+, 18+)
- [ ] **Kids Category**: If listed, comply with Apple's additional requirements (no third-party analytics/advertising, no login requirements, parental gate for external links)
- [ ] **Privacy policy URL**: Required for all apps; must be publicly accessible
- [ ] **Data deletion**: Provide account and data deletion capability within the app
- [ ] **Third-party SDKs**: Declare privacy manifests for all embedded SDKs

### Google Play Store

- [ ] **Data Safety Section**: Accurately complete data collection/sharing/security declarations
- [ ] **Play Age Signals API**: Integrate for age-appropriate experiences in applicable US states
- [ ] **Families Policy**: If targeting children, comply with Designed for Families requirements
- [ ] **Privacy policy**: Required; must be accessible and accurate
- [ ] **Account deletion**: Provide in-app and web-based account/data deletion
- [ ] **Data handling**: Disclose how Play Age Signals data is used (compliance only, no ads/profiling)
- [ ] **Permissions**: Request only necessary runtime permissions with clear justification

---

## 10. Open Source License Compliance

### License Compatibility Matrix

| License | Permissive | Can mix with proprietary | Must share source | Network copyleft |
|---------|-----------|------------------------|-------------------|-----------------|
| MIT | Yes | Yes | No | No |
| Apache 2.0 | Yes | Yes (patent grant) | No | No |
| BSD 2/3-Clause | Yes | Yes | No | No |
| LGPL 2.1/3.0 | Weak copyleft | Yes (if dynamically linked) | Modified LGPL files only | No |
| MPL 2.0 | Weak copyleft | Yes (file-level) | Modified MPL files only | No |
| GPL 2.0/3.0 | Copyleft | No (derivative = GPL) | Entire derivative work | No |
| AGPL 3.0 | Strong copyleft | No | Entire work, including network use | Yes |

### Compliance Checklist

- [ ] Maintain a software bill of materials (SBOM) listing all dependencies
- [ ] Verify license of every direct and transitive dependency
- [ ] No GPL/AGPL code in proprietary closed-source builds (unless compliant)
- [ ] LGPL: use dynamic linking only; do not statically link into proprietary code
- [ ] Apache 2.0: include NOTICE file and patent grant acknowledgment
- [ ] MIT/BSD: include copyright notice and license text in distribution
- [ ] Preserve all copyright headers and license files in source and binary distributions
- [ ] Automate license scanning in CI/CD (e.g., FOSSA, Snyk, license-checker)
- [ ] Review licenses before adding any new dependency
- [ ] Document license decisions for borderline cases

---

## 11. Accessibility Legal Requirements

### European Accessibility Act (EAA) — Effective June 28, 2025

- [ ] Determine if {APP_NAME} is in scope (e-commerce, banking, transport, communications)
- [ ] Micro-enterprise exemption: <10 FTE **and** <EUR 2M turnover (both conditions required)
- [ ] Meet EN 301 549 standard (incorporates WCAG 2.2 AA)
- [ ] New features/updates must comply immediately; legacy apps exempt until June 28, 2030 (if untouched)
- [ ] Publish an Accessibility Statement
- [ ] Monitor member-state-specific penalties (Spain: EUR 1M; Germany: EUR 500K; France: EUR 300K)

### ADA (United States)

- [ ] Title III applies to "places of public accommodation" — courts increasingly include websites and apps
- [ ] No explicit technical standard mandated, but WCAG 2.1 AA is the de facto benchmark
- [ ] DOJ has referenced WCAG 2.1 AA in settlements and consent decrees
- [ ] Risk of private lawsuits (no statutory damages cap in some circuits)

### WCAG 2.2 AA Checklist (Key Criteria)

**Perceivable**
- [ ] All non-text content has text alternatives (1.1.1)
- [ ] Captions for audio/video content (1.2.2)
- [ ] Content adaptable without loss of meaning (1.3.1)
- [ ] Minimum contrast ratio 4.5:1 for normal text, 3:1 for large text (1.4.3)
- [ ] Text resizable to 200% without loss of content (1.4.4)
- [ ] Content reflows at 320px width without horizontal scrolling (1.4.10)

**Operable**
- [ ] All functionality available via keyboard (2.1.1)
- [ ] No keyboard traps (2.1.2)
- [ ] Skip navigation mechanisms (2.4.1)
- [ ] Focus order is logical (2.4.3)
- [ ] Focus visible indicator (2.4.7 / enhanced: 2.4.11, 2.4.12)
- [ ] Target size minimum 24x24 CSS pixels (2.5.8)
- [ ] Dragging alternatives provided (2.5.7)

**Understandable**
- [ ] Language of page declared (3.1.1)
- [ ] Input labels and instructions provided (3.3.2)
- [ ] Error identification and suggestions (3.3.1, 3.3.3)
- [ ] Consistent navigation and identification (3.2.3, 3.2.4)
- [ ] Redundant entry minimized (3.3.7)

**Robust**
- [ ] Valid, well-formed markup (4.1.1 — deprecated in 2.2 but still good practice)
- [ ] Name, role, value for all UI components (4.1.2)
- [ ] Status messages programmatically determinable (4.1.3)

---

## 12. Record-Keeping & Audit Trail

### Retention Periods by Record Type

| Record Type | Minimum Retention | Authority | Notes |
|-------------|-------------------|-----------|-------|
| ROPA (Records of Processing) | Duration of processing + 3 years | GDPR Art. 30 | Update on any change |
| Consent records | Duration of processing + 5 years | GDPR Art. 7; ePrivacy | Timestamp, scope, method |
| DSARs (requests & responses) | 3 years from resolution | GDPR best practice | Include correspondence |
| DPIAs | 3 years after processing ends | GDPR Art. 35 | Review on material change |
| Data breach register | 5 years minimum | GDPR Art. 33(5); CCPA | All breaches, including non-reported |
| Data Processing Agreements | Duration of contract + 6 years | Contract law varies | Include termination records |
| Privacy policy versions | Indefinite (all versions) | All jurisdictions | Archive each published version |
| Cookie consent records | 2 years (reconsent cycle) | ePrivacy, CNIL guidance | Per-user, per-purpose |
| COPPA parental consent | Duration of account + 3 years | FTC COPPA Rule | Method of verification |
| CCPA consumer requests | 24 months | CCPA Reg. 7101 | Request + response + outcome |
| Security audit reports | 5 years | CCPA/CPRA, ISO 27001 | Include remediation records |
| Open source license records | Life of product + 3 years | License obligations | SBOM, license texts, notices |
| Accessibility audits | 3 years | EAA, ADA settlements | Include remediation timeline |
| Employee privacy training | 3 years from training date | GDPR, CCPA best practice | Attendance + materials |

### Audit Trail Requirements

- [ ] Maintain immutable logs for consent changes, data access, and deletions
- [ ] Log all DSAR submissions, processing steps, and responses
- [ ] Version-control all legal documents (privacy policy, ToS, DPA)
- [ ] Store records in a format that is exportable and searchable
- [ ] Conduct annual internal audit of record completeness
- [ ] Assign a single owner (solo dev: yourself) responsible for record maintenance

---

## 13. Sources

### COPPA & Children's Privacy
- [FTC COPPA Final Rule (Federal Register, Apr 2025)](https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule)
- [FTC COPPA Amendments Overview — Securiti](https://securiti.ai/ftc-coppa-final-rule-amendments/)
- [COPPA Amendments — White & Case](https://www.whitecase.com/insight-alert/unpacking-ftcs-coppa-amendments-what-you-need-know)
- [COPPA Amendments — Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2025/04/ftc-announces-significant-amendments-to-coppa)
- [COPPA Compliance for 2026 — Usercentrics](https://usercentrics.com/knowledge-hub/coppa-compliance/)

### GDPR & EU Data Protection
- [EU-US Data Privacy Framework — Official](https://www.dataprivacyframework.gov/Program-Overview)
- [EU-US Data Transfers in 2025 — Coblentz](https://www.coblentzlaw.com/news/eu-u-s-data-transfers-in-2025/)
- [DPF Survives Challenge — DLA Piper](https://privacymatters.dlapiper.com/2025/09/eu-u-s-data-privacy-framework-survives-first-challenge/)
- [Cross-Border Transfer Developments — Inside Privacy](https://www.insideprivacy.com/cross-border-transfers/roundup-of-cross-border-data-transfer-developments/)

### CCPA/CPRA
- [New CCPA 2026 Regulations Guide — Captain Compliance](https://captaincompliance.com/education/new-ccpa-2026-regulations-your-complete-compliance-action-guide/)
- [CCPA/CPRA Regulations Finalized — Grant Thornton](https://www.grantthornton.com/insights/articles/advisory/2025/privacy-update-ccpa-cpra-regulations-finalized)
- [CCPA 2025 Updated Regulations — DLA Piper](https://www.dlapiper.com/en/insights/publications/2025/09/ccpa-2025-updated-regulations)
- [CPRA Compliance Checklist — Drata](https://drata.com/blog/ccpa-compliance-checklist-2026)

### European Accessibility Act
- [EAA Compliance Guide — Level Access](https://www.levelaccess.com/compliance-overview/european-accessibility-act-eaa/)
- [Developer Guide to EAA 2025 — Chromatic](https://www.chromatic.com/blog/developers-guide-to-european-accessibility-act-2025/)
- [EAA — European Commission Official](https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/european-accessibility-act-eaa_en)
- [EAA Compliance Checklist — WCAG.com](https://www.wcag.com/compliance/european-accessibility-act/)

### App Store Requirements
- [Apple: Design Safe Experiences for Kids](https://developer.apple.com/kids/)
- [Apple: Declared Age Range API Forum Guidance](https://developer.apple.com/forums/thread/810754)
- [Google: Play Age Signals Overview](https://developer.android.com/google/play/age-signals/overview)
- [Countdown to ASA Compliance — FKKS](https://technologylaw.fkks.com/post/102lxsp/countdown-to-jan-1-2026-mobile-developers-must-adopt-apple-google-apis-to-com)
- [Mobile App Legal Requirements 2025 — OpenArc](https://www.openarc.net/mobile-app-legal-requirements-what-most-developers-miss-in-2025/)

### General
- [Website Compliance Laws 2026 — CookieYes](https://www.cookieyes.com/blog/website-compliance-laws/)
- [Data Protection & Privacy 2026 — Chambers](https://practiceguides.chambers.com/practice-guides/data-protection-privacy-2026)
