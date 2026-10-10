# R21 — Sonlu geçişlerde sonlu eğim optimumunun belirlenmesi

21 Eylül 2026. Analitik araştırma notu. R20'deki tek-geçiş dengesini
sonlu sayıda geçiş ve tam moment kısıtlarıyla birleştirir. Aşağıdaki
ispat kendi içinde verilmiştir; formal ispat veya dış hakem onayı değildir.
Literatür önceliği iddia edilmiyor. Theta ailesinin sonsuz kuyruğuna bu
teorem henüz uygulanmış değildir.

## 1. Problem ve açık varsayımlar

I=[L,R], L<R, m≥1 ve q₀,…,qₘ∈C²(I) gerçek olsun. f>0 için

\[
 \delta(M)=\inf\{\|g\|_\infty:g\in W^{1,\infty}(I),\quad
 \|g'\|_\infty\le M,\quad
 \int_Iq_jg=0\ (0\le j<m),\quad\int_Iq_mg=f\}. \tag{T1}
\]

W¹,∞ fonksiyonları sürekli Lipschitz temsilcileriyle kullanılır.
Eski notasyonla g=−h. Uç değerler ayrıca sabitlenmemiştir. Burada qⱼ
yoğunluklardır: pozitif integral ailesinde qⱼ=wpⱼ yazılabilir.

Bir b*∈Rᵐ için

\[
 q_*=q_m-\sum_{j<m}b_j^*q_j \tag{T2}
\]

şu koşulları sağlasın:

1. Tam olarak N≥1 tane iç sıfırı vardır: L<z₁<…<z_N<R. Hepsi basittir;
   q* başka yerde, uçlar dahil, sıfır değildir.
2. İşaret profili alt momentleri korur:
   ∫qⱼ sgn(q*)=0, j<m.
3. m×N matrisi (qⱼ(zₖ)) tam satır rankına sahiptir. Özellikle N≥m.

Tanımlar:

\[
 D=\int_I|q_*|>0,\qquad \delta_0=f/D,\qquad
 \sigma_k=\operatorname{sgn}q_*'(z_k),\quad d_k=2\sigma_k,
 \qquad \Gamma=\sum_k|q_*'(z_k)|. \tag{T3}
\]

