# R21 — İddia, ispat, açıklık ve kapsam denetimi

21 Eylül 2026. Bu kayıt araştırma sırasında yapılan özdenetimdir;
bağımsız bir hakemin değerlendirmesi veya formal doğrulama değildir.

## Kazanımın dar tanımı

R20'nin sıradaki sorusu sonlu geçişli problem için yanıtlandı: yeterince
büyük her M'de dengeli rampa merkezleri ve dual katsayılar birlikte
devam ettiriliyor; bu profilin **bütün** uygun Lipschitz fonksiyonlar
arasında tek global genlik optimumu olduğu doğrudan gösteriliyor.
Sonuç yalnız iki-geçişli polinoma ait değildir; kompakt aralıkta sonlu
sayıda basit sıfır ve tam moment rankı olan genel C² yoğunluklar içindir.
Polinom, ispatın sayısal dayanağı değil, tam çözülebilen bir sınamasıdır.

Bu sonuç çalışmanın içinde yeni bir adım olarak kaydedildi. Dünya
literatüründe ilk olduğuna henüz karar verilmedi. Mevcut R19/R20 makale
PDF'leri ve bütün eski sertifikalar aynen korundu; yeni teorem henüz
makaleye eklenmedi.

## İddia–gerekçe haritası

| İddia | Esas gerekçe | Hesabın rolü / sınırı |
|---|---|---|
| Sıfır ve merkezlerin yerel devamı | Basit sıfır, kompaktlık, IFT; PROOF §2.1 | Sonlu N gerekir; sonlu kesme sonsuz kuyruğu ispatlamaz. |
| Momentleri sağlayan b(a) | D_bΨ=−G, G pozitif tanımlı; PROOF §2.2 | Rank varsayılır; örnekte G=256/63 tam hesaplanır. |
| Global destek optimalitesi | Her hücrede Q'nun işareti, parçalı integrasyon; PROOF §2.3 | Durağanlık tek başına yeterli sayılmaz. |
| Gerçek genlik optimumu ve tekliği | Destek eşitliğinin tekliği, tam momentler; PROOF §2.4 | Yalnız rampalar sınıfında bir minimum değildir. |
| Her yeterince büyük M'yi kapsama | M(a)=A(a)/a kesin monoton, M→∞ | Birkaç örnek M değeri ile bu sonuç çıkarılmadı. |
| Merkez ve dual hareketi | Çift C² dal, T14–T16 | a ile M⁻¹ ayrılır; M katsayıları δ₀² ile çarpılır. |
| Eski baş katsayıyla tutarlılık | T17 ve doğrudan G/Γ/D hesabı | Baş katsayı yeni bir bulgu diye sayılmadı. |
| Örnek bütün M≥M(1/5)'te geçerli | E8–E9 ve uniform işaret/ayrıklık sınırları | Altı rasyonel örnek noktası bu uniform ispatın yerine geçmez. |
| Eski merkezlerden kesin iyileşme | T−T₀=2d²(1+2βd)>0 | Aynı a,A,M ve aynı alt moment karşılaştırılır. |

Genel notta T1–T17, örnekte E1–E12 etiketleri vardır. Denklem numarası
veya kontrol sayısı matematiksel doğruluğun otomatik ölçüsü değildir.

## En kolay karışabilecek noktalar yeniden kontrol edildi

1. q_b'nin kökü ile rampa merkezi aynı değişken değildir. Koşul
   ∫[c−a,c+a]q_b=0; q_b(c)=0 değildir.
2. Sabit residual için −q″/(6q′) kayması, momentli problemde tek başına
   doğru değildir. b(a) hareketi de cₖ katsayısına girer.
3. IFT yalnız yerel varlık/teklik verir. Global optimum sonucu IFT'den
   değil ayrı destek eşitsizliğinden gelir. Global dual tekliği iddia edilmedi.
4. Azalan geçişte Q>0, v′+M≥0; artan geçişte Q<0, v′−M≤0. İki işaret
   aynı formülde kontrol edildi. İki-geçişli örnek her ikisini içerir.
5. Uçlar sabit olsaydı destek doygunluğu farklılaşabilirdi. Serbest uç
   değerler T1'de açıkça belirtildi.
6. C² çiftlik M⁻³'ü tek başına yok etmez. |a|³ karşıörneğiyle bu
   çıkarımın sınırı açık bırakıldı. Genel M⁻⁴ katsayısı türetilmedi.
7. Tek optimum Lipschitz sınıfındadır. Düzgün/nondegenerate geometrik
   çekirdek için tam erişim sonucu çıkarılmadı.
8. Örnek pozitif temel ağırlık w=1 ile uyumludur, ama cusp veya theta
   sistemi değildir. Yeni fiziksel veya AI/LLM bulgusu diye sunulmadı.

