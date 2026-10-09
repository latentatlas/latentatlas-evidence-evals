# Stop Scope — araştırma ilerlemesi ve kanıt özeti

9 Ekim 2026 · v0.1.0 · Huseyin Buldurgan

[Ana kayıt ve inceleme yolu](README.md)

**Sorumuz:** Durdurulan görevin hangi etkilerinin sona erdiğini hangi kanıtlarla söyleyebiliriz; bunu yaparken yeni yetkilendirilmiş ve bağımsız işi nasıl koruruz?

Bu sürüm yeni bir makale değil; sprint sonrasındaki çalışmanın seçili, yeniden denetlenebilir bir kesiti. Üç tam kayıt kümesi içeriyor:

- **8 canlı geliştirme bölümü:** 3 sağlıklı bölüm doğru nihai rapor üretti. 5 dur bölümünde, kaydedilen gözlem aralığında dur sonrası araç çağrısı ve nihai dosya görülmedi. Yazarın incelediği yanıtlar durdurma onayı ve dosya durumu bildirimi içeriyordu.
- **16 programlanmış bekleme/teyit koşulu:** Mevcut işçilerin kapanmasını beklemek ile gelecekte aynı kökenden iş kabulünü engellemek ayrı ayrı izlendi. Canlı işçiyi envanterden çıkaran hatalı teyit, geç dosya oluşmasa da yakalandı.
- **8 programlanmış iptal-hedefi koşulu:** Kaynak durdurma sonrasında kayıtlı O kimliğine ek iptal 404 verdi. Aktif işleri yeniden arayan ek iptal yeni S özetini hedefledi ve 204 verdi. Önceden kabul edilmiş O yazımı her iki durumda da tamamlandı.

N, aynı konuşmada yeni insan yetkisiyle başlayan meşru iş; I ise bağımsız iş. İki matristeki 40 referans-dışı N/I dosya karşılaştırmasının tamamı kendi sağlıklı referansıyla hash düzeyinde eşleşti.

**İlerleme:** Artık durdurma isteğini, hedeflenen işi, kalan dosya etkisini ve verilen teyidin kanıtını birbirinden ayıran incelenebilir kayıtlarımız var. Programlanmış koşullar ölçüm düzeneğini sınar; canlı bölümler ise ayrı bir geliştirme gözlemidir. Canlı modelin dur emrine karşı koyduğunu gözlemlemedik.

**Açık iş:** Bu kayıtlar 286 vakanın tamamlanması değildir. Önce özgün F07 kollarını aynı kapsam ve aynı teyit anlamıyla birleştireceğiz; ardından ters gerçek etki sırası ve temiz ortam tekrarı gelecek. Alt ajan, zamanlanmış iş ve yeniden başlatma gibi mekanizmaların kendi koşulları korunuyor.

Kod, tam seçili olay kayıtları, dosya baytları ve çevrimdışı denetleyici bu klasörde. İngilizce ana not, [iddia–kanıt tablosu](CLAIMS.md) ve [yöntem/kapsam kaydı](METHODS_AND_SCOPE.md) ayrıntılı inceleme yolunu gösteriyor. Bu sürümü üretmek için yeni model çağrısı veya yeni deney yapılmadı; eski makale ve yayın etiketleri değiştirilmedi.
