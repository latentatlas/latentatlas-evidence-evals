# R18 — Ölçek, norm ve kaynak katsayısı kontrolü

21 Eylül 2026. Amaç yeni sonuç üretmek değil, eşdeğer problem ararken
aynı sembole farklı anlam yüklenmesini önlemek. Bütün hesaplar küçük
tanı örnekleri; R15/R16 sertifikaları yeniden hesaplanmadı/değiştirilmedi.

## Bizim sabit sözleşmemiz

H(A,M;μ)=sup ∫g dμ, ∥g∥∞≤A, Lip(g)≤M.
Toplam varyasyon ∥μ∥TV=|μ|(X); olasılık uzaklığındaki 1/2 çarpanı yok.
İki ayrı sınırın birim topu max(∥g∥∞,Lip(g))≤1 ile verilir; toplam norm
ile değiştirilmez. Ölçek dönüşümü H=A H(1,M/A)=M H(A/M,1).

İki işaretli birim atom, aralarındaki uzaklık d>0 için

    H(A,M;δ_d−δ_0)=min(2A,Md).

Üst sınır doğrudan iki kısıttan gelir; aradaki farkı min(2A,Md)
olan, ortası sıfır iki değer seçilerek erişilir. Tek pozitif atom için
H(A,M;δ_0)=A. Bu iki basit örnek 2 ve 1/2 hatalarını yakalar.

## L11'deki görünür katsayı tutarsızlığı

Heinemann–Klatt–Munk'ın [arXiv v3](https://arxiv.org/pdf/2112.03581),
s.7, Teorem 2.2(ii) satırı, TV=½Σ|μ−ν| tanımıyla birlikte
KR_{p,C}^p=(C^p/2)TV yazıyor. Aynı ifade
[yayıncı HTML'sinde](https://doi.org/10.1007/s00245-022-09911-x) de var.
Preprint sayfası PNG olarak render edilip gözle incelendi; yalnız OCR
çıktısına dayanılmadı. Yayıncının PDF aynası yerel istekte 403 döndü;
son dergi PDF'sinin görsel doğrulaması yapıldığı iddia edilmiyor.

Bu satır, aynı metnin (2) tanımı ve p=1 dualiyle tutarlı değil:
μ=δ_0, ν=0, p=1, C=2 seçilirse tek taşıma planı sıfırdır ve (2)'den
UOT=1 gelir. |g|≤C/2 duali de 1 verir; söz konusu TV satırı 1/2 verir.
Dolayısıyla bu sürümdeki TV çarpanı doğrudan aktarılmadı. Kullanılan
eşleme, birbiriyle uyumlu tanım ve dual üzerinden C=2A/M'dir.
Bu tespit makalenin diğer sonuçları hakkında toplu bir hüküm değildir.

## Denetçinin yaptığı işler

[check_normalization.py](check_normalization.py), standart Python
`Fraction` ile iki değişkenli doğrusal problemin bütün köşelerini
hesaplar; toleranslı sayısal çözücü kullanmaz. Farklı genlik/eğim/mesafe
durumlarında yukarıdaki atom formülünü ve iki ölçeklemeyi karşılaştırır.
Ek moment g(0)=0 örneği, sınırsız dual optimumunu sonlu M'de sabit
tutmanın doğru olmadığını gösterir. Sürekli doğrusal yoğunluk örneğinin
integrali, atomik doygunluk ile aynı şey olmadığını denetler.

[Sonuç dosyası](results/normalization_checks.json) bütün rasyonel
değerleri ve kod hash'ini içerir. Bunlar kaynak yorumu, minimax ispatı
veya özgünlük değerlendirmesi için otomatik doğruluk belgesi değildir.
