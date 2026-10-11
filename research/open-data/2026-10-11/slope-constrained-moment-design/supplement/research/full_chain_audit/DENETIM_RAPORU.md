# R01–R12 tam zincir denetimi

21 Eylül 2026, Europe/Istanbul. Kullanıcı bu turda yeni araştırma
eklenmemesini, mevcut bulgu, hesap ve çıkarımların tek tek denetlenmesini
istedi. Bu rapor o denetimi kapatır; yeni bir R13 matematik paketi değildir.

**Sonuç:** İncelenen R01–R12 sonuçlarından birini geri çekmeyi veya
yayımlanmış sayısal sınırlarını değiştirmeyi gerektiren matematiksel,
sayısal ya da mantıksal hata bu denetimde bulunmadı. Mevcut iddialar,
kendi varsayımları ve alanları içinde yeniden kontrol edildi. Bu ifade
mutlak hatasızlık ispatı, dış hakem kararı veya formal doğrulama anlamına
gelmez. Kalan güven sınırları aşağıda açıkça kayıtlıdır.

## 1. Kapsam ve koruma

Denetim R01–R12'nin ispatlarını, Türkçe araştırma notlarını, kritik hesap
kodlarını, güncel sertifika üreticilerini, bütün güncel check/crosscheck/test
giriş noktalarını ve bunların sonuç/iddia bağlarını kapsar. Yeni makale için
hazırlanan mevcut teorem parçalarının kapsamı da ispatlarla karşılaştırıldı.
Başarısız tarihsel uygulamalar aktif sertifika üreticisi sayılmadı.

Başlangıçtaki `buldurgan-A3-cusp-dBN.tex` ve eski çalışma arşivi, daha önce
kararlaştırıldığı üzere, yeni araştırmanın kanıt kaynağı veya kullanılacak
makale taslağı değildir. Bu rapor o eski metnin bütün hatalarını giderdiğini
iddia etmez. Onun dosyaları korundu.

12 paketin **437 dondurulmuş bilimsel dosyası ve 12 manifesti**, toplam
449 dosya, önceki içerikleriyle aynı kaldı. Özgün arşivin 40 dosyası da
korundu. Tekrar koşuları geçici kopyalarda yapıldı; geçici kopyalar temizlendi.
Yeni kayıtlar bu klasördedir. Yalnızca güncel kapsam belgesi ve çalışma
defterine tarihli denetim özeti eklendi.

## 2. Fiilen yapılan kontroller

| Denetim katmanı | Sonuç | Ne gösterir / neyi göstermez? |
|---|---|---|
| Güncel mevcut denetçi, regresyon ve sayısal çapraz kontrol programları | 34/34 geçti | Sertifika eşitsizlikleri ve kayıtlı çapraz kontroller yeniden çalıştı. Hepsi aynı tür kanıt değildir. |
| Güncel sertifika/moment üretim koşuları | 27/27 geçti | Veri üretimi yeniden yapıldı; yalnız önceki `passed` alanı okunmadı. |
| R01'in ek 130 basamak, 20 theta terimi, 16 panel koşusu | 1/1 geçti | Daha hassas kök kutusu 110 basamak kutusunun içinde. Toplam mevcut koşu 62. |
| Yeniden üretilen sayılar | 85 JSON karşılaştırmasında 201.023 tam ikili aralık kaydı aynı | Süre ve hash gibi metadata dışarıda tutuldu. Bu sayı 201.023 bağımsız teorem veya bağımsız deney demek değildir. |
| Kritik cebir | 32/32 tam rasyonel polinom kimliği geçti | Katsayı/işaret/determinant ve fold taşıma özdeşlikleri; rastgele nokta testi değil. |
| R12 işaret ve majorant girişleri | 28 kök kutusu, 113 işaret yaprağı; 2304 hücre-sıra ve 9 kuyruk zarfı geçti | Eski kontrol modülleri içe aktarılmadan farklı ifadelerle yeniden değerlendirildi. |
| R12 dokuz kesikli moment | 297 rigoröz integral; eski kapsamaların içinde | 140 basamak, 12 theta terimi, [1,2] bölümü dahil farklı integral bölümlenmesi. |
| R12 dokuz yumuşatma moment etkisi | Ölçeklenmiş değişkende 1764 rigoröz geçiş integrali; eski hata bütçelerinin içinde | Önceki analitik N Mⱼη² sınırına ek bir kontrol; yeni bilimsel sınır yayımlanmadı. |
| Analitik adımlar ve kapsam | 83 maddelik iddia/ara-adım envanteri | Hangi sonucun hangi varsayıma bağlı olduğu ayrıldı; dış uzman onayı yerine geçmez. |

