# Rules: CV Audit

## ATS-CHAR [CRITICAL] ATS-Unsafe Characters

All HTML output must contain zero non-ASCII characters.
- **Detect:** Search for `&mdash;`, `&ndash;`, `&rarr;`, or any character with code point > 127
- **Fix:** Replace with ASCII equivalents: `&mdash;`/`&ndash;` -> `-`, `&rarr;` -> `to`, unicode box-drawing -> `=`
- **Impact:** ATS parsers corrupt or drop non-ASCII content. PDF titles display garbled characters.
- **Source:** ATS compatibility testing. PDF title corruption observed with em dash.

Also applies to: `<title>` tag, `<meta>` content attributes, HTML comments, CSS comments.
Only `&amp;` is safe (standard HTML encoding).

## ATS-STRUCT [HIGH] ATS Structure Requirements

Single-column layout with standard section headings.
- **Detect:** Multi-column CSS (float, column-count), non-standard headings, images/SVG in content
- **Fix:** Single column, standard headings (Professional Summary, Technical Skills, Experience, Education)
- **Impact:** Multi-column causes ATS to read content out of order. Non-standard headings are not mapped.
- **Source:** Resume parsing best practices 2026

## METRIC-MATH [CRITICAL] Metric Verification

Every quantified claim must be mathematically correct.
- **Detect:** Cross-check: if "128h to 8h" then multiplier = 128/8 = 16x, not 9x
- **Fix:** Recalculate. Confirm with user. Use the correct multiplier.
- **Impact:** Recruiter or interviewer checks math. Wrong math = credibility loss.
- **Source:** Common CV error: users copy metrics without verifying math

## METRIC-DEDUP [HIGH] Summary-Experience Metric Separation

Same metric must not appear identically in both summary and experience.
- **Detect:** Identical numbers in summary paragraph and experience bullet
- **Fix:** Summary: abstract version ("up to 700x speedups"). Experience: specific ("from 21h to 2min")
- **Impact:** Copy-paste appearance. Recruiter reads both sections sequentially.
- **Source:** CV best practice: summary hooks, experience details

## ROLE-ATTRIB [CRITICAL] Achievement-Role Attribution

Achievements must be attributed to the role where they actually happened.
- **Detect:** Ask user "Which role did you do X in?" for every achievement
- **Fix:** Move bullet to correct role entry
- **Impact:** Misattribution is discoverable in interview ("Tell me about your Head of Optimization work")
- **Source:** Common misattribution when users hold multiple roles at same company

## DATE-HONEST [HIGH] Date Honesty

Combined role entries must use real departure dates.
- **Detect:** Combined entry date range covers a resignation gap
- **Fix:** If user resigned and returned, split into separate entries. End date = actual departure.
- **Impact:** Discoverable in background check
- **Source:** Common issue with combined role entries hiding resignation gaps

## EXP-YEARS [HIGH] Experience Timeframe Claims

"since YYYY" must reference a professional role, not hobby/student era.
- **Detect:** Check if claimed start year has a paid/professional role
- **Fix:** If no professional role in YYYY, use "for over a decade" or count from first professional role
- **Impact:** Recruiter checks timeline: if first role is 2014 but CV says "since 2008", credibility gap
- **Source:** Common inflation when users count from hobby/student era

## VERIFY-CLAIM [HIGH] Unverifiable Specific Claims

Specific numbers must be publicly verifiable or removed.
- **Detect:** "20+ repositories", "served 10K users" - can a recruiter check this?
- **Fix:** Remove specific number. Use qualitative: "multiple repositories"
- **Impact:** Recruiter visits GitHub, counts 5 public repos. Trust broken.
- **Source:** Common issue: users claim repo counts that include private repos

## SKILL-FILLER [MEDIUM] Skill Section Filler

