# /ds-cv

**CV Generator** — Professional, ATS-compatible HTML CV with LinkedIn companion guide.

## Triggers

- User runs `/ds-cv`, `/ds-cv generate`, `/ds-cv audit`, `/ds-cv update`, or `/ds-cv linkedin`
- User asks to create, update, or review a CV or resume
- User asks to align LinkedIn profile with their CV

## Contract

- Always ask before assuming. Never fabricate experience, metrics, or skills.
- Every metric is verified: cross-check math (e.g., if "Xh to Yh" then multiplier = X/Y). Confirm with user.
- Every achievement is attributed to the correct role. Ask explicitly.
- Output is a single HTML file with inline CSS. No external dependencies except Google Fonts.
- All content is ATS-safe: zero non-ASCII characters in output, zero special HTML entities except `&amp;`.
- Privacy by default: no email, phone, address, birth date, or photo in public HTML.
- Fully functional standalone — no dependency on other skills or external specs.

## Arguments

| Flag | Effect | Default |
|------|--------|---------|
| `generate` | Full interactive CV generation | - |
| `audit` | Audit existing CV against best practices | - |
| `update` | Update existing HTML CV with new info | - |
| `linkedin` | Generate LinkedIn profile guide from CV | - |
| (no flag) | Show command menu | - |

## Execution Flow

Gather -> Verify -> Write -> Generate -> Audit -> Deploy

### Phase 1: Gather [generate]

**Goal:** Collect all career data through structured questions. Never guess.

1. **Identity:** Name (ask about middle name - PII consideration), title, LinkedIn URL, GitHub URL, location + timezone, email preference (omit from public HTML - spam risk).
2. **Experience:** List all roles chronologically first, then detail each:
   - Company + descriptor, exact title (verify against contract/LinkedIn), exact dates
   - Technical or non-technical? (determines bullet depth)
   - Management: "Did you manage a team, or work independently?"
   - 1-4 bullet points per role with quantified results
3. **Skills:** Ask by CATEGORY after experience (informed by actual work). Filter: only defensible in interview. No filler (Git, Agile), no redundancy (GitHub Actions + CI/CD), no legacy signals (VBA), no commoditized terms (Prompt Engineering).
4. **Education:** Degrees reverse-chronological, graduation year only. GPA only if >= 3.5/4. Expired certs with honest date range. Remove unfinished courses ("Present" on incomplete education = bad signal).
5. **Gap analysis:** Map full timeline after collecting roles. Flag gaps > 6 months. Ask about same-company resignation/rehire scenarios.
6. **Privacy review:** Anonymize family businesses (generic descriptor), ask about middle name, verify no sensitive company names exposed.

**Gate:** All roles, skills, education, gaps addressed. Proceed to verify.

### Phase 2: Verify [generate, update]

**Goal:** Catch every factual error before generating.

1. **Metric math:** For every number, verify the calculation. Example: "Xh to Yh" must equal X/Y multiplier. If user rounds ("~700x" when exact is 630x), confirm intentional.
2. **Role-achievement attribution:** Ask "Which achievement belongs to which role?" for each. Never assume by role title.
3. **Role chronology:** Verify progression direction. "BAS to PM" or "PM to BAS"? Check actual dates.
4. **Combined role dates:** If combining roles at same company, end date = actual departure date. If user resigned and returned, split into separate entries.
5. **Unverifiable claims:** "20+ repos" - are they public? If not verifiable, remove specific number.
6. **Experience timeframe:** "since YYYY" only if YYYY has a professional role. Hobby/student years don't count. Use "for over a decade" instead.
7. **Project ownership:** Named projects must be publicly findable. Verify GitHub org membership is public if claiming project ownership.

**Gate:** All metrics verified, attributions confirmed. Proceed to write.

### Phase 3: Write [generate, update]

**Goal:** Produce polished, professional content.

**Voice:** Implied first person (no pronouns). Start every bullet with action verb, drop "I/He/She". Example: "Built Docker automation..." not "I built..." or "He built...". LinkedIn About section is the exception - explicit first person ("I build...") is standard there.

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
- No speculation ("likely still in use"), no jargon ("cross-functional synergies"), no generic duties ("led optimization initiatives")
- Management role without team: "Owned end-to-end" not "Led team"
- Non-technical roles: 1 bullet showing transferable impact

**Skills:** Pill/tag format, neutral gray background (not accent color). 4-5 categories, 2-5 items each.

**Company descriptors:** First mention "Company - Descriptor", subsequent just name.

**Role combining:** Format "Earlier Title to Later Title". If resignation gap, split entries.

