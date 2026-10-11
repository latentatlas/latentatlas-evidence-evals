# R17 — Yakın literatür ve katkı sınırı

21 Eylül 2026. Bu, odaklı bir karşılaştırmadır; tüketici bir bibliyografya
veya “ilk biz yaptık” kanıtı değildir. Aşağıdaki özetler birincil
makalelerin erişilen kısımlarına dayanır. Kaynaklardaki teoremler kendi
varsayımları dışında kullanılmadı. Aktarım/karşılaştırma yorumları bize
aittir. Uzun doğrudan alıntı yapılmadı.

## 1. Birincil kaynaklar ve gerçekten okunan kapsam

**L01 — P. Yuditskii / Petro Yudytskiy.** *On the L1 extremal problem
for entire functions*, Journal of Approximation Theory 179 (2014),
63–93, [DOI](https://doi.org/10.1016/j.jat.2013.11.011).
[Yazar ön baskısı](https://arxiv.org/abs/1204.4620),
[PDF](https://arxiv.org/pdf/1204.4620).
Okunan kapsam: giriş, Problem 1.2–1.3; ön baskı s. 1–3.
L¹ ekstremal problemi ile verilen momentleri sağlayan en küçük L∞
genlik arasındaki Markov L-moment dualitesi açıkça kuruluyor.
Bu, bizim sınırsız eğim dualitesini yeni bir genel ilke olarak
sunmamamızı gerektirir. Makalenin tüm entire-function sonuçları
incelenmiş veya bizim çekirdeğe aktarılmış değildir.

**L02 — Samuel Karlin.** *Interpolation properties of generalized
perfect splines and the solutions of certain extremal problems. I*,
Transactions of the AMS 206 (1975), 25–66,
[DOI](https://doi.org/10.1090/S0002-9947-1975-0367512-0).
AMS doğrudan erişimi başarısız oldu; asıl makalenin
[PDF kopyası](https://scispace.com/pdf/interpolation-properties-of-generalized-perfect-splines-and-3744ykflgq.pdf)
üzerinden §§7–8, Teorem 7.1/8.2 ve Problem II, basılı s.60–66 okundu.
Moment ağırlıkları bir complete Tchebycheff sistemi olduğunda,
sınırlı aralıkta türev L∞ normunu minimize eden perfect spline
sonuçları ve moment-dualite ilişkisi bulunuyor. Bizim problemde amaç
∥h∥∞, ayrı kısıt Lip(h)≤M, bölge yarı doğru. Sonsuz salınımlı
p₀=cos(2τu) içeren uzay global bir Chebyshev sistemi değildir.
Dolayısıyla okunan teorem doğrudan uygulanmıyor; benzer yöntemlerin
klasik olduğu gerçeği değişmiyor. PDF görüntü aracı başarısız olduğu
için karşılaştırma metin çıktısına dayandı; hassas düğüm sayısı
formülü üzerine bir iddia kurulmadı.

**L03 — Daniel Wachsmuth.** *Adaptive regularization and discretization
of bang-bang optimal control problems*, ETNA 40 (2013), 249–267,
[dergi PDF'si](https://etna.ricam.oeaw.ac.at/vol.40.2013/pp249-267.dir/pp249-267.pdf).
Okunan kapsam: problem (1.1)–(1.4), Varsayım 1.4, Önerme 1.5,
basılı s.249–253. Amaç kuadratik izleme hatası ve α∥u∥²/2
Tikhonov terimidir. Küçük switching-function değerlerinin ölçüsü
yakınsama hızlarını denetler. İlgili arka plan sağlar; α bizim M'nin
yerine konamaz ve bu sonuç kendi başına R15 katsayısını vermez.

**L04 — Nikolaus von Daniels.** *Tikhonov regularization of
control-constrained optimal control problems*, arXiv:1704.05797,
[yazar ön baskısı](https://arxiv.org/abs/1704.05797),
[PDF](https://arxiv.org/pdf/1704.05797).
Okunan kapsam: problem tanımı, Varsayım 7, Lemma 8 ve Teorem 11'in
ilgili yakınsama ifadeleri, özellikle s.1,6–9. Kaynak/ölçü koşulları
altında kontrol ve durum yakınsama hızları inceleniyor. Lemma 8'de
switching fonksiyonuyla ağırlıklı sapma alt sınırı var; bizim dual
kayıp yaklaşımımızla yakın bir mekanizma. Yorumumuz: basit geçişlerden
kuadratik kayıp beklemek tek başına özgünlük değildir. Buradaki
kuadratik düzenleme problemi, sert u-eğim kısıtlı genlik problemimizle
özdeş değildir.

**L05 — Cristiana J. Silva, Emmanuel Trélat.** *Smooth Regularization
of Bang-Bang Optimal Control Problems*, IEEE Transactions on Automatic
Control 55(11) (2010), 2488–2499,
[DOI](https://doi.org/10.1109/TAC.2010.2047742),
[yazarın üniversite PDF'si](https://www.ljll.fr/~trelat/fichiers/SilvaTrelat_TAC2010.pdf).
Okunan kapsam: girişteki düzenleme, Teorem 1 ve açıklamaları,
basılı s.2488–2490; s.2490 görüntüsü ayrıca incelendi.
Ek küçük kontrol yönleri ve Öklid kontrol küresiyle minimum-zaman
problemi düzenleniyor; uygun varsayımlarla bang-bang çözüme kuvvetli
yakınsama elde ediliyor. Bizim sabit moment hedefimiz ve sert türev
bütçemiz bu düzenleme değil. Teorem R15/R16'yı doğrudan sağlamaz.

**L06 — Bassam A. Albassam.** *Optimal Near-Minimum-Time Control
Design for Flexible Structures*, Journal of Guidance, Control, and
Dynamics 25(4) (2002), 618–625,
[DOI](https://doi.org/10.2514/2.4945).
Yayıncı bağlantısı erişilemedi; [yazar tarafından yüklenen asıl
makale metni](https://www.researchgate.net/publication/228607767_Optimal_Near-Minimum-Time_Control_Design_for_Flexible_Structures)
okundu: §§II–IV, özellikle (7)–(12) ve (16).
Sabit genlik sınırı altında manevra süresi minimize edilir; kontrolün
birinci türevine sert sınır ve uçlarda sıfır kontrol şartı eklenir.
Bu kaynak, sert türev sınırıyla bang-bang geçişleri düzenleme fikrinin
de önceden çalışıldığını gösterir. Bizde süre sabittir/optimize edilmez,
genlik minimize edilir, ağırlıklı momentler korunur ve sınırda sıfır
kontrol şartı yoktur. Buradan uygulamamızın fiziksel doğruluğu çıkarılmaz.

## 2. Karşılaştırmanın sonucu

| Çalışma hattı | Ortak yapı | R15–R16'da ayrıca gösterilmesi gereken |
|---|---|---|
| L-moment/L¹ dualitesi | Minimum genlik, momentler ve dual işaret tanığı | Bu salınımlı çekirdekte gerçek dual optimumun rigoröz yeri |
| Perfect spline ekstremal problemleri | Momentleri koruyan parçalı yapı, türev normları | Sert eğim altında genlik maliyeti; global Chebyshev yapısı olmadan sonsuz geçişler |
| Tikhonov bang-bang analizi | Sıfır çevresindeki kayıp ve yakınsama hızı | α'dan M'ye varsayımsız aktarım yapılamaz; baş katsayı ayrıca türetilmeli |
| Sert kontrol-türevi kısıtları | Sıçramaların sonlu eğimli geçişlere dönüşmesi | Sabit moment probleminde eşleşen alt/üst katsayı ve bütün M≥M₀ için hata |

R15'in 1/3 yerel integral katsayısı, konveks dualite, IFT ve Banach
teoremi ayrı ayrı yeni yöntemler diye sunulmamalı. M⁻² üssü de tek
başına güçlü özgünlük iddiası değildir. Potansiyel katkı, açık hipotezler
altında **tam baş katsayının** eşleşen alt/üst ispatı, sonsuz geçişli
theta örneğinde hipotezlerin rigoröz doğrulanması ve R16'nın açık,
uniform sonlu-bütçe kalan terimidir. Bu cümle bir katkı adayıdır;
taranmayan literatürde eşdeğer bir genel teorem bulunmadığını söylemez.

R15'teki sınırlı karşılaştırma yalnız kuadratik düzenleme ağırlıklıydı.
Bu tur L-moment, perfect spline ve sert türev kısıtı kaynakları eklendi.
Dolayısıyla “literatür sadece yumuşak ceza terimi kullanıyor” şeklinde
bir cümle artık kurulamaz; zaten böyle bir evrensel iddia kanıtlanmamıştı.

## 3. Açık kalan bibliyografik iş

Hedefli bir sonraki karşılaştırma, **sabit moment hedefi + minimum
L∞ genlik + ayrı Lipschitz sınırı** birleşiminin eşdeğer biçimlerini
aramalı: rate-limited minimum-norm control, generalized L-moment
problems with derivative bounds ve Lipschitz extremal approximation.
Bir genel teorem bulunursa, amaç/normalizasyon/katsayı birebir
eşleştirilmeden “aynısı” veya “farklısı” denmemeli. Karlin makalesinin
doğrudan yayıncı sürümü ve sonraki genişletmeleri ayrıca kontrol edilmeli.
Bu iş tamamlanmadan “ilk”, “yeni evrensel yasa” veya dergi kabulü
güvencesi kullanılmamalı.

Ulaşılamayan kaynaklar ve arama kapsamı [arama kaydında](SEARCH_LOG.md).
Üçüncü taraf özetleri matematiksel kanıt yerine kullanılmadı; yazar
metninin barındırıldığı kopyalar ayrıca belirtildi. Tam makale PDF'leri
yayın hazırlık paketine kopyalanmadı.
