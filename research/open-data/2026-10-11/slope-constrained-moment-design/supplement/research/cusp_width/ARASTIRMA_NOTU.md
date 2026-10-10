# R05: iki foldun hareketi ve üç köklü bölgenin sonlu genişlemesi

20 Eylül 2026. Bu notun dayanağı [analitik kanıt](PROOF.md),
[yeniden üretim dosyaları](README.md) ve
[çalışma defterindeki](../CALISMA_DEFTERI.md) D002-D008 kayıtlarıdır.

**Yeni sonuç:** Sertifikalı cusp eğrisi boyunca, daha önce incelediğimiz
sonlu kontrol penceresinin tamamında üç gerçek köklü bölgenin nasıl
genişlediğini hesap destekli olarak doğruladık. Nu azaldıkça üst fold
yukarı, alt fold aşağı ilerliyor. Her kesiti kendi tam cusp merkezine
taşıdığımızda bölgeler birbirini kapsayarak genişliyor.

## Önceki adımın üzerine ne eklendi?

R04, her kesitte iki fold bulunduğunu, aralarında tam üç basit gerçek
kök olduğunu ve genişliğin yaklaşık ell^(3/2) ölçeğinde büyüdüğünü
gösteriyordu. Ayrıca bu başterimin katsayısı C(nu) için değişim yönünü
kanıtlamıştı. Bu, tek başına sonlu ell'deki genişliğin de aynı yönde
değiştiğini göstermiyordu.

R05 bu eksik adımı tamamlıyor. Üstelik sadece toplam genişlik değil,
iki sınırın ayrı ayrı hareket yönü de belirleniyor. Dolayısıyla bir
sınırın diğerinin hareketini telafi ettiği bir durum söz konusu değil;
üst ve alt sınır dışarı doğru açılıyor.

## İddianın tam kapsamı

Merkez, yaklaşık hesaplanan nokta değil, varlığı ve tekliği daha önce
kanıtlanan tam cusp c(nu). s=t-t*(nu), ell=lambda-lambda*(nu),
m=mu-mu*(nu) yazıyoruz. Sonuç

\[
-29\le\nu\le0,\qquad 0<\ell\le10^{-6}
\]

boyunca, |s|<=0.003 ve |m|<=2*10^-9 olan yerel pencerede geçerli.
Üst ve alt fold için

\[
\partial_\nu m_{\rm üst}<0,\qquad
\partial_\nu m_{\rm alt}>0.
\]

Bu nedenle nu **azaldığında** üst sınır yükseliyor, alt sınır alçalıyor.
İki sınır arasındaki W genişliği için iki hesap yönteminin de doğruladığı
okunabilir ortak sınır

\[
0.0003\ell^{3/2}< -\partial_\nu W_\nu(\ell)
<0.003\ell^{3/2}.
\]

Ell=0'da genişlik sıfır; sıkı eşitsizlik orada iddia edilmiyor.
Kök sayımı bütün gerçek eksen için değil, belirtilen t penceresi için.
Kapsama ilişkisi, kesitleri kendi cusp merkezlerine taşıdıktan sonra
geçerli; mutlak lambda,mu düzlemindeki yerleri aynı değil.

## Neden yalnızca grafiğe bakarak söylenmiş bir sonuç değil?

