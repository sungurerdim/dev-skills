# Rules: Internationalization & Logging

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Internationalization & Logging** | I18N-01–07 (6 MAJOR, 1 MEDIUM) | ~10 |

---

## Internationalization & Logging

### I18N-01 [MAJOR] String Externalization
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

### I18N-02 [MAJOR] Locale-Aware Formatting
Dates, numbers, currency formatted per locale. No hardcoded format strings.
- **Detect:** Hardcoded date format (`MM/DD/YYYY`). Hardcoded currency symbol (`$`). Manual number formatting with fixed decimal separator
- **Fix:** Use `Intl.DateTimeFormat`, `Intl.NumberFormat` (JS). Use `locale` module (Python). Use `time.Format` with locale (Go). Always derive format from user's locale
- **Source:** MDN Intl, Unicode CLDR

### I18N-03 [MAJOR] Pluralization Rules
ICU message format or equivalent. Languages have different plural rules (EN: 2, AR: 6, Slavic: 4).
- **Detect:** Manual if/else for singular/plural. Hardcoded "1 item"/"X items". Template literals with simple ternary for plurals
- **Fix:** Use ICU plural syntax in resource files. Libraries: `intl-messageformat` (JS), `babel` (Python). Test with Arabic, Polish, or other complex-plural languages
- **Source:** ICU, Unicode CLDR Plural Rules

### I18N-04 [MAJOR] Structured Logging
JSON logs. No secrets/PII. Correlation IDs. Defined log levels.
- **Detect:** Unstructured log messages (`console.log`, `print()`). Sensitive data in logs (tokens, passwords, PII). No request correlation. Mixed log levels
- **Fix:**
  - Node: `pino` or `winston` with JSON format
  - Python: `structlog` or `logging` with JSON formatter
  - Go: `slog` (stdlib) or `zap`
  - Sanitize sensitive fields. Add correlation IDs. Define levels: debug/info/warn/error
- **Source:** Observability best practices, 12-Factor App

### I18N-05 [MAJOR] RTL Layout Support
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

### I18N-06 [MAJOR] Date/Time/Timezone Handling
All dates and times must use locale-aware formatting and proper timezone handling.
- **Detect:**
  - Search: `new Date().toLocaleDateString()` without explicit locale parameter
  - Search: hardcoded date format strings (`MM/DD/YYYY`, `DD.MM.YYYY`)
  - Search: `.toISOString()` displayed directly to users (not human-readable)
  - Search: timezone-naive operations (`new Date()` for scheduling, missing UTC/timezone conversion)
  - Python: `datetime.now()` without timezone (naive datetime), missing `pytz`/`zoneinfo`
  - Go: `time.Now()` formatted without timezone context
- **Fix:** Use `Intl.DateTimeFormat` (JS), `DateFormat` with locale (Flutter/Dart), `babel.dates` (Python). Store as UTC, display in user's timezone. Use `Temporal` API (JS) or `zoneinfo` (Python) for timezone math. Never hardcode date format strings.
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
