# Rules: CSS Design System

## DS-COLORS [INFO] Gestalt Color Variables

Each information type has a distinct color for instant visual parsing.

```css
:root {
  /* Role names, skill labels, section titles (darkest = most important) */
  --primary: #1e293b;
  --primary-mid: #334155;

  /* Timeline dots, summary border, section accent line */
  --accent: #1e4d8c;
  --accent-soft: #bdd0e8;
  --accent-bg: #e2ecf6;

  /* Date badges - consistent "when" signal across Experience + Education */
  --date-bg: #e2ecf6;
  --date-border: #b3c9e2;
  --date-text: #1a4273;

  /* Company name - "where" signal (slate, italic) */
  --org-color: #475569;

  /* Text hierarchy */
  --text: #111827;
  --text-secondary: #374151;
  --text-muted: #6b7280;

  /* Backgrounds and borders */
  --border: #d1d5db;
  --border-light: #e5e7eb;
  --bg-subtle: #f9fafb;
  --summary-bg: #f8fafc;
  --white: #ffffff;
  --timeline: #cbd5e1;
}
```

## DS-TYPO [INFO] Typography System

```
Font stack: Plus Jakarta Sans (400, 500, 600, 700, 800) + IBM Plex Mono (400, 500)
Google Fonts URL: https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap

Screen values:
  Body:           9.5pt / line-height 1.4
  Name (h1):      24pt / weight 800 / letter-spacing -0.5pt
  Subtitle:       10.5pt / weight 600 / accent color / uppercase / 2.5pt spacing
  Section titles: 8.5pt / weight 800 / uppercase / 2pt letter-spacing
  Role names:     9.5pt / weight 700 / primary color
  Dates:          7pt / IBM Plex Mono / weight 500 / blue badge
  Company:        8.5pt / weight 500 / italic / slate color
  Bullets:        9pt / text-secondary color / line-height 1.45
  Skill tags:     8pt / weight 600 / primary color on neutral gray bg
  Skill labels:   8pt / weight 700 / uppercase / 0.5pt spacing / primary color

Print values (compressed for A4):
  Body:           9pt
  Name:           21pt
  Subtitle:       9.5pt
  Section gap:    5pt (was 9pt)
  Entry gap:      5pt (was 7pt)
  Bullet font:    8.5pt / line-height 1.35
  Skill tags:     7.5pt
  Date badges:    6.5pt
  Contact items:  7.5pt
```

## DS-SPACING [INFO] Spacing System

```
Screen:
  Page padding: 11mm 14mm 8mm 14mm
  Section margin-bottom: 9pt
  Experience entry margin-bottom: 7pt
  Bullet margin-bottom: 1.5pt
  Skills section gap: 5pt
  Skill tags gap: 3pt
  Timeline left padding: 14pt

Print:
  Page padding: 7mm 10mm 5mm 10mm
  Page: width 100%, margin 0 (fill printable area)
  Section margin-bottom: 5pt
  Entry margin-bottom: 5pt
  Bullet margin-bottom: 1pt
  Skills section gap: 3pt
```

## DS-VISUAL [INFO] Visual Elements

```
Header:
  Gradient line: transparent -> accent -> primary -> accent -> transparent
  Position: absolute bottom, full width, 1.5pt height

Section titles:
  Border-bottom 1.5pt solid border-light
  Accent underline overlay: 28pt wide, 1.5pt height, absolute bottom-left

Summary:
  Left border: 2.5pt solid accent
  Background: summary-bg
  Border-radius: 0 3pt 3pt 0
  Padding: 6pt 10pt (screen), 4pt 8pt (print)

Timeline:
  Vertical line: 1.5pt wide, timeline color, left 2pt
  Entry nodes: 5pt circles, accent color, 1.5pt white border + box-shadow
  Node alignment: top: 0.6em + transform: translateY(-50%)
  All roles get equal visual weight (no minor/major distinction)

Bullet dots:
  3.5pt circles, accent color, 0.65 opacity
  Alignment: top: 0.68em + transform: translateY(-50%)

Skill tags:
  Pill shape, neutral gray (border-light bg + border) - NOT accent color
  Padding: 2pt 7pt, border-radius 3pt

Date badges:
  IBM Plex Mono, date-bg + date-border + date-text
  Padding: 1.5pt 6pt, border-radius 3pt
  width: 18ch + box-sizing: content-box (all same width, based on longest date "Apr 2025 - Present")
  text-align: center
  Same style in Experience and Education (consistent "when" signal)

Contact items:
  Pill shape, neutral gray (border-light bg + border) - same as skill tags
  Hover: accent-bg + accent border + accent text

Metric highlights (inside bullets):
  <strong> tags around key Nx multipliers and named project titles only
  Style: font-weight 500, font-style italic, color #1a56a8 (brighter blue than body text)
  Keep highlights sparse - only Nx multipliers and named projects. Not descriptions or ranges.

Clickable links:
  Project URLs: <a> with target="_blank", style color:inherit + text-decoration:underline
  Header links (LinkedIn, GitHub): <a> with target="_blank"

Print auto-fit:
  .page: height 297mm, display flex, flex-direction column
  .section + .header: margin-bottom auto (space distributes evenly across page)
  .section:last-child: margin-bottom 0
  page-break-inside: avoid on .section, .exp-entry, .edu-grid
  If overflow: reduce body font (9pt -> 8.5pt -> 8pt), then padding/gaps
```
