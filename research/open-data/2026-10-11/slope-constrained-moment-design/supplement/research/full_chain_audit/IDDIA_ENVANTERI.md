# R01–R12 iddia ve denetim envanteri

21 Eylül 2026, Europe/Istanbul. Bu belge yeni sonuç içermez. Önceki
araştırma paketlerinin sonuçlarını ve ispatta kritik ara adımlarını
ayrı satırlara ayırır. Başlangıçtaki makale bu zincirin kanıt kaynağı değildir.

**Durum anahtarı:** **M** = mevcut makine sertifikası yeniden üretildi ve
denetçi yeniden çalıştı; analitik dayanak ayrıca okundu. **A** = analitik
ispat adımları yeniden incelendi, geçersiz kılan hata saptanmadı; bu bir
ispat asistanı veya dış matematikçi onayı değildir. **K** = kapsam, kaynak
veya yorum kontrolü. M/A birlikte kullanılabilir. Bütün satırların geçerli
olduğu alan kendi varsayımları ve özgün ispat dosyasıyla sınırlıdır.
Literatür önceliği bu denetimle kesinleşmiş değildir.

Her bölümdeki bağlantılar özgün ispatı ve bu turdaki koşu kayıtlarını
gösterir. Koşuların tam listesi [denetçi özeti](replays/summary.json) ve
[üretim özeti](regenerations/summary.json) içindedir. Sayıların birebir
tekrarı [aralık karşılaştırmasında](regeneration_comparison.json), ek
130 basamak kontrolü [ayrı kayıtta](precision_comparison.json) bulunur.

## R01 — İntegral, iki cusp ve ilk yerel kök sayımı