Fold hareketini veren B=(4 lambda*' D2+D6/4)/D4 ifadesinde cusp'ta
B(0)=mu*', B'(0)=B''(0)=0 bulunuyor. İlk etkili türev B'''(0),
önceki C'(nu) sonucuna tam bir özdeşlikle bağlanıyor. Dördüncü türev
ve beşinci türev kalanı açık sınırlarla denetlenerek B'''(s)>0 sonucu
bütün |s|<=0.00075 aralığına taşınıyor. Bu s aralığı, hedeflenen sonlu
ell penceresinin tamamındaki iki foldu kapsıyor.

İlk kaba hata tahmini daha geniş aralıkta yetmedi. Bu tanılama
[saklandı](diagnostics/README.md); sınırın yetmemesi, teoreme
karşıörnek diye yorumlanmadı. Daha keskin cebir ve kalan hesabı sonucu
58 parametre hücresinin tamamını kapsadı.

Kontroller birbirinden farklı görev görüyor:

- FLINT/Arb hesabı bütün 58 hücre için interval kapsamaları üretiyor.
- Ayrı rasyonel denetçi, FLINT'i ve üretici jet kodunu kullanmadan
  fold diferansiyel denklemlerinden türev sınırını yeniden hesaplıyor.
- Tam kesirli cebir kontrolleri, iptalleri ve iki farklı türev yöntemini
  sınayıp 36 yeni türev-kapsama karşılaştırması yapıyor.
- 27 bağımsız mpmath türev hesabı ek sayısal uyum sağlıyor.
- Şekil için 128 fold kök kutusu doğrulanıyor; ayrı rasyonel denetçi
  bunların daralma, kök yarıçapı ve genişlik hesaplarını kontrol ediyor.
  Uç kesit Taylor hesabına ayrıca 60 doğrudan integral karşılaştırması yapılıyor.

Rasyonel denetçiler kaydedilen integral/Taylor kapsamalarını girdi
kabul ediyor. Mpmath hesabı rigoröz integral kanıtı değil. Dış uzman
incelemesi ve literatürde özgünlük değerlendirmesi hâlâ gerekli.

## Somut bir sonlu kesit

Ell=10^-6 için doğrulanmış aralıkların yaklaşık orta değerleri:

| Kesit | Üç köklü bölgenin sonlu genişliği |
|---|---:|
| Quartic cusp Q, nu=0 | 1.29460951629 × 10^-9 |
| Sextic cusp S, nu yaklaşık -28.82453269539050 | 1.3269052469 × 10^-9 |

Bu kesitte artış yaklaşık **%2.494631**. Sertifika daha somut olarak
%2.49463101 ile %2.49463103 arasında bir artış veriyor. Bu sayı,
R04'ün ell sıfıra giderken elde edilen C katsayısındaki yaklaşık
%2.4946327745 artışından ayrı tutuluyor. Bütün ell'lerde aynı yüzdelik
artış var denmiyor.

S kesitinde nu, tam sextic cusp değerinde sabit tutulup lambda ve mu
değiştiriliyor. Bu, ilk sextic cusp'ın bulunduğu mu=0, (lambda,nu)
kesitinden farklı bir kontrol kesiti; karşılaştırma boyunca aynı
lambda,mu yönlerinin kullanılması böyle sağlanıyor.

## Makaledeki yeri ve grafikler

Makalenin anlatısı artık üç bağlı sonuç etrafında kurulabilir:

1. Quartic ve sextic cusp'lar aynı sertifikalı eğriye ait.
2. Bu eğrinin her kesitinde iki fold ve nicel bir/üç kök diyagramı var.
3. Belirtilen sonlu pencerede iki foldun hareket yönü ve üç köklü bölgenin
   iç içe genişlemesi belirlenebiliyor.

Bu, bulduğumuz noktaları saymaktan daha güçlü bir geometrik açıklama.
Özel ailenin bu davranışının literatürde hangi boşluğu doldurduğu ayrıca
gösterilmeli. Genel cusp normal formunun, 3/2 üssünün veya standart
daralma yönteminin icat edildiği iddia edilmiyor. Fiziksel bir uygulama
için de ayrıca bir model bağlantısı gerekiyor.

Makale için iki İngilizce şekil hazırlandı:

- [Birinci şekil](output/pdf/figure_1_cusp_geometry.pdf): ortak bir/üç
  kök bölgeleri, fold kapsamaları ve cusp boyunca C katsayısı.
- [İkinci şekil](output/pdf/figure_2_finite_width.pdf): gerçek Q/S fold
  örnekleri ve bütün nu/ell aralığı için pozitif genişleme-hızı sınırları.

Şekiller PDF/EPS/SVG olarak vektörel; PNG önizlemeleri de var.
[LaTeX şekil eki](paper/figures.tex),
[teorem eki](paper/finite_width_section.tex) ve
[yerleştirme notu](paper/MAKALEYE_YERLESTIRME.md) ayrıca hazırlandı.
PDF'ler oluşturulup tekrar görüntülendi; LaTeX ekleri bu ortamda
derlenmedi. Hedef dergi seçildiğinde o derginin ölçü ve dosya kuralları
uygulanmalı.

Grafik çizgisi, ispatın yerini almıyor. Noktalar arasındaki interpolasyon
şekil açıklamasında belirtiliyor; uniform teoremler ayrı dayanağa sahip.
Özgün TeX ve R01-R04 paketleri değiştirilmedi. Yeni sonuçlar R05'te
ayrı ve izlenebilir olarak tutuluyor.

## Sonraki bilimsel karar

Artık aynı eksende daha çok nokta üretmek tek başına en yararlı adım
değil. Bir sonraki aşamada bu geometrinin özel deforme integral ailesi
için matematiksel önemini ve en yakın literatür karşısındaki farkını
belgelemek; R01-R05'i tek, tutarlı bir teorem zinciri halinde yazmak
yerinde olur. Daha geniş pencere veya çekirdek pertürbasyonuna dayanıklılık
ayrı bir sonraki araştırma olabilir. Yayın kabulü veya akademik derece
eşdeğerliği bu hesap paketinden otomatik çıkmıyor.
