# R30 numerical record

All published endpoints below are outward bounds. Exact fractions and
Arb enclosures are in the linked JSON files. Decimal approximate maxima
are labeled as diagnostics and are not substituted for interval bounds.

| Quantity | Lower / condition | Upper / consequence |
|---|---:|---:|
| Driver ν | −1/64 | 0 |
| Lipschitz budget M | 2×10⁻⁵ | no finite upper limit |
| Uniform remainder | −1.02×10⁻⁵³/M⁶ | 1.64×10⁻⁵³/M⁶ |
| δ₀′ | 2.7×10⁻¹¹ | 3.0×10⁻¹¹ |
| C₂′ | 7.4×10⁻²⁶ | 8.7×10⁻²⁶ |
| C₄′ | 1.9×10⁻⁴⁰ | 5.3×10⁻⁴⁰ |
| Actual-value ordering | Δν≥1.54×10⁻¹⁴(M₀/M)⁶ | strict positive difference |
| Z_M ordering | Δν>0.00035(M₀/M)² | strict positive difference |
| Endpoint actual difference at M₀ | 4.21877890×10⁻¹³ | 4.68753399×10⁻¹³ |
| Endpoint Z difference at M₀ | 2.90225×10⁻⁴² | 8.34775×10⁻⁴² |
| Adjacent-node Z difference, all M≥M₀ | >2.62734375×10⁻⁴⁴ | spacing 1/2048 |

Here Z_M=M⁴[δ_ν(M)−δ₀(ν)−C₂(ν)/M²]. The target f_ν and the
allowed perturbation depend on ν. This is a comparison of the specified
associated problems, not one profile for the entire arc.

The two maximum rationally reconstructed remainder bounds satisfy
Kminus<1.001×10⁻⁵³ and Kplus<1.620×10⁻⁵³; the theorem retains the
slightly wider old published constants above. Their approximate values
are 1.000440834663e-53 and 1.619183148903e-53, respectively.

There are 32 closed cells, 28 finite root neighborhoods and 354 sign
leaves per cell. Exact algebra: 12 groups. Rational checks: 4064
(81 remainder and 46 derivative decisions per cell). Exact comparison
checks: 146. The 33 ordered nodes are −1/64+k/2048, k=0,…,32.

- [Remainder cover](cover/certificate.json)
- [Rational reconstruction](rational_check.json)
- [Exact comparisons and negative controls](comparisons.json)
- [Exact tail algebra](algebra.json)
- [Figure data](plot_data.json)
