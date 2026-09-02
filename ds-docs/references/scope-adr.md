# Reference: ADR Scope

Consumer: ds-docs `adr` scope, activated by the `--adr` flag or when `adr` scope is explicitly selected.

## Structure + template

`docs/adr/NNNN-{kebab-slug}.md`, sequential zero-padded numbering from `0001`. Template follows the Nygard format that `adr-tools` and `log4brains` manage — generated ADRs stay compatible with those corpora:

```markdown
# ADR NNNN: {Title}
**Status:** proposed | accepted | deprecated | superseded-by NNNN
**Date:** YYYY-MM-DD
## Context
{One paragraph: forces at play — technical, political, social, project-level — that pressured this decision.}
## Decision
{One paragraph: the choice taken. Active voice. Specific.}
## Consequences
{Bullet list: positive + negative consequences, known and anticipated.}
```

## Operations (`--adr` mode)

1. **Inventory:** list existing ADRs, verify numbering contiguous, flag any missing status/date/sections. Spot-check each `accepted` ADR's referenced file paths/symbols against current code — a since-removed reference → flag `drifted`, propose a status review (deprecate / supersede); never silently trust an ADR the system has outgrown. An ADR grounded in a measurement or experiment carries a `**Locked:** {evidence reference} — not to be revisited without new evidence` line (DOC-21); a locked ADR reopened with no new evidence cited is flagged, not treated as a valid update.
2. **Proposal candidates:** every Category B decision surfaced in recent `ds/audit/findings.md` runs (scope `ideal-gap`, `architecture`, `stack-fitness`) without a matching ADR → propose a draft ADR. A finding disposed `skipped (accepted debt)` with a stated reason and fix path, recurring across runs with no ADR → propose a debt-tracking ADR instead (ID, missing piece, deferral reason, fix path — DOC-22), so reviews cite the existing record instead of re-litigating it. Default: each draft resolves by best judgment (written using best-judgment synthesis of the finding), recorded in the summary. `--ask`: user approves each before writing.
3. **Supersedence:** new ADR contradicting an earlier one cites superseded ADR; earlier ADR updated to `status: superseded-by NNNN`.
4. **No autonomous ADR writes without record.** Every new ADR is Category B. Default: title + draft resolve by best judgment — nothing about drafting a documentation file (git-reversible, no credential, no business/legal call) matches the publish/irreversible exception list, so it is never left `only you can do`; the choice is recorded in the summary. `--ask`: user approves title + draft before file creation.
