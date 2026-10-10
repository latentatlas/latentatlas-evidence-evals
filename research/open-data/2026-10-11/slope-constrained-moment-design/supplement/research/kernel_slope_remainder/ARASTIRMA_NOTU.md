# R16 — Asimptotik formülün kullanılabilir hata sınırı

21 Eylül 2026. Kullanıcının «devam edelim» isteği, R15'in açık kalan
sorusuna uygulandı: C*/M² baş terimi, hangi eğim bütçelerinde ne kadar
güvenilir? Aynı tam Q, aynı dört moment hedefi ve özgün u koordinatı
korundu. «Maliyet» en büyük bağıl çekirdek değişikliği ∥h∥∞'dır.

**Yeni sonuç:** Her M≥0.00002 için

\[
\frac{C_*}{M^2}-\frac{9.624\times10^{-33}}{M^3}
<\delta(M)-\delta_*
<\frac{C_*}{M^2}+\frac{2.167\times10^{-32}}{M^3}.
\]

Burada δ* ve C* gerçek matematiksel niceliklerdir; yaklaşık bir dual
tabana göre fark alınmadı. R15'teki C* aralığıyla birlikte

\[
\left|\frac{\delta(M)-\delta_*}{C_*/M^2}-1\right|
<0.001178\,\frac{0.00002}{M}
\]

elde edildi. Baş terimin bağıl hatası M=0.00002'de **yüzde 0,1178'den
küçük**; bütçe iki katına çıktığında bu garanti yüzde 0,0589'a iner.
Bu yüzde, toplam çekirdeğe veya toplam değişime değil, minimumun
üzerindeki küçük **ek değişikliğe** ilişkindir. İstatistiksel hata payı
değildir; belirtilen matematiksel modelde bir eşitsizliktir.

## 1. R15'in üzerine ne eklendi?

R15, M büyüdükçe ek maliyetin C*/M²'ye yaklaştığını ve C*'ın hangi
geçiş verileriyle belirlendiğini gösteren ispat taslağını verdi. R16
bu yaklaşıma açık bir bütçe başlangıcı ve açık kalan-hata sabitleri
ekliyor. Garanti yalnızca birkaç hesap noktasında değil, bütün
M≥0.00002 aralığında geçerli.

İki hata kaynağı ayrı kontrol edildi: sıçramaları sonlu genişlikli
doğrusal geçişlere dönüştürmek ve üç momenti korumak için ilk üç
geçişi kaydırmak. Geçiş yarı genişliği a≤2⁻¹⁴ için konumlar
cₖ=zₖ+a²vₖ biçiminde ele alındı. |vₖ|≤(512,768,384) kutusunda
açık bir büzülme hesabı, her genişlikte üç momenti tam koruyan
konumların varlığını verdi. Dördüncü moment genlikle tam düzeltildi.

Gerekli türevlerin bütün geçişler üzerindeki toplamları sınırlı.
Sonsuz kuyruk ayrıca hesaplandı; yalnızca [0,1]'deki geçişlerle
yetinilmedi. Alt sınırda çok uzak kuyrukta yerel Taylor alt ifadesi
negatifleşse bile gerçek kaybın pozitifliği doğru yönde kullanıldı.

## 2. Somut nicel kazanım

| Eğim bütçesi M | Minimumun δ*'a göre ek artışı, milyonda | Baş terim için garanti edilen bağıl hata üst sınırı |
|---|---:|---:|
| 0.00002 | 2.505415726 – 2.509677504 | %0,1178 |
| 0.00004 | 0.626517761 – 0.627050486 | %0,0589 |
| 0.00008 | 0.156649919 – 0.156716511 | %0,02945 |
| 0.00016 | 0.039165039 – 0.039173364 | %0,014725 |

M=0.00002 için toplam minimuma ait yeni aralık:

`0.00000000091787309568619750 < δ(0.00002) < 0.00000000091787309964331750`.

Bu aralık R14'ün gösterilen toplam-minimum aralığından **870 kattan
fazla dar**. Değişen, gerçek matematiksel optimum değil, onu ne kadar
iyi sınırladığımız. Ek artış artık milyonda yaklaşık 2,507 çevresinde
dar bir aralıkta kalıyor.

## 3. Ne tür bir ispat ve denetim var?

[Açık ispat](PROOF.md), moment düzeltmesinin bütün genişliklerde
varlığını, her M≥0.00002 bütçesinin kapsandığını ve iki taraflı hata
formülünü ayrı adımlarla veriyor. Sayısal eşik yalnızca «küçük bir
genişlikte çalışır» şeklinde bırakılmadı.

- 110 basamaklı Arb hesabıyla yerel yoğunluk/türev aralıkları, sonsuz
  kuyruk toplamları, büzülme katsayıları ve kalan-hata sabitleri üretildi.
- FLINT kullanmayan rasyonel denetçi, büzülmeyi ve sonuç eşitsizliklerini
  yeniden kurdu; okunabilir sabitler dışa yuvarlandı.
- Ayrı mpmath hesabı 80 ve 110 basamakta toplam 3.360 türev değerini
  aralık merkezleri ve uçlarında karşılaştırdı. Bu örnekleme tek başına
  bütün aralığın ispatı olarak kullanılmadı.
- Ayrıca M=0.00002'de optimal dual katsayılar ve doğrusal geçişli tasarım
  farklı integrallerle sayısal olarak yeniden kuruldu. İki hassasiyette
  de sonuç hata sınırının içinde kaldı. Bu yaklaşık sayısal tasarım,
  tam minimizer veya ayrı rigoröz tanık diye sunulmuyor.
- Beş yerel kalan-hata katsayısı tam rasyonel integrallerle denetlendi.

Yeni denetçide ilk kontrol, yeniden yüklenen Arb kutularından birebir
JSON eşitliği istediği için durdu. Arb yarıçapı yeniden kurulurken
bir birim dışa yuvarlanabiliyor. Matematiksel olarak gereken eski
kutuyu içerme koşulu denetlendi ve kontrol geçti. Sertifika ve sayısal
sınırlar değiştirilmedi. İlk kaynak ve log
[tanı kaydında](diagnostics/NOTES.md) korunuyor.

## 4. Sınırlar ve makalede kullanılabilecek iddia

Makaleye aday ifade: «Belirtilen sabit-konumlu moment tasarım
probleminde sonlu eğim kısıtının ek genlik maliyeti için keskin baş
terim ve açık bir bütçe aralığında geçerli, sertifikalı iki taraflı
kalan-hata sınırı.» Genel mekanizma R15'teki koşullu teoremde; bu
paketin açık sabitleri theta örneği için doğrulandı.

M⁻³, ispatladığımız bir hata üst sınırıdır. Bunun gerçek ilk kalan
terim olduğu veya daha iyi bir üs mümkün olmadığı gösterilmedi.
Sonlu-M optimumun tam şekli/tekliği de çözülmüş değil. Yeni üst
tasarım Lipschitz; düzgün pozitif tam-dörtlü/rank-üç sınıfa aynı
infimum R13 üzerinden aktarılıyor. R10 sonlu kök haritası bu yeni
tasarıma taşınmadı. Fiziksel model veya kütle koruma koşulu eklenmedi.

Analitik dış inceleme ve literatür önceliği açık kalıyor. Bu hesap,
makalenin doğrulanabilir nicel iddiasını güçlendirir; tek başına yayın
kabulü veya literatürde ilk olma garantisi değildir.

[Hata sınırı şekli](figures/remainder_envelope.png),
[önceki ve yeni aralık](figures/threshold_comparison.png),
[yeniden üretim](README.md), [kapanış denetimi](audit_report.json).
