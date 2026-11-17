# Privacy — Turkey, Brazil, China, Korea, Thailand, Singapore, Quebec

Loaded when the product serves one of these jurisdictions; the core rules are [privacy.md](privacy.md), processor contracts PRV-15, breach deadlines the [breach-notification](../templates/breach-notification.md) template. Dates, thresholds and fines are a seed: re-check the live official text before a finding depends on them.

### PRV-11 [CRITICAL] KVKK registration, explicit consent or transfer regime missing
applies_when: jurisdiction∋tr
- **Detect:** no VERBIS registration where the controller is not exempt; no information notice (aydınlatma metni) separate from the explicit-consent (açık rıza) text; consent bundled into terms; cross-border transfers resting on consent alone instead of the regime of Law 7499 (adequacy decision → appropriate safeguards such as the standard contract, notified to the Board within five business days → occasional-transfer exceptions).
- **Mech:** T `git grep -nIiE 'kvkk|verbis|aydinlatma|aydınlatma|acik.?riza|açık.?rıza' -- ':!*lock*'`
- **Fix:** register in VERBIS or record the exemption; publish a separate information notice; collect explicit consent per purpose where no other condition applies; document the transfer tier for each foreign recipient and notify standard contracts to the Board on time.
- **Impact:** registration, notice, consent and transfer-notification failures are each fined separately.
- **Source:** Law No. 6698 (KVKK) as amended by Law No. 7499 (Art. 9, in force 1 June 2024); transfer regulation, Official Gazette 32598 (10 July 2024); kvkk.gov.tr.

### PRV-07 [CRITICAL] LGPD basis, officer or transfer safeguards missing
applies_when: jurisdiction∋br
- **Detect:** no legal basis recorded per processing activity; no data protection officer (encarregado) named with contact in the notice where required; international transfers without an ANPD-recognized mechanism (standard contractual clauses).
- **Mech:** T `git grep -nIiE 'lgpd|encarregado|anpd' -- ':!*lock*'`
- **Fix:** record the basis per activity, name the officer and publish the contact, use an ANPD-recognized transfer mechanism for foreign recipients.
- **Impact:** gaps are directly enforceable by ANPD the moment a data subject or auditor asks.
- **Source:** Lei nº 13.709/2018 (LGPD); ANPD guidance (gov.br/anpd).

### PRV-08 [CRITICAL] PIPL separate consent or cross-border route missing
applies_when: jurisdiction∋cn
- **Detect:** one consent for several purposes; no separate consent for sensitive data, public disclosure, provision to other handlers or cross-border transfer; data exported without a security assessment, standard contract filing or certification where required.
- **Mech:** T `git grep -nIiE 'pipl|cac|cross.?border' -- ':!*lock*'`
- **Fix:** separate consents for each case the law lists; localize data or complete the applicable export route before transfer.
- **Impact:** China enforces cross-border rules strictly, and bundled consent invalidates the processing.
- **Source:** Personal Information Protection Law of the PRC (2021); Cyberspace Administration of China (CAC) cross-border data rules.

### PRV-12 [CRITICAL] PIPA per-purpose consent missing
applies_when: jurisdiction∋kr
- **Detect:** consent not separated by purpose, required versus optional items, third-party provision and overseas transfer; no privacy officer named.
- **Mech:** T `git grep -nIiE 'pipa|pipc' -- ':!*lock*'`
- **Fix:** separate consent items as the law lists them, a named privacy officer, an impact assessment where processing is large-scale.
- **Impact:** bundled consent is a direct PIPA violation.
- **Source:** Personal Information Protection Act (Republic of Korea, 2011, amended 2023); PIPC guidance.

### PRV-13 [CRITICAL] PDPA consent, officer or breach path missing
applies_when: jurisdiction∋th or jurisdiction∋sg
- **Detect:** no consent or notification of purpose before collection; no data protection officer where required; no process to assess and notify breaches within the statutory window.
- **Mech:** T `git grep -nIiE 'pdpa|pdpc|data.?protection.?officer' -- ':!*lock*'`
- **Fix:** consent and purpose notice before collection, a named officer, a breach process with the deadline in the breach template.
- **Impact:** both regulators fine for missed notification windows independently of the breach.
- **Source:** Thailand Personal Data Protection Act B.E. 2562 (2019); Singapore Personal Data Protection Act 2012.

### PRV-49 [CRITICAL] Quebec Law 25 duties missing
applies_when: jurisdiction∋ca-qc
- **Detect:** no designated person in charge of personal information with published contact; no privacy impact assessment before a new system or a transfer outside Quebec; consent bundled with general terms; no register of confidentiality incidents; automated decisions without notice.
- **Mech:** T `git grep -nIiE 'loi.?25|law.?25|quebec|québec|cai\.gouv' -- ':!*lock*'`
- **Fix:** designate and publish the officer, assess before new projects and transfers, collect specific separate consent, keep the incident register, disclose automated decisions with a review channel.
- **Impact:** penalties reach C$25 million or 4 % of worldwide turnover, and Quebec allows private suits with punitive damages.
- **Source:** Quebec Law 25 (2021) amending the private-sector privacy act; Commission d'accès à l'information du Québec (cai.gouv.qc.ca).
