# Rules: Internationalization & Logging

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Internationalization & Logging** | I18N-01–14 (8 HIGH, 5 MEDIUM, 1 LOW) | ~10 |

---

## Internationalization & Logging

### I18N-01 [HIGH] String Externalization
All user-visible strings in resource/locale files. Zero hardcoded UI text.
- **Detect:**
  - Search: quoted strings in UI components/templates that are user-visible (not keys, not log messages, not CSS classes)
  - Missing localization setup
- **Fix:**
  - React: `next-intl`, `react-intl`, or `i18next` with JSON locale files
  - Vue: `vue-i18n` with JSON locale files
  - Python (web): `gettext` or `babel` with PO files
  - Python (CLI): `gettext` with PO files
  - Go: `go-i18n` or `golang.org/x/text`
- **Source:** i18n best practices

### I18N-02 [HIGH] Locale-Aware Formatting
Dates, numbers, currency formatted per locale. No hardcoded format strings.
- **Detect:** Hardcoded date format (`MM/DD/YYYY`). Hardcoded currency symbol (`$`). Manual number formatting with fixed decimal separator
- **Fix:** Use `Intl.DateTimeFormat`, `Intl.NumberFormat` (JS). Use `locale` module (Python). Use `time.Format` with locale (Go). Always derive format from user's locale
- **Source:** MDN Intl, Unicode CLDR

### I18N-03 [HIGH] Pluralization Rules
ICU message format or equivalent. CLDR defines up to six plural categories — `zero`, `one`, `two`, `few`, `many`, `other` (EN uses 2, AR all 6, Slavic 3-4).
- **Detect:** Manual if/else for singular/plural. Hardcoded "1 item"/"X items". Template literals with simple ternary for plurals. Locale resource files missing required CLDR categories for their language — Polish/Russian reduced to `one`/`other` without `few`/`many`; any plural set missing the `other` fallback
- **Fix:** Use ICU plural syntax in resource files with the full CLDR category set per locale — always include `other` as fallback. Libraries: `intl-messageformat` (JS), `babel` (Python). Test with Arabic, Polish, or other complex-plural languages
- **Source:** ICU, Unicode CLDR Plural Rules

### I18N-04 [HIGH] Structured Logging
JSON logs. No secrets/PII. Correlation IDs. Defined log levels.
- **Detect:** Unstructured log messages (`console.log`, `print()`). Sensitive data in logs (tokens, passwords, PII). No request correlation. Mixed log levels
- **Fix:**
  - Node: `pino` or `winston` with JSON format
  - Python: `structlog` or `logging` with JSON formatter
  - Go: `slog` (stdlib) or `zap`
  - Sanitize sensitive fields. Add correlation IDs. Define levels: debug/info/warn/error
- **Source:** Observability best practices, 12-Factor App
- **Cross-ref:** Same check as [ARC-03](rules-arch.md) (canonical, arch scope) — when both `i18n` and `arch` scopes run together, report once under ARC-03.

### I18N-05 [HIGH] RTL Layout Support
Right-to-left text and layout must work correctly for Arabic, Hebrew, Persian, and Urdu users.
- **Detect:**
  - Search: CSS with hardcoded `left`/`right` instead of logical properties (`inline-start`/`inline-end`, `margin-inline`)
  - Search: `text-align: left` without RTL override
  - Search: hardcoded `direction: ltr` without conditional
  - Flutter: `Directionality` widget missing, hardcoded `EdgeInsets` with `left`/`right` instead of `start`/`end`
  - Icons with directional meaning (arrows, progress) not mirrored in RTL
- **Fix:** Use CSS logical properties (`margin-inline-start`, `padding-inline-end`). Flutter: use `EdgeInsetsDirectional`. Test with `dir="rtl"` attribute. Mirror directional icons. Use `Intl.textDirection` for dynamic detection.
- **Impact:** 400M+ Arabic speakers, 10M+ Hebrew speakers. RTL-broken UIs are unusable.
- **Source:** MDN Logical Properties, Material Design Bidirectionality

