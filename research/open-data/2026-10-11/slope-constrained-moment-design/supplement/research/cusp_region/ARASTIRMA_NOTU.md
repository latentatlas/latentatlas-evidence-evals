# R02: Cusp çevresinde bütün bir parametre bölgesini kapsayan sonuç

20 Eylül 2026. Hesap destekli kanıt ve yerel kontroller tamamlandı. Dışarıdan
uzman incelemesi ve literatürde özgünlüğün belirlenmesi henüz tamamlanmadı.

**Yeni kazanım:** Önceki iki ayrı parametre örneğindeki kök sayımlarından,
açık sınırları olan iki boyutlu bir parametre bölgesindeki bütün gerçek
kök çakışmalarını ve kök sayılarını sınıflandırmaya geçildi.

Fonksiyon yine quartic aile:

\[
F(t;\lambda,\mu)=\int_0^\infty\Phi(u)e^{\lambda u^2+\mu u^4}
                   \cos(2tu)\,du.
\]

Başlangıç sertifikasındaki tam dyadik merkez (t0,λ0,μ0) kullanılıyor.
Yaklaşık değerler (41.40034135868425, −3.645692061604919, 8.335120498918607).
Yeni sonucun kapsamı:

\[
|t-t_0|\le0.003,\quad |\lambda-\lambda_0|\le10^{-6},\quad
|\mu-\mu_0|\le2\cdot10^{-9}.
\]

Bu bölgedeki sonuçlar:

| Konum | Belirtilen t aralığındaki gerçek kökler |
|---|---|
| İki fold kolunun arasında | Tam üç basit kök |
| Fold kollarının dışında, parametre dikdörtgeninin içinde | Tam bir basit kök |
| Fold kollarının üzerinde, cusp hariç | Bir çift kök ve bir basit kök |
| Cusp noktasında | Bir üçlü kök |

Bu kapsamda tam bir cusp var. İki fold kolu ona bağlı ve başka bir çok
katlı gerçek kök yok. Parametre dikdörtgeninin tamamında t aralığının
uçlarında F sıfır olmuyor; kökler bu uçlardan girip çıkmıyor. Dolayısıyla
kök sayısı ayrımı yalnız örnek noktalara veya çizime dayanmıyor.

## Dal bağlantısı nasıl kapatıldı?

Her kutuda ayrı bir çözüm bulup bunların aynı dal olduğunu varsaymadık.
t aralığının tamamı için, aynı yardımcı kontrol kutusunda tek çözüm veren
bir daralma gösterildi. Daralma üst sınırı q<0.550; görüntünün kutuda
kalmasını sağlayan toplam sınır η+q<0.698. Böylece F=F_t=0 çözümleri
bütün aralıkta tek bir analitik eğri oluşturuyor.

Bu eğri üzerinde D_n=∂_t^n F ve Δ=D_3D_4−D_2D_5 olmak üzere

\[
\lambda'=\frac{4D_2D_4}{\Delta},\qquad
\mu'=\frac{16D_2^2}{\Delta}.
\]

İncelenen kutuda Δ<0 ve D_4<0. Ayrıca eğri üzerindeki D_2'nin toplam
türevi pozitif. Bu işaretler birlikte şunu sağlıyor: λ cusp'ta tek bir
minimuma sahip; μ eğri boyunca sıkı biçimde azalıyor; cusp iki kolun tek
birleşme noktası. Bu özdeşliklerin ilk kez bulunduğu iddia edilmiyor.

## Asimptotik açılımdan sonlu bölge sınırına

Önceki sonuçtaki O(s^4) biçimindeki açılımın yanında, artık sonlu bölgede
kullanılabilen eşitsizlikler var. Burada s=t−t*, yıldızlı nicelikler gerçek
cusp'ın koordinatları:

\[
1.91s^2\le\lambda(t)-\lambda_*\le2.09s^2,
\qquad
1.72|s|^3\le|\mu(t)-\mu_*|\le1.94|s|^3.
\]

Üç köklü bölgenin μ yönündeki genişliği W(λ) için, iki kolun mevcut olduğu
λ*<λ≤λ0+10^-6 aralığında:

\[
1.14(\lambda-\lambda_*)^{3/2}
\le W(\lambda)\le
1.46(\lambda-\lambda_*)^{3/2}.
\]

