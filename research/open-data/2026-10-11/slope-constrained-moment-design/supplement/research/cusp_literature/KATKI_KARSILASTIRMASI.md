# R06 — Yakın literatür ve iddia karşılaştırması

Erişim ve durum tarihi: 20 Eylül 2026. “Fark”, okunan sonuçların
kapsamıyla karşılaştırmadır; bir yazarın bütün çalışmalarında bir
sonucun bulunmadığı iddiası değildir. Tam makalelerin bağımsız ispat
denetimi yapılmadı. Kimlik, sürüm ve okuma düzeyleri [sources.json](sources.json)'da.

| Kaynak ve okunan yer | Kaynağın ilgili sonucu | Bizim iddiamızla ilişki |
|---|---|---|
| [Lessard–Pugliese (2025)](https://www.aimsciences.org/article/doi/10.3934/dcdsb.2024181), giriş, Lemma 1.1, §3, uygulama kapsamı | İki parametreli ODE cusp'larının tespiti ve bilgisayar destekli varlık doğrulaması. | Cusp doğrulamasında genel yöntem önceliği ileri süremeyiz. Bizim hedefimiz belirtilen integralin yay boyunca nicel sıfır geometrisi. |
| [Gameiro–Lessard–Pugliese (2016)](https://www.math.mcgill.ca/jplessard/papers/galepu.pdf), giriş ve §2/§4 kapsamı | Rigoröz çok parametreli devam, yerel çizelgeler ve komşu çizelgeleri bağlama. | Tüpleri/çizelgeleri birleştirmenin kendisi yöntem yeniliği değil. Q/S'nin özel bağlantısı hâlâ ayrı matematiksel bilgi. |
| [Lessard–Sander–Wanner (2017)](https://www.aimsciences.org/article/doi/10.3934/jcd.2017003), özet ve giriş | Diblock modelinde fold ve simetri kaynaklı pitchfork noktalarının sürekli dalları. | Çatallanma noktalarının dal olarak rigoröz devamı da yerleşik. Bir dal bulduğumuz için genel ilk iddiası kurulamaz. |
| [Papanicolaou–Kallitsi–Smyrlis (2021)](https://ejde.math.txstate.edu/Volumes/2021/44/papanicolaou.pdf), §1, Teorem 4.1 ve kanıt başlangıcı | Entire ısı çözümlerinde çok katlı sıfırlar \((\tau,z)\) uzayında birikemez. | Sabit \(\mu,\nu\) için bizde \(\tau=-\lambda/4,z=t\). Ek kontroller değişirken cusp yayı olmasıyla çelişmez; teorem özel üç kontrol geometrimizi belirlemez. |
| [Newman–Wu (2020)](https://arxiv.org/abs/1901.06596), giriş, §3 ve sınıflandırma kapsamı | Genel pozitif simetrik ölçülerin Gaussian deformasyonlarında tüm sıfırların gerçekliği çerçevesi. | Aile doğal biçimde bu çerçeveye yerleşir. Yerel cusp ve sonlu kök bölgesi sonucu, global tüm-sıfırlar sorusundan ayrıdır. |
| [Rodgers–Tao (2020)](https://doi.org/10.1017/fmp.2020.6), giriş (1)–(4), ana sonuç | Klasik tek parametreli ailenin \(\Lambda\ge0\) sonucu. | Aynı çekirdek ve açık normalizasyon bağlantısı; bizim teoremimiz klasik sabit için yeni sınır vermez. |
| [Blanco–Lessard (2026), v1 ön baskı](https://arxiv.org/html/2608.15613v1), özet ve §1 | PDE cusp'ları ve doğrulanan spektral bilgilerle çözüm kararlılığı. | Salt üç kök bilgisinden fiziksel bistabilite çıkarmamalıyız. 20 Eylül kaydında hakemli yayın olarak kullanılmadı. |
| [Michalowski (2026), v2 ön baskı](https://arxiv.org/abs/2602.20313v2), sürüm açıklaması/özet | Aynı çekirdekte PF5 başarısızlığına ilişkin sertifika; v1'in bazı global eşik iddiaları geri çekilmiş. | Toplam pozitiflik sorusu cusp geometrisinden farklı. R01–R05 bu kaynağın doğruluğunu kanıt girdisi olarak kullanmıyor. |
| [Dieci–Pugliese (2026)](https://epubs.siam.org/doi/10.1137/25M1780857), yayıncı özeti | İki parametreli kompleks matrislerde özdeğer çakışmaları ve faz birikimi. | “Cuspidal” sözcüğü burada farklı nesne için kullanılıyor. Doğrudan aynı skaler üçlü sıfır problemi sayılmadı. |

## İddia düzeyinde karar

| Olası iddia | Durum | Gerekçe / kullanılabilir biçim |
|---|---|---|
| Cusp çevresinde iki fold, bir/üç kök ve 3/2 üssü keşfettik. | **Bilinen; özgünlük iddiası uygun değil.** | Kübik normal formdan çıkar. |
| İlk bilgisayar destekli cusp kanıtı / ilk rigoröz devam yöntemini verdik. | **Yanlış öncelik iddiası.** | Yukarıdaki yöntem literatürü mevcut. |
| İki belirli cusp aynı doğrulanmış yayda. | **R03 içinde hesap destekli; özgünlük adayı.** | Yay ve kesit kimlikleri açık; global tek bileşen iddiası yok. |
| Bütün yayda açık ortak pencere için tam kök diyagramı. | **R04 içinde hesap destekli; özgünlük adayı.** | Normal formun nitel yerel sonucundan daha açık nicel kapsam. |
| Genişlik özgün kontrollerde ν ile monoton. | **R05 içinde hesap destekli; özgünlük adayı.** | Sonlu pencere, iki kolun ayrı işaretleri ve hız sınırı. Merkezleme şartı önemli. |
| C' işareti üç ısı özdeşliğinin otomatik sonucu. | **Genel analitik sınıfta yanlış.** | R06 tam polinom karşılaştırması zıt işaretler veriyor. Pozitif çekirdek sınıfına karşıörnek değil. |
| C' işaretinden hiçbir ek hesap olmadan tam 10^-6 pencere çıkar. | **Gerekçesiz.** | Küçük bir pencere nitel olarak çıkar; belirtilen sonlu pencere için R05 kalanı gerekir. |
| Evrensel, koordinattan bağımsız bir genişleme yasası. | **Kanıtlanmadı; mevcut ölçüm koordinata bağlı.** | λ, μ sabit monomiyal birimlerinde anlamlı. |
| RH, fiziksel faz geçişi veya global cusp sınıflandırması sonucu. | **Mevcut teoremler desteklemiyor.** | İlave matematiksel/uygulamalı model gerekir. |

## Kaynak kimliği düzeltmeleri

Önceki `research/MAKALE_KAPSAMI.md`, Lessard–Pugliese makalesi için
arXiv sayfasındaki **LAA 728 (2026), 26–46** bilgisini aktarmıştı.
[Dergi kaydı](https://www.aimsciences.org/article/doi/10.3934/dcdsb.2024181)
ve [yazar kaydı](https://www.alessandropugliese.com/research)
doğru yayını **DCDS–B 30(6) (2025), 2135–2158,
doi:10.3934/dcdsb.2024181** olarak gösteriyor.
LAA DOI'si başka başlığa ait. Bu bibliyografik hata açık kayıtla düzeltildi.

Özgün TeX'in Michalowski atfındaki başlık/yazar ilk harfi de güncel
v2 kaydıyla uyuşmuyor. v2'nin yazarın kendi geri çekme açıklaması
kaydedildi; geri çekilen iddialar yeniden kullanıma alınmadı.
Özgün TeX bu aşamada korunuyor; bu not gelecekteki kaynakça düzeltmesinin
izidir. Kaynağın bütün ispatının tarafımızdan doğrulandığı söylenmiyor.
