# Scopes: Desktop Distribution & A9 Ecosystem (Conditional)

Loaded when the Desktop Distribution or A9 Ecosystem scope resolves to run (see SKILL.md Scopes table).

## Desktop Distribution

Conditional — desktop project detected: Electron/Tauri config, `*.xcodeproj` with macOS target, MSIX/WiX manifest.

| Check | What It Covers | Severity |
|-------|---------------|----------|
| macOS notarization | Distribution outside MAS: hardened runtime enabled, app signed with Developer ID cert, notarized via `notarytool` (not legacy `altool`), ticket stapled (`stapler`) — unnotarized apps are blocked by Gatekeeper | HIGH |
| Windows signing | Authenticode signature on installer + binaries (unsigned → SmartScreen warning kills conversion); MSIX packaging where Microsoft Store or clean install/uninstall matters | HIGH |
| Auto-update integrity | Update channel (Sparkle, electron-updater, Tauri updater) serves signed updates over HTTPS with signature verification ON — an unsigned update feed is remote code execution as a feature | HIGH |
| Store option fit | MAS (sandbox + entitlements review) vs direct distribution vs Microsoft Store — chosen deliberately with the sandbox-restriction tradeoff stated; MAS submission then follows the standard store scopes above | MEDIUM |
| User-facing changelog + staged rollout | Same D6 rules as mobile Release scope — desktop auto-update is the archetypal silent OTA channel | MEDIUM |

## A9 — Google / Apple Ecosystem Rules

**Activate when:** the `integrations` signal names it — `Signals: integrations=` contains `google-workspace` or `apple-ecosystem` ([core signal inventory](../../core/signal-inventory.md)), or the Blueprint Profile's `Integrations:` field states either. Never inferred from a guess (an OAuth client ID alone does not activate this — the integration must be named by one of the two sources). Zero checks when absent from both.

| Provider | Rule | Scope |
|----------|------|-------|
| Google | OAuth consent screen — verify production approval status, homepage/privacy URLs, authorized domains (Google OAuth verification requirement — a citable external platform mandate, so a blocker, not advisory) | review |
| Apple | Sign in with Apple — verify entitlement + `ASAuthorizationAppleIDProvider` import (Guideline 4.8) | review |
| Google | Data safety section — ensure declarations match actual API scopes used | privacy |
| Apple | Apple Privacy Labels — verify nutrition label declares sign-in and contact info if applicable | privacy |
