# R20 — Açıklık ve ikna gücü

21 Eylül 2026. Ölçüt: bu sohbeti bilmeyen bir matematikçinin tanımlardan
ana sonuca ve sertifikalara, ara iddiaları tahmin etmeden ulaşabilmesi.
Bu değerlendirme bir okur deneyi veya dış hakem görüşü değildir.

**Karar:** R19 araştırma çekirdeği anlaşılabilir ve denetlenebilir bir
argüman taşıyordu. Bazı ispat adımları gereğinden kısa, uygulamanın
motivasyonu ise geç geliyordu. R20 bunları düzeltir. Genel teoremin
koşulları ve yerel maliyet mekanizması ikna edici; yayın gerekçesinin
en çok güçlendirilmesi gereken tarafı özgün katkının yakın literatürden
ayrılmasıdır. Henüz dış okurun ikna olduğunu iddia edemeyiz.

| Okurun sorusu | R19'daki zayıflık | R20'de yapılan |
|---|---|---|
| Bu optimizasyon neden yapılıyor? | Sabit cusp'ta türev iptali ancak dördüncü bölümde somutlaşıyor. | Girişte üç momentin sıfırları koruduğu, dördüncünün üçüncü türevi iptal ettiği yazıldı. |
| Hangi kısım bilinen teori? | KR ve moment dualitesi ayrılmış, Fortet–Mourier bağlantısı görünür değil. | İki ayrı norm sınırı, maksimum/toplam norm ayrımı ve iki yeni birincil kaynak eklendi. |
| Güçlü konveksliğin “yerel kısmı” tam olarak nedir? | “D'nin bu kısmı” sabit bir integral bölgesi olarak tanımlanmıyor. | D_loc ve sabit komşuluklar yazıldı; kalanın konveksliği açıklandı. |
| Düzgünleştirme pozitifliği nasıl koruyor? | İlk yaklaşımın genliği artırmaması belirtilmemiş. | Önce kesme, ardından pozitif mollifier ve δ*<1 payı belirtildi. |
| Sonlu merkez düzeltmesi nasıl A₄ veriyor? | İki farklı O(a⁴) katkısı tek cümlede. | Ayrı iki eşitsizlik ve 1/3 çarpanının kaynağı yazıldı. |
| Kuyruk tek bir noktadan nasıl denetleniyor? | Global azalmanın gerekçesi sıkıştırılmış. | Logaritmik türev e⁴ᵘ'ya bölünüp pozitif terimlerin azaldığı gösterildi. |
| C₊ ve Γ₊ nedir? | Kullanım anında açık tanım yok. | Sertifikalı üst sınırlar olarak tanımlandı. |
| 0,00002 nasıl “büyük” bir eğim? | Genlik çok küçük olduğundan çıplak M sayısı yanıltabilir. | İlgili küçük ölçeğin δ*/M olduğu ve eşikteki geçiş yarı genişliği açıklandı. |

Sayısal sabitler, H1–H3, Theorem 3.1, Proposition 4.1 ve Theorem 5.1
sonuçları değiştirilmedi. Üç bilimsel şekil R19'dan aynı baytlarla alındı.
R20'deki araştırma pilotu makaleye yeni teorem olarak eklenmedi.

## İkna sınaması: altı itiraz

1. **“Grafikten katsayı çıkarmış olabilirsiniz.”** Katsayı alt ve üst
   ispatların aynı değerde buluşmasından geliyor. Grafikler mekanizmayı
   gösteriyor; sayısal regresyon ispatın yerini almıyor.
2. **“Sadece tasarladığınız rampaların maliyetini buldunuz.”** Alt sınır
   bütün uygun h için. Üst tanık ayrı. Bu ayrım asimptotik optimumu
   sağlar, sonlu M'deki tam optimum profili sağlamaz.
3. **“28 kök bulup sonsuz geri kalanı attınız.”** Faz türevi kalan
   basit köklerin varlığını/ayrıklığını, kuyruk zarfı katkılarının toplam
   sınırını veriyor. Sonlu kökler örneğin tüm kökleri diye sunulmuyor.
4. **“Birkaç M değeri test edilip aralık teoremi yazılmış.”** Uniform
   kontraksiyon ve süreklilik bütün M≥M₀ için tanık verir.
5. **“Bilinen bir norm yeniden adlandırılıyor.”** Norm ve dualite
   bilinen olarak atfediliyor. Aday katkı, tam momentli keskin baş
   katsayı ve doğrulanmış sonsuz geçişli uygulama paketidir.
6. **“Dar örnek neden makale olsun?”** Genel koşullu teorem tek theta
   örneğine bağlı değil. Theta örneği varsayımların boş olmadığını ve
   sonsuz geçişlerin rigoröz denetlenebildiğini gösterir. Bunun yayın
   için yeterli ağırlıkta olup olmadığı dergi ve hakem değerlendirmesine
   açıktır; teknik doğruluk tek başına önem/özgünlük ispatı değildir.

## Dış inceleme için kalan somut işler

En değerli dış kontrol, genel teoremin başka bir bilinen sonucun doğrudan
özel hali olup olmadığını ve sonsuz geçiş varsayımlarının doğal olup
olmadığını sınamaktır. Kamuya dağıtım öncesinde kalıcı arşiv kimliği,
lisans ve temiz kurulumdan yeniden üretim belgesi ayrıca tamamlanmalıdır.
Bu tur herhangi bir başvuru veya dış yazışma yapılmadı.
