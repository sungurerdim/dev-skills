# /ds-cv

ATS rejects most CVs before a human ever sees them. This skill generates ones that pass.

**CV Generator** — Professional, ATS-compatible HTML CV with LinkedIn companion guide.

## Triggers

- User runs `/ds-cv`, `/ds-cv generate`, `/ds-cv audit`, `/ds-cv update`, or `/ds-cv linkedin`
- User asks to create, update, or review a CV or resume
- User asks to align LinkedIn profile with their CV

### Triggers — ÇAĞIRIR / ÇAĞIRMAZ

| ÇAĞIRIR | ÇAĞIRMAZ |
|---------|----------|
| "generate ATS-compatible CV", "review my CV" | "audit my project for portfolio" (→ ds-blueprint) |
| "align LinkedIn profile with CV" | "personal brand marketing" (→ ds-market) |
| "update CV with new role" | "research career options" (→ ds-research) |

## Contract

- Always ask before assuming. Only include verified experience, metrics, skills.
- Every metric verified mathematically (cross-check math, confirm with user). Every achievement attributed to correct role — ask explicitly.
- Output: single HTML file with inline CSS. Only Google Fonts as external dependency.
- ATS-safe: zero non-ASCII characters in output, zero special HTML entities except `&amp;`.
- Privacy by default: omit email, phone, address, birth date, photo from public HTML.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `generate` | Full interactive CV generation |
| `audit` | Audit existing CV against best practices |
| `update` | Update existing HTML CV with new info |
| `linkedin` | Generate LinkedIn profile guide from CV |
| `--resume` | Resume from `ds/audit/cv.json` without prompting |
| `--clean` | Delete existing state and start fresh |
| (no flag) | Show command menu |

## Delegation

**Owns:** cv-generation, cv-ats-compatibility, cv-metric-verification, linkedin-alignment | **Delegates:** ds-research → candidate / market research; ds-docs → proofreading | **Receives:** none

## Execution Flow

Gather → Verify → Write → Generate → Audit → [Needs-Approval] → Deploy

### Phase 1: Gather [generate]

