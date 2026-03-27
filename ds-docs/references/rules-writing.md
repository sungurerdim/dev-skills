# Rules: Documentation Quality

Rules for all doc generation/audit/verify modes. Each rule: ID, severity, detect pattern, fix action, source.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Structure & Content** | DOC-01 to DOC-04 (2 HIGH, 2 MEDIUM) | ~12 |
| **Maintenance & Tools** | DOC-05 to DOC-08 (2 MEDIUM, 2 LOW) | ~70 |

---

## Structure & Content

### DOC-01 | HIGH | README Hook

**Detect:** README starts with the project name, a badge wall, a feature list, or a generic description ("A library for..."). First line describes what the project is rather than why it matters.

**Fix:** Lead with a pain-point statement or contrarian hook in 10 words or fewer. Follow with the solution framing.

```markdown
<!-- Before -->
# MyTool
A CLI tool for managing Docker deployments with zero-config setup.

<!-- After -->
# MyTool
AI commits are vague and bundle unrelated changes.

MyTool analyzes your staged changes and generates atomic,
context-aware commit messages.
```

**Why:** Repos with compelling READMEs receive 4x more stars and 6x more contributors. The first line determines whether a visitor reads further or bounces. A pain-point hook creates immediate recognition and relevance.

**Source:** Launch research (rivereditor.com, GitHub analysis), .launch-research.md Pattern 6

---

### DOC-02 | HIGH | Verified Code Examples

**Detect:** Code blocks in documentation contain snippets that have drifted from the actual source code. Example output, function signatures, or API calls reference outdated implementations.

**Fix:** Verify every code block against the current source. Prefer auto-generated documentation (OpenAPI for REST, TypeDoc for TypeScript, rustdoc for Rust, Sphinx for Python) to keep examples in sync with implementation. For manually written examples, include the source file path as a comment.

```markdown
<!-- Include source reference for manual examples -->
```javascript
// From: src/config.ts#L42-L55
const config = loadConfig({ strict: true });
```
```

**Why:** Incorrect code examples waste developer time and erode trust. Auto-generated docs eliminate drift by construction.

**Source:** SKILL-SPEC verify scope, documentation best practices

---

### DOC-03 | MEDIUM | Quick Start in 5 Commands or Fewer

**Detect:** Getting started section requires more than 5 commands or more than 10 minutes for a new user to reach a working state.

**Fix:** Reduce setup to the minimum path: clone, install, run (3 commands ideal). Provide copy-paste blocks with expected output.

```markdown
## Quick Start

```bash
git clone https://github.com/user/project && cd project
npm install
npm start
# Server running at http://localhost:3000
```
```

For projects requiring configuration, provide sensible defaults or a setup script:

```bash
cp .env.example .env   # defaults work out of the box
npm install && npm start
```

**Why:** Every additional setup step loses a percentage of potential contributors. The 10-minute threshold aligns with the average attention span for evaluating a new tool.

**Source:** GitHub README best practices, launch research (Quick Start pattern)

---

### DOC-04 | MEDIUM | Scannable Format

**Detect:** Documentation sections contain more than 5 consecutive prose paragraphs without structural breaks (headings, tables, bullet lists, or code blocks).

**Fix:** Break dense prose into scannable elements:

- **Comparisons:** Use tables
- **Steps/procedures:** Use numbered lists
- **Options/features:** Use bullet lists
- **Concepts:** Use heading + 1-3 sentence summary + example

| Format | Use When |
|--------|----------|
| Table | Comparing 3+ items across 2+ dimensions |
| Bullet list | Enumerating items without priority |
| Numbered list | Sequential steps or ranked items |
| Code block | Any executable or configuration example |
| Heading | Every new concept or topic shift |

**Why:** Developers scan documentation; they rarely read linearly. Structured content reduces time-to-answer by 40-60% compared to prose walls.

**Source:** Nielsen Norman Group readability research, technical writing best practices

---

## Maintenance & Tools

### DOC-05 | MEDIUM | Link Freshness

**Detect:** Documentation contains links returning 404, pointing to moved pages, or referencing outdated URLs (e.g., old API versions, deprecated docs sites).

**Fix:** Verify all links resolve correctly. Use relative links for internal references (resilient to domain changes). For external links, prefer canonical URLs over blog posts or tutorials that may be removed.

```markdown
<!-- Prefer relative for internal -->
See [Configuration](./docs/config.md)

<!-- Prefer canonical for external -->
See [Express docs](https://expressjs.com/en/guide/routing.html)
```

**Why:** Broken links signal unmaintained documentation and send users to dead ends. A single 404 in a getting-started guide can block adoption.

**Source:** Web maintenance best practices

---

### DOC-06 | MEDIUM | Auto-Generated API Documentation

**Detect:** API documentation is manually written in a separate file, disconnected from the source code. Changes to the implementation require updating docs in a second location.

**Fix:** Use the framework's canonical documentation generator:

| Stack | Tool | Source |
|-------|------|--------|
| REST API | OpenAPI/Swagger (auto-generate from routes) | openapis.org |
| GraphQL | Schema introspection + GraphiQL | graphql.org |
| TypeScript library | TypeDoc | typedoc.org |
| Rust library | rustdoc (built-in) | doc.rust-lang.org |
| Python library | Sphinx + autodoc | sphinx-doc.org |
| Go library | godoc (built-in) | pkg.go.dev |

**Why:** Manually maintained API docs inevitably drift from implementation. Auto-generation makes source code the single source of truth.

**Source:** OpenAPI 3.1 specification, framework-specific documentation standards

---

### DOC-07 | LOW | Badge Discipline

**Detect:** README displays more than 7 badges, creating visual clutter that pushes the actual content below the fold.

**Fix:** Keep 4-7 badges maximum. Prioritize actionable information:

| Keep | Remove |
|------|--------|
| Build/CI status | "PRs welcome" |
| Test coverage | "Made with love" |
| Latest version/release | Duplicate status badges |
| License | Platform badges that add no info |

**Why:** Badge walls create visual noise and delay the reader from reaching the content that determines whether they will use or contribute to the project. Screenshots increase stars approximately 42%; excessive badges do the opposite.

**Source:** Launch research (README best practices), .launch-research.md Pattern 6

---

### DOC-08 | LOW | Changelog in Standard Format

**Detect:** No `CHANGELOG.md` file, or changelog exists in a non-standard format (e.g., raw git log dumps, unstructured notes).

**Fix:** Follow the Keep a Changelog format with sections for Added, Changed, Deprecated, Removed, Fixed, and Security. Auto-generate from conventional commits where the project uses them.

```markdown
# Changelog

## [1.2.0] - 2026-03-15

### Added
- Health check endpoint with dependency verification

### Fixed
- SSL certificate renewal failing silently on Caddy restart

## [1.1.0] - 2026-02-28

### Changed
- Switched from Nginx to Caddy for automatic HTTPS
```

**Why:** A well-maintained changelog helps users decide whether to upgrade and understand breaking changes without reading commit history. It is often the first file checked before a version bump.

**Source:** Keep a Changelog (keepachangelog.com), Semantic Versioning