[İspat](../cusp_verified/PROOF.md),
[Q yeniden üretimi](regenerations/01_certify_cusp_family_quartic/run.json),
[S yeniden üretimi](regenerations/01_certify_cusp_family_sextic/run.json),
[sayısal çapraz kontrol](replays/01_check_independent/run.json),
[regresyonlar](replays/01_test_validated_flow/run.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R01.01 | Theta çekirdeği u≥0 üzerinde pozitif; çift üstel azalma sonlu kontrollerde integrali ve gerekli türevleri tanımlar. Seri ve sonsuz aralık artıkları ayrıca sınırlandırılıyor. | A/M; kesilmiş seri tek başına tam integral sayılmıyor. |
| R01.02 | ∂λDₙ=−Dₙ₊₂/4, ∂μDₙ=Dₙ₊₄/16, ∂νDₙ=−Dₙ₊₆/64. İntegral altında türev ve işaret/faktörler doğru. | A; yeni tam cebir denetimi ilgili kullanımları da kapsıyor. |
| R01.03 | ν=0 kesitindeki Q ve μ=0 kesitindeki S, belirtilen kutularda tek çözüm: F=Fₜ=Fₜₜ=0. | M; Banach kendine gönderme ve daralma. Teklik bütün uzay için değil. |
| R01.04 | Q ve S'de D₃>0 ve iki kontrolün ilgili determinantı sıfırdan farklı; sıradan cusp açılımı. | M/A; fonksiyonun üçlü sıfırı ile potansiyelin A₃ adı ayrılıyor. |
| R01.05 | Yerel fold açılımının λ ikinci dereceden katsayısı 2; kübik katsayılar determinant/türev ifadeleriyle doğru. | M/A; bu pakette kalanla açık sonlu komşuluk henüz verilmez. |
| R01.06 | Q'nun iki kontrol tanığında ortak t penceresinde bir ve üç basit gerçek kök. Ayrıca 130 basamak Q kutusu 110 basamak kutusunun içinde. | M; işaretler ve Rolle üst sınırı birlikte kullanılıyor. |

## R02 — Tek cusp çevresinde bütün sonlu bölge

[İspat](../cusp_region/PROOF.md),
[yeniden üretim](regenerations/02_certify_region/run.json),
[tanık denetimi](replays/02_check_witnesses/run.json),
[regresyonlar](replays/02_test_region/run.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R02.01 | ∣t−t₀∣≤0,003, ∣λ−λ₀∣≤10⁻⁶, ∣μ−μ₀∣≤2×10⁻⁹ penceresi boyunca gerekli türev ve uç işaretleri. | M; t₀,λ₀,μ₀ bu paketin kayıtlı tam ikili merkezidir. |
| R02.02 | F=Fₜ=0 için t ile sürülen tek kontrol grafiği; fiziksel penceredeki bütün çoklu kökleri kapsar. | M/A; ortak yardımcı kutuda tekdüze daralma ve teklik. |
| R02.03 | Δ=D₃D₄−D₂D₅<0; λ′=4D₂D₄/Δ, μ′=16D₂²/Δ; fold boyunca D₂ sıkı artar. | M/A; türevler tam implicit denklemden geliyor. |
| R02.04 | Tek cusp, ondan çıkan iki fold kolu; başka çoklu kök yok; kollar sağ λ yüzüne çıkar. | M/A; grafik tekliği ve işaretler birlikte kullanılıyor. |
| R02.05 | Ayırıcı dışında bir/üç basit kök sınıflandırması pencerede tam. | A/M; uçlardan kök geçişi dışlanıyor, bileşenler tanıklarla tanımlanıyor. |
| R02.06 | Fold için 1,91–2,09 s² ve 1,72–1,94 ∣s∣³ sınırları; sonlu genişlik 1,14–1,46 ℓ^(3/2) aralığında. | M/A; yerel sonlu pencereye ait, global asimptotik iddia değil. |

## R03 — İki cusp'ın aynı dal ile bağlanması

[İspat](../cusp_connection/PROOF.md),
[58 hücrenin yeniden üretimi](regenerations/03_certify_connection/run.json),
[dal denetimi](replays/03_check_connection/run.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R03.01 | ν∈[−29,0] için 58 parametrik tüpte her ν'de tek cusp çözümü. | M; tüp dışındaki çözümler dışlanmıyor. |
| R03.02 | 57 komşu birleşmesi aynı dala ait; bir hücrenin ortak yüzdeki dar kök kapsaması komşunun teklik kutusunun içinde. | M/A; yalnızca büyük kutuların kesişmesine dayanılmıyor. |
| R03.03 | Dalın ν=0 ucu R01 Q ile; μ=0 geçişi R01 S ile aynı tam çözümdür. | M/A; içerme ve yerel teklik, ondalık yakınlıktan daha güçlüdür. |
| R03.04 | Dal boyunca D₃>8×10⁻¹⁴, D₄<0, D₆<0. | M; bu dalda dörtlü sıfır dışlanır, global yokluk çıkmaz. |
| R03.05 | 0,26<dμ/dν<0,34; μ=0 kesişmesi tektir. | M/A; monotonluk ve uç işaretleri. |
| R03.06 | t ve λ hareketleri ile μ sürüklenme aralıkları tüp verileriyle uyumlu. | M; merkez eğrisi tek başına ispat sayılmaz. |

## R04 — Cusp eğrisi boyunca ortak fold geometrisi

[İspat](../cusp_geometry/PROOF.md),
[yeniden üretim](regenerations/04_certify_geometry/run.json),
[denetim](replays/04_check_geometry/run.json),
[tam sembolik kayıt](symbolic_checks.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R04.01 | ν∈[−29,0] boyunca her tam cusp merkezinde aynı 0,003 / 10⁻⁶ / 2×10⁻⁹ penceresi. | M/A; yaklaşık merkez ile gerçek cusp farkı kapsanıyor. |
| R04.02 | Her kesitte tek cusp, iki fold kolu, eksiksiz bir/üç kök ayrımı; t uçlarından kök geçişi yok. | M/A; R02 argümanının tekdüze koşulları yeniden sağlanıyor. |
| R04.03 | 1,80–2,21 s², 1,61–2,09 ∣s∣³, 0,49–0,86 yarı-kübik katsayı ve 0,98–1,72 genişlik sınırları. | M; ortak sonlu pencere. |
| R04.04 | Başterim C=−8√2 D₃/(3D₄); dC/dν<0. | M/A; toplam dal türevi ve pay polinomu tam cebirle de kontrol edildi. |
| R04.05 | Q ve S başterimleri yaklaşık 1,29460899168 ve 1,32690473189; artış yaklaşık %2,49463277. | M; bu yüzde başterim içindir. |
| R04.06 | C'nin monotonluğu tek başına aynı sayısal pencerenin bütün sonlu genişliklerinin monotonluğu değildir. | K/A; R05'in ayrıca yaptığı iş gerekli. |

## R05 — Sonlu genişlik ve sıkı iç içelik

[İspat](../cusp_width/PROOF.md),
[genişlik üretimi](regenerations/05_certify_width/run.json),
[denetim](replays/05_check_width/run.json),
[uç foldları](regenerations/05_endpoint_folds/run.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R05.01 | Sabit cusp-merkezli ℓ için iki fold kolunun ν hız formülü implicit türevle doğru. | A/M; merkez hareketi toplam türevde hesaba katılıyor. |
| R05.02 | Taşınım fonksiyonunda B₀=μ*′, B₁=B₂=0, B₃=−32k′, B₄=96kA₃′. | A/M; 32 kimliklik bağımsız tam cebir kontrolüne dahil. |
| R05.03 | Dördüncü/beşinci türev kalanları ortak s≤0,00075 alanında kontrol edilir ve bütün ℓ≤10⁻⁶ kesitlerini kapsar. | M/A; sıfır yakınındaki iptal sıradan bölme ile kaybedilmiyor. |
| R05.04 | ∂νμüst<0<∂νμalt; sonlu üç köklü bölgeler ν artarken sıkı daralır. | M/A; her 0<ℓ≤10⁻⁶ için. |
| R05.05 | 0,0003 ℓ^(3/2)<−∂νW<0,003 ℓ^(3/2). | M; sonlu W, yalnızca C değil. |
| R05.06 | ℓ=10⁻⁶'da Q'dan S'ye sonlu genişlik artışı %[2,49463101;2,49463103]. | M; 128 fold örneği ve sürekli teorem ayrı rollerde. |

## R06 — Yapısal gerekçeler ve literatür sınırı

[Matematiksel konum](../cusp_literature/MATEMATIKSEL_KONUM.md),
[karşı örnek koşusu](replays/06_check_structural_example/run.json),
[bu tur kaynak kontrolü](KAYNAK_DENETIMI.md).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R06.01 | F(t;λ,0,0)=Hλ(2t); F(t;0,0,0)=ξ(1/2+it)/8. | A/K; frekans 2 ve normalizasyon 1/8 birincil kaynakla uyuşuyor. |
| R06.02 | Cusp normal biçimi ve 3/2 genişlik üssü klasik; bunlar kendi başına yeni sonuç değildir. | K; özgünlük nicel özel sonuçla ilgili olabilir. |
| R06.03 | Isı akışı türev özdeşlikleri tek başına C′ işaretini zorlamaz; kayıtlı polinom örnek bunu sağlar. | A/M; pozitif integral çekirdeği sınıfında karşı örnek iddia edilmez. |
| R06.04 | Kompakt dalda sıkı C′ işareti ve analitiklik, yeterince küçük fakat burada açık boyutu belirtilmemiş pencereyi nitel olarak kontrol eder. | A; R05 açık tam pencereyi ve hata sınırını ekler. |
| R06.05 | Yakın literatürle kıyaslanabilecek katkı adayları var; öncelik veya yayın kabulü kesinleşmiş değil. | K; kaynak künyeleri kontrol edildi, kapsamlı öncelik taraması yapılmadı. |

## R07 — Genel küçük hata ve özel konum-koruyan yön

[İspat](../cusp_robustness/PROOF.md),
[sağlamlık üretimi](regenerations/07_certify_robustness/run.json),
[sağlamlık denetimi](replays/07_check_robustness/run.json),
[özel yön denetimi](replays/07_check_pinned/run.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R07.01 | Kontrollerden bağımsız tek gerçek h ve ∥h∥∞≤10⁻¹⁸ için bütün [−29,0] cusp yayı ve ortak yerel geometri korunur. | M/A; εBₙ moment hatası bütün kutuda uygulanır. |
| R07.02 | Cusp koordinat kayması <4×10⁻⁵; μ=0 kesişmesinin ν kayması <2×10⁻⁴; 0,26<μ′<0,34. | M/A; 58 tüp ve 57 teklik birleşmesi. |
| R07.03 | Seçili cos(2au) yönünün yaklaşık 4,926×10¹¹ büyüklüğündeki μ duyarlılığı. | M/A; sonsuz küçük türev, sonlu genlik için doğrusal eşitlik değil. |
| R07.04 | Dört düşük kosinüs modunun tam moment kofaktörleri ilk üç momenti yok eder; Q tam sabit. | M/A; katsayılar ondalık yaklaşık sıfırlarla tanımlanmıyor. |
| R07.05 | Bu özel h₀ için ∥h₀∥∞=1; ε∈[−1/2,1/2] pozitifliği korur. | M/A; katsayı üst sınırı ve h₀(π/2)=1 birlikte. |
| R07.06 | Q'da üçüncü ve dördüncü türevler dejenerasyondan uzak kalır; ilgili alt oran ≥0,7995. | M; bu aşamadaki yerel sonuç bütün yayı otomatik kapsamaz; R08 ayrıca doğrular. |

## R08 — İki parametreli cusp yüzeyi

[İspat](../cusp_pinned_family/PROOF.md),
[4002 momentin taze hesabı](regenerations/08_build_moment_cache/run.json),
[aile üretimi](regenerations/08_certify_family/run.json),
[denetim](replays/08_check_family/run.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R08.01 | ρ=ε/(1+αε) değişkeni ve pozitif çarpanla eşdeğer aile; ε∈[−1/2,1/2] için kapsanan ρ alanı yeterli. | A/M; çarpan sıfır olmadığından kök çokluğu değişmez. |
| R08.02 | [−29,0]×[−1/2,1/2] boyunca cusp yüzeyi; 232 hücre ve 402 komşu teklik birleşmesi. | M/A; yalnızca örnek ızgarası değil, her parametre için. |
| R08.03 | ν=0 kenarı her genlikte aynı Q; her genlikte tek μ=0 geçişi. | M/A; başka ν kesitlerindeki cusp konumları sabit değildir. |
| R08.04 | Bütün yüzey boyunca ortak pencere ve bir/üç kök ayrımı. | M/A; genel küçük-h teoreminin ε=1/2'ye izinsiz uzatılması değil. |
| R08.05 | ν yönündeki iki fold hareketi ve sonlu iç içelik korunur. | M/A; genel sürücü türev polinomları ayrıca tam cebirle kontrol edildi. |
| R08.06 | ε artarken üst fold aşağı, alt fold yukarı; 0,0002–0,005 ℓ^(3/2) genişlik-hız sınırı. | M/A; sabit merkezlenmiş kesit ve kayıtlı yön. |
| R08.07 | ℓ=10⁻⁶'da genlik uçları arasındaki daralmalar Q / ν=−15 / ν=−29 için yaklaşık %0,05201560 / %0,04707661 / %0,04254130. | M; 21 cusp ve 144 fold örneği yeniden denetlendi. |

## R09 — Daha güçlü şekil tasarımı ve dörtlü sıfır

[İspat](../cusp_shape_design/PROOF.md),
[tasarım üretimi](regenerations/09_certify_design/run.json),
[tasarım denetimi](replays/09_check_design/run.json),
[yerel denetim](replays/09_check_local/run.json),
[örnek denetimi](replays/09_check_samples/run.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R09.01 | 10,13,15,16 frekanslı yeni yön ilk üç momenti tam korur ve ∥h*∥∞≤1. | M/A; R07 yönüyle aynı fonksiyon değildir; norm eşitliği iddia edilmez. |
| R09.02 | İlk 16 kosinüs, üç moment kısıtı ve katsayı ℓ¹ bütçesinde başlangıç log-açıklık daralma hızı için tek optimum; S≈83,766976561084. | M/A; dual eşitlik ve kullanılmayan modlarda sıkı boşluk. Bütün L∞ sınıfının optimumu değil. |
| R09.03 | C(ε)/C(0)=(1+aε)/(1+bε), a≈−53,2790, b≈30,4880. | M/A; tam moment tanımı ve türev oranı. |
| R09.04 | Her r>0 için ε=(1−r)/(rb−a), C(ε)=rC(0), Φε>0,9672Φ. | A/M; her r için yerel sonuç, aynı sonlu pencere bütün r'lerde garanti değil. |
| R09.05 | ε∈[−1/128,1/128], ν=0 üzerinde ortak sonlu pencere ve sıkı daralma; 16 slab ve 15 teklik birleşmesi. | M/A; eski bütün ν yayına aktarılmaz. |
| R09.06 | ℓ=10⁻⁶'da sonlu W %[74,63952480;74,63952481] daralır. | M; başterimin %74,63954595 değeriyle karıştırılmıyor; 176 fold örneği. |
| R09.07 | ε=−1/b'de D₄=0 fakat D₃>0: λ,μ açılımı rank kaybeder; kök hâlâ üçlüdür. | M/A; dörtlü kök değildir. |
| R09.08 | ε=−1/a'da ilk dört türev sıfır, D₄<0 ve üç kontrol rankı üç. | M/A; değiştirilmiş pozitif çekirdekte, özgün sabit Φ'de değil. |
| R09.09 | Weierstrass hazırlama ve rank koşulu uygun yerel koordinatlarda x⁴+ux²+vx+w biçimini verir. | A; açık sonlu kontrol kutusu R10'un ayrı sonucudur. |

## R10 — Dörtlü sıfırın sonlu 0/2/4 geometrisi

[İspat](../swallowtail_window/PROOF.md),
[ortak pencere üretimi](regenerations/10_certify_window/run.json),
[pencere denetimi](replays/10_check_window/run.json),
[harita denetimi](replays/10_check_chart/run.json),
[örnek denetimi](replays/10_check_samples/run.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R10.01 | R09'un ε₄ çekirdeği sabit; g=24G/G₄(Q) aynı kök ve çoklukları taşır. | A/M; normalize eden sabit negatif olabilir, kökler değişmez. |
| R10.02 | ∣s∣≤2⁻⁷, ∣ℓ∣≤2⁻¹⁷, ∣m∣,∣ν∣≤2⁻³⁴ kutusunda 22<g₄<26 ve uç işaretleri. | M; ν değişimine uygun yeni majorantlar kullanılıyor. |
| R10.03 | Pencerede toplam çokluk en fazla dört; ayırıcı dışında 0/2/4 basit kök; bütün durağan değer işaretleri kök sayısını tam belirler. | A/M; sıfır olmayan dejenereli durağan nokta da kapsanır. |
| R10.04 | Her (s,ℓ) için yardımcı kutuda tek (m,ν) fold grafiği; fiziksel kutudaki bütün çoklu kökleri içerir. | M/A; farklı s değerlerinde kontrol uzayında kendiyle kesişme dışlanmaz. |
| R10.05 | Tek cusp kontrol eğrisi, iki sıradan üçlü kök kolu; g₃ toplam türevi 16–32, 0,8s²<ℓc<4s². | M/A; yardımcı kutuda tek dörtlü sıfır Q. |
| R10.06 | (−L,0,0), (−L,−L²,0), (L,0,0), L=2⁻²⁴ çevresindeki açık kutuların tamamında sırasıyla 0/2/4 kök. | M/A; tek noktaya ait sayım değil. |
| R10.07 | ℓ=L'de iki cusp ile tek bir kontrol çiftinde iki ayrı çift kök; kesişme enine. | M/A; bütün çift-fold kesişmeleri için global teklik iddiası yok. |
| R10.08 | 64×56 kapalı hücrenin 430/2184/190'ı sırasıyla 0/2/4 köklü; 780'i sınıflandırılmamış. | M; gri hücrelerin hepsi çoklu kök içeriyor denemez. |
| R10.09 | Görsel eksenleri kayıtlı terslenebilir afin kontrol dönüşümü; 90 geometrik daralma kutusu doğrulanır. | M/K; bilinmeyen normal-biçim haritası gerçek kontrol haritası yerine kullanılmıyor. |

## R11 — Genel koşullar ve minimum-norm formülü

[İspat](../kernel_design_principle/PROOF.md),
[aday üretimi](regenerations/11_certify_candidate/run.json),
[rasyonel denetim](replays/11_check_candidate/run.json),
[analitik yeniden okuma notu](ANALITIK_DENETIM.md).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R11.01 | tQ≠0, bir açık aralıkta pozitif yoğunluk ve yeterli üstel momentler altında p₀,…,pₘ bağımsız. | A; yalnız atomik veya keyfî imzalı ölçüye otomatik uygulanmaz. |
| R11.02 | Pozitif Gram matrisi, düzgün kompakt destekli moment sağ tersi ve sonlu Cₘ verir. | A; bütün çekirdeklerde ortak sayısal Cₘ veya büyük hedef için küçük bütçe garantisi yok. |
| R11.03 | δ*=∣f₃∣/D, D=p₃'ün span(p₀,p₁,p₂)'ye ağırlıklı L¹ uzaklığı; D minimumu elde edilir ve pozitiftir. | A; koercivite, analitik artığın sıfır kümesi ve işaret durağanlığı ayrı kontrol edildi. |
| R11.04 | Ölçülebilir minimum-norm h, −f₃ sign(r)/D; ρ-hemen her yerde tek. | A; L¹ katsayı vektörünün tekliği iddia edilmez; destek dışı değerler serbesttir. |
| R11.05 | Tam pozitif destekte δ*<1. δ*<1 ise düzgün pozitif tam-dörtlü/rank-üç tasarımların infimumu da δ*. | A; aynı infimum, düzgün sınıfta minimumun elde edilmesi değildir. |
| R11.06 | 40–43 kosinüs modlu uygun aday ∥h∥∞<2,381×10⁻⁷; bütün uygun h'ler için δ*>3,96×10⁻¹⁰. | M/A; katsayıların mutlak toplamı normun üst sınırıdır, tam norm değildir. |
| R11.07 | Adayda g₄<0 ve g₄(g₄g₇−g₅g₆)/4096<0; tam dörtlü kök ve rank üç. | M/A; R10'dan farklı çekirdek; sonlu harita aktarılmaz. |

## R12 — Kanıtlı yakın minimum

[İspat](../kernel_norm_threshold/PROOF.md),
[yeniden üretim](regenerations/12_certify_threshold/run.json),
[rasyonel denetim](replays/12_check_threshold/run.json),
[bu turdaki ek giriş denetimi](threshold_input_audit.json).

| Kimlik | Kontrol edilen iddia ve gerekçe | Durum / sınır |
|---|---|---|
| R12.01 | Sabit Q'daki dört tam moment koşulu ve ∥h∥∞ bütçesi hedefi doğru tanımlar. | A/K; frekans veya türev bütçesi yok. |
| R12.02 | Her sabit r=p₃−Σaᵢpᵢ için δ*≥f₃/∫∣r∣dρ. | A; aday a'nın tam optimum olması gerekmiyor. |
| R12.03 | 28 artık sıfırı kutusu ve 113 işaret yaprağı [0,1]'i boşluksuz kapsar; her kök kutusunda tek sıfır. | M; bunlar F'nin 28 sıfırı değildir. Farklı formülle yeniden denetlendi. |
| R12.04 | Yanlış işaret hata katkısı kutu başına ≤4βWₖRₖ; u≥1 kuyruğu ayrıca dahil; objektif için üst sınır. | A/M; kuyrukta artık sıfırlarını tek tek bulmak gerekmez. |
| R12.05 | Pozitif çift logistic yumuşatma ∥sη∥∞≤1; moment hatası ≤N Mⱼη². | A/M; tek hata fonksiyonunun iptali ve iki yarı eksenin katsayıları kontrol edildi. |
| R12.06 | Dokuz global Lipschitz majorantı 256 hücre ve kuyrukla geçerli. | M/A; bu tur 2304 hücre-sıra ve dokuz kuyruk sınırı yeniden değerlendirildi. |
| R12.07 | Dokuz kesikli moment ve yumuşatma etkileri önceki hata bütçelerinde kalır. | M; bu tur 297 farklı bölüm integrali ve ölçeklenmiş değişkende 1764 geçiş integraliyle ek kontrol. |
| R12.08 | Tam moment sistemiyle düzeltme; pozitif gerçek-analitik h, aynı Q'da tam dörtlü kök ve rank üç. | A/M; g₄ ve determinantın yayımlanan negatif aralıkları korunuyor. |
| R12.09 | 0,00000000091787079603827 < δ* < 0,00000000091787079608363; bağıl boşluk <5×10⁻¹¹. | M/A; evrensel alt sınır ve uygun tasarım üst sınırı. Kesin kapalı-form optimum veya tam-optimal düzgün fonksiyon değil. |
| R12.10 | Tam pozitif destekli bu örnekte sürekli/düzgün minimum elde edilmez; aynı infimuma yaklaşılır. | A; analitik artık işaret değiştirir, dual eşitlik minimumu sıçramalı işarete zorlar. |

## Bütün zincire uygulanan sınırlar

Bu tablodaki M işaretleri ortak Arb/FLINT aritmetik ve integrasyon
altyapısının doğruluğunu varsayar. Rasyonel denetçiler bu altyapıdan gelen
integral kapsamalarının tümünü bağımsız bir integrasyon kütüphanesiyle
ispatlamaz. mpmath karşılaştırmaları sayısal destek sağlar, rigoröz
integral sertifikasının yerini almaz. Tam polinom denetimi yalnızca
belirtilen cebirsel kimlikleri kapsar.

Analitik satırların değerlendirmesi gerekçeli iç denetimdir. Formal
doğrulama, dış uzman raporu, literatür önceliği ve yayın kabulü bu
envanterden çıkarılamaz. Fiziksel zaman, dinamik kararlılık, Riemann
hipotezi, özgün çekirdekte global dörtlü-sıfır varlığı veya yokluğu
bu araştırma zincirinin sonucu değildir.
