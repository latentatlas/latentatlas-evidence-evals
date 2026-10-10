# R17 — R15–R16 ortak denetimi

21 Eylül 2026. Bu tur yeni matematiksel sonuç veya genişletme eklenmedi.
R15'in keskin baş katsayısı, R16'nın açık kalan terimi, kod/çıktı zinciri
ve yakın literatür birlikte kontrol edildi. **İncelenen kapsamda ana
sonuçları geri çekmeyi veya sayısal sabitleri değiştirmeyi gerektiren
hata bulunmadı.** Bu, bütün olası hataların dışlandığı veya dış hakem
incelemesinin tamamlandığı anlamına gelmez.

## 1. Hesapların yeniden üretimi

[Koşu aracı](replay_chain.py) önce 17 eski manifestin 811 dondurulmuş
dosya girdisini kontrol etti. R15/R16'nın kendi donmuş denetimleri
özgün ağaç üzerinde salt okunur çalıştırıldı. Sonra ayrı geçici ağaçta:

1. R15 sertifikası yeniden üretildi ve geçici ağaca yerleştirildi.
2. R15 rasyonel denetçisi bu yeni sertifikayı okudu; cebir ve iki
   hassasiyetli mpmath kök/integral kontrolü yeniden çalıştı.
3. R16 üreticisi yeni R15 sertifikasını ve denetim çıktısını okudu.
4. Yeni R16 sertifikasıyla rasyonel, cebir, türev ve ramp kontrolleri çalıştı.

Toplam **11 başarılı koşu**, **9 yeniden üretilmiş sonuç dosyası**,
**2.966 birebir aynı dyadik aralık** ve **832 aynı diğer değer** var.
14 değişiklik yalnız zamanlama ve yeni girdilerin hash metadata'sıdır;
matematiksel değişiklik yok. Eski kaynak/çıktılar sonunda tekrar hash
ile denetlendi, geçici ağaç silindi. Ayrıntılar:
[rapor](replays/report.json), [koşular](replays/runs.json),
[karşılaştırmalar](replays/comparisons.json).

Yeni [hedefli tam-kesir denetimi](check_review_algebra.py) eski aralık
yardımcısını kullanmadan **19 kontrol** yaptı: sekiz qⱼ türev özdeşliği,
yedi doğrudan parçalı geçiş integrali, üst hata cebiri, iki alt kayıp
katsayısı ve tam dyadik B determinantı. Sonuç [burada](results/review_algebra.json).
R15/R16'nın önceki 6+5 cebir kontrolü ayrıca yeniden çalıştı.

R16'nın iki hassasiyette toplam 3.360 türev örneği ve sayısal ramp
tasarımı da tekrar uyum verdi. Bunlar örnekleme/nümerik destek;
aralığın tamamının ispatı ya da ikinci bir bağımsız rigorous integral
motoru değildir. Standart kütüphane denetçisi cebirsel sonuçları ayrı
kuruyor ama yerel transcendental kutuları ve önceki integralleri girdi
olarak kabul ediyor. Tekrar üretim bu güven sınırını ortadan kaldırmaz.

## 2. Bulgular ve düzeltmeler

| Kimlik | Önem / durum | Bulgu ve gerekçesi | İşlem |
|---|---|---|---|
| F01 | İspat açıklaması, kapatıldı | R15 §3 sonsuz serinin C² olduğunu doğru majorant fikriyle söylüyor; türev majorantını açık yazmak denetlenebilirliği artırıyor | I'' için Q₁/3+|a|Q₂/12 sınırı eklendi; mevcut varsayımlar yeterli |
| F02 | İspat açıklaması, kapatıldı | R16 §3 sabit noktadan S=0'a geçerken B'nin tersinirliği açıkça belirtilmeli | ||I−BJ||<1 gerekçesi ve exact det B kontrolü yazıldı; a=0 uzantısı da açıklandı |
| F03 | Küçük metin hatası, düzeltildi | R16 §4 satır 150, (3)'teki “her terim”in sonsuz kuyruğu olduğunu söylüyor; A₄ yalnız üç hareketli merkezin sonlu toplamı | Yeni metin B₂/A₃ ve A₄ ayrımını doğru ifade ediyor; kod/formül/sabit aynı |
| F04 | Literatür konumlandırması, kısmen kapatıldı | R15'in sadece ağırlıkla Tikhonov karşılaştırması, özgünlük değerlendirmesine yetmez | L-moment, perfect spline ve sert türev sınırı kaynakları eklendi; öncelik hâlâ açık |

