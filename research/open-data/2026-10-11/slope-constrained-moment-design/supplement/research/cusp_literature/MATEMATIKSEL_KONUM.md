# R06 — Genel kuram ile aileye özgü sonuç arasındaki sınır

20 Eylül 2026. Bu not R01–R05'i değiştirmez. Aşağıdaki kısa türetimler
katkının kapsamını belirlemek içindir; bunlar için literatür önceliği
iddia edilmiyor. Yeni bir integral sertifikası üretilmedi.

## 1. Özel ailenin doğal yapısı

\[
F(t;\lambda,\mu,\nu)=\int_0^\infty\Phi(u)
e^{\lambda u^2+\mu u^4+\nu u^6}\cos(2tu)\,du.
\]

R01'deki çift üstel kuyruk sınırı, kompleks değişkenlerin kompakt
kümelerinde de polinom üssüne ve tüm sabit dereceli türevlere baskındır.
Böylece integral ortaklaşa entire'dır ve integral altında türev alınabilir.
\(D_n=\partial_t^nF\) için

\[
F_\lambda=-D_2/4,\qquad F_\mu=D_4/16,\qquad F_\nu=-D_6/64.
\tag{1}
\]

Bu özdeşlikler Jacobi çekirdeğine özgü değildir: aynı integrallenebilirlik
şartlarına sahip başka çekirdeklerde de geçerlidir. Katsayıları, seçtiğimiz
\(\cos(2tu)\) normalizasyonu belirler.

