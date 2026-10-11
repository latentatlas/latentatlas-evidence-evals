# R31 — Gerçek optimumun artışı için küçük mesafe koşulu kaldırıldı

23 Eylül 2026. Bu turda [−1/64,0] cusp parçasında, her M≥2×10⁻⁵ için
gerçek optimal genliğin ν ile kesin arttığını gösteren bir ispat ve
hesap doğrulaması elde edildi. Artış artık yalnız seçilmiş düğümler
veya yeterince uzak iki nokta için değil, bu aralıktaki her ν₁<ν₂ için.

δ_ν(M), ilk üç momenti koruyup üçüncü t-türevi hedefini sağlayan,
eğimi M ile sınırlı bir pertürbasyonun en küçük mümkün genliği.
Her ν'de çekirdek, hedef f_ν ve seçilebilecek pertürbasyon ayrıdır.
Buradaki maliyet/genlik, para, eğitim süresi veya fiziksel enerji değildir.

Yeni sonuç, d=ν₂−ν₁ ve η=τ(ν₁)/τ(ν₂)>1 ile

    δ_ν₂(M) ≥ η exp(d/50) δ_ν₁(M) > δ_ν₁(M),
    δ_ν₂(M) − δ_ν₁(M) > 2.07×10⁻¹¹ d.

Bunlar güvenli alt sınırlardır; en iyi sabit oldukları iddia edilmiyor.
Örneğin uçlar arasındaki farkın bu yoldan alt sınırı 3.234375×10⁻¹³.
R30'un uçlar için alt sınırı daha güçlü kalır. R31'in kazancı, keyfî
küçük pozitif ayrımlarda da sonuç vermesi ve bunun nedenini açıklamasıdır.

**Nasıl elde edildi?** ν₂'deki uygun g'yi ν₁'e

    g₁(u) = (f₁/f₂) η⁴ [w₂(ηu)/w₁(u)] g₂(ηu)

ile taşıyoruz. Değişken dönüşümünde dört moment koşulu tam korunuyor.
Sonra bu taşımanın hem genliği hem eğimi küçülttüğünü gösteriyoruz.
Böylece ν₂'deki en iyi tasarım bile ν₁'e daha küçük genlikle
aktarılabiliyor. Bu, gerçek optimumları doğrudan sıralıyor; optimumun
türevini veya eşsiz olmasını varsaymıyor.

Taşımanın yeter koşulu, r+κ+a₀|rᵤ|≤−1/50 eşitsizliğinin her u≥0
ve bütün cusp aralığında sağlanması. 32 cusp hücresinin parametre
sınırları, 1.024 tam u aralığı ve sonsuz kuyruk birlikte kullanıldı.
Arb sonlu-bölge üst sınırı <−0.0217069, ayrı rasyonel sınır <−0.0217085;
sonsuz kuyruk için üst sınır <−0.0511166. Hiçbiri yalnız nokta örneklemesi değil.

31 exact cebir grubu ve 19.017 rasyonel denetim geçti. Ayrıca 60 ve
90 basamakta, orijinal theta toplamıyla toplam 24 integral dönüşümü,
30 uzaysal türev ve 10 bileşke özdeşliği sayısal olarak kontrol edildi.
Bunların son grubu teşhis amaçlıdır; sertifikanın yerine geçmez.
Dört geliştirme hatası ve düzeltmesi [kayıtta](diagnostics/README.md).

Bu sonuç çalışmaya bir açıklama ekliyor: artış, uygun pertürbasyonları
birbirine taşıyan bir dönüşümün daralmasıyla ilişkili. Yeter koşul
pozitif ağırlıklı benzer moment aileleri için de yazılabiliyor; somut
uygulama burada doğrulanan theta cusp ailesidir. Ağırlıklı bileşke ve
karakteristik yöntemleri bilinen araçlardır; özel sonucun özgünlüğü
ayrıca literatür karşılaştırması ve uzman okuması gerektirir.

**Açık kalanlar:** normalize dördüncü terim Z_M'nin keyfî yakın ν'lerde
monotonluğu, gerçek optimumun türevlenebilirliği, optimum profilinin
tekliği, kalan terimin ν-türevi, C₆, M<M₀, bütün [−29,0] dalı,
ortak tek profil/hedef ve fiziksel karşılık. Bu sonuçlar R31'den otomatik
çıkmaz. Dış hakem onayı, formal ispat ve yayın kabulü elde edilmiş değil.

[İspat](PROOF.md), [sayılar](results/TABLE.md),
[grafik](figures/order_transport.png), [denetim](REVIEW.md).
