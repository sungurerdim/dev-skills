#!/usr/bin/env python3
"""ds-setup step 1 in one call: print the machine's rig as JSON (stdlib only, any OS, read-only).

  probe.py [TOOL ...]     probe the catalog tools (default list below) plus OS, package managers, harnesses,
                          MCP server counts and the manifest. A probe that cannot run is reported "unknown".
  probe.py --self-test    exit 0 when the output is complete and valid JSON
"""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TOOLS = ("rtk", "basic-memory", "context-mode", "agent-lsp", "serena", "pre-commit", "gitleaks", "osv-scanner",
         "actionlint", "zizmor", "hadolint", "typos", "gh", "rg", "jq", "fd", "git", "python3", "node", "uv")
PACKAGE_MANAGERS = ("brew", "apt", "dnf", "pacman", "winget", "scoop", "choco", "npm", "pnpm", "uv", "pipx", "pip",
                    "cargo", "go")
HARNESSES = {"claude-code": ".claude", "codex": ".codex", "gemini": ".gemini", "copilot": ".copilot",
             "opencode": ".config/opencode", "cursor": ".cursor", "windsurf": ".codeium/windsurf",
             "aider": ".aider.conf.yml"}
# JSON configs whose top-level "mcpServers" object lists MCP servers; Codex uses TOML [mcp_servers.<name>] tables
MCP_JSON = {"claude-code": ".claude.json", "gemini": ".gemini/settings.json", "cursor": ".cursor/mcp.json",
            "windsurf": ".codeium/windsurf/mcp_config.json"}
MCP_TOML = {"codex": ".codex/config.toml"}


def version(tool: str) -> str | None:
    exe = shutil.which(tool)
    if not exe:
        return None
    for flag in ("--version", "version", "-V"):
        try:
            r = subprocess.run([exe, flag], capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            return "unknown"
        line = (r.stdout or r.stderr).strip().splitlines()
        if r.returncode == 0 and line:
            return line[0][:120]
    return "unknown"


def mcp_counts(home: Path) -> dict:
    out = {}
    for name, rel in MCP_JSON.items():
        p = home / rel
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                n = len(data.get("mcpServers") or {})
                if name == "claude-code":  # project-scoped servers live under projects.<path>.mcpServers
                    n += sum(len(v.get("mcpServers") or {}) for v in (data.get("projects") or {}).values()
                             if isinstance(v, dict))
                out[name] = n
            except (ValueError, OSError, AttributeError):
                out[name] = "unknown"
    for name, rel in MCP_TOML.items():
        p = home / rel
        if p.is_file():
            try:
                out[name] = len(set(re.findall(r"^\s*\[mcp_servers\.([^\].]+)", p.read_text(encoding="utf-8"), re.M)))
            except OSError:
                out[name] = "unknown"
    return out


def probe(tools) -> dict:
    home = Path.home()
    names = sorted(set(tools) | set(PACKAGE_MANAGERS))
    with ThreadPoolExecutor(max_workers=8) as pool:
        found = dict(zip(names, pool.map(version, names)))
    config = home / ".config"
    return {
        "os": platform.system(), "release": platform.release(), "arch": platform.machine(),
        "python": sys.executable,
        "packageManagers": {m: found[m] for m in PACKAGE_MANAGERS if found[m]},
        "harnesses": {h: (home / rel).exists() for h, rel in HARNESSES.items()},
        "tools": {t: found[t] for t in tools},
        "mcpServers": mcp_counts(home),
        "manifest": next((str(p) for p in (config / "ds-setup" / "manifest.json", config / "ds-rig/manifest.json")
                          if p.is_file()), None),
        "env": {k: os.environ.get(k) for k in ("DO_NOT_TRACK", "CLAUDE_CONFIG_DIR", "SHELL", "ComSpec")
                if os.environ.get(k)},
    }


def self_test() -> int:
    data = json.loads(json.dumps(probe(["python3", "surely-not-a-real-tool-xyz"])))
    ok = (set(data) >= {"os", "arch", "packageManagers", "harnesses", "tools", "mcpServers", "manifest"}
          and data["tools"]["surely-not-a-real-tool-xyz"] is None and data["os"])
    print("probe self-test:", "all checks passed" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    print(json.dumps(probe(sys.argv[1:] or TOOLS), indent=2))