Frozen R15/R16 dosyaları yamalanmadı. Düzeltme ve açıklamalar
[PROOF_ADDENDUM.md](PROOF_ADDENDUM.md) içinde, yeni makalede kullanılacak
biçimiyle kaydedildi. F01/F02, sonuçları geçersiz kılan boşluk diye
sınıflandırılmadı: gereken koşullar mevcut kanıtta ve sertifikada vardı.
F03 sayısal bir hesap hatası değildir. F04 için literatürün tamamının
tüketildiği söylenemez.

## 3. Korunan ana sonuçlar

R15 genel teoremi; basit ve ayrık artık sıfırları, yerel türev
toplanabilirliği ve seçilmiş geçişlerde tam moment rankı koşullarıyla

    δ(M)=δ*+C*/M²+o(M⁻²),
    C*=δ*³Σw(zₖ)|r*'(zₖ)|/(3D*)

sonucunu veriyor. Bu koşullar theta örneğinde gerçek dual optimum
üzerinde doğrulanıyor. Yaklaşık sabit dual tabanın hatası, büyük M'de
baş terimi bastıracak şekilde gizlenmemiş.

R16 aynı tam Q'da her M≥0.00002 için

    C*/M²−9.624e−33/M³ < δ(M)−δ* < C*/M²+2.167e−32/M³

eşitsizliğini koruyor. C* aralığı
(9.20340371e−25, 9.20340375e−25). Başlangıç bütçesinde toplam minimum:

    0.00000000091787309568619750
      < δ(0.00002) <
    0.00000000091787309964331750.

Yüzde 0,1178 sınırı ek maliyetin C*/M² ile yaklaşımına aittir.
“870 kattan fazla daralma”, R14'e göre bilgi aralığının daralmasıdır;
gerçek optimumun iyileşmesi veya bir hızlandırma değildir.

27 maddelik [iddia denetimi](CLAIM_REVIEW.md) kanıt adımlarını ve
hangi tür doğrulamaya dayandıklarını ayrı ayrı gösterir.

## 4. Yayın bakımından karar

Moment dualitesi, işaret biçimli ekstremaller ve türev sınırıyla geçiş
düzenleme literatürde var. Bunları yeni buluş diye sunamayız. Okunan
kaynaklarla karşılaştırınca savunulabilir katkı adayı, aynı tasarım
probleminde **keskin baş katsayı + hipotezlerin sertifikalı özel örneği
+ açık uniform kalan terim** birleşimidir. Bu ayrım, formülün başka
bir dilde/eşdeğer problemde daha önce bulunmadığını kanıtlamaz.

Bu nedenle şu anki karar, yeni uzun hesaplarla kapsam büyütmek yerine
[makale katkı tanımını](MANUSCRIPT_POSITION.md) sabitleyip bu belirli
iddiayı literatür ve dış matematiksel okuma karşısında sınamaktır.
Çalışmayı yayın araştırması olarak sürdürmek için somut bir temel var;
hakemli kabul ve özgünlük konusunda kesin hüküm yok.

Tam sonlu-M minimizer, onun tekliği, en iyi kalan-terim mertebesi,
bir fiziksel sistemde gerçekleşebilirlik, kütle koruyan varyant veya
R10 kök penceresinin aktarımı bu turda elde edilmedi. R13'ten gelen
düzgün sınıf sonucu infimum eşitliğidir. Bunlar sınır olarak korunuyor.
