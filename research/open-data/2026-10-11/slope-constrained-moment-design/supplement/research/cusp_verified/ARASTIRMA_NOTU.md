# Matematiğe dönüş: elde edilen somut ilerleme

20 Eylül 2026. Bu not, `PROOF.md` ve `results/` içindeki hesap destekli yerel
sonuçları açıklar. İlk kez yapılmış olma, hakem kabulü veya akademik derece
eşdeğerliği hakkında karar değildir.

**Bu turdaki en önemli gelişme, altıncı derece terim olmadan da cusp
bulunmasıdır.** Eski sextic cusp korunuyor; daha sade quartic ailede ikinci
bir örnek ve onun yakınındaki gerçek kök geçişi eklendi.

## Sonuçların durumu

| İddia | Yeni durum | Sınır |
|---|---|---|
| Eski sextic cusp vardır ve yerel olarak tektir | Yeni doğrulayıcıyla daralma, üçüncü türev ve kontrol rankı testleri geçti | Yalnız açıkça kaydedilen küçük kutu; eski geniş teklik bölgeleri taşınmıyor |
| Quartic ailede cusp vardır | Yeni merkez, daralma sertifikası, sıfır olmayan üçüncü türev ve kontrol determinantı üretildi | ν=0, λ ve μ serbest; tüm cusp'ların sınıflandırması değil |
| Cusp çevresindeki fold eğrisi semicubical yapıdadır | Analitik örtük fonksiyon argümanı ve üçüncü derece katsayıları türetildi | Taylor kalanının açık sonlu bölge sabiti bu lemma için henüz verilmedi |
| Cusp yakınında bir/üç gerçek kök geçişi vardır | İki açık parametre seçimi ve t₀±0.003 aralığı için tam kök sayıları doğrulandı | Tüm kontrol düzlemini kapsayan faz diyagramı değil |
| Bulgular bağımsız hesapla destekleniyor | mpmath gerçek eksen integrasyonu iki merkezde ilk beş türevi yeniden üretti | Sayısal uyum, ikinci bağımsız rigoröz ispat değildir |
| Bulguların literatürdeki önceliği | Açık | Dar anahtar kelime taraması öncelik kanıtı sayılmadı |

Buradaki “doğrulandı”, belgelenen analitik sınırlarla çalışan yerel hesap
paketinin gerekli eşitsizlikleri geçmesi anlamındadır. Bir alan uzmanının
bağımsız incelemesi henüz yapılmadı.

## Yeni matematiksel sonuç neden değerli?

Quartic aile

\[
F(t;\lambda,\mu)=\int_0^\infty \Phi(u)e^{\lambda u^2+\mu u^4}\cos(2tu)\,du
\]

için yaklaşık

\[
t_*=41.4003413586842508894,\quad
\lambda_*=-3.64569206160491909881,\quad
\mu_*=8.33512049891860723771
\]

noktasında F=F_t=F_tt=0, F_ttt>0 ve bağımsız iki kontrol yönü vardır.
Bu, araştırmanın merkezini “altıncı derece terimle özel bir nokta”
anlatımından “dördüncü derece deformasyondaki doğrulanmış cusp ve kök
geçişleri” anlatımına taşıma olanağı verir.

Dördüncü derece deformasyonun yeterli olduğu gösterildi. En düşük mümkün
derecenin dört olduğu gösterilmedi. Yeni noktanın eski sextic cusp ile aynı
global dal üzerinde olduğu da henüz sertifikalanmadı. Pozitif μ kullanılması,
eski negatif μ aralığındaki dal iddialarıyla kendi başına bir çelişki değildir.

Standart ısı özdeşliği ayrıca fold eğrisinin yerel biçimini kısıtlıyor.
s=t−t* olmak üzere:

\[
\lambda(s)=\lambda_*+2s^2+1.908384250199\ldots s^3+O(s^4),
\]
\[
\mu(s)=\mu_*-1.830853594008\ldots s^3+O(s^4).
\]

Buradaki **2 katsayısı sayısal uyarlama değildir**; kullanılan
F_λ=−F_tt/4 normalizasyonundan analitik olarak çıkar. Diğer katsayıların
aralıkları hesaplanmıştır. Bu genel türetimin literatürde yeni olduğu ileri
sürülmüyor; somut aileye uygulanışı makalenin açıklayıcı bölümünü güçlendirir.

