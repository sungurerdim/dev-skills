# Rule index — which file to read, when

Read a file only when its signal holds (`../signals.md`); `unknown` loads it. An area's word (first column) limits a run to the named areas: `/ds-audit sec a11y`. Each rule: `### ID [SEVERITY] Title`, then Detect / Fix / Impact / Source; an `applies_when:` line narrows one rule further. Severity and reporting: `../kernel.md` §4. IDs are unique across all files.

**Dated facts** (policy names, thresholds, fines, deadlines, store guidelines) are a verified seed, never the authority: re-check any fact a finding depends on against the live official source; the live source wins. Offline → use the seed and mark the finding `unverified-currency`.

The **Standards** column names what the area is checked against — apply them by name, the same way as `../kernel.md` §7.

| Area (word) | Phase | Files | Load when | IDs | Standards |
|------|-------|-------|-----------|-----|-----------|
| `rules` | lean | — (recorded rules and decisions, `audit.py rules`) | always | LEAN-12 | ADRs · Chesterton's fence |
| `lean` | lean | lean.md · simplify.md | always | LEAN | YAGNI · KISS · Gall's law · fitness functions |
| `arch` | build | arch.md | always | ARC · RTP-10 · AIA | SOLID · GRASP · Twelve-Factor · OWASP Top 10 for LLM Applications |
| `code` | build | code.md | always | ARC (code level) · TST-06 | DRY · KISS · cyclomatic and cognitive complexity · CWE-362/367/407/1333 |
| `test` | build | test.md | always (`tests=none` is itself a finding) | TST | test pyramid · mutation testing · property-based testing · contract testing (Pact) · Semantic Versioning |
| `perf` | build | perf.md | `ui≠none` or `api≠none` | PRF · NET · COST · RTP | Core Web Vitals (LCP, INP, CLS) · RFC 9111 HTTP caching · CWE-400/770 |
| `sec` | safe | security.md · `../secret-patterns.md` | always | SEC · SAR · NWK | OWASP Top 10 (2025) · OWASP ASVS 5.0 · OWASP API Security Top 10 · NIST SSDF (SP 800-218) · HSTS |
| `privacy` | safe | privacy.md | `pii=yes` | PRV | privacy by design and data minimization (GDPR Art. 25) · NIST SP 800-122 |
| `auth` | safe | auth.md | `auth≠none` | AUTH | RFC 9700 (OAuth 2.0 Security BCP) · NIST SP 800-63B |
| `api` | safe | api.md | `api≠none` | API | RFC 9457 Problem Details · OpenAPI · OWASP API Security Top 10 |
| `db` | safe | database.md | `db≠none` | DB · DP | OWASP Database Security Cheat Sheet · CIS Benchmarks · expand/contract migrations |
| `web` | surface | web.md | `ui∋web` | WEB · CMP-09 · RSP | Core Web Vitals · Baseline / Browserslist · WCAG 2.2 SC 1.4.10 Reflow |
| `a11y` | surface | a11y.md | `ui∋web` or `ui∋ios` or `ui∋android` or `ui∋desktop` | AXE | WCAG 2.2 AA · WAI-ARIA APG · EN 301 549 clause 11 |
| `ux` | surface | ux.md · cli.md (terminal products) | `ui≠none` or `platforms∋cli` | UX · CMP · INT · TOK · THM · RSP · VIS · SCH · CLI | Nielsen's 10 heuristics · Laws of UX · W3C Design Tokens (DTCG) · clig.dev · POSIX Utility Syntax Guidelines · NO_COLOR |
| `i18n` | surface | i18n.md | `i18n=yes` or `audience=public` | I18N | Unicode CLDR · ICU MessageFormat · UAX #10 and #29 · BCP 47 |
| `mobile` | surface | mobile.md | `mobile≠none` | MUX · MARC · MPRF | Material Design · Apple HIG · Android platform guides |
| `store` | surface | store.md | `deploy=store` or `mobile≠none` | STO · LCH · REL · VIS-14 | Apple App Review Guidelines · Google Play requirements (technical) |
| `money` | surface | monetization.md | `billing≠none` | PRC · UX-DP | store billing APIs · deceptive.design |
| `ci` | ship | ci.md · dependencies.md · dependencies-advisories.md · signing.md · release.md | `ci≠none`, or any lockfile | DOP | SLSA · SBOM (SPDX / CycloneDX) · Conventional Commits · Semantic Versioning |
| `ops` | ship | deployment.md · monitoring.md | `deploy≠none` | DEP · OBS · COST | Twelve-Factor · CIS Benchmarks · Kubernetes Pod Security Standards · OpenTelemetry · golden signals · 3-2-1 backups |
| `docs` | ship | docs.md · docs-gaps.md · ai-context.md | always | DOC | Keep a Changelog · ADRs · AGENTS.md |
| `repo` | ship | repo.md | a git remote exists | RPO | community health files (LICENSE, SECURITY.md, CONTRIBUTING) · SPDX license IDs |
