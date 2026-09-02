# Rules: Code Signing

Applies to mobile and desktop projects only — skip for web/API/CLI/library. Loaded for the `signing` scope.

| Section | Rules |
|---------|-------|
| **Code Signing** | DOP-08–09 (2 HIGH) |

## Code Signing

### DOP-08 [HIGH] Code Signing Automation
No manual signing. Signing must be automated in CI.
- **Detect:** Manual cert install. Certs on individual machines. Signing breaks on CI.
  - iOS: no Fastlane Match or equivalent. Manual provisioning profiles.
  - Android: keystore on developer machine, not in CI secrets.
- **Fix:**
  - iOS: Fastlane Match (git or cloud). Gemfile.lock committed.
  - Android: base64 keystore in CI secrets. `keystore.properties` in `.gitignore`.
- **Impact:** Manual signing blocks releases and creates single-point-of-failure
- **Note:** Applies to mobile and desktop projects only. Skip for web/API/CLI/library.
- **Source:** Apple Code Signing Guide, Android App Signing docs, Fastlane Match docs

### DOP-09 [HIGH] Signing Security
Signing credentials must not be in source code.
- **Detect:**
  - Keystore file committed to git
  - Signing passwords/keys in plain text config files
  - CI secrets referenced but not rotated
- **Fix:** Store signing credentials in CI secret manager. Reference via environment variables. Document rotation policy.
- **Impact:** Compromised signing credentials allow malicious distribution
- **Note:** Applies to mobile and desktop projects only.
- **Source:** OWASP Mobile Security
