# Blueprint Dimension Weights

## Dimension Score Aggregation

| Dimension | Component Scopes | Aggregation |
|-----------|-----------------|-------------|
| Security & Privacy | security (70%), privacy (30%) | Weighted avg, CRITICAL in any → max 40 |
| Code Quality | hygiene (30%), types (25%), simplify (20%), ai-hygiene (15%), doc-sync (10%) | Weighted avg |
| Architecture | architecture (25%), patterns (20%), contract-consistency (15%), cross-cutting (10%), maintainability (15%), ai-architecture (15%) | Weighted avg, worst-case floor: min(components) + 10 |
| Performance | performance (100%) | Direct |
| Resilience | robustness (60%), production-readiness (40%) | Weighted avg |
| Testing | testing (60%), functional-completeness (40%) | Weighted avg |
| Stack Health | stack (55%), stack-fitness (45%) | Weighted avg |
| DX | dx (65%), external-tooling (35%) | Weighted avg |
| Documentation | docs (65%), spec-alignment (35%) | Weighted avg |

Overall = sum(dimension_score x dimension_weight)

User-facing checks (i18n, a11y, responsive layout — Phase 3 "User-facing project gate") are surfaced as HIGH-severity findings directly, not as a separate weighted scope or dimension component.

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

## Penalty Formula and Caps

Dimension scoring uses an explicit penalty-based formula:

```
base_score = 100
penalty = 25 × CRITICAL_count + 10 × HIGH_count + 3 × MEDIUM_count + 1 × LOW_count
dimension_score = max(0, base_score - penalty)
```

**Per-dimension cap:** A single dimension cannot lose more than 50 points from any one penalty class. Example: 10 HIGH findings = 100 raw penalty → capped at 50 → dimension score = max(0, 100 - 50) = 50. The cap prevents a single problematic category from collapsing a dimension to 0 when other categories are healthy.

**Overall caps (already enforced):**
- Any CRITICAL anywhere → overall ≤ 40
- 3+ HIGH in any single dimension → that dimension ≤ 60
- 3+ HIGH across all dimensions → overall ≤ 60

The caps survive aggregation: the overall score is `min(weighted_sum, applicable_caps)`.

## Cross-Dimension Coherence Check

Adjacent dimensions should move together. A 40+ point gap between related dimensions usually means the baseline is wrong, not that one dimension is genuinely 40 points better than its neighbor.

**Related-dimension pairs (flag gap > 40):**

| Pair | Why correlated |
|------|----------------|
| Code Quality ↔ Architecture | Bad architecture surfaces as code-quality issues; clean code rarely comes from messy structure |
| Testing ↔ Resilience | Both reflect maturity in handling failure paths |
| Security & Privacy ↔ Resilience | Defense-in-depth and reliability share patterns |
| Stack Health ↔ DX | Outdated stack typically degrades developer experience |
| Documentation ↔ Architecture | Documented systems are usually thoughtfully designed |

When a gap > 40 is detected:

1. Re-read signals from the higher-scoring dimension (often optimistic)
2. Re-read signals from the lower-scoring dimension (often missing context)
3. Adjust whichever has weaker evidence
4. If both are well-evidenced, the gap is real — note in the dashboard under "Anomalies: {dim_a} {score_a} vs {dim_b} {score_b}, gap {n}"

## Score Calibration Checks

| Check | Expected | Action if Failed |
|-------|----------|-----------------|
| Overall range | 20-95 for real projects | Re-examine — likely miscalculation |
| No dimension at 100 | Unless 0 findings in that scope | Suspicious for large codebases |
| CRITICAL consistency | Any CRITICAL → overall < 80 | Weights are wrong |
| Delta sanity | Score change between runs < 30 per dimension | Major refactor or scoring drift |
| Cross-dimension coherence | Related-dimension pairs (table above) within 40 points | Re-read evidence for both, adjust the one with weaker signals; persistent gap → flag as anomaly in dashboard |
| Per-dimension penalty cap | Max -50 from any single severity class | Cap kicks in automatically; record in audit field |

## Status Thresholds

- ≥ ideal target → OK
- within 15 points of ideal → WARN
- > 15 points below ideal → ALERT
