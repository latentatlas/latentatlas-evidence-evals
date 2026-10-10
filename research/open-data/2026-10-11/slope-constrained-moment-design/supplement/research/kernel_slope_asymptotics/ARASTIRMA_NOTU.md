# R15 — Eğim sınırının ek maliyeti için keskin asimptotik yasa

21 Eylül 2026. Aynı tam Q konumu, aynı dört moment hedefi ve aynı
bağıl genlik ölçüsü korunuyor. Kullanıcının «evet yapalım» onayı,
R14'ün ardından eğim sınırı değiştikçe ek maliyetin nasıl azaldığını
araştırmak için uygulandı. Uygulama/sektör merakı kapsamı değiştirmedi.

**Sonuç:** Uygun basit ve ayrık geçişler ile moment-rank koşulu altında

\[
\delta(M)=\delta_*+\frac{C_*}{M^2}+o(M^{-2}),\qquad M\longrightarrow\infty.
\]

Burada δ*, eğim kısıtı olmadan gereken en küçük ∥h∥∞; δ(M),
Lip_u(h)≤M koşuluyla gereken minimum. «Maliyet», çekirdekteki en büyük
bağıl değişiklik miktarıdır. Para, eğitim, işlem süresi, frekans veya
fiziksel enerji anlamına gelmez. M de özgün u koordinatındaki değişme
hızının üst sınırıdır.

Eğim sınırını iki katına çıkarmak, büyük-M rejiminde **minimumun
üzerindeki ek değişikliği** yaklaşık dörtte bire indirir. Toplam δ(M)
dörtte bire inmez: pozitif taban δ*'a yaklaşır.

## 1. Neden bu sonuç yalnızca sayısal eğri uydurma değil?

Alt sınır, en iyi sınırsız tasarımın her işaret değişiminde sonlu eğimin
zorunlu kıldığı kaybı toplar. Üst sınır, sıçramaları doğrusal geçişlerle
değiştirip üç geçiş konumunu ayarlayarak ilk üç momenti tam korur;
genliği ayarlayarak dördüncü koşulu da tam sağlar. İki hesap aynı
baş katsayıya ulaşır. Katsayı

\[
C_*=\frac{\delta_*^4}{3f_3}
\sum_k w(z_k)|r_*'(z_k)|
\]

ile belirlenir. r* optimal yardımcı artık fonksiyonu, zₖ onun basit
sıfırları, w pozitif integral yoğunluğudur. Bu zₖ'lar asıl F integralinin
yeni sıfırları değildir.

Bir geçişin yarı genişliği yaklaşık δ*/M'dir. Artık fonksiyonu basit
sıfır yakınında uzaklıkla doğrusal büyür. Dar geçiş boyunca bu doğrusal
kaybın integrali genişliğin karesi mertebesindedir. M⁻² ölçeğinin
geometrik nedeni budur; 1/3 katsayısı ayrıca tam rasyonel hesapla
kontrol edilen yerel integraldir.

## 2. Bu integral ailesinde koşullar sağlanıyor mu?

Yeni aralık hesabı, yalnızca eski yaklaşık katsayıları kullanmakla
kalmıyor. Gerçek dual minimumu, eski tam ikili-rasyonel merkez a₀
etrafında yarıçapı 2⁻⁴⁰ olan Öklid topunun içinde yerelleştiriyor.
Küçük gradyan ve pozitif eğrilik birlikte bu minimumun **tekliğini**
sağlıyor. Bu, dual katsayı a*'ın tekliği; sonlu-M tasarımının tekliği
iddiası değil.

- [0,1] içindeki 28 basit geçiş, bütün katsayı kutusunda doğrulandı;
  aradaki bölgeler 113 işaret aralığıyla kaplandı.
- [1,∞) bölümü kesilip atılmadı. Açık faz türevi sınırı bütün kuyruk
  köklerinin basitliğini ve ayrıklığını sağlıyor.
- İlk üç geçişin moment değerlendirme determinantı sıfırdan uzak.
  Böylece yumuşatma sonrası koşulları tam düzeltmek mümkün.
- Sonsuz ağırlıklı toplam yakınsak; u≥1 katkısı 5.705×10⁻⁶³'ten küçük.
- Sınırdaki işaret tasarımının dördüncü türevi ve üç-kontrol
  determinantı sıfırdan uzak. Küçük geçiş genişliklerinde aynı yerel
  geometrik özellikler korunuyor; açık bir başlangıç M değeri bulunmadı.

## 3. Okunabilir sayısal sonuçlar

