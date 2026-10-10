# R20 — Derinleştirmeye ilk adım: sonlu eğimde doğru geçiş merkezi

21 Eylül 2026. **Durum:** aşağıdaki yerel önerme burada türetilmiş bir
analitik araştırma notudur; özgünlüğü iddia edilmiyor. Theta problemine
yeni bir sertifika eklenmedi. Kesin olan yardımcı sonuç ile araştırılacak
ana soru ayrı tutulmuştur.

## Araştırma sorusu

**M sonlu olduğunda gerçek en iyi profil hangi merkezlerden geçer;
momentleri sağlayan dual katsayılar bu merkezlerle birlikte nasıl değişir?**

Bu soru mevcut sonucun doğrudan devamıdır. Bilinen norm için bir kez daha
isim veya algoritma üretmek yerine, tam moment koruyan optimumun sonlu
bütçe yapısını ve sonraki hata mertebesini anlamayı hedefler. Aşağıdaki
hesap, “her rampayı eski sıfıra merkezle” kestirmesinin neden yeterli
olmadığını açıkça gösterir.

## 1. Tek geçiş için denge koşulu

q sürekli olsun; z'nin solunda negatif, sağında pozitif olsun. A,M>0
ve a=A/M. [z−2a,z+2a] içinde başka işaret değişimi ve sınır noktası
bulunmasın. [z−a,z+a] içinde tek bir c için

\[
 B(c):=\int_{c-a}^{c+a}q(x)\,dx=0. \tag{N1}
\]

Gerçekten B(z−a)<0, B(z+a)>0 ve iç aralıkta
B′(c)=q(c+a)−q(c−a)>0. Ara değer teoremi varlık ve teklik verir.

Sabit artık yoğunluğu q için, g_c'nin dışarıda A sgn(q), içeride
M(x−c) olduğu profili ele alalım. Tek işaret değişimi olan daha büyük
bir aralıkta, bütün |g|≤A, Lip(g)≤M fonksiyonları arasında ∫qg'yi bu
profil en büyük yapar. **Bunun kısa global gerekçesi:** dış bölgelerde
noktasal doygunluk en iyidir. İçeride

\[
 Q(x)=\int_{c-a}^{x}q(v)\,dv
\]

negatiftir; iki uçta sıfırdır. Mutlak sürekli Lipschitz fonksiyonlar
için parçalı integrasyonla

\[
 \int_{c-a}^{c+a}q(g-g_c)
 =-\int_{c-a}^{c+a}Q(x)(g'(x)-M)\,dx\le0. \tag{N2}
\]

Azalan işaret geçişi q ve g'nin işaretleri çevrilerek ele alınır.
Bu, birinci dereceden optimaliteyi doğrudan integral eşitsizliğine
çeviren klasik bir yöntemdir; tek başına yayınlık yenilik sayılmamalıdır.

q bir basit sıfır çevresinde C² ise (N1)'den

\[
 c-z=-\frac{q''(z)}{6q'(z)}a^2+o(a^2). \tag{N3}
\]

Gerekçe: simetrik ortalama q(c)+a²q″(c)/6+o(a²)'dir.
Bölünmüş integral denkleminin c türevi q′(z)≠0; örtük fonksiyon
teoremi c(a) verir. Bu, **sabit q** için merkez kaymasıdır;
momentli tasarımda dual katsayının da değişmesi gerekebilir.

## 2. Tam kesirle yanlışlanabilen kestirme

[-1,1]'de q(x)=x+βx², 0<|β|<1/2 ve A=1 olsun.
q'nun tek sıfırı z=0'dır. Küçük a=1/M için dengeli merkez

\[
 c+\beta(c^2+a^2/3)=0,
 \qquad
 c=\frac{-1+\sqrt{1-4\beta^2a^2/3}}{2\beta}.
\]

J(c)=∫qg_c dersek, doğrudan üç parçalı integrasyon şunu verir:

\[
 J(c)-J(0)=-c^2-\frac{2\beta}{3}c^3
                 -\frac{2\beta}{3}a^2c. \tag{N4}
\]

Tam optimum merkezi hesaplamadan, uygun rasyonel c₀=−βa²/3 seçimi bile

\[
 J(c_0)-J(0)=\frac{\beta^2a^4}{9}
                    +\frac{2\beta^4a^6}{81}>0 \tag{N5}
\]

verir. Sıfır merkezli rampanın kaybı a²/3'tür; merkez kayması a⁴
mertebesinde iyileşme sağlar. Dört rasyonel (β,a) çifti için ayrı
üç parçalı integral hesabı [tam cebir tanısında](equation_checks.json)
doğrulandı. Bu bir grid optimizasyonu veya yaklaşık kazanç testi değildir.

**Çıkarım:** R19'un baş katsayısı ile bu iyileştirme uyumludur; a⁴
terimi a² baş terimini değiştirmez. Fakat merkezleri sadece eski
sıfırlara koyup “sonlu bütçede tam optimum” demek genel olarak yanlıştır.
R19/R20 böyle bir iddia taşımıyor.

## 3. Asıl problem için elde edilen somut hedef

q_b=q_m−Σ b_jq_j ve uygun ayrı geçiş aralıkları için şu sistemi araştır:

\[
 \int_{c_k-a}^{c_k+a}q_b(u)\,du=0 \quad\text{(her geçiş)},
 \qquad \int q_j g_{b,A,M}=0\quad(j<m),
 \qquad \int q_m g_{b,A,M}=f. \tag{N6}
\]

İlk eşitlikler destek normunun geçişlerini dengeler; sonraki eşitlikler
momentleri ve hedefi uygular. Bir çözümün gerçekten optimum olduğunu
söylemek için destek normu eşitliği, dual katsayıların bulunması ve
bütün kuyruk geçişlerinin kontrolü birlikte gerekir.

Sonraki araştırma sırası:

1. Önce sonlu sayıda basit geçişli bir genel aile için bu sistemin
   optimumla eşdeğerliğini ve b(M)'nin yerel varlığını kanıtlamak.
2. C² yerine gerekli daha yüksek düzenlilik/summability koşullarını
   açıkça koyarak M⁻⁴ düzeyine inilip inilemeyeceğini sınamak.
3. Ancak bundan sonra theta ailesinin sonsuz kuyruğuna geçirmek.

**Henüz bilinmeyen:** Theta probleminde M⁻³ teriminin sıfır olması,
M⁻⁴ katsayısının varlığı/değeri, sonlu-M optimumun tam profili veya
cusp boyunca uniformluğu. Tek geçişli polinom örneği bunları ispatlamaz.
Bu yön, mevcut M⁻³ üst hata sınırını gereksiz veya yanlış da yapmaz.
