# Geliştirme kaydı

İlk koşuda, işareti değişen bir Arb aralığı üzerinde genel kuvvet işlemi
sonlu sonuç vermedi. Sonlu değer kontrolü koşuyu durdurdu; bu koşudan
sertifika veya matematiksel başarı iddiası üretilmedi. Yeni Taylor kodu
tekrarlı aralık çarpımına geçirildi. Sıfırı kapsayan aralıklar için regresyon
kontrolü eklendi ve geçti.

`initial_power_evaluation_failure.log` bu duruşun kaydıdır.
`first_uniform_certificate.log` ilk başarılı ana eşitsizlik koşusudur;
son sürümün tamamlanmış sertifikası ve kontrolleri `../results/` içindedir.
Bu geliştirme kayıtları güncel kanıtın yerine kullanılmaz.
