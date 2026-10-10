# R19 — Yeni makale çekirdeği için okuma notu

21 Eylül 2026. Bu metin eski makalenin yamalanmış sürümü değildir. Araştırma
defterinde geliştirilen ve R17'de yeniden denetlenen sonuçlardan yeni bir
makale gövdesi kurulmuştur. R18'in literatür ayrımları doğrudan bu gövdeye
işlenmiştir. Bu tur yeni teorem, çekirdek örneği veya sayısal sabit eklenmemiştir.

## Metnin esas sorusu

**Belirli momentleri tam koruyarak pozitif bir çekirdeği değiştirirken,
değişimin eğimine sınır koymak, gereken en küçük genliği ne kadar artırır?**

Buradaki genlik, çekirdeğe çarpılan `1+h(u)` içindeki h'nin en büyük mutlak
değeridir. Eğim sınırı, h'nin özgün u koordinatında ne kadar hızlı değiştiğini
sınırlar. Bir para, enerji, eğitim veya bilgisayar çalışma süresi ölçüsü değildir.

Cusp araştırması bu sorunun somut kaynağıdır. Başlangıçtaki üç katlı sıfırı
yerinden oynatmadan en az dört katlı sıfıra geçirmek için dört moment
eşitliği gerekir. Pozitifliği, tam dört katlılığı ve üç kontrol yönünün
bağımsızlığını koruyan düzgün tasarımların aynı infimuma yaklaşabildiği de
ayrıca gösterilir. Böylece moment optimizasyonu geometrik soruya geri bağlanır.

## Okunacak ana zincir

1. **Bölüm 1–2:** problem, normalizasyon, bilinen moment dualitesi ve bilinen
   KR normuyla eşleme. Bunlar yeni yöntem olarak sunulmuyor.
2. **Teorem 3.1:** basit ve ayrık geçişler, toplanabilir yerel türevler ve
   seçilmiş geçişlerde moment rankı altında tam baş katsayı:
   `δ(M)=δ*+C*/M²+o(M⁻²)`.
3. **Bölüm 4:** varsayımların özel theta çekirdeğinde doğrulanması. Yuvarlanmış
   merkez değil sertifikadaki tam Q kullanılıyor. Sonsuz sayıdaki geçişin
   kuyruğu dahil; 28 geçiş yalnızca [0,1] içindeki sayıdır.
4. **Önerme 4.1:** düzgün, pozitif ve dejenere olmayan geometrik tasarımlar
   için aynı infimum. Düzgün minimumun elde edildiği iddia edilmiyor.
5. **Teorem 5.1:** her M≥0,00002 için açık alt ve üst hata. Baş terimin ek
   genliği tahminindeki bağıl hata bu eşikte %0,1178'den küçük.
6. **Ek A:** bilgisayar destekli sonuçların tam girdileri, kuyruk hesapları,
   sertifika arayüzü ve yeniden üretimin güven sınırı.

## R17'deki açıklamalar metne nasıl girdi?

- Sonsuz geçiş toplamının iki kez türevlenebilmesi için açık C² üst sınırları
  yazıldı; örtülü C³ varsayımı eklenmedi.
- Sabit noktanın yalnızca `B S=0` değil `S=0` verdiği, B'nin tersinirliğiyle
  gösterildi. Parametre sürekliliği tüm bütçe aralığını kapsıyor.
- B₂ ve A₃ sonsuz kuyruğu içeriyor; A₄ yalnızca üç taşınan merkezi içeriyor.
- Alt hata hesabındaki negatif Taylor alt sınırı, pozitif kısım adımıyla
  ele alındı. Üst hesapta `D* e=α L` çarpanı korundu.
- Sınırsız optimum, sonlu eğimli optimum ve moment düzelten sabit nokta
  farklı nesneler olarak kullanıldı; tekliği kanıtlanmayan nesneye tek denmedi.

## Üç şeklin rolü

Şekil 1 yerel geçişin neden kuadratik ek bedel ürettiğini anlatır.
Şekil 2 hangi dual geçişlerin baş katsayıya katkı verdiğini gösterir.
Şekil 3 açık hata bandını gösterir. Şekiller önceki dondurulmuş paketlerden
baytları değişmeden alınmıştır; dosya kimlikleri `inputs.json` içindedir.

Grafiklerdeki geçişler F'nin sıfırları değildir. Hata bandı istatistiksel
güven aralığı değildir. Sayısal ramp tanığı da sonlu-M probleminin tam
optimumu değildir. Bu ayrımlar şekil açıklamalarında yer alır.

## Bu metin ne ölçüde hazır?

Artık konu, varsayımlar, ispatlar ve sayısal örnek tek bir okunabilir
makale çekirdeği oluşturuyor. Ana iddia, koşullu bir genel teoremle
bilgisayar destekli özel bir uygulamayı birleştiriyor. Bu, eski makalenin
dağınık iddialarından daha net bir değerlendirme nesnesi sağlar.

**Hakemli dergiye gönderime hazır olduğu henüz söylenmiyor.** Dışarıdan bir
uzmanın analitik zinciri eleştirmesi ve en yakın sonuçlarla teorem düzeyinde
karşılaştırma hâlâ değerli. Çalışmanın tamamlanmış yazarlık/kurum bilgileri,
kod ve veri lisansı, kamusal arşiv adresi ve dergi biçimi de ayrıca
belirlenmeli. Bunlar matematiksel sonuçların yerine geçmez.

Sonlu-M optimumunun tam şekli veya tekliği, M⁻³ teriminin keskinliği,
cusp eğrisi boyunca uniform sonuç, yeni bir fizik modeli veya AI uygulaması
bu makalenin iddiası değildir. Gelecekte araştırılabilir olmaları bugün
kanıtlandıkları anlamına gelmez.

Öncelik iddiası da sınırlıdır: okuduğumuz kaynaklarda tam teoremle birebir
aynı sonuç belirlenmedi; literatürde bulunmadığı sonucuna varılmadı.
Makale gövdesinde “ilk”, “yeni evrensel yasa” veya yayın kabul güvencesi yoktur.

## İzlenebilirlik

- [İddia–kaynak haritası](CLAIM_SOURCE_MAP.md)
- [LaTeX kaynak metni](manuscript.tex)
- [Üretim ve kontrol talimatları](README.md)
- [Kaynak dosya kimlikleri](inputs.json)
- [Tam-kesir aktarım kontrolleri](data_checks.json)

Önceki 19 manifest ve 859 kayıtlı dosya girdisi yeni metin hazırlanırken
korunmuştur. R19 ayrı bir paket olarak kapanır; çalışma defteri ve masaüstü
yayın hazırlık kopyası yeni metne bağlanır.
