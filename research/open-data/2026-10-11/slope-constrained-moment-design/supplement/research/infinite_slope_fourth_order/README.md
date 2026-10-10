# R23 — Infinite-switch fourth-order moment design

21 Eylül 2026. R22'nin sonlu-geçişli değer açılımı, ağırlıklı toplam
koşullarıyla sonsuz geçişlere taşındı. Sabit theta cusp noktasında bu
koşullar analitik olarak doğrulandı. Bu, theta C₄'ünün sayısal değerini
sertifikalandırmak veya açık sonlu-M hata payı vermek değildir.

- [Genel ispat](PROOF.md): destek alt sınırı, sonlu merkezlerle moment
  onarımı, sonsuz Taylor toplamlarının kontrolü ve eşleşen üst sınır.
- [Theta uygulaması](THETA.md): kuyruk koşulları ve ortak ağırlıksız
  merkez-kayması varsayımının neden uygun olmadığı.
- [Sonsuz geçişli bağımsız örnek](EXAMPLE.md), [tablo](results/TABLE.md),
  [üç panelli grafik](figures/infinite_switches.png).
- [İddia ve kapsam denetimi](REVIEW.md), [kaynak erişimi](SEARCH_LOG.md),
  [yakalanan geliştirme hataları](results/DEVELOPMENT_NOTES.md).
- [Arb çıktısı](results/certificate.json), [exact cebir](results/algebra.json),
  [bağımsız integraller](results/integrals.json), [kapanış](audit_report.json).

Ana sonuç, açık yeter koşullar altında
δ(M)=δ₀+C₂/M²+C₄/M⁴+o(M⁻⁴). Theta için C₄ yakınsak seri/matris
formülüyle tanımlı; sayısal çevreleme ve etkin kalan sınırı sonraki işler.
Sonsuz geçişlerin her birindeki merkez katsayısı sınırlı olmak zorunda
değil: küçük ağırlıklarla çarpılmış toplamları kontrol etmek yeterli.

Bağımsız e^{-u}cos(πu) örneğinde C₄≈0.00634907424165.
Altı örtük bütçe Arb ile çevrelendi; 80/120 basamakta ayrı parça-integral
çözümü 54 örnek değeri ve 78 katsayı karşılaştırmasını geçti. Bu sayılar
theta ailesine ait değildir. Genel analitik ispat formal ispat veya
dış hakem doğrulaması olarak sunulmaz.

## Yeniden üretim

Araçlar yolları kendi konumlarına göre çözer; tüm araştırma ağacını koruyun.
R23 cebir aracı, dondurulmuş R22 cebir yardımcısını kullanır.
Python assertion'ları açık tutulmalıdır; `python -O` kullanmayın.

Standart kütüphane ile kimlik, kayıtlı aritmetik ve taze exact-cebir denetimi:

```sh
python3 /path/to/research/infinite_slope_fourth_order/audit_snapshot.py
```

Arb üreticisini de başka geçici dizinde taze çalıştırıp bayt eşitliğini sınamak:

```sh
python3 /path/to/research/infinite_slope_fourth_order/audit_snapshot.py --with-arb
```

İkinci komut `python-flint` gerektirir. Bağımsız sayısal integraller audit
tarafından her seferinde yeniden çözülmez; kayıtlı karşılaştırmaları denetlenir.
Taze hesaplar için yeni, henüz var olmayan çıktı yolları verin:

```sh
python3 /path/to/research/infinite_slope_fourth_order/check_algebra.py --output /tmp/r23-algebra-new.json
python3 /path/to/research/infinite_slope_fourth_order/certify_example.py --output /tmp/r23-certificate-new.json
python3 /path/to/research/infinite_slope_fourth_order/crosscheck_integrals.py --certificate /tmp/r23-certificate-new.json --output /tmp/r23-integrals-new.json
python3 /path/to/research/infinite_slope_fourth_order/plot_results.py --outdir /tmp/r23-figure-new
```

Exact cebir yalnız standart kütüphane; sertifika python-flint; ayrı integraller
mpmath; çizim mpmath/NumPy/Matplotlib kullanır. Sürümler `runtime.json` ve
`requirements.txt` içindedir. Çizici kayıtlı sertifikayı örnek işaretleri için
okur. `--freeze` kapanışta bir kez kullanılan geliştirici işlemidir.

R01–R22 ve mevcut makale sürümleri korunmuştur. Sonraki adım, exact theta
b* üzerinde G, B, R ve kuyruklarını sayısal çevreleyerek C₄'ün değerini ve
işaretini araştırmaktır. Kamuya yayın veya dergiye gönderim yapılmadı.
