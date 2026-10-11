# R03 — Quartic ve sextic cusp aynı düzenli eğri üzerinde

20 Eylül 2026. Durum: açıkça belirtilen kapsamda hesap destekli kanıt ve
ayrı aritmetik kontroller tamamlandı. Dış uzman incelemesi ve literatürde
öncelik değerlendirmesi tamamlanmış değil.

**Araştırma sorusunun cevabı evet:** daha önce ayrı ayrı sertifikalanan
quartic ve sextic cusp, üç kontrol parametreli integral ailesinde aynı
düzenli cusp eğrisi üzerinde bağlanıyor. Aradaki bütün yol sertifikalandı;
eski cusp noktalarının yeni eğriye aidiyeti de teklik bölgeleriyle
gösterildi. İki yakın sayısal noktanın aynı nokta olduğu varsayılmadı.

## 1. Tam olarak hangi nesne incelendi?

Önceki paketlerle aynı çekirdek ve normalizasyon kullanılıyor:

\[
F(t;\lambda,\mu,\nu)=\int_0^\infty\Phi(u)
 e^{\lambda u^2+\mu u^4+\nu u^6}\cos(2tu)\,du.
\]

Quartic kesitte ν=0, sextic kesitte μ=0. İkisinde de λ kontrolü var.
Aşağıdaki ondalıklar yalnız konum göstergesidir; kanıtta önceki
sertifikaların tam ikili rasyonel merkezleri ve hata kutuları kullanıldı.

| Önceki cusp | t | λ | μ | ν |
|---|---:|---:|---:|---:|
| Quartic Q | 41.40034135868425 | −3.645692061604919 | 8.335120498918607 | 0 |
| Sextic S | 44.28556344959544 | −12.43702949446505 | 0 | −28.82453269539050 |

Q'dan S'ye giderken ν azalıyor; t, λ ve μ, cusp koşullarını koruyacak
biçimde birlikte değişiyor. Bu bir parametre devamıdır. Fiziksel zaman
evrimi veya bir deneyin dinamiği olduğu ileri sürülmüyor.

## 2. Yeni teorem

Kaydedilen bağlı tüpler sistemi içinde, −29≤ν≤0 boyunca tek bir gerçek
analitik grafik vardır:

\[
\Gamma(\nu)=(t(\nu),\lambda(\nu),\mu(\nu),\nu),
\qquad F=F_t=F_{tt}=0.
\]

Her ν için teklik, o ν'ye ait kayıtlı tüp içinde geçerlidir. Bütün
parametre uzayında tek cusp eğrisi bulunduğu söylenmiyor. Q ve S bu
grafiğin üzerindedir; böylece cusp kümesinin aynı bağlı bileşenine aittir.

Yolun tamamında şu eşitsizlikler doğrulandı:

\[
F_{ttt}>8\times10^{-14},\qquad F_{t^4}<0,\qquad F_{t^6}<0,
\qquad 0.26<\frac{d\mu}{d\nu}<0.34.
\]

Burada F_{t^n}, t'ye göre n'inci türevi gösteriyor. Üçüncü türev sıfır
olmadığı için her noktadaki kök tam üç katlıdır. Kontrollerin bağımsızlığı
da şu determinantla sağlanıyor:

\[
\det D_{(\lambda,\mu)}(F,F_t)
=\frac{F_{ttt}F_{t^4}}{64}\ne0.
\]

Dolayısıyla yol üzerinde cusp tipi bozulmuyor. Dört katlı kök ve buna
karşılık gelen A4 potansiyel tekilliği bu yay üzerinde bulunmuyor.

μ'nün tek yönlü değişimi yalnız grafik gözlemi değil. Parametre-türev
özdeşlikleri cusp koşulları boyunca türevlenince

\[
\frac{d\mu}{d\nu}=\frac{F_{t^6}}{4F_{t^4}}
\]

elde ediliyor. Sağ tarafın alt ve üst sınırları bütün yol için doğrulandı.
Bu nedenle eğri **μ=0 sextic kesitiyle tam bir kez**, önceki S cusp'ında,
kesişiyor. Bu tekliğin kapsamı sertifikalı yaydır; kesitteki bütün başka
cusp'ları dışlamaz.

## 3. Nokta örneklerinden yol kanıtına nasıl geçildi?

ν aralığı, her biri 0.5 uzunluğunda 58 kapalı parçayla boşluksuz örtüldü.
Her parçada x=(t,λ,μ) için doğrusal bir merkez tahmini ve her koordinatta
2^-10 yarıçaplı bir tüp kullanıldı. Dört değişkenli Taylor açılımı,
analitik kalan ve integral kuyruk sınırlarıyla bu tüpün tamamı kapsandı.

Her sabit ν için x−Y(F,F_t,F_tt) dönüşümünün daralma olduğu ve tüpü
kendi içine gönderdiği gösterildi. Ayrı tam kesirli denetçinin doğruladığı
ortak sınırlar q<0.502 ve η+q<0.560<1. Burada q daralma katsayısı,
η ise ölçeklenmiş merkez kalıntısıdır.

En kritik ek koşul dal bağlantısıdır: 57 ortak sınırın her birinde bir
önceki parçanın **sertifikalı kök kutusunun tamamı**, sonraki parçanın
teklik kutusunun içine yerleştirildi. Kapsama oranı her koordinatta
0.117'den küçük. Böylece yan yana duran kutuların farklı dalları temsil
etmesi ihtimali, bu sertifikalı kökler için dışlandı. Sırf kutu kesişimi
kanıt olarak kullanılmadı.

