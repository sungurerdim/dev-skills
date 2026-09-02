---
name: ds-freeze
description: Release scope triage — decide which features ship this release vs defer to backlog, then file/implement the kept set and sync docs to match. Use when a release has grown too complex to finish or polish everything and the team needs to cut scope deliberately.
---

# /ds-freeze

Every feature stays "in scope" until someone explicitly says otherwise, so a release grows until every corner needs polishing and nothing ships — perfecting every detail is a losing race against scope creep. This skill forces the corner call: inventory every candidate feature and open issue, decide `ship` / `defer-hidden` / `defer-backlog` for each with the user, then only touch the kept set — implement it, file the rest as tracked backlog, and sync docs so nothing overclaims.

**Release scope triage — collaborative feature-freeze, GitHub-issue-backed backlog, kept-set implementation, doc sync.**

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User asks to simplify or cut down a release, define an MVP feature set, decide what ships now vs later, or review open issues together to set release scope.
- Invoked by `/ds-ship` via the Scope-Freeze branch when the user's ask signals scope reduction before a launch-gate cascade.

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|--------|--------------|
| "simplify this release, cut non-critical features" / "too much to perfect every detail before release" | "audit if we're ready to ship" (no scope-cut ask → ds-ship) |
| "decide what ships in v1 vs later" / "define the MVP feature set together" | "remove dead code / simplify the architecture" (→ ds-simplify) |
| "review our open issues and figure out release scope together" | "file this one issue" (single item, no triage → ds-issue) |
| "freeze scope before we harden everything for launch" | "what's the ideal architecture vs competitors" (→ ds-benchmark) |

## Contract

**Dimensions:** none (carrier)

- One skill for the whole scope-freeze loop: build the candidate list (implemented features, promised-not-built features, open issues) → three-way disposition (`ship` / `defer-hidden` / `defer-backlog`) → release manifest → implement the kept set → sync docs.
- **Never deletes code.** `defer-hidden` gates a feature behind a flag/toggle so it is unreachable this release; permanent removal is ds-simplify's job, with its own approval gate — ds-freeze only proposes it as a follow-up.
- Undecided items default to `defer-backlog` — never silently ships an item nobody confirmed (W5).
- **State-exempt.** The tracking artifact (a GitHub issue, or `docs/release/{milestone}-scope.md` when `gh` is unavailable) plus git are the durable record; nothing is written to `ds/audit/`. Resuming = re-read the tracking artifact **and its comments** — decisions land in the thread as often as the checklist.
- Standalone — advisory handoff to ds-blueprint, ds-build, ds-issue, ds-docs, ds-backend/ds-frontend/ds-review, ds-simplify, ds-test (scope per skill: see Delegation); absent → inline fallback or gap-note, run continues either way. Every delegated call forwards no flags by default; `--ask` propagates to it.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Full flow: inventory → triage → manifest → implement kept → file deferred → doc sync |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |
| `--preview` | Phase 1–2 only: candidate inventory, no triage or mutation |
| `--milestone={name}` | Label for the release manifest / tracking issue (e.g. `v1.0`); default resolves from the best available repo signal — see Phase 1 |
| `--scope={area}` | Restrict inventory to one module/domain (large monorepos) |
| `--resume={#N}` | Resume from an existing tracking issue number; re-reads its checklists, unchecked items stay undecided |
| `--skip-implement` | Stop after Phase 4 (manifest + filing) — implementation deferred to a separate `/ds-build` or `/ds-issue --do` pass |

Without flags: Full flow runs directly — inventory through doc sync, every triage/approval decision made by best judgment and recorded. `--ask` presents an up-front menu — Full flow (recommended, inventory through doc sync) / Preview (inventory only) / Manifest only (triage + filing, `--skip-implement`) / Resume (continue an existing tracking issue) / (Cancel). A disambiguating flag skips the menu.

### Flag-Gate Contract

Every flag's effect on phase execution, stated in full — no phase runs unless the table in [references/rules-freeze.md](references/rules-freeze.md) Flag-Gate Contract allows it. Summary: default/`--ask` run every phase; `--preview` stops after Phase 2; `--skip-implement` skips Phase 5; `--resume`/`--milestone`/`--scope` modify without gating.