Ana kanıt kayıtları:
[34 koşu](replays/status.json), [27 üretim](regenerations/status.json),
[ana karşılaştırma](regeneration_comparison.json),
[ek hassasiyet](precision_comparison.json),
[tam cebir](symbolic_checks.json),
[R12 giriş denetimi](threshold_input_audit.json).

Üretimler arasında R08'in önceki moment önbelleği kopyada kaldırıldı ve
4002 moment yeniden hesaplandı. R02'nin merkez türev önbelleği de kopyada
yenilendi. R03'ün 58 tüpü ve R08'in 232 hücresi tam olarak yeniden üretildi.
Her iş önceki dondurulmuş girdi kimliklerini kullandı; bu tur üretilen
sayısal veriler ayrıca bu girdilerle karşılaştırıldı. Yeni metadata hashleri
eski girdilere aitmiş gibi sessizce geçirilmedi.

## 3. Araştırma zincirinin durumu

| Bölüm | Korunan sonuç |
|---|---|
| R01–R03 | İki doğrulanmış cusp, yerel bir/üç kök ayrımı ve onları aynı dalda bağlayan parametrik sertifika. |
| R04–R05 | Cusp boyunca ortak sonlu fold geometrisi; hem başterimin hem sonlu genişliğin ayrı gerekçelerle kontrolü; sıkı iç içelik. |
| R06–R08 | Standart kuramla kapsam ayrımı, küçük genel perturbasyona dayanıklılık ve özel yönde iki parametreli cusp yüzeyi. |
| R09 | Q'yu tam sabit tutan açıklık tasarımı; belirtilen 16 mod/katsayı bütçesinde başlangıç hızı optimumu; değiştirilmiş pozitif çekirdekte tam dörtlü sıfır. |
| R10 | O belirli dörtlü-sıfır çekirdeğinin açık sonlu kutusunda 0/2/4 kök teoremi, cusp kolları ve doğrulanmış kesit. |
| R11 | Pozitif yoğunluk ve moment koşulları altında genel tasarım mekanizması; minimum L∞ maliyetinin L¹ uzaklık formülü. |
| R12 | Sabit Q'da minimum genlik maliyetine çok dar alt/üst sınır; ona yaklaşan düzgün pozitif ve rank-üç tasarım; sürekli sınıfta minimumun elde edilmeyişi. |

Tek tek iddialar, gerekçeler, koşu bağlantıları ve sınırlar
[83 maddelik envanterde](IDDIA_ENVANTERI.md) bulunur. Analitik kontrolün
özellikle hassas noktaları [ayrı notta](ANALITIK_DENETIM.md) açıklanır.

Son eşik sonucu değişmedi:

\[
0.00000000091787079603827<\delta_*
<0.00000000091787079608363.
\]

Gösterilen uçlar L,U için (U−L)/L<5×10⁻¹¹. Alt sınır bütün uygun sınırlı
gerçek h'lere; üst sınır tanımlanmış belirli uygun düzgün tasarıma dayanır.
Q'nun tam konumu, ilk dört momentin tam denklemleriyle korunur. Bu,
optimizasyon yazılımının başarılı durması veya küçük sayısal artık sonucu
değildir. Düzgün sınıfta kesin minimum elde edildiği iddia edilmez.

## 4. Bu turda yakalanan ve düzeltilen kontrol sorunu

Yeni yazılan R12 giriş denetiminin ilk sürümünde, alternatif interval
üst sınırının eski üst sınırdan mutlaka küçük olması istendi. Hücre 18,
türev sırası 2'de alternatif sınır yaklaşık 5,73705×10⁻⁹⁷ daha büyüktü.
Bu, gerçek fonksiyonun eski sınırı aştığını göstermez: iki geçerli üst
sınırın farklı genişlikte olması mümkündür.

Neden: `λ*r*r` biçimi aralık katsayısını iki kez çarparak yarıçapı
yeniden dışa yuvarlıyor; `λ*(r**2)` tam monomiyi önce hesaplayıp katsayıyla
bir kez çarpıyor. Zarf karşılaştırması ikinci biçimle yapıldığında bütün
2304 kontrol geçti. Tolerans eklenmedi, başarısız hücre atlanmadı,
matematiksel sınır gevşetilmedi. İlk sürüm ve başarısız log saklandı.

[Tanılama ve çözüm kaydı](diagnostics/threshold_input_envelope_comparison.json).
Bu, mevcut R12 araştırma sertifikasında bulunan bir hata değildir;
bu turdaki ek kontrol kodunun gereğinden güçlü karşılaştırmasının
düzeltilmesidir. İki durumu aynı hata sayımında birleştirmiyoruz.

## 5. İddialarda korunması gereken sınırlar

