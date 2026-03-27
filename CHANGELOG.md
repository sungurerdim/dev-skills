# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- 20 production-grade, tool-agnostic AI coding skills:
  - **Audit:** ds-compliance (regulatory), ds-mobile (mobile apps), ds-devops (CI/CD & deps), ds-repo (repo health)
  - **Development:** ds-fix (format/lint/typecheck), ds-test (test lifecycle), ds-review (code quality & architecture), ds-docs (documentation), ds-blueprint (project health scoring)
  - **Design:** ds-backend (API + DB + auth), ds-deploy (infra + monitoring), ds-init (project scaffolding)
  - **Git workflow:** ds-commit (smart commits), ds-pr (pull requests)
  - **Research & Growth:** ds-research (multi-source with CRAAP+), ds-market (marketing strategy), ds-analytics (privacy-first analytics), ds-launch (store submission)
  - **Specialized:** ds-cv (ATS-proof CV generation), ds-tune (autonomous optimization loop)
  - **Frontend:** ds-frontend (design system audit, tokens, components, a11y, responsive, theming)
- SKILL-SPEC.md — universal specification for tool-agnostic AI coding skills
- Findings pipeline (`.ds-findings.md`) — single-file inter-skill communication standard
- Blueprint profile — project context shared across skills (type, stack, config, scores, run history)
- AI instruction patterns reference — research-backed best practices (2025-2026)
- GitHub issue and PR templates
- Contributing guidelines, security policy, and code of conduct
- Finding Resolution Completeness (FRC) — every finding gets a disposition, zero silent drops
- Deterministic Scope Checklist (DSC) — every scope check evaluated every run
- Inter-Skill Data Utilization (IDU) — skills read upstream artifacts with specific field→behavior mapping
- Mandatory phase enforcement — phases without `[CONDITION]` always execute, always produce output

### Architecture
- Tool-agnostic design — works with Claude Code, Cursor, Copilot, Windsurf, Aider, and any AI coding tool
- Findings pipeline — analyzers produce `.ds-findings.md`, fixers consume it, eliminating duplicate analysis
- Single findings file with append-and-dedup semantics — 4 producers, 11 consumers, scope-level dedup
- Blueprint profile — auto-detects AI instruction file, embeds project profile with markdown heading markers, legacy marker migration
- Blueprint produces 20 granular scopes mapped 1:1 to consumer scope names
- Tier-based stack detection — 12 primary + 4 supplementary stacks with false-positive prevention
- 3-step project type detection — manifest → framework deps → secondary signals
- Skill evaluation rubric — 8 criteria, 24-point scoring (FRC+DSC+IDU criteria included)
