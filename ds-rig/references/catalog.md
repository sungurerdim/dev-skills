# Rules: Rig Tool Catalog

Curated candidates per category. **The catalog is advisory — the Trust Gate verifies every entry against its live registry/repo/docs at run time.** Measured-benefit claims carry their evidence class; UNVERIFIED-at-catalog-time items say so. Every category names its zero-dependency fallback.

Universal privacy baseline (apply where honored, verify per tool): `DO_NOT_TRACK=1` in the shell profile; package-manager analytics off (e.g. `HOMEBREW_NO_ANALYTICS=1`). Mechanisms drift — re-verify against the tool's current official docs before applying.

## RIG-01 [HIGH] Token-reducing CLI proxy — rtk

CLI output filter (boilerplate filtering, similar-line grouping, smart truncation, dedup) applied before command output reaches the model.
- **Benefit:** 60-90% claimed savings on common dev commands (vendor-documented; session example 118K→23.9K tokens). Hook-based auto-rewrite of shell calls; 15 harnesses listed.
- **Install:** macOS `brew install rtk` · Linux prebuilt binary/curl script (pin the release tag) · Windows prebuilt `.zip` + WSL.
- **Privacy:** telemetry disabled by default (vendor-documented) — verify with the tool's telemetry status output after install.
- **Verify:** `rtk --version` + `rtk gain` produces output.
- **Uninstall:** `rtk init -g --uninstall` (removes the hook), then package-manager remove.
- **Limit:** intercepts shell-command output only — native file-read/search tool calls bypass it.
- **Fallback:** output-truncation conventions in the rules file (pipe through `head`/`tail`/`wc -l`; never dump >200 lines).

## RIG-02 [MEDIUM] Context-sandboxed execution MCP — context-mode

Sandboxed execution + BM25 retrieval; only logged output enters the conversation (documented 98%-class reductions, e.g. 315KB→5.4KB).
- **MANDATORY per-item confirmation:** maintainer-acknowledged sandbox-escape class — "ctx_execute … can execute arbitrary code and commands"; the boundary is defense-in-depth, not an OS sandbox. Present this verbatim before install; recommended only with the risk accepted.
- **Install:** MCP registration (Node-based) — pin the package version; never bare `npx -y`.
- **Verify:** `ctx_doctor` green.
- **Uninstall:** remove the MCP registration from the harness config.
- **Fallback:** ad-hoc scripts writing intermediates to temp files; agent reads only a summary.

## RIG-03 [HIGH] Persistent memory MCP — basic-memory

Local-first Markdown knowledge base with SQLite index; plain files, no lock-in (AGPL-3.0 — fine for install-your-own use).
- **Install:** `uv tool install basic-memory` (uv covers all 3 OS).
- **Privacy:** local-first by design — verify no sync/cloud feature is enabled by default in the current version's docs.
- **Verify:** MCP client lists its tools; a test note round-trips.
- **Uninstall:** `uv tool uninstall basic-memory` + remove MCP registration.
- **Fallback:** plain `NOTES.md`/`docs/adr/*.md` files the agent is instructed to read/update.

## RIG-04 [HIGH] LSP bridge — agent-lsp / Serena

Symbol-level navigation instead of text search: measured 5-34× fewer tokens than grep/read on the same tasks (two independent benchmarks; grep keeps literal-text search).
- **Install:** agent-lsp — curl script (pinned), brew, Scoop/Winget, pip, npm, or `go install`; Serena — MCP registration (adds to the MCP budget — count it).
- **Verify:** `hover`/`goToDefinition` returns a known symbol.
- **Uninstall:** package-manager remove / MCP deregistration.
- **Fallback:** native search tools; accept the measured cost.

## RIG-05 [HIGH] Git quality gate — pre-commit framework

Language-agnostic hook manager with `rev:`-pinned hooks (the pinning discipline this skill mirrors).
- **Install:** `pip install pre-commit` or `brew install pre-commit`.
- **Verify:** `pre-commit run --all-files` executes in a test repo.
- **Uninstall:** `pre-commit uninstall` + package remove.
- **Fallback:** native `.git/hooks/pre-commit` shell script (zero tooling).
- **Handoff:** wiring a project's quality gate is ds-quality's job — this entry only makes the framework available.

## RIG-06 [HIGH] Security scanners — gitleaks · osv-scanner · actionlint · zizmor · hadolint · typos

Deterministic scanners the Improve/Ship skills prefer over prose checks (each named advisorily there). Installing them machine-wide makes every skill's tool-first path available.
- **Install:** all available via brew; Linux/Windows via each repo's pinned releases.
- **Privacy:** verify per tool — osv-scanner queries the OSV API by design (network use is its function, not telemetry); document that distinction in the report.
- **Verify:** each `{tool} --version`.
- **Fallback:** the consuming skills' prose checks.

## RIG-07 [MEDIUM] Skill distribution — npx skills (Vercel) · dev-skills install.sh --target

Cross-harness skill installation. `npx skills` telemetry: anonymous usage data collected, disabled in CI — **opt out explicitly per its current docs, or prefer `install.sh --target` (zero telemetry, this repo).**
- **Verify:** installed skill dir listing per target harness.
- **Fallback:** manual copy into host skill dirs.

## RIG-08 [LOW] Base CLI utilities — gh · ripgrep · jq · fd

Widely-assumed baseline for the other skills' tool-first paths.
- **Privacy:** gh — apply the update-check opt-out per current gh docs; others have no call-home (verify at install).
- **Verify:** each `{tool} --version`.
- **Fallback:** POSIX grep/find; GitHub web UI.

## Observability tier — deliberately excluded

Dedicated agent-observability platforms (Laminar/Langfuse class) add accounts + infra and conflict with the zero-call-home mandate. When the harness emits OpenTelemetry locally, that is user-side and acceptable; anything exporting to a vendor is out of catalog scope.
