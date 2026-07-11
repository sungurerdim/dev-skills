# dev-skills v4 — Kapsam Netliği + Standalone + AI-Legibility Programı

**Durum:** planlandı, onaylandı — uygulama ayrı oturum(lar)da.
**Plan tarihi:** 2026-07-11 · **Baseline:** 28 SKILL.md = 8.545 satır, SKILL-SPEC.md = 1.883 satır, 87 referans dosyası.
**Önceki ledger:** v2 planı tamamlanmıştı (bkz. commit geçmişi + CLAUDE.md "v2 Invariants"); bu dosya onun yerine geçti.

## Amaç (Goal)

dev-skills'i eksiksiz bir production-grade boyut taksonomisine oturtmak:

1. Sahipsiz kalite/ürün boyutu sıfır — her boyutun tek ve net sahibi olan skill/scope var.
2. ds-ship raporu **kapsam muhasebesi** yapar: hangi boyutlar denetlendi, hangileri sahipsiz/atlandı.
3. Her skill (orkestratörler hariç) **standalone** çalışır; orkestratörler eldeki skill'leri en efektif şekilde kullanır, olmayanda zarif düşüş yapar.
4. Her skill **AI-legible**: token-verimli, tek yorumlu, düşük kabiliyetli model/agent'ın bile sapmadan yürütebileceği netlikte.
5. **İdeal yapı dokümanlara normatif tasarım kuralı olarak yansır** — SKILL-SPEC SSOT; gelecekte eklenecek her skill/scope bu kurallara tabidir (boyut sahipliği beyanı zorunlu, sahipsiz boyut bırakmak spec ihlali).

**Scope (in):** SKILL-SPEC.md, CLAUDE.md, README.md, 28 SKILL.md + ilgili `references/*.md`, `.claude/commands/full-review.md` check güncellemeleri.
**Scope (out):** yeni skill üretimi (karar: gerekmedi), install.sh / CI mimarisi değişikliği, kaynak kod (repo Markdown-only).
**Done:** taksonomi tablosundaki her boyutun sahibi + kanıtı var · `bash scripts/check-consistency.sh` yeşil · `/full-review` yeşil · her P5 batch'inde önce/sonra token sayımı raporlanmış · ideal yapı SKILL-SPEC'te normatif kural olarak mevcut.

## Kayıtlı kararlar (2026-07-11 istişaresi)

| Karar | Seçim |
|---|---|
| Boşluk kapatma stratejisi | İdeal dağılımı sıfırdan tasarla, mevcudu ideale adapte et. Sıfırdan tasarım 28'lik aile yapısına yakınsadı → **yeni skill yok, scope genişletmesi var.** |
| Google entegrasyonu | Blueprint profili üzerinden sinyal + **Google VE Apple ekosistemi birlikte**, ilgili tüm skill'lerde eksiksiz koşullu kapsam. |
| Taksonomi yeri | SKILL-SPEC appendix (normatif SSOT) + ds-ship Phase 6 raporunda "Dimension Coverage" muhasebesi. |
| Ek görev | Standalone invariant + AI-legibility yazım standardı (aşağıda). |
| Tasarım kuralı | İdeal yapı dokümanlara normatif tasarım kuralı olarak işlenir; uygulama bittiğinde kural yaşamaya devam eder. |

## Mevcut durum tespiti (2026-07-11 taraması — Explore ajanı, dosya:satır kanıtlı)

