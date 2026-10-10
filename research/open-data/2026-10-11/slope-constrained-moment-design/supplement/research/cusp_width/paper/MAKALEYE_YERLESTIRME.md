# Şekilleri ve R05 sonucunu makaleye yerleştirme

İki şekil ana metne girebilecek sadelikte hazırlandı. Birincisini
uniform yerel kök teoreminin ardından, ikincisini sonlu genişlik ve
iç içe genişleme teoreminin ardından kullanmak uygun.

- `figures.tex`: İngilizce açıklamalar, etiketler ve iki includegraphics
  komutu. Yollar ana TeX'in proje kökünden derlendiğini varsayıyor.
- `finite_width_section.tex`: tanımlar, teorem ifadesi ve ispatın ana
  mekanizması. Tam kalan hesabı `../PROOF.md` içinden doğrulama ekine
  taşınmalı; bu kısa parça tek başına bütün teknik ispat değil.
- `../output/pdf/`: gömülü fontlu vektörel PDF şekilleri.
- Bu klasördeki EPS ve SVG sürümleri düzenlenebilir vektörel çıktılar;
  PNG sürümleri önizleme için.

Şekiller yaklaşık 179 mm genişliğinde üretildi; metinler 9 punto,
ana çizgiler yaklaşık 1.1 punto. Siyah-beyaz okumada da kesitleri
ayırmak için düz/kesikli çizgi kullanıldı. Açıklamalar şeklin içine
gömülmedi; ayrı LaTeX metni olarak tutuldu. Fontlar PDF içine gömüldü,
iki PDF yeniden PNG'ye çevrilip görsel olarak incelendi.

Hedef dergi belirlenince baskı genişliği, yazı boyutu ve kabul edilen
dosya biçimi o derginin yazar kılavuzuna göre ayarlanmalı. Genel
örnek olarak Taylor & Francis, ayrı şekil dosyaları, gömülü fontlar,
uygun boyut ve ayrı açıklamalar istiyor; çizgi grafikler için EPS
öneriyor. PDF'nin her dergide doğrudan tercih edilen yükleme biçimi
olduğu varsayılmadı.
[Resmi şekil kılavuzu](https://authorservices.taylorandfrancis.com/publishing-your-research/making-your-submission/submit-electronic-artwork/).

Bilimsel okumada şu ayrımlar korunmalı:

1. Şekil 1(a)'daki turuncu bantlar fold konumunu kapsar; bandın tümüne
   aynı kök sayısı atanamaz. Tam cusp üçlü köktür.
2. Şekil 1(b)'deki merkez çizgisi görsel yardımdır. C' işaretinin kanıtı
   interval hesapları ve analitik özdeşliklerdir.
3. Şekil 2(a)'da hesaplanan noktalar aralıklarla doğrulanmıştır. Aradaki
   çizgi/fill interpolasyonu ayrıca rigoröz bir interpolasyon sınırı
   olarak sunulmaz; dal ve iç içe geçme teoremleri ayrı kanıta dayanır.
4. Şekil 2(b)'deki dikdörtgenler bütün hücre ve bütün pozitif ell
   aralığı için geçerli sınırlardır, tek bir fonksiyonun ölçüm eğrisi değil.
5. Yüzdelik artışın ell=10^-6 kesitine ait olduğu yazılmalı. C'nin
   başterim artışı ile sonlu W'nin oranı birbirinin yerine kullanılmamalı.

Özgün `buldurgan-A3-cusp-dBN.tex` değiştirilmedi. Bu ekler bütün eski
makalenin güncellendiği anlamına gelmiyor. Ortamda LaTeX derleyicisi
bulunmadığı için TeX parçaları derlenmedi; PDF şekilleri ise üretilip
kontrol edildi. Gönderim öncesinde birleşik metnin derlenmesi ve şekil
numarası/teorem atıflarının bütün makale üzerinde denetlenmesi gerekir.
