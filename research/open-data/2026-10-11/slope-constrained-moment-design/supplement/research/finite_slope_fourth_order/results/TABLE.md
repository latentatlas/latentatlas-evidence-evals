# R22 — Yaklaşık gösterim tablosu

Bu ondalıklar aralık değildir. Kesin rasyonel uçlar certificate.json içindedir.
Hata oranı, M⁻⁴ eklenmiş yaklaşımın mutlak hatasının yalnız M⁻² yaklaşımının hatasına oranıdır.

| Örnek | a | M | M⁴ ölçekli artık | Yeni/eski hata oranı |
|---|---|---:|---:|---:|
| two_switch | 1/5 | 1.320282894 | 0.006396213824 | 0.1952585828 |
| two_switch | 1/10 | 2.533767729 | 0.005427946189 | 0.05170427306 |
| two_switch | 1/20 | 5.016720442 | 0.0052156857 | 0.01311189499 |
| two_switch | 1/50 | 12.5066701 | 0.005158162756 | 0.002106288481 |
| two_switch | 1/100 | 25.00333376 | 0.005150011575 | 0.0005268721331 |
| two_switch | 1/200 | 50.00166672 | 0.005147976355 | 0.0001317367893 |
| negative_C4 | 1/5 | 1.256473736 | -6.201562958e-05 | 0.04980255962 |
| negative_C4 | 1/10 | 2.503308134 | -6.438460068e-05 | 0.01117605726 |
| negative_C4 | 1/20 | 5.001663483 | -6.492758853e-05 | 0.002719616364 |
| negative_C4 | 1/50 | 12.50066646 | -6.507606292e-05 | 0.0004318599707 |
| negative_C4 | 1/100 | 25.00033331 | -6.509714605e-05 | 0.0001078483714 |
| negative_C4 | 1/200 | 50.00016666 | -6.510241184e-05 | 2.695480862e-05 |
| C2_only | 1/25 | 6.252128401 | 0.0005276474495 | uygulanmaz |
| C2_only | 1/100 | 25.00053052 | 0.0009211090466 | uygulanmaz |
| C2_only | 1/400 | 100.0001326 | 0.001710122754 | uygulanmaz |
| C2_only | 1/1600 | 400.0000331 | 0.003288390279 | uygulanmaz |

İlk iki örnekte sınırlar sırasıyla 253/49152 ve −1/15360.
C² örneğinde bu ölçekli artık sınırsız büyür; sonlu C₄ yoktur.
