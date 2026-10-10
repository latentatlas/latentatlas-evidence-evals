# R28 — Quantitative motion of C₄

The exact domain is ν∈[−2⁻¹⁶,0], with differentiation in the original ν
coordinate. All coefficient and design definitions are inherited from R27.

| Quantity | Bound valid throughout the arc |
|---|---:|
| C₄'(ν), published | (2.82,4.35)×10⁻⁴⁰ |
| C₄'(ν), Arb (outward display) | (2.82714,4.34233)×10⁻⁴⁰ |
| C₄'(ν), rational AD (outward display) | (2.84853,4.33411)×10⁻⁴⁰ |
| C₄(ν), anchored at exact Q(0) | (2.49202340,2.49203006)×10⁻³⁹ |
| C₄(0)−C₄(−2⁻¹⁶) | (4.302978515625,6.6375732421875)×10⁻⁴⁵ |
| f'(ν) | (1.47911,1.48258)×10⁻¹⁴ |
| D'(ν) | (4.91582,4.91985)×10⁻⁶ |
| δ₀'(ν) | (2.82738,2.83815)×10⁻¹¹ |
| Γ'(ν) | (0.0080972,0.0134648) |
| C₂'(ν) | (7.83176,8.24908)×10⁻²⁶ |

The exact Arb/rational endpoints are retained as integer dyadics or
fractions in the JSON records. The interval theorem is C₄'(ν)>0; positive
δ₀' and C₂' do not establish monotonicity of δ_ν(M), because no bound on
the ν derivative of its finite-M remainder has been proved.

For any ν₁<ν₂ on this arc, multiply the published derivative endpoints
by ν₂−ν₁ to bound C₄(ν₂)−C₄(ν₁). The endpoints in this difference
inequality are not the exact extrema of the derivative.

The 110-digit direct integral re-solves give the following diagnostic
finite differences with step 2⁻²¹. Endpoint stencils are second-order
one-sided; the midpoint stencil is central.

| Driver | Approximate finite difference for C₄' |
|---:|---:|
| −0.0000152587890625 | 3.5846975744327364×10⁻⁴⁰ |
| −0.00000762939453125 | 3.5847015591800866×10⁻⁴⁰ |
| 0 | 3.5847055439318954×10⁻⁴⁰ |

The second step is 2⁻²⁰. Their largest relative C₄ derivative difference
is <4.878×10⁻¹⁵. The agreement does not rigorously bound the finite-
difference truncation error. In particular, the tiny apparent increase
of C₄' is not a proof of C₄''>0.

Checks: 26 exact groups, 44 outward-rational decisions; 13 original
integral cusp/dual re-solves at each of 80/110 digits; 146 diagnostic
comparisons including the new ninth template moment; 72 cross-precision
derivative comparisons with largest relative difference <2.787×10⁻⁶².
Both diagnostic integrators use 12 theta terms and cutoff 1.

[Certificate](certificate.json), [rational check](rational_check.json),
[direct checks](direct_check.json), [proof](../PROOF.md).
