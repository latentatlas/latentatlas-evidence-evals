# “Certified” terimini hangi anlamda kullanıyoruz?

21 Eylül 2026. Bu not kullanıcının terimin teknik kullanım koşullarını
sorması üzerine yazıldı. Önceki paketler tarihsel kayıt olarak korunuyor;
buradaki ayrım bundan sonraki metinlerde de uygulanmalıdır.

Sayısal analizde “certified/validated” sıradan bir güven sıfatı değildir.
Kesin olarak tanımlanan bir matematiksel sonuç için, geçerli bir teorem
ve bütün ilgili hesap hatalarını kapsayan sınırlar sunma yükü taşır.
Örneğin bir kökün varlığını söylemek için küçük bir Newton residualı
yetmez; uygun varlık teoreminin hipotezleri doğrulanmalıdır. Bir katsayının
işaretini söylemek için de gerçek katsayıyı içeren aralık sıfırdan ayrılmalıdır.

Rump'ın doğrulama yöntemleri incelemesi, yöntemi matematiksel teoremlerin
varsayımlarını bilgisayar yardımıyla doğrulama şeklinde açıklar; yaklaşık
çözüm üretmek ile çözüm için doğrulanmış sınır üretmeyi ayırır. Aralık
işlemlerinin yanlış kullanımını da özellikle ele alır.
[Rump, Acta Numerica 2010, özellikle §§1.1–1.4](https://www.tuhh.de/ti3/rump/intlab/ActaNumerica2010.pdf).

Arb'nin temel kapsama ilkesi, her x∈X için f(x)∈F(X) olmasını ister.
Yuvarlama hatası çıktı yarıçapına eklenir. Ancak kendi yazdığımız sonsuz
seriyi kesiyorsak, atılan kuyruğun sınırını ayrıca gerekçelendirmeliyiz.
Arb kullanmak tek başına çevresindeki ispatı doğru yapmaz.
[Arb, Using ball arithmetic](https://arblib.org/using.html).
Bu belge eski Arb belgesidir; kütüphane 2023'te FLINT'e taşınmıştır.
Güncel FLINT sayfasına bu tur doğrudan erişim 403 döndürdü; erişilmiş
gibi gösterilmemektedir.

| Gerekli unsur | R24 katsayı sınırındaki karşılığı |
|---|---|
| Tam olarak hangi nesne? | R12/R15'in exact Q ve b* nesneleri; yaklaşık merkezler onların yerine konmuyor. |
| Geçerli matematiksel indirgeme? | R23 katsayı teoremi, R24 kök kimlikleri, kuyruk eşitsizlikleri ve matris kalıntı sınırı. Bunlar okunarak incelenmesi gereken analitik ispat parçalarıdır. |
| Aritmetik kapsama? | FLINT/Arb ball arithmetic ve ayrıca dışa yuvarlanan rasyonel yeniden hesap. |
| Kesme ve sonsuz kuyruk? | Atılan theta terimleri ve 1'den sonraki bütün kök katkıları ayrı çevreleniyor. |
| Parametre ve doğrusal çözüm belirsizliği? | Q/b* kutuları ve G⁻¹B çözümünün kalıntı hatası son katsayıya taşınıyor. |
| Gerçek karar ölçütü? | Her iki çevreleme de 2.49203004×10⁻³⁹ ile 2.49203006×10⁻³⁹ arasında; bu aralık sıfırdan kesin ayrılıyor. |
| Denetlenebilir uygulama? | Kod, girdi aralıkları, sürümler, kaynak bağımlılıkları, yeniden üretim komutları ve dosya hash'leri saklı. |

Bu tur R24'ün aralık üreticisi ve rasyonel denetçisi yeniden çalıştırıldı;
kayıtlı hesaplar aynı baytlarla yeniden üretildi. Bu, tekrar üretilebilirlik
ve hesap zinciri için kanıttır; bütün önceki analitik lemmaların otomatik
ispatı veya bağımsız bir uzman incelemesi değildir.

Dolayısıyla R24'teki **belirli katsayı aralığı ve işareti** için teknik
“validated enclosure / doğrulanmış sayısal çevreleme” kullanımının somut
dayanakları vardır. “Bütün çalışma sertifikalıdır”, “hata ihtimali yoktur”,
“bağımsız kurum onayladı” veya “yayınlanabilirliği belgelendi” bu sonuçtan
çıkmaz. Bir analitik bağımlılık yanlışsa, ona dayanan sonuç da geri alınır;
başarılı testler bu kusuru kendiliğinden gidermez.

Bu bağlamda bir kurumdan sertifika almak veya bir ispat asistanı kullanmak
terimin ön koşulu değildir. Formal doğrulama ve dış uzman incelemesi ayrı,
değerli güvence katmanlarıdır. Bizim çalışmamızda ikisi de henüz yoktur.
Rasyonel denetçi aşkın fonksiyon aralıklarını Arb çıktılarından alır;
bu nedenle bütün yazılım yığınından bağımsız ikinci bir ispat değildir.
mpmath hesapları ise yalnız bağımsız sayısal sağlamadır.

Makale için tercih edilecek açık İngilizce ifade:

> We use “validated enclosure” for numerical intervals obtained with ball
> arithmetic and analytic bounds for truncation and tail errors. The
> computer-assisted arguments rely on the stated analytic lemmas and on
> the correctness of FLINT/Arb and our implementation. They have not been
> formalized in a proof assistant or independently refereed.

Bu paragraf bizim kendi kapsam beyanımızdır; bir kaynaktan alıntı değildir.
R25'in yeni sonlu-bütçe teoremi de aynı ayrımı korur: analitik ispat,
doğrulanan sayısal hipotezler ve yardımcı tanısal kontroller ayrı tutulur.

[R24 iddia incelemesi](../theta_fourth_order/REVIEW.md),
[R25 ispat](PROOF.md), [R25 denetim](REVIEW.md).
