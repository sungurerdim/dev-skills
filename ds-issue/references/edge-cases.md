# Reference: Edge Cases

Consumer: ds-issue, all phases. The `--do --all` queue-specific rows are also stated in Phase 6 step 0 and the Contract (§`--do --all`); this file is the full illustrative set, not a second definition.

| Scenario | Behavior |
|----------|----------|
| No adapter present | Auto-detect repo/done-signal/criteria; hazards → six generic axes only |
| No git repo, no remote, remote host isn't `github.com`, `gh` not installed, or `gh` installed but unauthenticated | Local mode — root `tasks.md` replaces every `gh issue *` call (Contract); state the reason once (`no GitHub remote` / `gh not installed` / `gh unauthenticated`); gap-note once that cross-issue linking, `gh search` dedup, and label priority are unavailable; `gh auth login` (or installing `gh`) switches back to GitHub mode on the next run |
| Both a GitHub remote and an existing local `tasks.md` present | GitHub mode wins (the remote is the signal); flag the stale `tasks.md` once. Default: import its open entries as issues, recorded in the summary. `--ask`: ask whether to import or leave it alone. |
| `gh` < `GH_MIN_VERSION` (no native sub-issue/dependency flags) | Fall back to REST sub-issue link / task-list body per [github-features.md](github-features.md); recommend upgrade |
| No raw input given | Ask for a 1-2 sentence description, then start |
| Refining an existing raw issue | Take the number; read body + comments, fold requirement-bearing comments into the body Done list; edit rather than create |
| True duplicate | Don't create; link the existing issue |
| Symptom can't be reproduced | Don't create; report missing evidence |
| Pure-decision, no code change | `needs-decision` + ADR-stub; skip reproduction |
| Estimate exceeds bounded task | Propose an epic + sub-issues, natively linked; never one mega-issue |
| Epic would exceed `EPIC_MAX_CHILDREN` children or `EPIC_MAX_DEPTH` nesting levels | GitHub's verified limits — split the epic into sibling epics rather than nesting deeper |
| Issue types unavailable (`gh api /orgs/<org>/issue-types` → 404, e.g. any user-owned repo) | Labels only; never claim a type was set |
| Repo has no labels at all | Ask once whether to scaffold the type + priority set; declined → record the gap and proceed label-free, priority stated in the body |
| A decision arrives while the issue is open | Write it into the body's Open decision block as `Resolved <date>: …` + a Log line; never leave it in a comment |
| Issue scope collapsed (premise no longer holds) | Closure block in the body → successor issue with the context restated → link both ways → close `--reason "not planned"` |
| Body approaching the `BODY_MAX` character bound | It is an epic — split it; the bound is observed from the API error, not documented |
| Feature with open design decisions | `/ds-pipeline` present → route to it (spec chain) first, file sub-issues from its tasks; absent → file as-is with an Open decision block naming the open question — never a mega-issue guessing the "how" |
| `--do` issue already resolved | Close as completed with proving evidence covering the full Done set (requirement promotion runs first); skip implementation |
| `--do` issue is stale | Stop; report with evidence; don't fabricate a fix |
| `--do --all`, no open issues | Report `nothing to do — 0 open issues`; mutate nothing |
| `--do --all`, one issue stale/blocked/red | Record its outcome, continue the queue; surface it in the per-issue outcome table |
| `--do --all`, an issue needs a live credential or other exception-list item | Skip that issue, record `only you can do`, continue the queue |
| `--do --all`, repeated failures across issues | After `QUEUE_FAIL_STREAK` consecutive issues fail the same way, stop the queue and report the systemic blocker (don't burn the whole backlog) |
| `--do` untyped code (no language server) | grep-based references; flag affected-set confidence lower |
| `--do` aggregate red after units green | Composed regression — fix and re-run; never close red |
| Security/payments/crypto/migration touched | Top-tier care + line-by-line-review note in the body's Closure block |
