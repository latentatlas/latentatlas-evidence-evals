# R30 — Katsayı hareketinden gerçek tasarım değerine

Bu aşamada önceki katsayı incelemesini, sonlu eğim bütçesi altındaki
gerçek optimizasyon problemine bağladık. Çalışılan aralık
ν∈[−1/64,0]; ortak bütçe koşulu M≥2×10⁻⁵. M, g'nin ne kadar hızlı
değişebileceğini sınırlayan Lipschitz bütçesi. δ_ν(M), moment koşullarını
sağlamak için gereken en küçük ||g||∞ genliği. Buradaki maliyet bir
para, hesaplama, eğitim veya enerji maliyeti değil.

## 1. Kalan hata bütün genişletilmiş aralıkta kontrol altında

P₄,ν(M)=δ₀(ν)+C₂(ν)/M²+C₄(ν)/M⁴ için

    −1.02×10⁻⁵³/M⁶ < δ_ν(M)−P₄,ν(M) <1.64×10⁻⁵³/M⁶.

Önceki R27 sonucu sadece [−1/65536,0] içindi. Bu turda aynı hata
sabitlerini ve M başlangıcını koruyarak 1024 kat uzun aralığın tamamını
kapsadık. R29'daki 32 kapalı hücrenin her biri üzerinde yerel türevler,
işaret örtüsü, moment düzeltmesi ve skaler tersleme yeniden hesaplandı.
νu⁶ teriminin sonsuz kuyruk üzerindeki türev etkisi de yeni aralıkla
kontrol edildi. Bu bir sonlu örnekleme sonucu değil.

## 2. Üç katsayının da hareket yönü belirlendi

Orijinal ν koordinatında, aralık boyunca

| Türev | Kesin alt sınır | Kesin üst sınır |
|---|---:|---:|
| δ₀′(ν) | 2.7×10⁻¹¹ | 3.0×10⁻¹¹ |
| C₂′(ν) | 7.4×10⁻²⁶ | 8.7×10⁻²⁶ |
| C₄′(ν) | 1.9×10⁻⁴⁰ | 5.3×10⁻⁴⁰ |

Bu işaretler sonlu fark grafiğinden okunmadı. R29'un doğrulanmış
türev girdileriyle katsayı ifadeleri ayrı rasyonel otomatik türevleme
hesabında yeniden değerlendirildi.

## 3. Gerçek optimal değerleri sıralayabiliyoruz

Aynı M için ν₁<ν₂ alındığında katsayıların artışı ile iki kalan
hatasının toplamı karşılaştırılıyor. Genel eşitsizlikler
[ispatta F7 ve F9](PROOF.md) yazılı. Kullanımı kolay iki yeterli koşul:

- ν₂−ν₁≥1.54×10⁻¹⁴(M₀/M)⁶ ise δ_ν₂(M)>δ_ν₁(M).
- Z_M(ν)=M⁴[δ_ν(M)−δ₀(ν)−C₂(ν)/M²] için
  ν₂−ν₁>0.00035(M₀/M)² ise Z_M(ν₂)>Z_M(ν₁).

M₀=2×10⁻⁵. Özellikle ν_k=−1/64+k/2048, k=0,…,32 noktalarının
hem gerçek optimal değerleri hem Z_M değerleri, bütün M≥M₀ için
kesin artan sırada. Bu 33 nokta, genel iki-nokta eşitsizliğinin kolay
görülen bir sonucu; sonuç yalnızca bu noktalara sınırlı değil.

M=M₀ için aralığın iki ucu arasında

    4.21877890×10⁻¹³ < δ_{ν=0}(M₀)−δ_{ν=−1/64}(M₀) <4.68753399×10⁻¹³.

İlk iki terim çıkarıldığında kalan etkinin karşılaştırması da
2.90225×10⁻⁴² < Z_M₀(0)−Z_M₀(−1/64) <8.34775×10⁻⁴².
Dolayısıyla C₄'ün hareketi, sonlu M'de gerçek optimal değerin kalan
kısmında da nicel olarak görülebiliyor; sadece formal bir katsayı
hesabı olarak kalmıyor.

Her ν'de hedef f_ν ve yoğunluklar değişiyor; karşılaştırılan şey bu
tanımlı problemlerin minimum genlikleri. Her noktaya aynı sayısal hedefi
ve aynı pertürbasyonu dayattığımız sonucu çıkmıyor.

## 4. Açık sınır

Birbirine keyfî derecede yakın bütün ν çiftleri için monotonluk
kanıtlamadık. Değerler üzerindeki hata sınırı, kalan hatanın türevini
sınırlamaz. Yeterli mesafe koşulu sağlanmadığında sonuç belirsizdir;
bu, ters sıralama bulunduğu anlamına gelmez. C₆, tüm [−29,0] eğrisi,
aynı g'nin bütün aralığı çözmesi ve her değiştirilmiş çekirdeğin ek
geometrik rank koşulları da bu sonucun dışında.

Bu aşama makalenin iddiasını güçlendiriyor: katsayı formülü, parametre
duyarlılığı, bütün bir (ν,M) bölgesindeki açık hata ve gerçek optimal
değer karşılaştırması aynı ispat zincirinde birleşiyor. Literatürde
öncelik, dergi kabulü veya doktora/postdoc seviyesi bu hesapla tek başına
belirlenmiş olmuyor.

## 5. Kayıt ve denetim

12 exact kuyruk-cebir grubu, 4064 rasyonel kontrol ve 146 exact
karşılaştırma kontrolü kaydedildi. Arb ile üretilen aralıkların
transandantal girdileri, ayrı rasyonel aritmetik denetiminin açık
girdileridir; iki denetim aynı şeyi yaptığı iddiasında değiliz.
`--with-arb` denetimi ayrıca R30 ve R29 bağımlılık zincirini yeni
dizinde yeniden üretip çıktı baytlarını karşılaştırır.

[Grafik](figures/finite_design_comparison.png) gerçek değerlerin
kanıtlanmış aralıklarını gösterir. Çizilmiş bir yaklaşık optimum
eğrisi yoktur. [Denetim kaydı](audit_report.json) ve
[inceleme sınırları](REVIEW.md) hesaplamayla analitik gerekçeyi ayırır.