- **FULL (13):** UI/UX (ds-frontend), güvenlik (ds-compliance kanonik + ds-fix/ds-backend/ds-mobile/ds-devops), mahremiyet (ds-compliance kanonik), performans (ds-review --perf + ds-launch --perf-budget), rekabet/pazar (ds-benchmark + ds-productize GTM), kod sadeliği (ds-simplify + ds-review --meta-quality), veri yönetimi (ds-backend), monetizasyon (ds-productize), a11y (ds-frontend impl + ds-compliance regülatif), observability (ds-deploy + ds-backend), resilience (ds-backend + ds-deploy), i18n (ds-fix l10n fazı + ds-compliance), legal (ds-compliance + ds-docs + ds-repo).
- **PARTIAL (4):** ürün-DX (blueprint'teki "DX" boyutu katkıcı deneyimi ölçüyor, ürünün geliştirici-kullanıcısının DX'ini değil) · veri tasarrufu (ds-review/SKILL.md L103'te tek checklist satırı) · usability/onboarding (heuristik denetim + ilk-kullanım akışı denetimi hiçbir skill'de yok) · SEO/analytics (WEB-08 rules-web.md'de, ds-launch L256 tek satır, ds-repo topics, ds-productize funnel — dağınık, sahipsiz).
- **NONE (4):** Google/Apple ekosistem entegrasyonu (repoda "Google" geçen 66 dosyanın tamamı Play Store/SEO bağlamı; Sign-In/Drive/Calendar/Gmail API denetimi yok) · API referans kalitesi (OpenAPI spec tamlığı, SDK ergonomisi, örnek kalitesi hiçbir skill'de denetlenmiyor) · deprecation yönetimi (sunset timeline, migration guide üretimi yok) · breaking-change yönetimi (semver/schema/contract kırılması tespiti yok).
- **Nokta eksik:** ToS/EULA şablonu üretilmiyor (Privacy Policy şablonu ds-docs L191-198'de var).
- **ds-ship:** yapısal olarak tam — 27 skill'de `Receives: ds-ship → Phase N` hattı mevcut; körlük skill katmanındaki sahipsiz boyutlarda ve raporun bunu gösterememesinde.

## İdeal taksonomi (SKILL-SPEC appendix'ine girecek SSOT — taslak)

Katmanlar: A Ürün & Pazar · B Mühendislik · C Güven & Uyum · D Operasyon · E Süreç (taşıyıcı, boyut değil).

| # | Boyut | Sahip skill (scope) | Bu programdaki değişiklik |
|---|---|---|---|
| A1 | Pazar konumlandırma & rekabet avantajı | ds-benchmark + ds-productize (GTM) | — (etiketleme) |
| A2 | Monetizasyon (pricing/billing/entitlements) | ds-productize | — |
| A3 | Analytics/telemetry | ds-productize (funnel, privacy-first) + ds-deploy (ops) | sahiplik netleşir |
| A4 | Keşfedilebilirlik (SEO + ASO + repo topics) | **ds-launch (tek sahip)** | web yoluna SEO fazı eklenir |
| A5 | Usability / onboarding / sezgisellik | **ds-frontend (yeni `ux` scope)** | heuristik denetim + ilk-kullanım akışı |
| A6 | UI görsel kalite & tutarlılık | ds-frontend | — |
| A7 | Erişilebilirlik (a11y) | ds-frontend (impl) + ds-compliance (regülatif) | — |
| A8 | i18n/l10n | ds-fix (mekanik) + ds-compliance (kural) | — |
| A9 | Ekosistem entegrasyonu (Google + Apple) | **blueprint sinyali + koşullu kurallar** (ds-backend, ds-mobile, ds-compliance, ds-launch, ds-frontend) | yeni — aşağıda tasarım |
| A10 | API referans kalitesi (OpenAPI/SDK/örnekler) | **ds-docs (API doc completeness)** + ds-backend (OpenAPI spec) | yeni |
| B1 | Kod kalitesi & kod sadeliği | ds-review, ds-fix, ds-simplify, ds-quality | — |
| B2 | Mimari sağlık | ds-blueprint + ds-review --strategic | — |
| B3 | Test & doğrulama | ds-test | — |
| B4 | DX — katkıcı | ds-blueprint (dx dimension) + ds-repo | — |
| B5 | DX — ürün (devtool/API ürünlerde) | **ds-backend (API ergonomisi) + ds-docs (getting-started)** | mevcut kurallar boyut olarak etiketlenir + docs'a onboarding-eğrisi kontrolü |
| B6 | Dokümantasyon | ds-docs | — |
| C1 | Güvenlik | ds-compliance (kanonik) + ds-fix/ds-backend/ds-mobile/ds-devops | — |
| C2 | Mahremiyet & veri koruma | ds-compliance (kanonik) | — |
| C3 | Legal (ToS/EULA, lisans, regülasyon) | ds-compliance + ds-docs (şablonlar) + ds-repo (lisans) | **ds-docs'a ToS/EULA şablonu** |
| C4 | Tedarik zinciri / bağımlılıklar | ds-deps | — |
| C5 | Deprecation yönetimi (sunset/migration guide) | ds-docs (deprecation notice) + ds-repo (release notes) | yeni |
| D1 | Performans & verimlilik | ds-review --perf + ds-launch --perf-budget + ds-tune | — |
| D2 | Kaynak ekonomisi (payload/bandwidth/storage) | **ds-review --perf (yeni grup)** + ds-deploy --cost (infra-$) | tek satır → ayrı denetim grubu |
| D3 | Resilience/reliability (retry/DR/backup) | ds-backend + ds-deploy | — |
| D4 | Observability/monitoring | ds-deploy + ds-backend | — |
| D5 | Veri yönetimi (schema/migration/retention) | ds-backend | — |
| D6 | CI/CD & release engineering | ds-devops + ds-launch | — |
| D7 | Deploy/infra & incident response | ds-deploy | — |
| D8 | Repo governance | ds-repo | — |
| D9 | Breaking-change yönetimi (semver/schema/contract) | ds-deps (semver analizi) + ds-review (API kontrat kırılması) | yeni |
| E | Süreç taşıyıcıları (boyut değil) | ds-ship, ds-pipeline, ds-commit, ds-pr, ds-issue, ds-init, ds-solve, ds-tune, ds-research, ds-brief | taksonomide "carrier" olarak işaretlenir |

## Ekosistem entegrasyonu tasarımı (A9)

- **Blueprint profili:** `Integrations: google-workspace | apple-ecosystem | none` alanı; otomatik tespit sinyalleri: `google_sign_in`, `googleapis`, GIS/GSI script, `Sign in with Apple` entitlement, `StoreKit`, `CloudKit`, `AuthenticationServices` vb. (tespit kuralları ds-blueprint `references/detection.md`'ye).
- **Koşullu kural blokları** (sinyal aktifken devrede, değilken sıfır gürültü):
  - ds-backend: OAuth scope minimizasyonu, incremental authorization, Google verification süreci + Limited Use, API quota/backoff, refresh-token güvenliği; Apple: Sign in with Apple token doğrulama, private relay e-posta işleme.
  - ds-mobile: "üçüncü taraf login varsa Sign in with Apple zorunlu" (App Store Review 4.8), entitlements doğruluğu, Play `google-services.json` hijyeni.
  - ds-compliance: Google API Limited Use policy, store data-disclosure etiketleri (Data Safety / Privacy Nutrition Labels) ↔ gerçek API kullanımı tutarlılığı.
  - ds-launch: store gereklilikleri + OAuth consent screen üretim onayı launch-blocker olarak.
  - ds-frontend: resmi buton/akış standartları (Google Identity branding, Apple HIG Sign-in).
- **ds-ship:** Phase 0'da Integrations sinyalini okur, ilgili skill'lerin koşullu bloklarını sıralamaya not eder; Phase 6 raporunda A9 kapsam satırı.

## v4 çapraz invariantlar (SKILL-SPEC'e normatif olarak girecek)

1. **Standalone Invariant:** Orkestratör olmayan her skill, tek başına yüklüyken eksiksiz çalışır. Skill'ler arası her referans "advisory handoff" kalıbındadır: hedef skill mevcut → delege et; mevcut değil → (a) asgari inline kontrolü kendisi yapar VEYA (b) açık boşluk notu düşer — asla hard-fail, asla sessiz atlama. (Mevcut emsal: ds-ship "Delegated skill unavailable → surface gap".) Orkestratörler (ds-ship, ds-pipeline) eldeki skill'leri en efektif sırayla kullanır; eksik skill'i raporda `## Missing skills` altında gösterir.
2. **AI-Legibility Yazım Standardı:** (a) tek yorumlu emir cümleleri; (b) kavram başına tek terim — eş anlamlı kayması yasak; (c) tablo > düz yazı; (d) her fazda açık girdi/çıktı sözleşmesi; (e) örtük bağlam bağımlılığı yasak; (f) belirsiz nicelik/koşul yasak ("uygunsa" değil — koşulu yaz); (g) düşük kabiliyetli modelin sapabileceği her noktada açık karar kuralı (if/then tablosu); (h) iş kalitesini koruyarak/artırarak ölçülür token azaltımı — her rewrite'ta önce/sonra token sayımı raporu.
3. **Boyut Sahipliği Tasarım Kuralı:** Her yeni skill/scope, taksonomideki hangi boyut(lar)ı sahiplendiğini SKILL.md'de beyan eder; hiçbir boyut sahipsiz bırakılamaz; iki skill aynı boyutun aynı yüzeyini sahiplenemez (overlap = spec ihlali; emsal: ds-mobile ↔ ds-compliance exclusivity). Bu kural, program bittikten sonra da yaşayan tasarım kuralıdır.

---

## Phase 0.5: Baseline ölçümü (dönüşüm öncesi)

Dönüşüme başlamadan önce mevcut durumun somut ölçümü — Phase 5 batch raporları ve Done kriterleri bu baseline'e karşı doğrulanır. Her metrik `ds/audit/v4-baseline.json`'a yazılır.

- [ ] SKILL.md satır sayımı (28 dosya × ayrı satır + toplam) — verify: toplam 8.545 ± %1
- [ ] Referans dosyası satır sayımı (87 dosya × toplam) — verify: `wc -l` sonucu
- [ ] Token tahmini (içerik karakter sayısı / 4, YAML frontmatter hariç): her SKILL.md için ayrı + toplam. Standart: `wc -c` çıktısından `---...---` blokları çıkarılıp kalan / 4.
- [ ] SKILL-SPEC size-target audit: her skill'in mevcut satır sayısı × sınıfına göre tavan (orchestrator ≤350, multi-mode ≤350, single-mode ≤240, atomic ≤220) → tavan aşan skill'lerin listesi — verify: tablo mevcut
- [ ] `bash scripts/check-consistency.sh` çıkış kodu + `/full-review` skoru (8 kategori) — verify: her ikisi de kaydedildi
- [ ] İş kuralı sayımı: her SKILL.md'de `verify|check|ensure|enforce|MUST|kural|doğrula|denetle` kalıplarına uyan satır sayısı (yaklaşık kural sayacı) — verify: becer başına sayı + toplam

Gate: `ds/audit/v4-baseline.json` yazıldı; tüm metrikler dolu; tavan aşan skill listesi çıkarıldı. Bu dosya program boyunca referans noktasıdır — değiştirilmez.

## Phase 1: Araştırma doğrulaması

- [ ] Taksonomiyi endüstri çerçevelerine karşı doğrula — `ds-research-agent` ile: Google SRE production-readiness (PRR), Nielsen usability heuristikleri (güncel hali), Apple HIG + App Store Review Guidelines (özellikle 4.8 login), Google Identity/OAuth verification + Limited Use güncel gereksinimleri, Material Design — verify: kaynaklı bulgu artefaktı (`ds/audit/` dışında, scratchpad veya `references/` altına taslak) → her taksonomi satırı için ≥1 dış kaynak teyidi veya "teyitsiz, bilinen-iyi" işareti
- [ ] Araştırmadan taksonomiye delta çıkar (eksik boyut / yanlış sahiplik / güncelliğini yitirmiş kural) — verify: delta listesi bu dosyaya işlenir → taksonomi tablosu güncel
Gate: Taksonomi tablosu araştırma teyitli ve dondurulmuş; P2 bu tabloyu SSOT alır.

## Phase 2: SKILL-SPEC v4 — ideal yapı normatif kural olur

- [ ] SKILL-SPEC.md'ye "Appendix: Dimension Coverage Map" — P1'de dondurulan taksonomi tablosu + carrier listesi — verify: appendix mevcut, tablo tam → her boyutta sahip + scope sütunu dolu
- [ ] SKILL-SPEC'e Standalone Invariant (advisory-handoff kalıbı, örnek dahil) — verify: bölüm mevcut + Cross-Tool Verification Checklist'e madde eklendi
- [ ] SKILL-SPEC'e AI-Legibility Yazım Standardı (8 kural, iyi/kötü örnek çiftleriyle) — verify: bölüm mevcut
- [ ] SKILL-SPEC'e Boyut Sahipliği Tasarım Kuralı (yeni skill/scope eklerken zorunlu beyan) — verify: §'e kural + SKILL.md şablonuna "Dimensions:" satırı eklendi
- [ ] `.claude/commands/full-review.md` checkler güncellenir: standalone, ai-legibility, dimension-ownership kategorileri — verify: yeni checkler listede → full-review v4'ü denetleyebilir
- [ ] `scripts/check-consistency.sh` v4 uzantıları: her SKILL.md'de "Dimensions:" satırı mevcut mu, beyan edilen her boyut SKILL-SPEC appendix'inde var mı, iki skill aynı boyut·scope çiftini sahipleniyor mu (overlap), cross-skill referanslar advisory-handoff kalıbında mı — verify: betik bu 4 check'i içeriyor + örnek skill'ler üzerinde çalışıyor
Gate: SKILL-SPEC self-consistent (`bash scripts/check-consistency.sh` yeşil); v4 kuralları normatif.

## Phase 3: Blueprint Integrations + ds-ship kapsam muhasebesi

- [ ] ds-blueprint: profile'a `Integrations:` alanı + `references/detection.md`'ye tespit sinyalleri — verify: alan + sinyal tablosu mevcut
- [ ] ds-blueprint: `--test-integrations=google|apple|both` flag'i — gerçek proje olmadan A9 koşullu kurallarını test edebilmek için simüle entegrasyon sinyali; sadece test amaçlı, production'da kullanılmaz — verify: flag mevcut + simüle edilen sinyalle ds-ship Phase 0'da koşullu bloklar tetikleniyor
- [ ] ds-ship Phase 0: Integrations sinyalini okuma + sıralamaya yansıtma kuralı — verify: SKILL.md'de kural satırı
- [ ] ds-ship Phase 6 raporuna "Dimension Coverage" bölümü: boyut × (denetlendi / sahip-skill-atlandı / sahipsiz) tablosu; sahipsiz boyut = raporda açık uyarı — verify: rapor şablonunda bölüm mevcut
- [ ] Bu reponun kendi Blueprint Profile'ına (CLAUDE.md) `Integrations: none` satırı — verify: profil güncel
Gate: consistency script yeşil; ds-ship raporu taksonomiye referans veriyor.

## Phase 4: Scope genişletmeleri (boşluk kapatma)

- [ ] **Pre-expansion size audit:** genişletilecek her skill'in mevcut satır × sınıf tavanı × tahmini genişleme satırı tablosu. Tavan aşma riski olan skill'ler için önce içerik `references/`'a taşınır, sonra yeni scope eklenir. Verify: tablo bu dosyada + hiçbir genişletilmiş skill tavanı aşmıyor.
- [ ] ds-frontend: yeni `ux` scope — Nielsen-tipi heuristik denetim, onboarding/ilk-kullanım akışı, mevcut `states` scope'uyla bütünleşme; Dimensions beyanı A5 — verify: scope + INVOKE tablosu + faz güncel
- [ ] ds-launch: web yoluna SEO fazı (meta/OG, sitemap, robots, canonical, structured data) — A4 tek sahip; ds-compliance WEB-08 ile overlap-skip kuralı — verify: faz mevcut + overlap kuralı iki tarafta tutarlı
- [ ] ds-review: `--perf` içine "Resource Economy" grubu (payload, compression, cache-hit, storage growth, veri tasarrufu) — D2 — verify: grup mevcut
- [ ] ds-docs: ToS/EULA şablonu (legal set'e) + ürün-DX getting-started/onboarding-eğrisi kontrolü — C3/B5 — verify: şablon + kontrol maddeleri mevcut
- [ ] ds-backend: API scope'una "Product DX" etiketi + A9 Google/Apple koşullu kural bloğu — verify: blok mevcut, sinyal koşulu açık
- [ ] ds-mobile: A9 koşullu kuralları (Sign in with Apple zorunluluğu, entitlements, google-services hijyeni) — verify: kurallar mevcut
- [ ] ds-compliance: A9 koşullu kuralları (Limited Use, data-disclosure ↔ API kullanımı tutarlılığı) — verify: kurallar mevcut
- [ ] ds-frontend + ds-launch: A9 koşullu kuralları (branding/HIG buton standartları; consent-screen launch-blocker) — verify: kurallar mevcut
- [ ] ds-productize: A3 analytics sahipliğinin etiketlenmesi (funnel = ds-productize, ops = ds-deploy) — verify: Delegation bloğu güncel
Gate: Her genişletme SKILL-SPEC v4 formatına uygun (Dimensions beyanı dahil); consistency script yeşil; PARTIAL/NONE kalmadı.

## Phase 5: 28 skill'e standalone + AI-legibility geçişi

**Rewrite metodolojisi — her SKILL.md için uygulanacak checklist:**

1. [ ] Prose → tablo: 3+ maddeli kural listesi varsa tabloya çevir.
2. [ ] Imperative mood: her adım fiille başlasın ("Search", "Verify", "Skip").
3. [ ] De-duplicate: aynı kural Phase body + Gate + Output'ta tekrarlanıyorsa sadece en ilgili konumda tut, diğerlerinde cross-ref.
4. [ ] Gate compactness: her gate ≤2 cümle (pass condition + If-fails arm).
5. [ ] Reference externalization: bir domain'de ≥10 kural varsa `references/`'a taşı; SKILL.md'den link ver.
6. [ ] Positive framing: "Don't/never/do not" kalıplarını pozitif aksiyon ifadesine çevir.
7. [ ] Token ölçümü: `wc -c` çıktısından YAML frontmatter çıkar, kalan / 4 = token tahmini. Batch başında/batch sonunda ölç.
8. [ ] Before/after diff: her batch için toplu token delta tablosu (beceri × önce × sonra × delta%).
9. [ ] Kural koruma: `verify|check|ensure|enforce|MUST|kural|doğrula|denetle` kalıplarına uyan satır sayısı düşmemiş olmalı — düştüyse gerekçe yazılı.
10. [ ] Dimension declaration: her SKILL.md'de `Dimensions:` satırı mevcut + taksonomiyle eşleşiyor.

**Token sayım standardı:** `(wc -c <SKILL.md içeriği, frontmatter hariç) / 4` — tokenizer'dan bağımsız, işletim sistemi agnostik yaklaşık token sayısı. Batch raporunda `önce → sonra (delta%)` formatı.

Batch'ler ~5 skill; her batch bağımsız doğrulanır ve önce/sonra token sayımı raporlanır. Sıra (büyükten küçüğe — en yüksek kazanç önce):

- [ ] Batch 1: ds-blueprint, ds-ship, ds-review, ds-test, ds-backend — verify: full-review ilgili kategorileri + token raporu → belirsiz ifade sıfır, advisory-handoff kalıbı uygulanmış
- [ ] Batch 2: ds-solve, ds-launch, ds-deps, ds-repo, ds-docs — verify: aynı
- [ ] Batch 3: ds-simplify, ds-mobile, ds-frontend, ds-compliance, ds-tune — verify: aynı
- [ ] Batch 4: ds-fix, ds-commit, ds-pr, ds-deploy, ds-init — verify: aynı
- [ ] Batch 5: ds-devops, ds-benchmark, ds-quality, ds-productize, ds-issue — verify: aynı
- [ ] Batch 6: ds-research, ds-brief, ds-pipeline + `agents/ds-research-agent` — verify: aynı
- [ ] Referans dosyaları taraması (87 dosya): sadece SKILL.md değişikliklerinden etkilenenler + bariz redundancy — verify: değişen her referansın tüketicileri grep'le doğrulanır
Gate: 28/28 skill v4-uyumlu; toplam token delta raporu; hiçbir batch'te iş kuralı kaybı yok (önce/sonra kural sayımı — kural düşüşü varsa gerekçesi yazılı).

## Phase 6: Senkron + reconcile

- [ ] CLAUDE.md: family map'e boyut sütunu/referansı + v4 invariants bölümü — verify: CLAUDE.md ↔ SKILL-SPEC tutarlı
- [ ] README.md: kapsam iddiası güncellenir (taksonomi linki) — verify: içerik güncel
- [ ] Tam `/full-review` koşusu — verify: 8+ kategori yeşil → sıfır CRITICAL/HIGH bulgu
- [ ] `bash scripts/check-consistency.sh` — verify: exit 0
- [ ] SKILL-SPEC appendix'e "Taxonomy Amendment Process" bölümü: yeni bir boyut ekleme prosedürü — (1) issue/PR ile teklif: boyut adı, katmanı (A/B/C/D), sahip skill, ≥1 endüstri çerçevesine referans; (2) gate: bu yüzeyi mevcut bir skill kapsamıyor; (3) gate: sahip skill'in tavan kapasitesi var; (4) merge sonrası: SKILL.md'ye Dimensions satırı, SKILL-SPEC appendix'e satır, ds-ship Phase 6 raporuna ek — verify: bölüm mevcut + prosedür adımları tam
- [ ] Reconcile: bu dosyadaki tüm maddeler [x]; kalan açık madde varsa gerekçeli — verify: ledger tam
- [ ] Commit(ler): conventional commits, faz başına atomik — verify: git log temiz
Gate: Done kriterlerinin tamamı (Amaç bölümü) sağlandı; program kapanışında bu tasks.md silinir (ideal yapı artık SKILL-SPEC'te yaşar).

## Oturum açılış notu

Yeni oturumda: bu dosyayı baştan sona oku → ilk açık ([ ]) maddeden devam et → Phase gate'lerini atlama → her batch/faz sonunda bu dosyayı güncelle. Taksonomi tablosu P1 gate'inden sonra SSOT'tur; P2'den itibaren SKILL-SPEC appendix'i SSOT olur ve bu dosyadaki kopya güncellenmez (drift önlemi).
