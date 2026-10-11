# R20 — Hesap denetimi, açık ispat ve özgünlük incelemesi

21 Eylül 2026. R19 korunarak yeni 14 sayfalık İngilizce sürüm hazırlandı.
Ana teorem sonuçları, sertifikalı sabitler ve üç bilimsel şekil değişmedi.
Bu tur C1–C4 hesapları tekrar üretildi; R19'un 54 denklem bloğu ve
metindeki çıkarımlar incelendi. R20 bir dış hakem raporu değildir.

- [Matematik ve hesap incelemesi](MATH_REVIEW.md)
- [54 denklem bloğunun tek tek kaydı](equation_inventory.json)
- [Açıklık ve ikna sınaması](CLARITY_REVIEW.md)
- [Özgünlük değerlendirmesi](ORIGINALITY_REVIEW.md)
- [Derinleştirmeye başlangıç: dengeli geçiş merkezleri](NEXT_QUESTION.md)
- [Yeni LaTeX](revised/manuscript.tex) ve [14 sayfalık PDF](revised/output/pdf/manuscript.pdf)
- [Kaynak sicili](sources.json), [arama kaydı](SEARCH_LOG.md)
- [Görsel kontrol](pdf_qa.json), [kapanış denetimi](audit_report.json), [manifest](manifest.json)

Yeni araştırma notundaki tek geçişli yardımcı önerme ve tam kesir
karşıörnekleri, theta için yeni bir optimum sertifikası değildir.
Literatür önceliği, dış hakemlik, M⁻⁴ yasası ve sonlu bütçede tam optimum
açık kalıyor. Önceki araştırma paketleri ve R19 dosyaları değiştirilmedi.

## Dosyaları denetleme

Standart Python yeterlidir; `-O` kullanmayın. Tam araştırma ağacı gereklidir.
Herhangi bir çalışma dizininden:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/research/manuscript_review/audit_snapshot.py
```

Bu denetçi önceki 20 manifest/884 girdiyi, yeni-eski matematiksel
aralıkların eşliğini, kod/girdi kimliklerini, basılı sayı aktarımını,
teorem ifadelerinin korunmasını ve bu paketin dosyalarını kontrol eder.
Standart kütüphaneli ek cebir tanısını geçici bir dosyada yeniden çalıştırır.
Analitik ispatın doğruluğunu otomatik olarak kararlaştırmaz.

## Matematik hesaplarını tekrar üretme

Önce önceki paketlerin README'lerinde kayıtlı matematik ortamını kurun
(bu tur: Python 3.12.14, python-flint 0.9.0 / FLINT 3.6.0,
mpmath 1.4.1). Aşağıdaki çıktılar için araştırma ağacının dışında yeni
bir geçici dizin kullanın; donmuş dosyaları ezmeyin.

```sh
python3 -B /path/to/research/cusp_verified/certify_cusp.py \
  --family quartic --dps 110 --terms 16 --pieces 8 --output /tmp/new-review/base.json
python3 -B /path/to/research/kernel_norm_threshold/certify_threshold.py \
  --output /tmp/new-review/norm.json
python3 -B /path/to/research/slope_chain_review/replay_chain.py \
  --output-dir /tmp/new-review/slope-chain
python3 -B /path/to/research/manuscript_review/crosscheck_base_cusp.py \
  --output /tmp/new-review/base-numerical.json
python3 -B /path/to/research/kernel_norm_threshold/crosscheck_moments.py \
  --output /tmp/new-review/norm-numerical.json
python3 -B /path/to/research/slope_chain_review/check_review_algebra.py \
  --output /tmp/new-review/review-algebra.json
python3 -B /path/to/research/manuscript_review/check_equations.py \
  --output /tmp/new-review/equation-checks.json
```

`/tmp/new-review` üst dizinini önceden oluşturun; `slope-chain` alt
dizini henüz bulunmamalıdır. Sonraki denetim turlarında manifest sayıları
artabilir; sayısal uçlar ve ispat koşulları karşılaştırılmalıdır.
`crosscheck_base_cusp.py`, R20'de kaydedilen taze C1'i; norm karşılaştırıcı
özgün donmuş C2'yi okur. İkinci sertifikanın yeni uçlarla eşliği ayrıca
denetlenir. Bu karşılaştırmalar aralık üreticisinden ayrı mpmath
integralleridir, rigoröz sertifika değildir.

## Metni/PDF'yi tekrar üretme

R19'dan R20'ye yapılan her metin değişikliği
`revise_manuscript.py` içinde tekil eşleşmeyle tanımlıdır. Yeni bir dizinde:

```sh
python3 -B /path/to/research/manuscript_review/revise_manuscript.py \
  --output-dir /tmp/new-review/paper
python3 -B /tmp/new-review/paper/build_pdf.py \
  --tectonic /path/to/tectonic --output-dir /tmp/new-review/pdf
```

Tectonic 0.17.0 kullanıldı. Derleme ve şekiller yereldir; makale dışarıya
yüklenmez. Yeni PDF derlemesinin zaman damgaları nedeniyle hash'i
değişebilir. Kaynak hash'i ve içerik kontrolü ayrıca yapılmalıdır.
Bu tur bütün 14 sayfa Poppler ile 1400 piksele render edilip görsel
olarak incelendi; kaynakça, denklemler, tablo ve şekillerde taşma veya
eksik karakter görülmedi. Yeni bir dizgi değişiminde görsel kontrol
tekrarlanmalıdır.

Kamusal dağıtım, lisans ve kalıcı arşiv kimliği bu yerel hazırlığın
parçası olarak tamamlanmış sayılmıyor.
