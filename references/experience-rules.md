# Experience-Rule Registry (XR) — Pointer Map

Cross-project experience rules (Akış + SafeScribe programs, 2026) mapped to their dev-skills home. This is a POINTER index — rule content lives in the target skill rule files (English) and in the canonical registry (`~/projects/.rules-audit/canonical-xr.json`, Turkish). Never duplicate rule text here.

Registry size: 198 rules. Statuses: `integrated` (added by the 2026-07-24 transfer), `covered (pre-existing)` (already present before the transfer), `skipped` (deliberately not transferred — product-specific or duplicate; reason in the table).

| XR | Title (TR) | Status | dev-skills target | Skip reason |
|----|-----------|--------|-------------------|-------------|
| XR-001 | Aracısız doğrudan sağlayıcı entegrasyonu | integrated | ds-backend:DP-21 |  |
| XR-002 | Senkronizasyon sadakati: kayıpsız çift-yön alan eşlemesi | integrated | ds-backend:DP-17 |  |
| XR-003 | Route'lar tek manifestten türer | integrated | ds-frontend:CMP-27 |  |
| XR-004 | Deterministik veri-öncelikli önyükleme + tek tema uygulaması | integrated | ds-frontend:THM-06 |  |
| XR-005 | Veri-yerleşimi değişmezi: her yazma yolu paylaşılan owner deposuna | integrated | ds-compliance:PRV-30 |  |
| XR-006 | Sahiplik açık ve devredilebilir; owner ödeyenden türetilmez | covered (pre-existing) | ds-backend:SKILL.md:156 |  |
| XR-007 | Tüm yönetim uygulama üzerinden; zorunlu manuel dış adımlar otomatik… | covered (pre-existing) | ds-frontend:UX-ON-04 |  |
| XR-008 | Sektör-bağımsız terminoloji: etiketler admin-yönetimli tek kayıttan | integrated (merged) | ds-backend:DB-15 |  |
| XR-009 | Konfigürasyon dört sahiplik katmanına ayrılır | covered (pre-existing) | ds-backend:SKILL.md:155 |  |
| XR-010 | Depolama erişimi tek soyutlama katmanından geçer | integrated | ds-backend:DB-19 |  |
| XR-011 | Çok-kiracılı kimlik değişmez sub claim'ine bağlanır | covered (pre-existing) | ds-backend:SKILL.md:121 |  |
| XR-012 | Çapraz-yüzey gerçekler tek SSOT dosyasından türetilir + drift bekçisi | integrated | ds-devops:DOP-39 |  |
| XR-013 | Üretilen artefaktlar elle düzenlenmez; otomatik üretilip doğrulanır | integrated | ds-devops:DOP-38 |  |
| XR-014 | Yapısal değişiklik ile dokümantasyon aynı commit'te güncellenir | integrated | ds-docs:DOC-18 |  |
| XR-015 | Çapraz-repo belge tek kanonik kopyada; diğerleri işaretçi bırakır | integrated | ds-docs:DOC-19 |  |
| XR-016 | Yaşayan uyum belgeleri tarihli inceleme günlüğüyle düzeltilir | integrated | ds-docs:DOC-20 |  |
| XR-017 | Kanıta dayalı kararlar kilitlenir; yeni kanıt olmadan yeniden tartı… | integrated | ds-docs:DOC-21 |  |
| XR-018 | Kabul edilmiş mimari borç açık kimlikle takip edilir | integrated | ds-docs:DOC-22 |  |
| XR-019 | Güvenlik kontrolleri gerçek tehdit modeline göre ölçeklenir | integrated | ds-compliance:CSEC-09 |  |
| XR-020 | Çok-repo sürüm orkestrasyonu ince delegasyonla yapılır | integrated | ds-devops:DOP-35 |  |
| XR-021 | Şema migrasyonları çift yönlü + kayıp sınırları belgeli | integrated | ds-backend:DB-17 |  |
| XR-022 | Uzun-ömürlü kayıt formatı her an kurtarılabilir seçilir | integrated | ds-mobile:REL-24 |  |
| XR-023 | Kalıcı tanımlayıcılar ham değil tuzlanmış hash olarak saklanır | integrated | ds-backend:DB-12 |  |
| XR-024 | Kişisel içerik yalnız RAM'de, zorunlu failsafe TTL ile | integrated | ds-compliance:PRV-35 |  |
| XR-025 | Büyük dosya işlemleri akışlı ve ana-iş-parçacığı dışında | integrated | ds-compliance:PRF-09 |  |
| XR-026 | Tek-yazarlı gömülü DB WAL + eşleşen kısmi indeksle ayarlanır | integrated | ds-backend:DB-13 |  |
| XR-027 | Kimlik doğrulama PKCE redirect akışıyla yapılır | integrated | ds-backend:AUTH-12 |  |
| XR-028 | Oran-sınırlama pratik, düşük-yük ve tam kapsayıcı | integrated | ds-compliance:NET-14 |  |
| XR-029 | Yetkilendirme kapısı çok-noktalı; entitlement sunucuda zorlanır | covered (pre-existing) | ds-productize:references/rules-monetization.md:19-24 |  |
| XR-030 | Rol-bağlı şifreleme: anahtar alıcı kümesi statik seed'den türer | covered (pre-existing) | ds-productize:references/rules-monetization.md:19-24 |  |
| XR-031 | Tek yetki-verme aksiyonu tüm katmanlara atomik yayılır | covered (pre-existing) | ds-backend:SKILL.md:157 |  |
| XR-032 | Yıkıcı işlemler dar-kapsamlı, adlandırılmış ve idempotenttir | covered (pre-existing) | ds-backend:SKILL.md:78 |  |
| XR-033 | Yönetici anahtar rotasyonu çift-anahtar örtüşme penceresiyle | integrated | ds-backend:AUTH-14 |  |
| XR-034 | Çapraz-platform güvenlik asimetrisi dürüstçe belgelenir | integrated | ds-compliance:CSEC-11 |  |
| XR-035 | Alan-hassasiyeti tek deklaratif registry'de tanımlanır | covered (pre-existing) | ds-compliance:references/rules-compliance.md:231-238 |  |
| XR-036 | KVKK: özel-nitelikli veri sağlayıcıyla asla paylaşılmaz | integrated | ds-compliance:PRV-31 |  |
| XR-037 | Serbest metin loglanmadan/saklanmadan önce PII redakte edilir | covered (pre-existing) | ds-compliance:PRV-05 |  |
| XR-038 | Silme hakkı tek kanonik anahtar listesinden yürür | integrated | ds-compliance:PRV-32 |  |
| XR-039 | Silme vaadi istemci-doğrulanabilir kanıtla desteklenir | integrated | ds-compliance:PRV-39 |  |
| XR-040 | Rıza sürümlenir; şema artışı yeniden-rıza tetikler | integrated | ds-compliance:PRV-33 |  |
| XR-041 | Uyum eşikleri gerekçe ve yargı-bölgeleriyle belgelenir | integrated | ds-compliance:PRV-40 |  |
| XR-042 | İhlal bildirimi eksik bilgiyle bile süresinde yapılır | integrated | ds-compliance:PRV-34 |  |
| XR-043 | Yasal/mevzuat değerleri birincil metne karşı doğrulanır | integrated | ds-compliance:PRV-41 |  |
| XR-044 | Üçüncü-taraf lisans yükümlülükleri tek belgede mekanizmaya eşlenir | integrated | ds-compliance:PRV-43 |  |
| XR-045 | Katı CSP: satır-içi script/style/handler tamamen dışarı taşınır | covered (pre-existing) | ds-compliance:rules-web.md:18-27 |  |
| XR-046 | Yerleşim & hizalama tek SSOT'tan; boş/dengesiz kenar yok | integrated | ds-frontend:TOK-13 |  |
| XR-047 | Üç görsel yoğunluk varyantı tek SSOT'tan yansır | covered (pre-existing) | ds-frontend:references/rules-design-system.md:16-19 |  |
| XR-048 | Filtre işlevleri (hepsini-seç/temizle) tek SSOT bileşenden türer | integrated | ds-frontend:CMP-23 |  |
| XR-049 | Detay/düzenleme aynı sayfada gömülü panelde yapılır | integrated | ds-frontend:SCH-10 |  |
| XR-050 | Nadir kullanılan toplu istatistikler ayrı rapor ekranına taşınır | integrated | ds-frontend:UX-16 |  |
| XR-051 | Randevu hover-önizlemesi | integrated | ds-frontend:SCH-01 |  |
| XR-052 | Oluşturma akışı adım-bazlı sadeleşir | integrated (merged) | ds-frontend:SCH-02 |  |
| XR-053 | Takvimde entity görsel ayrımı: renk SSOT + ikinci görsel eksen | integrated | ds-frontend:SCH-07 |  |
| XR-054 | Mesai-dışı alan her zaman taralı/pasif görünür | integrated | ds-frontend:SCH-05 |  |
| XR-055 | Görsel kalite en-iyi-örnek seviyesinde, performanstan ödünsüz | covered (pre-existing) | ds-frontend:references/rules-components.md:245 |  |
| XR-056 | Form ergonomisi: bağımlılık-sıralı, türetilen-ama-düzenlenebilir, d… | integrated | ds-frontend:CMP-26 |  |
| XR-057 | Sürüm-reload / cache-invalidation form durumunu korur | covered (pre-existing) | ds-frontend:CMP-22 |  |
| XR-058 | Canlı arama ilk karakterden; başlangıç kümesi tohumlanır | covered (pre-existing) | ds-frontend:references/rules-components.md:39-49 |  |
| XR-059 | Birleşik durum/sağlık merkezi + kademeli şiddet düşürme | covered (pre-existing) | ds-frontend:CMP-20 |  |
| XR-060 | Yüzey durum bütünlüğü: boş/yüklüyor/hata/yetki tek SSOT'tan | covered (pre-existing) | ds-frontend:CMP-13 |  |
| XR-061 | Tek-başlık ilkesi: gereksiz alt-başlık render edilmez | covered (pre-existing) | ds-frontend:UX-WR-03 |  |
| XR-062 | Kopyalanabilir metin platform-güvenlidir | integrated (merged) | ds-frontend:UX-WR-04 |  |
| XR-063 | Kişi-satırı hizalı-sütun primitive'inden türer | integrated | ds-frontend:CMP-24 |  |
| XR-064 | Kişi seçici rol-bağlamlı filtreler | integrated (merged) | ds-frontend:CMP-24 |  |
| XR-065 | i18n-öncelikli: hardcoded metin yasak, chrome dahil; denetim chrome… | integrated | ds-compliance:I18N-10 |  |
| XR-066 | Mekanik a11y minimumları zorlanır | covered (pre-existing) | ds-frontend:references/rules-accessibility.md |  |
| XR-067 | Çoklu-dil anahtar ve parametre eşliği mekanik zorlanır | integrated | ds-compliance:I18N-09 |  |
| XR-068 | Terminoloji tercihi otoriter kaynağa bağlı ve günlük dilde | integrated | ds-compliance:I18N-11 |  |
| XR-069 | hreflang tam BCP-47 alt-etiketleri kullanır | integrated | ds-compliance:I18N-13 |  |
| XR-071 | Gömülü büyük varlıklar kapsama göre alt-kümelenir, build-dışı | integrated | ds-mobile:PRF-10 |  |
| XR-072 | Gürültülü native geri-çağırım selleri başlangıçta kapatılır | integrated | ds-mobile:REL-25 |  |
| XR-073 | Retry sonuçları üç-değerlidir | covered (pre-existing) | ds-backend:SKILL.md:110 |  |
| XR-074 | Yerel kalıcı kuyruklar boyut/retry/yaş ile sınırlanır | integrated | ds-backend:DP-14 |  |
| XR-075 | Pahalı kaynak işleri giriş-tavanıyla, retry'dan önce reddedilir | integrated | ds-backend:DP-15 |  |
| XR-076 | Kaynak-tükenmesi sonrası tekil-process worker kendini yeniden başlatır | integrated | ds-backend:DP-16 |  |
| XR-077 | Uzun-ömürlü bağlantı için ikinci taşıma yedeği zorunludur | integrated | ds-backend:API-14 |  |
| XR-078 | Hata hiyerarşisi tipli ve mühürlü; boş catch yasak | integrated | ds-review:empty-catch rule (~line 77) |  |
| XR-079 | Sağlık sinyali kuyruk-başı bayatlığını da ölçer | integrated | ds-deploy:MON-07 |  |
| XR-080 | Kuyruk iş-fonksiyonu çözümlemesi giriş-modülü takma adıyla düzeltilir | integrated | ds-backend:DP-12 |  |
| XR-081 | Kritik env yoksa başlangıçta hızlı başarısız olunur | integrated | ds-deploy:DEP-20 |  |
| XR-082 | Dev-override yapılandırması prod'a sızdırılmaz | integrated | ds-deploy:DEP-21 |  |
| XR-083 | İki-katmanlı yerel kalite kancaları; sürümü versiyonlu kaynakla sen… | integrated | ds-quality:hook-arm design section |  |
| XR-084 | Public repo backlog'u private kardeş repoda tutulabilir | integrated | ds-repo:RPO-10 |  |
| XR-085 | Tek-komut release deterministik kapı-zincirinden geçer | integrated | ds-devops:DOP-32 |  |
| XR-086 | Üretim derlemesi zorunlu obfuscation + sembol-arşiv sarmalayıcısınd… | covered (pre-existing) | ds-mobile:SEC-07 |  |
| XR-087 | Ağır kontroller deploy-tetikleyen eylemden önce koşar | integrated | ds-devops:DOP-33 |  |
| XR-088 | Statik-host deploy'u build-API SHA doğrulamasıyla biter | integrated | ds-deploy:DEP-18 |  |
| XR-089 | Zorunlu store beyanları özellik koduyla aynı commit'te güncellenir | integrated | ds-mobile:REL-23 |  |
| XR-090 | UI/UX/DX kuralları maksimum mekanik denetime çevrilir | covered (pre-existing) | ds-review:SKILL.md:276 |  |
| XR-091 | Kritik akışlar gerçek dispatch/registry üzerinden test edilir | covered (pre-existing) | ds-test:SKILL.md:194 |  |
| XR-092 | Platform-duyarlı testler yerelde hariç, CI'da tam koşulur | integrated | ds-review:TST-08 |  |
| XR-093 | Kalite/performans iddiaları yeniden-üretilebilir ölçümle desteklenir | integrated | ds-docs:DOC-23 |  |
| XR-094 | Bilinen-yanlış iddialar kalıcı denylist ile engellenir | integrated | ds-quality:optional arm / check inventory |  |
| XR-095 | Çok-katılımcılı randevu modeli | skipped | — | Akış-specific appointment-domain data model (multi-provider/multi-client participant roster with per-participa |
| XR-096 | Mekan kapasitesi ve hizmet-tipi kısıtı saniye-hassas çakışma kontro… | integrated | ds-frontend:SCH-08 |  |
| XR-097 | Randevu modalitesi seçilebilir (online/yüz-yüze) | skipped | — | product feature choice (session modality online/in-person as a domain field). No generalizable enforcement con |
| XR-098 | Randevu yapılandırması admin-tanımlıdır | skipped | — | covered by generalizations landing in this same transfer: admin-defined types/templates/pricing = configuratio |
| XR-099 | Kişi etkileşim geçmişi yerel-şifreli izlenir | skipped | — | Akış-specific CRM interaction-history model. Its two transferable invariants are carried elsewhere in this tra |
| XR-100 | Her mutasyon (silme dahil) tam-önceki-durumla denetlenir ve geri al… | covered (pre-existing) | ds-backend:SKILL.md:147 |  |
| XR-101 | Denetim kaydı her eksen boyunca filtrelenebilir, aranabilir, grupla… | integrated | ds-frontend:UX-15 |  |
| XR-102 | Randevu ücret/ödeme takibi net ve admin-tanımlı yöntemlerle | skipped | — | product feature (per-appointment fee/payment-status tracking with admin-defined payment methods). The transfer |
| XR-103 | Genel toplu-düzenleme motoru + batch-gruplu denetim ve geri-alma | integrated | ds-backend:DB-18 |  |
| XR-104 | İki-katmanlı idempotency + idempotent iade (yeniden-teslim güvenliği) | integrated | ds-productize:MON-04 |  |
| XR-105 | Teslim edilmemiş ücretli iş için durable-store SSOT'undan otomatik … | integrated | ds-productize:MON-14 |  |
| XR-106 | Runtime pini build betiğiyle zorlanır | integrated | ds-devops:version-pinning rule at rules-devops.md:53-56 |  |
| XR-107 | Sürüm-hassas ve ampirik-doğrulanmış bağımlılıklar gerekçeyle pinlenir | integrated | ds-deps:pin-handling section (the `# pinned` comment convention, ~line 264) |  |
| XR-108 | Belirsiz YAML değerleri tırnaklanır/lint'lenir | integrated | ds-devops:DOP-40 |  |
| XR-109 | Uygulama-ürettiği dosyalar kalıp-eşleşmesiyle güvenle silinir | integrated | ds-compliance:PRV-37 |  |
| XR-110 | Kullanıma-dayalı faturalama metni 'kimin hatası' belirsizliği taşımaz | integrated | ds-productize:MON-16 |  |
| XR-111 | Firma sitesi verisi merkezi SSOT'tan; kopya yok, alan alt-kümesi se… | integrated | ds-backend:DP-22 |  |
| XR-112 | Firma sitesi yayın/önizleme dahil piyasa-standardı özellikler mekan… | covered (pre-existing) | ds-review:references/rules-quality.md:177-180 |  |
| XR-113 | Firma sitesi görselleri merkezi depodan çekilir | integrated (merged) | ds-backend:DP-22 |  |
| XR-114 | Public rezervasyon yüzeyi izole ve PII'sizdir | integrated | ds-compliance:PRV-45 |  |
| XR-115 | Genel SSOT değişmezi: tüm ayar/nitelik/kriter tek tanımdan türer | covered (pre-existing) | ds-review:references/meta-quality-scopes.md:5-15 |  |
| XR-116 | Yayın-öncesi: geriye-dönük-uyumluluk kalıntısı istenmez | integrated | ds-simplify:dead-code category (backward-compat branches, ~lines 56,105) |  |
| XR-117 | Kanonikleştir-önce-uygula: muafiyet/gate-bypass yok | integrated | ds-pipeline:blocking-gates section |  |
| XR-118 | Yeni entegrasyon inşa etmeden önce native yetenek belgelenir | integrated | ds-review:(next free ID in the file's strategic/architecture series; assign at apply) |  |
| XR-119 | Tek desteklenen model tercih edilir; paralel modlar reddedilir | integrated | ds-review:(next free ID after XR-118's rule; assign at apply) |  |
| XR-120 | Demo/örnek veri gerçek buluta asla ulaşamaz | integrated | ds-compliance:PRV-36 |  |
| XR-121 | Tanılama/geri-bildirim kanalı kullanıcı-tetiklemeli, PII'siz, previ… | integrated | ds-compliance:PRV-38 |  |
| XR-122 | Locale-duyarlı case-fold (TR İ/I) kullanılır, ASCII-only değil | integrated | ds-compliance:I18N-12 |  |
| XR-123 | Bundle-boyutu ölçülen-baseline+%10 tavan, yalnız uyarı | integrated | ds-review:bundle-size audit rule (~line 33) |  |
| XR-124 | Ertelenen modüller yapısal olarak gizli, 'yakında' değil | covered (pre-existing) | ds-freeze:SKILL.md:33 |  |
| XR-125 | Marketplace scope/redirect değişikliği yeniden-verification tetikler | integrated | ds-launch:store/marketplace listing maintenance section |  |
| XR-126 | Mobil launch native-köprü akışlarının cihazda doğrulanmasına bağlıdır | covered (pre-existing) | ds-mobile:references/scoring.md:74 |  |
| XR-127 | Kripto katmanı bağımsız dış incelemeden geçmeden production-final s… | integrated | ds-compliance:CSEC-10 |  |
| XR-128 | Felaket kurtarma canlı tatbikatla kanıtlanır; yedek varlığı yetmez | covered (pre-existing) | ds-backend:SKILL.md:89 |  |
| XR-129 | Fiyat/konumlandırma gerçek ücretli pilotla doğrulanır | integrated | ds-productize:PRC-06 |  |
| XR-130 | Duplike çalışma-alanı birleştirme: elle kanonik seçim + cloud-wins … | integrated | ds-backend:DP-13 |  |
| XR-131 | Tooltip disiplini: kendini anlatan öğede tooltip yok; varsa endüstr… | integrated | ds-frontend:UX-13 |  |
| XR-132 | Yerleşim stabilitesi: scrollbar/hover yerleşimi değiştirmez | integrated | ds-frontend:RSP-21 |  |
| XR-133 | Tek adaptör geçidi + kayıtlı strategy dağıtımı | covered (pre-existing) | ds-backend:SKILL.md:249 |  |
| XR-134 | Eşzamanlı çok-kullanıcı uzlaşımı; paylaşılan varlık tek SSOT'tan | integrated | ds-backend:DP-18 |  |
| XR-135 | Kullanıcı-niyeti korunur: bayat-ETag sahte çakışması otomatik çözülür | integrated | ds-backend:DP-19 |  |
| XR-136 | Her yüzey adreslenebilir: route + yer imi + refresh-güvenli açılış | integrated (merged) | ds-frontend:CMP-27 |  |
| XR-137 | Bilgi mimarisi iki katman: kişisel bağlam / paylaşılan çalışma alanı | integrated | ds-frontend:UX-IA-01 |  |
| XR-138 | DOM olay kalıbı: olay-delegasyonu + data-action | covered (pre-existing) | ds-frontend:references/rules-components.md:195 |  |
| XR-139 | Kopya-önleme: deklaratif dedupe-strateji registry'si | covered (pre-existing) | ds-backend:references/rules-database.md:268 |  |
| XR-140 | Singleton sistem dosyalarını yalnız owner oluşturur | integrated | ds-backend:DP-26 |  |
| XR-141 | Çalışma alanı kimliği kalıcı ASCII UUID'dir | integrated | ds-backend:DB-14 |  |
| XR-142 | Rol kalıcılığı SSOT'ta saklanır; girişte izinden türetilmez | integrated | ds-backend:AUTH-15 |  |
| XR-143 | Taksonomi registry'si: rol/kategori/etiket tek kanonik kaynaktan | integrated | ds-backend:DB-15 |  |
| XR-144 | Rol taksonomileri ayrıştırılır: RBAC ≠ alan/hizmet rolleri ≠ kişi r… | integrated | ds-backend:AUTH-16 |  |
| XR-145 | Açık kullanıcı isteği olmadan veri silinmez | integrated | ds-backend:DB-16 |  |
| XR-146 | Yerel istemci deposu restore kaynağıdır (yeniden-inşa edilebilirlik) | integrated | ds-backend:DP-23 |  |
| XR-147 | Domain objeleri sağlayıcının obje modeline eşlenir | integrated | ds-backend:DP-20 |  |
| XR-148 | OAuth robustluk zarfı testlerle korunur | integrated | ds-backend:AUTH-13 |  |
| XR-149 | İstemci-IP yalnız güvenilir proxy arkasında ve en-sağdaki değerden … | integrated | ds-compliance:NET-13 |  |
| XR-150 | Uygulama-içi satın alma makbuzu sunucuda doğrulanır | integrated | ds-productize:MON-15 |  |
| XR-151 | Yüksek-değerli ücretli veri entitlement-bağlı anahtarla şifrelenir | covered (pre-existing) | ds-productize:references/rules-monetization.md:19-24 |  |
| XR-152 | Yıkıcı yanıt bütünlüğü: sessiz sahte-başarı yasak | covered (pre-existing) | ds-backend:SKILL.md:78 |  |
| XR-153 | Yıkıcı işlemler owner-only: sahiplik yetkiden önce doğrulanır | covered (pre-existing) | ds-backend:SKILL.md:156 |  |
| XR-154 | Dışa-dönük iddialar gerçek mimariyle birebir örtüşür | integrated | ds-compliance:PRV-42 |  |
| XR-155 | Her görsel öğe merkezi primitive'den türer | covered (pre-existing) | ds-frontend:references/rules-design-system.md:16-19 |  |
| XR-156 | Tema/palet token SSOT'u: hardcoded renk yasak | covered (pre-existing) | ds-frontend:references/rules-design-system.md:16-19 |  |
| XR-157 | Tek modal: create = edit | integrated | ds-frontend:SCH-02 |  |
| XR-158 | Sürükle-bırak akıcı ve net geri-bildirimli | integrated | ds-frontend:SCH-03 |  |
| XR-159 | Aktif filtre seçimleri yeni kayda ön-doldurulur | integrated | ds-frontend:SCH-04 |  |
| XR-160 | Anında filtre + mute-not-hide | covered (pre-existing) | ds-frontend:references/rules-ux.md:314-320 |  |
| XR-161 | Öğe-özel sağ-tık bağlam menüsü | integrated | ds-frontend:SCH-11 |  |
| XR-162 | Görünür saat aralığı ayarlanabilir | integrated | ds-frontend:SCH-06 |  |
| XR-163 | Takvim render'ı tek-geçiş + tembel yükleme ile optimize edilir | integrated | ds-review:PRF-14 offscreen-rendering rule (~line 157) |  |
| XR-164 | Tam adaptif yerleşim: her viewport'ta taşma/overlap yok | covered (pre-existing) | ds-frontend:references/rules-responsive.md:35 |  |
| XR-165 | Alan-tipi registry'si: giriş/doğrulama/gösterim tek yapıdan | covered (pre-existing) | ds-frontend:references/rules-components.md:125-129 |  |
| XR-166 | Arama davranışı tek SSOT'tan: debounce/eşik/limit/a11y | integrated | ds-frontend:CMP-25 |  |
| XR-167 | UI yazım konvansiyonları tutarlı | integrated | ds-frontend:UX-WR-04 |  |
| XR-168 | Telefon numaraları ülke-bazlı biçimlenir | integrated | ds-frontend:CMP-11 |  |
| XR-169 | Seç-veya-oluştur kalıbı | covered (pre-existing) | ds-frontend:references/rules-components.md:174-179 |  |
| XR-170 | Modal/panel boyutlandırma standardı | integrated | ds-frontend:CMP-10 |  |
| XR-171 | RTL için mantıksal CSS özellikleri varsayılandır | covered (pre-existing) | ds-compliance:references/rules-i18n.md:51-61 |  |
| XR-172 | Kritik özel widget'lar gerçek ekran okuyucuyla test edilir | covered (pre-existing) | ds-frontend:references/rules-accessibility.md:11 |  |
| XR-173 | Sözlük gerçek kullanıcılarla kullanılabilirlik testinden geçer | integrated | ds-compliance:I18N-14 |  |
| XR-174 | Terminal durumdan geçiş korunur (at-least-once teslimat) | integrated | ds-backend:DP-11 |  |
| XR-175 | Yakalanmamış hatalar için üç global kanca birlikte bağlanır | integrated | ds-mobile:DEV-05 |  |
| XR-176 | Orkestrasyon her hedef platformda hazır araçla yazılır | integrated | ds-devops:DOP-37 |  |
| XR-177 | CI'sızlık kararı tüm kardeş repolarda tutarlı uygulanır | integrated | ds-devops:DOP-36 |  |
| XR-178 | Uykuda kalmış kapının ilk gerçek koşusunda birikmiş hata varsayılır | integrated | ds-devops:DOP-34 |  |
| XR-179 | Tek-node yeniden-başlatma güvenli sırayla yapılır | integrated | ds-deploy:DEP-19 |  |
| XR-180 | Prensipler somut-fayda şartıyla bütünsel uygulanır | covered (pre-existing) | ds-review:SKILL.md |  |
| XR-181 | İşlevsel uyum tabanı zorunludur | integrated | ds-review:(next free ID; assign at apply) |  |
| XR-182 | Patch'ler giriş-noktası re-export konumunda yapılır | integrated | ds-review:TST-09 |  |
| XR-183 | Process-global önbellekler her test öncesi autouse fixture ile sıfı… | integrated | ds-review:TST-10 |  |
| XR-184 | Üçüncü-taraf adları vendor-nötr; metin güncel boru hattına karşı ye… | integrated | ds-docs:DOC-24 |  |
| XR-185 | Veri-kaybı olmayan limit ihlalleri yumuşak-uyarıdır | integrated | ds-frontend:UX-14 |  |
| XR-186 | Gelecekteki online rezervasyon/ödeme mimarisi baştan kurgulanır (YA… | integrated | ds-backend:DP-24 |  |
| XR-187 | Randevu zaman seçimi atomik DateTimePicker ile yapılır | integrated | ds-frontend:SCH-09 |  |
| XR-188 | İptal/erteleme risk göstergesi izlenir | integrated | ds-frontend:SCH-12 |  |
| XR-189 | Esnek-aralıklı gelir-gider rapor ekranı | skipped | — | product feature (flexible-range P&L/report screen). Feature specification, not an audit/quality rule; drillabl |
| XR-190 | Firma sitesinde minimal-sorumluluk statik yayın modeli korunur | skipped | — | product-specific hosting-model preservation directive (keep the minimal-responsibility static-publish model fo |
| XR-191 | Görsel sunumu: streç yok, ideal çerçeve, responsive teslimat | integrated | ds-frontend:RSP-07 |  |
| XR-192 | Firma sitesi mobil-dostu ve yazdırma-dostudur | covered (pre-existing) | ds-frontend:references/rules-responsive.md |  |
| XR-193 | Yasal-belge dahil-etme SSOT'tan yönetilir | integrated | ds-compliance:PRV-44 |  |
| XR-194 | Yan-etkili POST'lar Idempotency-Key başlığını destekler | integrated | ds-backend:API-07 |  |
| XR-195 | Stdlib'den çıkarılan modüller açık bağımlılık yapılır | integrated | ds-deps:classification/audit checklist |  |
| XR-196 | Uygulama limitleri altyapının güncel gerçek limitine karşı doğrulanır | integrated | ds-compliance:NET-06 |  |
| XR-197 | Hesap-sınırı değişmezi: firma-sahipli ve ürün-sahipli altyapı asla … | integrated | ds-deploy:DEP-22 |  |
| XR-198 | Ayrıcalık-bağlı runtime yalnız o ayrıcalığı gerektiren işe ayrılır | integrated | ds-backend:DP-25 |  |
| XR-199 | Varsayılan kökten-temiz değişiklik; geriye-dönük uyumluluk yalnız k… | integrated | multi:principles §core |  |

Maintenance: adding/retiring an XR rule updates canonical-xr.json first, then this map; a transferred rule renaming its skill ID updates the target column in the same commit (DOC-18).
