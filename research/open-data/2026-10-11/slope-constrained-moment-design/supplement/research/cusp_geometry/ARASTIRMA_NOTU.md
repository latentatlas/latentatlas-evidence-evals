# R04 — Cusp eğrisi boyunca fold geometrisi ve üç gerçek köklü bölge

20 Eylül 2026. Açık kapsamlı hesap destekli kanıt, ayrı tam kesirli
denetim ve doğrudan integral kontrolleri tamamlandı. Dış uzman incelemesi
ve literatürde öncelik değerlendirmesi henüz tamamlanmadı.

**Sonuç:** Quartic ve sextic cusp'ı bağlayan yol boyunca, cusp'ın
çevresindeki iki fold kolu ve bir/üç kök düzeni ortak bir sonlu çevrede
korunuyor. Üç köklü bölgenin cusp yakınındaki açılma katsayısı ise
quartic'ten sextic'e giderken sıkı biçimde artıyor. Uç noktalar
arasındaki katsayı artışı yaklaşık **%2,494633**.

## 1. Yer değiştirme ile biçim değişimini ayırmak

R03'ün tam cusp eğrisini c(ν)=(t*(ν),λ*(ν),μ*(ν)) olarak yazalım.
−29≤ν≤0 boyunca, her sabit ν kesitinde şu koordinatları kullanıyoruz:

\[
s=t-t_*(\nu),\qquad \ell=\lambda-\lambda_*(\nu),\qquad
m=\mu-\mu_*(\nu).
\]

Böylece her kesitte cusp merkeze taşınıyor. Kontrollerin ölçeği
değiştirilmiyor; aynı λ,μ koordinatları kullanılıyor. Merkezin hareketi
ile çevresindeki bölgenin açılması ayrı ayrı ölçülebiliyor.

Sextic cusp'ta da ν sabit tutularak λ,μ değiştiriliyor. Bu, önceki
sextic örneğin μ=0 olan (λ,ν) düzlemiyle aynı kesit değildir.
Bir açılma katsayısının anlamı hangi kontrollerin kullanıldığına bağlıdır.

## 2. Yolun tamamında geçerli sonlu bölge

Her ν için aynı boyutlar kullanılabildi:

\[
|s|\le0.003,\qquad |\ell|\le10^{-6},\qquad |m|\le2\times10^{-9}.
\]

Bu, sadece 58 örnek noktada yapılan kontrol değil. 58 kapalı ν aralığı
bütün [−29,0] yolunu örtüyor; her birinin içindeki bütün parametre
değerleri kapsanıyor. Aşağıdaki kök sayıları yalnız belirtilen s
penceresindeki gerçek kökler içindir.

| Kontrollerin konumu | Penceredeki tam kök düzeni |
|---|---|
| İki fold kolunun arası | Üç basit gerçek kök |
| Foldların dışı, ayırıcı üzerinde olmayan noktalar | Bir basit gerçek kök |
| Bir fold kolunun üzerinde | Bir çift kök ve bir basit kök |
| Cusp'ın kendisi | Bir üçlü kök |

Kontrol bölgesinin hiçbir noktasında kökler s=−0.003 veya s=+0.003
sınırından girip çıkmıyor. Bölgede başka cusp veya başka çok katlı
kök dalı bulunmuyor. Bu nedenle kök sayısının değişimi kapsanan fold
geometrisiyle tamamen açıklanıyor.

ν değişirken iki fold kolu da analitik olarak devam ediyor. Üç
kontrollü parametre uzayında bunları, aynı cusp eğrisi boyunca birleşen
**iki fold yüzeyi** olarak ele alabiliyoruz. Her sabit ν kesitindeki
iki kol bu yüzeylerin kesitleri.

## 3. Kollar hangi yöne açılıyor?

