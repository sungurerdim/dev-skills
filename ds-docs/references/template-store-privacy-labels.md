# Store Privacy Labels — Declaration Template

Template for completing Apple App Store Privacy Nutrition Labels and Google Play Data Safety Section. Replace `{APP_NAME}`, `{SUPPORT_EMAIL}`, and data types with your app's specifics.

---

## Apple App Store — Privacy Nutrition Labels

App Store Connect > App Privacy > Data Collection

### Data Types Declaration Template

| Data Type | Sub-type | Collected | Linked to Identity | Used for Tracking | Purpose |
|-----------|----------|-----------|-------------------|-------------------|---------|
| Contact Info | Email Address | {Yes/No} | {Yes/No} | No | {Purpose} |
| Contact Info | Name | {Yes/No} | {Yes/No} | No | {Purpose} |
| Identifiers | User ID | {Yes/No} | {Yes/No} | No | {Purpose} |
| Purchases | Purchase History | {Yes/No} | {Yes/No} | No | {Purpose} |
| Diagnostics | Crash Data | {Yes/No} | No | No | App Functionality |
| Diagnostics | Performance Data | {Yes/No} | No | No | App Functionality |
| User Content | {Content Type} | {Yes/No} | {Yes/No} | No | {Purpose} |

### Common "Not Collected" Categories

Explicitly select "No" for categories your app does not collect:

- Health & Fitness (all sub-types)
- Financial Info (credit card, bank account, etc.)
- Location (precise or coarse)
- Sensitive Info
- Contacts
- Browsing History
- Search History
- Photos or Videos
- Gameplay Content
- Body (motion, skin data, etc.)
- Environment Scanning

### Key Declaration Guidelines

**Email/Name (via OIDC):**
- Source: OIDC provider (Google/Apple Sign-In)
- Linked to identity: Yes (used to identify the user's account)
- NOT used for tracking across apps/websites
- NOT shared with third parties

**Diagnostics (Crash Reporting):**
- Collected: Yes (via crash reporting service)
- Linked to identity: No (PII redacted before transmission)
- NOT used for tracking
- Third-party sharing: Crash reporting service is data processor, not controller

**Purchase History (IAP):**
- Collected: Yes (IAP receipts for balance/subscription verification)
- Linked to identity: Yes (purchases are per-user)
- NOT used for tracking
- NOT shared with third parties beyond Apple/Google payment processing

### Privacy Nutrition Label Summary Template

```
Data Used to Track You:       None
Data Linked to You:           {list linked data types}
Data Not Linked to You:       {list unlinked data types}
```

---

## Google Play — Data Safety Section

Play Console > App content > Data safety

### Data Collected or Shared Template

| Data type | Collected | Shared | Ephemeral | Required | Purpose |
|-----------|-----------|--------|-----------|----------|---------|
| Personal info > Email address | {Yes/No} | No | No | {Yes/No} | Account management |
| Personal info > Name | {Yes/No} | No | No | {Yes/No} | Account management |
| Financial info > Purchase history | {Yes/No} | No | No | {Yes/No} | App functionality |
| App info and performance > Crash logs | {Yes/No} | No | Yes | No | Analytics |
| App info and performance > Diagnostics | {Yes/No} | No | Yes | No | Analytics |
| Device or other IDs | {Yes/No} | No | - | - | - |
| Location | No | No | - | - | - |

### Security Section

| Question | Answer |
|----------|--------|
| Is data encrypted in transit? | {Yes/No} |
| Can users request data deletion? | {Yes/No} |
| App follows Google Play Families Policy? | {N/A or Yes} |
| Independent security review? | {Yes/No} |

### Ephemeral Data Guidelines

Mark data as **ephemeral** when:
- Data is processed in server RAM and deleted immediately
- Data is not written to persistent storage
- This accurately reflects zero-retention processing

### "Data Deletion" Declaration

If users can request data deletion:
- **Answer: Yes**
- **Mechanism:** {describe in-app deletion mechanism}
- **What happens:**
  1. All local data permanently erased
  2. Server-side session/data invalidated
  3. Pseudonymous records retained for legal/financial compliance (no PII)
- **Contact:** {SUPPORT_EMAIL}

---

## Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|-----------------|
| Declaring ephemeral data as "not collected" | Data IS collected if uploaded. Mark as collected but ephemeral (Google) or not linked to identity (Apple). |
| Omitting crash reporting data | Crash data IS collected even if PII is redacted. Declare it as diagnostics. |
| Marking OIDC email as "shared with third parties" | OIDC providers provide data TO you. You don't share outward. Not shared. |
| Forgetting purchase history | IAP receipts are collected for verification. Declare under financial/purchase data. |
| Claiming "no data collected" | If any data leaves the device, it's collected. Honest declaration builds trust. |

---

## Filing Checklist

### Apple App Store Connect
- [ ] Navigate to App Privacy section
- [ ] Select each data type from your declaration table
- [ ] For each: specify collection purpose, linking, and tracking status
- [ ] Review the generated Privacy Nutrition Label preview
- [ ] Ensure Privacy Policy URL is set and accessible

### Google Play Console
- [ ] Navigate to App content > Data safety
- [ ] Complete the questionnaire using your declaration table
- [ ] Mark ephemeral data appropriately
- [ ] Enable "users can request data deletion" if applicable
- [ ] Provide deletion request URL/email
- [ ] Review the generated Data Safety summary
- [ ] Ensure Privacy Policy URL is set and accessible

---

*Template — customize for your specific app's data practices.*
