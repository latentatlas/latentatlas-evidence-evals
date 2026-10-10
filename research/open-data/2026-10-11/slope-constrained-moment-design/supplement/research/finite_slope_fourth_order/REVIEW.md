# R22 — İddia, kapsam ve hesap denetimi

21 Eylül 2026. Araştırma sırasında yapılan özdenetim. Dış hakem raporu
veya bilgisayar tarafından denetlenmiş formal ispat değildir.

## Ne eklendi?

R21'in sonlu-geçişli gerçek optimumu üzerinden M⁻⁴ katsayısı türetildi.
Katsayı yerel residual türevleri ve alt momentlerden oluşan sonlu bir
matris formülüyle ifade edildi. Merkezlerin yalnız a² hareketi yeterli;
bu, gereken düzenliliği ilk düşünülebilecek C⁴ düzeyinin altında tutuyor.
R21'in C² koşullarına ek olarak yalnız q*'ın kök komşuluklarında C³
olması yeterli. Bunun en zayıf mümkün varsayım olduğu iddia edilmedi.

Ayrıca C² koşullar altında M⁻³ ölçekli artığın sıfıra gittiği,
simetrik hücre integraliyle gösterildi. R21, çiftlik tek başına bunu
gerekçelendirmez diyordu; o uyarı korunur. Burada q*(z)=0, Δ=O(a²)
ve Taylor–Peano kalanı kullanılarak ek kanıt verildi.

| İddia | Gerekçe | Durum/sınır |
|---|---|---|
| C² altında o(M⁻³) kalan | PROOF F7–F8 ve üçüncü mertebe Peano açılımı | Sonlu geçişler; yalnız çiftlik argümanı kullanılmadı. |
| Ek yerel C³ altında C₄ | PROOF F9–F15 | Genel kalan o(M⁻⁴); açık uniform sabit yok. |
| Xi=R−P, P≥0 | Hücrede kare tamamlama, G pozitif tanımlı | Baz değişmezliği ayrıca kontrol edildi. |
| P'nin destek kaybı anlamı | PROOF F12–F13 | Sabit q* residual desteği ile karşılaştırma. |
| İki-geçişli C₄=253/49152 | Genel jet formülü ve bağımsız beş parçalı integral | R21'in aynı örneği, aynı normalizasyon. |
| Toplam C₄ negatif olabilir | x−3x³+9x⁵ örneği, C₄=−1/15360 | P'nin işareti ile C₄'ün işareti ayrıldı. |
| C², C₄ için genel olarak yetmez | x+sgn(x)|x|⁵ᐟ² örneği | M⁻⁷ᐟ² katkısı; M⁴ ölçekli artık sınırsız. |
| Yeni yaklaşım seçilmiş bütçelerde daha doğru | 12 düzgün örnek noktasında rasyonel hata oranı <1 | Noktasal sertifikalar, bütün M'ler için hata sabiti değil. |

## Özellikle sınanan yanlış çıkarımlar

1. a=A/M bağımlılığı dördüncü mertebede hesaba katılır. Katsayıdaki
   3t² yerine t² yazan **bilerek yanlış** aday, exact testte sıfır
   olmayan artık üretir. Bu negatif kontrol geçmiş hesapta hata
   bulunduğu anlamına gelmez; yanlış bir kestirmenin test tarafından
   yakalandığını gösterir.
2. Moment kısıtları b*, D, Γ ve dolayısıyla C₂'yi zaten etkiler.
   “Momentlerin etkisi ancak M⁻⁴'te başlar” denmedi. R22'nin ayırdığı
   P, aynı başlangıç residualı etrafında sonlu-eğim moment düzeltmesinin
   ilave dördüncü mertebe katkısıdır.
3. H*(a), momentleri kaldırılmış orijinal qₘ-hedef problemi değildir.
   Residual q* sabit tutularak tanımlanan destek problemidir. Bu ayrım
   P'yi yorumlarken açık bırakılmadı.
4. P≥0, C₄≥0 anlamına gelmez. Düzgün negatif katsayılı örnek bu yanlış
   genellemeyi dışlar. P, alt momentlerin tersinir baz değişiminde aynıdır.
5. Bütün tek kuvvetlerin yokluğu iddia edilmedi. Kanıtlanan belirli
   sonuç M⁻³'ün yokluğu ve ek düzenlilikle dördüncü mertebe açılımıdır.
