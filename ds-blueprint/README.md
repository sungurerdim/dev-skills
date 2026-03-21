# ds-blueprint

Project health system — profile-based assessment, transformation, and progress tracking.

## Install

See the [main README](../README.md#install) for install instructions per AI tool.

## Use

Run `/ds-blueprint`, or ask to assess your project health.

## Flow

1. Discovery: detect project type, stack, toolchain
2. Init: profile creation (type, quality, data, priorities, constraints)
3. Assess: 5-track parallel analysis (code quality, architecture, production, docs, audit)
4. Consolidate: dimension scoring with project-type weights
5. Plan and apply fixes
6. Update profile with new scores

## Features

- **9 health dimensions** — Security, Code Quality, Architecture, Performance, Resilience, Testing, Stack Health, DX, Documentation
- **14 project types** — with type-specific weight matrices
- **Score tracking** — delta and trend across runs
- **Auto-detected instruction file** — embeds profile in CLAUDE.md, .cursorrules, copilot-instructions.md, etc. Always in context.
- **4 quality levels** — Prototype, MVP, Production, Enterprise
