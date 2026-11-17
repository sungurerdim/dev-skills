# Privacy — EU and UK duties

Loaded when the product serves the EU or the UK (`jurisdiction∋eu` or `jurisdiction∋uk`); the core rules are [privacy.md](privacy.md). Consent and cookies (ePrivacy Art. 5(3)) are PRV-01, breach deadlines the [breach-notification](../templates/breach-notification.md) template. Dates and thresholds below are a seed: re-check the live official text before a finding depends on them.

### PRV-52 [HIGH] No record of processing activities
applies_when: pii=yes
- **Detect:** no written inventory of processing activities (purposes, data and subject categories, recipients including third countries, transfer safeguards, retention, security measures); an inventory not updated when a feature adds processing; compliance records (DPIAs, consent logs, breach register, request log) with no retention period.
- **Mech:** T `git ls-files | grep -iE 'ropa|records?.?of.?processing|processing.?activity|processing.?activities|data.?inventory|data.?map'`
- **Fix:** one record per GDPR Art. 30, updated in the change that adds or alters processing; give each compliance-record type its own retention (PRV-27).
- **Impact:** it is the first document a regulator asks for, and its absence shows nobody knows what data is processed.
- **Source:** GDPR Art. 30 (the under-250-employee exemption does not cover regular or sensitive processing).

### PRV-58 [CRITICAL] Special-category data on the wrong legal basis
applies_when: pii=yes
- **Detect:** health, biometric, genetic, ethnic, religious, sexual-life, political or trade-union data processed on legitimate interest or contract alone; no per-activity record separating the Art. 6 basis from the Art. 9(2) condition.
- **Mech:** M (the processing record against the special-category fields PRV-31 lists)
- **Fix:** name the Art. 9(2) condition for every activity touching such data (explicit consent unless a narrower condition applies) and record it beside the Art. 6 basis.
- **Impact:** legitimate interest cannot cover special-category data, and the gap is visible from the records alone.
- **Source:** GDPR Art. 6, 9.

### PRV-15 [CRITICAL] Processor without a contract or a registry entry
applies_when: pii=yes
- **Detect:** SDKs or services receiving personal data (hosting, email, analytics, crash reporting, AI APIs, support tools, payment) with no data processing agreement on file or not listed in a processor registry; an agreement missing the Art. 28(3) terms; sub-processor changes unnoticed.
- **Mech:** T `git ls-files | grep -iE 'processor|sub-?processor|vendor|dpa'` · `git grep -nIiE 'sentry|datadog|mixpanel|amplitude|segment|posthog|sendgrid|mailgun|postmark|twilio|intercom|zendesk|openai|anthropic|stripe' -- '*.json' '*.toml' '*.txt' '*.gradle*' '*.yaml' '*.yml' '*.mod'`
- **Fix:** an agreement with every processor and an entry per the [processor-registry](../templates/processor-registry.md) template (entity, location, data, basis, transfer mechanism, retention, agreement status); review it when dependencies change.
- **Impact:** a processor's mishandling becomes the controller's violation with no proof of due diligence.
- **Source:** GDPR Art. 28.

### PRV-53 [HIGH] Data leaves the EU or UK without a transfer mechanism
applies_when: pii=yes
- **Detect:** processors or hosting in third countries with no recorded mechanism (adequacy decision, standard contractual clauses, binding corporate rules, Art. 49 derogation); reliance on the EU-US Data Privacy Framework without checking the recipient's current certification; no transfer impact assessment where there is no adequacy; US-hosted analytics for EU users with neither.
- **Mech:** M (processor registry and hosting regions)
- **Fix:** record the mechanism per recipient; verify DPF certification on the official list; keep the 2021 standard contractual clauses as a fallback; assess transfers without adequacy and document supplementary measures; prefer EU-region processing where offered.
- **Impact:** a transfer without a mechanism is unlawful from the first byte, and EU authorities have ruled exactly this for US-hosted analytics.
- **Source:** GDPR Chapter V (Art. 44–49); EDPB Recommendations 01/2020 (supplementary measures); the official Data Privacy Framework participant list.

### PRV-16 [CRITICAL] High-risk processing without an impact assessment
applies_when: pii=yes
- **Detect:** large-scale special-category data, systematic monitoring, profiling with legal or similar effects, children's data at scale, new technology such as AI on personal data, or matching datasets — with no DPIA on file, or one older than the processing it describes.
- **Mech:** T `git ls-files | grep -iE 'dpia|impact.?assessment|pia\.md'`
- **Fix:** write it from the [dpia](../templates/dpia.md) template before the processing starts; consult the authority when high residual risk remains (Art. 36); review it when the processing changes.
- **Impact:** skipping the assessment is a violation on its own, apart from any harm it would have caught.
- **Source:** GDPR Art. 35–36; EDPB-endorsed guidelines on DPIA.

