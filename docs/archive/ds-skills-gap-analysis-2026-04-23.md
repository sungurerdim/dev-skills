# ds-skills — Boşluk Analizi ve İyileştirme Planı

> **Tarih:** 2026-04-23
> **Bağlam:** Kullanıcı, projelerini fikir aşamasından OSS-ready lansmana kadar götürecek bir "production-readiness mega-audit" pipeline'ı kurmak istiyor. Mevcut 22 ds- skill'inin bu pipeline'ı ne kadar kapsadığı denetlendi. Bu doküman, denetim sonucu ortaya çıkan somut boşlukları ve her biri için ne yapılması gerektiğini listeler.
> **Hedef repo:** `dev-skills` (bu plan burada uygulanacak)
> **Bu dosyanın statüsü:** Uygulama kılavuzu — ayrı ayrı skill değişiklikleri olarak uygulanmalı.

---

## 1. Mevcut Koleksiyonun Şekli (Özet)

- **Güçlü koridor:** review / fix / pre-launch. `ds-blueprint`, `ds-review`, `ds-compliance`, `ds-mobile`, `ds-fix`, `ds-frontend` burada derin, dosya:satır hassasiyetinde örtüşen kapsama veriyor.
- **Üretici/tüketici deseni:** `ds-blueprint` `.ds-findings.md` üretir, diğerleri bunu okur ve ikinci tarama yapmaz. Bu temiz bir mimari — pipeline tasarımı bunu kırmamalı.
- **İnce koridorlar:** idea / research / spec (yalnızca `ds-research` ve `ds-blueprint --init` buralarda ayak basıyor) ve post-launch (yalnızca `ds-tune` ve `ds-analytics`).
- **Orkestratör yok:** "İdeal sırayla şu skill'leri çalıştır" diyen bir üst-düzey pipeline komutu bulunmuyor. Her skill bağımsız çağrılıyor.

---

## 2. Somut Boşluklar (öncelik sıralı)

### GAP-1 (YÜKSEK) — Production-Readiness Orkestratörü yok

**Ne eksik:** Tek bir komutla "bu proje fikir-aşamasında mı, taslak halinde mi, production-ready mi?" diye sınıflandırıp, o aşamaya uygun skill'leri doğru sırayla tetikleyecek bir **üst-pipeline skill'i** yok. Kullanıcı bugün `ds-blueprint → ds-review → ds-fix → ds-compliance → ds-repo → ds-launch` sırasını her seferinde akılda tutmak zorunda.

**Neden kritik (somut fayda):**
- Kullanıcı çok projeli (15+ aktif). "Kaldığım yeri hatırlama" zaafı var — sıra hatası ciddi zaman kaybı demek.
- Her skill'i tek tek çağırmak, skill'ler arası `.ds-findings.md` bağımlılığını atlama riski yaratıyor (blueprint çalışmadan review çağırılırsa review yeniden tespit ediyor — token israfı).
- Tüm eksiklerin tek raporda toplanması, tek karar noktası üretir. Bugün 5 ayrı skill çalıştırmak = 5 ayrı rapor = bilişsel yük.

**Öneri:** Yeni skill `ds-ship` (veya `ds-pipeline` / `ds-finalize`).

