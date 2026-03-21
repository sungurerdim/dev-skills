# ds-research

Multi-source research with CRAAP+ reliability scoring and tiered synthesis.

## Install

See the [main README](../README.md#install) for install instructions per AI tool.

## Use

Run `/ds-research`, or ask to research a topic.

## Flow

1. Choose depth: Quick (T1-T2), Standard (T1-T4), or Deep (all tiers)
2. Parallel web search across multiple source categories
3. Score each source using CRAAP+ methodology (Currency, Relevance, Authority, Accuracy, Purpose)
4. Synthesize findings with citation and contradiction resolution
5. Output with confidence level and recommendation

## Features

- **CRAAP+ scoring** — 5-dimension reliability assessment for every source
- **Source tiers** — T1 (official docs) through T6 (unverified), auto-classified
- **Saturation gate** — stops searching when sources converge
- **Deep mode** — iterative deepening with backward/forward snowballing
- **Dependency mode** — registry lookups for version/CVE checking
- **Triangulation** — no claim without 2+ independent sources
