# R24 — Certified positive theta fourth-order coefficient

21 Eylül 2026. R23'te varlığı ve formülü bulunan dördüncü mertebe
katsayısı, şimdi exact theta cusp Q ve exact dual b* için sayısal olarak
çevrelendi:

    2.49203004×10⁻³⁹ < C₄,θ < 2.49203006×10⁻³⁹.

İşaret pozitiftir. Bu, yeterince büyük M'de δ₀+C₂/M² yaklaşımının
minimum genliği eksik tahmin ettiğini gösterir. Bu cümledeki “yeterince
büyük” için sayısal bir başlangıç bütçesi henüz belirlenmedi.

- [İspat, kuyruklar ve kapsam](PROOF.md).
- [İddia/kanıt denetimi](REVIEW.md).
- [Katsayı ve kuyruk tablosu](results/TABLE.md).
- [İki panelli bilimsel şekil](figures/theta_fourth_order.png) ve
  [açıklaması](FIGURE_CAPTIONS.md).
- [Arb sertifikası](results/certificate.json),
  [bağımsız rasyonel yeniden hesap](results/rational_check.json),
  [doğrudan türev/integral kontrolü](results/direct_check.json),
  [exact cebir](results/algebra.json).
- [Kapanış denetimi](audit_report.json), [dosya kimlikleri](manifest.json).

Hesap 28 sonlu kökü, bütün sonsuz kök kuyruğunu, theta serisinin
atılan terimlerini, parametre belirsizliğini ve Gram matrisinin çözüm
hatasını içerir. Daha önceki gradient/kuvvetli konvekslik kanıtı dual
kutuyu daraltır; merkez nokta exact optimizer gibi kullanılmaz.

R23'ün analitik teoremi ve R12/R15'in exact nesne sertifikaları bu
sonucun açık bağımlılıklarıdır. Bağımsız mpmath hesabı merkez parametrelerde
yapılır ve tanısal kontroldür. Şeklin sağ paneli yalnız bilinen iki
asimptotik terimin oranını gösterir; bir sonlu-M hata sertifikası değildir.

## Yeniden üretim

Tam araştırma ağacını koruyun; R24 cebir ve rasyonel araçları dondurulmuş
R21/R22 yardımcılarına bağlıdır. Python assertion'ları açık olmalıdır.

Standart kütüphane ile dosya kimlikleri, taze exact cebir ve taze rasyonel
yeniden hesap:

```sh
python3 /path/to/research/theta_fourth_order/audit_snapshot.py
```

Arb üreticisini de taze çalıştırmak için (`python-flint` gerekir):

```sh
python3 /path/to/research/theta_fourth_order/audit_snapshot.py --with-arb
```

Denetçi kayıtlı doğrudan integral karşılaştırmalarını kontrol eder;
mpmath kök/türev/quadrature hesabını her denetimde yeniden koşturmaz.
Taze hesaplar için henüz mevcut olmayan yollar verin:

```sh
python3 /path/to/research/theta_fourth_order/check_algebra.py --output /tmp/r24-algebra-new.json
python3 /path/to/research/theta_fourth_order/certify_coefficient.py --output /tmp/r24-certificate-new.json
python3 /path/to/research/theta_fourth_order/check_certificate.py --certificate /tmp/r24-certificate-new.json --output /tmp/r24-rational-new.json
python3 /path/to/research/theta_fourth_order/crosscheck_direct.py --certificate /tmp/r24-certificate-new.json --output /tmp/r24-direct-new.json
python3 /path/to/research/theta_fourth_order/plot_results.py --outdir /tmp/r24-figure-new
```

Sürümler `runtime.json` ve `requirements.txt` içindedir. Çizici işaret ve
aralıklar için kayıtlı sertifikayı okur. `--freeze` kapanışta bir kez
kullanılan geliştirici işlemidir. Araçlar kayıtlı çıktıları sessizce ezmez.

Önceki R01–R23 paketleri ve makale dosyaları korundu. Sonraki soru etkin
dördüncü mertebe kalan sınırıdır. Dış hakem incelemesi, formal ispat ve
özgünlük önceliği bu hesap denetimleriyle elde edilmiş sayılmaz.
