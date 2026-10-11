# Hassas analitik adımların yeniden incelenmesi

21 Eylül 2026. Bu not yeni bir teorem içermez. İncelemenin akıl yürütme
izini kaydeder; özgün tam ispatlar R01–R12 paketlerindedir. Dış uzman
veya ispat asistanı doğrulaması değildir.

## İntegral ve türev sözleşmesi

u≥0 için theta terimi
πk²e^(5u)(2πk²e^(4u)−3)e^(−πk²e^(4u)) pozitiftir. Her sonlu kontrol
kutusunda çift üstel negatif terim, kontrol polinomlarını ve gereken
moment kuvvetlerini domine eder. Bu, integral altında türevleri ve yerel
analitik bağımlılığı destekler. Türev işaretleri pₙ=(2u)ⁿcos(2tu+nπ/2)
üzerinden yeniden çıkarıldı; 1/4, 1/16, 1/64 faktörleri doğru.

Arb callback'ine verilen theta toplamı sonludur ve karmaşık değişkende
entiredir. Sonsuz theta serisi ve sonsuz u aralığı için gerçek eksen
artıkları ayrıca kapsanır. Sonsuz serinin karmaşık bütün düzlemde aynı
şekilde yakınsadığı varsayılmıyor. Türev majorantlarında kontrol kutusunun
en kötü ucu, integral kesilmesinde seri ve alan kuyruğu, Taylor modelinde
ise bütün kutuyu kapsayan kalan kullanılıyor. Nokta integrali küçük
çıkıyor diye kutu üzerinde küçük olduğu varsayılmıyor.

## Cusp dalı ve hücreleri birleştirme

Bir parametrede X₁ ve X₂ kutularının yalnız kesişmesi, kutulardaki tekil
çözümlerin aynı olmasını sağlamaz. İncelenen güncel zincir daha güçlü bir
koşul kullanıyor: ortak parametre yüzündeki bir çözümün dar kök kapsaması,
komşu hücrenin teklik kutusunun içine giriyor. O komşu kutuda çözüm tek
olduğu için iki çözüm aynıdır. Bu nedenle R03'te 57 ve R08'de 402 birleşme
gerçek bir dal/yüzey elde etmeye yeterlidir. Q ve S kimlikleri de benzer
içerme ve teklik argümanına dayanır; ondalık yakınlıkla özdeşleştirme yoktur.

Uniform kontraksiyonun strict boşlukları ve denklemlerin analitikliği,
kapalı parametre hücrelerinde kurulan grafiklerin yerel analitik
devamlılığını verir. Yerel grafikler ortak yerde aynı olduğundan yapıştırılır.
Tüp dışındaki bütün kökler için teklik iddiası bu gerekçeden çıkmaz.

## Fold geometrisi ve kök sayısı

F=Fₜ=0 denklemlerinin kontrol Jacobian'ı, integralin türev ilişkileriyle
yazıldı. Cusp'ta D₀=D₁=D₂=0, D₃=a, D₄=b için tam üç-değişken
Jacobian determinantı a²b/64. Kontrol determinantının işaretini yanlış
cofactor ile ters çevirmeme kontrolü yapıldı.

Fold jetleri aynı denklemlere yerine konularak s⁰,…,s⁴ katsayıları tam
rasyonel polinom aritmetiğinde sıfırlandı. Özellikle λ'nın s² katsayısı 2,
μ'nün s³ katsayısı 16a/(3b), s⁴ katsayısı −4. Dal sürücüleriyle toplam
türev ve B₀,…,B₄ taşıma ifadeleri de ayrı cebirle kontrol edildi. Sıfırdan
uzak paydalar bu cebir programından değil ilgili paketlerin aralık
sertifikalarından gelir; cebir denetiminin kapsamı bununla karıştırılmadı.

Cusp çevresinde t uçlarının sıfırdan uzak olması köklerin pencereye
uçlardan girip çıkmasını engeller. D₃'ün işareti Rolle ile en fazla üç
kökü, dörtlü kökte g₄'ün işareti toplam çokluk dahil en fazla dört kökü
sağlar. Basit kök sayısı ancak bir çoklu kökten veya uçtan geçişle değişir.
Bu yüzden fold grafiği, uç işaretleri ve bileşen tanıkları birlikte
bir/üç sınıflamasını verir; tek başına çizim veya birkaç kök örneği vermez.

R10'da tüm ayrı durağan noktalar sıralandığında aralarında türev sıfır
olmadığından fonksiyon sıkı monotondur. Durağan noktanın kendisi dejenereli
olsa bile fonksiyon değeri sıfır değilse işaret-değişimi ölçütü geçerlidir.
İki çift kök örneğinde dört denklem aynı kontrol değerlerinde birlikte
çözülür; farklı parametrelerdeki iki fold noktası birleştirilmez.

## Genel moment sağ tersi ve tam minimum formülü

R11'de bir jet bağımlılığı P(u)cos(2τu)+Q(u)sin(2τu)=0 verir. Pozitif
yoğunluklu aralıkta hemen her yerde sıfır olan analitik fonksiyon
özdeş sıfırdır. τ≠0 iken üstel/rasyonel fonksiyon çelişkisi P=Q=0 verir.
Bu nedenle pozitif bump ile Gram matrisi pozitif tanımlıdır ve tersinden
kurulan Rₘ gerçekten L(Rₘv)=v sağlar. Kompakt destek norm sabitini sonlu
yapar. Bu argüman keyfî dört kosinüs matrisinin otomatik terslenebilir
olduğunu söylemez; kullanılan matrisler sayısal sertifikada ayrıca sınanır.