Yerel fold, s ile parametrelendirildiğinde λ yönünde cusp'ta tek bir
minimuma sahip. Her iki kol da λ>λ*(ν) tarafına açılıyor.
Bir kol μ>μ*(ν), diğeri μ<μ*(ν) tarafında. s arttıkça fold üzerindeki
μ sıkı biçimde azalıyor; λ önce azalıyor, cusp'tan sonra artıyor.

Isı-türev özdeşlikleri şu yerel açılımları veriyor:

\[
\ell(s,\nu)=2s^2+O_\nu(s^3),\qquad
m(s,\nu)=\frac{16\,\partial_t^3F}{3\,\partial_t^4F}s^3
         +O_\nu(s^4).
\]

Türevler cusp üzerinde değerlendiriliyor. λ yönündeki ikinci derece
katsayı **2** yol boyunca değişmiyor. μ yönündeki üçüncü derece katsayı
ise cusp boyunca değişiyor. Bu, hangi özelliğin korunduğunu ve hangisinin
değiştiğini analitik olarak ayırıyor. Bu genel özdeşliklerin literatürde
yeni olduğu iddia edilmiyor.

## 4. Sonlu uzaklıklarda genişlik için kesin sınırlar

Her kesitte, cusp'ın sağında ℓ>0 için iki fold arasındaki μ genişliğini
Wν(ℓ) olarak tanımlayalım. Yolun tamamı için

\[
0.98\,\ell^{3/2}\le W_\nu(\ell)\le1.72\,\ell^{3/2},
\qquad0<\ell\le10^{-6}
\]

kanıtlandı. Örneğin ℓ=10^-6 seviyesinde genişlik her kesitte
0.98×10^-9 ile 1.72×10^-9 arasında.

Tek tek kollar için 0.49ℓ^(3/2)≤|m|≤0.86ℓ^(3/2) var. Bu,
bütün kesitlerde |m|<0.49ℓ^(3/2) şeridinin kesinlikle üç köklü
olduğunu gösterir. |m|>0.86ℓ^(3/2) ise, tanımlanan kontrol
dikdörtgeni içinde, kesinlikle bir köklüdür. İki sınır arasındaki
şeritlerde gerçek fold konumuna bakmak gerekir.

Bu ortak sınırlar R02'nin yalnız quartic kesitteki daha dar sınırlarından
daha tutucudur. R02'nin daha hassas sonucu korunuyor; R04 çok daha geniş
bir parametre ailesini aynı anda kapsıyor.

## 5. Yeni değişim sonucu: açılma katsayısı monoton

Genişliğin cusp yakınındaki başterimi

\[
W_\nu(\ell)=C(\nu)\ell^{3/2}+O_\nu(\ell^2),\qquad
C(\nu)=-\frac{8\sqrt2}{3}
 \frac{\partial_t^3F(c(\nu),\nu)}{\partial_t^4F(c(\nu),\nu)}.
\]

C(ν)'yü, aynı küçük λ uzaklığında üç köklü bölgenin ne kadar açıldığını
belirleyen ilk katsayı olarak okuyabiliriz. Bütün yol boyunca
**C'(ν)<0** kanıtlandı. Quartic'ten sextic'e giderken ν azaldığı için
C artıyor.

| Tam sertifikalı nokta | C(ν), yaklaşık |
|---|---:|
| Quartic cusp, ν=0 | 1.29460899168317 |
| Sextic cusp, ν≈−28.82453269539050 | 1.32690473189189 |
| Sextic / quartic oranı | 1.02494632774544 |

Dolayısıyla açılma katsayısındaki artış yaklaşık %2,494633. Oranın
1.024 ile 1.026 arasında olduğu ayrıca tam kesirlerle doğrulandı.

**Bu yüzdelik, bütün sonlu bölgede gerçek genişliğin tam artış oranı
değildir.** Cusp'a yaklaşırken belirleyici olan katsayıya aittir.
Her sabit ℓ>0 için Wν(ℓ)'nin bütün yol boyunca monotonluğu henüz
kanıtlanmadı. İki farklı kesit seçildiğinde daha büyük C, yeterince
küçük ℓ için daha büyük genişlik verir; o eşik için burada ortak
sayısal değer sunulmuyor.