\[
 G_{j\ell}=2\sum_{k=1}^N
       \frac{q_j(z_k)q_\ell(z_k)}{|q_*'(z_k)|}. \tag{T4}
\]

Rank koşulu G'nin pozitif tanımlı olmasıyla eşdeğerdir:
vᵀGv=2Σₖ(Σⱼvⱼqⱼ(zₖ))²/|q*′(zₖ)|. Ayrıca δ₀ eğim sınırlaması
olmadan gerçek optimumdur. Her uygun g için f=∫q*g≤D‖g‖∞;
δ₀ sgn(q*) bütün momentleri sağlar ve bu alt sınırı gerçekleştirir.

## 2. Teorem: küçük geçiş genişliğinde gerçek global optimum

Yukarıdaki varsayımlar altında bir a₀>0 vardır. Her 0<a<a₀ için b(a)
ve c₁(a),…,c_N(a) aşağıdaki sistemi çözer:

\[
 \frac12\int_{-1}^1q_{b(a)}(c_k(a)+av)\,dv=0\quad(1\le k\le N),
 \quad q_b=q_m-\sum_{j<m}b_jq_j, \tag{T5}
\]

\[
 \int_Iq_j(x)s_a(x)\,dx=0\quad(j<m). \tag{T6}
\]

Burada sₐ, [cₖ−a,cₖ+a] dışında sgn(q_b), bu aralıkta ise
σₖ(x−cₖ)/a'dır. Geçiş aralıkları birbirinden ve uçlardan ayrıdır.
Her biri q_b'nin tam bir basit sıfırını içerir. b ve c fonksiyonları
a=0 çevresine çift C² fonksiyonlar olarak uzanır;
b(0)=b*, cₖ(0)=zₖ. Çözüm bu taban nokta yakınında tektir.

\[
 S(a)=\int_Iq_ms_a>0,\qquad
 A(a)=f/S(a),\qquad M(a)=A(a)/a. \tag{T7}
\]

a₀ gerekirse küçültüldüğünde M(a) kesin azalan ve M(a)→∞'dir.
Böylece bütün yeterince büyük M için tek bir a=a(M) elde edilir ve

\[
 \boxed{\delta(M)=A(a(M)),\qquad g_M=A(a(M))s_{a(M)}.} \tag{T8}
\]

g_M yalnız bu parametrizasyon içinde değil, (T1)'deki **bütün** uygun
Lipschitz fonksiyonlar arasında tek optimumdur. Her M için b(a(M)),
sabit A=A(a(M)), M destek probleminin global dual minimizatörlerinden
biridir. Bu not global dual tekliği iddia etmez; IFT yerel tekliği verir.

### 2.1. Sıfırların ve dengeli merkezlerin devamı

Basit sıfır teoremiyle b* yakınında q_b'nin zₖ(b) kökleri C² devam eder.
I kompakt olduğu, sıfırlardan uzakta |q*| pozitif bir alt sınıra sahip
olduğu ve kök komşuluklarında q*′ sıfırdan uzak olduğu için başka sıfır
doğmaz. Bu adım sonsuz aralığa otomatik geçmez.

\[
 E_k(b,c,a)=\tfrac12\int_{-1}^1q_b(c+av)\,dv
\]

C²'dir; Eₖ(b,zₖ(b),0)=0 ve ∂cEₖ=q_b′(zₖ(b))≠0. IFT tek C² merkez
cₖ(b,a) verir. Eₖ a'da çift olduğundan yerel tekliğe göre merkez de
çifttir. Sonuçta cₖ(b,a)=zₖ(b)+O(a²) ve a>0 küçükken kök rampanın
içindedir. Yön σₖ değişmez. Taylor açılımı, sabit b için,

\[
 c_k(b,a)=z_k(b)-\frac{q_b''(z_k(b))}{6q_b'(z_k(b))}a^2+o(a^2)
 \tag{T9}
\]

verir. Her sıfır için ayrı komşuluk seçip sonlu sayıda yarıçapın
minimumunu almak bütün geçişleri aynı a aralığında kontrol eder.

### 2.2. Moment haritasının a=0'daki düzenliliği

Rⱼ(t)=∫ₜᴿqⱼ(x)dx ve s_L=sgn(q*(L)) yazalım. Rampalı profilin
momentleri şu **düzgün integral formülü** ile verilir:

\[
 J_j(c,a)=s_L\int_Iq_j+
       \sum_k\frac{d_k}{2}\int_{-1}^1R_j(c_k+av)\,dv. \tag{T10}
\]

Neden: rampalı Heaviside geçişi, eşiği cₖ+av olan keskin geçişlerin
v∈[−1,1] üzerindeki ortalamasıdır. Fubini (T10)'u verir. Bu formül
a=0'a ve negatif a'ya çift olarak uzanır; negatif a için fiziksel
rampa tanımlamak gerekmez. C² qⱼ altında Rⱼ C³, c(b,a) C² olduğundan
Ψⱼ(b,a)=Jⱼ(c(b,a),a) bir C² haritasıdır.

Kök denkleminin b türevi
∂bℓzₖ=qℓ(zₖ)/q*′(zₖ)'dır. Dolayısıyla

\[
 \partial_{b_\ell}\Psi_j(b^*,0)
 =-\sum_kd_kq_j(z_k)\frac{q_\ell(z_k)}{q_*'(z_k)}
 =-G_{j\ell}. \tag{T11}
\]

G tersinir ve Ψ(b*,0)=0 olduğundan IFT, Ψ(b(a),a)=0 çözen tek yerel
C² dalı verir. a→−a simetrisi ve teklik bu dalın çift olmasını sağlar.
Bu yüzden b(a)−b*=O(a²), cₖ(a)−zₖ=O(a²). Burada yalnız merkezleri
kaydırıp eski b*'yi sabit tutmak için bir gerekçe yoktur.

### 2.3. Parçalı integrasyonla global destek optimalitesi

b=b(a), A>0, M=A/a sabit olsun; g*=Asₐ. Her uygun v için |v|≤A,
|v′|≤M. Rampalar dışında q_b(v−g*)≤0 noktasal olarak geçerlidir.
Bir k rampasında

\[
 Q_k(x)=\int_{c_k-a}^xq_b(t)\,dt
\]

iki uçta sıfırdır. Rampa içinde tek işaret değişimi bulunduğundan
σₖQₖ(x)<0 bütün iç noktalarda geçerlidir. Bu, artan geçişte Q<0,
azalan geçişte Q>0 anlamına gelir. Sınır terimleri kaybolduğu için

\[
 \int_{c_k-a}^{c_k+a}q_b(v-g^*)
 =-\int_{c_k-a}^{c_k+a}Q_k(x)(v'(x)-\sigma_kM)\,dx\le0. \tag{T12}
\]

İşaret kontrolü: σ=+1 ise Q<0 ve v′−M≤0; σ=−1 ise Q>0 ve v′+M≥0.
İki durumda da eksi integral ≤0. Hücreleri ve dış aralıkları toplamak,

\[
 \mathcal H(A,M;q_b):=
 \sup_{|v|\le A,\,\operatorname{Lip}v\le M}\int_Iq_bv
 =\int_Iq_bg^* \tag{T13}
\]

verir. Her dış aralıkta q_b≠0 olduğundan eşitlik ancak v=g* ile olur.
Rampalarda Q'nun içte kesin işareti v′=σₖM a.e. gerektirir. Uç değerler
ve süreklilik rampayı da sabitler. Böylece destek maksimizatörü tektir.
Bu bir ızgara, yerel ikinci-türev testi veya varsayılan KKT yeterliliği
değil, bütün uygun v'lere uygulanan doğrudan bir eşitsizliktir.

### 2.4. Moment desteğinden minimum genliğe geçiş

S(0)=∫qₘ sgn(q*)=D olduğundan S(a)>0 küçük a için. (T7)'deki A ile
g*=Asₐ alt momentleri ve hedefi tam sağlar. Alt momentlerin sıfırlığı
nedeniyle ∫q_bg*=∫qₘg*=f. Aynı M ve genliği en fazla A olan herhangi
bir momentli çözüm v için yine ∫q_bv=f. (T13)'te eşitliğin tekliği
v=g* gerektirir. Dolayısıyla daha küçük genlikli çözüm olamaz; genliği
A olan başka çözüm de olamaz. Bu, (T8)'in global ve tek olmasını ispatlar.

Her başka dual katsayı \tilde b için
ℋ(A,M;q_{\tilde b})≥∫q_{\tilde b}g*=f; oysa ℋ(A,M;q_b)=f.
Bu nedenle bulunan b global bir dual minimizatördür. Bu argüman ek bir
minimax değiş tokuşuna veya dual optimumun peşinen varlığına ihtiyaç duymaz.

A(a) çift C², A(0)=δ₀>0, A′(a)=O(a) olduğundan
M′(a)=(aA′(a)−A(a))/a²<0 yeterince küçük a için. M→∞ ve süreklilik
(T8)'i bütün yeterince büyük M'lere taşır. Kapsam yalnız bir dizi M değildir.

## 3. Dual katsayı ve merkezlerin ilk hareketi

\[
 B_j=\frac13\sum_k\sigma_k\left[
   q_j(z_k)\frac{q_*''(z_k)}{q_*'(z_k)}-q_j'(z_k)\right],
 \qquad v=G^{-1}B. \tag{T14}
\]

O zaman

\[
 b(a)=b^*+va^2+o(a^2),\qquad
 c_k(a)=z_k+\kappa_ka^2+o(a^2),\quad
 \kappa_k=\frac{\sum_{j<m}v_jq_j(z_k)-q_*''(z_k)/6}{q_*'(z_k)}.
 \tag{T15}
\]

Kontrol: (T10)'da cₖ=zₖ+κₖa²+o(a²) koymak

\[
 J_j(c,a)-J_j(z,0)=
 -a^2\sum_kd_kq_j(z_k)\kappa_k
 -\frac{a^2}{6}\sum_kd_kq_j'(z_k)+o(a^2) \tag{T16}
\]

verir. (T9) ile bu katsayı −Gv+B olur. Alt momentleri sıfır yapan
eşitlik Gv=B'dir. q* yerine her sabit qⱼ için (T16) geçerlidir.

Hedef için S(a)=∫q*sₐ, çünkü alt momentler sıfırdır. q*(zₖ)=0 olması
merkez hareketinin (T16)'daki ilk toplamını yok eder. Sonuç:

\[
 S(a)=D-\frac{\Gamma}{3}a^2+o(a^2),\qquad
 \delta(M)=\delta_0+
  \frac{\delta_0^3\Gamma}{3D}\frac1{M^2}+o(M^{-2}). \tag{T17}
\]

Son dönüşümde a=A(a)/M=δ₀/M+O(M⁻³) kullanılır. Bu baş katsayı R15'in
sonlu-geçişli özel haliyle aynıdır. R21'in eklediği şey baş katsayı değil,
**gerçek sonlu-M optimumun** denklem sistemi, global optimalitesi,
tekliği ve b/c hareketidir. M cinsinden (T15)'in katsayıları δ₀² ile
çarpılır. a ile M⁻¹ aynı sayı değildir.

## 4. Kapsam sınırları ve açık kalan iş

- Kompakt I, sonlu N, basit iç sıfırlar, serbest uç değerler ve tam rank
  bu teoremin varsayımlarıdır. Küçük M'de rampalar birleşebilir veya sınıra
  değebilir; o rejimde bu parametrizasyonun geçerli olduğu iddia edilmez.
- Noktasal pozitif çekirdek w(1+h)>0 ayrıca istenirse A<1 yeterlidir.
  Teorem genel f için A<1 vaat etmez; doğrulama örneğinde bu sınır sağlanır.
- Optimum Lipschitz'tir ve rampaların uçlarında köşeleri vardır.
  Düzgün geometrik çekirdek sınıfında bunun aynen elde edildiği söylenmez.
  R15/R19'daki düzgün yaklaşım ve nondegeneracy argümanları ayrı kalır.
- C² ve a'da çiftlik, tek başına M⁻³ katsayısının yokluğunu veya M⁻⁴
  açılımını ispatlamaz: örneğin |a|³ çift ve C²'dir. Daha yüksek
  düzenlilikle dördüncü mertebe hesabı sıradaki sorudur.
- Theta artık yoğunluğunun sonsuz geçişleri için uniform merkez varlığı,
  moment toplamlarının türevlenmesi, kuyruk denetimi ve dual devamlılık
  yeniden kurulmalıdır. Sonlu kesme theta için tam optimum ispatı olmaz.
- Bu sonuç cusp eğrisi boyunca uniform bir teorem, yeni bir fiziksel yasa,
  LLM uygulaması, yayın kabulü veya bağımsız bir özgünlük ispatı değildir.

Yardımcı destek fonksiyoneli R18'de bilinen KR/flat normuyla eşlenmiştir.
Parçalı integrasyon ve IFT klasik araçlardır. Yeni araştırma katkısının
ne kadarının literatürdeki sonuçların özel hali olduğu ayrıca incelenmelidir.
[Kapsam ve kaynak notu](REVIEW.md), [iki-geçişli örnek](EXAMPLE.md).
