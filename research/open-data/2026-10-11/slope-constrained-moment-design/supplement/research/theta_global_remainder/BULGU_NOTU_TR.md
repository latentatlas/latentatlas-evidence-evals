# R26 — Sonlu bütçe aralığından bütün büyük bütçelere

22 Eylül 2026. Önceki R25 sonucunun üst bütçe sınırını kaldırdık.
Sabit theta cusp noktamız ve daha önce tanımlanan exact katsayılar için

    δ(M)=δ₀+C₂/M²+C₄/M⁴+E(M),   M≥2×10⁻⁵,
    −9.593×10⁻⁵⁴/M⁶<E(M)<1.488×10⁻⁵³/M⁶.

Burada δ(M), üç koruma momentini ve hedef momenti sağlayan çekirdek
değişikliğinin mümkün olan en küçük maksimum genliği; M, bu değişikliğin
ne kadar dik olabileceğine koyduğumuz matematiksel sınırdır. δ₀ eğim
sınırı olmadığındaki eşik, diğer terimler eğim sınırının ek maliyetidir.
M'nin para, donanım veya model eğitimiyle doğrudan bir özdeşliği yoktur.

Önceki ispat yalnız 2×10⁻⁵≤M≤2×10⁻³ için geçerliydi. Bu aralığı
uzatmak, aynı grafikte daha fazla nokta hesaplayarak sağlanamazdı:
sabit bırakılan sonsuz kuyruk, geçişler inceldikçe gereken hata
mertebesini garanti etmiyordu. Şimdi geçiş genişliğine göre değişen
sonlu bir kök listesi kullanıyoruz. Geçişler inceldikçe bu liste büyüyor;
liste dışında kalan bütün kökler ve integral kuyruğu ağırlıklı
eşitsizliklerle sınırlandırılıyor. Orijinal sonsuz problem korunuyor.

Kök sayısının değişmesi profil ailesinde sürekliliği garanti etmiyor.
Bu yüzden önceki ara değer argümanını olduğu gibi taşımadık. Yardımcı
bir skaler polinomun kökü, her bütçede momentleri tam sağlayan bir
profilin varlığını veriyor. O polinomun kökünün tek olması, gerçek
sonsuz boyutlu optimumun tek olması anlamına gelmiyor.

Bu adımın iki somut kazanımı var:

1. Dördüncü mertebe açılımının kalanı artık M→∞ için açık sabitli
   O(M⁻⁶) ile kontrol ediliyor. Belirli bir sonlu pencereden daha güçlü
   bir optimal-değer sonucu elde edildi.
2. C₄>0 ve kalan sınırı birlikte, δ₀+C₂/M² yaklaşımının bütün
   M≥2×10⁻⁵ için gerçek minimum genliği eksik tahmin ettiğini gösteriyor.
   Bu başlangıç yeterli; mümkün olan en küçük başlangıç olduğu iddia edilmiyor.

Başlangıç bütçesinde |E|<2.325×10⁻²⁵. Bu, dördüncü terim C₄/M⁴'ün
%0.001493'ünden küçük. M on katına çıkarsa, mutlak hata üst sınırı
bir milyon kat; dördüncü terime göre hata üst sınırı yüz kat küçülüyor.
Bunlar gerçek hatanın ölçümü değil, kanıt zincirinden çıkan sınırlardır.
Teorem exact katsayılar içindir: basılı δ₀,C₂,C₄ değerlerinin ondalık
yuvarlama hatası ayrıca eklenmelidir.

Kapsam sabit Q'dur. Cusp eğrisi boyunca uniformluk, C₆ katsayısı,
sonlu M'deki optimum profilin tam biçimi ve yayın özgünlüğü bu adımla
çözülmüş sayılmıyor. O(M⁻⁶), M⁶E(M)'nin bir limite yakınsadığını
tek başına göstermez. Dış hakem incelemesi veya formal ispat yok.

Kontroller: 22 tam cebir/eşitsizlik grubu, 22 rasyonel karar eşitsizliği,
120 basamak Arb çevrelemeleri; iki hassasiyette 600 ayrı tanısal yerel
eşitsizlik ve 40 hassasiyet karşılaştırması. Önceki R25 aralık hesabı
da yeniden üretildi. Kontrol sayısı analitik ispatın yerine geçmiyor;
hangi yükümlülüğün hangi kanıtla karşılandığı [REVIEW](REVIEW.md)'de.

[İspat](PROOF.md), [sayısal kayıtlar](results/TABLE.md),
[grafik](figures/global_fourth_order.png), [yeniden üretim](README.md).
