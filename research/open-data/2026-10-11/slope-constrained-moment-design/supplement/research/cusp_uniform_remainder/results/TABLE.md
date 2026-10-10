# R27 quantitative results

The domain is the exact original cusp subarc ν∈[−2⁻¹⁶,0] and the
original-coordinate slope budget M≥2×10⁻⁵. The entries below are outward
rounded from the Arb output and, where applicable, the rational reconstruction.

| Quantity | Uniform bound |
|---|---:|
| Driver width | 2⁻¹⁶=0.0000152587890625 |
| τ' | (−0.107402,−0.107375) |
| λ' | (0.326200,0.326224) |
| μ' | (0.294035,0.294042) |
| f_ν | (3.335610,3.335649)×10⁻¹³ |
| D_ν | (0.0003634032,0.0003634160) |
| δ₀(ν) | (9.178490,9.178920)×10⁻¹⁰ |
| Γ_ν | (1.297389,1.297695) |
| C₂(ν) | (9.2015,9.2053)×10⁻²⁵ |
| C₄(ν) | (2.47,2.52)×10⁻³⁹ |
| Xi_ν | (143.29,165.09) |
| Initial dual radii | (2⁻²²,2⁻¹⁸,2⁻¹⁶) |
| Dual contraction rows | <(.025586,.038809,.026084) |
| Dual forcing rows | <(.131538,.154021,.134816) |
| Dual localization shrink factor | <0.160239 |
| Absolute bounds for v | (5,4,180) |
| Repair contraction rows | <(.010534,.014440,.008662) |
| Repair forcing rows | <(.358977,.489798,.291664) |
| K_d | <739740 |
| K_p | <4831937 |
| Feasible amplitude U | <9.178959760×10⁻¹⁰ |
| Common scalar upper endpoint margin | >1.76885×10⁻¹⁵ |
| Published lower remainder constant | 1.02×10⁻⁵³ |
| Published upper remainder constant | 1.64×10⁻⁵³ |

Consequently, for every ν in the arc and every M≥M₀,

    −1.02×10⁻⁵³/M⁶ < δ_ν(M)−P₄,ν(M) <1.64×10⁻⁵³/M⁶.

At M₀=2×10⁻⁵ the upper absolute error is 2.5625×10⁻²⁵, less than
0.001660 percent of the fourth-order term. The positive fourth-order
dominance ratio lies between

    1−1.033×10⁻⁵(M₀/M)² and 1+1.660×10⁻⁵(M₀/M)².

The coefficients in these statements are exact mathematical quantities;
rounding the printed coefficients introduces an additional error.

The independent 130-digit direct calculation gives these **diagnostic**
samples, rounded here for reading:

| ν | Approximate C₄(ν) |
|---:|---:|
| −0.0000152587890625 | 2.49202458264749079×10⁻³⁹ |
| −0.000011444091796875 | 2.49202595010147433×10⁻³⁹ |
| −0.00000762939453125 | 2.49202731755621791×10⁻³⁹ |
| −0.000003814697265625 | 2.49202868501172151×10⁻³⁹ |
| 0 | 2.49203005246798515×10⁻³⁹ |

This observed increase does not prove monotonicity between the samples.
The common enclosure above is conservative and is not the exact range.

Checks: 12 new exact groups; 116 outward-rational decision inequalities;
1180 numerical enclosure checks over two precisions and five drivers;
90 cross-precision comparisons, maximum relative difference about
2.134×10⁻⁷⁴. The numerical check has a finite cutoff and is not a
rigorous reintegration of the whole half-line.

[Certificate](certificate.json), [rational check](rational_check.json),
[direct diagnostic](direct_check.json), [proof](../PROOF.md), [review](../REVIEW.md).
