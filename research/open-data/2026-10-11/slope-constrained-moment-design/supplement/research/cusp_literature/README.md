# R06 — Literatürde konumlandırma

20 Eylül 2026. Bu paket yeni bir integral taraması değildir. R01–R05'in
korunmuş sonuçlarının bilimsel kapsamını, yakın literatürle farkını ve
hangi özgünlük iddialarının uygun olduğunu kaydeder.

- [Türkçe araştırma değerlendirmesi](ARASTIRMA_NOTU.md)
- [Yakın literatür ve iddia tablosu](KATKI_KARSILASTIRMASI.md)
- [Genel kuramdan çıkan sonuçlar ve tam karşılaştırma örneği](MATEMATIKSEL_KONUM.md)
- [İngilizce ilgili çalışmalar taslağı](RELATED_WORK_DRAFT.tex)
- [Kaynakça](references.bib), [kaynak/sürüm/okuma kataloğu](sources.json)
- [Tarama sorguları ve sınırları](SEARCH_LOG.md)
- [Tam cebir kontrolü](check_structural_example.py), [çıktı](structural_example.json)

Yeniden üretim, proje kökünden:

```sh
.venv-math/bin/python research/cusp_literature/check_structural_example.py
.venv-math/bin/python research/cusp_literature/audit_snapshot.py
```

İlk komut yalnız standart Python kütüphanesi ve tam rasyonel aritmetik
kullanır; raporu standart çıktıya yazar. `--output` verilirse mevcut
dosyanın üzerine yazmayı reddeder. İkinci komut, dondurulmuş paketleri,
özgün dosyaları, R05 bağımlılık denetimini, R06 belge bağlantılarını,
kaynak anahtarlarını ve tam cebir örneğini kontrol eder. Ağ isteği yapmaz.

`audit_snapshot.py --freeze` yalnız ilk sürümü kaydetmek içindir;
mevcut manifesti değiştirmez. Çalışma defteri ve genel makale kapsamı
bu paketin dışında tutulur. Sonraki düzeltme yeni bir kayıt/sürüm
olarak yapılmalı. Kodun başarılı çalışması, literatürde önceliğin veya
dış matematiksel denetimin tamamlandığı anlamına gelmez.

LaTeX parçası kaynakça anahtarları ve ayraç dengesi açısından kontrol
edilir; bu ortamda derlenmiş bir makale/PDF teslim edildiği iddia
edilmez. R05'in mevcut şekilleri bu turda yeniden üretilmedi.
