# Quality Level Definitions

## Prototype

All thresholds relaxed 30%.

- **Scopes:** Core checks only (security, hygiene)
- **Skip:** Architecture, docs, ai-hygiene
- **Focus:** Get it working
- **Weight:** All dimensions equal (11.1% each)

## MVP

All thresholds relaxed 15%.

- **Scopes:** Security + quality + performance
- **Skip:** ai-hygiene
- **Focus:** Ship fast with basics covered
- **Weight:** Standard weights apply

## Production

Standard thresholds.

- **Scopes:** All 9 dimensions
- **Checks:** Full scope coverage
- **Focus:** Full quality gates, OWASP security scan
- **Weight:** Standard weights apply

## Enterprise

All thresholds strict +10%.

- **Scopes:** All 9 dimensions + compliance
- **Checks:** Full scope with audit trail
- **Focus:** Regulatory compliance, audit trail required
- **Weight:** Testing +5%, Architecture +3%, others decrease proportionally
- **Modifiers:** Sensitive data → Security & Privacy +10%
