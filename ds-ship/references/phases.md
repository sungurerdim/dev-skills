# Reference: ds-ship Phase Expansion

Extended reference for `/ds-ship` phase internals. Loaded only when a phase requires the full rule set.

## Phase 0 — Classification Signals

| Stage | Primary signal | Secondary signal |
|-------|----------------|------------------|
| idea | No source files; only `.md` / idea dump | No `package.json` / `go.mod` / stack manifest |
| spec-only | SPEC.md / PRD.md / detailed README present | Source files absent or 1-file stub |
| scaffold | Source files present | Entry points stub, bodies TODO-only, no tests |
| implementation | Non-trivial source | Tests may be partial; no CI deploy step |
| review-pending | Source + tests + CI | No deploy artifacts |
| pre-launch | review-pending + deploy config | Dockerfile / CI deploy step / hosting config present |
| launched | pre-launch + released versions | `CHANGELOG.md` with version entries OR git tags |
| frozen | launched | No commits in past 180 days |

## Phase 2 — Delegation Exclusivity

| Project type | Runs | Skips (because subsumed) |
|--------------|------|--------------------------|
| mobile | ds-mobile (authoritative for security / privacy / regulatory / a11y) | ds-compliance for those scopes |
| web | ds-compliance + ds-frontend (a11y impl) + ds-backend | ds-mobile |
| backend-only | ds-compliance + ds-backend + ds-devops + ds-deploy | ds-frontend, ds-mobile |
| library | ds-test (high coverage) + ds-docs (API-heavy) + ds-repo --oss-ready | ds-launch, ds-market, ds-frontend |
| CLI | ds-test + ds-docs + ds-repo | ds-frontend, ds-launch, ds-market |

## Phase 6 — HTML Report Structure

```
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Ship Report</title>
  <style>/* inline CSS */</style>
</head>
<body>
  <header>Stage gauge + timestamp</header>

  <details open>
    <summary>Orchestration flow</summary>
    <!-- inline Mermaid-rendered SVG -->
  </details>

  <details>
    <summary>Findings heatmap</summary>
    <!-- SVG grid: rows=scope, cols=severity -->
  </details>

  <details>
    <summary>Category A / B counters</summary>
    <!-- inline SVG bar chart -->
  </details>

  <details>
    <summary>Ship-readiness gauge</summary>
    <!-- inline SVG gauge -->
  </details>

  <details>
    <summary>Autonomous fixes applied</summary>
    <table>...</table>
  </details>

  <details>
    <summary>Awaiting user decision (Category B)</summary>
    <table>...</table>
  </details>

  <details>
    <summary>Promise vs reality</summary>
    <table>...</table>
  </details>

  <details>
    <summary>Orchestration log</summary>
    <pre>...</pre>
  </details>
</body>
</html>
```

**Constraints:**
- `<style>` inline; no external stylesheet.
- No `<script>` tags; Mermaid flow is pre-rendered to static SVG inline.
- ASCII-only: no non-ASCII characters anywhere in the HTML (print compatibility across viewers).
- Opens offline: browser loads the file with network disabled → renders identically.

## Phase 5 — Launch Chain Ordering

```
ds-devops (CI/CD integrity, signing, deps audit)
   ↓
ds-deploy (container security, TLS, monitoring, runbook)
   ↓
ds-launch (store submission OR web launch OR library publish; --perf-budget if missing)
   ↓
ds-repo (branch protection, CODEOWNERS, metadata, --oss-ready if public)
```

Each skill in the chain consumes `ds/audit/findings.md` and adds its own scope's findings. ds-ship does not re-invoke an already-completed skill in the same pass.

## Category A vs B — Examples

| Change | Category |
|--------|----------|
| Missing input validation on a route that already validates similar routes | A (conformance to existing pattern) |
| Add new route that accepts user input | B (new capability) |
| Format fix (Prettier, gofmt, ruff) | A |
| Switch formatter from Prettier to Biome | B (stack change) |
| Remove dead export with 0 references | A when LSP-verified, B when grep-only on a large codebase |
| Upgrade a patch version of a library with no breaking changelog | A |
| Upgrade a major version | B |
| Rewrite README section for compaction, preserving every fact | A |
| Rename public export | B (caller impact) |
| Delete `// legacy` code block | B (user may have kept it intentionally) |