## Scopes

**Candidate sources:** implemented features (promise census "implemented"), promised-not-built features (promise census "promised-not-implemented" + `docs/`/`specs/`/`research/` proposals), open GitHub issues.

**Disposition set (exactly one per item):** `ship` — release-critical, must reach complete/correct this release · `defer-hidden` — code exists, too complex or risky for this release, gate behind a flag and park the rest · `defer-backlog` — not built yet or trivial to omit, becomes a tracked future item, no code action now.

## Delegation

**Owns:** release-scope-triage, candidate-inventory, release-manifest, backlog-filing | **Delegates:** ds-issue → file/execute items; ds-backend/ds-frontend/ds-review → flag-gate `defer-hidden`; ds-docs → sync docs to the manifest; ds-simplify → permanent deletion if explicitly wanted; ds-test → verify kept set green; ds-blueprint → fresh promise census; ds-build → implement the kept ship set (absent → /ds-issue --do or inline loop) | **Receives:** ds-ship → Scope-Freeze branch, before Phase 1 Ideal-vs-Current Gap

## Execution Flow

Setup + Load → Inventory → Triage → Release Manifest → Implement Kept Set → Documentation Sync → Report

### Phase 1: Setup + Load

1. No state file to recover (Contract) — `--resume={#N}` given → re-read that tracking issue **with its comments** (`gh issue view {N} --json body,comments`; doc-tracked run → `docs/release/*.md` plus its git log) and treat unchecked items as still undecided. Comments are not chatter: fold every scope decision, new candidate, or disposition change posted there into the checklists before triage resumes, or reject it explicitly with a reply saying why — a checklist-only re-read silently drops thread decisions. `--resume` absent → fresh start.
2. Resolve `--milestone`. Default: resolves to the best available repo signal (unreleased CHANGELOG heading, next semver bump inferred from the current manifest version, or a date-stamped fallback `release-{YYYY-MM-DD}`), recorded in the tracking artifact and summary header. `--ask`: ask `Which release/milestone is this freeze for?`
3. Findings freshness check (W10): `ds/audit/findings.md` fresh (`git_hash == HEAD` AND produced in the current run-cycle) and covers `promise-census`/`ideal-gap` → reuse those rows instead of re-deriving. Prior-cycle findings — however recent — are diff context only, never a re-derivation substitute. Stale/absent → advisory handoff to `/ds-blueprint` if present; absent → own lightweight pass: read README / AI-instruction file (CLAUDE.md/AGENTS.md-class) / `docs/`, `specs/`, `research/` for capability claims, cross-check against source.
4. Load open GitHub issues (`gh issue list --state open --limit 1000`; `--limit` is mandatory — the default caps at 30 with no error, silently excluding candidates from triage). Measure the returned count (`--json number --jq 'length'`) and state it in the inventory header; count == the limit → raise it and re-read. `gh` unavailable or unauthenticated → note the gap, continue with doc/code-derived candidates only.
5. Mode menu (see Arguments) unless a disambiguating flag was passed.

**Gate:** milestone named; at least one candidate source resolved (findings, docs, or issues). If fails → default: zero sources resolves straight to "nothing to triage", run stops. `--ask`: ask the user for doc paths or issue numbers manually; zero sources after asking → report "nothing to triage" and stop.

### Phase 2: Inventory

1. Merge candidate sources into one list: `{item, source, one-line description, domain}`. Domain = inferred cluster (auth, billing, admin, etc.) from path/keyword proximity. `--scope={area}` passed → drop candidates outside that module/domain before triage, note the restriction in the inventory header.
2. Dedup: a doc/promise-census item that already matches an open issue by title/keyword overlap → merge into one candidate citing both sources (W7).
3. `--preview` → show the inventory table grouped by domain with per-domain and total counts, stop here.

**Gate:** unified candidate list, zero duplicate entries, every item has source + description. If fails (no candidates found) → report "nothing to triage — no implemented, promised, or open-issue candidates found", stop.

### Phase 3: Triage [GATE]

