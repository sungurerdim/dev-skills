# Rules: Analytics Design & Privacy

Rules for design/setup/audit modes. Each rule: ID, severity, title, detect pattern, fix action, source.

Applies to all project types with analytics: web, mobile, API, desktop.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Event Taxonomy** | EVT-01–04 (2 HIGH, 2 MEDIUM) | ~14 |
| **Privacy & Consent** | PVA-01–04 (2 HIGH, 1 MEDIUM, 1 LOW) | ~62 |

---

## Event Taxonomy

### EVT-01 [HIGH] Event Naming Convention

Events use verb_noun format in snake_case, consistent across entire application.

- **Detect:** Mixed naming patterns in event tracking calls (camelCase, PascalCase, inconsistent verb/noun order). Grep for analytics track/log calls and check naming consistency.
- **Fix:** Standardize all events to `verb_noun` snake_case format (e.g., `button_clicked`, `page_viewed`, `form_submitted`, `item_purchased`). Create naming guide and lint rule to enforce it.
- **Impact:** Inconsistent naming makes funnel analysis unreliable and creates duplicate event counts
- **Source:** Segment Analytics Academy, Mixpanel Naming Best Practices Guide

### EVT-02 [HIGH] Minimum Viable Taxonomy

Track only events that inform a specific business decision. Every event maps to a question.

- **Detect:** More than 50 distinct event types without a documented purpose map. Events tracked "just in case" with no associated dashboard or query.
- **Fix:** Map each event to a business question it answers (e.g., `signup_completed` answers "How many users complete registration?"). Remove events that don't inform decisions. Document mapping in a taxonomy file.
- **Impact:** Event bloat increases costs, slows queries, and dilutes focus on actionable metrics
- **Source:** Amplitude Data Taxonomy Playbook, PostHog Event Tracking Guide

### EVT-03 [MEDIUM] Funnel Definition

Key user journeys mapped to AARRR framework with corresponding events at each stage.

- **Detect:** No funnel definitions in analytics config or documentation. Events exist but no defined conversion paths between them.
- **Fix:** Define 3-5 key funnels mapped to AARRR stages:
  - **Acquisition:** `page_viewed`, `app_opened`
  - **Activation:** `signup_completed`, `onboarding_finished`
  - **Retention:** `session_started` (returning), `feature_used`
  - **Revenue:** `purchase_completed`, `plan_upgraded`
  - **Referral:** `invite_sent`, `share_clicked`
- **Impact:** Without funnels, analytics data exists but provides no actionable conversion insights
- **Source:** Dave McClure AARRR Framework, Amplitude Funnel Analysis Guide

### EVT-04 [MEDIUM] Property Standardization

Common properties (user_id, session_id, platform, app_version) attached to every event.

- **Detect:** Inconsistent properties across events. Some events missing user_id or session_id. Platform/version not included in event payloads.
- **Fix:** Define global properties set once per session and attached to all events automatically:
  - `user_id` (hashed, not PII)
  - `session_id`
  - `platform` (web/ios/android)
  - `app_version`
  - `locale`
  Configure analytics SDK to auto-attach these via middleware or identify calls.
- **Impact:** Missing properties make cross-platform analysis and debugging unreliable
- **Source:** Segment Tracking Plan Documentation, PostHog Properties Guide

---

## Privacy & Consent

### PVA-01 [HIGH] Consent Before Tracking

No analytics SDK initialization before user consent (where legally required).

- **Detect:** Analytics SDK init at application startup without a consent gate. SDK loaded unconditionally in index.html or main entry point. No consent management platform (CMP) integration.
- **Fix:** Gate analytics init behind consent check. Load SDK only after user grants consent. For privacy-first tools (Plausible, Umami): consent banner may not be required in EU, but document legal basis. For tools requiring consent (GA4, Mixpanel, Amplitude): integrate CMP and defer init.
- **Impact:** Tracking without consent violates GDPR/ePrivacy and exposes project to legal risk
- **Source:** GDPR Article 6, ePrivacy Directive Article 5(3), ICO Cookie Guidance

### PVA-02 [HIGH] No PII in Events

No email, name, phone number, IP address, or other personally identifiable information in event properties.

- **Detect:** PII fields in event payloads (email, name, phone, ip_address, address). Check analytics track calls for properties containing raw user data. Review network requests to analytics endpoints for PII leaks.
- **Fix:** Hash or remove PII before sending to analytics. Use anonymous identifiers only. Configure server-side analytics to strip IP addresses. Add a pre-send hook to redact known PII fields.
- **Impact:** PII in analytics violates privacy regulations and creates data breach liability
- **Source:** GDPR Article 4 (definition of personal data), CCPA Section 1798.140, OWASP Privacy Risks

### PVA-03 [MEDIUM] Data Retention Policy

Defined retention period with automatic deletion for analytics data.

- **Detect:** No retention policy configured in analytics platform. Self-hosted analytics database growing without bounds. No documented data lifecycle policy.
- **Fix:** Set 90-day default retention period (adjust based on business needs, document reason). Configure auto-delete in analytics platform. For self-hosted: set up cron job or database policy to purge old data. Document retention policy in project's privacy documentation.
- **Impact:** Indefinite data retention increases storage costs and regulatory exposure
- **Source:** GDPR Article 5(1)(e) (storage limitation), NIST SP 800-188

### PVA-04 [LOW] Opt-Out Mechanism

Users can disable analytics tracking via an accessible UI toggle.

- **Detect:** No opt-out toggle in application settings. No documented way for users to disable tracking. Opt-out exists but does not take effect immediately.
- **Fix:** Add analytics opt-out toggle in settings or preferences screen. When toggled off: stop all event tracking immediately, clear any pending event queue, and respect setting on next session. Store preference locally (not via analytics).
- **Impact:** Missing opt-out reduces user trust and may not meet regulatory requirements in some jurisdictions
- **Source:** GDPR Article 7(3) (right to withdraw consent), Apple App Store Guidelines 5.1.2
