# R20 — Özgünlük değerlendirmesi ve derinleştirme kararı

21 Eylül 2026. Bu tur 29 ek arama sorgusu kullanıldı; daha önceki
R17/R18 karşılaştırmasına üç birincil çalışma eklendi. Hille–Theewis
çalışmalarının hem preprintleri hem yayımlanmış metinlerindeki ilgili
teoremler okundu. Kaynak sürümleri ve indirilen dosya kimlikleri
[sources.json](sources.json), sorgular [SEARCH_LOG.md](SEARCH_LOG.md)
içindedir. Bir aramada eşdeğer teorem bulunmaması, yokluk kanıtı değildir.

**Karar:** Genel baş katsayı + tam moment koruması + sonsuz geçişli
doğrulanmış örnek + açık uniform hata birleşimi savunulabilir bir katkı
adayı olarak kalıyor. “Özgünlüğü kesinleşti” veya “yayın garantilendi”
diyemiyoruz. Normu tanımlamak, dualiteyi yazmak, rampalar çizmek veya
yalnız M⁻² üssünü bulmak yeterli özgünlük gerekçesi olmayacaktır.

## 1. Ek kaynakların somut karşılaştırması

**L14 — Hille–Theewis (2023), J. Approx. Theory 294, 105947.**
[Yayımlanmış makale](https://doi.org/10.1016/j.jat.2023.105947),
[kurumsal tam metin](https://repository.tudelft.nl/file/File_ff6818b8-cf87-43a3-9c6e-47eec4824c97).
Okunan odak: tanım, Theorem 2.1, Theorem 3.1 ve ispatları; basılı
s.6 ve s.9–10, kapaklı PDF s.7 ve s.10–11. İlk teorem bir ölçü sonlu
pozitif atomik olduğunda norm hesabını sonlu parametrelere indirir;
ikincisi tek atoma uzaklık için açık optimum verir. Sürekli işaretli
artık ailemizdeki tam momentli M→∞ katsayısı bu ifadelerde yoktur.
Atomik yaklaştırmadan aynı katsayıyı çıkarmak ayrıca limitlerin ve
ızgara hatasının kontrolünü gerektirir.

**L15 — Hille–Theewis (2024), J. Math. Anal. Appl. 536, 128200.**
[Yayımlanmış makale](https://doi.org/10.1016/j.jmaa.2024.128200),
[kurumsal tam metin](https://repository.tudelft.nl/file/File_b2c44320-36ca-446f-a6b8-667d537402c1).
Okunan odak: maksimum/toplam norm tanımları; Theorem 5.1 ve
Corollary 5.1, basılı s.18 / kapaklı PDF s.19. Sonuçlar ekstrem test
fonksiyonlarının norm belirleyen yoğun altkümelerini kurar. Bunlar
yardımcı destek normumuzun yapısını açıklar. Ek moment eşitliklerini
ve katsayı asimptotiğini kendiliğinden vermez. Bu yüzden birim topun
ekstrem noktalarını yeni bir buluş gibi sunmuyoruz.

**L16 — Wachsmuth–Walter, arXiv:2403.12001v1 (2024).**
[Birincil metin](https://arxiv.org/pdf/2403.12001v1).
Okunan odak: problem (P), giriş, Theorem 5.17 ve Corollary 5.18,
s.1–3 ve s.14–15. Sonuç, L(Ku)+α∥u∥_M türü ölçü optimizasyonunda
seyrek çözüm, dual eğrilik ve bounded-Lipschitz normunda yerel
kuadratik büyüme arasındaki eşdeğerlikleri verir. Bizde değişen parametre
ayrı bir sert eğim sınırıdır ve amaç genliği azaltmaktır. Bu nedenle
“kuadratik” sözcüğünden bizim C* formülüne doğrudan geçilemez.
Bu çalışmanın daha sonraki sürümlerini/yayın durumunu denetlediğimiz
iddia edilmiyor; karşılaştırma belirtilen v1 sonucuyla sınırlıdır.

## 2. Bilinen teoremlerden doğrudan çıkıyor mu?

Karşılaştırmayı yalnız başlık/anahtar kelime düzeyinde yapmadık.
Kendi formülümüzü standart norma şu şekilde çeviriyoruz:

\[
H(A,M;\mu)=A\|\mu\|^*_{\mathrm{FM},\,(M/A)d},\qquad
V(A,M)=\inf_b H(A,M;(q_m-\sum b_jq_j)du).
\]

İlk eşitlik bilinen normun ölçeklemesidir. İkincisi klasik minimax ve
moment dualitesidir. Önceki [R18 eşlemesi](../slope_equivalence_review/EQUIVALENCE_MAP.md)
Lellmann vd.'nin iki parametreli KR normuyla tam karşılığı verir;
bu tur yalnız adı değişmiş bir problem olasılığını ayrıca sınadı.

Ancak bu eşitlikler tek başına şu dört işi bitirmez:

1. Artık yoğunluğun her basit geçişindeki kaybın tam katsayısını bulmak.
2. Bütün momentleri tam koruyan bir üst tanığı aynı katsayıda kurmak.
3. Sonsuz geçişlerde toplam ve parametre limitlerini haklı kılmak.
4. Belli bir örnekte, yuvarlama ve sonsuz kuyruk dahil, bütün büyük M
   için sayısal kalan sınırı üretmek.

R19/R20 bu dört adımı kendi ispatıyla tamamlıyor. İncelenen yakın
teorem ifadeleri bu zincirin tamamını doğrudan vermedi. Bununla birlikte,
norm asimptotikleri ve optimal kontrol literatüründe uygun uniform bir
destek-fonksiyon teoremi bulunursa genel sonucumuz onun bir uygulaması
olabilir. Bu ihtimal kapanmış değildir; dış uzman incelemesinin en
önemli sorusu budur.

## 3. Katkının ağırlığına dürüst bakış

| Parça | Bugünkü konumu | Yayın savunusundaki rolü |
|---|---|---|
| L¹/L∞ dualite, Sion, Gram düzeltmesi, kontraksiyon | Bilinen araçlar | Doğru atıf ve açık kullanım gerekir. |
| Tek basit geçişte M⁻² ölçeği | Yerel Taylor/rampa mekanizması | Tek başına güçlü yenilik iddiası taşımamalı. |
| Tam momentli genel C* formülü | Koşullu katkı adayı | En yakın genel teoremle bağımsız eşdeğerlik incelemesi gerekli. |
| Sonsuz geçişli theta uygulaması ve açık kalan | Somut rigoröz uygulama | Yeniden üretilebilir hesap ve analitik kuyruk birlikte değer taşır. |
| Sonlu M'de tam optimum / sonraki katsayı | Açık araştırma sorusu | Çözülürse mevcut sonuçtan daha ileri bir yapı açıklaması sağlar. |

Çok sayıda basamak üretmek, teknik dosya sayısı veya hesap süresi katkının
bilimsel önemini belirlemez. Özel ailede kalmak da tek başına zayıflık
değildir: ailenin genel mekanizmayı sınaması, zor bir sonsuz-toplam
durumunu çözmesi ve başka sonuçlardan ayrılan açık bir önerme vermesi
gerekir. Mevcut metinde bu yönde gerçek içerik var; önem/öncelik kararı
için dış değerlendirme hâlâ değerlidir.

## 4. Seçilen tek derinleştirme

Sonlu eğimde **gerçek optimum geçiş merkezleri ve dual katsayıların
birlikte hareketi** üzerinde çalışmayı seçiyoruz. Bu turdaki
[başlangıç notu](NEXT_QUESTION.md), sabit artık için dengeli geçiş
koşulunu ispatlar ve sıfıra merkezlenen rampanın genel olarak tam optimum
olmadığına dört tam kesir örneği verir. Bu yardımcı argüman klasik
optimalite yöntemine dayanır; kendisine yeni literatür önceliği atfedilmedi.

İlk amaç sonlu sayıda geçişte momentli optimumu karakterize etmek.
Ardından, gerekli yüksek düzenlilik açıkça sağlanırsa M⁻⁴ düzeyinde
bir sonraki terim incelenebilir. Theta'nın sonsuz kuyruğuna geçiş ayrı
bir adımdır. Şu an M⁻⁴ yasası, yeni theta sabiti veya cusp eğrisi boyunca
uniform sonuç ilan edilmiyor.
