# Rule index — which file to read, when

Read a file only when its signal holds (`../signals.md`); `unknown` loads it. An area's word (first column) limits a run to the named areas: `/ds-audit sec a11y`. Each rule: `### ID [SEVERITY] Title`, then Detect / Fix / Impact / Source; an `applies_when:` line narrows one rule further. Severity and reporting: `../kernel.md` §4. IDs are unique across all files.

**Dated facts** (policy names, thresholds, fines, deadlines, store guidelines) are a verified seed, never the authority: re-check any fact a finding depends on against the live official source; the live source wins. Offline → use the seed and mark the finding `unverified-currency`.

The **Standards** column names what the area is checked against — apply them by name, the same way as `../kernel.md` §7.

| Area (word) | Files | Load when | IDs | Standards |
|------|-------|-----------|-----|-----------|
| `sec` | security.md · security-arch.md · network.md · `../secret-patterns.md` | always | SEC · SAR · NWK | OWASP Top 10 (2025) · OWASP ASVS 5.0 · OWASP API Security Top 10 · NIST SSDF (SP 800-218) · HSTS |
| `privacy` | privacy.md · templates: [dpia](../templates/dpia.md), [breach-notification](../templates/breach-notification.md), [privacy-policy](../templates/privacy-policy.md), [processor-registry](../templates/processor-registry.md) | `pii=yes` | PRV | GDPR · UK GDPR · KVKK · CCPA/CPRA · LGPD · PIPL · ePrivacy · EU AI Act · PCI DSS |
| `auth` | auth.md | `auth≠none` | AUTH | RFC 9700 (OAuth 2.0 Security BCP) · NIST SP 800-63B |
| `api` | api.md | `api≠none` | API | RFC 9457 Problem Details · OpenAPI · OWASP API Security Top 10 |
| `db` | database.md · data-pipeline.md | `db≠none` | DB · DP | 3-2-1 backups · expand/contract migrations |
| `arch` | engineering.md · architecture-testing.md · architecture-rubric.md · review-strategic.md | always | ARC | SOLID · GRASP · Twelve-Factor |
| `code` | review-tactical.md · review-meta.md · simplify.md | always | — | DRY/SSOT · KISS · YAGNI · SoC · cyclomatic complexity |
| `test` | testing.md · architecture-testing.md | always (`tests=none` is itself a finding) | TST | test pyramid · mutation testing · property-based testing · contract testing (Pact) |
| `perf` | performance.md · performance-runtime.md · review-performance.md | `ui≠none` or `api≠none` | PRF · NET · COST · RTP | Core Web Vitals (LCP, INP, CLS) · RFC 9110 caching semantics |
| `web` | web.md | `ui∋web` | WEB | HSTS · CSP · Core Web Vitals |
| `a11y` | a11y.md | `ui≠none` | AXE | WCAG 2.2 AA · WAI-ARIA APG · EN 301 549 · EAA |
| `ux` | ux.md · ui-components.md · ui-design-system.md · ui-responsive.md · ui-scheduling.md | `ui≠none` (scheduling: calendar/booking UI present) | UX · CMP · INT · THM · TOK · RSP · SCH | Nielsen's 10 heuristics · Fitts / Hick / Jakob / Tesler / Postel laws · W3C Design Tokens (DTCG) |
| `i18n` | i18n.md | `i18n=yes` or `audience=public` | I18N | Unicode CLDR · ICU MessageFormat |
| `mobile` | mobile-engineering.md · mobile-experience.md · mobile-compliance.md · mobile-release.md | `mobile≠none` | MARC · MNET · MPRF · MTST · DEV · HYB · MUX · VIS · MPRV · MSEC · STO · REL | OWASP MASVS · Apple App Review Guidelines · Google Play policies |
| `store` | store.md · store-aso.md · templates: [store-submission](../templates/store-submission.md), [store-privacy-labels](../templates/store-privacy-labels.md) | `deploy=store` | LCH | Apple App Review Guidelines · Google Play policies |
| `money` | monetization.md · pricing.md · gtm.md | `billing≠none` | MON · PRC · GTM · pricing IDs | PCI DSS scope · store billing rules |
| `ci` | ci.md · dependencies.md · dependencies-advisories.md · signing.md · release.md | `ci≠none`, or any lockfile | DOP | SLSA · SBOM (SPDX / CycloneDX) · Conventional Commits · Semantic Versioning |
| `ops` | deployment.md · monitoring.md | `deploy≠none` | DEP · OBS | Twelve-Factor · CIS Benchmarks · Kubernetes Pod Security Standards · OpenTelemetry · golden signals · 3-2-1 backups |
| `docs` | docs.md · docs-gaps.md · ai-context.md | always | DOC | Keep a Changelog · ADRs · AGENTS.md |
| `repo` | repo.md | a git remote exists | RPO | community health files (LICENSE, SECURITY.md, CONTRIBUTING) · SPDX license IDs |