## 6. Neden yalnız grafik gözlemi değil?

Yerel bölgeler için her (s,ν) değerinde aynı yardımcı kontrol
kutusunda daralma ve teklik gösterildi. Eski cusp eğrisi tam olarak
merkez alındı; sayısal tahminin kalıntısı sıfırmış gibi kullanılmadı.
F_ttt, kontrol Jacobian'ı, fold üzerindeki F_tt'nin toplam türevi ve
pencere sınırlarındaki işaretler bütün bölgede kapsandı.

Açılma türevinde doğrudan aralık hesabı iptalleri kaybederek belirsiz
sonuç veriyordu. Analitik türev, işareti belirleyen beşinci derece
bir polinoma indirildi. Ortak ν değişkeni korunarak polinom
katsayıları hesaplandı; Taylor kalanı ve gerçek cusp'ın tahminden
uzaklığı ayrıca kapsandı. Sonuç 58 aralığın tamamında aynı işareti verdi.

Ayrı denetçi bu polinomu 11 monom halinde açarak, katsayıları ve
türevlerini tam kesirlerle yeniden kurdu. Bütün 58 kesitte pozitif
pay ve dolayısıyla C'(ν)<0 yeniden doğrulandı.

| Kontrol | Sonuç |
|---|---|
| Uniform bölge ve açılma sertifikası | 58/58 parametre aralığı geçti |
| Ayrı tam kesirli denetçi | Daralma, sonlu büyüme, kök işaretleri ve açılma türevinin işareti geçti |
| Doğrudan, daha ince integral kontrolleri | 54 korelasyonlu türev kapsaması ve 18 cusp merkezli karşılaştırma geçti |
| Cebir ve hata yakalama | Teğet/açılma türevi özdeşliği, kısmi türevler, kapsam dışı ve sıfırdan geçen aralıklar; dört test grubu geçti |
| mpmath | Üç merkezde 24 türev karşılaştırması, C ve C' kontrolü geçti; ek sayısal destek |

Tam kesirli denetçi kaydedilen integral/türev kapsamalarını girdi
kabul ediyor; bunları yeniden bütünleyen ayrı bir ispat değil.
mpmath kontrolleri de rigoröz kuyruk ve yuvarlama hatası sertifikası
vermiyor. Bu sınırlar [analitik kanıtta](PROOF.md) açıkça yazıldı.

## 7. Makaleye kattığı şey ve sonraki soru

Çalışmanın matematiksel anlatısı artık birbirine bağlı dört parçalı:
cusp varlığı, bir kesitte nicel kök geometrisi, iki cusp arasındaki
sertifikalı bağlantı ve bağlantının tamamındaki kök düzeni/açılma değişimi.
Özel integral ailesinde hangi geometrinin korunduğunu ve hangi niceliğin
değiştiğini birlikte açıklayabiliyoruz.

Sonuç özgünlük ve önem açısından literatürle karşılaştırılmalı.
Doğrulama yöntemi kullanmış olmak veya standart cusp üssünü yeniden
elde etmek tek başına yöntem yeniliği değildir. Dergi kabulü ve
akademik derece eşdeğerliği hakkında hüküm verilmiyor.

Doğal sonraki soru, **C'nin monotonluğunun sonlu genişliğe ne ölçüde
taşındığıdır:** Wν(ℓ) için de belirli, açık bir ℓ aralığında aynı değişim
yönü kanıtlanabilir mi? Bunun için fold sınırlarının toplam ν
türevleri ve cusp yakınında iptal eden terimler ayrıca ele alınmalı.

Önceki üç paket ve özgün makale değiştirilmedi. Kaynak/çıktı bağları
ve dosya özetleri manifestte; komutlar [README.md](README.md) içinde.
