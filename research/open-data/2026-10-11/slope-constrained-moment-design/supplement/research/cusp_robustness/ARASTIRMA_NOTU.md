# R07 — Cusp geometrisinin çekirdek hatalarına dayanıklılığı

20 Eylül 2026. **Durum:** Belirtilen yerel kapsam için hesap destekli
sonuç ve ayrı rasyonel denetim tamamlandı. Dış hakem incelemesi ve
literatürde öncelik değerlendirmesi tamamlanmış değil.

## Sorumuz ve elde ettiğimiz cevap

Önceki sonuçlarımız belirli bir Φ çekirdeğine aitti. Bu turda şu soruya
geçtik: **Çekirdeği biraz değiştirirsek aynı cusp eğrisi, çevresindeki
iki fold ve üç köklü bölgenin genişleme yönü korunuyor mu?**

Cevap artık belirli bir hata sınıfı için nicel: Φ_h=Φ(1+h), h gerçek
ve ölçülebilir, tüm parametrelerden bağımsız tek bir fonksiyon ve
|h|≤10^-18 ise, −29≤ν≤0 boyunca bütün bu yapı korunuyor. h düzgün
olmak zorunda değil; dolayısıyla yalnız birkaç örnek fonksiyon
denemedik. Bütün bu sonsuz boyutlu hata sınıfını kapsayan eşitsizlikler
kurduk. Pozitiflik ve çift simetri korunuyor.

**Birbirinden ayrı üç kazanım var:** Çekirdeğin bir komşuluğunda
geometrinin korunduğuna dair açık bir yeter koşul; cusp konumunun bazı
izin verilen değişimlere gerçekten hassas olduğunu gösteren bir yön;
özel olarak kurulan başka bir yönde ise tek cusp'ın sonlu ve daha
büyük genlikte tam yerinde kaldığını gösteren ek sonuç.

## Hangi sonuçlar korundu?

Her sabit h için yeni cusp eğrisinin kendi merkezlerine göre
s=t−t_h, ℓ=λ−λ_h, m=μ−μ_h alınıyor. Eksenler yeniden ölçeklenmiyor.

| Nesne | Kanıtlanan kapsam |
|---|---|
| Cusp eğrisi | −29≤ν≤0 boyunca 58 teklik tüpünde bağlı, analitik bir yay; 57 birleşme kök kapsamasıyla doğrulandı |
| Konum değişimi | Aynı ν'da t,λ,μ koordinatlarının her birinde mutlak değişim <4×10^-5 |
| Sextic kesit | Yeni yay μ=0 kesitini tam bir kez geçiyor; ν koordinatı eski kesişimden <2×10^-4 uzaklaşıyor |
| Yerel kök düzeni | |s|≤0.003, |ℓ|≤10^-6, |m|≤2×10^-9 içinde tam bir/üç kök ayrımı; foldlarda çift+basit, cusp'ta üçlü kök |
| Sonlu genişlik | 0.98ℓ^(3/2)≤W_h≤1.72ℓ^(3/2) |
| Hareket yönü | 0<ℓ≤10^-6 için üst foldun ν türevi negatif, altınki pozitif |
| Ortak hız sınırı | 0.0003ℓ^(3/2)<−∂νW_h<0.003ℓ^(3/2) |

Bu, iki farklı pertürbe çekirdeğin bölgelerinin birbirini kapsadığı
anlamına gelmiyor. Her çekirdek kendi içinde ν boyunca izleniyor.
Merkezlemeyi eski cusp'ta sabit bırakmak aynı teorem değil. Eski Q/S
yüzdelik genişleme değerinin pertürbasyon altında aynen kaldığı da
iddia edilmiyor.

## 10^-18 neden küçük; sonucu değersiz mi yapıyor?

Bu eşik, tüm şekillerde değişebilen bağıl hataya karşı bir **yeter
koşul**. Büyük fiziksel gürültüye dayanıklılık veya en iyi olası eşik
anlamına gelmiyor. Kullanılan tüpler, ortak pencere ve açık sabitler de
hesaplanan eşiği etkiliyor. Küçük sayıyı geniş pratik güvence diye
sunmak doğru olmaz.

Fakat asıl sorun yalnız kaba sınır seçimi değil. Şu açık değişimi ayrıca
inceledik:

Φ_ε(u)=Φ(u)[1+ε cos(2au)], a≈41.40034135868425.

|ε|<1 için bu çekirdek pozitif ve simetrik kalıyor. Tam bir özdeşlik var:

G_ε(t)=F(t)+ε[F(t+a)+F(t−a)]/2.

