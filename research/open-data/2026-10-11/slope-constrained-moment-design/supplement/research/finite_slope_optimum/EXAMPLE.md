# R21 — İki geçişli, tam çözülen doğrulama örneği

21 Eylül 2026. Bu örnek theta çekirdeği değildir. Kompakt aralıktaki
teoremin hem azalan hem artan geçişini, moment bağını ve dual katsayı
hareketini aynı anda sınamak için seçildi. Rastgele bir nümerik uyum yerine
doğrudan integrallenebilen polinomlar kullanılır.

## 1. Aile ve başlangıç optimumu

\[
 I=[-1,1],\quad q_0(x)=1,\quad
 q_1(x)=(x^2-\tfrac14)(1+\beta x),\quad
 \beta=\tfrac14,\quad f=\tfrac18. \tag{E1}
\]

∫g=0 ve ∫q₁g=f istenir. b*=0; artık yoğunluk q*=q₁'dir.
Sıfırlar z₋=−1/2, z₊=1/2; işaret dışta +, içte − olduğundan
∫sgn(q*)=0. Doğrudan integrasyon ve türevle

\[
 D=\tfrac12,\quad\delta_0=\tfrac14,\quad
 q_*'(z_-)=-\tfrac78,\quad q_*'(z_+)=\tfrac98,
 \quad\Gamma=2,\quad G=\tfrac{256}{63}>0. \tag{E2}
\]

## 2. İki merkezin tek bir kaymayla bağlanması

İlk rampa +1'den −1'e, ikinci −1'den +1'e geçer. İkisi de yarı genişlik a
taşısın. Beş parçalı doğrudan integral ∫s=2+2c₋−2c₊ verir.
Bu nedenle moment koşulu tam olarak c₊−c₋=1'dir. Yazalım:

\[
 c_-=d-\tfrac12,\qquad c_+=d+\tfrac12. \tag{E3}
\]

Ortak dual katsayı b için her rampa aralığında q₁−b integrali sıfırdır.
İki hücre ortalamasının farkını ve ortalamasını almak sırasıyla

\[
 2d+3\beta d^2+\beta a^2=0, \qquad
 b=d^2+\beta d^3+\frac{\beta d}{2}
                   +\frac{a^2}{3}+\beta da^2 \tag{E4}
\]

verir. Küçük kök

\[
 d(a)=\frac{-1+\sqrt{1-3\beta^2a^2}}{3\beta}
     =-\frac{\beta a^2}{1+\sqrt{1-3\beta^2a^2}}. \tag{E5}
\]

İkinci biçim çizimlerde çıkarma kaybını azaltır. Sertifika üreticisi
karekökün kayan noktalı değerini kullanmaz; (E4)'ün kökünü tam rasyonel
aralıkta 210 ikili bölmeyle çevreler.

Beş parçalı integralin hedefi

\[
 T(a)=\int_{-1}^1q_1s_a
 =\tfrac12-2d^2-2\beta d^3-\tfrac23a^2-2\beta da^2. \tag{E6}
\]

Sonlu eğim optimumu parametrik olarak

\[
 \boxed{A(a)=\frac{1}{8T(a)},\quad M(a)=\frac{A(a)}a,
 \quad \delta(M(a))=A(a),\quad g_{M(a)}=A(a)s_a.} \tag{E7}
\]

Bu eşitliğin global optimalite gerekçesi yalnız denklemleri çözmüş olmak
değildir; [genel teoremin](PROOF.md) destek eşitsizliğidir. Aşağıdaki
uniform kontroller onu bütün 0<a≤1/5 aralığında geçerli kılar.

## 3. Yalnız altı örnek değil, bütün bir bütçe aralığı

0<a≤1/5 için (E4)'ün küçük kökü −1/100<d<0'dır: denklemin sol tarafı
−1/100'de negatiftir, sıfırda pozitiftir ve arada türevi pozitiftir.
Bu tek kök dalı süreklidir. Rampalar

- sol tarafta [−0.71,−0.30] içinde;
- sağ tarafta [0.29,0.70] içinde

kalır. Aralarında en az 3/5 boşluk vardır; sınıra değmezler.
q₁′ sol bölge boyunca negatif, sağ bölge boyunca pozitiftir.
q₁″=2+6βx≥1/2>0 olduğundan q₁−b en fazla iki sıfır taşıyabilir.
Her rampanın sıfır ortalaması ve sıkı monotonluğu o rampada tam bir
basit sıfır bulunduğunu gösterir. Dolayısıyla bütün aralıktaki işaret
yapısı gerçekten +,−,+ olup başka bir geçiş gizlenmez.

d<0 olduğundan (E6)'nın kübik ve son terimi pozitiftir. Böylece