No commoditized, redundant, or assumed skills.
- **Detect:** "Prompt Engineering" (commoditized), "GitHub Actions" + "CI/CD" (redundant), "Git" (assumed), "Agile" (generic)
- **Fix:** Remove filler. Only skills defensible in 30-min deep-dive interview.
- **Impact:** Too many skills = "knows nothing deeply". Filler = padding.
- **Source:** CV best practice

## JARGON [HIGH] Corporate Jargon Without Substance

Generic phrases that say nothing.
- **Detect:** "Led cross-functional optimization initiatives", "Drove strategic alignment", "Spearheaded transformative change"
- **Fix:** Replace with specific achievement + metric
- **Impact:** Recruiter skips jargon. Zero information content.
- **Source:** Common CV filler that conveys zero information

## SPECULATION [MEDIUM] Speculative Claims

No unverifiable present-tense claims about past work.
- **Detect:** "tools likely still in active use today", "probably saved millions"
- **Fix:** Remove. State only what you know.
- **Impact:** Unprofessional. Interviewer may ask "How do you know?"
- **Source:** Common CV pattern: users speculate about current impact of past work

## PRIVACY-EMAIL [HIGH] Email in Public HTML

No raw email address in publicly hosted HTML.
- **Detect:** `mailto:` link or email text in HTML body
- **Fix:** Remove. Keep email only in private PDF version.
- **Impact:** Spam bots harvest emails from public HTML
- **Source:** Privacy best practice

## PRIVACY-FAMILY [HIGH] Family Business Real Name

Family businesses should use generic descriptors.
- **Detect:** Real company name for a family business in public CV
- **Fix:** Use generic descriptor: "Consulting Firm", "Retail Company", etc.
- **Impact:** Unnecessary personal information disclosure
- **Source:** Privacy best practice for family-owned businesses

## PRINT-FIT [HIGH] Single Page A4 Fit

Content must fit single A4 page when printed.
- **Detect:** Print preview shows content on 2nd page
- **Fix:** Reduce print CSS spacing. If still overflows, evaluate: cut weakest role or expand to fill page 2 meaningfully.
- **Impact:** 2-page CV with 3 orphan lines on page 2 looks unprofessional
- **Source:** Common issue when CV content grows beyond single page

## LEADERSHIP [MEDIUM] Leadership Narrative Missing

Management/leadership roles should show scope, not just IC work.
- **Detect:** "Head of..." or "Director" role with only "Built X" bullets
- **Fix:** Add ownership/scope bullet: "Owned end-to-end...", "Established...", "Founded..."
- **Impact:** Appears as IC when role was leadership. Undervalues the position.
- **Source:** Common issue with management roles described using only IC verbs

## GPA-THRESH [LOW] GPA Below Threshold

GPA below 3.5/4 should be omitted.
- **Detect:** GPA displayed that is < 3.5/4 or equivalent
- **Fix:** Remove GPA field. No one asks about GPA with 10+ years experience.
- **Impact:** Low GPA draws negative attention. Omission draws zero attention.
- **Source:** GPA only helps new graduates; experienced professionals gain nothing

## CERT-INCOMPLETE [MEDIUM] Unfinished Course/Certification

Courses with "Present" end date that are abandoned.
- **Detect:** Education entry with "Present" and user confirms abandoned/inactive
- **Fix:** Remove entirely. "Present" on unfinished education = "started and quit" signal.
- **Impact:** Recruiter sees: started but never finished. Negative signal.
- **Source:** Common issue: users forget to remove or update abandoned courses

---

## Sources

- ATS compatibility rules derived from testing with Workday, Greenhouse, Lever, and iCIMS parsers (2025-2026)
- [Jobscan — ATS Resume Formatting Guide](https://www.jobscan.co/blog/ats-resume-formatting/)
- [Harvard Business Review — Resume Best Practices](https://hbr.org/topic/subject/resumes)
- Metric verification and privacy rules based on production CV generation experience
- Resume parsing best practices verified against 2026 ATS behavior