Klasik aileyle tam ilişki \(F(t;\lambda,0,0)=H_\lambda(2t)\) ve
\(F(t;0,0,0)=\xi(1/2+it)/8\)'dir. Normalizasyon,
[Rodgers–Tao'nun girişindeki (1)–(4)](https://arxiv.org/pdf/1801.05914)
ile karşılaştırıldı. Dolayısıyla araştırılan integral, bilinen özel
fonksiyonun somut bir çok parametreli uzantısıdır.

Sabit gerçek \(\mu,\nu\) için
\(d\rho_{\mu,\nu}(u)=\Phi(|u|)e^{\mu u^4+\nu u^6}du\)
sonlu, pozitif, simetrik bir ölçüdür. Onun \(\lambda\)-deforme Fourier
dönüşümü \(2F(z/2;\lambda,\mu,\nu)\)'dir. Bu eşitlik,
Newman–Wu'nun genel ölçü çerçevesine doğrudan yerleştirmedir; her böyle
ölçü için sonlu bir Newman eşiği bulunduğunu ileri sürmez.

## 2. Cusp'ın bilinen geometrisi

Normalize edilmiş kübik \(x^3+ax+b=0\)'ın foldları için
\(a=-3x^2, b=2x^3\). Dolayısıyla
\(27b^2+4a^3=0\); iki kol, bir/üç gerçek kök ayrımı ve \(3/2\)
açılma üssü zaten bu normal formda vardır. Normal formun koordinat
dönüşümü, bizim özgün \((\lambda,\mu)\) penceremizi kendiliğinden
hesaplamaz. \(A_3\) adı potansiyel \(V_t=F\) için kullanılabilir;
\(F\)'nin üçlü sıfırı ile potansiyelin tekillik indisi karıştırılmamalıdır.

(1), \(D_0=D_1=D_2=0\), \(D_3>0>D_4\) altında, cusp merkezli
\(s=t-t_*,\ell=\lambda-\lambda_*,m=\mu-\mu_*\) fold açılımı

\[
\ell=2s^2+O(s^3),\qquad m=\frac{16D_3}{3D_4}s^3+O(s^4),
\qquad C=-\frac{8\sqrt2}{3}\frac{D_3}{D_4}
\tag{2}
\]

olur. Bunlar yapısal türetimlerdir. R03–R05'in ek bilgisi, ilgili
cusp grafiğinin varlığı/bağlantısı ile bu katsayıların ve kalanların
belirli integral için bütün kayıtlı yay boyunca denetlenmesidir.

## 3. R04'ten nitel olarak ne zaten çıkar?

Kompakt \(J=[-29,0]\) üzerinde düzenli analitik cusp grafiği olsun.
\(\ell(s,\nu)=s^2a(s,\nu)\), \(a(0,\nu)=2\) yazılabilir.
\(r=s\sqrt{a(s,\nu)}\) yerel analitik koordinattır. Ortak küçük bir
\(r\) aralığı kompaktlıkla seçilebilir. Tersini fold \(m\)'sinde
yerine koyup \(r=\pm\sqrt\ell\) alınca

\[
m_{\rm high}(\ell,\nu)=\tfrac12 C(\nu)\ell^{3/2}+O(\ell^2),\qquad
m_{\rm low}(\ell,\nu)=-\tfrac12 C(\nu)\ell^{3/2}+O(\ell^2).
\]

Analitiklik, kalanların \(\nu\) türevleri için de ortak
\(|\partial_\nu R_\pm|\le K\ell^2\) sınırı sağlar. Eğer
\(a_0=\min_J(-C')>0\) ise
\(K\sqrt\ell<a_0/4\) olduğunda
\(\partial_\nu m_{\rm high}<0<\partial_\nu m_{\rm low}\).
\(K=0\) durumunda bu ek küçültmeye gerek yoktur.

**Sonuç:** R04'ün analitiklik ve sıkı işaret sonucu, *bir miktar küçük*
ortak pencerede iç içe genişlemeyi zaten verir. R05'in katkısı bu nitel
varlık sonucunu yeniden keşfetmek değildir. R05, önceki pencerenin
tamamını, \(0<\ell\le10^{-6}\), ve nicel hız sınırını doğrular.
Bu not R05'in sayısal kalan hesaplarının yerine geçmez.

## 4. Açılma yönü üç ısı özdeşliğinin zorunlu sonucu mu?

Hayır; yalnız bu özdeşliklere dayanan böyle bir çıkarım yanlış olur.
\(\sigma\in\{-1,1\}\) için şu tam polinomları ele alalım:

\[
q_\sigma(x)=\frac{x^3}{6}-\frac{x^4}{24}+\frac{\sigma x^9}{9!},
\qquad
G_\sigma=\exp\left(-\frac\lambda4\partial_x^2
+\frac\mu{16}\partial_x^4-\frac\nu{64}\partial_x^6\right)q_\sigma.
\tag{3}
\]

Üstel seri sonludur; tüm operatörler komütatiftir. Bu nedenle (1)'in
üç eşiti polinom özdeşlikleri olarak sağlanır. Orijinde
\(D_0=D_1=D_2=0,D_3=1,D_4=-1,D_5=\cdots=D_8=0,D_9=\sigma,D_{10}=0\).
\((G,G_x,G_{xx})\)'in \((x,\lambda,\mu)\) Jacobian'ı

\[
\begin{pmatrix}0&0&-1/16\\0&-1/4&0\\1&1/4&0\end{pmatrix},
\qquad\det=-1/64
\]

olduğundan, \(\nu=0\) yakınında tek analitik cusp grafiği vardır.
\(D_6=D_7=D_8=0\) onun teğetinin orijinde sıfır olduğunu verir.
Cusp boyunca \(a=D_3,b=D_4\) için
\(a'=-\sigma/64,b'=0\); böylece

\[
C'(0)=\frac{8\sqrt2}{3}\frac{ab'-a'b}{b^2}
=-\frac{\sigma\sqrt2}{24}.
\tag{4}
\]

İki seçim zıt hareket yönleri verir. Kesin rasyonel denetim, sonlu
polinomu kurup üç PDE'yi bütün katsayılarıyla, Jacobian'ı ve bu
türevleri kontrol eder: [kod](check_structural_example.py),
[sonuç](structural_example.json).

**Sınır:** Bu polinomlar pozitif Jacobi çekirdeği dönüşümü olarak
sunulmuyor; çift fonksiyon oldukları da ileri sürülmüyor. Örnek yalnızca
üç PDE ile genel cusp şartlarının işareti zorlamadığını gösterir.
Pozitif, simetrik Fourier çekirdekleri alt sınıfında ters yönün mümkün
olup olmadığı bu örnekle çözülmüş değildir. R04'ün işareti böylece
özdeşliklerin ötesinde bilgi taşır; bunun yalnız bu çekirdeğe mahsus
veya literatürde yeni olması ayrı sorulardır.

## 5. Ölçtüğümüz geometri hangi anlamda somut?

\(C\) ve \(W\), sabit ve yeniden ölçeklenmemiş monomiyal kontrol
katsayılarında ölçülür. \(\widetilde m=m/C(\nu)\) seçilirse başterim
katsayısı 1 olur. Dolayısıyla \(C'<0\), keyfi parametre değişimleri
altında korunan bir tekillik invariantı değildir. Buna karşılık
\(e^{\lambda u^2+\mu u^4+\nu u^6}\) ailesinde aynı \(\lambda,\mu\)
birimleriyle yapılan karşılaştırma tanımlıdır ve yeniden üretilebilir.

İç içe geçme, her kesitin **kendi tam cusp merkezine** taşınmasından
sonradır. Mutlak kontrol düzleminde kapsama, bütün gerçek eksendeki
kök sayısı, fiziksel kararlılık, RH veya klasik \(\Lambda\) için
iyileştirme anlamına gelmez.