D=minₐ∫|p₃−Σaᵢpᵢ|dρ için sonlu boyut norm eşdeğerliği koerciviteyi
sağlar. Bağımsızlık ve sonlu boyut uzayının kapalılığı D>0 verir. Artık
analitiktir ve özdeş sıfır değildir; sıfırları Lebesgue ölçüsü, dolayısıyla
ρ ölçüsü bakımından sıfırdır. Mutlak-değer integralinin a'ya türevi,
|pᵢ| majorantıyla gerekçelendirilir. Minimumda ∫pᵢsign(r)dρ=0 olur.
Buradan ∫p₃sign(r)dρ=D, h*=−f₃sign(r)/D'nin uygulanabilirliği ve zayıf
dualite ile tam δ*=|f₃|/D eşitliği çıkar.

Eşitlik koşulu, minimum-norm h'nin r≠0 olan ρ-desteğinde belirlenmiş
işarete eşit olmasını zorlar. Katsayı vektörü a'nın tekliği gerekli
değildir. Normun bütün pozitif eksende alınması ile ρ-hemen her yerde
tekliğin farkı korunur; destek dışı değerler minimumu bozmayacak biçimde
seçilebilir. Tam pozitif destekte bu ayrım kaybolur.

Tam destekte artık büyük u sinüs zirvelerinde zıt işaretler alır;
D>|f₃|, dolayısıyla δ*<1. Düzgün kompakt yaklaşımın normu korunur,
ilk dört moment hatası R₃ ile tam düzeltilir, kalan 4–7 jetleri R₇ ile
istenildiği kadar küçük değiştirilebilir. g₄(g₄g₇−g₅g₆) sıfır polinomu
olmadığından sıfır olmadığı küme yoğundur. Bu, norm ve pozitiflik payını
koruyarak tam dörtlü ve rank üç tasarımlar verir. İnfimum eşitliği bu
argümana dayanır; düzgün bir tam minimizerin varlığına değil.

## R12: alt/üst sınırların yönü ve yumuşatma

Her sabit r için |∫rh dρ|=f₃≤∥h∥∞∫|r|dρ. Böylece ∫|r| için bir
**üst** sınır, δ* için **alt** sınırdır. Aday katsayıların tam optimal
olması gerekmez. Üst maliyet için ise belirli uygulanabilir h ve onun
normuna **üst** sınır gerekir. İki taraf farklı gerekçeyle kapanır.

İşaretin yanlış olabileceği kök kutusunun uzunluğu 2β, |r|−rs₀ en fazla
2|r| olduğundan hata 4βWₖRₖ'dir. [0,1] işaret örtüsünün bütünlüğü ve
kutularda monoton artık, gözden kaçmış sıfır olasılığını o aralıkta
giderir. Sonsuz kuyrukta bütün sıfırları saymak gerekli değildir.

Eη=Hη−H tek olduğundan sabit q(b) terimi gider. Tek geçiş için
∫|v|exp(−2|v|/η)dv=η²/2; sıçrama büyüklüğü 2, çift uzantıda 2N geçiş
ve yarı eksen faktörü 1/2 birlikte N Mη² verir. q'nun pozitif eksendeki
global Lipschitz sınırı çift uzantısı için de yeterlidir; sıfırda türev
varlığına ihtiyaç yoktur.

Bu turdaki ek kontrolde v=(u−b)/η kullanıldı. Pozitif yarı eksendeki
moment farkı, ayna geçişlerini de içerecek biçimde her pozitif knot için
dₖη∫₀∞E(v)[q_even(b+ηv)−q_even(b−ηv)]dv olarak yazıldı. V=40 sonrası
hata N Mη²(2V+1)e^(−2V) ile kontrol edilir. Finite [0,40] bölümde bütün
u argümanları pozitiftir; kullanılan 12-terimli çekirdeğin seri hatası
ayrıca eklenir. Bu yeniden düzenleme dar geçişleri çözülemeyen sivri
aralıklar olarak integratöre vermeyi önler. Dokuz sonuç önceki hata
bütçelerinin içinde kaldı; eski sınırlar daraltılmadı veya değiştirilmedi.

Son tasarımın ilk dört türevi tam doğrusal sistemle sıfırlanır. Aralık
residualının sıfırı içermesi bu tam eşitliklerin ispatı değildir; yalnız
tutarlılık kontrolüdür. Pozitiflik norm üst sınırından gelir. g₄ ve üç
kontrol determinantı ayrıca sıfırdan uzak bulunur. Determinantın doğru
ifadesi g₄(g₄g₇−g₅g₆)/4096; tam 3×3 determinantla da denetlenir.

Minimumun sürekli sınıfta elde edilemeyişi, tam minimumdaki işaret
çarpanının en az bir izole işaret değişimine sahip olmasına dayanır.
Yoğunluğun her açık aralıkta pozitif olduğu durumda iki tarafta karşıt
sabitlere hemen her yerde eşit sürekli bir fonksiyon, geçişte sürekli
kalamaz. Bu nitel sonuç son eşik aralığının çok dar olmasından çıkarılmaz.
