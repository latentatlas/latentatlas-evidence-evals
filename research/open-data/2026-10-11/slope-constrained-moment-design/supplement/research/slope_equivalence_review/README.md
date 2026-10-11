# R18 — KR/flat norm eşdeğerliği ve katkı karşılaştırması

21 Eylül 2026. Yeni araştırma sonucu eklemeyen literatür/eşleme turu.
R15–R16 sayısal sabitleri ve dondurulmuş paketleri değişmedi.

- [Katkı değerlendirmesi](CONTRIBUTION_REVIEW.md): Türkçe ana sonuç ve makale paragrafı.
- [Tam formülasyon eşlemesi](EQUIVALENCE_MAP.md): amaç, momentler, norm, topoloji ve ölçek.
- [Yedi kaynakla karşılaştırma](LITERATURE.md) ve [kaynak kimlikleri](sources.json).
- [Arama ve erişim kaydı](SEARCH_LOG.md).
- [Normalizasyon tanısı](NORMALIZATION_CHECK.md) ve [tam-kesir çıktısı](results/normalization_checks.json).
- [Paket denetimi](audit_report.json), [girdi kimlikleri](inputs.json), [manifest](manifest.json).

Standart Python 3 ile, çalışma dizininden bağımsız salt okunur kontrol:

```sh
python3 research/slope_equivalence_review/audit_snapshot.py
```

Küçük örnekleri ayrı üretmek için (dondurulmuş çıktı üzerine yazmayın):

```sh
python3 research/slope_equivalence_review/check_normalization.py --output /tmp/r18-normalization.json
```

Denetçi eski paketlerin bütün hash'lerini, R18'in kendi içeriğini,
kaynak kayıtlarını ve tam-kesir sonuçlarını kontrol eder. Matematiksel
minimax ispatı ve kaynak yorumları insan/LLM tarafından yazılmış
incelemelerdir; kod bunları formal doğrulamaz. Öncelik ve dış hakemlik
açıktır. Masaüstündeki ana klasör yerel yayın hazırlık kopyasıdır.
