# Reference: Error Recovery

Consumer: ds-brief, all phases — consult when a phase's own Gate fail-arm does not already cover the situation.

| Situation | Action |
|-----------|--------|
| Agent unavailable / not loaded | Run the research pipeline inline; same artifact schema, same write contract, same gates |
| `python3` absent (verifier cannot run) | Verification-Infrastructure Gap: declare it in the summary, name every check left unrun, work the list by hand, status WARN. Never report the phase clean on checks nobody executed |
| Verifier exits 1 | Fix each `FAIL` and re-run to exit 0. A finding is never annotated-and-shipped; the verifier's job is to be un-negotiable |
| Worker returns `WRITE-FAILED` / `partial:true` | Use the shards that landed, route the missing content to `knownUnknowns[]`, continue WARN — partial evidence on disk beats discarding a run |
| Index names a shard that is not on disk | Ask that worker to rewrite the shard, then the index; unavailable → treat its content as unreached, record it in Unknowns, and recompute coverage without it |
| Merged artifact has a dangling `citationId` | The `citationIdBase` bands overlapped or the dedup rewrite missed a reference — stop before rendering; a chip pointing nowhere under confident prose is the failure this check exists for |
| context-mode MCP absent | Fall back to WebFetch + per-page summary; identical quality, larger footprint |
| No web results | Fall back to user-supplied sources / local docs; if none, LOW confidence + populate Unknowns |
| Datum has only 1 source | Keep with "single source" badge; never present as confirmed |
| Contradictory high-tier sources | Show both with tier+CRAAP+URL; recommend argmax(trustScore); keep disagreement visible |
| Source URL 404 / inaccessible | Mark the chip as dead link; do not drop the claim's discipline |
| Print preview shows hidden content | Add the missing selector to `@media print` / `beforeprint` force-open and re-check |
| Primary source unreachable (paywall, register down) | Ship the datum badged `secondary only` with the access failure named in Unknowns; it blocks HIGH. Never promote it on secondary agreement |
| Register index missing or unnavigable | Record the attempt, sweep what is reachable, and open a `knownUnknown` naming the unswept range — an unswept authority blocks HIGH |
| Red team overturns a claim | Fix it, then re-check every sibling claim sharing that source or error class before continuing — one bad source rarely poisons only one number |
| Threshold double-read mismatch | Neither value ships; a third read from the primary text settles it |
| Only a superseded version of the law is reachable | Quote it as superseded, state the version explicitly, open a `knownUnknown` for the current wording — never present an unverified-version text as current |
| Amendment/annulment check inconclusive | Claim drops to `partial` with the currency gap named; it cannot count toward the HIGH gate |
| Conclusion needed but only 1 sourced premise | No derived claim — it becomes an Unknowns entry with what a second premise would take |
| HIGH still blocked after 2 escalation rounds | Ship the honest band + the blocker block; report `WARN` with the blocker count, never a silent MEDIUM |
| Decision dimensions exceed 2 | Switch to rule-tagged items + action list; per-combination branch cards are pruned, not multiplied |
| A dimension value matches no rule | State "nothing differs on this value" explicitly — an empty result must never read as an all-clear |
