# Stop Scope — güncel inceleme yolu

16 Ekim 2026 · Huseyin Buldurgan

**Araştırma sorusu:** Ana ajan çalıştırmasını durdurmak, ondan önce kabul edilmiş işlerin etkilerini hangi koşullarda durdurur; bunu hangi kanıtlarla ve meşru yeni işleri engellemeden doğrularız?

- [Güncel makale v1.2 — PDF](../../paper/v1.2/Verifying_Stop_Scope_v1.2.pdf)
- [Düzenlenebilir Word](../../paper/v1.2/Verifying_Stop_Scope_v1.2.docx)
- [İngilizce sonuç tablosu, yöntem ve doğrulama komutları](README.md)
- [Beş canlı kalıcılık bölümünün bütün seçili kayıtları](live-persistence/README.md)
- [Hesapsız, yeni model çağrısı olmadan yeniden çalıştırılabilen deney](receiver-reproducer/README.md)
- [286 vakanın tek tek kapsam haritası](COVERAGE_MAP.json)

## Yeni karşılaştırma ne gösteriyor?

Alıcı servisin kabul ettiği işi, ana çalıştırmanın kesilmesi tek başına ortadan kaldırmadı. Bellekte tutulan geri alma kararı da alıcı yeniden başlatılınca korunmadı. Tek işlemin kalıcı iptali o işlemi engelledi; aynı kökenden sonraki iki programlanmış iş yine gerçekleşti. Köken yetkisinin kalıcı geri alınması, bu düzeneğin dosya yolunda üçünü de engelledi. Bağımsız I ve yeni insan yetkisiyle başlayan N işlerinin raporları sağlıklı referansla aynı kaldı.

Canlı model kullanılan beş bölümde 64 istek bulunuyor. Takip işlerini temsil eden C programlanmış; ana görev O'ya doğal dilde “dur” denmiyor, framework çalıştırması kesiliyor. Ölçülen şey modelin itaatsizliği değil, kabul edilmiş işin ve kontrol kararının kapsamı.

Dört ayrı dur-özeti nihai analiz değerlerini de aktardı. Özetler alıcı kontrolünden ve yeniden başlatmadan önce verildi. Dolayısıyla dosyayı engellemek ile bilgi teslimini sınırlamak aynı sonuç değil.

## Çalışmanın bütünü nerede?

İlk sprint çalışması 26 koşul ve aynı bilgisayardaki tekrarından oluşuyordu; aktörler programlanmıştı. Yeni makale bu başlangıcı koruyor, canlı kalıcılık karşılaştırmasını ve gerçek ayrı süreçlerle yeniden çalıştırılabilen 12 ana koşul + 4 hata kontrolünü ekliyor. Yayın, bütün geliştirme arşivinin dökümü değil; tamamı incelenebilir iki pakete dayanan güncel bir araştırma teslimi.

15 Ekim kapsam değerlendirmesinde 286 vakanın 29'unda doğrudan, bu 29 dahil 68'inde doğrudan veya kısmi deney kanıtı var. Seçili yerel kapsamda iki teknik paket kapalı; tam katalog kabul zinciri henüz **0/286**. Katalog 24 aile ve etkileşim zincirlerinden oluşuyor. Hedef, bu programın tamamlanması ve kritik hatların birden fazla canlı modelle sistematik sınanması; bu teslim hedefi küçültmüyor.

Mevcut kayıtları yeniden hesaplamak ücretsiz ve çevrimdışı. Yeni sağlayıcısız deney de hesap gerektirmiyor. Yeni canlı model koşusu ve kontrolü başka bir ajan sistemine uyarlamak ayrı işlerdir.
