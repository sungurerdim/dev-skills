# /ds-cv

ATS rejects most CVs before a human ever sees them. This skill generates ones that pass.

**CV Generator** — Professional, ATS-compatible HTML CV with LinkedIn companion guide.

## Triggers

- User runs `/ds-cv`, `/ds-cv generate`, `/ds-cv audit`, `/ds-cv update`, or `/ds-cv linkedin`
- User asks to create, update, or review a CV or resume
- User asks to align LinkedIn profile with their CV

## Contract

- Always ask before assuming. Only include verified experience, metrics, and skills.
- Every metric is verified: cross-check math (e.g., if "Xh to Yh" then multiplier = X/Y). Confirm with user.
- Every achievement attributed to correct role. Ask explicitly.
- Output: single HTML file with inline CSS. Only Google Fonts as external dependency.
- All content ATS-safe: zero non-ASCII characters in output, zero special HTML entities except `&amp;`.
- Privacy by default: omit email, phone, address, birth date, and photo from public HTML.
- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect | Default |
|------|--------|---------|
| `generate` | Full interactive CV generation | - |
| `audit` | Audit existing CV against best practices | - |
| `update` | Update existing HTML CV with new info | - |
| `linkedin` | Generate LinkedIn profile guide from CV | - |
| `--resume` | Resume from `ds/audit/cv.json` without prompting | - |
| `--clean` | Delete existing state and start fresh | - |
| (no flag) | Show command menu | - |

## Delegation

**Owns:** cv-generation, cv-ats-compatibility, cv-metric-verification, linkedin-alignment | **Delegates:** ds-research → candidate / market research; ds-docs → proofreading | **Receives:** none

## Execution Flow

Gather -> Verify -> Write -> Generate -> Audit -> [Needs-Approval] -> Deploy

### Phase 1: Gather [generate]

