# Rules: Harness Permission Surfaces & Safe-Default Profile

Per-harness allow/ask/deny surfaces verified 2026-07-15 against official docs (sources in [dev-skills cross-host research](https://github.com/sungurerdim/dev-skills/blob/main/docs/methodology/cross-host-program.md)). **Surfaces drift — re-verify against the harness's live docs at apply time; this file is the starting map, not the authority.** All writes: backup first, additive merge only, parse-validate after, diff must show only additions.

## Risk-command taxonomy (safe-default profile)

Policy classes, harness- AND OS-independent intent. **The intent class is the contract; concrete patterns are instantiated for the detected OS at apply time** — every class gets its POSIX (Linux/macOS) and Windows (cmd + PowerShell) expansions; a class with no equivalent on the detected OS is skipped with a note, never half-applied. Seeds below show both families; the skill also adds patterns for tools it installs this run.

### DENY by default (destructive / irreversible / trust-breaking)

| Class | POSIX seeds (Linux/macOS) | Windows seeds (cmd/PowerShell) | Why deny |
|-------|---------------------------|--------------------------------|----------|
| RC-1 Filesystem destruction | `rm -rf` outside workspace · `rm -rf /`, `~`, `$HOME` · broad `find … -delete` · `shred` · `truncate` on system paths | `rd /s /q`, `del /f /s /q` outside workspace · `Remove-Item -Recurse -Force` on `$env:USERPROFILE`/drive roots · `robocopy /MIR` onto non-empty targets | irreversible data loss |
| RC-2 Disk/device ops | `dd of=/dev/*` · `mkfs*` · `fdisk`/`parted`/`diskutil eraseDisk` · `mount`/`umount` system volumes | `format` · `diskpart` · `bcdedit` · `Clear-Disk`/`Initialize-Disk` | machine-level damage |
| RC-3 Privilege escalation | `sudo`/`su`/`doas` · `chmod`/`chown` outside workspace · setuid bits | `runas` · `Start-Process -Verb RunAs` · `icacls`/`takeown` outside workspace | breaks the permission model itself |
| RC-4 Unpinned remote code | `curl … \| bash`/`sh` · `wget … \| sh` · `npx -y {pkg}` unpinned · `sh -c "$(curl …)"` · `eval` over fetched content · `pip install {url}` | `iex (iwr …)` / `Invoke-Expression` over `Invoke-WebRequest` · `powershell -enc {base64}` · unpinned `npx -y` (cross-OS) | CVE-2025-6514-class supply-chain execution |
| RC-5 Git history/remote destruction | `git push --force*` · `git branch -D {default}` · `git reset --hard` + push · `git filter-branch`/`filter-repo` · deleting pushed tags · `git remote remove` | same (git is cross-OS) | destroys shared history |
| RC-6 Credential/secret access | reads of `~/.ssh/*`, `~/.aws/credentials`, `~/.config/gcloud/*` · `security dump-keychain` (macOS) · `gpg --export-secret-keys` · `printenv`/`env` piped to network commands | reads of `%USERPROFILE%\.ssh`, `%USERPROFILE%\.aws` · `cmdkey /list` + Credential Manager dumps · DPAPI extraction · `Get-ChildItem Env:` piped outward | exfiltration surface |
| RC-7 Outbound exfiltration | `curl`/`wget` POST/PUT with local-file payloads to unlisted hosts · `scp`/`rsync`/`nc` outbound to new hosts | `Invoke-RestMethod`/`iwr -Method Post` with file payloads · `Send-MailMessage` · SMB copies to new UNC paths | data leaves the machine |
| RC-8 Persistence/system modification | shell-profile writes outside the skill's managed block · `crontab` edits · `launchctl` (macOS)/`systemctl` enable/load · `/etc/*` writes · hosts-file edits · kernel modules | `$PROFILE` writes outside the managed block · Registry Run keys (`reg add …\Run`) · `schtasks /create` · Startup folder writes · `C:\Windows\System32\drivers\etc\hosts` | survives the session, invisible later |
| RC-9 Cloud/infra destruction | `terraform destroy` · `aws s3 rb`/`rm --recursive` · `gcloud … delete` · `az … delete` · `kubectl delete ns/--all` · `DROP DATABASE/TABLE` · `redis-cli FLUSHALL/FLUSHDB` · `docker system prune -a --volumes` | same (cloud CLIs are cross-OS) | production blast radius |
| RC-10 Sandbox/permission weakening | harness flags that skip permissions (dangerously-skip class) · editing the permission config itself · disabling hooks | same + Defender/AV exclusion additions (`Add-MpPreference -ExclusionPath`) | removes the last guard |

### ASK by default (outward / consequential / reversible-with-effort)

| Class | Command patterns (seed set) |
|-------|------------------------------|
| RC-11 Publish/push | `git push` (non-force) · `npm publish` · `cargo publish` · `twine upload` · `gem push` · `docker push` · `gh release create` |
| RC-12 External writes | PR/issue creation · comments · API mutations via `gh api` non-GET |
| RC-13 Installs | package installs (pinned) · MCP registrations · extension installs |
| RC-14 Network fetch | fetches to hosts not seen before in the session · cloning new remotes |
| RC-15 Executable bits | `chmod +x` on downloaded files · running freshly downloaded binaries |
| RC-16 Data migrations | schema migration apply · bulk data update/delete scripts |

### Protected-path map (path-centric layer — complements the command classes)

Writes/deletes/permission-changes targeting these paths are **deny** regardless of which command performs them; reads of the credential group are deny (RC-6). One intent row, instantiated per detected OS at apply time — never apply one OS's column to another:

| Group (intent) | Linux | macOS | Windows |
|----------------|-------|-------|---------|
| System | `/etc` `/usr` `/bin` `/sbin` `/var` `/boot` `/opt` | same + `/System` `/Library` `/private` | `C:\Windows` `C:\Program Files*` `C:\ProgramData` |
| User-critical (credentials) | `~/.ssh` `~/.gnupg` `~/.aws` `~/.config/gcloud` `~/.kube` · keyrings | same + Keychain (`~/Library/Keychains`) | `%USERPROFILE%\.ssh` `.aws` `.kube` · Credential Manager/DPAPI stores · `%APPDATA%` credential dirs |
| Browser profiles | `~/.mozilla` `~/.config/{chromium,google-chrome}` | `~/Library/Application Support/{browser}` | `%LOCALAPPDATA%\{browser}\User Data` |
| Harness + rig configs | `~/.claude` `~/.codex` `~/.gemini` `~/.copilot` `~/.config/ds-rig` + per-harness settings files (RC-10 — the permission model must not edit itself) — except the skill's own gated, backed-up, additive writes | same | `%USERPROFILE%\.claude` etc. + `%APPDATA%`/`%LOCALAPPDATA%` harness dirs |
| Shell/persistence | `~/.bashrc` `~/.zshrc` `~/.profile` outside the managed block · systemd user units · crontabs | same + `~/Library/LaunchAgents` | PowerShell `$PROFILE` outside the managed block · Registry Run keys · Startup folder · Scheduled Tasks |

**OS instantiation rule:** path separators, home-dir notation (`~` vs `%USERPROFILE%`/`$env:USERPROFILE`), and case-sensitivity follow the detected OS; on WSL both the Linux column and mounted Windows paths (`/mnt/c/Windows`, `/mnt/c/Users/*/`) are protected.

### WORKSPACE AUTONOMY (allow — full permissions inside *whichever* project is open, written once, globally)

The rule is expressed with **cwd-relative path matchers** (`./**`, unprefixed globs — never an absolute path baked to one repo) written a single time into the harness's **global/user-scope** config. Because the matcher is relative, it re-resolves against whatever directory the harness is currently running in — opening a different project the next day auto-inherits the same rule with zero new entry, zero per-project file, zero repeat run of this skill. This is the mechanism, not a description of an outcome: **ds-rig never writes a project-scoped or repo-local permission file, and never hardcodes a specific project path into a rule.** A harness whose surface cannot express a *relative* scope (only accepts absolute per-project paths) cannot host this rule — gap-note it instead of falling back to a project-local file.

Effect: **allow file creation/edit/delete, project-local commands, test/build/lint runs without prompts** inside the project root currently open (and its declared temp/build dirs) — friction-free by design, for every harness whose surface can express a relative path scope (Claude Code path-scoped permissions; Codex workspace-write sandbox mode; Kilo Sandbox write-confinement; others via matcher prefixes).

Still enforced INSIDE the workspace (command-class risks are not path risks):
- RC-3 (sudo/escalation), RC-4 (unpinned remote code), RC-6 (credential reads), RC-7 (exfiltration), RC-10 (permission-config edits) remain deny.
- RC-5 git remote-destruction and RC-11 push/publish remain deny/ask — the working tree is free, the shared remote is not.
- Optional strictness (offer, default off): ask-gate reads of `.env*` / `*key*` / `secrets.*` files even inside the workspace.

### OFFICIAL HARNESS DIRECTORIES (allow — reads, everywhere, no ask)

Reads of the harness's own config, skill, plugin, and agent directories — the same paths named in the **Harness + rig configs** protected-path row (`~/.claude` incl. `skills/`, `plugins/`, `agents/`; `~/.codex`; `~/.gemini`; `~/.copilot`; `~/.config/ds-rig`; per-OS equivalents) — are **ALLOW, never ask**. A harness reading its own shipped or installed skill/plugin/agent definitions is not a trust boundary; prompting on it is friction with no security value and must not be written into the profile. **Writes/deletes to these paths remain DENY (RC-10)** except this skill's own gated, backed-up, additive writes — read and write are governed independently; loosening this row never extends to write access.

### ALLOW (read-only + rig tools, everywhere)

File reads within workspace · official harness directories (above) · `git status/log/diff/show` · `{rig tool} --version` · rtk-wrapped read commands · LSP queries · linters/formatters in check mode.

**Loosening any existing deny → never automatic; flag as needs-user-decision.**

### GLOBAL-ONLY WRITE SCOPE (binding on every phase of this skill)

ds-rig writes permission entries **exclusively to each harness's user/global-scope config file** — never to a project- or repo-scoped permission file, regardless of which project is open when the skill runs. This is what makes the rig machine-level: one write, every project inherits it via the cwd-relative matchers above. Concretely:

- Target the global path in the table below; never `.claude/settings.local.json` or a project's `.claude/settings.json`, never `.github/hooks/*.json`, never a project-root `kilo.jsonc` — even if one already exists and looks like the natural place to add a rule.
- A harness whose *only* documented permission surface is project/repo-scoped (no user-global file) cannot receive a workspace-autonomy write from this skill — gap-note it (see per-harness table) rather than writing the project file.
- If a project-local permission file is found to already exist (user's own prior config, not this skill's), leave it untouched and unread-into — it is out of scope, not a merge target.

## Honest limits (state these in the report)

1. **Pattern lists are not a sandbox.** Chaining (`a && b`), subshells, `sh -c`, base64 pipes, and aliases can evade naive matchers. Declarative lists raise the floor; they do not guarantee containment.
2. **Strength order — install the strongest arm the harness offers:** OS-level sandbox (e.g. Kilo Sandbox write-confinement) > scriptable blocking hook that parses the command (Claude Code/Codex/Gemini/Copilot `PreToolUse`-class) > declarative allow/ask/deny lists > prose rules. When a hook surface exists, mirror RC-1..RC-10 into a deny hook script, not just the list.
3. **The deny list must not become a wall:** over-denying trains users to bypass the profile. RC classes above are calibrated deny=irreversible, ask=consequential; keep that line when extending.

## Per-harness surfaces (verified state, 2026-07-15)

**ds-rig writes only the Global config path column. The Project-local equivalent column exists for detection/documentation only — never a write target; a harness whose only surface is project-local gets a gap-note instead.**

| Harness | Global config path (ds-rig's only write target) | Project-local equivalent (never touched) | Mechanism | Notes |
|---------|---------------------------------------------------|-------------------------------------------|-----------|-------|
| Claude Code | `~/.claude/settings.json` | `.claude/settings.json`, `.claude/settings.local.json` | declarative allow/deny/ask lists + `PreToolUse` hooks | merge with jq; never clobber `hooks.*` entries; mirror RC-1..10 in a hook for chain-resistance; workspace-autonomy rules use cwd-relative matchers here, not per-project files |
| Codex CLI | `~/.codex/hooks.json` | project-level hooks (need trusted project) | hook decisions | hooks are hash-pin trusted per user; `PreToolUse` intercepts simple shell + apply_patch + MCP, not every path — note the gap |
| Gemini CLI | `~/.gemini/settings.json` | project `.gemini/settings.json` | `BeforeTool` block/rewrite hooks | exit 0+`{"decision":"deny"}` or exit 2; Antigravity-CLI transition for unpaid tiers — re-verify surface |
| GitHub Copilot | `~/.copilot/hooks/` | `.github/hooks/*.json` (repo-scoped — out of scope for this skill) | `preToolUse` returns allow/deny/ask | only blocking event; no matchers — RC filtering lives in the script; provide bash+powershell; `toolArgs` is a JSON string — parse; if only the repo-scoped surface is available on this machine → gap-note, do not write it |
| Kilo Code | global Kilo settings (verify current path at apply time) | project-root `kilo.jsonc` (out of scope for this skill) | declarative patterns + OS-level Kilo Sandbox | the sandbox (global, machine-level) is the strongest deterministic guarantee in the thin-harness class; if only `kilo.jsonc` exists → gap-note |
| OpenCode | plugin hooks + global config (verify current docs at apply time) | project config | block semantics UNVERIFIED at catalog time | reads `~/.claude/skills/` for skills — apply once, covers both |
| Cursor / Windsurf (Devin Desktop) | no scriptable deny surface confirmed | — | — | gap-note; compensating control: ds-quality pre-commit arm + RC list in rules file (advisory only — say so) |
| Aider | none | — | — | gap-note; compensating control: ds-quality Aider arm (edit-time) + git hooks |

## Apply procedure (every harness)

1. Read the live permission doc for the harness; confirm the surface still matches the table.
2. Backup the target config with a timestamped copy.
3. Merge additively: RC-1..10 as deny, RC-11..16 as ask, allow-list entries for this run's installed tools. Existing user entries always win on conflict — show the conflict, ask.
4. Where the harness has a scriptable blocking hook, offer the hook-script arm (chain-resistant) in the same confirmation — recommended, per Honest limits.
5. Validate: host's own config check when available, else strict JSON/TOML parse.
6. Prove: diff backup→new shows only additions; record the diff summary in the manifest.
