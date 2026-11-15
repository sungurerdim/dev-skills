---
name: ds-setup
description: Set up and maintain the machine-level AI dev rig — install or update a pinned toolset, turn off telemetry in every tool and harness, apply allow/ask/deny permission profiles (risk-free work never prompts), and keep the MCP tool count within budget. Use for setting up or upgrading the AI dev environment, privacy hardening, or harness permissions.
---

# /ds-setup

Build the AI-dev environment deliberately: every tool pinned and recorded, nothing phoning home, permissions that never prompt for risk-free work and always stop the dangerous kind. Machine-level — writes nothing into any project. Follows [kernel.md](../core/kernel.md); this file adds only the rig specifics.

## Input

| Word | Effect |
|------|--------|
| *(none)* | Every part, in step order: tools → privacy → perms → prove |
| `tools` | Steps 1-4: detect, select, trust gate, install/update |
| `update` | Only manifest-tracked tools that have a newer version |
| `privacy` | Step 5 only: research, apply and prove telemetry opt-outs |
| `perms` | Step 6 only: apply or refresh permission profiles and the deny hook |
| `mcp` | MCP tool count and token cost against the budget only |
| `uninstall <tool\|all>` | Each tool's own uninstall, its privacy/permission entries removed, manifest updated |
| `dry` | Read-only report for the named parts (all when none): version drift, privacy and permission posture, MCP budget |
| `ask` | Questions with a recommended option at each decision (kernel §5) |

Every part runs alone: it probes what it needs (step 1) itself and ends with its own proof (step 7).

## Done when

Every selected tool shows its pinned version and an observed effect; every tool and harness has proven-off telemetry, an explicit acceptance, or a sourced `functional-network` label; every written config parses and its diff against the backup shows additions only; the manifest reads back as valid JSON.

## Never without the user

Recorded `Only you can do` by default, a per-item question under `ask`: unpinned `npx -y` / `curl | sh`, MCP servers that receive credentials, self-updating tools, MCP additions past the budget, flags that disable a sandbox or permission checks, and loosening any existing deny rule.

## Steps

1. **Detect** from probes, never assumption: OS, architecture, package managers (brew, apt/dnf, winget/scoop, npm, uv/pip, cargo); harnesses (`~/.claude/`, `~/.codex/`, `~/.gemini/`, `~/.copilot/`, Aider, OpenCode, Cursor, Windsurf); catalog tools and versions (`{tool} --version`); MCP servers per harness, counted by parsing the config (`python3 -c "import json,sys; print(len(json.load(open(sys.argv[1])).get('mcpServers', {})))" {config}`); manifest `~/.config/ds-setup/manifest.json` (present = re-run; only the pre-3.0 `~/.config/ds-rig/manifest.json` present → move it there). A probe that cannot run → `unknown`, excluded from automatic actions. Print the rig before changing anything.
2. **Select** from [catalog.md](references/catalog.md): every category whose signal holds, plus manifest tools with updates. For each MCP-class pick, name the CLI alternative if one exists. Project the MCP tool count; past ~20-30 tools definitions cost more context than they save.

   | Category | Runs when | Tools | Fallback |
   |----------|-----------|-------|----------|
   | Token-reducing CLI proxy | always | rtk | truncate output (`head`, `wc -l`) |
   | Sandboxed execution MCP | offered; escape caveat accepted per item | context-mode | temp file + summary |
   | Persistent memory | always | basic-memory | Markdown notes |
   | LSP bridge | a language server exists for a project language | agent-lsp, Serena | native search |
   | Git hook manager | a git repo is in use | pre-commit | `.git/hooks/*` |
   | Security scanners | always | gitleaks, osv-scanner, actionlint, zizmor, hadolint, typos | rule-file checks |
   | Base CLI | always | gh, ripgrep, jq, fd | grep, find |

3. **Trust gate**, per item before anything runs: the package exists in its official registry with real history (a near-miss name is a suspected typosquat), the version is current, the license and telemetry posture are documented. Record the URL and the exact version to pin. No pinnable path → skip.
4. **Install / update** one item at a time with the OS package manager; show `{tool}: {installed} → {latest}` for updates. A failure → exact error plus the category fallback; at most two retries. Already installed outside the manifest → adopt it (`external`), never reinstall over it.
5. **Privacy** — for every harness and tool, research the current opt-out in official docs at run time; [privacy.md](references/privacy.md) is the seed, the live source wins (offline → seed, marked `unverified-currency`). Apply with backup and merge; universal `DO_NOT_TRACK=1` in a managed shell-profile block. Prove each by reading the setting back or running the tool's status command. Required traffic (model API calls, a scanner's lookup API) is `functional-network`, never hidden. A known-broken opt-out is `non-disableable-in-practice` with the issue cited → replace with the fallback when one exists.
6. **Permissions** per [permissions.md](references/permissions.md), global/user config files only — never a project file:
   - RC-1..10 and the protected-path map → deny; RC-11..16 → ask; everything risk-free → allow; workspace autonomy through cwd-relative matchers.
   - Every Bash entry mirrored for wrappers the harness does not strip (rtk and others).
   - The `rc_deny.py` hook arm where the harness has a blocking hook (Claude Code: `"{py}" "{dir}/rc_deny.py" --claude-hook` under `PreToolUse` with matcher `Bash`).
   - Harness with no global surface → gap-note with the compensating control (a ds-gate git pre-commit arm).
   - Never remove or loosen an existing user entry; a conflict skips that file and is recorded.
7. **Prove and record** — each tool's observed effect from the catalog's Verify line; MCP recount against the projection; run `python3 assets/test_rc_deny.py` when the hook arm was installed; write the manifest (tool, version, install method, privacy proof, permission entries, date) and parse it back.

## Report

`ds-setup: OK|WARN|FAIL|INCOMPLETE | tools {n} installed · {m} updated | privacy {p}/{n} proven | permissions {h} harnesses | MCP {count}/{budget}`, then: rig detected, per-item table (action, version, evidence), privacy posture per item, permission diff per harness with the RC coverage table and the honest limits from permissions.md, gap-notes, and the closing block of kernel §6. A run where the user declines every install is valid: read-only report, `OK`.

## Edge cases

| Case | Behavior |
|------|----------|
| No package manager (bare Windows) | Catalog's prebuilt binary with checksum; none → gap-note |
| Offline or registry unreachable | Trust gate cannot verify → no installs; `dry` report |
| MDM-managed machine reverts writes | Detected at read-back → `managed-environment` gap |
| Two harnesses share a surface (OpenCode reads `~/.claude/skills/`) | Apply once, note the shared coverage |
| Manifest missing on an existing rig | Build it by adoption from probed versions |
