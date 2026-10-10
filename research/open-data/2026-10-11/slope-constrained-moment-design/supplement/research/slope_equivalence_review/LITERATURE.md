# R18 — Eşdeğer formülasyonlara yönelik kaynak karşılaştırması

21 Eylül 2026. R17'deki altı kaynağa ek olarak yedi birincil metnin
aşağıdaki kısımları incelendi. Bu bir sistematik bütün-literatür taraması
değil. «Okunan sonuçta bulunmadı» ile «literatürde yok» ayrıdır.
Kaynak kimlikleri [sources.json](sources.json) içinde; sorgular ve erişim
sınırları [SEARCH_LOG.md](SEARCH_LOG.md) içinde kayıtlıdır. Tam makaleler
bu yayın hazırlık paketine kopyalanmadı.

## L07 — Lellmann, Lorenz, Schönlieb, Valkonen (2014)

*Imaging with Kantorovich–Rubinstein Discrepancy*, SIAM Journal on Imaging
Sciences 7(4), 2833–2859.
[DOI](https://doi.org/10.1137/140975528),
[birincil preprint](https://arxiv.org/pdf/1407.0221).

Okunan odak: §2, (2)–(3), Lemma 2.1; §3 giriş, Lemma 3.1 ve
Theorem 3.4; §4.4'teki problem/teorem ifadeleri. Ayrı genlik ve
Lipschitz sabitleriyle KR normu bizim H(A,M) yardımcı problemimizle
aynıdır. Sınırsız eğimde Radon normu elde edilir. Diverjans biçimi ve
onun minimizer düzenliliği için verilen bounded/convex domain
koşulları yarı-doğruya otomatik aktarılmadı.

**Karşılaştırma:** yeni bir genlik/eğim normu tanımladığımız iddiasını
engeller. Okunan teoremler görüntü düzenleme ve norm dualitesiyle
ilgili; R15'in tam moment hedefi için M⁻² baş katsayısı bunların
ifadesi değildir.

## L08 — Piccoli, Rossi (2016; incelenen preprint v3: 2014)

*On properties of the Generalized Wasserstein distance*, Archive for
Rational Mechanics and Analysis 222, 1339–1365.
[DOI](https://doi.org/10.1007/s00205-016-1026-7),
[preprint](https://arxiv.org/pdf/1304.7014).

Odak: giriş ve §3, Definition 12/Theorem 13, preprint s.7–10.
Flat norm ile taşıma ve kütle değiştirme maliyetlerinin birleşimi
arasındaki dualiteyi verir; yalnız olasılık ölçüleriyle sınırlı değildir.

**Karşılaştırma:** H'nin bilinen taşıma yorumunu doğrular. Bizdeki
μ_a=w r_a du işaretli artıktır; başlangıç çekirdeğinin kütlesinin
korunduğunu söylemez. Moment kısıtlı optimumun açık ikinci mertebe
yaklaşımı, incelenen Theorem 13'ün sonucu olarak sunulamaz.

## L09 — Jabłoński, Marciniak-Czochra (arXiv:2013)

*Efficient algorithms computing distances between Radon measures on R*.
[Kayıt](https://arxiv.org/abs/1304.3501),
[preprint](https://arxiv.org/pdf/1304.3501).

Odak: §2.3 Definition 2.6 ve §3.3.1–3.3.5. Sonlu atomlar için flat
metriği hesaplayan algoritmalar ve sürekli ölçülerin ayrık yaklaşımı
ele alınıyor; O(n log n) algoritması bu ayrık problem içindir.
PDF başlığındaki 2021 tarihi yeni bir yayın tarihi sayılmadı: arXiv
kayıt geçmişinde tek v1, 11 Nisan 2013 görünüyor.

**Karşılaştırma:** hesaplama yolu için yakın kaynak; sabit bir ızgarada
elde edilen optimum, sürekli yoğunlukta M→∞ katsayısının kanıtı
değildir. Bunun nedeni [E8 ve atom örneğinde](EQUIVALENCE_MAP.md) açık.

## L10 — Schmidt, Düll (2025)

*Computing the distance between unbalanced distributions: the flat metric*,
Machine Learning 114, article 195.
[Yayıncı tam metni](https://doi.org/10.1007/s10994-025-06828-8).

Odak: §1.1 tanım/normalizasyon, §2.1–2.2 yöntem, ek Analytical ground
truth/Proposition 1 ve ispatı. ∥g∥BL=max(∥g∥∞,Lip(g)) seçimi açık.
Çalışma flat metriği sinir ağıyla yaklaşık hesaplıyor; atom örnekleri
için analitik kıyas değerleri de veriyor.

**Karşılaştırma:** aynı normun güncel kullanımını gösterir; bizim
integral/moment asimptotiğimize veya AI/LLM uygulamasına dair kanıt
değildir. Buradan yeni bir uygulama iddiası çıkarılmadı.

## L11 — Heinemann, Klatt, Munk (2023; çevrimiçi 2022)

*Kantorovich–Rubinstein Distance and Barycenter for Finitely Supported
Measures: Foundations and Algorithms*, Applied Mathematics & Optimization
87, article 4.
[Yayıncı](https://doi.org/10.1007/s00245-022-09911-x),
[incelenen preprint v3](https://arxiv.org/pdf/2112.03581).

Odak: (2) tanımı, §2.1 Lemma 2.1/Theorem 2.2 ve p=1 duali, ayrıca
ilgili ispat bölümü. Taşıma/mass-deletion parametresi C, dualde genlik
sınırı C/2 olur. Sonlu desteklerde küçük C rejimi ayrık doygunluktur.

**Karşılaştırma:** M ile C ters yönde gider: C=2A/M. TV satırındaki
görünür faktör tutarsızlığı [normalizasyon kaydında](NORMALIZATION_CHECK.md)
ayrıldı; kullanılan eşleme tanım ve dualden geliyor. Sonlu destek
varsayımı bizim sürekli ve sonsuz geçişli yoğunluğumuzla eş tutulmadı.

## L12 — Sion (1958)

*On general minimax theorems*, Pacific Journal of Mathematics 8(1), 171–176.
[DOI](https://doi.org/10.2140/pjm.1958.8.171),
[yayıncı PDF'si](https://msp.org/pjm/1958/8-1/pjm-v8-n1-p14-p.pdf).

Odak: s.174, Theorem 3.4 ve ardından gelen tek-kompakt-küme corollary.
Sayfa görsel olarak da kontrol edildi; basılı corollary numarası 3.3
göründüğünden yalnız numarayla atıf yapılmıyor.

**Karşılaştırma:** momentleri dual katsayılarla geri koyan (E3), bu
klasik minimax sonucunun uygulamasıdır. Yarı-doğruda gereken
kompaktlık ve moment sürekliliği [eşleme notunda](EQUIVALENCE_MAP.md)
ayrıca yazıldı. Dual minimizer tekliği/varlığı bu atıftan çıkarılmadı.

## L13 — Schmitzer, Wirth (2019; preprint v2: 2018)

*A Framework for Wasserstein-1-Type Metrics*, Journal of Convex Analysis
26(2), 353–396.
[Yayıncı kaydı](https://journalofconvexanalysis.com/articles/jca26020/),
[preprint](https://arxiv.org/pdf/1701.01945).

Odak: §1.2, §1.4 domain koşulları; Proposition 2.26 ve §3.2'nin
KR/total-variation özel halleri (preprint s.25–26). KR normu daha
geniş bir infimal-konvolüsyon/taşıma çerçevesine zaten yerleşir.
Bu çerçevedeki esas domain kompakt path metric space'tir.

**Karşılaştırma:** yalnız normu farklı sembollerle yazmak yöntemsel
yenilik değildir. Okunan eşdeğerlik teoremi, R15'teki basit kökler,
sonsuz geçiş toplamı ve tam moment düzeltmesi altında C* değerini
belirleyen bir asimptotik teorem olarak ifade edilmemiştir.

## Kararın kesinlik düzeyi

**Confirmed:** H'nin KR ile eşitliği ve standart dualiteyle moment
problemine bağlanması. **Mevcut kanıt zincirinde doğrulanmış:** R15/R16
hesapları, R17 kapsamıyla. **Uncertain:** R15'in bütün hipotez/sonuç
birleşiminin literatür önceliği. Yedi kaynağın incelenen sonuçlarında
eşdeğer baş-katsayı teoremi saptanmadı. Özel uygulama ve açık kalan
terim de özgünlük/önem bakımından dış değerlendirme gerektirir.
