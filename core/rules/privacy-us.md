# Privacy — United States duties

Loaded when the product serves the US (`jurisdiction∋us` or a state token such as `us-ca`); the core rules are [privacy.md](privacy.md). California is the strictest state baseline; most other state laws follow a lighter template — check which states' thresholds the business meets. Dates and thresholds are a seed: re-check the live official text before a finding depends on them.

### PRV-06 [CRITICAL] California opt-out, sensitive data and risk duties missing
applies_when: jurisdiction∋us-ca
- **Detect:** a business meeting the CCPA thresholds with no "Do Not Sell or Share My Personal Information" (or "Your Privacy Choices") link where data is sold or shared for cross-context ads; Global Privacy Control ignored or honoured without visible confirmation; sensitive personal information (including precise location and neural data) used beyond permitted purposes with no "Limit the Use" option; automated decision-making used for significant decisions with no notice and opt-out; risk-triggering processing (selling or sharing, sensitive data, such decisions) with no risk assessment on file.
- **Mech:** T `git grep -nIiE 'do.?not.?sell|doNotSell|opt.?out|globalPrivacyControl|Sec-GPC|ccpa|cpra|limit.?the.?use' -- ':!*.md'`
- **Fix:** opt-out link and flow, GPC read as an opt-out with a visible confirmation, a limit option for sensitive data, notice and opt-out for automated decisions, documented risk assessments with a review cadence; answer requests within 45 days.
- **Impact:** ignoring GPC and opt-outs is an active enforcement priority of the California regulator and attorney general.
- **Source:** Cal. Civ. Code §1798.100 et seq. (CCPA as amended by CPRA), §1798.135; 11 CCR §7025 (opt-out preference signals); CPPA regulations (cppa.ca.gov).

### PRV-22 [CRITICAL] Children's or age-restricted use without US safeguards
applies_when: audience=public
- **Detect:** a child-directed or mixed-audience service collecting personal information from under-13 users with no verifiable parental consent; third-party disclosure (ads, analytics SDKs) without its own separate parental consent; biometric identifiers or government IDs from children; no written security program or retention limit for children's data; age-restricted content served in a state with an age-verification statute on self-declared age only.
- **Mech:** T `git grep -nIiE 'coppa|parental.?consent|age.?gate|date.?of.?birth|is_?minor|age_?verif' -- ':!*.md'`
- **Fix:** route under-13 users to a verifiable parental consent flow with separate consent for third-party disclosure; treat biometrics and IDs as personal information; write the security program and retention limit; verify age by a method the applicable statute accepts. App-store age signals are STO-07.
- **Impact:** collecting from children without parental consent is an active FTC enforcement target with multimillion-dollar settlements.
- **Source:** 16 CFR Part 312 (COPPA Rule; amendments effective 23 June 2025, compliance required from 22 April 2026); *Free Speech Coalition v. Paxton*, 606 U.S. (2025).

### PRV-14 [CRITICAL] Health information handled outside HIPAA safeguards
applies_when: pii=yes
- **Detect:** a covered entity or business associate handling protected health information without encryption in transit and at rest, without access logs per PHI access, sharing PHI with vendors without a business associate agreement, accessing whole records where a subset is needed, or with no documented backup and contingency plan; a health app outside HIPAA sharing health data with advertisers without authorization.
- **Mech:** T `git grep -nIiE 'hipaa|phi|patient|diagnos|medical_?record|icd-?10|baa' -- ':!*.md' ':!*lock*'`
- **Fix:** encrypt PHI, log every access (SAR-01), sign a business associate agreement with every vendor touching PHI, apply the minimum-necessary standard, keep a contingency plan and an annual risk analysis; non-HIPAA health apps get explicit authorization before sharing.
- **Impact:** each gap is independently reportable and enforced by HHS OCR; health-data sharing by non-covered apps is enforced by the FTC.
- **Source:** 45 CFR Part 164 (HIPAA Security and Privacy Rules); HITECH Act 2009; FTC Health Breach Notification Rule.
