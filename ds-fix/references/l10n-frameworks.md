# L10n Frameworks per Stack

Consumer: SKILL.md Phase 2 (L10n). No framework detected → skip silently.

| Stack | Framework | Key files |
|-------|-----------|-----------|
| flutter | flutter_localizations / gen-l10n | `lib/l10n/*.arb` |
| node | i18next / react-intl / next-intl | `locales/*.json`, `messages/*.json` |
| python | gettext / babel | `*.po`, `babel.cfg` |
| jvm | Android resources / Spring messages | `res/values-*/strings.xml`, `messages_*.properties` |
| swift | NSLocalizedString / String Catalogs | `*.lproj/*.strings`, `*.xcstrings` |
| dotnet | resx | `Resources/*.resx` |
| ruby | rails-i18n | `config/locales/*.yml` |
| php | Laravel lang / Symfony translations | `lang/*.php`, `translations/*.yaml` |
| c-cpp | gettext | `*.po`, `*.pot` |
| elixir | Gettext | `priv/gettext/*.po` |
| scala | Play i18n / Java ResourceBundle | `conf/messages.*`, `*.properties` |
