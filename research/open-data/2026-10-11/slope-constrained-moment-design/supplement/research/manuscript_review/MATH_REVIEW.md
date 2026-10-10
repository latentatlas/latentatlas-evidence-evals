# R20 — Matematik ve hesap denetimi

21 Eylül 2026. İncelenen metin: R19 `manuscript_core/manuscript.tex`.
Bu kayıt iç denetimdir; dış hakem raporu veya formal doğrulama değildir.
Eski, terk edilmiş TeX bu denetimin doğruluk kaynağı değildir.

**Sonuç:** R19'un ana katsayısını, sayısal sınırlarını veya teorem
sonuçlarını değiştiren bir hata bu incelemede saptanmadı. Bazı ispat
geçişleri yeterince açık yazılmamıştı; R20 metni bunları tamamlar.
“Hiç hata kalamaz” sonucu çıkmaz. Aşağıdaki hipotezler, yazılım
güven sınırı ve dış inceleme ihtiyacı geçerliliğini korur.

## 1. Gerçekte yeniden yapılan kontroller

- Başlangıçta 20 önceki manifestin 884 dosya girdisi doğrulandı.
  Bu, kaynak kimliği kontrolüdür; matematik ispatı değildir.
- C1 temel cusp aralık üreticisi ve C2 minimum norm üreticisi yeniden
  çalıştırıldı. Sırasıyla 72 ve 3.972 dyadik aralık kaydı aynı uçları verdi.
- R15/C3 ve R16/C4, geçici araştırma kopyasında yeniden üretildi;
  yeni R15 sonucu R16'ya girdi oldu. Üreticiler, ayrı rasyonel denetçiler,
  cebir ve mpmath kontrollerinden oluşan 11 işlik zincir tamamlandı.
  2.966 aralık kaydı ve 832 diğer matematiksel değer eşleşti.
- Toplam **7.010 aralık kaydı** ve 1.157 diğer değer eşleşti. Bunlar
  kayıtlardaki oluşumlardır; 7.010 bağımsız teorem veya tekil sayı değildir.
  Değişen alanlar süreler ve bunları içeren dosyaların hash'leridir.
- C1'in beş türevi ayrıca, aralık üreticisini kullanmayan gerçek eksen
  mpmath integraliyle 115 basamakta karşılaştırıldı; farklar 10⁻⁹⁶'dan
  küçüktü. C2'nin üç işaret profili momenti 50 ve 80 basamakta tekrar
  hesaplandı; hassasiyet farkı 10⁻⁴⁵'in altında ve değerler sertifika
  aralıklarının içindeydi. C2 karşılaştırıcısı donmuş sertifikayı okur;
  yeni C2'nin matematiksel uçlarının aynı olduğu ayrıca doğrulanmıştır.
- R17'nin 19 tam cebir kontrolü tekrar geçti. Bu tur eklenen yedi
  kontrol grubu determinantları, theta türev polinomlarını, 1/3 ve
  1/12 çarpanlarını ve ayrı araştırma pilotunun dört tam kesir örneğini
  kontrol eder. Son grup R19'un doğruluğuna delil olarak sayılmaz.

Üreticilerin tekrar çalışması bağımsız bir aralık yazılımı geliştirmek
anlamına gelmez. Temel kutular ve önceki tasarım girdileri donmuş
araştırma dosyalarından gelir. mpmath sonuçları sayısal karşılaştırmadır;
rigoröz kuyruk sınırının veya aralık integralinin yerine geçmez.

[Başlangıç kimlikleri](baseline.json), [C1–C2 eşleştirmesi](base_comparison.json),
[C3–C4 tekrar zinciri](slope_replay/report.json),
[ayrı cebir kontrolü](independent_algebra.json),
[ek cebir tanıları](equation_checks.json).

## 2. Denklemlerin tek tek kapsanması

[Denklem envanteri](equation_inventory.json), R19'daki 54 numaralı
`equation`/`align` bloğunun tamamını, kaynak satırları ve aşağıdaki
gerekçe gruplarıyla eşler. Bir blok birden çok denklem içerebilir.
Numarasız metin çıkarımları da bu gruplarda incelendi. Envanter bir
inceleme kaydıdır; kendi başına denklemleri ispatlayan bir program değildir.

