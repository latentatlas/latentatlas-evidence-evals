# Doğrulanmış cusp araştırması — çalışma paketi

20 Eylül 2026. Bu paket özgün masaüstü projesinden ayrı hazırlanmıştır.
Makale yayımlanmış veya bağımsız hakem tarafından onaylanmış değildir.

**Yeni sonuç:** Orijinal çekirdeğin yalnızca λu²+μu⁴ deformasyonu, yaklaşık
(t,λ,μ)=(41.40034135868425, -3.645692061604919, 8.335120498918607)
noktasında transversal cusp verir. Altıncı derece terim bu örnek için gerekli
değildir. Bu, dördüncü derecenin gerekli/minimal olduğunu göstermez.

**Yerel geçiş:** Sertifikadaki tam merkezin μ koordinatı sabitken, λ merkezden
10⁻⁶ küçük seçildiğinde t₀±0.003 içinde tam bir gerçek kök, 10⁻⁶ büyük
seçildiğinde tam üç gerçek kök vardır. İki durumun da kökleri basittir.

**Analitik katkı:** Isı özdeşliğini sağlayan ailelerde cusp çevresindeki fold
eğrisinin λ yönündeki ikinci derece katsayısı kullanılan normalizasyonda tam
olarak 2'dir. Kontrol eğrisinin üçüncü derece katsayıları türetildi ve iki
cusp için kapsandı. Genel lemanın literatürde yeni olduğu ileri sürülmüyor.

Tam matematiksel gerekçe [PROOF.md](PROOF.md), Türkçe sonuç değerlendirmesi
[ARASTIRMA_NOTU.md](ARASTIRMA_NOTU.md), ham tanıklar `results/` içindedir.

## Yeniden çalıştırma

Python 3.12.14, python-flint 0.9.0 ve mpmath 1.4.1 ile çalıştırıldı. Aynı
ortamda, bu klasörden:

```sh
python -m pip install -r requirements.txt
python certify_cusp.py --family sextic
python certify_cusp.py --family quartic
python certify_cusp.py --family quartic --dps 130 --terms 20 --pieces 16 --output results/quartic_precision_check.json
python local_roots.py
python test_validated_flow.py
python check_independent.py
```

Kod başarısız bir kanıt testinde hata verir. JSON'daki durum etiketi, tek
başına matematiksel gerekçe olarak kullanılmaz; PROOF.md ile birlikte okunur.
`center_exact_dyadic` alanı gerçek sertifika merkezidir. Ekranda az basamakla
yazılan yaklaşık merkez, 10⁻⁸⁸ yarıçaplı bir sertifikanın merkezi değildir.

Grafik isteğe bağlıdır ve kanıtın bir bağımlılığı değildir:

```sh
python -m pip install -r requirements-plot.txt
python plot_local_roots.py
```

`manifest.json` kaynak/çıktı özetlerini ve kaynak masaüstü dosyalarının
değişmediğine ilişkin karşılaştırmayı kaydeder. Yeniden üretimde süre alanları
değişebileceğinden JSON dosyalarının byte düzeyinde aynı olması beklenmez.

## Dosyalar ve sorumlulukları

| Dosya | İşlev |
|---|---|
| validated_flow.py | Sonlu tüm fonksiyonun integrasyonu, iki ayrı kuyruk sınırı, aralık normları ve uniform türev sınırları |
| certify_cusp.py | Sabit önkoşullayıcıyla daralma kanıtı; cusp, kontrol rankı ve yerel katsayılar |
| local_roots.py | Açık t aralığında bir/üç kök sayımı, Taylor kalanı ve işaret tanıkları |
| check_independent.py | Eski/yeni çekirdek kodunu içe aktarmayan mpmath sayısal karşılaştırması |
| test_validated_flow.py | Kanıtı etkileyen hataları hedefleyen on regresyon kontrolü |
| plot_local_roots.py | Sertifikalı geçişin gösterimi; çizilen orta değerler kanıt yerine geçmez |

## Henüz kapsamda olmayanlar

Eski uzun devam koşularının düzeltilmesi; yeni quartic cusp'ın eski sextic
cusp ile aynı global dal üzerinde olduğunun ispatı; özgün zeta kök çiftlerine
aidiyet; bütün parametre düzlemindeki cusp/A4 sayımı; fiziksel sistem modeli;
literatürde öncelik ve dergi kabulü. Bunlar sonuç etiketi altında sunulmaz.

Bir sonraki matematiksel hedef: cusp'a ulaşan fold kollarını açık bir kontrol
bölgesinde devam ettirip aynı dala ait olduklarını bağlantı tanıklarıyla
göstermek; ardından o bölgenin bir/üç kök sınırını nicel olarak sertifikalamak.
