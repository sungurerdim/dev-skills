# Contributing

Thanks for your interest in contributing to dev-skills! This guide covers how to add skills, report issues, and submit pull requests.

## How to Contribute

- **Report a bug** — Open an issue using the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Request a skill** — Open an issue using the [skill request template](.github/ISSUE_TEMPLATE/skill_request.md)
- **Fix a bug or improve a skill** — Fork, fix, and open a PR
- **Add a new skill** — Follow the structure below, then open a PR

## Skill Structure

Every skill is a self-contained folder:

```
ds-skill-name/
  SKILL.md        <- Instructions, execution flow, and contract
  README.md       <- What it does, install, usage, modes
  references/     <- Detailed rules loaded on demand (optional)
```

- Prefix skill folders with `ds-` (dev-skills namespace)
- Use kebab-case for folder names
- No dependencies between skills — each one stands alone

## Quality Standards

All skills must follow [SKILL-SPEC.md](SKILL-SPEC.md):

- **Size limits** — SKILL.md ≤500 lines, reference files loaded on demand, total skill overhead ≤10K tokens
- **Contract** — Every finding must cite file and line; standalone guarantee ("zero dependency on other skills")
- **FRC** — Every finding gets a disposition in the summary (fixed/skipped/failed/needs-approval/not-applicable) — zero silent drops
- **DSC** — Scopes that audit must define an explicit checklist of checks, every check evaluated every run
- **IDU** — When blueprint profile or `.ds-findings.md` exist, use them; when absent, run own complete analysis
- **Modes** — Provide at least audit-only and audit-and-fix modes where applicable
- **Overlap** — Skills may overlap in scope; `.ds-findings.md` deduplicates across producers

## Commit Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add ds-new-skill with 20 rules
fix: correct false positive in ds-compliance security check
docs: update ds-repo README with new scopes
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`

## Pull Request Process

1. Fork the repository and create a feature branch
2. Follow the skill structure and quality standards above
3. Update the root README.md skill table if adding a new skill
4. Fill out the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
5. Ensure your skill passes a self-audit: run `/ds-compliance` on your own skill folder

## Questions?

Open an issue — we're happy to help.
