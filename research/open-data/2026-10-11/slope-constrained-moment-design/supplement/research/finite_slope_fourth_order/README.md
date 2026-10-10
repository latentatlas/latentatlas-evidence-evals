# R22 — Fourth-order cost in finite-switch moment design

21 Eylül 2026. R21'in devamı. Kompakt sonlu-geçişli optimum için
dördüncü mertebe genlik katsayısı, moment düzeltmesinin katkısı ve
düzenlilik sınırı. Analitik araştırma paketi; formal ispat, dış hakemlik,
özgünlük önceliği veya theta için yeni sertifika değildir.

- [Genel ispat ve düzenlilik karşıörneği](PROOF.md).
- [İki-geçişli katsayı, negatif katsayı ve C² sınırı](EXAMPLES.md).
- [İddia/kapsam denetimi](REVIEW.md).
- [Bilimsel şekil](figures/fourth_order.png) ve [açıklaması](FIGURE_CAPTIONS.md).
- [Yaklaşık tablo](results/TABLE.md), [rasyonel aralıklar](results/certificate.json),
  [tam cebir](results/algebra.json), [ayrı integral hesabı](results/integrals.json).
- [Kapanış denetimi](audit_report.json) ve [dosya kimlikleri](manifest.json).

Ana sonuç: R21'in C² varsayımları altında M⁻³ ölçekli artık sıfıra
gider; q* sıfır komşuluklarında ayrıca C³ ise
δ=δ₀+C₂/M²+C₄/M⁴+o(M⁻⁴), açık C₄ formülüyle.
C₄ iki-geçişli örnekte 253/49152, başka düzgün bir örnekte −1/15360.
C² bir karşıörnekte M⁻⁷ᐟ² terimi vardır. Genel o-kalan açık bir uniform
hata sertifikası değildir; 16 bütçedeki çevrelemeler noktasaldır.

## Yeniden üretim

Tam araştırma arşivini koruyun; araçlar komşu R21 paketindeki dondurulmuş
rasyonel aralık ve bağımsız integral yardımcılarını kullanır. Tek başına
bu klasörü kopyalamak bütün bağımlılıkları taşımaz.

```sh
python3 /path/to/research/finite_slope_fourth_order/audit_snapshot.py
```

Standart kütüphane yeterlidir. Bu denetim önceki dosyaları korunduğu
halleriyle doğrular; rasyonel üretim ve tam cebiri geçici dizinde yeniden
yapar; kayıtlı sayısal karşılaştırmaları kontrol eder. Analitik teoremi
otomatik olarak ispatladığı veya her audit'te 32 quadrature koşusunu
tekrarladığı iddia edilmez.

Yeni, var olmayan çıktı yollarında taze hesaplar:

```sh
python3 /path/to/research/finite_slope_fourth_order/check_fourth_order.py --output /tmp/r22-algebra-new.json
python3 /path/to/research/finite_slope_fourth_order/certify_fourth_order.py --output /tmp/r22-certificate-new.json
python3 /path/to/research/finite_slope_fourth_order/crosscheck_integrals.py --certificate /tmp/r22-certificate-new.json --output /tmp/r22-integrals-new.json
python3 /path/to/research/finite_slope_fourth_order/plot_results.py --outdir /tmp/r22-figure-new
```

İlk iki işlem yalnız standart Python kütüphanesiyle çalışır. İntegral
karşılaştırması mpmath, çizim mpmath/Matplotlib gerektirir. Sürümler
[runtime.json](runtime.json) ve [requirements.txt](requirements.txt)
içindedir. Çizici kayıtlı sertifikayı işaret noktaları için okur.
Araçlar kayıtlı çıktıları sessizce ezmez; donmuş paket değiştirilmez.
`--freeze` kapanışta tek seferlik geliştirici işlemidir.

R01–R21 ve mevcut makale sürümleri korunmuştur. Sonraki araştırma,
sonsuz geçişli theta kuyruğu için uniform geçiş/kalan koşullarıdır.
Kamuya yayın veya dergiye gönderim yapılmadı.