**Kapsam:**
1. **Faz 0 — Durum tespiti:** Repo'yu tara (kod var mı? spec var mı? testler var mı? CI var mı? README var mı?) → otomatik sınıflandır: `idea | spec | scaffold | implementation | review | pre-launch | launched`.
2. **Faz 1 — Planlama:** O aşamaya uygun skill sırasını tablolaştır, kullanıcıya onaylat ("şu 7 skill şu sırayla çalışacak, atlamak istediğin var mı?").
3. **Faz 2 — İdeal vs mevcut:** Önce `ds-blueprint --strategic` + web tabanlı rakip araştırma (`ds-research` ile) ile **ideal mimari** çıkart. Kullanıcıya "ideal şu, seninki şu, şu farklar var — mimari değişiklikleri onaylıyor musun?" diye sor. Onaylanan değişiklikler mimari plana işlensin.
4. **Faz 3 — Otonom fix:** Mimariye uygun küçük eksikler otomatik düzeltilir (`ds-fix`, `ds-review --tactical` fix-mode). Mimari değiştiren her şey onay kapısından geçer.
5. **Faz 4 — Pre-launch:** `ds-compliance`, `ds-test`, `ds-devops`, `ds-deploy`, `ds-repo`, `ds-launch` sırayla.
6. **Faz 5 — OSS check (opsiyonel):** Proje public ise `ds-repo` + license + CODE_OF_CONDUCT + SECURITY.md + CONTRIBUTING.md + issue template kontrolü + README quality gate.
7. **Faz 6 — Raporlama:** Tek bir `.ds-ship-report.md` dosyası — hangi faz hangi bulguları verdi, hangileri fix'lendi, hangileri kullanıcı eylemi bekliyor.

**Kritik kural:** Orkestratör hiçbir skill'in işini tekrar yapmamalı. `.ds-findings.md` SSOT olarak kalmalı. Orkestratör sadece **tetikleyici + agregatör** — analiz/fix işini her zaman ilgili skill yapar.

**Uyarı — overengineering riski:** Orkestratör kendi analiz mantığını içermemeli. Her faz sadece "hangi skill'i hangi argümanlarla çağır" bilgisine sahip olmalı. Aksi halde `ds-review` ile çakışır.

---

### GAP-2 (YÜKSEK) — Spec vs Implementation (feature-completeness) denetimi

**Ne eksik:** `ds-review --strategic`'te `functional-completeness` scope'u var ama sadece TODO/stub işaretlerini buluyor. **Ürün spec'i ile kod arasındaki divergence'ı** (gereksinim X dokümandaydı, kodda yok; veya kodda var, dokümanda yok) denetleyen kimse yok.

**Neden kritik:**
- Kullanıcının asıl derdi "dokümanlarda belirtilen tüm işlevleri karşılıyor mu?" — bu soruya tam cevap veren skill yok.
- Spec drift, canlıya çıkarken "bu özelliği söz vermiştik ama yokmuş" felaketinin ana kaynağı.

**Öneri:** `ds-blueprint` içinde yeni scope: `spec-gap` (ya da yeni küçük skill: `ds-spec-audit`).

**Kapsam:**
- Proje içindeki spec dokümanlarını (README, docs/, SPEC.md, blueprint profile) tespit et.
- Her spec maddesini ayrı satıra ayır (madde → kod referansı beklentisi).
- Kod içinde o maddeyi karşılayan modül/fonksiyon var mı, grep + LSP ile doğrula.
- Üç kategori rapor:
  - **Söz verilmiş, kodda yok** (kritik — lansmanı engeller)
  - **Kodda var, dokümante edilmemiş** (`ds-docs` devri)
  - **İkisinde de var ama drift** (spec v1, kod v2 → hangisi doğru, kullanıcı karar versin)
- Fix mode yok — sadece rapor + öneri. Çünkü her divergence bir ürün kararı gerektirir.

---

### GAP-3 (YÜKSEK) — İdeal mimari ↔ Mevcut mimari kıyas dokümanı

**Ne eksik:** `ds-review --strategic` mimariyi değerlendiriyor (8 scope, 92 kontrol) ama **"bu problem alanının ideal çözümü şöyle olurdu, seninki şöyle, fark şurada"** şeklinde kıyas üretmiyor. Kullanıcı bunu örnek prompt'larında defalarca istemiş ("webden benzer/rakip her türlü başarılı projeyi araştır, ideal yolu tespit et, mevcut vs ideal kıyasla, plana dönüştür").