### I18N-06 [HIGH] Date/Time/Timezone Handling
All dates and times must use locale-aware formatting and proper timezone handling.
- **Detect:**
  - Search: `new Date().toLocaleDateString()` without explicit locale parameter
  - Search: hardcoded date format strings (`MM/DD/YYYY`, `DD.MM.YYYY`)
  - Search: `.toISOString()` displayed directly to users (not human-readable)
  - Search: timezone-naive operations (`new Date()` for scheduling, missing UTC/timezone conversion)
  - Search: fixed UTC-offset arithmetic (`+ 3 * 3600`, hardcoded `+03:00`/`GMT-5` constants) instead of IANA tzdb zone identifiers — fixed offsets silently break on every DST transition
  - Python: `datetime.now()` without timezone (naive datetime), missing `pytz`/`zoneinfo`
  - Go: `time.Now()` formatted without timezone context
- **Fix:** Use `Intl.DateTimeFormat` (JS), `DateFormat` with locale (Flutter/Dart), `babel.dates` (Python). Store as UTC, display in user's timezone. Use `Temporal` API (JS) or `zoneinfo` (Python) for timezone math with IANA tzdb identifiers (`America/New_York`), never fixed offsets. Prefer CLDR skeleton-based formatting APIs over hand-authored per-locale patterns — translator-edited literal patterns are error-prone. Never hardcode date format strings.
- **Impact:** Date confusion causes booking errors, financial mistakes, missed deadlines across timezones.
- **Source:** ICU Date Formatting, Temporal API proposal

