# R22 — Katsayı, işaret ve düzenlilik sınaması

21 Eylül 2026. Üç örnek kompakt aralıkta, tek alt moment ∫g=0 ile
çalışır. Theta çekirdeği değillerdir. Amaç genel formülü, katsayının
işaretini ve düzenlilik varsayımının sınırını ayrı ayrı sınamaktır.

## 1. R21'in iki-geçişli örneği

[-1,1]'de q₀=1, q₁=(x²−1/4)(1+βx), f=1/8 ve β=1/4.
R21'de tam optimum, c±=d±1/2 ve
2d+3βd²+βa²=0 ile belirlenmişti. Burada aynı gerçek optimum kullanılır.

Merkez denklemi ve doğrudan beş parçalı integralden

\[
 d=-\frac\beta2a^2-\frac{3\beta^3}{8}a^4+O(a^6),\quad
 S(a)=\frac12-\frac23a^2+\frac{\beta^2}{2}a^4+O(a^6). \tag{E1}
\]

Genel katsayı formülünün ayrı hesapladığı değerler:

\[
 D=\frac12,\quad\Gamma=2,\quad
 G=\frac{256}{63},\quad B=\frac{244}{189},\quad
 \mathcal R=\frac{134}{567},\quad
 \mathcal P=\frac{3721}{18144},\quad\Xi=\frac1{32}. \tag{E2}
\]

Sonuç:

\[
 \boxed{\delta(M)=\frac14+\frac{1}{48M^2}
                    +\frac{253}{49152M^4}+O(M^{-6}).} \tag{E3}
\]

C₄=253/49152≈0.005147298177083333. d(a), S(a), A(a), a=0 yakınında
çift analitiktir. ε=1/M için a−εA(a)=0 denkleminin a türevi başlangıçta
1'dir; analitik IFT tek ve tek-fonksiyon a(ε) dalını verir. A(a(ε))
çift analitik olduğundan gösterilen O(M⁻⁶) kalanı geçerlidir. Bu bir
açık uniform hata sabiti değildir. Aşağıdaki polinom örneğinde de aynı
analitik dönüşüm uygulanır.

Asimetri parametresini sabit |β|<1 içinde değiştirmek de açıklayıcıdır:
D=1/2, Γ=2 ve C₂=1/48 aynı kalır; buna karşılık

\[
 C_4(\beta)=\frac1{1024}\left(\frac{16}{3}-\beta^2\right). \tag{E4}
\]

Böylece aynı baş katsayıya sahip tasarımlar, dördüncü mertebede
ayırt edilebilir. Her sabit β için yeterince büyük M anlaşılır;
bütün β aralığında ortak bir bütçe eşiği burada iddia edilmiyor.

Taze rasyonel çevrelemelerle, iki terimli yaklaşımın hatası incelendi:

| Parametrik bütçe | Yalnız M⁻² ile mutlak hata | M⁻⁴ eklenince mutlak hata | Yeni/eski hata oranı |
|---|---:|---:|---:|
| M(1/20)≈5.0167204417 | 8.2343972×10⁻⁶ | 1.0796855×10⁻⁷ | ≈0.0131119 |
| M(1/200)≈50.0016667203 | 8.2356640×10⁻¹⁰ | 1.0849399×10⁻¹³ | ≈0.000131737 |

Tablo yuvarlatılmış gösterimdir. Kesin kesir aralıkları
[sertifikada](results/certificate.json). Hata oranı örneklenen altı
bütçede 1'den küçüktür; bu örneklerden bütün M'ler için aynı oran
çıkarılmaz. Hata, toplam genlik farkı değil yaklaşımın gerçek minimumdan
sapmasıdır. M(a) sayılarının yalnız yaklaşık gösterimi tabloda yer alır.

## 2. Düzgün bir örnekte negatif C₄

[-1,1]'de q₀=1, q*=q₁=x−3x³+9x⁵ ve f=5/8 olsun. Çünkü

\[
 1-3x^2+9x^4=(3x^2-1/2)^2+3/4>0, \tag{E5}
\]