Quartic cusp t≈a çevresinde bu değişim, integralin salınımlı küçük
değerine t−a≈0'daki salınımsız değerden katkı getiriyor. Cusp koşullarını
yeniden sağlamak için gereken koordinat değişimini örtük türevle
hesapladık. ε=0'da

dμ_cusp/dε≈4.926008495177408×10^11.

Diğer iki bileşen dt_cusp/dε≈−2.777415877599239×10^11 ve
dλ_cusp/dε≈5.315610059314121×10^11. Bunlar hata paylarıyla kapsanan
türevler. Sonlu ε için aynı çarpımın kesin yer değiştirme olduğunu
iddia etmiyoruz; bunun için ayrıca sonlu-ε kalan sınırı gerekir.

Dolayısıyla **konum duyarlılığı ile cusp çevresindeki geometrinin
korunması farklı sorular**. Sabit bir çekirdek çarpanı sıfırları hiç
yerinden oynatmazken, bu kosinüslü yön büyük bir konum türevi üretiyor.
Hatanın hangi yönde olduğu, yalnız büyüklüğü kadar önemli.

Bu örnek 10^-18'in en iyi eşik olduğunu veya 10^-17'de bozulma
olduğunu kanıtlamaz. Daha büyük iki üç-kutu denemesi kayıtlı:
10^-18 geçti; 10^-17'de bazı yeter eşitsizlikler sonuç vermedi.

## Nasıl kontrol ettik?

Yeni kanıt, eski integralleri değiştirmeden hata katkısını pozitif
moment sınırlarıyla kapsıyor. Her türev için
|D_nG_h−D_nF|≤10^-18 B_n kullanılıyor. Yeni cusp konumu için
daralma, dal birleşmeleri, bütün yerel pencere ve fold taşıma
eşitsizlikleri yeniden kuruluyor.

- 110 basamaklı Arb hesabı 58 kutu ve 57 birleşmeyi geçti.
- Arb veya yeni üretici kodunu kullanmayan ayrı rasyonel denetçi,
  **yeni türev Taylor kapsamalarını da yeniden kurarak** aynı 58 kutu
  ve 57 birleşmeyi doğruladı. Polinom açılımları ve fold türevi için
  farklı hesap yolları kullanıldı.
- Açık kosinüslü yön için altı yeni rigoröz integral hesabı yapıldı.
  Üç doğrudan pertürbe-integral mpmath hesabı 10^-80 içinde uyumlu.
  mpmath kısmı bağımsız sayısal destek; rigoröz ispat yerine geçmiyor.
- Eski integral kapsamaları, pozitif moment sınırları ve R03 daralma
  tanıkları yeni denetimin güvenilen girdileri. Dış uzman değerlendirmesi
  bu hesapların başarılı çalışmış olmasıyla tamamlanmış sayılmıyor.

Rasyonel denetçinin ilk sürümü çok dar bir yarıçap karşılaştırmasında
gereksiz yuvarlama genişlemesi üretti. Kesin ikili girdiler o adımda tam
kesir olarak tutularak düzeltildi. Ana sertifika değiştirilmedi;
[tanı kaydı](DIAGNOSTICS.md) ve çalışma defteri bunu açıkça kaydediyor.

## Makalenin bilimsel hikâyesine katkısı

Artık yalnız tek çekirdekte bulunan şekli göstermiyoruz. Aynı yerel
nicel kök diyagramının belirli bir çekirdek komşuluğunda korunduğunu
ve aynı anda konumun bazı yönlerde hassas olduğunu söyleyebiliyoruz.
Bu, önceki geometri ve taşıma sonuçlarıyla aynı soruya bağlı bir ek
teorem oluşturuyor.

