# Rules: LinkedIn Profile Fields

Complete field reference for LinkedIn profile editing. Verified March 2026.

## PROFILE-CORE [INFO] Core Profile Fields

| Field | Limit | Notes |
|-------|-------|-------|
| First Name | 50 chars | Required |
| Last Name | 50 chars | Required |
| Pronouns | Dropdown | Optional: she/her, he/him, they/them, custom |
| Profile Photo | 400x400px, 8MB | JPG/PNG/GIF |
| Banner | 1584x396px, 8MB | 4:1 aspect ratio |
| Headline | 220 chars | Auto-populates from job but fully editable |
| Location | City/Country | Affects search visibility |
| Industry | Dropdown | e.g., "Software Development" |
| About | 2,600 chars | Supports bold, links, line breaks |
| Custom URL | 100 chars | linkedin.com/in/{custom} - max 5 changes per 6 months |

## EXP-FIELDS [INFO] Experience Form Fields

Each role has these editable fields:

| Field | Type | Notes |
|-------|------|-------|
| Title* | Text (100 chars) | Job title |
| Employment type | Dropdown | Full-time, Part-time, Self-employed, Contract, Freelance, Temporary, Internship, Apprenticeship, Seasonal |
| Company or organization* | Text (auto-linked) | Links to company page if exists |
| Start date | Month/Year picker | Required |
| End date | Month/Year or Present | "Currently working here" toggle |
| Location | Text | City, Country |
| Location type | Dropdown | Remote, On-site, Hybrid |
| Description | 2,000 chars | Rich text (bold, links, bullets) |
| Profile headline | Text | Usually keep main headline - changes profile-wide |
| Skills | Multi-select | Tag skills to this role from your skills list |
| Media | Upload | Images, docs, video links |

Same-company roles: LinkedIn auto-groups under one company header with total duration.

**Date overlap fix:** LinkedIn counts both start and end months inclusively. Role A ends March + Role B starts March → LinkedIn double-counts March. Fix: set Role A end date one month earlier (February).

## EDU-FIELDS [INFO] Education Form Fields

| Field | Type | Notes |
|-------|------|-------|
| School* | Text (auto-linked) | Links to school page |
| Degree | Dropdown | Bachelor's, Master's, MBA, BBA, Ph.D., etc. |
| Field of Study | Text/Dropdown | e.g., "Information Security Engineering" |
| Start date | Month/Year | Optional - omit if program duration unusual |
| End date | Month/Year | Graduation date |
| Grade | Text | Optional - omit if below 3.5/4 |
| Activities and societies | 500 chars | Clubs, thesis, projects |
| Description | 1,000 chars | Optional |
| Skills | Multi-select | Tag relevant skills |
| Media | Upload | Transcripts, certificates |

## CERT-FIELDS [INFO] Licenses & Certifications

| Field | Type | Notes |
|-------|------|-------|
| Name* | Text | Certification title |
| Issuing Organization* | Text | e.g., "Scrum Alliance" |
| Issue Date | Month/Year | When earned |
| Expiration Date | Month/Year | Optional - "Does not expire" toggle |
| Credential ID | Text | Optional |
| Credential URL | URL | Optional verification link |

## SKILLS-FIELDS [INFO] Skills Section

| Setting | Value |
|---------|-------|
| Maximum skills | 100 |
| Top skills (visible without "Show all") | 3 |
| Endorsements | Can enable/disable per skill |
| Reorder | Drag to reorder by importance |

Recruiter-visible: top 5 skills appear in search results and profile card.

## FEATURED-FIELDS [INFO] Featured Section

| Field | Notes |
|-------|-------|
| Item types | Posts, articles, links, media, documents |
| Title | Custom label for each item |
| Description | Short text description |
| Reorder | Drag to arrange |
| Thumbnail | Auto-generated from OG image, or manual upload |

## LANG-FIELDS [INFO] Languages Section

Proficiency levels (dropdown):
1. Elementary
2. Limited Working
3. Professional Working
4. Full Professional
5. Native or Bilingual

## CONTACT-FIELDS [INFO] Contact Info

| Field | Visibility Options |
|-------|-------------------|
| Email | Public / Connections only |
| Phone | Public / Connections only |
| Website (up to 3) | Public |
| Twitter/X | Public |
| Birthday | Connections only / Hidden |

## OTW-FIELDS [INFO] Open to Work Settings

| Setting | Options |
|---------|---------|
| Visibility | All LinkedIn members / Recruiters only |
| Job titles | Text (multiple) |
| Employment type | Full-time, Part-time, Contract, Freelance, Temporary, Internship |
| Seniority | Entry, Associate, Mid-Senior, Director, Executive |
| Work arrangement | Remote, On-site, Hybrid |
| Location preferences | Multiple locations |
| Start date | Immediately / Custom date |
| Salary expectations | Range (optional, recruiter-visible) |

## VISIBILITY [INFO] Profile Visibility Settings

| Setting | Options | Recommended |
|---------|---------|-------------|
| Public profile | On/Off | ON (search engines index) |
| Profile viewing | Public/Semi-anonymous/Anonymous | Public (networking) |
| Share updates | On/Off | ON (new role notifications) |
| Discover by email | On/Off | ON (recruiter discovery) |
| Discover by phone | On/Off | OFF |
| Follower settings | Everyone/Connections | Everyone |
| Active status | On/Off | Personal preference |

## OPTIONAL-SECTIONS [INFO] Additional Sections

Available but not required:

| Section | Fields | When to use |
|---------|--------|-------------|
| Volunteer | Org, role, cause, dates, description | If relevant to target role |
| Publications | Title, publisher, date, URL, co-authors | Academic/research roles |
| Patents | Title, office, number, dates, co-inventors | Engineering/R&D roles |
| Honors & Awards | Title, issuer, date, description | Notable industry awards |
| Test Scores | Test name, score, date | Professional standardized tests only |
| Languages | Language + proficiency | Always if multilingual |
| Organizations | Org name, role, dates | Professional associations |
| Courses | Course name, institution, date | Only if completed and relevant |
| Projects | Title, description, dates, URL, team | Alternative to Featured |
| Services | Title, description, categories, pricing | Freelancers only |

## CV-LINKEDIN-DIFF [INFO] Key Differences

| Aspect | CV | LinkedIn |
|--------|----|---------|
| Roles at same company | Combine to 2-3 entries | Keep each separate (auto-groups) |
| Detail level | 1-3 bullets per role | Can be longer (2,000 chars) |
| Skills format | Category + pill tags | Flat list, endorsable |
| Non-technical roles | Minimal or omit | Can include (less space pressure) |
| Photo | Never include | Essential |
| Email | Omit from public HTML | Include (connections-only visibility) |
| Company descriptor | First mention only | Not needed (company page links) |
| "Responsibilities:" style | Never | Replace with achievement bullets |

---

## Sources

- [LinkedIn Help — Edit Your Profile](https://www.linkedin.com/help/linkedin/answer/a543685)
- [LinkedIn Help — Profile Character Limits](https://www.linkedin.com/help/linkedin/answer/a542091)
- [LinkedIn Help — Open to Work Preferences](https://www.linkedin.com/help/linkedin/answer/a507508)
- [LinkedIn Help — Custom URL](https://www.linkedin.com/help/linkedin/answer/a542685)
- [LinkedIn Help — Featured Section](https://www.linkedin.com/help/linkedin/answer/a704787)
- Field limits verified against LinkedIn UI, March 2026