**Neden kritik:**
- Kullanıcının felsefesi: somut fayda üretmeyen hiçbir yapı kalmasın. Ama "somut fayda" ölçütü için ideal yapıyı bilmek lazım.
- OSS olarak yayımlanan projelerin rakiplere karşı pozisyonu netleşir.

**Öneri:** Yeni skill `ds-benchmark` (veya `ds-vs-ideal`).

**Kapsam:**
1. Proje tanımını oku (`ds-blueprint` profilinden).
2. `ds-research` ile web'de 5-10 popüler/başarılı benzer proje bul.
3. Her birinin iyi/kötü yaptığı şeyleri CRAAP+ ile tier'la.
4. **İdeal yapı sentezi** üret: mimari, stack, veri modeli, UX, güvenlik kararları.
5. Mevcut projenin her boyutunda ideal'e göre **fark tablosu**.
6. Her farka: "bu fark kapanmalı mı? yoksa bilinçli bir sapma mı?" sorusu kullanıcıya.
7. Onaylanan farklar mimari plana yazılır → `ds-ship` pipeline'ı buradan devam eder.

**İlişki:** `ds-research` bu skill'in motoru. `ds-ship` bunu Faz 2'de çağırır.

---

### GAP-4 (ORTA) — Overengineering'e özel audit

**Ne eksik:** `ds-review --strategic`'te overengineering check var ama diğer check'lerle aynı seviyede gömülü. Kullanıcı kompozit bir skill istiyor: "projenin her yerinde overlap/redundant/obsolete/duplicate/orphan/premature abstraction yok mu?"

**Neden kritik:**
- Kullanıcının en sık tekrarladığı felsefe: "üç benzer satır, prematüre soyutlamadan iyidir." Ama AI ajanları spontan olarak soyutluyor.
- Overengineering temizliği sistematik yapılmadığında birikiyor; çorba olunca geri dönmek ciddi efor.

**Öneri:** Yeni skill `ds-simplify` **veya** `ds-review --overengineering` standalone modu.

**Kapsam — sadece tespit + onaylı silme:**
- Dead code (LSP `findReferences` = 0 olan exports).
- Tek çağrılan helper'lar (inline'a adayı).
- Fallback / backward-compat kalıntıları (kullanıcı explicit istememişse).
- Feature flag'li ama tek path'i kullanılan kod.
- Üç satırlık benzerliği abstraction'a çıkaran yerler.
- `// removed` / `// legacy` / `_unused` pattern'li karantina kodu.
- Her bulgu için: "sil / tut + neden?" sorusu. Otomatik silme YOK — her biri onay.

**Neden ayrı skill:** Bu, tek seferlik temizlik operasyonu değil, periyodik hijyen. Kullanıcı bunu her sprint sonu çağıracak. Kendine ait modu olmalı.

**Not:** Global `simplify` skill'i zaten var ama bu `ds-` ailesinde yok. `ds-simplify` onu sarmalayıp `.ds-findings.md` ekosistemiyle entegre edebilir.

---

### GAP-5 (ORTA) — OSS-readiness tek-kapı denetimi

**Ne eksik:** OSS yayına hazır olmak için gereken 15+ check (LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY.md, issue templates, PR template, CHANGELOG disipli, semver, README quality, topics/metadata, CODEOWNERS, branch protection, Dependabot, discussions, sponsorship config, discoverability badges) parça parça `ds-repo`, `ds-docs`, `ds-launch`, `ds-compliance` arasında dağılmış. Tek komutla "bu repo public olmaya hazır mı?" cevabı alınmıyor.

**Neden kritik:**
- Kullanıcı bazı projelerini OSS yapmayı planlıyor (dev-skills, ledger, kuzgun ekosistemi).
- OSS lansmanında eksik bir CONTRIBUTING veya yanlış license "işe yaramaz ilk izlenim" demek.

**Öneri:** `ds-repo` skill'ine `--oss-readiness` yeni modu ekle **veya** yeni skill `ds-oss-ready`.

