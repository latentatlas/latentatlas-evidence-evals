# R18 — Katkı adayının daha yakın literatür karşısındaki durumu

21 Eylül 2026. Bu tur R17'de önerilen eşdeğer-formülasyon karşılaştırması
yapıldı. Yeni integral ailesi, yeni ana teorem veya yeni sayısal sabit
eklenmedi. Önceki sonuçlar yerinde; onların hangi bölümünün bilinen
bir yapıya dayandığı artık daha açık.

## En önemli sonuç

Yardımcı genlik/eğim optimizasyonu iki parametreli KR normuyla **birebir
aynı**. Benzerlik yalnız sözcüklerde değil, amaç fonksiyonu ve uygun
fonksiyon kümesinde. Moment koşulları eklenince de problem, klasik
minimax sayesinde bu normların bir aile üzerindeki infimumuna bağlanıyor.
Bu ilişki yeni bir yöntem iddiası olarak kullanılmayacak.

Asıl katkı adayımız, moment koşulları tam korunurken minimum genlikteki
artışın tam baş katsayısını belirlemek; bunu sonsuz geçişli theta
örneğinde sertifikalı ve açık bir hata bütçesiyle gerçekleştirmek.
Okunan yakın sonuçlar bu birleşik teoremi doğrudan vermiyor. Bunun
başka bir adla daha önce kanıtlanmış olması ihtimali açık kalıyor.

## İddia düzeyinde karar tablosu

| Öğe | Bu turdaki değerlendirme | Yeni makaledeki yeri |
|---|---|---|
| Genlik ve eğim sınırının birlikte kullanılması | Bilinen iki parametreli KR normu | Tanım ve atıflı arka plan |
| Moment kısıtlarını residual ailesinin infimumuna çevirmek | Klasik minimax uygulaması; E1–E3 | Kısa açıklayıcı lemma/atıf, özgünlük iddiası değil |
| Sınırsız minimumun işaret fonksiyonuyla verilmesi | Klasik moment/L¹ dualitesi; R17 | Arka plan |
| Yalnız M⁻² üssü veya üçgensel kaybın 1/3'ü | Tek başına yenilik için yetersiz | Mekanizma açıklaması |
| Tam moment koruması altında C*=δ*³Γ/(3D*) | İncelenen yakın sonuçta eşdeğeri saptanmadı; öncelik açık | Genel, koşullu katkı adayı |
| Gerçek dual optimum, sonsuz artık kökleri, Γ ve C* sertifikası | Mevcut R15 zinciri; bu tur değişmedi | Somut uygulamanın doğrulanabilir içeriği |
| Bütün M≥0.00002 için açık iki taraflı kalan terim | Mevcut R16 zinciri; bu tur değişmedi | Asimptotiğin nicel kullanım aralığı |
| Sonlu-M minimizerin tam şekli/tekliği | Gösterilmedi | İddia edilmez |
| Cusp eğrisinin tamamına aynı katsayıları taşımak | Gösterilmedi; nicel sonuç sabit Q'da | İddia edilmez |

## Neden moment düzeltmesi esas bir ayrım?

İşaret profilini eğim sınırına uygun biçimde yumuşatmak, korunması gereken
momentleri genellikle bozar. R15, seçilmiş geçiş merkezlerini ayarlayarak
bu momentleri tam geri getirir. Bunu yaparken baş mertebedeki kaybı
değiştirmediğini de gösterir. Böylece hesaplanan katsayı sadece belirli
bir deneme eğrisinin maliyeti değil, eşleşen alt ve üst sınırlarla
**minimum değerin** baş katsayısı olur.

Yine de bu argüman standart dualite, yerel integral hesabı ve örtük
fonksiyon teoremi kullanır. Makaleyi «yeni optimizasyon kuramı» diye
tanımlamak uygun olmaz. Kombinasyonun daha önce aynı varsayımlarla
yapılıp yapılmadığı ve ne kadar önemli olduğu ayrı değerlendirmedir.

## Yeni makale için güncellenmiş katkı paragrafı

> We study minimum-amplitude multiplier designs that impose exact
> higher-order-zero moment conditions on positive integral kernels,
> under a separate Lipschitz bound in the original integration variable.
> The associated support problem is a two-parameter
> Kantorovich–Rubinstein norm; finite moment constraints enter through
> standard minimax duality. Under simple-switch, separation, summability
> and moment-rank hypotheses, we identify the leading excess amplitude
> as the slope bound tends to infinity. The coefficient is expressed by
> a density-weighted sum of residual slopes at the switches. For a theta
> kernel at a fixed certified cusp, we verify the hypotheses and numerical
> constants, including the infinite switch tail, and give an explicit
> two-sided remainder valid on a stated range of slope budgets.

Bu paragraf taslaktır; «first», «novel norm» veya «complete solution»
iddiası içermez. Başlık önerisi değişmedi:
**Certified amplitude and slope costs for higher-order zeros of positive
integral kernels**. Cusp/fold geometrisi problemin nedenini ve geometrik
bağını anlatır; yeni makalenin bütün sonuçlarını tek geometrik devam
iddiasına dönüştürmek gerekmez.

## Yayın değeri açısından değerlendirme

Bu tarama özgünlük alanını daraltıyor; sonuçların matematiksel içeriğini
geri çekmeyi gerektirmiyor. Savunulabilir paket, bilinen normun yeniden
tanımı değil; genel koşullu katsayı sonucu, zorlu somut örnekte eksiksiz
varsayım doğrulaması ve açık uniform hata sınırıdır. Hakemli yayın için
aday olabileceği yönündeki değerlendirme sürer. Yayın hakkı/kabulü veya
genel teoremin önceliği bu taramayla kesinleşmiş değildir.

Bir sonraki somut iş, R15–R17 ispatını ve bu karşılaştırmayı kısa bir
makale çekirdeğinde birleştirmek: tam varsayımlar, tek ana asimptotik
teorem, theta uygulaması, açık kalan terim ve aynı notasyondaki yakın
literatür paragrafı. Dış matematiksel okumada özellikle «Bu katsayı
teoremi hangi bilinen sonuçtan doğrudan çıkar?» sorusu sorulabilecek
kadar belirgin bir metin oluşmalı. Bu belge dışarıya gönderim yetkisi
veya gönderim yapıldığı anlamına gelmez.

## Kayıt sınırı

Kaynaklardaki norm/toplam-varyasyon farkları, yarı-doğru ile kompakt
domain ayrımı, sınırsız dual optimumun sonlu M'ye taşınmaması ve sabit
atomik ızgaranın doygunluğu ayrıca kontrol edildi. Küçük rasyonel
örnekler sadece bu eşlemeleri denetler; R15/R16 ispatını veya literatür
önceliğini otomatik doğrulamaz. 18 eski manifest ve 847 dondurulmuş
dosya girdisi korunarak R18 ayrıca dondurulur.
