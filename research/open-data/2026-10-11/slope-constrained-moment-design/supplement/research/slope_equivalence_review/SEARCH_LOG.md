# R18 — Arama, erişim ve eleme kaydı

Tarih: 21 Eylül 2026. Soru: R15 genel teoremi, aynı hedef momentleri,
en küçük L∞ genliğini ve ayrı sert Lipschitz sınırını kullanan önceki
bir teoremin eşdeğeri mi? R17'nin kontrol/regularizasyon karşılaştırması
bu tur KR/flat/Fortet–Mourier ve unbalanced transport adlarıyla genişletildi.

Aramalar genel web aramasında yapıldı. Sonuçlar birincil makale/PDF ve
yayıncı/kurumsal kayıt üzerinden değerlendirildi. Arama motorunun
sıralaması ve birleştirdiği çoklu sorgu sonuçları tekrar koşuda aynı
olmayabilir. Bu kayıt, kapsamı gösterir; bibliyografik eksiksizlik
belgesi değildir. Sorgu sonucunun boş/ilgisiz gelmesi bir yokluk ispatı
olarak kullanılmadı.

## Çalıştırılan sorgular

### İlk keşif: moment, hard-rate ve bounded Lipschitz

1. `"L-moment problem" "derivative"`
2. `"minimum norm control" "rate" "constraints" continuous`
3. `"flat metric" "bounded Lipschitz" Piccoli Rossi`
4. `"Lipschitz approximation" "moment" constraints`
5. `"flat metric" "asymptotic" "total variation"`
6. `"Kantorovich Rubinstein" "two parameters" discrepancy`
7. `"On properties of the generalized Wasserstein distance" Piccoli Rossi pdf`
8. `"bounded Lipschitz" "asymptotic expansion"`
9. `"Kantorovich–Rubinstein discrepancy"`
10. `"flat norm" "asymptotic" density`
11. `"Fortet-Mourier" "total variation" rate`

Sonuç: L07–L11 hattı bulundu. TV–Fortet–Mourier yakınsaklık
eşitsizliklerinde çoğunlukla değişen ölçü dizileri inceleniyor;
sabit residual yoğunluğunda test-fonksiyonu eğim sınırını büyütmekle
aynı problem olarak kaydedilmedi.

### Amaç ve asimptotik eşlemesi

12. `"Kantorovich Rubinstein" "asymptotic" "norm"`
13. `"flat norm" "large" "Lipschitz" density`
14. `"flat metric" "moment constraints"`
15. `"Kantorovich-Rubinstein" "moment" "minimum"`
16. `"Kantorovich" "Rubinstein" "asymptotic expansion"`
17. `"flat metric" "asymptotics"`
18. `"flat norm" "total variation" "limit" density`
19. `"Imaging with Kantorovich" 2014 DOI`
20. `"Kantorovich-Rubinstein" "second order" norm`
21. `"flat norm" "density" "expansion" -metric -geometry -Riemannian`
22. `"Lipschitz" "moment constraints" optimization`
23. `"Lipschitz approximation" "sign" weighted`
24. `minimum amplitude control bounded derivative fixed time moment bang bang`
25. `Lipschitz moment problem extremal norm spline derivative bound`
26. `Kantorovich Rubinstein norm total variation limit rate smooth density zeros`
27. `flat distance smooth densities small scale asymptotic expansion`
28. `"minimum amplitude" "rate" control optimization`
29. `"minimum norm" "control derivative"`
30. `"moment problem" "Lipschitz" "norm"`
31. `"flat norm" "zeros" measure density`

Sonuç: doğrudan aynı tam baş-katsayı teoremi saptanmadı. «Flat metric»
aramalarında Riemann geometrisi/genel görelilik sonuçları çok sayıda
çıktı; ölçülerdeki bounded-Lipschitz normu yerine kullanılmadı.
Hessian/ikinci-türev kısıtlı transport, minimum-time veya L¹ minimum-fuel,
entropy/rational moment ve rastgele örnekleme yakınsaması da amaç/kısıt
eşitliği sağlamadığından bu teoremin önceki hali olarak sayılmadı.

### Atıf zinciri ve normalizasyon doğrulaması

32. `Maurice Sion On general minimax theorems 1958 pdf`
33. `"Kantorovich–Rubinstein Distance and Barycenter" Heinemann Klatt Munk`
34. `"Efficient algorithms computing distances between Radon measures" doi`
35. `"flat norm" "regularization parameter" "asymptotic"`
36. `"Heinemann" "09911" correction`
37. `"flat metric" "large Lipschitz"`
38. `"Kantorovich-Rubinstein" "sign changes"`
39. `Schmitzer Wirth 2019 framework Wasserstein 1 type metrics asymptotic`
40. `"unbalanced transport" "small" "asymptotic" total variation`
41. `"flat norm" "smooth" "asymptotic" measures -flat-sky -Riemannian -scalar`

Sonuç: L12 klasik minimax; L13 daha geniş eşdeğerlik çerçevesi.
L11 katsayı tutarsızlığı için bulunan düzeltme kaydı olmadı; bu,
«hiç düzeltme yayımlanmadı» iddiasına dönüştürülmedi.

## Okuma ve erişim sınırları

- L07/L08/L09/L11/L12/L13: birincil PDF'ler geçici dizine indirildi,
  metinleri pdfplumber ile çıkarıldı. PDF hash'leri sources.json'da.
  Tam okuma iddiası yok; kullanılan bölüm/sonuçlar LITERATURE.md'de.
- L10: yayıncı tam HTML, tanım/yöntem ve atomlar için Proposition 1.
  Yerel PDF indirilmedi; dolayısıyla PDF hash'i uydurulmadı.
- L11 yayıncı PDF'sinin MPG aynası yerel istekte 403 verdi. ArXiv v3
  ve yayıncı HTML kullanıldı. ArXiv s.7 render edilerek TV faktörü ve
  dualdeki C/2 gözle kontrol edildi. Yayıncı PDF'si gözle kontrol edilmiş
  gibi gösterilmedi.
- L12 s.174 render edilip compact-one-side corollary doğrulandı;
  numaralama belirsizliğine karşı sayfa ve konum birlikte belirtiliyor.
- L09 için ilk not taslağındaki §3.2 atfı kaynak başlıklarıyla kontrol
  edilerek §3.3'e düzeltildi: §3.2 centralized Wasserstein, §3.3 flat
  distance algoritmasıdır. Paket dondurulmadan yapılan bir atıf
  düzeltmesi; araştırma formülü veya sabiti değişmedi.
- Web PDF ekran görüntüsü isteğinde L09 s.6 hata verdi. Bu erişim
  bir matematiksel doğrulama sayılmadı; ilgili metin yerel PDF'den okundu.
- Geçici makale PDF/metin/render dosyaları paket kapanışında silinir;
  dağıtılacak klasörde yalnız bibliyografik metadata ve kendi notlarımız
  tutulur. Tam telifli kaynak içerikleri paketlenmez.

## Kalan özgünlük sorusu

R15'teki tam C* formülünü, tam moment koruması ve sonsuz geçişler için
gösteren daha eski bir sonuç başka terminolojiyle bulunabilir.
Bu turda «bulunmadı» statüsü korundu. Özellikle sadece norm tanımına,
yalnız üssün M⁻² olmasına veya sayısal sonuçların tutmasına dayanarak
öncelik iddia edilmeyecek. Sonraki değerlendirmeye somut temel,
[E1–E7 eşlemesi](EQUIVALENCE_MAP.md) ve açık varsayım listesi olacak.