q*'ın tek sıfırı 0'dır ve r=1. Teklik, basitlik ve rank koşulları
sağlanır. Teklik/çiftlik nedeniyle merkez 0 ve dual katsayı 0 olarak
kalır; sₐ=clip(x/a,−1,1) alt momenti ve hücre dengesini tam sağlar.
R21'in destek eşitsizliği bu profilin gerçek optimum olduğunu verir.

Doğrudan üç parçalı integral:

\[
 S(a)=\frac52-\frac{a^2}{3}+\frac{3a^4}{10}-\frac{3a^6}{7},
 \quad A=\frac{5}{8S},\quad M=A/a. \tag{E6}
\]

0<a≤1/5 için S>0 ve S+aS′=5/2−a²+(3/2)a⁴−3a⁶>0 olduğundan
bu parametrizasyon bütün yeterince büyük M'leri kapsar. Burada
D=5/2, Γ=1, t=0, u=−18, B=0, P=0 ve Xi=3/10'dur. Sonuç:

\[
 \boxed{\delta(M)=\frac14+\frac{1}{480M^2}
                      -\frac{1}{15360M^4}+O(M^{-6}).} \tag{E7}
\]

Dolayısıyla genel C₄'ün pozitif olması zorunlu değildir. P≥0 olması
ile C₄≥0 olması aynı iddia değildir. Bu örneğin temel ağırlığı w=1
pozitiftir; işaret değiştiren q₁ hedef moment yoğunluğudur.

## 3. C² olup M⁻⁴ katsayısı bulunmayan örnek

q₀=1, q*=q₁=x+sgn(x)|x|⁵ᐟ², f=11/28. [Genel ispatın](PROOF.md)
F16–F18 adımları bütün koşulları ve doğrudan integrali verir:

\[
 S=\frac{11}{7}-\frac{a^2}{3}-\frac8{63}a^{7/2},\qquad
 \delta(M)=\frac14+\frac7{2112M^2}
               +\frac1{6336M^{7/2}}+O(M^{-4}). \tag{E8}
\]

M⁻³ terimi yoktur, fakat sonraki ilk etki M⁻⁷ᐟ² ölçeğindedir. Bu nedenle
M⁴[δ(M)−δ₀−C₂/M²] sınırsız büyür. Sadece C² düzenlilikle bir C₄
ilan edilemeyeceğini gösteren somut sınır örneğidir.

Rasyonel örnek genişlikleri 1/25, 1/100, 1/400, 1/1600 seçildi.
Karekökleri rasyonel olduğundan a⁷ᐟ² ve tam hedef integrali rasyoneldir;
bu noktalarda hiçbir kayan noktalı kök hesabına ihtiyaç duyulmaz.

## 4. Yeniden üretim ve kontrol

- 12 tam cebir grubu: simetrik hücre Taylor katsayıları; her iki geçiş
  yönünde kare tamamlama; örtük a=A/M dönüşümü; hatalı dönüşümü yakalayan
  negatif kontrol; bağımsız beş/üç parçalı integraller; katsayılar ve
  C² karşıörneği; iki momentli Gram kimliği ve baz değişmezliği.
- 16 parametrik bütçede 132 dışa yuvarlatılmış rasyonel aralık kaydı.
  R21 üreticisi yeniden çalıştırıldı ve önceki çıktıyla aynı bulundu.
  İki düzgün örnekte toplam 12 bütçe için dördüncü mertebe eklemenin
  yaklaşım hatasını düşürdüğü aralık hesabıyla kontrol edildi.
- İki-geçişli örnekte eski bağımsız integral çözücüsü taze çalıştırıldı;
  diğer ikisinde fonksiyon değerlerinden doğrudan parçalı integrasyon
  yapıldı. 90/130 basamakta 32 koşu; 132 niceliğin tümü rasyonel
  aralıklarda, hassasiyet farkları <10⁻⁷⁰. Bu hesaplar rigoröz ispatın
  yerine konmayan ayrı sayısal tanılardır.

[Tam cebir](results/algebra.json), [sertifika](results/certificate.json),
[ayrı integraller](results/integrals.json), [tam tablo](results/TABLE.md),
[grafik](figures/fourth_order.png).