## Sayısal ve dosya denetimi

- Sekiz tam cebir/denetim grubu: beş parçalı momentler, iki denge,
  durağanlık, pozitif kazanç, genel katsayıların özel örneği,
  uniform rasyonel eşitsizlikler ve altı sertifikanın ayrı integralleri.
- Altı genişlikte 11'er nicelik, toplam 66 rasyonel aralık kaydı.
  Bunlar 66 bağımsız teorem anlamına gelmez.
- Tam üç bilinmeyenli integral sistemini çözen 12 mpmath koşusu
  (6 genişlik × 80/120 basamak); 42 karşılaştırılan değer aralıkların
  içinde, iki hassasiyet farkı <10⁻⁷⁰. Cebirsel kapalı merkez/dual
  formülleri bu çözücüde kullanılmadı.
- İlk görselde logaritmik eksenin küçük etiketleri üst üste geldi.
  Ana tikler 2,5,10,20,50 olarak ayarlanarak düzeltildi; son PNG
  ayrıca görüntülendi. İlk üretimdeki Python kaçış uyarısı ve font
  ağırlığı geri dönüşü düzeltildi. Matematiksel kayıtlar değişmedi.
- Bağlantı denetimi, düz yazıdaki bir integral sınırının Markdown
  bağlantısı gibi okunmasını yakaladı. Cümle yeniden yazıldı; integral
  koşulu veya cebirsel sonuç değişmedi.
- Paket dondurulurken üretici ve tam cebir denetçisi ayrı geçici dizinde
  yeniden çalışır; deterministik sonuçlar kayıtlarla karşılaştırılır.
  Bu tekrar mpmath koşusunu her audit'te yeniden çalıştırmaz; mpmath
  kaydının kaynak kimliği, sayıları ve aralık içermeleri kontrol edilir.
- Önceki 21 manifest ve 943 dosya girdisinin kimliği korunur.
  Masaüstü aktarımı sonrasında bütünlük ve R21 denetimi farklı bir
  çalışma dizininden tekrar çalıştırılır.

## Literatür: bilinen temel, yeni sorunun sınırı

Destek fonksiyonelimiz |v|≤A, Lip(v)≤M altında ∫qv supremumudur.
Bu iki sınırla KR normu tanımı, Lellmann–Lorenz–Schönlieb–Valkonen'in
2014 çalışmasının yazar PDF'sinde sayfa 2'de açıkça bulunur.
Normu yeniden adlandırmak veya bu tanımı kullanmak yenilik değildir.
[Yazar PDF'si](https://tuomov.iki.fi/mathematics/krtv.pdf),
[yayın DOI'si](https://doi.org/10.1137/140975528).

Geçiş noktalarına indirgeme fikri de genel olarak yeni değildir.
Aghaee–Hager'in *The Switch Point Algorithm* çalışmasının yazar özetinde,
sonlu geçişli bang-bang/singular optimal kontrol problemlerinin geçiş
noktaları üzerinden optimize edildiği belirtilir. Bu tur o çalışmanın
**özeti** incelendi; bütün teoremleriyle bir eşdeğerlik incelemesi
yapıldığı iddia edilmiyor.
[Birincil özet ve sürüm kaydı](https://arxiv.org/abs/2011.10022v5),
[yayın DOI'si](https://doi.org/10.1137/21M1393315).

Bizim şu anki somut sorumuz: sabit alt momentleri korurken, genlik ve
türev sınırını birlikte taşıyan optimumun dual/rampa denge sistemi,
yerel devamı, bütün uygun profillere karşı global optimalitesi ve
merkez/katsayı hareketi. Bu özel paketin yakın klasik spline ve optimal
kontrol sonuçlarından ne ölçüde çıktığı, bir sonraki özgünlük
incelemesinde ayrıntılı teorem karşılaştırması gerektirir. Bu kısa tarama
öncelik sertifikası değildir; R20'nin geniş taramasının yerini de tutmaz.

## Sıradaki tek araştırma adımı

Önce sonlu-geçişli teoremde uygun daha yüksek düzenlilik altında
δ(M)=δ₀+C₂/M²+C₄/M⁴+o(M⁻⁴) açılımının kurulup kurulamayacağını araştır.
Merkez ve dual hareketlerinin ilk kez hangi katsayıya girdiğini türet;
aynı tam çözülebilir örnekte bağımsız integrasyonla kontrol et. Genel
C₄ hesabı ve M⁻³'ün yokluğu bu paketin sonucu değildir.

Bu adım kapandıktan sonra sonsuz geçişli theta kuyruğu için uniform
varsayımlara dön. Araştırmanın sırası kuyruk zorluğunu gizlemeden
ilerler; mevcut R16'nın geçerli açık hata sınırı korunur.