1. **Belirli dal ile bütün uzay ayrımı:** R03'te D₃'ün sıfır olmaması
   yalnızca doğrulanmış cusp yayı üzerinde dörtlü sıfırı dışlar.
2. **Başterim ile sonlu geometri ayrımı:** C′ işareti ve sonlu W'nin
   hareketi ayrı iddialardır. R05'in açık kalan sınırları bu farkı kapatır.
3. **Çekirdek kimliği:** R07/R08 yönü, R09/R10 yönü, R11 adayı ve R12
   yakın-minimum adayı aynı çekirdek değildir. R10'un sonlu kutusu ve
   kök haritası R12'ye taşınmış değildir.
4. **Bütçe ve hedef:** R09'un katsayı ℓ¹ bütçeli 16 mod optimumu ile
   R11/R12'nin bütün sınırlı fonksiyonlardaki L∞ genlik problemi farklıdır.
   Birbirleriyle çelişmezler.
5. **Genlik ile türev:** R12 yaklaşık 9,1787×10⁻¹⁰ genlik maliyeti verir.
   Türev/frekans bütçesi yoktur; yumuşatma geçişi η=2⁻³² kadar dardır.
   Bu sayı fiziksel gürültü toleransı veya bütün normlarda dayanıklılık
   olarak sunulamaz.
6. **Harita ile tam sınıflama:** R10'daki 2804 renkli hücre sertifikalıdır;
   780 gri hücre çözümlenmemiştir. Gri hücrelerin hepsi ayırıcı üzerinde
   sayılmaz. Ortak analitik kök ölçütü ile ağ sınıflaması farklı şeylerdir.
7. **Tarihsel notlar:** R09'un sonunda henüz yapılmadığı söylenen R10
   çalışması ve R11'in geniş eşik aralığı, kendi tarihleri için doğrudur.
   Güncel durumu R12 ve bu denetim gösterir. R12'nin eski notunda dar
   geçişlerin doğrudan integre edilmediği yazması da tarihsel olarak doğru;
   ölçeklenmiş geçiş kontrolü yalnız bu denetimde eklendi.

Bu sınırlar mevcut metinlerde esas olarak doğru tutulmuştu. Denetim
envanterinde görünür kılındılar; ispatlanmış bir sonuç geri alınmadı.

## 6. Güven düzeyi ve açık kalanlar

**confirmed — yeniden üretilebilirlik ve kayıt bütünlüğü:** Yukarıdaki
koşular geçti, 201.023 aralık kaydı önceki sayılarla tam aynı, dondurulmuş
dosyalar değişmedi. Bu sayılar tek başlarına bir matematiksel ispatın
doğruluğunu garanti etmez; bir yanlış program da tekrarlanabilir.

**İç denetimde desteklenen matematik:** Analitik ispat adımları okundu;
kritik cebir ayrı yöntemle sınandı; rasyonel denetçiler yeniden çalıştı;
özellikle hassas R12 girişleri farklı ifadeler ve bölümlenmeyle hesaplandı.
Bu kapsam içinde bilinen açık bir matematiksel hata kalmadı.

**needs_review — dış matematiksel inceleme:** Genel moment/dualite ispatı,
global kuyruk majorantları, interval integrasyonla analitik ispat arasındaki
sözleşme ve sonlu geometri zinciri başka bir uzman tarafından incelenmiş
değil. Bu tur bağımsız bir araştırmacı veya hakem raporu üretmedi.

Ortak güven tabanı Python, python-flint/FLINT/Arb, integral callback'lerinin
analitik koşulları ve elle yazılan ispatlardır. Yeni cebir denetimi mevcut
formül kodlarını içe almaz, fakat yine FLINT'in tam rasyonel polinom
aritmetiğini kullanır. Yeni R12 kontrolü mevcut hesap modüllerini içe
almaz; yine Arb integrasyonu kullanır ve ayrı yeniden denetlenmiş Q,
moment-düzeltme matrisi ile kök-taşıma majorantlarına dayanır. Dolayısıyla
uçtan uca tamamen bağımsız bir yazılım temeli veya formal ispat yoktur.

**uncertain — öncelik ve yayın kararı:** Cusp normal biçimi, moment
sağ tersi, L¹/L∞ dualitesi ve yumuşatma klasik araçlardır. Özel nicel
birleşimin literatürdeki önceliği ve dergi kabulü bu denetimin sonucu
değildir. [Sınırlı birincil kaynak kontrolü](KAYNAK_DENETIMI.md) ayrıca kayıtlı.

Yeni makale henüz yazılmadı. TeX parçaları bütün bir makale olarak
derlenmedi. Bu tur yeni şekil, fiziksel model, daha yüksek tekillik,
yeni norm bütçesi veya yeni bilimsel iddia eklenmedi.
