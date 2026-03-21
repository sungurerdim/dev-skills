# Store Submission Guide

Step-by-step guide for testing, review, and launch on Apple App Store and Google Play Store.

---

## Phase 1 — Local Testing (Before Store Account)

| Step | iOS | Android |
|------|-----|---------|
| Run on physical device | Build + USB | Build + USB |
| OIDC testing | Google Sign-In works (OAuth client ID required) | Same |
| Apple Sign-In | Real Apple ID with dev provisioning | N/A |
| Backend | Real server or local Docker Compose | Same |
| IAP | Does not work (sandbox required) | Does not work (license testing required) |

At this stage, everything except IAP can be tested: auth, core features, data export, account deletion.

---

## Phase 2 — Sandbox / Internal Testing

### Apple (TestFlight)

1. Apple Developer Program ($99/year) membership
2. Create app in App Store Connect (Bundle ID, description, screenshots)
3. Xcode Archive → Upload to App Store Connect
4. Create "Internal Testing" group in TestFlight
   - Up to 100 internal testers (added to Apple Developer account)
   - **Add your own account to test solo — no other testers needed**
   - No review required, available immediately after upload
5. "External Testing" group (optional, later stage)
   - Up to 10,000 external testers
   - First build requires short Beta App Review (~24-48 hours)
   - Invite via link: testers install TestFlight app
6. Sandbox IAP: Create "Sandbox Tester" accounts in App Store Connect
   - No real money spent
   - Full purchase flow tested

### Google Play (Internal Testing)

1. Google Play Developer account ($25 one-time fee)
2. Create app in Play Console
3. Upload AAB (Android App Bundle)
4. "Internal testing" track
   - Up to 100 testers (email list)
   - **Add your own Gmail to test solo**
   - No review required, instant access
   - Real Play Store install experience
5. "Closed testing" track (optional, later stage)
   - More testers, via Google Groups
   - May have short review process
6. License Testing: Play Console → Settings → License Testing
   - Add test account emails
   - IAP purchases are free
   - Auto-cancel after 3 minutes

### Solo Developer Test Flow

```
Open developer account
       ↓
Upload build (Internal Testing)
       ↓
Install on your device (TestFlight / Play Store internal link)
       ↓
Full test: OIDC + Sandbox IAP + core features
       ↓
Bugs found? → Yes → Fix, upload new build, retest
       ↓
No
       ↓
Submit for review
```

---

## Phase 3 — Pre-Launch Checklist

Complete before submitting for review on either platform:

- [ ] Auth flow tested on real device (all providers)
- [ ] Sandbox IAP purchase flow tested
- [ ] Core feature end-to-end test (real server)
- [ ] Data export functionality tested
- [ ] Account deletion flow tested
- [ ] Consent screen + age verification tested
- [ ] Offline/queue behavior tested (disconnect → reconnect)
- [ ] Privacy Manifest validation (Xcode → Privacy Report) — iOS only
- [ ] Screenshots prepared (required sizes per platform)
- [ ] App description, keywords, categories set
- [ ] Privacy Policy URL (live, accessible)
- [ ] Support URL
- [ ] Age Rating questionnaire (App Store Connect)
- [ ] Data Safety form (Play Console)

---

## Phase 4 — Submit for Review

| | Apple App Store | Google Play |
|---|---|---|
| Review time | 24-48 hours (usually 24h) | 1-7 days (first app takes longer) |
| Rejection risk | Medium — strict rules | Low — more automated |
| Common rejections | Missing Privacy Policy, non-IAP payment link, crash, incomplete metadata | Policy violation, missing Data Safety declaration |
| After rejection | Fix → resubmit (new review) | Same |
| Demo account | Apple may request test login — not needed if using Sign in with Apple | Rarely requested |

---

## Phase 5 — Release (Launch)

After review approval, two options:

1. **Manually release** — You control when to publish
   (Recommended: controlled launch when everything is ready)

2. **Automatically release** — Publishes as soon as review passes

For first release, "Manually release" recommended:
- After review passes, do final check in TestFlight/Internal
- Verify backend is production-ready
- Click "Release this version"
- Visible in store within ~2-24 hours

---

## Recommended Order (Solo Dev)

```
 1. Open Google Play Developer account ($25)     ← can do immediately
 2. Join Apple Developer Program ($99/year)       ← can do immediately
 3. Deploy backend to production server
 4. Upload AAB to Google Play Internal Testing
 5. Full test on Android device (OIDC + IAP sandbox + core features)
 6. Upload build to TestFlight
 7. Full test on iOS device
 8. Prepare screenshots + metadata
 9. Submit to both stores for review (parallel)
10. Review passes → manual release
```

---

## Post-Launch: Update Process

### Minor Update (Bug fix, UI tweaks)

```
1. Fix code
2. Version bump in project config: 1.0.0+1 → 1.0.1+2
   (build number MUST increase — stores reject same number)
3. Build release artifact
4. Upload to Internal Testing → test on your device
5. Submit for review
6. Approval → Release
```

### Major Update (New feature)

```
1. Develop feature + test
2. Version bump: 1.0.x → 1.1.0+N
3. Upload to Internal Testing → comprehensive testing
4. Optional: Closed/External Testing for beta users
5. Once stable, submit for review
6. Update "What's New" notes (per language)
7. Approval → Release
```

### No OTA Updates for Native Apps

Native mobile apps (Flutter, SwiftUI, Kotlin) require store submission for every update. No instant deploy like web apps. This means:
- Test every build thoroughly
- Have a fast patch process for critical bugs
- Implement a force-update mechanism (minimum version check from server)

### CI/CD (Optional, recommended post-launch)

- Fastlane for automated TestFlight/Play Store upload
- Tag-based release (git tag → CI → store)
- Code signing automation
- GitHub Actions workflow for automated builds

Manual upload is sufficient for launch — automate later.

---

## Staged Rollout Strategy

### Google Play
- Supports percentage-based rollout (1% → 5% → 20% → 50% → 100%)
- Monitor crash-free rate at each stage
- Halt rollout if crash-free rate drops below 99%

### Apple App Store
- Supports phased release (7-day automatic rollout)
- Day 1: 1%, Day 2: 2%, Day 3: 5%, Day 4: 10%, Day 5: 20%, Day 6: 50%, Day 7: 100%
- Can pause or halt at any time

---

*Guide — adapt timelines and specifics to your project's needs.*