### I18N-07 [MEDIUM] Currency and Number Formatting
Numbers and currencies must be formatted per locale.
- **Detect:**
  - Search: hardcoded currency symbols (`$`, `€`, `£`) concatenated with numbers
  - Search: `toFixed(2)` for currency display (doesn't handle locale-specific decimal separators)
  - Search: hardcoded thousand separators (`,` or `.`) in number formatting
- **Fix:** Use `Intl.NumberFormat` (JS), `NumberFormat` (Flutter/Dart), `babel.numbers` (Python). Specify locale and currency code. Let formatter handle symbol placement, decimal separator, and grouping.
- **Source:** ICU Number Formatting

### I18N-08 [MEDIUM] No Business Logic in Message Files
ICU select/plural mechanisms exist for grammar, not application branching.
- **Detect:**
  - Translation resource files containing nested `select`/conditional patterns that encode business decisions (feature availability, pricing tiers, role checks) rather than grammatical variation
- **Fix:** Move business-logic branching into application code; keep message files to grammar-only variation (plural, gender, formality). ICU's own guidance: program switch cases in the application, not in resource files
- **Impact:** Logic hidden in message strings is invisible to tests and type checkers, and every translator becomes an unwitting maintainer of business rules
- **Source:** ICU MessageFormat guidance

### I18N-09 [HIGH] Key and Parameter Parity Enforced Mechanically
Every message key and every placeholder/ICU-plural argument exists with identical names across all supported locales, enforced by an automated pre-commit/pre-push check.
- **Detect:** Locale files with divergent key sets; placeholders present in the template language but missing/renamed in a translation; parity checked only by human review.
- **Fix:** Run an automated parity script (keys AND parameter names, including ICU plural arguments) against all locales at pre-commit/pre-push; fail the gate on any mismatch. Missing keys don't error at compile time — they silently fall back — so only a mechanical gate catches them.
- **Impact:** A missing key ships as silent English fallback in production; a missing placeholder ships as a runtime formatting error — both invisible until a user in that locale hits them.
- **Source:** XR-067 — cross-project experience registry (2026).

### I18N-10 [MEDIUM] Chrome and Layout Strings Are Externalized and Explicitly Scanned
Layout/chrome strings — nav aria-labels, footer taglines, alt text, template-level slogans — come from the same i18n SSOT as page content, and the i18n audit explicitly scans layout/chrome templates.
- **Detect:** Hardcoded strings in layout templates, navigation chrome, aria-labels, alt attributes, or generated-site UI; i18n audit tooling scoped to content pages only.
- **Fix:** Externalize chrome strings into the same locale resources as body content; extend the audit's file scope to layout/chrome/template directories explicitly — chrome strings escape most i18n audits precisely because the scan skips those paths.
- **Impact:** A fully translated product with English chrome reads as unfinished in every non-English locale — and chrome is the one part of the UI every user sees on every page.
- **Source:** XR-065 — cross-project experience registry (2026); extends I18N-01.

### I18N-11 [MEDIUM] Terminology Bound to an Authoritative Source, in the Everyday Register
When a technical term has multiple renderings in a language, the preferred term is documented as an explicit rule bound to an authoritative external source — and loanword-sensitive languages prefer everyday descriptive phrasing.
- **Detect:** The same concept translated differently across surfaces; term choices resting on individual translator intuition; formal loanwords where the target language has a natural everyday phrase; action and result-object conflated under one term.
- **Fix:** Record each preferred term as a documented rule citing an authoritative source (e.g. the platform's official page in that language). In loanword-sensitive languages (e.g. Turkish), prefer everyday descriptive phrasing over foreign-rooted jargon ("yazıya dönüştürme", not "transkripsiyon"); keep the action and its result object as distinct terms.
- **Impact:** Undocumented term choices drift with every translator rotation, and jargon-heavy copy measurably narrows the user base to those who already know the loanwords.
- **Source:** XR-068 — cross-project experience registry (2026).

### I18N-12 [HIGH] Case Folding Is Locale-Aware — Never Plain toUpperCase/toLowerCase
Locale-sensitive string comparisons (typed-name confirmations, search normalization) use locale-aware case folding, never ASCII/English case functions.
- **Detect:** `toUpperCase()`/`toLowerCase()` (default locale) on user-input comparisons in locales with special casing (Turkish İ/I/i/ı, Greek ς, Lithuanian accents); type-to-confirm destructive dialogs failing on correctly typed input.
- **Fix:** Use locale-parameterized case folding (`toLocaleUpperCase('tr')`, ICU case folding) for every comparison involving user-visible text; add a regression test with Turkish dotted/dotless i pairs ("DRİVE SİL" vs "DRIVE SIL").
- **Impact:** ASCII folding makes the confirmation gate on the most destructive actions unpassable (or bypassable) for entire locales — Turkish users literally cannot type a matching confirmation.
- **Source:** XR-122 — cross-project experience registry (2026).

### I18N-13 [MEDIUM] hreflang Uses Full BCP-47 Subtags Where Script or Region Disambiguates
When a locale's script or region is ambiguous, hreflang/language-alternate values use the full BCP-47 subtag, never the bare two-letter code.
- **Detect:** `hreflang="zh"` where Simplified/Traditional both exist; `pt` where BR and PT variants differ; bare ISO 639-1 codes on alternates targeting a specific regional audience.
- **Fix:** Emit full BCP-47 subtags (`zh-Hans`, `zh-Hant`, `pt-BR`, `pt-PT`) wherever script or region carries meaning; keep bare codes only for genuinely undifferentiated languages.
- **Impact:** Ambiguous codes leave search engines guessing which variant serves which market — the wrong-script page ranks in the wrong region and reads as broken to native users.
- **Source:** XR-069 — cross-project experience registry (2026).

### I18N-14 [LOW] Glossary Comprehension Validated With Real Target Users
Automated terminology consistency is necessary but not sufficient: the glossary's comprehensibility is validated in a moderated usability test with at least 5 participants from the real target segment.
- **Detect:** Terminology adopted purely from internal/automated consistency checks; no record of target-segment users (clinic staff, salon operators, teachers) confirming they understand the chosen terms.
- **Fix:** Run a moderated comprehension test (≥5 participants from the actual target segment) on the glossary's key terms; feed misunderstood terms back into the terminology rules. This is a human-only gate — flag it for the owner; do not auto-pass it.
- **Impact:** A perfectly consistent glossary of terms the target users don't understand is consistently incomprehensible — the audit passes while the users fail.
- **Source:** XR-173 — cross-project experience registry (2026).
