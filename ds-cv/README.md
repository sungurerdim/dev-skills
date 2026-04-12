# ds-cv

Generate professional, ATS-compatible HTML CVs with LinkedIn profile alignment.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-cv ~/.claude/skills/ds-cv` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-cv`, or ask to create, update, or audit your CV.

```
/ds-cv generate    # Full interactive CV generation
/ds-cv audit       # Audit existing CV against best practices
/ds-cv update      # Update existing HTML CV with new info
/ds-cv linkedin    # Generate LinkedIn profile guide from CV
```

## Features

- ATS-safe output: zero non-ASCII, standard headings, single column, semantic HTML
- Gestalt-driven design: color-coded info types (role, company, dates, skills)
- Metric verification: cross-checks math, confirms role attribution
- Privacy by default: no email/phone/address in public HTML
- LinkedIn companion: maps every form field, achievement-based descriptions
- Print-optimized: single A4 page with compressed print CSS
- Career reference file: full history with excluded details for future use

## Output Files

| File | Purpose | Visibility |
|------|---------|------------|
| `cv.html` | CV source (HTML+CSS) | Public |
| `linkedin-profile-guide.md` | LinkedIn update guide | Private |
| `cv-reference-full.md` | Full career reference | Private |
