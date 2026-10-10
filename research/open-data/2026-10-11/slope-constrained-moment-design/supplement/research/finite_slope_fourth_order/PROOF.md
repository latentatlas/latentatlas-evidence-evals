# R22 — Sonlu geçişlerde dördüncü mertebe genlik maliyeti

21 Eylül 2026. Analitik araştırma notu. R21'in gerçek sonlu-eğim
optimumuna dayanır. İspat aşağıda verilir; formal ispat veya dış hakem
incelemesi değildir. Sonsuz geçişli theta ailesi bu teoremin kapsamında
değildir. Literatür önceliği ayrıca incelenmelidir.

## 1. Varsayımlar ve notasyon

[R21 teoreminin](../finite_slope_optimum/PROOF.md) bütün varsayımları
korunsun: I=[L,R] kompakt; q₀,…,qₘ∈C²(I); f>0; serbest uç değerler;
q*=qₘ−Σbⱼ*qⱼ'nin sonlu sayıda basit iç sıfırı zₖ; başka sıfır yok;
∫qⱼsgn(q*)=0 ve (qⱼ(zₖ)) tam satır rankında.

\[
 r_k=q_*'(z_k),\quad t_k=q_*''(z_k),\quad
 \sigma_k=\operatorname{sgn}(r_k),\quad \gamma_k=|r_k|,
 \quad D=\int_I|q_*|,\quad \Gamma=\sum_k\gamma_k,
 \quad \delta_0=f/D. \tag{F1}
\]

Qₖ=(q₀(zₖ),…,qₘ₋₁(zₖ))ᵀ yazalım. R21'de