**Recovery check:** DETECT `ds/audit/cv.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (reconfirm gathered blocks), skip `done` phases, announce `[CV] Resuming from Phase {N}: {name}.` On successful Deploy, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start.

**State `data`:** `{ mode, sections_gathered: {identity, experience[], skills, education, gaps}, verifications_done[], html_generated, audit_findings[{id, severity, disposition}] }`.

**IDU:** Profile → Type + Stack, Project Map. Findings() → verify + use. Absent → own analysis.

1. **Identity:** Name (ask middle name — PII consideration), title, LinkedIn URL, GitHub URL, location + timezone, email preference (omit from public HTML — spam risk).
2. **Experience:** roles chronological, then per-role: company + descriptor, exact title (verify vs contract/LinkedIn), exact dates, technical/non-technical (bullet depth), management (team-led vs independent), 1-4 bullets with quantified results.
3. **Skills:** ask by CATEGORY after experience (informed by actual work). Filter: only defensible in interview. Exclude filler (`{generic-tool}`), redundancy (`{tool-A}` + `{tool-A-synonym}`), legacy signals, commoditized terms.
4. **Education:** degrees reverse-chronological, graduation year only. GPA only if ≥ 3.5/4. Expired certs with honest date range. Remove unfinished courses (`"Present"` on incomplete education = bad signal).
5. **Gap analysis:** map full timeline. Flag gaps > 6 months. Ask about same-company resignation/rehire scenarios.
6. **Privacy review:** anonymize family businesses (generic descriptor), ask about middle name, verify no sensitive company names exposed.

**Gate:** All roles, skills, education, gaps addressed. If fails → re-prompt missing section individually with targeted question; user explicitly skips → mark `[SKIPPED BY USER]` in state.data.sections_gathered, note omission in CV with placeholder so output is structurally complete.

### Phase 2: Verify [generate, update]

1. **Metric math:** every number's calculation verified. Example: `{before} to {after}` must equal `{before}/{after}` multiplier. Rounded ("`~{n}x`" vs exact `{m}x`) → confirm intentional.
2. **Role-achievement attribution:** "Which achievement belongs to which role?" Verify before including.
3. **Role chronology:** progression direction verified against actual dates.
4. **Combined role dates:** combining at same company → end date = actual departure. Resigned + returned → split entries.
5. **Unverifiable claims:** "`{n}+ repos`" — public? Not verifiable → remove specific number.
6. **Experience timeframe:** "since {year}" only if `{year}` has professional role. Hobby/student years don't count. Use "for over a decade" instead.
7. **Project ownership:** named projects must be publicly findable. Verify GitHub org membership is public.

**Gate:** All metrics verified, attributions confirmed. If fails → unverifiable item → remove from draft, add `[UNVERIFIED — OMITTED]` note in state.data.verifications_done, proceed with verified content only.

### Phase 3: Write [generate, update]

**Voice:** implied first person (no pronouns). Every bullet starts with action verb. Example: `"Built {what}..."` not `"I built..."`. LinkedIn About section exception — explicit first person standard there.

**Summary (3 sentences, 50-60 words):**
- S1: Who + how long + what you build
- S2: Differentiator + abstract top metric (`"up to {n}x speedups"`)
- S3: Background anchor (education / domain breadth)
- Summary metric MUST differ from experience bullets (abstract vs specific)

**Experience bullets (Action + What + Result):**

| Verb category | Verbs |
|---------------|-------|
| Building | Built, Developed, Created, Designed, Architected |
| Improving | Redesigned, Automated, Optimized, Reduced, Scaled |
| Leadership | Owned, Led, Established, Founded, Managed |
| Scope | Owned end-to-end, Delivered independently |

- Every role: min 1 bullet with a number. Max 1-2 printed lines per bullet.
- Concrete facts only — avoid speculation (`"likely still in use"`), jargon (`"cross-functional synergies"`), generic duties.
- Management role without team: `"Owned end-to-end"` not `"Led team"`.
- Non-technical roles: 1 bullet showing transferable impact.

**Other elements:**
- **Skills:** pill/tag format, neutral gray background. 4-5 categories, 2-5 items each.
- **Company descriptors:** first mention `"{Company} - {descriptor}"`, subsequent just name.
- **Role combining:** `"{Earlier-Title} to {Later-Title}"`. Resignation gap → split.
- **Metric highlights:** wrap only `{n}x` multipliers + named projects in `<strong>`. Style: italic + accent blue. Sparse highlights only.
- **Clickable links:** project URLs `<a target="_blank">` with underline. ATS reads as plain text — no compatibility risk.
- **Date badges:** uniform width ([references/css-design-system.md](references/css-design-system.md)).

**Gate:** All content follows rules, no filler, no jargon. If fails → flag violations inline with `[RULE VIOLATION: {reason}]` in draft, add to state.data.audit_findings, proceed (Phase 5 audits formally).

### Phase 4: Generate [generate, update]

1. **Character safety [CRITICAL]:** zero non-ASCII. No `&mdash;`/`&ndash;`/`&rarr;` — use `-` and `to`. Only `&amp;` allowed.
2. **Structure:** single column, semantic HTML (`h1`, `header`, `section`, `ul/li`, `span`). Text-only — no images, SVG, icons, canvas, JS.
3. **Section headings:** Professional Summary, Technical Skills, Experience, Education — standard names ATS recognizes.
4. **Design system:** load [references/css-design-system.md](references/css-design-system.md). Gestalt color-coding: role names (navy), company (slate italic), dates (blue badge), bullets (gray), skills (pill tags).
5. **Print CSS:** compressed for A4 single page. `page-break-inside: avoid` on sections and entries. `width: 100%; margin: 0` for print.
6. **OG meta tags:** `og:title`, `og:description`, `og:type` for link preview. Plain hyphen in all meta content.
7. **Final scan:** search for non-ASCII. Found → replace before delivering.
8. **Single-page auto-fit [CRITICAL]:** CSS flex auto-spacing for A4 (see references/css-design-system.md). Overflow → reduce print font incrementally (9pt → 8.5pt → 8pt).
9. **External resource minimization ([references/principles.md §5](references/principles.md)):** only Google Fonts CDN loads externally. Zero inline JavaScript. Page MUST be auditable with view-source alone.

**Gate:** Zero non-ASCII; print preview fits single A4; standard section headings. If fails → non-ASCII found → replace each with ASCII equivalent and re-scan; print overflow persists at 8pt floor → inform user `"Content requires 2 pages — cut a role or reduce bullet count to fit A4"`, deliver overflow version with note (no silent truncation).

### Phase 5: Audit [audit, generate]

Audit rules from [references/audit-rules.md](references/audit-rules.md). Key checks:

| Category | CRITICAL | HIGH | MEDIUM |
|----------|----------|------|--------|
| Content | Wrong dates, bad metric math, wrong role attribution | Unverifiable claims, jargon, metric dedup failure | Speculation, redundant skills, long bullets |
| Format | Special chars in HTML, print overflow | Multi-column, no standard headings | Inconsistent dates, poor hierarchy |
| Privacy | Birth date exposed | Email/phone/address in public HTML, real family business name | Photo, low GPA shown |
| Cross-doc | — | Metrics mismatch CV vs LinkedIn | Date/title mismatches |

**Gate:** Zero CRITICAL; all HIGH addressed or acknowledged. If fails → present each CRITICAL with `{file}:{line}` + required fix; do not proceed to Phase 6 until every CRITICAL is fixed or user explicitly overrides with documented reason in state.data.audit_findings[].disposition.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** All items resolved. If fails → forced binary re-prompt; no response → `skipped (no response)` and proceed.

### Phase 7: Deploy [generate]

1. **PDF:** instruct user: open in browser, print to PDF (Margins: None, Background graphics: ON). Verify single page.
2. **GitHub Pages [SKIP if user declines]:** create repo `{username}.github.io` (public); copy HTML as `index.html`, push; configure homepage URL, topics (`cv`, `resume`, `portfolio`, `github-pages`), disable issues/wiki/projects.
3. **LinkedIn guide [SKIP if user declines]:** generate from [references/linkedin-fields.md](references/linkedin-fields.md). Map every LinkedIn field. Achievement-based descriptions, not `"Responsibilities:"` style. Verify all metrics match CV.
4. **Reference file:** private career reference with excluded details, attribution mapping, metric proofs, gap explanations. Default path: `ds/cv/reference.md` (committed user record). User may pass `--reference={path}` to write outside repo. Never write to repo root or hidden dotfile.

**Summary:**

```
ds-cv: {OK|WARN|FAIL} | Sections: {n} | Metrics: {n} verified | ATS: {score} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

