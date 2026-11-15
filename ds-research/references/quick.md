# Quick mode — a sourced answer in the chat, no HTML

`/ds-research quick <question>` answers a "which one / is it safe / what changed / how do I" question in minutes. It keeps every evidence rule of [craap.md](craap.md) (tiers, scores, triangulation, dating, rule 8) and drops only the deliverable: no `report.html`, no `findings.json`, no `sources/` bundle, no verifier run. A question that turns out to need tables, branches or a printable record → say so and offer the full run.

## Tracks

Run the tracks that fit the question, in parallel where the host allows; `ds-research-agent`, when present, takes the web tracks with `depth=quick`.

| Track | What | When |
|-------|------|------|
| Local | This repository: code, config, lockfiles, docs, git history | inside a repository and the question touches it |
| Official | T1 docs, standards, the vendor's own pages | always |
| Releases | T2 repositories, changelogs, registry records | a library, tool, API or version is named |
| Advisories | osv.dev, NVD, the vendor's advisories; registry endpoints per craap.md | security, dependency or upgrade question |
| Practice | T3-T5 expert and community sources | only while T1-T2 have not saturated (3+ agree → stop) |
| Comparison | each option through the tracks above, the same criteria for all | the question compares options |

Every query carries the current date. A track with no source scoring ≥ 50 → keep its best source with an `[unverified]` caveat and say the track is low-confidence.

## Answer

In this order, in the language of the question:

1. **Verdict** — `DO` · `AVOID` · `CONDITIONAL (when …)` · `UNKNOWN (what would settle it)`, then the answer in 1-3 sentences. A comparison names the winner per criterion, not only overall.
2. **Evidence** — each claim followed by its citation `[T{n}|{domain}]`; datums confirmed twice or marked `[single-source]`; for local findings `file:line`.
3. **Disagreements** — both readings with their sources; the primary or newer one leads, the conflict stays visible.
4. **Gaps** — what was not found or could not be verified.
5. **Sources** — `[{band}] T{n}|{score}|{domain}|{title}|{pub-date or unknown}|accessed {date}`.

It ends with the closing message of kernel §6 (counts `verdict {v} · sources {n} · T1-T2 {m} · 2x-confirmed {pct}% · gaps {g}`; WARN when no T1-T2 source exists; no Change table, since nothing is written).