**Recovery check:** DETECT `ds/audit/cv.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD (project context changed). Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (reconfirm gathered identity/experience blocks are still correct), skip `done` phases, announce `[CV] Resuming from Phase {N}: {name}.` On successful Deploy, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start, append if missing.

**State `data` shape:** `{ mode, sections_gathered: {identity, experience[], skills, education, gaps}, verifications_done[], html_generated, audit_findings[{id, severity, disposition}] }`.

**Findings file check:** If `ds/audit/findings.md` exists with fresh `git_hash`, check for relevant findings that may inform CV content (project metrics, quality scores).

**IDU:** Profile → Type + Stack, Project Map. Findings() → verify + use. Absent → own analysis.

1. **Identity:** Name (ask about middle name - PII consideration), title, LinkedIn URL, GitHub URL, location + timezone, email preference (omit from public HTML - spam risk).
2. **Experience:** List all roles chronologically first, then detail each:
   - Company + descriptor, exact title (verify against contract/LinkedIn), exact dates
   - Technical or non-technical? (determines bullet depth)
   - Management: "Did you manage a team, or work independently?"
   - 1-4 bullet points per role with quantified results
3. **Skills:** Ask by CATEGORY after experience (informed by actual work). Filter: only defensible in interview. Exclude filler (Git, Agile), redundancy (GitHub Actions + CI/CD), legacy signals (VBA), commoditized terms (Prompt Engineering).
4. **Education:** Degrees reverse-chronological, graduation year only. GPA only if >= 3.5/4. Expired certs with honest date range. Remove unfinished courses ("Present" on incomplete education = bad signal).
5. **Gap analysis:** Map full timeline after collecting roles. Flag gaps > 6 months. Ask about same-company resignation/rehire scenarios.
6. **Privacy review:** Anonymize family businesses (generic descriptor), ask about middle name, verify no sensitive company names exposed.

**Gate:** All roles, skills, education, gaps addressed. Proceed to verify. If fails → user has not provided details for one or more required sections (e.g., no roles given, no skills listed); re-prompt for each missing section individually with a concise targeted question; if user explicitly skips a section, mark it as `[SKIPPED BY USER]` in state.data.sections_gathered and note the omission in the CV with a placeholder so the output is structurally complete.

### Phase 2: Verify [generate, update]

1. **Metric math:** For every number, verify calculation. Example: "Xh to Yh" must equal X/Y multiplier. If user rounds ("~700x" when exact is 630x), confirm intentional.
2. **Role-achievement attribution:** Ask "Which achievement belongs to which role?" for each. Verify before including — confirm by role title match.
3. **Role chronology:** Verify progression direction. "BAS to PM" or "PM to BAS"? Check actual dates.
4. **Combined role dates:** Combining roles at same company → end date = actual departure date. If user resigned and returned, split into separate entries.
5. **Unverifiable claims:** "20+ repos" - are they public? Not verifiable → remove specific number.
6. **Experience timeframe:** "since YYYY" only if YYYY has a professional role. Hobby/student years don't count. Use "for over a decade" instead.
7. **Project ownership:** Named projects must be publicly findable. Verify GitHub org membership is public if claiming project ownership.

**Gate:** All metrics verified, attributions confirmed. Proceed to write. If fails → a metric's math does not check out and user cannot provide correct numbers, or an attribution cannot be confirmed to a specific role; remove the unverifiable metric or attribution from the draft, add a `[UNVERIFIED — OMITTED]` note in state.data.verifications_done for that item, and proceed with only verified content.

### Phase 3: Write [generate, update]

**Voice:** Implied first person (no pronouns). Start every bullet with action verb, drop "I/He/She". Example: "Built Docker automation..." not "I built..." or "He built...". LinkedIn About section is exception - explicit first person ("I build...") is standard there.

**Summary (3 sentences, 50-60 words):**
- Sentence 1: Who + how long + what you build
- Sentence 2: Differentiator + abstract top metric (e.g., "up to Nx speedups")
- Sentence 3: Background anchor (education/domain breadth)
- Summary metric MUST differ from experience bullets (abstract vs specific)

**Experience bullets (Action + What + Result):**
- Building verbs: Built, Developed, Created, Designed, Architected
- Improving verbs: Redesigned, Automated, Optimized, Reduced, Scaled
- Leadership verbs: Owned, Led, Established, Founded, Managed
- Scope verbs: Owned end-to-end, Delivered independently
- Every role: min 1 bullet with a number. Max line: 1-2 printed lines.
- Use concrete facts only — avoid speculation ("likely still in use"), jargon ("cross-functional synergies"), and generic duties ("led optimization initiatives")
- Management role without team: "Owned end-to-end" not "Led team"
- Non-technical roles: 1 bullet showing transferable impact

**Skills:** Pill/tag format, neutral gray background (not accent color). 4-5 categories, 2-5 items each.

**Company descriptors:** First mention "Company - Descriptor", subsequent just name.

**Role combining:** Format "Earlier Title to Later Title". Resignation gap → split entries.

**Metric highlights:** Wrap only Nx multipliers and named projects in `<strong>`. Style: italic + accent blue color (#1a56a8). Keep highlights sparse - if everything is highlighted, nothing stands out.

**Clickable links:** Project URLs use `<a target="_blank">` with underline. Header links (LinkedIn, GitHub) also `target="_blank"`. ATS reads links as plain text - no compatibility risk.

**Date badges:** All date badges must have uniform width (see `references/css-design-system.md`).

**Gate:** All content follows rules, no filler, no jargon. Proceed to generate. If fails → one or more bullets contain jargon, filler skills, or non-imperative-mood phrasing that the user insists on keeping; flag each violation inline with `[RULE VIOLATION: {reason}]` in the written draft, add those items to state.data.audit_findings, and proceed to generation — the audit phase (Phase 5) will surface them formally.

### Phase 4: Generate [generate, update]

1. **Character safety [CRITICAL]:** Zero non-ASCII in output. No `&mdash;` `&ndash;` `&rarr;` - use `-` and `to`. Title tag uses plain hyphen. Only `&amp;` is allowed.
2. **Structure:** Single column, semantic HTML (h1, header, section, ul/li, span). Only text-based elements — exclude images, SVG, icons, canvas, JavaScript.
3. **Section headings:** Professional Summary, Technical Skills, Experience, Education - standard names ATS recognizes.
4. **Design system:** Load from `references/css-design-system.md`. Gestalt color-coding: role names (navy), company (slate italic), dates (blue badge), bullets (gray), skills (pill tags).
5. **Print CSS:** Compressed spacing for A4 single page. `page-break-inside: avoid` on sections and entries. `width: 100%; margin: 0` for print.
6. **OG meta tags:** Add `og:title`, `og:description`, `og:type` for link preview. Plain hyphen in all meta content.
7. **Final scan:** Execute character scan - search for any non-ASCII characters. Found → replace before delivering.

8. **Single-page auto-fit [CRITICAL]:** Use CSS flex auto-spacing for single-page A4 fit (see `references/css-design-system.md`). Overflow → reduce print font-size incrementally (9pt -> 8.5pt -> 8pt). Ensure every delivered CV fits within page bounds.

9. **External resource minimization ([references/principles.md §5](references/principles.md)):** Verify only Google Fonts CDN loads externally — no other third-party scripts, tracking pixels, analytics SDKs, or remote images. Zero inline JavaScript. The deployed page MUST be auditable with view-source alone.

**Gate:** Zero non-ASCII characters. Print preview fits single A4. All section headings standard. If fails → non-ASCII characters found after final scan: replace each with its ASCII equivalent and re-scan; print overflow persists after all font-size reductions (8pt floor): inform user `"Content requires 2 pages — cut a role or reduce bullet count to fit A4"` and deliver the overflow version with a note rather than silently truncating content.

### Phase 5: Audit [audit, generate]

Load audit rules from `references/audit-rules.md`. Key checks:

| Category | CRITICAL | HIGH | MEDIUM |
|----------|----------|------|--------|
| Content | Wrong dates, bad metric math, wrong role attribution | Unverifiable claims, jargon, metric dedup failure | Speculation, redundant skills, long bullets |
| Format | Special chars in HTML, print overflow | Multi-column, no standard headings | Inconsistent dates, poor hierarchy |
| Privacy | Birth date exposed | Email/phone/address in public HTML, real family business name | Photo, low GPA shown |
| Cross-doc | - | Metrics mismatch between CV and LinkedIn | Date/title mismatches |

**Gate:** Zero CRITICAL findings. All HIGH addressed or acknowledged. If fails → CRITICAL findings remain (wrong dates, bad metric math, or PII exposed in HTML); present each CRITICAL finding to the user with the specific file:line and the required fix; do not proceed to Phase 6 until every CRITICAL is either fixed or the user explicitly overrides with a documented reason in state.data.audit_findings[].disposition.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped). If fails → one or more needs_approval items have no decision recorded; re-present each unresolved item with a forced binary prompt (Apply / Skip); if user declines to respond, mark as `skipped (no response)` and proceed.

### Phase 7: Deploy [generate]

1. **PDF:** Instruct user: open in browser, print to PDF (Margins: None, Background graphics: ON). Verify single page.
2. **GitHub Pages [SKIP if user declines]:**
   - Create repo: `{username}.github.io` (public)
   - Copy HTML as `index.html`, push
   - Configure: homepage URL, topics (cv, resume, portfolio, github-pages), disable issues/wiki/projects
3. **LinkedIn guide [SKIP if user declines]:** Generate from `references/linkedin-fields.md`. Map every LinkedIn form field. Achievement-based descriptions, not "Responsibilities:" style. Verify all metrics match CV.
4. **Reference file:** Generate private career reference with all excluded details, attribution mapping, metric proofs, gap explanations. Default path: `ds/cv/reference.md` (committed; the user's private record). User may pass `--reference=<path>` to write outside the repo (e.g., `~/Documents/cv-reference.md`). Never write to repo root or to a hidden dotfile — both violate the dev-skills artifact discipline (data outside `ds/audit/` or `ds/<skill>/` namespaces).

**Summary format:**
```
ds-cv: {OK|WARN|FAIL} | Sections: N | Metrics: N verified | ATS: {score} | Fixed: N | Skipped: N | Failed: N | Total: N
```

**Gate:** PDF renders single page. GitHub Pages live. LinkedIn guide metrics match CV. If fails → GitHub Pages creation failed (repo already exists, permissions error, or user declined); provide manual deployment instructions (create `{username}.github.io` repo, push `index.html`); if LinkedIn guide metrics do not match CV, list each mismatched field with CV value vs guide value and require the user to confirm which is correct before finalizing the guide; print summary with status `WARN` noting which deploy steps were skipped.

## Quality Gates

- Every metric cites its calculation proof (input, output, multiplier)
- Every achievement attributed to a verified role
- Zero non-ASCII characters in final HTML output
- Summary metric differs from experience bullet metrics (abstract vs specific)
- Print CSS → single A4 page
- All dates match between CV, LinkedIn guide, and reference file
- All company descriptors appear only on first mention
- All non-technical roles have at least 1 bullet showing transferable impact
- Experience timeframe claims match first professional role date
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/cv.json` updated per section gathered, gitignored, deleted on successful Deploy.