\[
 T\ge\tfrac12-\tfrac{2}{10000}-\tfrac{2}{75}
    >\tfrac{47}{100}>0,\qquad A<\tfrac{25}{94}<1. \tag{E8}
\]

Bu A<1, örnekte w=1 ve h=−g alınırsa 1+h>0 olmasını da sağlar;
başlı başına yeni bir cusp veya fiziksel model kurulduğu anlamına gelmez.

∂T/∂d=−2(2d+3βd²+βa²)=0 dal üzerinde. Bu yüzden
T′(a)=−4a/3−4βda ve

\[
 T+aT'=\tfrac12-2d^2-2\beta d^3-2a^2-6\beta da^2
 \ge\tfrac12-\tfrac{2}{10000}-\tfrac{2}{25}>0. \tag{E9}
\]

M=f/(aT) kesin azalır ve a↓0 iken ∞'ye gider. Böylece (E7),
**her M≥M(1/5)** için tam parametrik optimumdur. Buradaki kesin eşik
M(1/5)'tir; aşağıdaki ondalıklar yuvarlatılmış gösterimdir:

\[
 M(1/5)\simeq1.32028289388310536,\qquad
 \delta(M(1/5))\simeq0.264056578776621072. \tag{E10}
\]

## 4. Neden eski merkezlerden ayrılmak gerekiyor?

c±=±1/2 seçimi de alt momenti korur. Aynı a, A, M=A/a için bu sabit
merkezli profilin birim hedef değeri T₀=1/2−2a²/3'tür. (E4) ile

\[
 \boxed{T(a)-T_0(a)=2d(a)^2(1+2\beta d(a))>0.} \tag{E11}
\]

Yani yeni profil, aynı genlik ve eğim bütçesinde, aynı alt momenti
koruyarak daha yüksek hedef momenti verir. Bu fark birim profil için
yazılmıştır; gerçek g için kazanç A ile çarpılır. Farkı farklı M'lerdeki
iki genliğin farkı gibi yorumlamıyoruz.

a=1/5'te d≈−0.005009410321914991; dolayısıyla iki merkez
−0.505009410321915 ve 0.494990589678085 olur. Aynı sırada
b≈0.01268212570487230'dur. Merkezlerin ikisi de sola gider;
dual katsayı sıfırda kalmaz. Yeni q_b sıfırlarıyla rampa merkezleri de
genelde aynı değildir: denge tek bir noktadaki q_b(c)=0 koşulu değildir.

Genel hareket formüllerinin burada verdiği tam katsayılar:

\[
 d(a)=-\tfrac18a^2+O(a^4),\qquad
 b(a)=\tfrac{61}{192}a^2+O(a^4),\qquad
 M^2(\delta(M)-\tfrac14)\longrightarrow\tfrac1{48}. \tag{E12}
\]

Bu örnekte (E5) analitik olduğundan gösterilen O(a⁴) geçerlidir.
Genel C² teoremindeki o(a²) ifadesi bu örnekten dolayı güçlendirilmez.

## 5. Doğrulama katmanları

1. Genel ispat: bütün uygun Lipschitz profillere uygulanan integral
   eşitsizliği; varlık için IFT, global optimum için destek eşitliği.
2. Tam cebir: üç değişkenli Laurent polinomlarıyla beş parçalı momentler,
   iki hücre dengesi, pozitif kazanç ve durağanlık kimlikleri doğrulandı.
   Sayısal örnek değerleri kullanmadan genel β,d,a kimlikleri sınandı.
3. Tam rasyonel aralıklar: altı a değeri için benzersiz kök çevrelendi;
   b, merkezler, T, A, M ve kazanç dışa kapsayan kesir aralıklarıyla verildi.
   Uniform işaret/ayrıklık sınırları ayrıca tam kesirlerle kontrol edildi.
4. Ayrı sayısal çözüm: indirgenmiş d/b formüllerini kullanmadan iki denge
   integrali ve alt moment eşitliği üç bilinmeyende çözüldü. mpmath
   80 ve 120 basamakta hesaplandı. Altı genişlikte yedi niceliğin tümü
   rasyonel aralıkların içinde; hassasiyetler arası fark <10⁻⁷⁰.

Son madde rigoröz aralık ispatının yerine geçmez. İlkel fonksiyonun 38
iç noktadaki işaret örneklemesi yalnız tanıdır; her noktada gerekli işaret
analitik olarak tek sıfır ve denge koşulundan ispatlanmıştır.

[Hesap tablosu](results/NUMERICAL_TABLE.md),
[rasyonel sertifika](results/certificate.json),
[tam cebir denetimi](results/algebra.json),
[ayrı sayısal çözüm](results/quadrature.json),
[grafik](figures/finite_optimum.png).
