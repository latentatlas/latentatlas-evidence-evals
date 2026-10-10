# R27 — Tek noktadan küçük bir cusp ailesine

22 Eylül 2026. Q'da bulduğumuz pozitif dördüncü düzeltme ve açık hata
kontrolü, cusp eğrisinin Q'ya bitişik kapalı bir aralığına taşındı:
ν∈[−2⁻¹⁶,0]=[−0.0000152587890625,0]. Bu küçük ama açıkça belirtilmiş
bir başlangıç aralığıdır. Önceki [−29,0] eğrisinin tamamı kapsanmıyor.

Her cusp noktasında moment hedefleri için gereken en küçük değişiklik
genliğini δ_ν(M) ile gösteriyoruz. M eğim sınırı. Her ν için farklı
bir çekirdek değişikliğine izin veriliyor; tek bir değişikliğin bütün
eğriyi aynı anda sağlaması araştırılmadı.

Aralıktaki her ν ve her M≥2×10⁻⁵ için

    δ_ν(M)=δ₀(ν)+C₂(ν)/M²+C₄(ν)/M⁴+E_ν(M),
    2.47×10⁻³⁹<C₄(ν)<2.52×10⁻³⁹,
    −1.02×10⁻⁵³/M⁶<E_ν(M)<1.64×10⁻⁵³/M⁶.

Katsayılar cusp üzerinde değişiyor. Q'daki tek katsayı listesini diğer
noktalara yerleştirmiyoruz. Ortak olan, bu değişen katsayıların işaret ve
hata sınırlarıdır. Baş yaklaşım δ₀(ν)+C₂(ν)/M² bütün bu nokta/bütçe
çiftlerinde minimum genliği eksik tahmin eder.

M=2×10⁻⁵'te ortak mutlak hata üst sınırı 2.5625×10⁻²⁵; bu,
dördüncü terimin %0.001660'ından küçüktür. Sınır tam matematiksel
katsayılarla yazılmış formül içindir; ondalık belirsizliği ayrıca eklenir.

Temel iş, noktaya bağlı en iyi yardımcı katsayı b*(ν)'yi uniform
contraction ile takip etmekti. İlk kaba kutu katsayı işaretleri için
yeterince dar değildi. Aynı contraction'ın verdiği daha küçük çözüm
kutusuyla, ν aralığını küçültmeden pozitif C₄ çevrelemesi elde edildi.
νu⁶ teriminin yerel türevlere ve sonsuz kuyruklara etkisi dahil edildi.

İki hassasiyette beş cusp noktasını ve dual çözümlerini orijinal
integrallerden yeniden hesapladık; çevrelemelerle uyuştular. Bu örneklerde
ν arttıkça C₄ çok az artıyor: uçlar arasındaki göreli değişim yaklaşık
2.195 ppm. Bu sayısal gözlem bir monotonluk teoremi değildir.

Sonuç, pozitif dördüncü düzeltmenin belirtilen yakın cusp ailesinde
korunduğunu nicelleştiriyor. İşaretin süreklilikle yerel korunması tek
başına yeni bir genel ilke değildir. Buradaki ek içerik; açık parametre
aralığı, hareketli dual çözüm, sonsuz kuyruk ve ortak etkin hata sınırıdır.

Aralığın en geniş olduğu, bütün cusp eğrisinin kapsandığı, C₄'ün
monotonluğu veya C₆'nın varlığı iddia edilmiyor. Her yeni tasarımın
dördüncü türev/rank koşulları ayrıca doğrulanmadığı için, sonuç tek
başına bütün tasarımların tam geometrik sınıflandırması da değildir.
Bağımsız uzman incelemesi açık.

[İspat](PROOF.md), [sayılar](results/TABLE.md), [denetim](REVIEW.md),
[grafik](figures/cusp_uniformity.png), [yeniden üretim](README.md).
