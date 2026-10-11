# R02 — Quartic cusp için doğrulanmış yerel bölge

Bu paket, `../cusp_verified` sonuçları üzerine eklenen yerel bir araştırma
sonucudur. Eski paket salt okunur bağımlılık olarak kullanılır ve 25 dosya
özeti başlangıçta doğrulanır. Ana sonuç ve sınırlar
[Türkçe araştırma notunda](ARASTIRMA_NOTU.md); ayrıntılı analitik gerekçe
[PROOF.md](PROOF.md) içinde.

## Sonuç

Başlangıç sertifikasındaki tam merkez çevresinde
|t−t0|≤0.003, |λ−λ0|≤10^-6, |μ−μ0|≤2×10^-9 için tek cusp, iki fold kolu
ve bir/üç gerçek kök bölgeleri sınıflandırıldı. Kök sayıları yalnız bu
t aralığı içindir. Sonlu bölgede cusp büyümesi ve üç köklü bölgenin
genişliği için açık sınırlar da var.

## Yeniden üretim

Çalışma kökünde mevcut `.venv-math` ortamı kullanıldı: Python 3.12.14,
python-flint 0.9.0, mpmath 1.4.1. Bağımlılık listeleri önceki paketin
`requirements.txt` ve isteğe bağlı `requirements-plot.txt` dosyalarıdır.

Çalışma kökü `/PROJECT` iken:

```sh
.venv-math/bin/python research/cusp_region/certify_region.py
.venv-math/bin/python research/cusp_region/check_witnesses.py
.venv-math/bin/python research/cusp_region/test_region.py
.venv-math/bin/python research/cusp_region/check_independent.py
.venv-math/bin/python research/cusp_region/plot_region.py
```

Sıra önemlidir: diğer işlemler ilk komutun sertifikasını okur. `-O`/`-OO`
kullanmayın; kesirli tanık denetçisi böyle çalıştırıldığında durur.
Komutlar bu yeni paketin `results/` dosyalarını yeniden üretir; önceki
pakete veya özgün TeX'e yazmaz.

Merkezi integral türevleri `results/center_derivatives.json` içinde
girdisi ve hesap çekirdeği doğrulanarak yeniden kullanılabilir. Bütün
merkezi integralleri yeniden hesaplamak için:

```sh
.venv-math/bin/python -c 'import sys; sys.path.insert(0,"research/cusp_region"); from flint import ctx; from taylor_box import TaylorBox; ctx.dps=110; TaylorBox(reuse_cache=False)'
```

Bu işlemden sonra yukarıdaki sırayı yeniden çalıştırın. Çalışma süresi
alanı nedeniyle sertifikanın bayt özeti yeni koşuda değişebilir; bu
matematiksel tanıkların değiştiği anlamına gelmez. Alt kontrol dosyaları
okudukları sertifikanın tam özetini kaydeder.

## Dosyalar

- `taylor_box.py`: iki kontrolü de kapsayan Taylor polinomu ve gerçek kalan.
- `certify_region.py`: bütün aralıkta örtük eğri, işaretler, sınır noktaları
  ve kök sayısı tanıkları.
- `check_witnesses.py`: yalnız standart Python kesirleriyle tanık
  eşitsizliklerinin ayrı aritmetik denetimi.
- `test_region.py`: yeni hesaba özgü beş kontrol grubu ve 24 doğrudan
  integral karşılaştırması.
- `check_independent.py`: mpmath ile altı ayrı türev kontrolü; sayısal destek.
- `plot_region.py`: makale için PNG/SVG bilimsel şekil; çizgiler örneklenmiş
  gösterimdir, ispat nesnesi değildir.
- `results/region_certificate.json`: tam merkez, kutular, türev aralıkları,
  daralma verileri, kanıt ve kod özetleri.
- `results/witness_check.json`, `results/independent_check.json`, ilgili
  `.log` dosyaları: kontrol izleri.
- `diagnostics/`: başarısız ilk geliştirme koşusu ve açıklaması.

## Güven sınırı

Analitik kanıt ve sayısal kapsama kuralları açıkça incelenebilir; FLINT/Arb
ve Python yürütmesi güvenilen hesap tabanındadır. Kesirli denetçi kaydedilen
türev aralıklarını yeniden bütünleştirmez. mpmath kontrolü hata kapsaması
veren ikinci bir ispat değildir. Dışarıdan uzman incelemesi, literatürde
özgünlük ve dergi değerlendirmesi henüz tamamlanmadı.