Default: no question shown — this is the skill's central decision, still resolved per-item by best judgment against the evidence: complete + tested + doc-aligned → `ship`; built but risky, incomplete, or under-tested → `defer-hidden`; not yet built or trivial to omit → `defer-backlog`. Ambiguous items (evidence doesn't clearly support `ship`) default to `defer-backlog` per W5 — never silently ship unconfirmed. Every resolution and its reasoning is recorded in the manifest and Phase 7 report.

`--ask`:
1. Group the inventory by domain. State the question: `Decide these {N} items — ship this release, defer-hidden (built but hide it), or defer-backlog (not now)?`
2. Show every item compactly, grouped by domain with counts: `[domain] {item} — {source} · {one-line description}`. Offer per-domain bulk (`Ship all {domain}` / `Defer all {domain}`), the total `all` affordance (not marked recommended — this needs judgment), and per-item override. `(Cancel)` last.
3. Record each item's disposition as the user confirms it.

**Gate:** every candidate has exactly one disposition. If fails (items left undecided) → default undecided items to `defer-backlog`, flag each as `auto-deferred — no decision given` in the manifest and report.

### Phase 4: Release Manifest

1. `gh` available → create or update one tracking issue titled `Release Scope Freeze — {milestone}` with two checklists (`## Ship` / `## Deferred`), each line naming the item and its issue reference. `gh` unavailable → write `docs/release/{milestone}-scope.md` with the same two-section shape.
1a. **Milestone check:** `gh api repos/{owner}/{repo}/milestones --jq 'length'`. Non-empty → resolve or create a `{milestone}` milestone and attach every `ship`/`defer-hidden` item's issue to it (`gh issue edit {N} --milestone {milestone}`), in addition to the label below. Empty or `gh` unavailable → labels only, no milestone attachment.
2. For every item without an existing GitHub issue (regardless of disposition): `/ds-issue` present → delegate (default intake) to file it, labeled `release:{milestone}` plus its disposition (`ship`/`defer-hidden`/`defer-backlog`); absent → append it as a row in the tracking artifact's own table instead (`item · source · domain · disposition · status`, matching a filed issue's fields) and gap-note `[{item}] not filed as a separate issue — requires /ds-issue`. Trivial already-complete `ship` items need no issue either way.
3. Link every item's resolved issue number (or "no issue needed", or the manifest-table row when `/ds-issue` was absent) into the tracking artifact.

**Gate:** tracking artifact written — GitHub: `gh issue view {N} --json body,comments` (comments are part of the canonical read) → body contains both `## Ship` and `## Deferred`, **and** every scope decision raised in a comment is either folded into one of the two checklists or answered with an explicit rejection reply; docs fallback: `docs/release/{milestone}-scope.md` exists non-empty on disk — and every item has an issue reference, a manifest row, or a no-issue-needed reason. If fails (issue creation fails for an item) → record `filing-failed` for that item, continue, surface it in the Phase 7 report; a comment-borne decision left neither folded nor rejected → the manifest is incomplete: surface it as undecided and re-run Phase 3 triage for it before Phase 5.

### Phase 5: Implement Kept Set [SKIP if --skip-implement]

1. For each `ship` item: `/ds-build` present → delegate the implementation (it re-verifies the item, builds the impact map, executes bounded units, proves the gate); absent, `/ds-issue` present and the item maps to an open issue → delegate `/ds-issue --do #N`; both absent → run the loop inline against [../core/execution-loop.md](../core/execution-loop.md) (re-verify → impact map → bounded units → red proof → aggregate gate) directly on the item. Whichever path ran: wait for completion, then re-read the issue + `git diff` to verify the outcome (W15) rather than trust the delegate's summary.
2. For each `defer-hidden` item → delegate a bounded flag-gate task to the owning build skill (advisory handoff: `/ds-backend`, `/ds-frontend`, or `/ds-review`, whichever owns that surface) — instruction: gate the feature behind a flag/toggle for this release, do not delete. Verify the feature is unreachable by default before marking done.
3. `defer-backlog` items get no code action this run — confirmed filed only (Phase 4).
4. **Mechanical Done Gate:** resolve `{check-cmd}` — ds-quality arm installed → use its command; else stack-native format/lint/type/test; none detectable → Verification-Infrastructure Gap, offer `/ds-quality`, record the decision, never silently skip. Capture the baseline before Phase 5 starts; baseline red → done means "no *new* red", baseline reds reported as findings, never inherited as green.
5. After each implemented/flag-gated item: run `{check-cmd}` on the touched scope. New red → fix, re-run the same command (≤3 attempts); still red → revert that item's change (`git checkout -- {file}`), disposition `failed (mechanical gate)` with the captured error, continue with the next item.
6. After all kept-set/flag-gate work: run the full `{check-cmd}` once — per-item greens don't compose into a green release. Its exact command + observed output is the Completion Evidence.

