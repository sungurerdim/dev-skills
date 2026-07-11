# Contract: Dimension Declaration

**Purpose**: Define the format and validation rules for a SKILL.md's `Dimensions:` declaration.

**Location**: Each `ds-<name>/SKILL.md`, typically in the Contract section or directly after the title block.

**Format**:
```markdown
**Dimensions:** A6 (UI), A7 (implementation), A5 (new ux scope)
```

The line starts with `**Dimensions:**` followed by a comma-separated list of dimension IDs. Each dimension ID may be followed by a parenthesized scope qualifier: `A5 (new ux scope)`. Scope qualifiers are optional but recommended when the skill owns only a specific surface of a multi-owner dimension.

**Validation rules**:

| Rule | Check | Failure |
|------|-------|---------|
| Presence | Every SKILL.md MUST contain a `Dimensions:` line | `check-consistency.sh` exits non-zero |
| Taxonomy membership | Each declared dimension ID MUST exist in the SKILL-SPEC appendix | Script reports unknown dimension |
| Surface overlap | No two skills MAY declare the same dimension·scope pair | Script reports conflict with owning-skill names |
| Scope uniqueness | A single skill MUST NOT declare the same dimension ID twice | Script reports duplicate within skill |
| Layer E exclusion | Process carriers (layer E) MUST NOT be declared as dimensions | Script rejects E-layer IDs |

**Consumers**: `check-consistency.sh` (v4 extension), `/full-review` (v4 category), `/ds-ship` Phase 6 (dimension coverage table).

**Examples**:

Valid:
```
**Dimensions:** A6 (UI), A7 (implementation), A5 (new ux scope)
```
```
**Dimensions:** C1 (canonical), C2 (canonical), C3 (regulatory), A7 (regulatory)
```

Invalid (would fail check-consistency.sh):
```
**Dimensions:** E1, E2                # E-layer IDs don't exist (carriers only)
```
```
**Dimensions:** A99                   # Dimension A99 doesn't exist in taxonomy
```
```
**Dimensions:**                       # Empty declaration
```
