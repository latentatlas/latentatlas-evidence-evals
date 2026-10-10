# R29 — Cusp boyunca hareketi daha uzun bir parçada izledik

23 Eylül 2026. Önceki artış teoremi −1/65536≤ν≤0 aralığındaydı.
Bu turda −1/64≤ν≤0 aralığının tamamına geçildi: uzunluk 1024 katına
çıktı. Bu, örnek nokta sayısının artması değil, aradaki bütün noktaları
kapsayan bir türev sınırıdır:

    1.9×10⁻⁴⁰ < C₄'(ν) < 5.3×10⁻⁴⁰.

Dolayısıyla özgün ν koordinatı arttığında dördüncü katsayı kesin artıyor.
Her iki sürücü arasındaki artış da bu sınırlar ile sürücü farkının
çarpımları arasında kalıyor. Tüm yeni parçada

    2.48374879×10⁻³⁹ < C₄(ν) < 2.49203006×10⁻³⁹.

İki uç arasındaki fark (2.96875,8.28125)×10⁻⁴² içinde. Ayrı sayısal
integral hesabında C₄(−1/64)≈2.48643532077589×10⁻³⁹ ve
C₄(0)≈2.49203005246799×10⁻³⁹. Fark, C₄(0)'ın yaklaşık %0.224505'i.
Bu son yüzdelik bir tanısal tahmindir; rigoröz sonuç yukarıdaki aralıktır.

Buradaki C₄, çekirdeği belirli moment koşullarını sağlayacak biçimde
değiştirirken gereken en küçük genliğin büyük eğim bütçesindeki
açılımına aittir. Bir hesaplama süresi, parasal maliyet veya fiziksel
enerji ölçümü değildir. Yeni sonuç, bu hassas düzeltme katsayısının cusp
üzerinde tek noktaya özgü kalmadığını nicel olarak gösteriyor.

Hesapta 32 yeni merkez kullanıldı. Her merkezde cusp integralleri yeniden
hesaplandı, gerçek çözüm kontraksiyonla çevrelendi ve önceki R03 dalının
teklik kutusunun içine yerleştirildi. Her parçada yardımcı dual optimum,
28 sonlu kök, kökler arasındaki 354 işaret aralığı ve sonsuz kuyruklar
kontrol edildi. Komşu parçaların aynı cusp'a ait olması teklikle; aynı
dual optimuma ait olması global minimizer'ın tekliğiyle gerekçelendirildi.

Yeni merkezleme, ayrı mutlak hataları başlangıçtan sürekli taşımak yerine
önkoşullandırılmış artık türevini yerel merkezden taşıyor. Geniş bir
kutu −1/512≤ν≤0 üzerinde türevin işaretini belirleyemedi. Aynı aralık
dört küçük kutuyla kapatıldığında hepsinde pozitiflik doğrulandı. Bu
denemenin sınırı bir matematiksel yön değişimi değil, fazla geniş bir
çevrelemeydi. Yeni −1/64 ucu en uzak mümkün devam noktası olarak seçilmedi.

Denetim katmanları:

- 14 exact rasyonel koşul, daha geniş sextic kuyruk alanını ve kapsamı kontrol etti.
- 512 bit dışa yuvarlanan ayrı hesap 17.088 eşitsizlik/kontrolü geçti.
  Bunun 1408'i türev formüllerini otomatik türevleyerek yeniden kuran kararlardır.
- 23 ayrı sürücüde 80 ve 110 basamakla toplam 46 orijinal integral çözümü
  yapıldı. 240 türev, 690 noktasal değer karşılaştırması, 92 küçük artık
  kontrolü, 10 adım-boyu karşılaştırması ve 120 hassasiyet karşılaştırması geçti.
  Hassasiyetler arasındaki en büyük göreli türev farkı yaklaşık 4.506×10⁻⁶³.

Rasyonel denetçinin ilk koşusu `RI.contains` adlı mevcut olmayan metodu
çağırdığı için durdu. Sıfırın rasyonel uçlarla dışlanması kontrolüne
düzeltildi; sayısal kabul sınırları değişmedi. Eski kaynak ve başarısızlık
kaydı korundu. Büyük kutunun belirsiz sonucu da saklandı.

Kapanış denetçisindeki ikinci düzeltme, işaret örtüsünün bölme uçlarını
zorunlu olarak sıfır yarıçaplı kabul etmesiydi. Bazı uçlar Arb tarafından
çok dar aralıklar olarak saklanıyor. Yaprakların değerlendirme kutularının
kapsadığı dış uçlar kullanılarak örtü tekrar kontrol edildi; bütün
parçalarda boşluksuzluk geçti. Üretici hesaplar ve kabul eşitsizlikleri
değişmedi; bu başarısız denetim ve eski kaynak da kayıtlarda duruyor.

Kapsam sınırı nettir: her yeni cusp'ta katsayının gerçek optimal değer
açılımındaki anlamı R23'ün ağırlıklı koşullarıyla sürüyor. Ancak R27'nin
sonlu M için açık O(M⁻⁶) hata sabitleri bu yeni aralığa taşınmış değildir.
Gerçek sonlu-M optimumun ν ile monotonluğu, C₄'' işareti, C₆, bütün
[−29,0] eğrisi ve değiştirilmiş çekirdeğin bütün geometrik koşulları açık.

Sonraki bilimsel karar, yalnız daha fazla kutu hesaplamak değil, bu
katsayı hareketinin ana cusp/fold sorusuna ne kattığını açık bir önerme
ile birleştirmek ve etkili kalan sınırını aynı alana taşımanın yararını
değerlendirmek. Literatür önceliği ve bağımsız uzman incelemesi ayrıca
gerekiyor; hesapların geçmesi tek başına yayın kabulü anlamına gelmez.

[İspat](PROOF.md), [tablo](results/TABLE.md),
[grafik](figures/continuation.png), [denetim](REVIEW.md),
[yeniden üretim](README.md).