### PRV-09 [HIGH] UK-specific duties missing
applies_when: jurisdiction∋uk
- **Detect:** no data protection fee paid to the ICO; no UK representative for a controller outside the UK serving UK users; a service likely to be used by children without the Age Appropriate Design Code standards (PRV-48); privacy notice and complaint handling not updated for the Data (Use and Access) Act 2025 (complaints to the controller first, recognised legitimate interests, changed transfer test).
- **Mech:** M
- **Fix:** pay the fee, appoint a representative where required, apply the Children's Code, and update the notice and complaint process for the 2025 Act.
- **Impact:** the regulator cannot reach the controller, and the fee and representative duties are fined independently of any breach.
- **Source:** UK GDPR Art. 27; Data (Use and Access) Act 2025; ICO guidance (data protection fee, Children's Code).

### PRV-48 [CRITICAL] Children reach the service with adult defaults
applies_when: audience=public
- **Detect:** a service likely to be used by children with no age assurance proportionate to the risk; adult defaults (public profiles, geolocation on, nudges toward sharing, profiling for ads); the GDPR Art. 8 consent age hard-coded to one value where member states set 13 to 16.
- **Mech:** T `git grep -nIiE 'age.?gate|date.?of.?birth|birth_?date|dob|is_?minor|age_?verif|parental' -- ':!*.md'`
- **Fix:** high-privacy defaults and no nudges for users who may be children; age assurance proportionate to the content's risk; the Art. 8 threshold per member state; parental consent below it.
- **Impact:** children's data processed on adult terms is an enforcement priority in both the EU and the UK.
- **Source:** GDPR Art. 8; ICO Age Appropriate Design Code; Regulation (EU) 2022/2065 Art. 28.

### PRV-21 [HIGH] AI features without AI Act duties
applies_when: jurisdiction∋eu
- **Detect:** users interacting with an AI system without being told; synthetic image, audio, video or text published without machine-readable marking; a use that falls under the prohibited practices (Art. 5) or the high-risk list (Annex III: employment, education, credit, essential services, biometrics) with no classification recorded; generative features with no control against prohibited output.
- **Mech:** T `git grep -nIiE 'openai|anthropic|gemini|generativeai|mistral|bedrock|vertexai|huggingface|ollama|llama' -- ':!*.md' ':!*lock*'`
- **Fix:** record the system's risk class; disclose AI interaction and mark generated content (Art. 50); stop prohibited uses; for high-risk uses start the conformity work; check the current application dates on the European Commission's AI Act pages, which the Digital Omnibus changed.
- **Impact:** penalties reach €35 million or 7 % of worldwide turnover for prohibited practices.
- **Source:** Regulation (EU) 2024/1689 (AI Act) Art. 5, Art. 50, Annex III; AI Act Service Desk (ai-act-service-desk.ec.europa.eu).

### PRV-23 [HIGH] Cloud service without Data Act switching terms
applies_when: audience=public or api≠none
- **Detect:** a SaaS, PaaS or IaaS offered to EU customers whose contract lacks switching terms (notice of at most two months, migration within 30 days, cost-based switching fees, export of data and exportable assets); no published description of export formats and procedures; data of a connected product not accessible to its user.
- **Mech:** M (terms and export features)
- **Fix:** add the switching clauses, publish the export procedure and formats, and provide a structured machine-readable export (PRV-04).
- **Impact:** the regulation forbids lock-in contracts; switching charges must disappear entirely from 12 January 2027.
- **Source:** Regulation (EU) 2023/2854 (Data Act), applicable since 12 September 2025.

### PRV-24 [HIGH] Product sold in the EU without Cyber Resilience Act readiness
applies_when: jurisdiction∋eu
- **Detect:** a product with digital elements made available commercially in the EU (app, firmware, desktop or library sold or monetized) with no vulnerability-disclosure policy or security contact, no process to report actively exploited vulnerabilities and severe incidents (24-hour early warning, 72-hour notification, final report), no SBOM. Non-commercial open source is out of scope.
- **Mech:** T `git ls-files | grep -iE '(^|/)SECURITY\.md$|security\.txt$|sbom|cyclonedx|spdx'`
- **Fix:** publish a disclosure policy and contact (`SECURITY.md`, `/.well-known/security.txt`), write the reporting runbook for the single reporting platform, generate an SBOM in the build; plan for the full obligations (security by design, conformity, CE marking).
- **Impact:** reporting duties apply since 11 September 2026 to products already on the market; the rest applies from 11 December 2027, with fines up to €15 million or 2.5 % of turnover.
- **Source:** EU Cyber Resilience Act (in force 10 December 2024); digital-strategy.ec.europa.eu/policies/cyber-resilience-act.

### PRV-47 [HIGH] Hosting service without Digital Services Act duties
applies_when: audience=public
- **Detect:** user-generated or third-party content hosted for EU users with no notice-and-action path for illegal content; removals or account restrictions without a statement of reasons; no points of contact for authorities and users; feeds ranked by a recommender with no plain-language parameters in the terms; ads targeted using special-category data or profiling of known minors.
- **Mech:** T `git grep -nIiE 'report.?(content|abuse|post)|flag.?(content|post)|moderation|takedown' -- ':!*.md'`
- **Fix:** a notice form any user can use with timely decisions; a statement of reasons on every restriction; published contacts; recommender parameters disclosed; no such ad targeting.
- **Impact:** fines reach 6 % of worldwide turnover, and notice-and-action is checkable from outside.
- **Source:** Regulation (EU) 2022/2065 (Digital Services Act) Art. 11, 12, 16, 17, 26, 27, 28.
