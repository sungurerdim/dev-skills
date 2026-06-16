# dev-skills v2 — Implementation Tasks

Plan: Meta-Quality + Overlap Fix + Error Ownership + CCO Heritage. Onaylı plan: bkz. transcript.

## Numbering decision

Plan içinde `W9` (Findings-SSOT) ve `W10` (Error Ownership) olarak adlandırılmıştı, ancak `SKILL-SPEC.md §3` zaten `W9: State Hygiene` tanımlıyor ve 26 SKILL.md `W9: ds/audit/*.json updated` referansı içeriyor. Çakışmayı önlemek için yeni gate'ler aşağıdaki numaralarla eklenir:
- **W10 — Findings-SSOT Gate** (downstream skiller `ds/audit/findings.md`'yi runtime'da doğrular)
- **W11 — Error Ownership Gate** (tespit edilen hata pas geçilemez)

## Phase 1: SKILL-SPEC.md ✓ TAMAM
- [x] §3'e W10 Findings-SSOT Gate
- [x] §3'e W11 Error Ownership Gate
- [x] §2'ye **Trigger Discipline** mini-kuralı (ÇAĞIRIR / ÇAĞIRMAZ)
- [x] §2'ye **Interaction Discipline** + **All-Affordance Rule**
- [x] §8 W1-W8 → W1-W11; §9 Cross-Tool Verification Checklist 4 yeni madde
- [x] §1 Section Order tablosu Triggers + Quality Gates güncel

## Phase 2: 26 SKILL.md broadcast ✓ TAMAM
- [x] 26/26 dosyada Contract'a Pre-existing/out-of-scope errors satırı
- [x] 26/26 dosyada Quality Gates one-liner'da W10 + W11 (consumer / SSOT-producer / orchestrator varyantları)

## Phase 3: Overlap düzeltme ✓ TAMAM
- [x] ds-blueprint W10 SSOT runtime enforcement Contract'ta
- [x] ds-ship milestone gates + 2-onay cascade + ÇAĞIRIR/ÇAĞIRMAZ + ds-deploy/ds-launch routing
- [x] ds-fix --skip-if-clean flag
- [x] ds-compliance: mobile-project overlap-skip runtime enforce
- [x] ds-solve backtrack-logic.md zaten var (link health OK)

## Phase 4: Trigger discipline ✓ TAMAM
- [x] 26/26 SKILL.md'de ÇAĞIRIR/ÇAĞIRMAZ tablosu (3-4 satır her biri)

## Phase 5: ds-review --meta-quality ✓ TAMAM
- [x] --meta-quality, --meta-scope, --criteria-fit, --suggest-paths flags
- [x] Phase 3a (Analyze-Principles), 3b (Criteria-Fit), 4a (Suggest-Paths)
- [x] meta-quality-scopes.md (yeni, 5 scope + 4 alias)
- [x] criteria-fit.md (yeni, 9 proje tipi baseline)
- [x] path-proposals.md (yeni, Path A/B/C template per scope)
- [x] principles.md §10 anti-overengineering, §11 dedup, §12 reason discipline

## Phase 6: CCO yüksek-etki ✓ TAMAM
- [x] B.1 Parallel-track batching (ds-blueprint Phase 2.5, ds-review Phase 2)
- [x] B.2 CRITICAL escalation (ds-fix, ds-solve, ds-review)
- [x] B.3 Anti-overengineering 3-gate (principles.md §10)
- [x] B.4 Penalty formula + cap (weights.md)
- [x] B.5 filters_applied audit field (detection.md, 3 occurrence)
- [x] B.6 Cross-scope dedup (principles.md §11)
- [x] B.7 Cross-dimension coherence (weights.md)
- [x] B.8 Educational output triple (ds-fix Quality Gates)
- [x] B.9 Reason discipline (principles.md §12)

## Phase 7: CCO düşük-etki ✓ TAMAM
- [x] B.10 Branch-protection-aware merge (ds-pr Phase 6, gh api detection)
- [x] B.11 --memory-cleanup flag + Phase 8.5 (ds-blueprint)
- [x] B.12 .claude/commands/full-review.md (8 kategori × 56 check)

## Phase 8: Verification ✓ TAMAM
- [x] 26/26 SKILL.md'de W10 + W11
- [x] 26/26 SKILL.md'de "Pre-existing" Contract satırı
- [x] 26/26 SKILL.md'de ÇAĞIRIR/ÇAĞIRMAZ tablosu
- [x] 3 yeni reference dosya mevcut (meta-quality-scopes, criteria-fit, path-proposals)
- [x] CCO B.1-B.12 her unsur target dosyada presence check PASS
- [x] /full-review.md slash command mevcut

## Toplam değişiklik

- 30 dosya modify (SKILL-SPEC + 26 SKILL.md + 3 reference)
- 4 yeni dosya (3 ds-review reference + .claude/commands/full-review.md)

**Status: Plan tamamı uygulandı.**