Küçük değişim altında dejenerasyonsuz cusp'ın yerel devamı genel
örtük fonksiyon/daralma yöntemlerinin beklenen sonucudur. Cusp'ın
hesap destekli varlığını ve normal formunu doğrulayan yakın bir
çalışma [Lessard–Pugliese](https://arxiv.org/html/2404.00535v2)
makalesidir. Buradaki aday ek bilgi, bu özel integralde **açık bir
hata sınıfı ve eşik, bütün bağlı yay, aynı sonlu kök penceresi ve
iki foldun yönü için ortak nicel güvence** verilmesidir. Bunların
literatürde ilk kez elde edildiği bu turda kanıtlanmadı.

Fiziksel zaman, enerji, kararlılık veya faz geçişi için ayrı bir
model kurulmadı. Bu sonuç akademik derece eşdeğerliği veya yayın
kabulü hakkında bir karar da vermiyor.

## Seçilmiş bir yönde çok daha büyük değişim: cusp tam yerinde kaldı

Üç momenti koruma fikri aynı turda somut bir sonuca dönüştü. İntegral
çekirdeğe doğrusal bağlı olduğundan, belirli bir cusp'taki ilk üç
pertürbasyon momenti tam sıfırsa o nokta **sonlu genlikte de** üçlü
kök olarak kalır. Üçüncü türev ve kontrol rankı ayrıca korunmalıdır.

Dört düşük frekanslı kosinüs modunu bu koşula göre birleştirdik:

h₀(u)=w₁cos(2u)+w₂cos(4u)+w₃cos(6u)+w₄cos(8u).

Yaklaşık katsayılar (−0.6179413550, 0.2914178602, −0.0804226747,
0.0102181101). **Tam katsayıların tanımı bu yuvarlanmış sayılar değil;**
tam cusp'taki üç moment matrisinin kofaktörleri ve bunların mutlak
değerleri toplamıyla yapılan normalizasyon. Bu tanımla ilk üç moment
bir cebirsel özdeşlik gereği tam sıfır ve ‖h₀‖∞=1.

**Yeni yerel sonuç:** Φ_ε=Φ(1+εh₀), −1/2≤ε≤1/2 için pozitif ve
simetrik kalıyor; quartic cusp Q aynı tam noktada dejenerasyonsuz cusp
olarak kalıyor. D₃ ve D₄'ün mutlak büyüklükleri, özgün değerlerinin
en az 0.7995 katı. Bu, yalnız sonsuz küçük değişime ait bir sonuç değil.
Bu yönde bağıl çekirdek değişimi %50'ye kadar çıkabiliyor; tam değeri
u'ya bağlı. Aynı çalışma dört modu keyfî katsayılarla birleştirmek
için bir güvence vermiyor.

Kapsam farkı kritik: **10^-18 sonucu bütün hata yönleri ve bütün
ν yayı için; ±1/2 sonucu özel olarak kurduğumuz tek yön ve tek Q
cusp'ı için.** Büyük genlikte bütün yay, aynı kök penceresi veya
foldların genişleme yönü henüz doğrulanmadı. Cusp tipi korunuyor
diye eski nicel pencereyi otomatik olarak taşımıyoruz.

Bu ek için 40 rigoröz kaydırılmış-frekans integrali, kofaktör
özdeşliğinin tam sembolik kontrolü, ayrı rasyonel eşitsizlik denetimi
ve beş doğrudan mpmath moment kontrolü yapıldı. Rasyonel kontrolün
integral kapsamalarını girdi kabul ettiği açıkça kayıtlı.
[Yerinde kalan cusp sertifikası](results/pinned_cusp_certificate.json),
[ayrı kontrol](results/pinned_check.json), [analitik kanıt](PROOF.md).

## Şimdi daha açıklayıcı araştırma sorusu

**Hangi çekirdek değişim yönleri cusp'ı çok oynatıyor; hangi yönler
konumu ve genişleme düzenini çok daha büyük genliklerde koruyor?**

Yeni hesap bu soruya üç karşılaştırma veriyor: sabit çarpan etkisiz;
belirli bir yüksek frekanslı kosinüs modu yüksek etkili; seçilmiş dört
modun üç momenti koruyan bileşimi ise cusp'ı sonlu genlikte tam
yerinde tutuyor. Cusp'ın ilk tepkisi bütün h fonksiyonundan yalnız üç
integral momenti (r₀,r₁,r₂) üzerinden geçiyor: δc=−J^−1(r₀,r₁,r₂).

Bir sonraki somut soru: **Q'yu yerinde tutan bu tek çekirdek yönünde,
ε değişirken Q'dan çıkan cusp yayı ve çevresindeki fold geometrisi
nasıl değişiyor?** Q'nun yerinin korunduğu artık biliniyor; böylece
geometrinin değişimini konum kaymasından ayırabileceğiz. Bütün yayda
genişleme yönünün ne kadar büyük genliğe kadar korunduğu ve hangi
koşulun ilk sınır olduğu araştırılabilir. Bu sonuç henüz hesaplanmış
veya vaat edilmiş değil; mevcut doğrulanmış çıktının açtığı belirli
bir sonraki soru.

[Analitik kanıt](PROOF.md), [ana sertifika](results/robustness_certificate.json),
[ayrı rasyonel denetim](results/rational_check.json),
[duyarlılık sertifikası](results/condition_witness.json),
[bağımsız kontrol](results/condition_check.json).