6. Genel o(M⁻⁴), örneklerin O(M⁻⁶) kalanı veya sayısal noktalardaki
   hata oranıyla aynı güçte değildir. Üç kesinlik düzeyi ayrı yazıldı.
7. Sonlu sayıda Taylor kalanı toplamak ile sonsuz geçişli theta
   kuyruğunu kontrol etmek aynı adım değildir. Theta için yeni C₄
   değeri, M⁻³ yokluğu veya hata garantisi ilan edilmedi.

## Kontroller ve kayıtların sınırı

12 exact cebir grubu; genel hücre/Taylor kimliği, yön işaretleri,
örtük bütçe dönüşümü, üç doğrudan örnek ve iki momentli matris cebiri
sınamalarını içerir. Son matris testi ilave bir integral ailesinin
inşa edildiği anlamına gelmez; genel vektör formülünün cebir sınamasıdır.

16 parametrik bütçede 132 rasyonel aralık üretildi. Altı R21 kök
çevrelemesi taze tekrarlandı. Diğer iki örnekte seçilen genişliklerde
tam hedefler rasyoneldir. Son kayıtlar 2⁻¹⁸⁰ ızgarasına dışa
yuvarlatıldı; yuvarlatılmış orta noktalar kesin uç gibi sunulmadı.

Asıl integral sisteminden/fonksiyon değerlerinden 90 ve 130 basamakta
32 ayrı sayısal koşu yapıldı. 132 yüksek hassasiyetli değer rasyonel
aralıkların içinde; iki hassasiyet farkı <10⁻⁷⁰. Bu yöntem Peano
kalanının analitik ispatını veya özgünlüğü otomatik doğrulamaz.

Üç panelli bilimsel şekil 80 basamakta örneklenip PNG/SVG çizildi.
PNG ayrıca görüntülendi. Eğriler ispat olarak kullanılmadı.
Yazım sırasında bir LaTeX ters-bölü kaçışı kontrol karakterine
dönüşmüştü; dondurma öncesi düzeltildi ve bütün metin dosyaları kontrol
karakterlerine karşı tarandı. Matematiksel formül değiştirilmedi.

Kapanış denetçisi rasyonel üretici ve exact cebir denetçisini farklı
geçici dizinde tekrar çalıştırır, sonuç baytlarını karşılaştırır;
sayısal kayıtların kaynak kimliği ve aralık içermelerini kontrol eder.
Her audit'te 32 sayısal koşuyu tekrar çalıştırdığı iddia edilmez.
Önceki 22 manifest ve 968 dosya girdisi korunur; R19/R20 makalesi
değiştirilmez. Masaüstü kopyası aktarım sonrasında ayrıca denetlenir.

## Özgünlük ve sonraki adım

Optimal değerlerin pertürbasyon açılımları yerleşik bir konudur.
Bonnans–Shapiro'nun *Optimization Problems with Perturbations: A Guided
Tour* başlıklı çalışmasının yayıncı özetinde bu tür açılımlar ve yaklaşık
optimal çözümler açıkça ele alınır. Bu tur **özet ve yayın kaydı**
incelendi; bütün teoremlerle birebir eşdeğerlik incelemesi yapılmadı.
[Birincil yayıncı sayfası](https://epubs.siam.org/doi/10.1137/S0036144596302644).

Bu nedenle kare tamamlama, Hessianın tersiyle katsayı hesaplama veya
pertürbasyon fikri tek başına yenilik sayılmıyor. Değerlendirilecek özel
paket: tam momentli eğim/genlik probleminde açık yerel-jet katsayısı,
moment düzeltmesinin ayrıştırılması ve düzenlilik sınırının açık örnekle
gösterilmesi. Bu araştırma katkısı adayıdır; literatür önceliği henüz
kurulmadı. Üç sorguluk bağlam kontrolü R20'nin özgünlük incelemesinin
yerine geçmez. [Arama kaydı](SEARCH_LOG.md).

Sıradaki somut araştırma, sonlu geçişli ispatın sonsuz kuyruk için
hangi uniform koşullarla sürdürülebileceğini belirlemektir. Merkezlerin
devamı, türev toplamları ve kalan kontrolü kurulmadan theta C₄'ü
hesaplayıp kesin sonuç gibi sunmak uygun olmaz. R16'nın mevcut sertifikalı
hata sınırı bu yeni nottan etkilenmez.
