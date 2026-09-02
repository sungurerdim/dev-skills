# ds-rig

AI-dev environments rot by default: unpinned installs, telemetry left on, MCP servers stacked past the point where their tool-definition tax outweighs their savings, harness permissions at insecure defaults.

One skill builds and maintains the whole rig — budgeted, pinned, privacy-hardened, permission-profiled, reversible.

## Install

```bash
cp -r dev-skills/ds-rig ~/.claude/skills/ds-rig   # or ./install.sh
```

## Use

```
/ds-rig                    # full flow: detect → select+budget → trust gate → install → privacy → permissions → prove
/ds-rig --check            # read-only drift + privacy + permission + budget report
/ds-rig --update           # drift table for tracked tools, approved updates only
/ds-rig --privacy-only     # re-apply + re-prove telemetry opt-outs
/ds-rig --permissions-only # apply/refresh harness allow/ask/deny profiles
/ds-rig --budget           # MCP tool-count + token-tax report
/ds-rig --uninstall rtk    # symmetric removal via the tool's own uninstaller
/ds-rig --ask              # interactive: category menu, per-item confirmations
```

## Categories

| Category | Primary tools | Fallback (zero-dep) |
|----------|--------------|---------------------|
| Token-reducing CLI proxy | rtk | truncation conventions |
| Sandboxed-execution MCP | context-mode (caveat gated) | temp-file + summarize |
| Persistent memory MCP | basic-memory | plain Markdown notes |
| LSP bridge | agent-lsp / Serena | native search |
| Git quality gate | pre-commit | native `.git/hooks` |
| Security scanners | gitleaks, osv-scanner, actionlint, zizmor, hadolint, typos | consuming skills' prose checks |

## Features

- **MCP token budget** — projects and re-checks total registered tool count against the ~20-30 net-negative threshold; crossing needs explicit override
- **Zero telemetry, proven — harnesses included** — opt-outs for tools AND detected harnesses, determined by live web research against official docs at run time, applied and verified by config read-back; non-disableable traffic reported honestly as `functional-network`
- **Permission profiles** — 16-class risk-command taxonomy (RC-1..10 deny: destruction, escalation, unpinned remote code, exfiltration, persistence; RC-11..16 ask: push/publish/installs/migrations) merged additively into every harness that exposes a surface, with a chain-resistant hook arm offered where scriptable — and honest limits stated (pattern lists are not a sandbox)
- **Pinned + current** — versions recorded in `~/.config/ds-rig/manifest.json`; re-runs show a drift table and update only with approval
- **Symmetric uninstall** — every install path recorded with its reversal
