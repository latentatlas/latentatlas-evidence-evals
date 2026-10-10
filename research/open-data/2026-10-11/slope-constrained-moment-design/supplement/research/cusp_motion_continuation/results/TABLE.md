# R29 — Numerical record

Published statements (strict bounds):

| Quantity | Bound |
|---|---|
| Driver | −1/64 ≤ ν ≤ 0 |
| Derivative | 1.9×10⁻⁴⁰ < C₄′ < 5.3×10⁻⁴⁰ |
| Coefficient | 2.48374879×10⁻³⁹ < C₄ < 2.49203006×10⁻³⁹ |
| Endpoint gain | 2.96875×10⁻⁴² < C₄(0)−C₄(−1/64) < 8.28125×10⁻⁴² |
| Cover | 32 closed cells, half-width 1/4096 |
| Length ratio to R28 | 1024 |

Independent diagnostics below are approximations, not certified decimal values:

| ν | C₄ / 10⁻³⁹ | C₄′ / 10⁻⁴⁰ (finite difference) |
|---:|---:|---:|
| -0.01562500 | 2.486435320776 | 3.576554147301 |
| -0.01171875 | 2.487832809876 | 3.578590238789 |
| -0.00781250 | 2.489231094552 | 3.580627501604 |
| -0.00390625 | 2.490630175264 | 3.582665936425 |
| 0.00000000 | 2.492030052468 | 3.584705543930 |

The endpoint difference is approximately 0.224505% of C₄(0). The rigorous
gain is the interval above, not the diagnostic percentage.

14 exact groups; 17,088 rational decisions; 46 diagnostic solves at 23
distinct drivers; 240 derivative comparisons; 690 local value comparisons;
92 residual checks; 10 step comparisons; 120 precision comparisons.
Maximum relative two-precision derivative difference: 4.505803988647396704427915101550706185174e-63.

[Certificate index](cover/certificate.json), [rational reconstruction](rational_check.json),
[diagnostics](direct_check.json), [proof](../PROOF.md).
