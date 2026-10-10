# R06 — Tarama günlüğü ve kapsam sınırı

Tarih: 2026-09-20. Yöntem: web araması, bulunan makalelerin birincil
tam metinleri, arXiv sürüm kayıtları, yayınevi/yazar kayıtları ve
yakın makalelerin kaynakçalarından iz sürme. Aşağıdaki sorgular bu
oturumda kullanıldı; sıralama kronolojik bir çalışma süresi kaydı değildir.
Sonuç sıraları zamanla değişebilir. Kullanıcının yayımlanmamış sayısal
merkezleri, CV'si veya çalışma dosyaları arama hizmetine gönderilmedi.

## Aynı aile ve problem için sorgular

```text
"de Bruijn" "Newman" "quartic"
"de Bruijn" "cusp"
"polynomial" "deformations" "Riemann" "zeros" heat
"de Bruijn Newman" "polynomial" deformation cusp
"de Bruijn-Newman" "higher order" flow
"de Bruijn-Newman" "u^4"
"de Bruijn" "higher-order"
"de Bruijn" "sextic"
"de Bruijn-Newman" "higher-order" "zeros"
"de Bruijn-Newman" "sextic" "cusp"
"de Bruijn-Newman" "polynomial deformation"
"de Bruijn-Newman" "cusp bifurcation"
"de Bruijn-Newman" "hexa-harmonic"
"Jacobi" "kernel" "cusp" "zeros"
"Riemann" "quartic" "sextic" "cusp"
"de Bruijn" "cusp" "fold"
"Newman" "higher heat" zeros
"Riemann xi" "cusp" integral
"de Bruijn-Newman" "Pearcey"
"de Bruijn-Newman" "quartic deformation"
"de Bruijn-Newman" "multiple zeros" "parameters"
```

Bu sorgularda doğrudan aynı quartic–sextic cusp bağlantısı ve nicel
iç içe geçme teoremi saptanmadı. Çok sayıda sonuç “cusp form”, Jacobi
matrisi, bilgisayar bilimindeki de Bruijn yapıları veya başka alanlarda
aynı isimleri içeriyordu; terim benzerliği matematiksel eşleşme sayılmadı.

## Yöntem, sıfır kuramı ve kaynak kimliği sorguları

```text
"Lessard" "Pugliese" "cusp" computer assisted
"Newman" "Wu" constants Fourier transforms only real zeros 2019
"heat equation" "multiple zeros" Hermite polynomials entire functions
"Constants of de Bruijn-Newman type"
"Entire solutions for the heat equation"
"Rodgers" "Tao" "de Bruijn" arxiv
"10.1016/j.laa.2025.08.015"
"Computation of Smooth Manifolds Via Rigorous Multi-parameter Continuation" pdf
"Generic Cuspidal Points and their Localization"
"Generic Cuspidal Points and their Localization" Dieci Pugliese pdf
"Lehmer pairs of zeros" Csordas Smith Varga 1994 pdf
"Über trigonometrische Integrale mit nur reellen Nullstellen" 1927 pdf
"de Bruijn-Newman constant is non-negative" "e6" 2020
site.ams.org "Constants of de Bruijn" "595"
"Wei Wu" "Constants of de Bruijn" "2020"
```

Sonuçlardan Lessard ve Pugliese'nin yazar sayfalarına, ilgili yayıncı
kayıtlarına, Gameiro–Lessard–Pugliese'nin makalesine ve
Lessard–Sander–Wanner'ın bifurcation continuation çalışmasına gidildi.
Okuma düzeyleri `sources.json` içinde makale bazında kayıtlıdır.
Başlık/özet kontrolü ile seçilmiş teoremin okunması aynı şey sayılmadı.

## Dışarıda tutulan veya açık kalan eşleşmeler

- Pólya'nın 1927 makalesinin DOI ve bibliyografik kaydı bulundu;
  eski taramanın tam metin erişimi başarısız oldu. Evrensel çarpan
  sınıflandırması bu pakette bağımsız bir yeni çıkarımın dayanağı yapılmadı.
- Newman–Wu'nun AMS sayfaları son doğrudan erişimde 403 döndürdü.
  Yayıncı PDF'sinin başlığı arama çıktısında ve yazar kaydıyla
  kontrol edildi; içerik okumasında arXiv tam metni kullanıldı.
- Varga'nın kaynak listesindeki 1994 Lehmer-pair makalesi bağlantısı,
  beklenen tam metinle güvenle eşleştirilemedi. Tam makale okunmuş gibi
  kaydedilmedi; tarihsel kök hareketi bağlamı için okunan Rodgers–Tao
  makalesi yeterli tutuldu.
- Yeni RH çözümü veya daha güçlü global sınır iddiası taşıyan arama
  sonuçları, yalnız arama özeti nedeniyle yerleşik sonuç kabul edilmedi.
  Bu çalışma güncel en iyi \(\Lambda\) sınırını belirleme denetimi değildir.
- Dieci–Pugliese'nin “cuspidal points” başlığı incelendi; matris
  özdeğer çakışması olduğu için doğrudan aynı problem olarak eşleştirilmedi.
- “Jacobi cusp form” ve Pearcey/catastrophe terimleri ortak sözcükler
  üzerinden otomatik fiziksel veya sayı teorik bağlantı kurmak için kullanılmadı.

## Bu tarama neyi kanıtlamaz?

MathSciNet/zbMATH üzerinden eksiksiz kayıt taraması, tüm ileri atıfların
okunması ve konu uzmanından öncelik değerlendirmesi yapılmadı. Her
ilgili makalenin bütün kanıtları yeniden denetlenmedi. Bu nedenle
“başkası yapmadı”, “ilk”, “en güçlü” veya “hakemli dergide kesin kabul”
sonuçları üretilmiyor. Yenilik durumu: **sınırları belirli aday katkı**.

Gönderim öncesi kalan iş: aynı aileyi başka notasyonlarla inceleyen
deformasyon/çok katlı sıfır literatürünü atıf zincirleriyle genişletmek;
en yakın birkaç makale karşısında ana teorem kapsamını uzmanla kontrol
etmek. Bu açık iş, R01–R05'in dosya veya sayısal doğrulama durumunu
değiştirmez.
