# Scoring System

100-point dynamic scoring for release readiness assessment.

## Dimensions & Weights

| Dimension | Weight | Domains |
|-----------|--------|---------|
| D1 Security | 22 pts | SEC-01–12 from rules-compliance |
| D2 Privacy & Compliance | 18 pts | PRV-01–05, REL-09–10, REL-12–13 |
| D3 Build Configuration | 18 pts | REL-02, REL-04, REL-07–08, REL-22, REL-26 |
| D4 Performance | 14 pts | REL-07, REL-17 |
| D5 Dependencies | 12 pts | REL-14–16 |
| D6 Localization & Accessibility | 10 pts | REL-19–20, A11Y basics |
| D7 Quality | 6 pts | Test suite, CI/CD, changelog, IAP restore |

## Dynamic N/A Handling

Each sub-check is tagged: `android` | `ios` | `both`.
When platform excludes a sub-check:
- Remove its points from `applicable_max`
- Do not generate findings
- Do not award free points

```
applicable_max  = sum of points for sub-checks that apply to PLATFORM
dimension_score = round((points_earned / applicable_max) × dimension_weight)
```

`applicable_max = 0` for a dimension → exclude, show as N/A.

## Status Thresholds

| Score | Status | Meaning |
|-------|--------|---------|
| ≥ 85 | READY | Ready for store submission |
| 70-84 | REVIEW | Review recommended before submission |
| 50-69 | CAUTION | Significant gaps exist |
| < 50 | BLOCKED | Not ready for submission |

**Additional blockers:**
- Any unconfirmed manual gate → BLOCKED regardless of score
- Any CRITICAL finding → score capped at 40

## Manual Verification Gates

Binary: confirmed or unconfirmed. Not scored. Any unconfirmed → status cannot be READY.

### iOS Gates
| ID | Gate | Auto-confirmable? |
|----|------|-------------------|
| MG01 | App Store Connect metadata (title, subtitle, description, keywords) | No |
| MG02 | Age rating questionnaire completed | No |
| MG03 | Privacy nutrition labels complete | No |
| MG04 | Export compliance answered | No |
| MG05 | Screenshots for all required device sizes | No |
| MG06 | App icon: no alpha channel, correct dimensions | Yes (via icon validation) |
| MG08 | TestFlight: internal test completed, no critical crashes | No |

### Android Gates
| ID | Gate | Auto-confirmable? |
|----|------|-------------------|
| MG09 | Data Safety form complete | No |
| MG10 | IARC content rating completed | No |
| MG11 | App icon: correct dimensions for all densities | Yes (via icon validation) |
| MG12 | Payment profile verified, distribution agreement signed | No |
| MG13 | Internal test track: successful build uploaded and tested | No |

### Both Platforms Gates
| ID | Gate | Trigger Condition |
|----|------|-------------------|
| MG07 | Support URL accessible | Always (auto-confirm via URL fetch) |
| MG14 | Privacy policy URL accessible | Always (auto-confirm via URL fetch) |
| MG15 | Release build tested on physical device | Always |
| MG_DSYM | dSYM/mapping.txt uploaded to crash reporting | If crash reporting detected |
| MG_TOS | Terms of Service URL active and accessible | If auth plugin detected |
| MG_COPPA | COPPA compliance verified | If kids-directed content detected |
| MG_SUB | Subscription terms visible on paywall screen | If IAP detected |
| MG_CANCEL | Cancellation mechanism accessible in-app | If subscription detected |
| MG_SIWA | Privacy-preserving login option offered (Sign in with Apple satisfies it) alongside third-party/social login — Guideline 4.8 "Login Services"; 5 exemptions incl. own-account-system-only | If third-party OAuth detected |
| MG16 | Android developer identity verified (mandatory for installs on certified devices in BR/ID/SG/TH from 30 Sep 2026; global rollout 2027) | Android release |

## Live Policy Fetch

On every release-ready run, fetch live requirements from official sources:

| Constant | Source | Fallback |
|----------|--------|----------|
| android_new_target_sdk | Google Play SDK requirements page | 36 |
| android_update_target_sdk | Google Play SDK requirements page | 35 |
| min_ios_deployment | Apple upcoming requirements page | 13.0 |
| privacy_manifest_required | Apple upcoming requirements page | true |
| latest_flutter | Flutter release notes page | 3.29.0 |
| latest_dart | Flutter release notes page | 3.7.0 |
| min_billing_lib | Play Billing Library release notes | 7 |
| ios_min_build_sdk | Apple upcoming requirements page | Xcode 26 / iOS 26 SDK (mandatory since 2026-04-28) |

Fetch failure: use fallback value, warn in report.

Fallback basis (2026-07): Play deadline Aug 31, 2026 — new apps and updates target Android 16 (API 36), existing apps API 35; extension available to Nov 1, 2026. Apple: builds must use Xcode 26 / iOS 26 SDK since Apr 28, 2026 (build SDK, not deployment target). 16 KB page-size support required for native code since Nov 1, 2025 (REL-22). Framework fallbacks (latest_flutter/latest_dart) are last-update snapshots — always prefer the live fetch; on fetch failure warn that the snapshot may lag.

## Store Launch Kit

Generated when status is REVIEW or READY. Contains:
- App Store Connect metadata template
- Play Console store listing template
- App Review Notes template with demo account placeholders
- Data Safety form guidance based on detected SDKs

## Report Diff

When previous report exists, show:
- Score delta per dimension
- Policy value changes since last audit
- Resolved findings
- New findings
- Unchanged high-priority findings
- Manual gate status changes