**Kapsam:**
- 15+ check listesi, her biri için durum: ✅ / ⚠️ / ❌.
- Eksik dosyalar için template öner (var olanları değiştirmeden).
- Lisans uyumluluğu (bağımlılıkların lisansları ana lisansla çelişiyor mu?).
- Marka/ticari kelime taraması (proje adı başkasının markası mı?).
- README "maintenance signal" taraması (son commit, son release, açık issue yaşı).
- Public olmadan önce secret history taraması (git-filter-repo önerisi).
- Fix mode: sadece mimari-etkisiz olanları (templates, metadata) otomatik; içerik kararlarını onay ile.

---

### GAP-6 (ORTA) — Bağımlılık yükseltme execution döngüsü

**Ne eksik:** `ds-devops` outdated dep'leri tespit ediyor, `ds-blueprint` stack sağlığını skorluyor ama **yükselt → test → commit** döngüsünü kimse çalıştırmıyor. Kullanıcı bunu manuel ya da `ds-solve` ile ad-hoc yapıyor.

**Neden kritik:**
- Uzun süre dokunulmayan projelerde (örn. kullanıcının dondurulmuş projeleri) bu iş birikiyor.
- Latest-stable politikası kullanıcının deklare ettiği kural — sistem bunu enforce edecek bir aracı hak ediyor.

**Öneri:** Yeni skill `ds-deps` (veya `ds-upgrade`).

**Kapsam:**
- Her bağımlılık için: mevcut sürüm, latest stable, breaking changes (changelog diff).
- Gruplandır: safe patch/minor vs review-required major.
- Safe grup: yükselt → test çalıştır → geçerse commit (tek commit, bir grup).
- Review-required: kullanıcıya tablolu özet + her birinin migration notu.
- `ds-test` entegrasyonu (yükseltme sonrası test).
- Rollback planı her grup için.
- Security advisory taraması (npm audit / pip-audit / cargo audit) ile öncelik.

---

### GAP-7 (DÜŞÜK) — ADR tracking

**Ne eksik:** Architecture Decision Record üreten/bakımlayan skill yok. `ds-review --strategic` mimari değerlendirir ama karar dokümantasyonu çıkarmaz. Kullanıcı 3 ay sonra "neden bu DB seçildi?" dediğinde cevap yok.

**Neden kritik (ama düşük):**
- Tek kişi + AI ajanı için ADR ağır yük.
- Yine de OSS olunca contributor'ların bağlamı kaçırmaması için değerli.

**Öneri:** `ds-docs` skill'ine `--adr` modu ekle.

**Kapsam:**
- `docs/adr/` dizininde numaralı ADR dosyaları (şablon: Context / Decision / Consequences).
- `ds-review --strategic` ile yakalanan her "mimari karar" için taslak ADR üretme teklifi.
- Yeni ADR eklendiğinde eskileri "superseded" olarak işaretleme.

---

### GAP-8 (DÜŞÜK) — Performans bütçesi enforcement

**Ne eksik:** `ds-review --perf` ve `ds-tune` optimize ediyor ama **formal bir perf budget** (LCP<2.5s, p99<200ms, bundle<300KB) CI'da enforce edilmiyor. `ds-deploy` alert threshold'ları söylüyor ama budget artifact'ı yok.

**Neden kritik (ama düşük):**
- Küçük projeler için gereksiz.
- Web/mobil gibi UX-kritik projeler için değerli.

**Öneri:** `ds-launch` skill'ine `--perf-budget` modu ekle; `ds-devops` ile CI integration.

---

### GAP-9 (DÜŞÜK) — Secrets rotation / vaulting

**Ne eksik:** `ds-fix` ve `ds-blueprint` hardcoded secret detect ediyor, `ds-compliance` flags. Ama **rotate + vault migration** yapan yok.

**Neden kritik (ama düşük):**
- Tespit + manuel rotate kullanıcı için yönetilebilir.
- Enterprise/multi-contributor projelerde değerli.