3/2 kuvveti standart cusp ölçeklemesidir. Burada eklenen bilgi, bu özel
integral ailesinde sınırları belirtilen sonlu bölge ve doğrulanmış sayısal
sabitlerdir. Bu ayrım makaledeki yenilik iddiasında korunmalı.

Sağ kenarda λ=λ0+10^-6 iken, fold kesişimlerinin μ kaymaları yaklaşık
+6.469598777×10^-10 ve −6.476496386×10^-10. JSON sertifikada bu sayılar
yuvarlak nokta tahminleri yerine kapsayan aralıklarla kaydedildi.

## Kontroller ve izlenebilirlik

- Önceki `cusp_verified` paketinin 25 dosyası özetleriyle kontrol edildi;
  yeni sonuçlar ayrı klasörde üretildi.
- Yeni Taylor formülü t, λ ve μ değişimlerini birlikte içeriyor. Merkezi
  türevler 34. dereceye, pozitif kalan sınırları 38. dereceye kadar kullanıldı.
- Beş kontrol grubu geçti: işaret değiştiren aralıkların sonlu kapsanması,
  kapsam dışı girdilerin reddi, teğet özdeşliğinin tam kesirli kontrolü,
  24 doğrudan integral karşılaştırması ve sınır fold noktalarında doğrudan
  integralle artık kontrolü.
- FLINT veya Taylor modülünü içe aktarmayan ayrı kesirli aralık denetçisi,
  genel daralmayı, dört yerel daralmayı, geometrik işaretleri, kök sayısı
  tanıklarını ve büyüme sınırlarını yeniden denetledi. Bu denetçi integral
  kapsamalarını veri olarak kullanır; onları ayrıca ispatlamaz.
- 115 basamaklı mpmath hesabında, iki farklı ve iki kontrolü de değiştiren
  noktada toplam altı türev değeri kaydedilen kapsamalara düştü. Bu destek
  bağımsız sayısal kontroldür; ikinci rigoröz integral ispatı değildir.

Geliştirme sırasında ilk koşu, işareti değişen bir aralık için kullanılan
kuvvet işlemi sonlu sonuç üretmeyince durdu. O koşudan sertifika üretilmedi.
İşlem, bütün gerçek aralıklarda geçerli tekrarlı çarpımla değiştirildi ve
bu durum için regresyon kontrolü eklendi. Tanı kaydı `diagnostics/` altında.
Bu, önceki matematiksel sonuçlara aktarılmış bir hata değildi.

## Bilimsel değerlendirme ve açık sorular

Önerilen ana teoremin yerel hesap destekli sürümü artık mevcut. Matematiksel
kazanım, bir cusp örneğinin çevresini bölge boyunca sınıflandırmak ve açık
nicel sınırlar vermek. Bölge küçüktür; tüm parametre uzayı veya tüm gerçek
eksen hakkında sonuç çıkarılmıyor.

Quartic ve sextic örneklerin aynı cusp eğrisinde bağlanması açık. Bu
sonuç, eski geniş devam kayıtlarını veya global A4 yokluğunu doğrulamaz.
Fiziksel bir model ya da zaman evrimi de kurulmuş değil.

Sıradaki araştırma için iki somut soru var: aynı yöntemle anlamlı biçimde
daha geniş bir bölgeyi kapsayabilir miyiz; üçüncü parametre ν serbestken
quartic ve sextic cusp'ları bağlayan düzenli bir cusp eğrisi var mı?
İkincisinde sayısal bir yol bulmak ile onu bütünüyle sertifikalamak ayrı
aşamalardır. Hangi yönün makaleye daha özgün bilgi katacağı, literatür
karşılaştırmasıyla birlikte seçilmeli.

## Bu turdaki sınırlı literatür kontrolü

arXiv üzerinde quartic deformasyon, cusp, üçlü sıfırlar ve yüksek ısı
akışlarıyla ilgili dar ve geniş anahtar kelime aramaları yapıldı. Dar
aramaların sonuç vermemesi bir öncelik kanıtı sayılmadı.
[Newman–Wu'nun incelemesi](https://arxiv.org/abs/1901.06596), Fourier
dönüşümlerinin karesel deformasyonları ve ölçü çekirdeklerine uzanan
bağlam için eklendi. Bu turda özet kaydı okundu; tam metin üzerinden
özgünlük karşılaştırması tamamlanmış sayılmıyor.

Ana kanıt: [PROOF.md](PROOF.md). Yeniden üretim: [README.md](README.md).
Şekil: [cusp_region.png](results/cusp_region.png).
