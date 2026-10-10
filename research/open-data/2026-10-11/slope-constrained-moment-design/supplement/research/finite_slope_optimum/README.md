# R21 — Finite-slope optimum with finitely many switches

21 Eylül 2026. R20'nin sıradaki sorusunun sonlu-geçişli cevabı.
Bu paket, kompakt aralıkta basit sıfırlar ve tam moment rankı altında,
yeterince büyük M için gerçek Lipschitz genlik optimumunu, tekliğini,
denge sistemini ve merkez/dual katsayı hareketini türetir. Genel teorem
analitik, iki-geçişli polinom örneği ise tam cebir ve rasyonel aralıklarla
denetlenmiştir. Dış hakemlik, formal ispat ve literatür önceliği yoktur.

- [Genel teorem ve ispat](PROOF.md).
- [İki-geçişli tam çözülen örnek](EXAMPLE.md).
- [İddia, açıklık ve kapsam denetimi](REVIEW.md).
- [Hesap tablosu](results/NUMERICAL_TABLE.md).
- [Bilimsel grafik](figures/finite_optimum.png) ve [açıklaması](FIGURE_CAPTIONS.md).
- [Rasyonel sertifika](results/certificate.json), [tam cebir](results/algebra.json),
  [ayrı integral çözümü](results/quadrature.json).
- [Denetim kaydı](audit_report.json) ve [dosya kimlikleri](manifest.json).

Sonuçların theta ailesinin sonsuz kuyruğuna aktarımı ve genel M⁻⁴
katsayısı açık kalır. Eski R01–R20 paketleri değiştirilmedi; R19/R20
makale PDF'lerine yeni sonuç eklenmedi. Kamusal yayın veya gönderim yapılmadı.

## Yeniden üretim

Kendi ortamınızdaki Python 3.12+ ile, herhangi bir çalışma dizininden:

```sh
python3 /path/to/research/finite_slope_optimum/audit_snapshot.py
```

Bu denetim standart kütüphaneyle çalışır. Önceki manifestleri ve bu
paketi kontrol eder; üretici/tam cebir hesaplarını geçici dizinde yeniden
yapar. Sayısal tanının kayıtlı sonuçlarını doğrular; bu, o tanının her
seferinde yeniden çözülmesi veya analitik teoremin otomatik ispatı değildir.

Yeni, var olmayan çıktı yollarına taze hesap üretmek için:

```sh
python3 /path/to/research/finite_slope_optimum/certify_example.py --output /tmp/r21-certificate-fresh.json
python3 /path/to/research/finite_slope_optimum/check_algebra.py --certificate /tmp/r21-certificate-fresh.json --output /tmp/r21-algebra-fresh.json
python3 /path/to/research/finite_slope_optimum/crosscheck_quadrature.py --certificate /tmp/r21-certificate-fresh.json --output /tmp/r21-quadrature-fresh.json
python3 /path/to/research/finite_slope_optimum/plot_results.py --outdir /tmp/r21-figures-fresh
```

İlk iki işlem yalnız standart kütüphaneyi kullanır. Ayrı integral
çözücüsü mpmath; görsel NumPy/Matplotlib gerektirir. Kullanılan sürümler
[runtime.json](runtime.json) ve [requirements.txt](requirements.txt)
içindedir. Çizici kayıtlı rasyonel sertifikayı işaret noktaları için okur;
son çıktıları belirtilen dizinin `figures/` ve `results/` altına yazar.

Araçlar mevcut çıktıları sessizce ezmez. `--freeze` yalnız kapanışta bir
kez kullanılan geliştirici seçeneğidir; donmuş paket üzerinde kullanılmaz.
Arşivde gerçek hesaplar ile yüksek hassasiyetli sayısal tanılar ayrı
etiketlenmiştir. SHA-256 kaydı dosya kimliğini korur; bilimsel doğruluk
veya özgünlük hükmünü bir hash'e bırakmaz.