**Öneri:** `ds-compliance` içinde `--secrets-migrate` walkthrough (interactive — her secret için "nereye taşıyorsun, rotate mi?").

---

### GAP-10 (DÜŞÜK) — Monorepo koordinasyonu

**Ne eksik:** Skill'lerin çoğu monorepo edge-case'i ele alıyor ama özel bir monorepo skill'i yok (affected-package detection, workspace-level health aggregation, cross-package dep graph).

**Neden kritik (ama düşük):**
- Kullanıcının mevcut projelerinde klasik monorepo yok.
- Gelecekte (kuzgun ekosistemi 8 repo) devreye girebilir.

**Öneri:** Şimdilik skip — ihtiyaç doğduğunda yeniden değerlendir.

---

## 3. Overlap Temizlikleri

Bu overlap'ler yeni skill gerektirmez, sadece mevcut skill'lerin `allowed-tools` / description alanlarına **delegasyon kuralları** eklenmesiyle çözülür.

### OVERLAP-1 — `ds-mobile` ↔ `ds-compliance`

**Durum:** Mobil projelerde ikisini de çalıştırmak duplicate bulgular üretir (OWASP, PII, GDPR/KVKK çakışıyor).

**Çözüm:** `ds-compliance` SKILL.md'sine: "Eğer proje mobil ise (pubspec.yaml/Info.plist/AndroidManifest.xml var), `ds-mobile --scope=security,privacy,regulatory`'ye delege et ve ana dönüş." notu ekle. Tersi yön: `ds-mobile` sadece mobil-spesifik kuralları çalıştırdığını açıkça deklare etsin, web/backend kurallarına bulaşmasın.

### OVERLAP-2 — `ds-frontend` (a11y) ↔ `ds-compliance` (a11y)

**Durum:** İkisi de WCAG 2.2 AA'ya bakar. `ds-frontend` fix yapar, `ds-compliance` yapmaz.

**Çözüm:** `ds-compliance` a11y scope'u `ds-frontend`'e delege etsin (mevcut kod frontend ise). Sadece **regulatory framing**'i (bu WCAG maddesi ADA/EN301549 için gerekli mi) `ds-compliance`'ta kalsın.

### OVERLAP-3 — `ds-deploy` ↔ `ds-devops` (CI deploy configuration)

**Durum:** İkisi de CI deploy step'lerini kontrol ediyor.

**Çözüm:** `ds-devops` → pipeline yapısı, signing, deps, cache, test execution. `ds-deploy` → container image, TLS, monitoring, incident runbook, deploy hedefi tarafı. CI deploy stage'i sadece **`ds-devops`'ta** kalsın; `ds-deploy` "CI deploy step'i `ds-devops`'tan doğruluyorum" dese yeter.

### OVERLAP-4 — `ds-launch --privacy` ↔ `ds-analytics` (privacy) ↔ `ds-compliance` (privacy)

**Durum:** Üç farklı lens'ten aynı veri toplama pattern'lerini kontrol ediyorlar.

