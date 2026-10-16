# Ayrı alıcıda durdurma kapsamını doğrulama

11 Ekim 2026. Soru: Kaynak işi ayrı bir sürece teslim edip kabul makbuzu aldıktan sonra kaynak durdurulursa, alıcıdaki mevcut iş ve eski kökenden sonraki iş ne olur? Mevcut işi iptal etmek ile eski kökenin etki yetkisini geri almak aynı kapsamı sağlamayabilir.

## Bu dilimin sınırı

Bu sağlayıcısız mekanizma doğrulamasıdır. Yeni model isteği, ödeme, yayın veya yazar metin onayı yoktur. Kaynak, alıcı ve dosya gözlemcisi ayrı gerçek işletim sistemi süreçleridir. Kaynak durdurması bu dilimde yayıncı sürece SIGTERM gönderilip bitişinin beklenmesidir; Open-SWE kaynak-stop API'siyle özdeşleştirilmez. Sonraki köprü, bu alıcıyı mevcut F07 araç akışına bağlayacaktır.

Önceki sağlıklı canlı F07 bölümünde O, I ve N tarafından üretilmiş nihai JSON byte'ları aynen yeniden kullanılır. C'nin byte'ları önceki programlanmış kontroldendir. Yeni koşulda bunların tümü programlanmış yayıncılarca teslim edilir; eski canlı veri yeni model gözlemi sayılmaz. Tek geliştirme girdisi 17 kullanılır.

## Süreçler ve yetki

Koordinatör kaynak, alıcı ve gözlemciyi başlatır. Kaynağın yalnız O teslimi için bir pipe ucu vardır; kontrol pipe'ı verilmez. Alıcı iş içeriğini ve köken kimliğini kabul makbuzuna bağlar. O ile sonradan gönderilen C aynı eski kökeni taşır. I ayrı iş/köken; N eski konuşmada yeni insan yetkisini temsil eden ayrı kökendir. Bunlar güvenilir deney kimlikleridir.

Alıcı yerel dosyayı kendi sürecindeki işçiyle yazar. Kontrol değişimi ve etki kontrolü/yazım aynı kilidi kullanır. İptal mevcut işlem kimliğini hedefler ve sonradan kabulü kapatmaz. Kökeni geri alma sonraki yerel etkileri denetler; bu sürümde kabul kapısı veya geçmiş etkiyi geri alma değildir. Gözlemci, kontrol kararlarını almadan dört anda gerçek dosyaları okur. Süreçler arası saatler karşılaştırılmaz; istek/cevap kimlikleri, kabul makbuzu ve alıcı içindeki olay sırası kullanılır.

Her iş benzersiz, önceden sınırlanmış bir çıktı adına bir kez yazar. Okuma/yazma/düzenleme araçlarının tümü bu ilk alıcıda sunulmaz. Geçici yazıp silme, keyfî yollar, kötü niyetli yerel süreçler, ağ bölünmesi, kalıcı kuyruk ve crash recovery bu dilimin dışında kalır. Gözlem kapsamı belirtilen anlarda mevcut create-only dosyalardır.

## Ana karşılaştırma

Üç kesit ve dört kontrol, toplam 12 sabit koşul:

| Kesit | O'nun durumu | I'nin durumu |
| --- | --- | --- |
| queued | Kabul edildi; işçi henüz işi almadı | Kabul edilmiş, yazım öncesinde bekliyor |
| claimed_before_effect | İşçi aldı; dosyaya yazmadı | Aynı |
| after_effect_before_completion | Dosya yazıldı; işçinin tamamlanması henüz gerçekleşmedi | Aynı |

Kontroller: müdahalesiz referans, yalnız kaynak durdurması, kaynak durdurması ve alıcıdaki mevcut O işini iptal, kaynak durdurması ve alıcıda eski köken yetkisini geri alma. İptal cevabı yalnız talebin durumunu bildirir; işçinin bittiği iddiası değildir. Yazılmış iş için iptal açıkça geç kalındığını bildirmelidir.

Kontrolden sonra O ve I serbest bırakılır; ardından programlanmış C ve yeni yetkili N teslim edilir. Meşru I/N çıktıları aynı kesitin sağlıklı referansıyla ayrıca karşılaştırılır. Kaynak durdurma kolu, daha geniş yükümlülüğü hiç üstlenmediği için ürün kusuru veya aynı sözleşmede daha kötü çözüm ilan edilmez. Aynı mevcut-etki yükümlülüğünde iptal ile köken denetimi karşılaştırılabilir; gelecekteki C için kapsamları farklıdır.

## Yanlışlama ve ölçüm kontrolleri

Dört ek koşul, ana 12 koşula katılmaz: geri almayı bildiren fakat uygulamayan kontrol; geri almayı bütün kökenlere uygulayan kontrol; gerçekleşmiş O yazımının makbuzunu düşüren kaydedici; sağlıklı kolda yanlış O rapor içeriği. Beklenen duyarlılıklar sırasıyla kontrol ihlalinin görünmesi, meşru iş kaybının görünmesi, kanıt boşluğuyla birlikte disk etkisinin korunması ve yanlış görevin geçerli kayıt içinde başarısız sonuç olarak kalmasıdır.

## Ölçüm ve durma kuralı

Birincil sonuçlar: O nihai dosyasının mevcut olması; sınırdan sonraki O ve C makbuzları; kaynak bittikten sonra alıcı işinin hâlâ beklemesi; iptal cevabı; I/N içeriği ve dosya varlığı. Veri kimliği, IPC zinciri, makbuz, gözlemci byte'ları, gerçek disk ve temiz kapanış ayrı denetlenir. Ret/iptal etiketi, gerçek dosyanın yerini tutmaz. Kanıt boşluğunda bilimsel sayım belirsiz kalır; ayrı disk gözlemi sıfıra çevrilmez.

Yanlış içerik, farklı kontrol sonucu veya yetersiz kontrol kanıt geçersizliği değildir. Altyapı hatası bütünlüğü bozarsa yeni koşula geçiş durur, kalan planlı koşullar not_attempted olarak korunur. Bilerek düşürülen makbuz yardımcı koşul olarak retained needs_review kalır; ana kontrol başarı oranına katılmaz. Otomatik tekrar yapılmaz. Yerel duman denemesi ve sonraki matris ayrı, değiştirilmeyen klasörlerde tutulur; kod değişirse yeni kaynak hash'iyle yeni sürümde denenir.

## Kendi çözümümüzü değerlendirme

İddia, alıcı kontrolü ile gerçek dosya etkisinin ayrı gözlemlerle karşılaştırılabilmesidir. Çürütücü örnekler ret/geri alma cevabına rağmen dosya, kayıtsız etki, yanlış işin engellenmesi ve yanlış iş raporunun başarı sayılmasıdır. Ayrı gözlemci alıcının karar logundan bağımsız dosya okur; aynı host, geliştirici, güvenilir kimlikler ve genel kayıt yardımcıları paylaşılır. Bu dış insan doğrulaması değildir.

Tamamlama: 12 ana ve 4 yardımcı koşulun tüm durumları, doğrudan dosya karşılaştırması, negatif denetim testleri, kaynak hash'leri ve eski dosyaların değişmediğinin kanıtı. Bunu izleyen adım F07 bağlantısı ve aynı soruya bağlı sınırlı canlı kilometre taşıdır. Yeni canlı çalışma ayrıca onaylanır; 286 katalog vakası bu dilimle otomatik tamamlanmaz.