| Nicelik | Doğrulanmış dış aralık / sınır |
|---|---|
| δ* | (0.00000000091787079603827, 0.00000000091787079608363) — R12 |
| Γ=Σw(zₖ)\|r*′(zₖ)\| | (1.297542117, 1.297542121) |
| C* | (9.20340371×10⁻²⁵, 9.20340375×10⁻²⁵) |
| C*/δ* | (1.002690547×10⁻¹⁵, 1.002690552×10⁻¹⁵) |
| Her M≥0.00002 için | δ(M)−δ* > 9.13976214×10⁻²⁵/M² |

Son satır asimptotik bir tahmin değil; gerçek minimuma göre geçerli
tek taraflı sonlu-M eşitsizliğidir. Bir eşleşen sonlu-M üst hata sınırı
henüz yoktur.

R14'teki M=0.00002 yerine yalnızca baş terim yazılırsa ek genlik
yaklaşık 2.30085×10⁻¹⁵, taban minimuma göre artış milyonda yaklaşık
2,5067 çıkar. Bu **gerçek sonlu-M farkının yeni bir sertifikası değildir**.
Geçerli iki taraflı sonlu-M sonucu R14'ün

`0.000000000917873080 < δ(0.00002) < 0.000000000917876530`

aralığıdır. Baş terimin bu aralıkla uyumlu olması, kalan terimin
büyüklüğünü ispatlamaz.

## 4. Bilimsel kazanım ve henüz açık olanlar

Artık yalnızca tek bir bütçedeki aralığı bilmiyoruz. Ek gereksinimin
neden oluştuğunu, hangi hızla azaldığını ve baş katsayısının hangi
yerel geçiş verilerinden geldiğini açıklayan bir ispat taslağımız var.
Genel önerme ağırlıklı moment problemleri için yazıldı; theta çekirdeği
koşulları hesapla doğrulanmış temel örneğimiz.

İspat, katsayısı belirlenmiş analitik bir sonuç olarak makaleye aday.
Klasik dualite, işaret tipi optimum ve örtük fonksiyon yöntemleri kendi
başlarına yeni yöntem diye sunulmayacak. Bu özel birleşimin ve katsayı
formülünün literatür önceliği henüz tamamlanmış bir taramayla ayrılmadı.
Yakın literatür ve kapsam [REFERENCES.md](REFERENCES.md) dosyasında.

Somut açık iş: o(M⁻²) yerine, belirtilen bir M aralığında kullanılabilen
kanıtlı kalan-terim sınırı elde etmek. Böylece asimptotik bilgi bir
tasarım hesabında hangi hata payıyla kullanılabileceği belli bir
araca dönüşür. Bu paket bunu yapmış sayılmıyor.

Sonlu-M optimumun tam şekli/tekliği, kütle koruma, fiziksel uygulama
ve yeni çekirdeğin sonlu 0/2/4 kök haritası eklenmedi. Doğrusal geçişler
Lipschitz sınıfta; düzgün pozitif sınıfta aynı infimum R13'ten gelir.
Düzgün bir minimumun elde edildiği söylenmiyor.

## 5. Denetim ve kayıt

[Açık ispat](PROOF.md) ve [sayısal sertifika](results/asymptotic_certificate.json)
birbirinden ayrıdır. 110 basamaklı Arb hesabını, FLINT kullanmayan
[rasyonel yeniden kurma](results/asymptotic_check.json) ve 80/110
basamakta 48/64 Gauss düğümlü [ayrı mpmath hesabı](results/coefficient_crosscheck.json)
izledi. Altı [tam cebir kontrolü](results/algebra_check.json) ayrıca var.

Üretimde her kök kutusunun üç kez kesin daralmasını istemek gereksiz
bir durmaya yol açtı: ikinci daralmadan sonra üçüncü yarıçap aynıydı.
Son kanıtlı kutuyu koruyup iyileşmeyen öneriyi kaydetmekle giderildi.
Rasyonel denetçide aralık çarpımını tam sayı gibi okuma ve çok küçük
kuyruk yoğunluklarında sabit 2⁻⁵¹² ızgaranın etkisi düzeltildi.
Matematiksel sınırlar gevşetilmedi; girdilerden exact rasyonel uçlar
okundu. İlk sürümler ve tanı [diagnostics/NOTES.md](diagnostics/NOTES.md)
altında saklandı. Eski paketler değiştirilmedi.

Şekiller: [geçiş ve yerel kayıp](figures/linear_transition_loss.png),
[katsayıya geçiş katkıları](figures/switch_contributions.png).
Şekiller gerçek optimum eğrisi diye sunulmuyor.

Analitik dış inceleme ve formal ispat henüz yok. Hata bulmaya yönelik
çoklu kontroller, «artık hata olamaz» garantisi olarak anlatılmıyor.
[Yeniden üretim](README.md), [kapanış denetimi](audit_report.json).
