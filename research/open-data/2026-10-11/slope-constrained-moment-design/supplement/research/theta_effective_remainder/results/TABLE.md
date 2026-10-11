# R25 — Computed bounds and interpretation

The theorem uses exact coefficients and the finite window 2×10⁻⁵≤M≤2×10⁻³.

    −9.593×10⁻⁵⁴/M⁶ < δ(M)−δ₀−C₂/M²−C₄/M⁴ <1.488×10⁻⁵³/M⁶

## Error at three example budgets

The inequalities hold continuously over the full window; the table is only an illustration.

| M | C₄/M⁴ (approximately) | Upper bound for absolute fourth-order error | Error / fourth term, percent (upper bound) |
|---|---:|---:|---:|
| 2e-5 | 1.5575187813e-20 | 2.3250000000e-25 | 0.001492758891 |
| 2e-4 | 1.5575187812e-24 | 2.3250000000e-31 | 1.492758891e-05 |
| 2e-3 | 1.5575187812e-28 | 2.3250000000e-37 | 1.492758891e-07 |

The last column is a displayed numerical value of a rational upper bound; the exact formulas above determine the bound. Coefficient midpoint rounding is not included in this error.

## Internal constants

The following displays are approximate readings of enclosing/upper bounds. The JSON certificate stores full dyadic intervals.

| Quantity | Display |
|---|---:|
| Kstar6 | 175404.011663 |
| K6_finite | 467723.212389 |
| K8dual | 2564483127.13 |
| K8primal | 9.3828694965e+14 |
| tail_objective_bound | 5.60900659844e-67 |
| tail_as_sixth_bound | 3.05383366796e-27 |
| Kdual6 | 467732.765833 |
| Kprimal6 | 3963114.48309 |
| maximum_loss | 1.61124249557e-09 |
| amplitude_upper | 9.17874865649e-10 |
| Kpoly | 3.22937023851e-57 |
| inversion_derivative_lower | 0.000363406863969 |
| Kminus (before rounding up) | 9.59283889646e-54 |
| Kplus (before rounding up) | 1.48722542112e-53 |

The strict published constants include rounding slack over both the Arb and independent rational calculations.

[Proof](../PROOF.md), [review](../REVIEW.md), [certificate](certificate.json), [rational reconstruction](rational_check.json).
