# R28 — Cusp boyunca dördüncü katsayı gerçekten artıyor

22 Eylül 2026. Önceki grafikte gözlem olarak gösterdiğimiz C₄ artışı,
aynı küçük aralık için türev sınırıyla doğrulandı:

    ν∈[−2⁻¹⁶,0],
    2.82×10⁻⁴⁰<C₄'(ν)<4.35×10⁻⁴⁰.

Dolayısıyla ν arttıkça C₄ kesin olarak artar. Aralıktaki herhangi iki
nokta arasındaki artış da türev sınırları ile aradaki ν farkının
çarpımları arasında kalır. Bu sonlu sayıda örnekten çıkarılan bir sonuç
değil; hareketli cusp, hareketli optimal dual çözüm, kök hızları ve
bütün sonsuz türev kuyruğu hesaba katıldı.

C₄, moment koşullarını sağlamak için gereken en küçük çekirdek
değişikliği genliğinin büyük eğim bütçelerinde açılımındaki dördüncü
katsayıdır. Elde edilen hareket, bu katsayının özgün ν koordinatına
göredir. C₄'ün artması tek başına gerçek sonlu-M minimumun arttığını
göstermez; bunun için kalan terimin ν türevini de kontrol etmek gerekir.

Q(0)'daki daha dar katsayı çevrelemesiyle birleştirince bütün aralıkta

    2.49202340×10⁻³⁹<C₄(ν)<2.49203006×10⁻³⁹

elde ediliyor. Önceki ortak bandın belirgin biçimde daralması, yeni
türev bilgisinin doğrudan bir sonucudur. Tam kısa aralık boyunca artış
4.302978515625×10⁻⁴⁵ ile 6.6375732421875×10⁻⁴⁵ arasındadır.

Rasyonel denetçi, üreticinin açık türev formüllerini aynen kopyalamak
yerine kök katkılarını otomatik türevleme ile yeniden kurdu. İkinci
kontrol, yakındaki cusp ve dual denklemlerini orijinal integrallerden
çözüp iki adım büyüklüğüyle sonlu fark aldı; bu hesap analitik C₄'
formülünü kullanmadı. Her iki kontrol yayımlanan pozitif bandın içinde.

26 exact kontrol grubu, 44 rasyonel karar, iki hassasiyette toplam 26
integral sistemi çözümü ve 146 sayısal karşılaştırma geçti. 72 hassasiyet
karşılaştırmasında en büyük göreli fark yaklaşık 2.787×10⁻⁶².
Sonlu farklar tanısaldır; bütün aralık için kanıtın yerine geçmez.

Bu aralık hâlâ küçüktür: [−0.0000152587890625,0]. Bütün [−29,0]
cusp eğrisine, C₄'' işaretine, C₆ katsayısına veya değiştirilmiş
çekirdeklerin bütün geometrik koşullarına ilişkin yeni iddia yoktur.
İspat ve hata kapsamaları kayıtlıdır; bağımsız uzman incelemesi açık.

Bir sonraki anlamlı derinleştirme, bu hareketin daha uzun bir cusp
parçasında sürüp sürmediğini ve sınırına gelindiğinde hangi matematiksel
koşulun değiştiğini araştırmaktır. Tek başına başarısız bir çevreleme,
gerçek bir işaret değişimi diye yorumlanmamalıdır.

[İspat](PROOF.md), [sayılar](results/TABLE.md), [denetim](REVIEW.md),
[grafik](figures/coefficient_motion.png), [yeniden üretim](README.md).
