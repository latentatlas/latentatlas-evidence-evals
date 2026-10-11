# R17 — R15–R16 iddia ve gerekçe denetimi

21 Eylül 2026. Bu tablo yeni iddia üretmez. “Korundu”, bu tur analitik
okumada geri çekme gerektiren hata bulunmadığını ifade eder; dış hakem
veya formal ispat statüsü değildir. R01/R09/R11/R12 girdileri önceki
donmuş kanıt zinciri olarak kullanıldı; bu tur o zincirin bütün
integralleri baştan hesaplanmadı. R13'ün düzgün sınıfa geçiş ispatı okundu.

| Kimlik | Denetlenen önerme | Gerekçe / kontrol | Sonuç |
|---|---|---|---|
| A01 | δ*=f₃/D* | Moment kısıtları ve L∞–L¹ eşitsizliği; işaret tanığı eşitlik sağlar | Analitik olarak korundu; klasik dualite |
| A02 | Gerçek dual optimum var ve tek | Kapalı kürede minimum; sınırda güçlü konvekslik/gradyan farkı; iç minimumdan global konvekslik | R15 yeniden üretimi ve rasyonel denetim geçti |
| A03 | D'nin kullanılan Hessian alt sınırı | Sabit kaba kök komşuluklarında pozitif ilk theta terimi; geriye kalan yoğunluk ve dış integral konveks | Bölme katsayıya bağlı değil; döngü yok |
| A04 | Optimumda sıfır sign momentleri | İzole sıfırlar ölçü sıfır; |p_j| integrallenebilirliğiyle D'nin birinci türevi | Ek varsayım gerekmedi |
| A05 | Sonlu bölgede tam artık kök örtüsü | 28 basit kök kutusu ve aralıksız 113 işaret yaprağı | Taze üretim ve rasyonel bölüşüm kontrolü geçti |
| A06 | Sonsuz kuyrukta bütün kökler basit/ayrık | A>7u³, faz türevi 81–85; sonlu-kuyruk birleşim mesafesi | Analitik sınır ve katsayı kontrolleri korundu |
| A07 | Γ ve yerel türev toplamları sonlu | Ayrıklık + polinom çarpanlı süperüstel theta zarfı | Kesme dışı ihmal yapılmıyor |
| A08 | Genel alt baş katsayı δ*³Γ/(3D*) | Pozitif dual kayıp; karşılıklı noktalarda Lipschitz eşitsizliği; önce sonlu kök toplamı | 1/3 katsayısı yeniden kontrol edildi |
| A09 | Sonsuz yumuşatma haritası C² | Yerel fark integralleri ve toplanabilir türev majorantları | Ayrıntılı sınır PROOF_ADDENDUM §1'e yazıldı |
| A10 | İlk m moment tam düzeltilebilir | Seçili geçiş değerlendirme matrisi tersinir; sonlu boyutlu IFT | R15 determinant kutusu sıfırı dışlıyor |
| A11 | Konum düzeltmesi O(a²); artık moment etkisi O(a⁴) | a'da çiftlik; q_r(z_k)=0 | Baş terimi değiştirmiyor |
| A12 | Büyük M için eşleşen üst baş katsayı | α=f₃/S₃, eğim α/a; yeterince küçük a'da monotonluk | Genel teorem varsayımları altında korundu |
| A13 | C* sertifikalı sayısal aralığı | Gerçek a* kutusu, tam yoğunluk, sonsuz Γ kuyruğu, R12 δ* | (9.20340371e−25,9.20340375e−25) değişmedi |
| A14 | R16 üç-konum büzülmesi bütün 0<a≤2⁻¹⁴ için geçerli | κ_i+η_i<1; türev ve merkez hata sınırları uniform | Taze rasyonel denetim geçti |
| A15 | Sabit nokta moment sıfırıdır | B tersinir; ||I−BJ||<1 yeterli | İspat cümlesi açıklandı; exact det B ayrıca sıfır değil |
| A16 | a=0'a sürekli uzantı ve bütün M≥M₀ kapsamı | S/a²→Jv−F uniform; uniform büzülme; ara değer teoremi | PROOF_ADDENDUM §2'de açıklandı |
| A17 | B₂/A₃ sonsuz toplam, A₄ yalnız üç konum | Yalnız üç merkez hareket ediyor | Formül/kod doğru; tek metin cümlesi düzeltildi |
| A18 | Açık üst kalan terim | D*e_a=αL; α³ farkının pozitif paydaya alınması | Rasyonel hesap + bağımsız polinom özdeşliği geçti |
| A19 | Açık alt kalan terim | Negatif yerel Taylor alt sınırında pozitif kısım; sonra mutlak yakınsak toplam | İşaret yönü ve 1/12 katsayısı korundu |
| A20 | Gerçek δ* tabanı bütün büyük M için kullanılıyor | Yaklaşık sabit dual hata formüle sokulmuyor | Büyük M'de sabit hata tabanı sorunu yok |
| A21 | M₀'da toplam minimum aralığı | Ayrı rasyonel dışa yuvarlama | 0.00000000091787309568619750 ile 0.00000000091787309964331750 değişmedi |
| A22 | Yüzde 0,1178 bağıl hata | Payda C*/M₀²; bütün genlik değil ek maliyet | Doğru niceliğe ait; katsayı keskinliği iddiası yok |
| A23 | Düzgün geometrik sınıfta aynı infimum | R13: sıkı eğim payı, mollifier, dört moment sağ tersi, küçük jet düzeltmesi | Kütle normalizasyonu yokken geçerli; minimumun bu sınıfta varlığı çıkarılmıyor |
| A24 | Sayısal ramp koşusu yalnız destekleyici | Merkezi Q, sonlu theta kesmesi ve sayısal artıklar | Rigoröz tanık veya tam optimum diye yükseltilmedi |
| A25 | R15/R16 çıktılarının tekrar üretimi | Yeni sertifikalar geçici ağaca yerleştirildi; bağımlı kontrol bunları okudu | 11 koşu, 9 yeni sonuç, 2.966 aynı aralık |
| A26 | Eski kanıt girdileri korunmuş | 17 manifestin 811 girdisi önce/sonra hash ile kontrol edildi | Değişiklik yok |
| A27 | Literatürden özgünlük sonucu | Amaç, kısıt, bölge ve sonuç türü karşılaştırıldı | Katkı adayı belirgin; öncelik kanıtlanmış değil |

Kaynaklar: [R15 ispatı](../kernel_slope_asymptotics/PROOF.md),
[R16 ispatı](../kernel_slope_remainder/PROOF.md),
[R13 düzgün sınıf geçişi](../kernel_slope_budget/PROOF.md),
[ispat ekleri](PROOF_ADDENDUM.md), [koşu raporu](replays/report.json),
[cebir denetimi](results/review_algebra.json),
[literatür karşılaştırması](LITERATURE.md).