| Grup / bloklar | Kontrol edilen çıkarım ve gerekçesi | Sonuç |
|---|---|---|
| A: E01–E07 | Moment hedefinin işareti, δ*=f/D*, işaret tanığı, Sion minimax ve iki ayrı norm ölçeği. Yerel düzgün yakınsama + integrallenebilir kuyruklar moment sürekliliğini sağlar. V≥f olduğunda işaret değişimi ve f/V ölçeklemesi negatif hedefe ulaşır. | Yeniden türetildi |
| B: E08–E13 | H1–H3, Γ'nın sonluluğu, tüm uygun h için dualite açığı. İki kusurun toplamı ≥2δ*−2Mv; integral δ*³/(3M²). Önce sonlu kök kümesi, sonra M limiti, sonra ε, sonra kök kümesi artırılır. | Limit sırası ve 1/3 doğru |
| C: E14–E20 | Birim basamak düzeltmesi, C² majörantları, J'nin tersinirliği ve c(a)−z=O(a²). Momentler tam korunur; qᵣ(z)=0 olduğundan sonlu merkez düzeltmesi O(a⁴)'tür. α′=O(a) nedeniyle α/a küçük a'da monoton ve bütün büyük M'leri kapsar. | Baş katsayı değişmiyor |
| D: E21–E27 | Pozitif theta çekirdeği, analitiklik, sabit h, t türevleri ve kontrol türevlerinin çarpanları. Cusp determinantı f₄f₃/64; hedef rank determinantı g₄(g₄g₇−g₅g₆)/4096. Gram matrisi tam moment sağ tersini verir. | Çarpanlar/işaretler doğru |
| E: E28–E33 | a*'ın kutuda bulunması, yerel güçlü ve küresel konvekslikten tekliği. Sonlu kök örtüsü, faz türevi, sonsuz basit kökler, ayırma ve theta türev zarfları. | Sayısal ve analitik zincir korundu |
| F: E34–E43 | Uniform hata teoremi, B₂/A₃ sonsuz toplamları ile A₄ sonlu toplamı; merkez Jacobian sapması, κ/η sınırları. B'nin tersinirliği ve a=0'a sürekli uzatma, sabit noktayı gerçek moment çözümü yapar. | Bütün genişlik aralığı kapsanıyor |
| G: E44–E51 | Merkez kayması maliyeti, Ū, her M≥M₀ için tanık, D*e=αL özdeşliği ve paydada pozitiflik. Alt sınırda negatif Taylor polinomu pozitif kısım adımıyla kullanılır. Eşik ve yüzde hata tam kesirle hesaplanır. | K₋,K₊ ve eşik aynı |
| H: E52–E54 | Yarı doğru integrali ve türev toplamları için üstel kuyruk. Başlangıç noktasındaki oran, pozitif terimler e⁻⁴ᵘ ile çarpılınca azaldıkları için bütün kuyrukta geçerlidir. | Gerekçe R20'de açıklaştırıldı |

### En hassas beş geçiş

**Tam moment düzeltmesi baş katsayıyı neden değiştirmiyor?**
J_{jk}=−d_k q_j(z_k) tersinirdir. Simetrik yumuşatma momentlerde O(a²)
hata üretir; örtük fonksiyon teoremiyle seçilmiş merkezler O(a²) oynar.
Hedef artık yoğunluğu qᵣ kökte sıfırdır. Bu nedenle merkez kaymasının
hedef momentteki etkisi O(|c−z|²)=O(a⁴)'tür. Burada yalnız “küçük
kayma” demek yetmez; qᵣ(z)=0 iptali gereklidir ve sağlanıyor.

**Sonsuz toplamda gizli limit değişimi var mı?**
Üst yapımda H2'nin q_j, q_j′ ve q_j″ için toplanabilir yerel
üst sınırları vardır. Yerel yumuşatma farkları iki kez türevlenebilir.
Ayrı ayrı sonsuz basamak kuyrukları toplanmaz. Alt sınır sonlu kök
kümelerinde kurulur; sonra monoton biçimde artırılır. Böylece bütün
kökler için tek bir uniform Taylor kalanı varsayılmıyor.