\[
 G=2\sum_k\frac{Q_kQ_k^\top}{\gamma_k},\qquad
 B_j=\frac13\sum_k\sigma_k\left[
 q_j(z_k)\frac{t_k}{r_k}-q_j'(z_k)\right],\quad v=G^{-1}B,
 \quad \kappa_k=\frac{Q_k^\top v-t_k/6}{r_k}. \tag{F2}
\]

G pozitif tanımlıdır. Gerçek optimumun birim profili sₐ için
b(a)=b*+va²+o(a²), cₖ(a)=zₖ+κₖa²+o(a²),
S(a)=∫qₘsₐ=∫q*sₐ, A(a)=f/S(a), M(a)=A(a)/a'dır.
Son eşitlik, alt momentlerin **tam** sıfır olmasına dayanır.

## 2. Teorem ve yeterli düzenlilik

**(i) Mevcut C² varsayımlar altında bile**

\[
 \delta(M)=\delta_0+\frac{C_2}{M^2}+o(M^{-3}),
 \qquad C_2=\frac{\delta_0^3\Gamma}{3D}. \tag{F3}
\]

Dolayısıyla M⁻³ ölçekli artık sıfıra gider. Bu sonuç, yalnız a'da
çiftlikten çıkarılmaz; aşağıdaki hücre integralinde q*(zₖ)=0 olması ve
simetrik ortalama kullanılır. R21'deki çiftlik uyarısı bu nedenle
yanlış değildi; burada ek bir yapısal gerekçe sağlanır.

**(ii) Ek olarak q* her zₖ'nin bir komşuluğunda C³ ise**
uₖ=q*‴(zₖ) tanımlanır ve şu katsayılar vardır:

\[
 \mathcal R=\sum_k\left[\frac{t_k^2}{36\gamma_k}
                              -\frac{\sigma_ku_k}{60}\right],
 \qquad \mathcal P=\frac12B^\top G^{-1}B\ge0,
 \qquad \Xi=\mathcal R-\mathcal P. \tag{F4}
\]

\[
 S(a)=D-\frac\Gamma3a^2+\Xi a^4+o(a^4). \tag{F5}
\]

\[
 \boxed{\delta(M)=\delta_0+\frac{C_2}{M^2}
                         +\frac{C_4}{M^4}+o(M^{-4}),\qquad
 C_4=\delta_0^5\left[\frac{\Gamma^2}{3D^2}
                         -\frac{\mathcal R}{D}
                         +\frac{\mathcal P}{D}\right].} \tag{F6}
\]

Tüm qⱼ'lerin C³ olması yeterli bir özel durumdur. Daha zayıf biçimde,
yalnız sabit optimum residual q*'ın sıfırlar yakınında ek türevi gerekir;
R21'in C² moment dalları yeterlidir. C⁴ dal veya dördüncü türev
varsayılmamıştır. Bunun gerekli en zayıf koşul olduğu iddia edilmiyor.

## 3. Hücre açılımı: neden yalnız ikinci mertebe merkez hareketi yeterli?

H(x)=∫ₓᴿq*(t)dt, dₖ=2σₖ ve Δₖ=cₖ(a)−zₖ olsun.
R21'in eşik ortalaması formülü tam olarak

\[
 S(a)-D=\sum_k d_k\left[
 \frac12\int_{-1}^1H(z_k+\Delta_k+ay)\,dy-H(z_k)\right]. \tag{F7}
\]

verir. Sadece sonlu sayıdaki geçiş komşulukları değişir.
H′(zₖ)=−q*(zₖ)=0 olduğundan Δₖ'nın doğrusal katkısı yoktur.
E, y∈[−1,1] üzerindeki uniform ortalamayı göstersin. Tam kimlikler:

\[
 E(\Delta+ay)^2=\Delta^2+a^2/3,\quad
 E(\Delta+ay)^3=\Delta^3+\Delta a^2,\quad
 E(\Delta+ay)^4=\Delta^4+2\Delta^2a^2+a^4/5. \tag{F8}
\]

C² q* altında H C³'tür. Taylor–Peano açılımı
H(z+h)=H(z)−r h²/2−t h³/6+o(|h|³) verir.
Δ=O(a²) olduğundan üçüncü kuvvetin ortalaması O(a⁴), ikinci kuvvetin
Δ² parçası da O(a⁴)'tür. Sonlu komşuluklarda kalanların toplamı o(a³).
Böylece S=D−Γa²/3+o(a³), bu da (F3)'ün a-ölçekli karşılığıdır.

Ek C³ q* altında H C⁴'tür ve açılıma −u h⁴/24+o(|h|⁴) eklenir.
Δ=κa²+o(a²) ve (F8) kullanılarak

\[
 S(a)-D=-\frac\Gamma3a^2
 -a^4\sum_k\sigma_k\left[
 r_k\kappa_k^2+\frac{t_k\kappa_k}{3}+\frac{u_k}{60}\right]
 +o(a^4). \tag{F9}
\]

Kalanın gerekçesi: her hücrede |Δ+ay|≤C a; Taylor kalanının uniform
modülü a→0'da sıfıra gider. Sonlu k toplamı o(a⁴)'ü korur. Δ'nın
o(a²) hatası, Δ² içinde o(a⁴), a²Δ içinde o(a⁴) üretir. Dolayısıyla
merkezlerin a⁴ katsayılarına veya b(a)'nın a⁴ katsayısına ihtiyaç yoktur.

## 4. Katsayının ayrışması ve moment düzeltmesinin anlamı

wₖ=Qₖᵀv yazalım; bu wₖ, integral ailesinin pozitif ağırlığı w değildir.
κₖ=(wₖ−tₖ/6)/rₖ sayesinde her hücrede

\[
 -\sigma_k\left[r_k\kappa_k^2+\frac{t_k\kappa_k}{3}
                                +\frac{u_k}{60}\right]
 =\frac{t_k^2}{36\gamma_k}-\frac{\sigma_ku_k}{60}
                                -\frac{w_k^2}{\gamma_k}. \tag{F10}
\]

Son terimlerin toplamı

\[
 \sum_k\frac{(Q_k^\top v)^2}{\gamma_k}
 =\frac12v^\top Gv=\frac12B^\top G^{-1}B=\mathcal P \tag{F11}
\]

olduğu için (F5) elde edilir. P≥0 ve P=0 ancak B=0 olduğunda.

Yorumun karşılaştırma nesnesi açık tutulmalıdır. Sabit residual q* için
**alt momentler uygulanmadan** birim destek değerini tanımlayalım:

\[
 H_*(a)=\sup_{|s|\le1,\ \operatorname{Lip}s\le1/a}\int_Iq_*s.
 \tag{F12}
\]

R21'in hücre optimalitesiyle serbest merkez katsayısı −tₖ/(6rₖ)'dır.
Aynı açılım H*=D−Γa²/3+R a⁴+o(a⁴) verir. Böylece

\[
 H_*(a)-S(a)=\mathcal P a^4+o(a^4). \tag{F13}
\]

Bu fark, aynı a'da residual destek problemiyle tam momentli tasarımın
farkıdır. Alt momentleri kaldırılmış orijinal qₘ-hedef probleminin
değeri olduğu iddia edilmez. qₘ ile q* yalnız momentli sınıfta aynı
hedefi verir. Bu ayrım katsayının yorumunda gereklidir.

Genlik katsayısında moment düzeltmesinin payı +δ₀⁵P/D'dir. Bu pay
negatif olamaz; **toplam C₄'ün işareti sabit değildir.** R terimi ve
normalizasyon katkısı da vardır. Alt moment bazının tersinir L matrisiyle
değiştirilmesi G→LGLᵀ, B→LB verir; P aynı kalır. Dolayısıyla bu pay
moment denklemlerinin baz seçiminin yapay bir sonucu değildir.

## 5. a ile M⁻¹ arasındaki dönüşüm

t=Γ/(3D), e=Xi/D yazalım. (F5)'ten

\[
 A(a)=\delta_0[1+t a^2+(t^2-e)a^4]+o(a^4),\qquad a=A/M. \tag{F14}
\]

ε=M⁻¹ olsun. R21'in monoton dalı ε→0 için tek a(ε) verir.
a=δ₀ε+O(ε³). İkinci mertebe sonucu A=δ₀+C₂ε²+o(ε²) kullanılırsa
a²=δ₀²ε²+2δ₀C₂ε⁴+o(ε⁴), a⁴=δ₀⁴ε⁴+o(ε⁴).
Bu ifadelerin (F14)'e konması

\[
 C_2=\delta_0^3t,\qquad
 C_4=2\delta_0^2t C_2+\delta_0^5(t^2-e)
     =\delta_0^5(3t^2-e) \tag{F15}
\]

verir. 3t² içindeki 2t², a=A/M bağımlılığından gelir. a'yı yalnız
δ₀/M ile değiştirip dördüncü mertebeye devam etmek bu katkıyı kaybeder.
Benzer biçimde C² durumda S=D−Γa²/3+o(a³) dönüşümü (F3)'ü verir;
dönüşümün ilk ek etkisi O(M⁻⁴) olduğundan M⁻³ terimi oluşmaz.

## 6. C² düzenlilik neden genel bir M⁻⁴ yasasına yetmez?

[-1,1]'de q₀=1 ve

\[
 q_*(x)=q_1(x)=x+\operatorname{sgn}(x)|x|^{5/2},\quad
 b^*=0,\quad D=11/7,\quad f=11/28,\quad\delta_0=1/4. \tag{F16}
\]

Bu fonksiyon C²'dir: ikinci türevi (15/4)sgn(x)|x|¹ᐟ², sıfırda
sıfıra gider. Üçüncü türevi sıfır çevresinde sınırsızdır; C³ değildir.
Tek basit sıfır 0, r=1, G=2; q* tek, q₀ çift olduğundan merkez 0,
b=0 profili bütün alt moment/dengeleri tam sağlar. R21'in doğrudan
destek eşitsizliğiyle sₐ=clip(x/a,−1,1) gerçek optimum birim profildir.

Doğrudan integral

\[
 S(a)=\frac{11}{7}-\frac{a^2}{3}-\frac{8}{63}a^{7/2}. \tag{F17}
\]

verir. 0<a≤1/5 için S>0 ve S+aS′>0; böylece A=f/S, M=A/a
gerçek minimumu parametrik verir. Açılım:

\[
 \delta(M)=\frac14+\frac{7}{2112M^2}
               +\frac{1}{6336M^{7/2}}+O(M^{-4}). \tag{F18}
\]

Dolayısıyla M³ ölçekli artık sıfıra gider, fakat M⁴ ölçekli artık
√M/6336+O(1) ile sınırsız büyür. Sonlu bir C₄ yoktur. Bu, C²
koşulunu C³ düzeyindeki sonuç için yeterli saymanın açık karşıörneğidir.
Kuvvet hesabı genel olarak 2a^(p+1)/((p+1)(p+2)) integral kaybına dayanır;
p=5/2 için katsayı 8/63'tür.

## 7. Kapsam

- (F6) sonlu geçişlerde, sabit bir problem için M→∞ açılımıdır. Bütün
  M'lerde sayısal bir hata sınırı vermez. Genel o(M⁻⁴) için açık bir
  modül veya keskin M⁻⁶ katsayısı bu pakette türetilmedi.
- İki düzgün örnekte C₄ pozitif ve negatif çıkıyor; bu işaretler genel
  sonuca yüklenmez. Örneklerin analitik formülleri O(M⁻⁶) kalan verir,
  ancak genel teoremin daha zayıf kalanını değiştirmez.
- Theta'nın sonsuz sıfırlarında gerekli uniform Taylor kontrolü ve
  türev toplamlarının yakınsaklığı bu tur doğrulanmadı. R16'nın mevcut
  açık hata sınırı korunur; theta için M⁻³ yokluğu veya C₄ ilan edilmez.
- Cusp boyunca uniformluk, yeni fiziksel yasa veya AI uygulaması
  çıkarılmadı. Yeni katsayının literatürdeki önceliği açık kalır.

[Örnekler ve kontroller](EXAMPLES.md), [iddia/kapsam incelemesi](REVIEW.md).