## Kök geçişi

Sertifikadaki tam merkezin μ₀ değeri sabit tutularak:

| λ seçimi | t₀−0.003 ≤ t ≤ t₀+0.003 içindeki gerçek kök sayısı |
|---|---:|
| λ₀−10⁻⁶ | Tam 1, basit |
| λ₀+10⁻⁶ | Tam 3, hepsi basit |

Bu sayılar grafikten okunmadı. İlk satır uç nokta işaretleri ve aralığın
tamamında F_t>0 ile; ikinci satır dört sırayla değişen işaret ve aralığın
tamamında F_ttt>0 ile gösterildi. İkinci durumda Rolle teoremi dördüncü bir
kökü dışlıyor. Taylor kalanları açık aralık sınırlarıyla taşındı.

`results/local_root_transition.png` sonucu gösterir. Şekil ispatın yerine
geçmez ve bütün spektrumu göstermez.

## Doğrulayıcıda ne değişti?

- Eski hesap çekirdeği içe aktarılmadı. Yeni integratör yalnız sonlu, tüm bir
  fonksiyonu görüyor; atılan çekirdek serisinin hatası gerçek eksende ayrıca
  sınırlandırılıyor.
- Sonsuz integral kuyruğu için bütün kuyruk boyunca geçerli azalma hızı
  kanıtlanıyor. Bir noktadaki negatif türev yeterli sayılmıyor.
- Normlar yönlü üst sınırlarla hesaplanıyor; çakışan aralıklar sıralanmıyor.
- Teklik, Hessian sınırının gerçekten geçerli olduğu kutuda daralma
  teoremiyle gösteriliyor.
- Tam dyadik merkez, önkoşullayıcı matris, hata sınırları, türev aralıkları
  ve dosya özetleri kaydediliyor. Ekrana yazılan kısa ondalıklar tam merkezin
  yerini almıyor.

On regresyon kontrolü geçti. İki merkezde 115 basamaklı bağımsız mpmath
hesabının ilk beş türevi, yeni aralık hesabının orta değerleriyle 10⁻¹¹¹'den
daha küçük mutlak farkla uyuştu. Quartic sertifika ayrıca 130 basamak,
20 çekirdek terimi ve farklı bölümlendirmeyle çalıştırıldı; daha hassas
kök kutusunun ilk sertifikanın teklik bölgesinde kaldığı kontrol edildi.

## Yayına doğru en güçlü devam

Önerilen makale sorusu artık daha somut:

> Dördüncü derece de Bruijn–Newman deformasyonunda bir cusp'ı, ona ulaşan
> fold kollarını ve yakınındaki gerçek kök bölgelerini tam olarak
> sertifikalayabilir miyiz?

İlk varlık ve iki yerel kök sayımı bu turda elde edildi. Makaleyi büyütecek
sonraki sonuç, cusp'a ulaşan iki fold kolunu açık bir kontrol bölgesinde
sertifikalamak ve bu kolların ayırdığı kök bölgelerini nicel olarak
belirlemektir. Kutu bağlantıları, teklik bölgeleri ve işaret tanıkları aynı
pakette yer almalı. Literatür karşılaştırması bu teknik çalışmayla birlikte
ilerlemeli; yalnız daha fazla basamak veya daha uzun tarama amaç yapılmamalı.

Yayın için hâlâ özgünlük incelemesi, bağımsız uzman okuması, tam kapsamlı
makale metni ve yeniden üretim paketinin dışarıdan denenmesi gerekiyor.
Mevcut uzun aralık A4/fold iddiaları bu pakete aktarılmadı. Fiziksel uygulama,
RH sonucu veya Global Talent uygunluğu bu hesaplardan çıkarılmıyor.

“Doktora sonrası düzey” resmi bir makale sınıflandırması değildir. Bu turda
ulaşılan şey, ileri araştırma yöntemleri kullanan, açık bir matematiksel
sonucu ve kontrol edilebilir kanıtını bir araya getiren bir çekirdektir.
Araştırmanın nihai ağırlığını özgünlük, kapsam ve alan uzmanlarının
değerlendirmesi belirleyecek.