**Çözüm:** Privacy'yi tek noktada topla — `ds-compliance --privacy` authoritative olsun. `ds-launch --privacy` sadece **store label declaration** doğruluğuna bakın (Apple/Google label field'ı koddaki davranışla uyumlu mu?). `ds-analytics --privacy-audit` sadece **event property PII** taraması (event'lere kişisel veri sızıyor mu?) ile sınırlansın.

### OVERLAP-5 — `ds-blueprint` ↔ `ds-review --tactical` (bare run)

**Durum:** `.ds-findings.md` yoksa `ds-review` her şeyi yeniden tarıyor.

**Çözüm:** `ds-review` ilk adımda `.ds-findings.md` kontrolü yapsın. Yoksa önce `ds-blueprint`'i otomatik çalıştır, dosyayı üret, sonra review başlasın. Yasak kelime: "rediscover" — her tarama tek noktadan çıkmalı.

---

## 4. Uygulama Sırası (Öneri)

Kullanıcı dev-skills repo'sunda bu planı uygularken şu sırayı izlemeli — en yüksek fayda / en düşük risk:

1. **Overlap-5** düzeltmesi (blueprint-review bağı). Tek satırlık SKILL.md ekleme. Anında token tasarrufu.
2. **GAP-1: `ds-ship` orkestratörü** (YÜKSEK). Kullanıcının asıl acı noktası. Diğer gap'leri bu beslenecek.
3. **GAP-4: `ds-simplify` veya `ds-review --overengineering`** (ORTA). Mevcut projelerin temizliği için anında kullanılacak.
4. **GAP-2: spec-gap scope'u** (YÜKSEK). `ds-blueprint` içinde veya `ds-spec-audit` olarak. Kullanıcının "dokümanlarda söz verilen işlevler karşılanıyor mu?" sorusuna direkt cevap.
5. **GAP-3: `ds-benchmark`** (YÜKSEK). İdeal vs mevcut kıyas. `ds-ship`'in Faz 2 motoru.
6. **Overlap-1, 2, 3, 4** (düşük risk, kolay).
7. **GAP-5: OSS-ready** (ORTA). Kuzgun ve diğer OSS adayları için.
8. **GAP-6: `ds-deps`** (ORTA). Dondurulmuş projelerin güncellenmesi için.
9. **GAP-7, 8, 9, 10** (DÜŞÜK). İhtiyaç doğdukça.

---

## 5. Her Yeni Skill İçin Ortak Tasarım Kriterleri

Yeni skill'ler koleksiyonun tutarlılığını bozmamalı. Her yeni skill:

- **SSOT:** Kendi analiz mantığını yazma — varsa mevcut skill'e delege et.
- **`.ds-findings.md` entegrasyonu:** Bulgularını bu dosyaya ekle, yoksa oluştur, overwriting değil merge.
- **İki seviyeli onay modeli:** Mevcut mimariye uygun fix'ler otonom; mimari değiştiren her şey onay.
- **Claude-native:** Ek bağımlılık yok (git + gh istisna). Python/Node script gerektirmesin.
- **OS-agnostic:** Windows/Mac/Linux aynı çalışsın.
- **Model-agnostic:** Opus/Sonnet/Haiku fark etmeksizin çalışsın (yeteneğe göre kalite düşebilir ama kırılmasın).
- **Token-efficient:** Progressive loading — gerekmeyen modülü contexte alma.
- **Compact rapor formatı:** Etki/fayda odaklı ("X eksikti → Y soruna yol açıyordu → Z fix'i uygulandı → şu önlendi"). Verbose yok.
- **Report yaratma:** Sadece `.ds-findings.md` + varsa onun altında skill-spesifik rapor. Log/trace/debug/history/cache dosyası üretme.

---

## 6. Uygulama Sonrası Doğrulama

Her yeni skill eklendikten sonra:

1. `SKILL.md` → frontmatter kontrolü (description anahtar kelimeli, trigger net).
2. `install.sh` → yeni skill deploy edilebiliyor mu.
3. Dry run: örnek bir proje üzerinde skill'i çalıştır, çıktı formatı tutarlı mı.
4. Overlap testi: aynı projede 2 skill peş peşe çalıştır, aynı bulgu iki kere raporlanmıyor mu.
5. Doküman güncellemesi: README.md + SKILL-SPEC.md'ye yeni skill referansı.

---

**Sonuç:** Koleksiyon review/fix/pre-launch koridorunda zaten güçlü. Eksik olan üç şey: **(1) tek-komut orkestratör**, **(2) spec/ideal kıyas katmanı**, **(3) overengineering'e özel hijyen**. Bu üçü eklenirse ve 5 overlap temizlenirse, kullanıcının "fikirden OSS-lansmana kadar eksiksiz denetim" hedefi karşılanır.