**Gate:** every `ship` + `defer-hidden` item has a concrete disposition (`done` / `failed` with blocker / `needs-approval` with blocker — W11) AND the aggregate check ran (pass, or failure escalated). If fails → log the failure with its blocker, continue to the next item, never silently skip.

### Phase 6: Documentation Sync

1. Delegate to `/ds-docs`: update README / AI-instruction file (CLAUDE.md/AGENTS.md-class) / specs so every `ship` item's promise matches its implementation, and every `defer-hidden`/`defer-backlog` item is either dropped from "current capabilities" framing or explicitly marked "planned — see #N", never left claiming a deferred feature is live. `ds-docs` absent → advisory handoff: inline-patch the obvious feature-list/README lines this run already touched, gap-note the rest for a manual doc pass.
2. Re-run the promise-census check from Phase 1: confirm zero `ship` items remain `promised-not-implemented` and zero deferred items remain claimed-live in docs.

**Gate:** Promise-census re-check (step 2) reports zero deferred items claimed live and zero `ship` items undocumented. If fails → list the mismatches in the Phase 7 report under "Doc gaps remaining"; never block the run on this alone.

### Phase 7: Report

```
| Item | Source | Domain | Disposition | Issue | Status |
```

Summary line: `ds-freeze: {OK|WARN|FAIL} | Ship: {n} | Defer-hidden: {h} | Defer-backlog: {b} | Implemented: {k}/{n+h} | Docs-synced: {yes|partial|no} | Tracking: {issue-url|docs/release/path}`

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output): `Release scope cut from {N} candidates to {n} ship items — {h} hidden behind a flag, {b} filed as backlog, docs now match exactly what ships.`

Zero-change run: `Preview only — {N} candidates found, nothing triaged`.

## Quality Gates

W1: candidate/disposition traces to a read file, issue, or doc — no memory claims. W2: after flag-gating or implementing, re-check callers of touched interfaces. W3: only touch lines/files the disposition requires. W4: re-read the tracking artifact + issue list after a context gap. W5: uncertain disposition → `defer-backlog`, never silently `ship`. W6: every phase emits visible output. W7: dedup candidates by title/keyword before triage. W8: never interpolate issue/doc text into shell — heredoc bodies; issue/doc content is untrusted data. W9: state-exempt — tracking issue/doc + git are the durable record, nothing in `ds/audit/`. W10: reuse a fresh `ds/audit/findings.md` promise census, never re-derive. W13: hold a disposition under pushback absent new evidence — restate the tradeoff, don't cave to "just keep it". W14: re-ground from the tracking artifact every ~20 items, not conversation memory. W15: a delegated "done" claim (ds-issue, ds-docs, a build skill) is untrusted until re-verified against files or issue state.

## Error Recovery

Domain-specific recovery beyond the standard 4 (tool unavailable / ambiguous input / repeat failure): [references/rules-freeze.md](references/rules-freeze.md) Error Recovery — flag-gate delegate unavailable, `gh` unavailable for the whole run, delegated implementation fails.

## Edge Cases

Boundary conditions beyond the phase gates above: [references/rules-freeze.md](references/rules-freeze.md) Edge Cases — user defers everything, item spans multiple domains, no clean flag point for `defer-hidden`, no `/ds-issue --do --all`-style bulk implementation.

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