**Value Delivered:** 1-5 concrete bullets, real CV outputs only. Example shapes (placeholders, not literal):

- `ATS-compatible HTML CV generated ({n} kB, zero non-ASCII, inline CSS only) — passes every applicant tracking system without re-formatting`
- `{n} metrics verified mathematically ({claimed-value} vs cross-checked source) — no fabricated numbers reach a recruiter`
- `LinkedIn alignment guide produced — profile keywords match CV verbatim, no inconsistency penalty in recruiter search`

Audit-only run: `{n} audit findings on existing CV (severity: {breakdown}) — actionable list returned, no overwrite`.

**Gate:** PDF single page; GitHub Pages live; LinkedIn guide metrics match CV. If fails → GitHub Pages creation failed → manual deployment instructions; LinkedIn metric mismatch → list each mismatched field with CV value vs guide value, require user to confirm correct value before finalizing; summary status `WARN` noting skipped deploy steps.

## Quality Gates

- Every metric cites its calculation proof (input, output, multiplier)
- Every achievement attributed to a verified role
- Zero non-ASCII characters in final HTML output
- Summary metric differs from experience bullet metrics (abstract vs specific)
- Print CSS fits single A4 page
- All dates match between CV, LinkedIn guide, and reference file
- Company descriptors on first mention only
- Non-technical roles have ≥1 bullet showing transferable impact
- Experience timeframe claims match first professional role date
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/cv.json` updated per section gathered, gitignored, deleted on successful Deploy. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Unsure which role an achievement belongs to | Mark `unverified`, ask again with context. Only use confirmed data. |
| Metric math doesn't check out | Show calculation, ask for correct numbers |
| Print overflows 1 page | Reduce print CSS spacing. Still overflows → inform user: "Content requires 2 pages. Expand to fill page 2 meaningfully or cut a role." |
| GitHub Pages creation fails | Provide manual instructions |
| Non-ASCII found in final scan | Replace automatically, show what was replaced |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| User has 15+ roles | Combine older/shorter roles. Detailed bullets only for recent 5-7 roles. |
| Career changer (non-tech to tech) | Lead with tech experience. Older non-tech roles: 1 line each, no bullets. |
| Family business | Anonymize with generic descriptor (`"{Sector} Firm"`). Neutral descriptor on CV. |
| Concurrent roles (2× "Present") | Acceptable. Use `"Part-time"` for secondary to explain overlap. |
| Resignation + rehire same company | Split into separate entries with real dates. |
| User claims hobby/student-era experience | Challenge: "What professional work did you do then?" No paid role → use "for over a decade" or count from first professional role. |
| GPA below 3.5/4 | Omit from CV and LinkedIn. |
| Unfinished course with "Present" | Remove. `"Present"` on unfinished education = "started and quit" signal. |
| 3+ orphan lines on page 2 | Compress content or expand to fill half of page 2 meaningfully. |
