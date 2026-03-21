# Blueprint Dimension Weights

## Dimension Score Aggregation

| Dimension | Component Scopes | Aggregation |
|-----------|-----------------|-------------|
| Security & Privacy | security (60%), privacy (25%), robustness (15%) | Weighted avg, CRITICAL in any → max 40 |
| Code Quality | hygiene (40%), types (35%), simplify (25%) | Weighted avg |
| Architecture | architecture (35%), patterns (25%), cross-cutting (15%), maintainability (25%) | Weighted avg, worst-case floor: min(components) + 10 |
| Performance | performance (100%) | Direct |
| Resilience | robustness (50%), functional-completeness (50%) | Weighted avg |
| Testing | testing (100%) | Direct |
| Stack Health | stack-assessment (40%), dependency-health (40%), user-facing-defaults (20%) | Weighted avg. Non-UI project → redistribute |
| DX | dx-quality (60%), project-structure (40%) | Weighted avg |
| Documentation | doc-sync (100%) | Direct |

Overall = sum(dimension_score x dimension_weight)

## Weight Matrix by Project Type

| Dimension | cli | library | api | web | mobile | desktop | monorepo | iac | devtool | data | ml | embedded | game | extension | Default |
|-----------|-----|---------|-----|-----|--------|---------|----------|-----|---------|------|----|---------|----|-----------|---------|
| Security & Privacy | 15% | 12% | 22% | 18% | 20% | 15% | 18% | 20% | 12% | 18% | 15% | 12% | 10% | 15% | 18% |
| Code Quality | 15% | 18% | 12% | 14% | 14% | 15% | 14% | 10% | 18% | 14% | 12% | 18% | 12% | 16% | 14% |
| Architecture | 10% | 16% | 14% | 14% | 14% | 12% | 18% | 8% | 14% | 12% | 10% | 10% | 14% | 12% | 14% |
| Performance | 8% | 8% | 14% | 12% | 14% | 12% | 10% | 5% | 8% | 16% | 18% | 20% | 22% | 8% | 10% |
| Resilience | 12% | 8% | 12% | 10% | 12% | 14% | 10% | 15% | 10% | 14% | 12% | 18% | 10% | 10% | 10% |
| Testing | 10% | 16% | 10% | 10% | 8% | 10% | 10% | 12% | 14% | 10% | 15% | 10% | 8% | 14% | 10% |
| Stack Health | 8% | 8% | 6% | 8% | 8% | 8% | 8% | 10% | 10% | 6% | 8% | 5% | 8% | 10% | 10% |
| DX | 12% | 8% | 5% | 7% | 5% | 7% | 7% | 12% | 8% | 5% | 5% | 4% | 8% | 8% | 7% |
| Documentation | 10% | 6% | 5% | 7% | 5% | 7% | 5% | 8% | 6% | 5% | 5% | 3% | 8% | 7% | 7% |

## Modifiers

- Sensitive data: Security & Privacy +10%, others decrease proportionally
- Enterprise quality: Testing +5%, Architecture +3%, others decrease proportionally
- Prototype quality: All dimensions equal weight (11.1% each)

## Ideal Metrics by Project Type

| Type | Coupling | Cohesion | Complexity | Coverage |
|------|----------|----------|------------|----------|
| cli | <40% | >75% | <10 | 70%+ |
| library | <30% | >80% | <8 | 85%+ |
| api | <50% | >70% | <12 | 80%+ |
| web | <60% | >65% | <15 | 70%+ |
| mobile | <55% | >65% | <12 | 65%+ |
| desktop | <50% | >70% | <12 | 70%+ |
| monorepo | <35% | >70% | <12 | 75%+ |
| iac | <45% | >70% | <10 | 60%+ |
| devtool | <35% | >75% | <10 | 80%+ |
| data | <45% | >70% | <12 | 70%+ |
| ml | <50% | >65% | <15 | 60%+ |
| embedded | <40% | >80% | <8 | 75%+ |
| game | <55% | >60% | <15 | 50%+ |
| extension | <40% | >75% | <10 | 70%+ |

Adjustments: prototype 30% relaxed, mvp 15% relaxed, production standard, enterprise 10% strict.

## Score Calibration Checks

| Check | Expected | Action if Failed |
|-------|----------|-----------------|
| Overall range | 20-95 for real projects | Re-examine — likely miscalculation |
| No dimension at 100 | Unless 0 findings in that scope | Suspicious for large codebases |
| CRITICAL consistency | Any CRITICAL → overall < 80 | Weights are wrong |
| Delta sanity | Score change between runs < 30 per dimension | Major refactor or scoring drift |
| Cross-dimension coherence | High architecture + Low code quality = suspicious | Flag if gap > 40 points |

## Status Thresholds

- ≥ ideal target → OK
- within 15 points of ideal → WARN
- > 15 points below ideal → ALERT
