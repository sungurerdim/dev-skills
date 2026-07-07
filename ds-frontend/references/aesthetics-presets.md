# Named Aesthetics — Style Presets

> **Why named presets:** Generic prompts ("make it modern", "make it clean") produce homogeneous AI-generated UIs — same Inter font, same purple-gradient, same rounded cards. A named aesthetic encodes a complete design vocabulary so the model can disambiguate.
>
> Inspired by an open-source frontend design-token toolkit originally built for AI pair-programming workflows, generalized here for tool-agnostic use.

This file is loaded by `/ds-frontend` when invoked with `--aesthetic=<preset>`. Each preset defines: **palette** (color), **typography**, **spacing**, **motion**, **shadow**, **border**, **iconography**, and a one-paragraph **mood description** that acts as a prompt anchor.

---

## Preset Catalog

| ID | Name | Best For | Mood |
|----|------|----------|------|
| `dark-oled-luxury` | Dark OLED Luxury | premium SaaS, fintech, AI tools | Black-on-black, gold accents, high-end watch feel |
| `warm-trust` | Warm Trust | health, legal, family services, advisory | Cream/sand neutrals, deep teal accent, reassuring |
| `clean-minimal` | Clean Minimal | productivity, dev tools, docs | High whitespace, monospaced details, no decoration |
| `arctic-data` | Arctic Data | dashboards, analytics, monitoring | Cold blue-grey, data-dense, terminal-inspired |
| `terracotta-craft` | Terracotta Craft | artisan, indie commerce, wellness | Warm earth tones, hand-drawn texture, organic |
| `neo-brutalist` | Neo Brutalist | manifestos, indie creative, music | Hard shadows, primary colors, raw type |
| `clinical-calm` | Clinical Calm | medical, mental health, telehealth | Muted blue-greens, generous spacing, soft shadows |
| `consumer-glow` | Consumer Glow | mobile apps, social, lifestyle | Vibrant gradients, glassmorphism, large radii |
| `editorial` | Editorial | content publishing, long-form, magazine | Serif headings, asymmetric grid, sparse imagery |
| `enterprise-sober` | Enterprise Sober | B2B tools, admin panels, internal | Neutral grey, dense data, no flair, function-first |
| `studio-mono` | Studio Mono | designer/dev portfolios | Monospaced everywhere, single-color, surgical |

---

## Preset Definitions (excerpt — full token files referenced)

### `warm-trust` (suited to trust-sensitive service sectors — health, care, appointments)

```yaml
mood: >
  A patient sits across from you in a quiet, sun-warmed room. The interface
  feels like a well-kept appointment book — calm, dependable, never urgent.
  Trust is earned by restraint, not by visual noise.

palette:
  background:        "#FAF6EE"   # warm cream
  surface:           "#FFFFFF"
  surface_recessed:  "#F0E9DA"   # toasted oat
  text_primary:      "#1F2A33"   # near-black, slight blue
  text_secondary:    "#5A6470"
  accent_primary:    "#1F5C5A"   # deep teal — anchor color
  accent_secondary:  "#C97B3B"   # terracotta — used sparingly
  success:           "#3D7A4F"
  warning:           "#B6792B"
  error:             "#A53A2D"
  border:            "#E0D7C4"

typography:
  display: "Fraunces, Georgia, serif"   # warm serif for hero/numbers
  body:    "Inter, -apple-system, sans-serif"
  mono:    "JetBrains Mono, monospace"
  scale_ratio: 1.250                     # major third — calm progression

spacing:
  base: 4
  scale: [4, 8, 12, 16, 24, 32, 48, 64]
  density: comfortable                   # wider gutters than enterprise

motion:
  duration_fast:  150ms
  duration_base:  240ms
  duration_slow:  400ms
  easing: cubic-bezier(0.32, 0.72, 0.0, 1.0)   # natural ease-out
  reduce_motion: respect

shadow:
  sm: "0 1px 2px rgba(31, 42, 51, 0.06)"
  md: "0 4px 12px rgba(31, 42, 51, 0.08)"
  lg: "0 12px 24px rgba(31, 42, 51, 0.10)"

border:
  radius_sm: 6px
  radius_md: 10px
  radius_lg: 16px
  width: 1px
  style: solid

iconography:
  weight: medium      # never thin (cold) or bold (loud)
  fill: outline       # outline default, filled for active state
  recommended_set: "praxis-icons (github.com/gorkem-bwl/praxis-icons), Phosphor (regular)"

forbidden:
  - pure black (#000)        # too clinical for advisory context
  - neon accents
  - drop shadows >12px       # too modern, breaks "warm book" feel
  - gradients on primary CTAs
```

