# Rules: Privacy Opt-Out Seed Map (verified 2026-07-15)

Seed data for Phase 5 — every entry traced to official docs/changelogs/issues on the date above. **Mechanisms drift between versions: the live official source wins on conflict; this map only seeds the lookup.** Full provenance: `docs/methodology/cross-host-program.md` research artifacts.

**Effectiveness discipline:** a documented opt-out is a claim, not a result. Prove by (1) config/env read-back, (2) status command where one exists, and (3) for items with documented-broken opt-outs (marked ⚠ below), network observation where feasible — otherwise record `setting-applied-effect-unverified`, never `proven`.

**Irreducible traffic (report honestly, never hide):** model API calls are the tool's function; registry/index fetches are package managers' function; OSV API queries are osv-scanner's function (`--offline` exists but disables the function itself). Classify as `functional-network`.

## Harnesses

| Harness | Disable mechanism | Caveat / what remains |
|---------|-------------------|------------------------|
| Claude Code | `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` (bundles `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`, feedback + survey) | WebFetch domain-preflight needs separate `skipWebFetchPreflight: true` (sends hostname only); Bedrock/Vertex/Foundry providers: metrics/Sentry already off |
| Codex CLI | `analytics.enabled = false` in `~/.codex/config.toml` | default described as "client default", rollout evolving — read back after set; OTel export off by default |
| Gemini CLI | `.gemini/settings.json` `{"privacy":{"usageStatisticsEnabled":false}}` (restart required) | OTel off by default (`GEMINI_TELEMETRY_ENABLED` guards it) |
| Copilot CLI | `COPILOT_OFFLINE=true` — the only full opt-out | ⚠ functional side effects (no /delegate, web_fetch, hosted models); **no online-mode telemetry opt-out exists** (open request) — online use = telemetry accepted; surface this decision |
| VS Code Copilot | `telemetry.telemetryLevel: "off"` | ⚠ official caveat: extensions may collect independently; open bug on Copilot Chat survey after off |
| Cursor | Privacy Mode toggle (forced on for Business) + separate Telemetry toggle | ⚠ Privacy Mode explicitly does not stop product-improvement telemetry or provider-side transient retention; requests route through Cursor backend regardless |
| Windsurf / Devin Desktop | account settings → code-snippet telemetry opt-out | scope beyond "code snippets" undocumented — mark `partial` |
| Aider | `analytics: false` in `~/.aider.conf.yml` / `--no-analytics` / `AIDER_ANALYTICS=false` | clean opt-out; unset = random-subset enrollment, so set it explicitly |
| OpenCode | `{"share":"disabled","autoupdate":false,"experimental":{"openTelemetry":false}}` | ⚠ **effectively non-disableable** — open issues confirm outbound traffic continues; report `non-disableable-in-practice`, offer the harness-level decision to the user |
| Cline | settings toggle (also follows VS Code level) | ⚠ open bugs: sends after disable, client still initializes; "required events" bypass the toggle |
| Roo Code | settings toggle (PostHog honored) | ⚠ cloud-telemetry client hardcodes enabled — confirmed non-disableable component |
| Kilo Code | About → uncheck "Allow error and usage reporting" | ⚠ toggle broken/missing in v5.6.0; unexplained traffic reported even when disabled |

## Package managers / runtimes

| Item | Mechanism | Note |
|------|-----------|------|
| Homebrew | `HOMEBREW_NO_ANALYTICS=1` (or `brew analytics off`); installer run: `HOMEBREW_NO_ANALYTICS_THIS_RUN=1` | official |
| pip | none needed — official "does not collect any telemetry" | index requests = functional |
| npm/npx · uv · cargo · scoop | no telemetry feature documented (npm/uv/cargo/scoop: absence-based, not first-party denial) | registry fetches = functional; mark `no-telemetry-by-default (absence-based)` |
| winget | Windows OS diagnostics setting (no dedicated flag); Home/Pro cannot fully zero it | mark `os-governed` |

## Rig catalog tools

| Tool | Mechanism | Note |
|------|-----------|------|
| rtk | disabled by default (since 2026-04 fix, issue #1154); belt-and-braces: `RTK_TELEMETRY_DISABLED=1` | local tracking DB (`~/.local/share/rtk/tracking.db`) is local-only, 90-day default (`tracking.history_days`) |
| context-mode | vendor states no telemetry/accounts/tracking (local-only) | vendor claim, not independently audited — mark `vendor-claimed` |
| basic-memory (OSS) | **telemetry ON by default** → `basic-memory telemetry disable`; verify `basic-memory telemetry status` | Cloud tier is account-linked, separate policy |
| agent-lsp | no telemetry documentation either way | mark `unverified` — probe or ask upstream |
| Serena | `record_tool_usage_stats` in `~/.serena/serena_config.yml`; anonymous startup ping by default | verify the template default at install time |
| pre-commit | no telemetry in the framework | third-party hooks may differ — note per hook |
| gh CLI | telemetry ON by default since v2.91.0 → `GH_TELEMETRY=false` or `gh config set telemetry disabled`; honors `DO_NOT_TRACK` | update checks separate: `GH_NO_UPDATE_NOTIFIER=1` |
| gitleaks · ripgrep · jq · fd | fully local, no network code | `no-telemetry-by-default` |
| osv-scanner | OSV/deps.dev queries are the function | `--offline` for air-gapped; classify `functional-network` |
| npx skills (Vercel) | no manual opt-out documented (CI auto-disabled) | prefer `install.sh --target` (zero telemetry) |

## DO_NOT_TRACK

Set `DO_NOT_TRACK=1` in the shell profile as baseline — **but adoption is a minority** (confirmed honored: gh CLI, Claude Code survey, Turborepo). Never rely on it alone; per-tool mechanisms above are the actual work.
