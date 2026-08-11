# Manual Checklist: Browser and Judgment Checks

Consumer: SKILL.md Phase 6 (Output), after a green `assets/verify-brief.py` run. These are the checks a static parser cannot see — they need a rendered page, print emulation, or human judgment. Work every applicable row and report what was checked with what was observed; a bare "looks fine" is not evidence.

## Always

- Offline open: open the file with the network disabled — page renders fully, zero console errors, no request leaves the browser.
- Print preview: chrome hidden, collapsibles force-open, page breaks clean, in-file anchors print no URL; the cover renders as page 1 and the contents as page 2 under print emulation.
- Mobile discipline at 320/480/600px: card tables, ≥44px touch targets, ≥16px inputs, sticky calc output ([report-template.md](report-template.md) § Mobile discipline).
- Chrome budget: header ≤150px at 1280px wide; nav renders as one row at 320/480/768/1280/1920 (measure its height — it must not grow); `main.wrap` exceeds 1080px on a 1920px viewport while prose stays at the measure; back-to-top appears after 400px of scroll; the collapsed apparatus opens on a search hit.
- Anchor landing: click nav and in-text anchors — each target lands below the sticky nav (the CSS rule is machine-checked, R16; the live landing is not).
- Ornament sweep: no scalar rendered twice across prose, tables and the trust strip.
- Confidence reading: the trust strip's plain-language sentence actually explains the band, in the request language.
- 60-second test: from a cold open, one selection answers "what applies to me, what must I do, by when" within one screen — otherwise the spine is wrong, not the reader.
- Bundle independence (unless `--no-archive`): the HTML still opens and works with the `sources/` directory removed.

## When the layer shipped

| Layer | Check |
|-------|-------|
| Cites (`data-cite`) | Spot-check ≥3 chips: popover opens with its quote, the outbound link resolves live, JS-off chips stay plain links (quote↔artifact byte-match is machine-checked, X05) |
| Charts | Chart row count equals its JS-built data-table row count |
| Xref | Arriving via a `.xref` auto-opens the target `<details>` |
| Matrix | Every filled cell shows a `.cellcite`, every `N/M` completeness score recomputes from the artifact (never asserted), gaps render as "—"; "differences only" hides exactly the `same` rows and print restores them |
| Branch | Each selection shows exactly its matching blocks; "Show all" / no-selection / JS-off show all branches labeled; print carries every branch with its `.whochip`; a fully hidden section also hides its nav button and `#hiddenNote` states the count |
| Obligation badges | Every normative statement carries exactly one badge and the legend renders above first use |
| Action list | Selecting a situation changes the visible item count and the profile line; an unset decision raises the unanswered note; every item shows who / by when / how / source; the copy control produces the visible list (clipboard or textarea fallback); default print carries every item with its condition label and `print-profile` narrows only the list |
| Derived badges | Each popover shows ≥2 premise quotes plus the reasoning sentence |
| Coverage ledger | Rendered counts recompute from the rows and no `gap` row is missing from Unknowns (artifact side is machine-checked, A12) |