## Error Recovery

| Situation | Action |
|-----------|--------|
| User unsure which role an achievement belongs to | Mark as "unverified", ask again with context. Only use confirmed data. |
| Metric math doesn't check out | Show calculation, ask user for correct numbers |
| Print overflows 1 page | Reduce print CSS spacing incrementally. Still overflows → inform user: "Content requires 2 pages. Expand to fill page 2 meaningfully or cut a role." |
| GitHub Pages creation fails | Provide manual instructions |
| Non-ASCII found in final scan | Replace automatically, show what was replaced |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| User has 15+ roles | Combine older/shorter roles. Keep detailed bullets only for recent 5-7 roles. |
| Career changer (non-tech to tech) | Lead with tech experience. Older non-tech roles: 1 line each, no bullets. |
| Family business | Anonymize with generic descriptor (e.g., "Consulting Firm"). Use neutral company descriptor on CV. |
| Concurrent roles (2x "Present") | Acceptable. Use "Part-time" for secondary role to explain overlap. |
| Resignation and rehire at same company | Split into separate entries with real dates. Keep each entry separate to show accurate timeline. |
| User claims experience from hobby/student era | Challenge: "What professional work did you do in that period?" No paid role → use "for over a decade" or count from first professional role. |
| GPA below 3.5/4 | Omit from CV and LinkedIn. Only display GPA >= 3.5/4. |
| Unfinished course with "Present" | Remove. "Present" on unfinished education = "started and quit" signal. |
| 3+ orphan lines on page 2 | Compress content or expand to fill half of page 2 meaningfully. Page 2 must be either empty or meaningfully filled. |
