# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- 12 production-grade, tool-agnostic AI coding skills:
  - **Audit:** ds-compliance (web/API/CLI), ds-mobile (mobile apps), ds-devops (CI/CD & deps)
  - **Development:** ds-fix (format/lint/typecheck), ds-test (test lifecycle), ds-review (code quality & architecture), ds-docs (documentation), ds-blueprint (project health scoring)
  - **Git workflow:** ds-commit (smart commits), ds-pr (pull requests), ds-repo (repo health)
  - **Research:** ds-research (multi-source with CRAAP+ scoring)
- SKILL-SPEC.md — universal specification for tool-agnostic AI coding skills
- Findings pipeline (`.findings.md`) — inter-skill communication standard
- AI instruction patterns reference — research-backed best practices (2025-2026)
- GitHub issue and PR templates
- Contributing guidelines, security policy, and code of conduct

### Architecture
- Tool-agnostic design — works with Claude Code, Cursor, Copilot, Windsurf, Aider, and any AI coding tool
- Findings pipeline — analyzers produce `.findings.md`, fixers consume it, eliminating duplicate analysis
- Blueprint profile injection — auto-detects AI instruction file, embeds project profile with markdown heading markers
- Tier-based stack detection — 12 primary + 4 supplementary stacks with false-positive prevention
- 3-step project type detection — manifest → framework deps → secondary signals