Önceki quartic kökün tüm hata kutusu ilk tüpe sığıyor. Önceki sextic kökün
ν belirsizliği de hesaba katılarak tüm kutusu son tüpte kapsanıyor. Bu iki
teklik argümanı, yeni eğriyi önceki kesin matematiksel nesnelere bağlıyor.
Ayrıntılar [analitik kanıtta](PROOF.md).

## 4. Hangi kontroller geçti?

| Kontrol | Sonuç ve işlevi |
|---|---|
| Uniform tüp sertifikası | 58 parçanın tamamında varlık, teklik ve cusp işaretleri |
| Dal bağlantısı ve eski nokta aidiyeti | 57 birleşme ve iki eski cusp'ın kapsanması |
| Ayrı rasyonel aritmetik | Taylor katsayıları farklı yöntemle yeniden kuruldu; bütün daralmalar, birleşmeler ve μ türev sınırları geçti |
| Doğrudan integral karşılaştırmaları | Üç farklı parçada 42 türev kapsaması, altı noktada önkoşullandırılmış Jacobian ve 18 tahmin kalıntısı bileşeni kontrol edildi |
| Cebir ve geçersiz girdi kontrolleri | Tam kesirlerle teğet özdeşlikleri, kapsam dışına çıkma ve sonlu olmayan girdiler; toplam dört kontrol grubu geçti |
| Ayrı mpmath hesabı | Üç parça merkezinde 18 türev değeri kayıtlı integral aralıklarının içinde bulundu; ek sayısal destek |

Kesirli denetçi FLINT kullanmadan çalışıyor; ancak merkezi integral
aralıklarını ve mutlak türev majorantlarını girdi kabul ediyor. Bu kısmı
yeniden ispatlayan bağımsız bir integratör değil. mpmath karşılaştırması
da sertifikalı hata sınırları sağlayan ikinci bir kanıt sayılmıyor.
Analitik gerekçe, FLINT/Arb aralık hesabı ve Python yürütmesi güvenilen
hesap tabanıdır. Harici hakem veya biçimsel ispat doğrulayıcısı yok.

İlk geliştirme denemesinde kaba Jacobian kapsaması q>1 verdi ve işlem
durdu. İlgili merkezi türevler önkoşullandırılmış Taylor ifadesinde birlikte
ele alınarak bağımlılık kaybı azaltıldı; aynı sıkı daralma koşulları
ardından sağlandı. Bu başarısız deneme ve açıklaması
[diagnostics](diagnostics/README.md) içinde korunuyor. Geçmeyen koşu
başarılı sertifika olarak sunulmadı.

## 5. Bilimsel kazanım ve sınırlar

Artık aynı makale hikâyesinde birbirine bağlı üç bilgi var:

1. **R01:** iki referans cusp'ın varlığı, dejenerasyonsuzluğu ve bağımsız
   kontrol yönleri; seçilmiş iki yerel kök sayımı.
2. **R02:** quartic cusp çevresinde belirli bir sonlu bölgede tam bir/üç
   kök sınıflandırması ve iki fold kolunun nicel geometrisi.
3. **R03:** bu cusp ile sextic cusp arasındaki düzenli eğri, yol boyunca
   cusp tipinin korunması ve sextic kesitin tek geçilişi.

Bu, iki ayrı örneğe ortak bir geometrik yapı ekler. Standart örtük
fonksiyon teoremi tek başına hangi uzak sertifikalı cusp'a ulaşıldığını
söylemez; burada o aidiyet bütün yol boyunca doğrulanmıştır. Bunun
literatürde daha önce bilinmediği ise ayrıca araştırılmalıdır.

**Henüz çıkarılmayan sonuçlar:** Bütün cusp bileşenlerinin sınıflandırılması,
−29≤ν≤0 dışındaki devam, global A4 yokluğu, tüm gerçek eksendeki kök
sayıları, Riemann hipotezi veya klasik Newman sabiti hakkında yeni bir
sınır. Mevcut t' aralıkları her yerde tek bir işareti kanıtlamıyor;
t(ν)'nün monoton olmadığı sonucu da bundan çıkarılamaz.

Özellikle R02'nin |t−t0|≤0.003, |λ−λ0|≤10^-6, |μ−μ0|≤2×10^-9
dikdörtgenindeki kök sayımı **ν=0 kesitine aittir**. Aynı sayısal pencerenin
ve sınırların bu yeni yolun tamamında çalıştığı kanıtlanmadı. Her noktada
cusp düzenliliğinin korunması nitel yerel modeli sağlar; ortak, açık
büyüklükte bir çevre vermek ek çalışma gerektirir.

## 6. Sonraki araştırma sorusu

**Bu bağlanan cusp eğrisi boyunca, yakınındaki iki fold kolu ve üç gerçek
köklü bölge açık hata sınırlarıyla birlikte nasıl değişiyor?**

Somut hedef, eğri boyunca uygun merkezlenmiş kontrol bölgeleri kurmak;
fold kollarını, sınırdan kök giriş-çıkışını ve bir/üç kök ayrımını ortak
veya parçalı doğrulanmış sınırlarla izlemek. Böylece makalenin katkısı
yalnız cusp merkezinin hareketini değil, çevresindeki kök geometrisinin
değişimini de açıklayabilir. Bu hedef henüz tamamlanmış sonuç değil.

Eski R01 ve R02 paketleri ile özgün makale bu yeni çalışmada değiştirilmedi.
Dosya bütünlükleri ve yeni çıktıların kaynak bağları `manifest.json`
içinde kayıtlıdır. Yeniden üretim adımları [README.md](README.md) içinde.
Bu paket derece eşdeğerliği veya dergi kabulü hakkında hüküm vermiyor.
