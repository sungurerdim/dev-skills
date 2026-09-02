# Rules: Release Automation, Build & Registry Provenance, Backup/DR, Build Hygiene

Applies to all project types with a release or publish step. Loaded for the `release-pipeline` scope.

| Section | Rules |
|---------|-------|
| **Build & Registry Provenance** | DOP-18, DOP-21 (2 HIGH) |
| **Backup, DR & Resilience** | DOP-30–31 (1 HIGH, 1 MEDIUM) |
| **Release Automation** | DOP-32–35, DOP-37, DOP-43, DOP-47 (4 HIGH, 3 MEDIUM) |
| **Build Hygiene** | DOP-38–39 (2 MEDIUM) |

## Build & Registry Provenance

### DOP-18 [HIGH] Build Provenance & Artifact Attestation
Beyond pinning inputs (DOP-01 action SHA-pin, DOP-14 dependency pin): the build *output* itself needs a verifiable, signed record of how it was produced (SLSA-style provenance) so a consumer can confirm the artifact came from the claimed CI run and source commit, not a tampered build.
- **Detect:** Release artifacts (binaries, container images, packages) published without a signed provenance/attestation record; no `actions/attest-build-provenance` (or equivalent SLSA provenance generator) step in the release job; attesting job lacks `attestations: write` + `id-token: write` permissions; consumers have no way to verify artifact-to-source-commit lineage.
- **Fix:** Add a build-provenance step to the release job (GitHub: `actions/attest-build-provenance`, generates a signed SLSA-style attestation tied to the workflow run) with `permissions: attestations: write` + `id-token: write`; publish the attestation alongside the artifact; document the verification command (`gh attestation verify <artifact> -R <org>/<repo>`, requires gh 2.49.0+) in release notes. Attestation alone = SLSA v1.0 Build Level 2; isolating the build in a reusable workflow reaches Build Level 3.
- **Impact:** Without signed provenance, a compromised build step or registry can substitute a malicious artifact and no one downstream can detect it.
- **Source:** [SLSA Provenance](https://slsa.dev/spec/v1.0/provenance), [GitHub Artifact Attestations](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds)

### DOP-21 [HIGH] Registry Publish Auth Currency (Trusted Publishing / OIDC)
Release workflows publishing to package registries must use short-lived OIDC trusted publishing, not long-lived token secrets. npm classic tokens were fully revoked 9 Dec 2025 — a publish job still referencing one is broken, not just insecure; granular npm tokens now cap at a 90-day lifetime.
- **Detect:**
  - npm publish step authenticating via a stored token secret (`NODE_AUTH_TOKEN` / `.npmrc` `_authToken`) instead of trusted publishing — classic tokens no longer authenticate at all; granular tokens expire ≤90 days and rot silently in secrets
  - PyPI publish using `password:` / long-lived API token with `twine` instead of a Trusted Publisher
  - Publish job missing `permissions: id-token: write` when trusted publishing is intended
- **Fix:** npm — configure Trusted Publishing (OIDC, GA since 31 Jul 2025 for GitHub Actions + GitLab CI; requires npm CLI ≥ 11.5.1 and `id-token: write`); provenance attestations are generated automatically, no `--provenance` flag needed. PyPI — configure a Trusted Publisher and publish via `pypa/gh-action-pypi-publish` (≥ v1.11.0 auto-generates PEP 740 attestations). Remove the long-lived token from secrets after cutover.
- **Impact:** A leaked long-lived publish token = full package-takeover; OIDC tokens are per-run and unexfiltratable at rest. On npm the classic-token path is additionally a hard availability bug since Dec 2025.
- **Source:** npm Trusted Publishing GA (github.blog, 2025-07-31); npm classic-token revocation (2025-12-09); PyPI Trusted Publishers + PEP 740

## Backup, DR & Resilience

### DOP-30 [HIGH] Backup & DR Posture (3-2-1-1-0)
Infra-level backups follow 3-2-1-1-0 with tested recovery; DR objectives are explicit. (Database-level backup/restore checks live in ds-backend's Database scope — this rule covers the infrastructure posture.)
- **Detect:**
  - Backup config with no immutable/air-gapped tier (object-lock/WORM): 3 copies, 2 media, 1 offsite, 1 immutable, 0 errors on recovery test
  - Backup infrastructure sharing credentials/network segment with production admin accounts — backups are an active ransomware target (Veeam-reported: 89% of surveyed orgs had backup repositories specifically targeted)
  - No explicit RPO/RTO per service tier; no dated log of a DR/failover drill
- **Fix:** Add an immutable storage tier; segment backup admin identities (separate credentials, MFA, ideally separate IdP); define RPO/RTO per tier and align backup frequency/replication to them; schedule recurring restore/failover drills and log pass/fail
- **Impact:** A backup with no immutable tier is itself a ransomware target — attackers who reach production credentials delete the backups first; an undrilled DR plan fails exactly when it is needed.
- **Source:** 3-2-1-1-0 rule (Veeam et al.); ransomware backup-targeting reports

### DOP-31 [MEDIUM] Failure-Injection Readiness (advisory)
Resilience assumptions are exercised, not assumed — at minimum in pre-production.
- **Detect:** services with retry/timeout/failover logic that has never been exercised by any failure injection (no chaos/fault-injection config, no game-day/tabletop record)
- **Fix:** Start minimal: kill one instance/dependency in staging and observe whether timeouts, retries, and alerts behave as designed; record the result. Full chaos-engineering platforms are optional — one exercised failure beats ten documented assumptions. Advisory only — never a blocker
- **Impact:** Retry/timeout/failover logic that has never been exercised is an untested assumption — the first real failure is the first time anyone learns whether it actually works.
- **Source:** Principles of Chaos Engineering; SRE game-day practice

## Release Automation

### DOP-32 [HIGH] Single-Command Release Runs a Deterministic Gate Chain
The one-command release pipeline replaces human memory with deterministic gates at every step.
- **Detect:** Release scripts that skip dirty-tree checks, deploy unchanged code, bump versions manually, re-implement quality checks the hooks already own, or run the full heavy suite on every deploy regardless of cost.
- **Fix:** Chain the gates: reject a dirty working tree → skip deploy when nothing changed since the last release tag → derive the semver bump from the CHANGELOG's [Unreleased] section (no real content → skip the release entirely) → trigger the existing pre-push quality gate once instead of re-coding it → age-gate the heavy layer (full E2E, link-proofing, cross-repo drift) with a timestamp file (run when older than N days, not per-deploy) → build/deploy → verify live. Allow `--emergency` to bypass gates only during a real incident.
- **Impact:** Every gate the script owns is a failure class removed from human memory — unreleased-junk deploys, empty releases, and skipped quality checks stop depending on whoever runs the command.
- **Source:** XR-085 — cross-project experience registry (2026).

### DOP-33 [HIGH] Heavy Checks Run Before the Deploy-Triggering Action
Identify which action actually triggers deployment, and sequence heavy checks strictly before it.
- **Detect:** On push-equals-deploy hosts (static-page platforms, git-integrated deploys to a protected branch), heavy validation (build health, link check, fact drift) scheduled after push — i.e. after the deploy already started.
- **Fix:** Map the deploy trigger explicitly. Where push IS the deploy, run the heavy layer pre-push — the gate and the deploy collapse onto the same action, so nothing can run "between" them. Where a separate deploy step exists, gate→push→deploy is acceptable.
- **Impact:** Heavy checks sequenced after the trigger validate what production is already serving — every failure they catch is a live incident instead of a blocked push.
- **Source:** XR-087 — cross-project experience registry (2026).

### DOP-34 [MEDIUM] A Dormant Gate's First Real Run Expects Accumulated Failures
A local gate/build pipeline that hasn't genuinely run in a long time is assumed to hide multiple independent latent failures; its re-activation is itself validated as a first real run.
- **Detect:** A gate installed or reconfigured long ago, never since exercised end-to-end, treated as "known green"; surprise when its first genuine run fails in several unrelated ways.
- **Fix:** Treat setup or reactivation of any gate as a first-real-run event: execute it fully, expect a batch of independent findings (environment drift, moved paths, stale versions), and budget for fixing them before trusting the gate. Zero findings from a long-dormant gate is a signal the gate isn't actually checking anything.
- **Impact:** Teams that assume dormant gates are green ship through a gate that silently stopped working — the accumulated failures then surface in production instead of the pipeline.
- **Source:** XR-178 — cross-project experience registry (2026).

### DOP-35 [MEDIUM] Multi-Repo Releases: Thin Orchestrator, Repo-Owned Gates
When independent repos release in sequence from one top-level script, each repo owns its gated release; the orchestrator only invokes and reports.
- **Detect:** A top-level release script re-implementing per-repo checks; one repo's failure rolling back another's completed release; repos that can no longer release independently.
- **Fix:** Keep each repo's gated release script authoritative inside that repo; the cross-platform orchestrator calls them in order and aggregates a combined summary. Each repo carries independent success/failure — a downstream failure never unwinds an upstream completed release, and every repo stays independently releasable.
- **Impact:** Fat orchestrators become a second, drifting copy of every repo's release logic, and coupled rollbacks turn one repo's flake into a multi-product outage.
- **Source:** XR-020 — cross-project experience registry (2026).

### DOP-37 [MEDIUM] Orchestration Tooling Is Preinstalled on Every Target Platform
Task-runner/orchestration scripts are written in a tool already present on all platforms the team targets.
- **Detect:** Build/release orchestration requiring a tool absent by default on a supported platform (e.g. `make` on Windows); onboarding docs whose first step is installing the runner itself.
- **Fix:** Choose the runner from the intersection of default installs across target platforms (e.g. bash where Git-for-Windows is assumed, or the language runtime the project already requires); if a non-universal tool is genuinely warranted, gate it behind an explicit documented install step, not an assumption.
- **Impact:** A runner missing on one platform silently forks the team into "can run the automation" and "pastes commands from chat" — the second group ships the mistakes the automation existed to prevent.
- **Source:** XR-176 — cross-project experience registry (2026).

### DOP-43 [HIGH] `GITHUB_TOKEN` Does Not Trigger Downstream Workflows
A workflow run, push, or PR created using the default `GITHUB_TOKEN` does not trigger other `on: push`/`on: pull_request` workflows — a deliberate recursion guard, not a bug — so a release-automation chain that depends on one workflow's output triggering the next silently stalls.
- **Detect:** A release/publish workflow (e.g. `googleapis/release-please-action`) whose output (tag push, release event) is expected to trigger a downstream workflow (publish, deploy, notify), authenticated only with the default `GITHUB_TOKEN`; the downstream workflow never runs and no error is logged anywhere.
- **Fix:** Where a workflow's output must trigger another workflow, authenticate the triggering step with a PAT (fine-grained, minimal scope) or a GitHub App token instead of `GITHUB_TOKEN`. Alternative: use `workflow_run` to chain explicitly, or consolidate both steps into one workflow so no cross-workflow trigger is needed.
- **Impact:** The failure is silent — no error, no failed job, just a downstream workflow that never starts — so the gap is usually discovered only when a release ships without its supposed-to-be-automatic follow-up action.
- **Source:** [GitHub Actions — Triggering a workflow from a workflow](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#triggering-a-workflow-from-a-workflow)

### DOP-47 [HIGH] Deploy Workflow Safety: Concurrency and Environment Gates
A deploy workflow needs different concurrency and approval behavior than a PR/CI workflow — copying the same `cancel-in-progress: true` pattern, or skipping environment protection, turns a routine push into a partial deploy or an unreviewed production release.
- **Detect:**
  - Deploy workflow using `cancel-in-progress: true` (a second push mid-deploy cancels the first deploy partway through, leaving a mixed/partial release)
  - Production deploy job with no `environment:` block, or an `environment:` with no required reviewers configured — any `workflow_dispatch` or auto-triggered job can ship to production unreviewed
  - Staging and production sharing one workflow/job with no distinct gating between them
- **Fix:** On deploy workflows, set `cancel-in-progress: false` (or omit `concurrency` entirely if deploys must never overlap — use a queue instead). Set `environment: { name: production, url: <url> }` on the production deploy job and configure required reviewers on that GitHub Environment. Keep staging auto-deploying on push to main with no approval; gate production behind `workflow_dispatch` or environment reviewers.
- **Impact:** A cancelled mid-deploy leaves production in a mixed, half-updated state with no clear rollback point; an ungated production job means any triggering event — including an automation bug — can ship to users with zero human checkpoint.
- **Source:** [GitHub Actions — Using concurrency](https://docs.github.com/en/actions/using-jobs/using-concurrency), [GitHub Actions — Using environments for deployment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)

## Build Hygiene

### DOP-38 [MEDIUM] Generated Artifacts Are Never Hand-Edited; Regenerated and Verified at the Gate
Generated artifacts (compiled output, SRI hashes, cache manifests, template-derived files) are produced automatically at pre-commit and verified fresh before push — hand edits are forbidden.
- **Detect:** Manual edits inside generated files; generated outputs stale relative to their sources at push time; no gate step comparing regenerated output to the committed copy.
- **Fix:** Regenerate artifacts in the pre-commit hook; verify freshness (regenerate-and-diff) in the pre-push gate; treat any manual edit to a generated file as a gate failure pointing at the true source to change.
- **Impact:** A hand-edited artifact is overwritten by the next regeneration — the "fix" silently evaporates, and stale artifacts (wrong SRI hash, old manifest) break production in ways that look like caching voodoo.
- **Source:** XR-013 — cross-project experience registry (2026).

### DOP-39 [MEDIUM] Cross-Surface Facts Come From One Canonical File With a Drift Gate
A numeric/pricing fact living on multiple independently-deployed surfaces (backend config, client, marketing site) has one canonical facts file, documented source owners, and a zero-dependency drift check wired into the gate.
- **Detect:** The same limit/TTL/price/count hardcoded in two or more surfaces; no canonical facts file; no automated check comparing the fact file to source owners and rendered copies; derived indicators (discount %, savings) as static strings.
- **Fix:** Maintain one canonical facts file; document the owning source file per fact; render values through the template engine's data access wherever possible, and mark the genuinely untemplatable remainder (e.g. numbers spelled out in prose) as WIRED vs NOT-WIRED. Wire a zero-dependency drift script into pre-push (no-op when the full workspace isn't checked out) validating the facts file against owners and rendered copies. Compute derived indicators (discount/savings) from real values at runtime, floored so the displayed figure never exceeds the true one.
- **Impact:** Fact drift across surfaces means the marketing site sells limits the backend doesn't honor — a support and legal problem discovered by customers, not tests.
- **Source:** XR-012 — cross-project experience registry (2026).