**Metric highlights:** Wrap only Nx multipliers and named projects in `<strong>`. Style: italic + accent blue color (#1a56a8). Keep highlights sparse - if everything is highlighted, nothing stands out.

**Clickable links:** Project URLs use `<a target="_blank">` with underline. Header links (LinkedIn, GitHub) also `target="_blank"`. ATS reads links as plain text - no compatibility risk.

**Date badges:** All date badges must have uniform width (see `references/css-design-system.md`).

**Gate:** All content follows rules, no filler, no jargon. Proceed to generate.

### Phase 4: Generate [generate, update]

**Goal:** Produce ATS-safe, single-page A4 HTML.

1. **Character safety [CRITICAL]:** Zero non-ASCII in output. No `&mdash;` `&ndash;` `&rarr;` - use `-` and `to`. Title tag uses plain hyphen. Only `&amp;` is allowed.
2. **Structure:** Single column, semantic HTML (h1, header, section, ul/li, span). No images, SVG, icons, canvas, JavaScript.
3. **Section headings:** Professional Summary, Technical Skills, Experience, Education - standard names ATS recognizes.
4. **Design system:** Load from `references/css-design-system.md`. Gestalt color-coding: role names (navy), company (slate italic), dates (blue badge), bullets (gray), skills (pill tags).
5. **Print CSS:** Compressed spacing for A4 single page. `page-break-inside: avoid` on sections and entries. `width: 100%; margin: 0` for print.
6. **OG meta tags:** Add `og:title`, `og:description`, `og:type` for link preview. Plain hyphen in all meta content.
7. **Final scan:** Execute character scan - search for any non-ASCII characters. If found, replace before delivering.

8. **Single-page auto-fit [CRITICAL]:** Use CSS flex auto-spacing for single-page A4 fit (see `references/css-design-system.md`). If overflow, reduce print font-size incrementally (9pt -> 8.5pt -> 8pt). Never deliver a CV that overflows.

**Gate:** Zero non-ASCII characters. Print preview fits single A4. All section headings standard.

### Phase 5: Audit [audit, generate]

**Goal:** Catch all content, format, and privacy issues.

Load audit rules from `references/audit-rules.md`. Key checks:

| Category | CRITICAL | HIGH | MEDIUM |
|----------|----------|------|--------|
| Content | Wrong dates, bad metric math, wrong role attribution | Unverifiable claims, jargon, metric dedup failure | Speculation, redundant skills, long bullets |
| Format | Special chars in HTML, print overflow | Multi-column, no standard headings | Inconsistent dates, poor hierarchy |
| Privacy | Birth date exposed | Email/phone/address in public HTML, real family business name | Photo, low GPA shown |
| Cross-doc | - | Metrics mismatch between CV and LinkedIn | Date/title mismatches |

**Gate:** Zero CRITICAL findings. All HIGH addressed or acknowledged.

### Phase 6: Deploy [generate]

**Goal:** CV accessible as PDF and web page.

1. **PDF:** Instruct user: open in browser, print to PDF (Margins: None, Background graphics: ON). Verify single page.
2. **GitHub Pages [SKIP if user declines]:**
   - Create repo: `{username}.github.io` (public)
   - Copy HTML as `index.html`, push
   - Configure: homepage URL, topics (cv, resume, portfolio, github-pages), disable issues/wiki/projects
3. **LinkedIn guide [SKIP if user declines]:** Generate from `references/linkedin-fields.md`. Map every LinkedIn form field. Achievement-based descriptions, not "Responsibilities:" style. Verify all metrics match CV.
4. **Reference file:** Generate private career reference with all excluded details, attribution mapping, metric proofs, gap explanations.

**Gate:** PDF renders single page. GitHub Pages live. LinkedIn guide metrics match CV.

## Quality Gates

- Every metric cites its calculation proof (input, output, multiplier)
- Every achievement is attributed to a verified role
- Zero non-ASCII characters in final HTML output
- Summary metric differs from experience bullet metrics (abstract vs specific)
- Print CSS produces single A4 page
- All dates match between CV, LinkedIn guide, and reference file
- All company descriptors appear only on first mention
- All non-technical roles have at least 1 bullet showing transferable impact
- Experience timeframe claims match first professional role date

## Error Recovery

| Situation | Action |
|-----------|--------|
| User unsure which role an achievement belongs to | Mark as "unverified", ask again with context. Do not guess. |
| Metric math doesn't check out | Show the calculation, ask user for correct numbers |
| Print overflows 1 page | Reduce print CSS spacing incrementally. If still overflows, inform user: "Content requires 2 pages. Expand to fill page 2 meaningfully or cut a role." |
| GitHub Pages creation fails | Provide manual instructions |
| Non-ASCII found in final scan | Replace automatically, show what was replaced |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| User has 15+ roles | Combine older/shorter roles. Keep detailed bullets only for recent 5-7 roles. |
| Career changer (non-tech to tech) | Lead with tech experience. Older non-tech roles: 1 line each, no bullets. |
| Family business | Anonymize with generic descriptor (e.g., "Consulting Firm"). Never say "family business" on CV. |
| Concurrent roles (2x "Present") | Acceptable. Use "Part-time" for secondary role to explain overlap. |
| Resignation and rehire at same company | Split into separate entries with real dates. Do not merge to hide gap. |
| User claims experience from hobby/student era | Challenge: "What professional work did you do in that period?" If no paid role, use "for over a decade" or count from first professional role. |
| GPA below 3.5/4 | Omit from CV and LinkedIn. Do not display. |
| Unfinished course with "Present" | Remove. "Present" on incomplete education signals abandonment. |
| 3+ orphan lines on page 2 | Either compress content or expand to fill half of page 2 meaningfully. Never leave 3 orphan lines. |