### `clinical-calm`

```yaml
mood: >
  A waiting room with afternoon light through frosted glass. Every element
  is intentional, clearly labeled, and impossible to misclick. The user is
  already stressed; the UI cannot add cognitive load.

palette:
  background:        "#F7FAF9"
  surface:           "#FFFFFF"
  text_primary:      "#0F2A2E"
  text_secondary:    "#4A5C60"
  accent_primary:    "#2E7D6F"   # muted sea-green
  accent_secondary:  "#5B8FA8"   # dusk blue
  success:           "#2E7D6F"
  warning:           "#A66A1F"
  error:             "#9C3A3A"   # never harsh red
  border:            "#D8E5E2"

typography:
  body:    "Source Sans 3, system-ui, sans-serif"
  display: "Source Sans 3, system-ui, sans-serif"
  scale_ratio: 1.200

spacing:
  density: spacious              # +25% over default

motion:
  duration_base: 300ms           # slower than default — reduces anxiety
  reduce_motion: aggressive       # disable parallax, autoplay, etc.

shadow: minimal                  # 1-2px only
border:
  radius_md: 12px                # softer than default

forbidden:
  - red as accent (alarm coding)
  - autoplay video / sound
  - dense data tables in flow (relegate to detail panel)
```

### `enterprise-sober`

```yaml
mood: >
  A power user lands on the screen and immediately scans for the data they
  need. No marketing, no delight, no decorative surfaces. Every pixel is
  load-bearing.

palette:
  background:        "#F5F6F8"
  surface:           "#FFFFFF"
  text_primary:      "#1A1F2E"
  text_secondary:    "#5C6680"
  accent_primary:    "#1E40AF"   # workhorse blue
  border:            "#D5D8E0"

typography:
  body: "Inter, system-ui, sans-serif"
  mono: "JetBrains Mono, monospace"

spacing:
  density: compact               # data-dense

motion:
  duration_base: 120ms           # snappy
  reduce_motion: respect

forbidden:
  - hero illustrations
  - large-radius cards (>8px)
  - decorative gradients
  - icon-only labels (always pair with text)
```

> Other presets follow the same schema. Full files: `references/aesthetics/<preset-id>.yml` (auto-generated by `/ds-frontend --mode=design --aesthetic=<id>`).

---

## How `/ds-frontend` Uses Presets

```bash
/ds-frontend --mode=design --aesthetic=warm-trust
# → tokens.json populated from preset
# → motion + shadow + radius variables wired
# → forbidden list emitted as findings rules in audit mode
```

```bash
/ds-frontend --mode=audit --aesthetic=warm-trust
# → audit checks the project against the preset's `forbidden` list
# → flags any pure-black surface, gradient CTA, or >12px shadow
```

When `--aesthetic` is set, the skill:

1. Loads the preset YAML
2. Generates / updates `tokens.json` (W3C DTCG 2025.10) using preset values
3. Adds preset-specific lint rules to the audit (e.g., "no pure black under `warm-trust`")
4. References the preset in `state.data.aesthetic` so resume picks up the same vocabulary

---

## Authoring New Presets

A preset is fit for the catalog when:

- It has a **distinctive palette** (3+ tokens that are not in any other preset)
- It has a **named mood** that disambiguates from siblings
- It has a **forbidden list** (negative space — what NOT to do)
- It has a **typography pair** (display + body) that is licensed for product use

Submit via PR: `references/aesthetics/<preset-id>.yml` + entry in this catalog table.

---

## Cross-Reference

- `rules-design-system.md` — token format spec (W3C DTCG)
- `rules-accessibility.md` — every preset must pass WCAG AA contrast checks
- `controlled-vs-innovative.md` — when to lock to a preset vs. allow exploration
