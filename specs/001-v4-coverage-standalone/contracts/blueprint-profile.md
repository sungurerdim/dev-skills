# Contract: Blueprint Profile

**Purpose**: Define the format for the project metadata block consumed by all analyzing skills.

**Location**: Between `## Blueprint Profile` and `## End Blueprint Profile` markers in the AI instruction file (CLAUDE.md).

**Format** (max 25 lines):

```markdown
## Blueprint Profile

Type: {library|cli|web|api|mobile|monorepo}
Stack: {tech stack description}
Target: {production|prototype|enterprise}
Priorities: {comma-separated quality priorities}
Constraints: {comma-separated constraints}
Data: {data types handled, if any}
Regulations: {applicable regulations, if any}
Audience: {target audience}
Deploy: {deployment target}
Integrations: {google-workspace | apple-ecosystem | none}
Current Scores: {dimension → score map, optional}
Ideal Metrics: {metric → target map, optional}

## End Blueprint Profile
```

**v4 addition**: The `Integrations:` field is new — values are `google-workspace`, `apple-ecosystem`, or `none`. This triggers conditional rule blocks in 5 A9-owning skills.

**Consumer rules**:

1. All analyzing skills MUST check for `## Blueprint Profile` before running their own detection
2. If present, skills MUST use profile values to skip redundant detection and calibrate severity/thresholds
3. If absent, skills MUST run their own complete detection and analysis
4. Only ds-blueprint MAY write or modify the Blueprint Profile. All other skills MUST treat it as read-only.
5. The `--test-integrations=google|apple|both` flag on ds-blueprint simulates integration signals for testing. When active, ds-blueprint writes the simulated value into the `Integrations:` field.

**Consumers**: All 28 skills (directly or via findings file).