**Sabit nokta yalnız örneklenmiş bütçeleri mi kapsıyor?**
Hayır. κ+η<1 bütün 0<a≤2⁻¹⁴ için geçerlidir. B'nin tersinirliği
∥I−BJ∥<1'den gelir. a=0'a sürekli uzatma ve uniform kontraksiyon,
v(a)'nın sürekliliğini verir. α(a)/a sıfırda sonsuza gider ve son
uçta M₀'ın altındadır. Ara değer teoremi her M≥M₀'ı sağlar;
bu aralığın tamamında monotonluk varsayılmıyor.

**A₄ hesabının gerekçesi:** |Δ_k|≤a²V_k için

\[
\left|\int q_r(s_c-s_z)\,du\right|
\le\sum_{k=1}^3R_{1k}\Delta_k^2,
\qquad
|d_k(I(c_k,a)-I(z_k,a))|
\le a^2R_{2k}|\Delta_k|/3.
\]

İlk eşitsizlik sıfırdaki iptalden, ikincisi |∂_cI|≤a²R₂/6 ve
|d_k|=2'den gelir. Böylece daha önce kullanılan A₄ formülü aynen
elde edilir. R19 bunu bir cümleye sıkıştırmıştı; R20 iki adımı yazar.

**Düzgün ve rank-üç sınıf için neden aynı infimum?**
Kesme ve pozitif mollifier genliği artırmaz; küçük Gram düzeltmeleri
momentleri tam korur. δ*<1 pozitiflik payı bırakır. h_θ=−1+θ(1+h₀)
ailesi, temel dört moment nedeniyle uygun kalır ve eğimi istenildiği
kadar küçültür. Bir minimum dizi yerel kompaktlıkla Lipschitz minimum
verir. Daha düşük eğimli tanıkla karışım, yumuşatma ve küçük C¹
düzeltmeleri eğim/pozitiflik payına sığar. Rank determinantının sıfır
kümesinden küçük jet değişimiyle çıkılır. **Düzgün sınıfta minimuma
ulaşıldığı söylenmiyor.**

## 3. Değişmeyen nicel sonuç

\[
\delta(M)=\delta_*+C_*M^{-2}+o(M^{-2}),\qquad
C_*=\frac{\delta_*^3}{3D_*}\sum_k w(z_k)|r_*'(z_k)|.
\]

Theta örneğinde

\[
9.20340371\times10^{-25}<C_*<9.20340375\times10^{-25},
\]

ve bütün M≥2×10⁻⁵ için

\[
\frac{C_*}{M^2}-\frac{9.624\times10^{-33}}{M^3}
<\delta(M)-\delta_*<
\frac{C_*}{M^2}+\frac{2.167\times10^{-32}}{M^3}.
\]

M₀'daki %0,1178 üst hata sınırı **ek genliğe** aittir. Bunu toplam
genliğin hatası veya istatistiksel güven aralığı diye yorumlamıyoruz.

## 4. Kapanmayan sınırlar

- H1–H3 doğrulanmadan her pozitif çekirdeğe uygulanamaz.
- Q tek bir kesin cusp noktasıdır; bütün cusp eğrisi için uniform
  teorem bu metinde yoktur.
- R19/R20 yapımı, sonlu M'de gerçek optimum profili bulduğunu söylemez.
- M⁻³ rigoröz kalan sınırıdır; ilk gerçek sonraki asimptotik terimin
  M⁻³ olduğu veya katsayısının keskin olduğu söylenmez.
- Bu çalışma zeta sıfırları hakkında küresel bir sonuç, fiziksel deney
  veya AI/LLM başarımı sonucu vermez.
- Kaynak kodu/Arb/FLINT, analitik zarflar ve hesapları metne taşıyan
  mantık güvenilen bileşenlerdir. Dış uzman incelemesi yapılmış değildir.

Bu sınırlar sonuçların değersiz olduğu anlamına gelmez; tam olarak hangi
önermeleri savunabildiğimizi belirler.
