# R31 constants and outcomes

All decimal bounds below are directed outward or exact conservative
constants, not estimates of optimal constants. Machine-readable full
endpoints are in [rational_check.json](rational_check.json).

| Item | Verified value/domain |
|---|---|
| Exact driver arc | −1/64≤ν≤0 |
| Slope budget | Every M≥2×10⁻⁵ |
| Ratio κ=−τ′/τ | .00259<κ<.00260 |
| Ratio f′/f | .0437<f′/f<.0451 |
| Weighted derivative coefficient a₀ | 1/16384 |
| Contraction constant c | 1/50 |
| Finite-u Arb maximum upper bound | <−.0217069 |
| Finite-u rational maximum upper bound | <−.0217085 |
| Infinite-u analytic upper bound | <−.0511166 |
| Whole-domain required upper bound | <−.02 |
| Actual optimal amplitude bounds | 9.17×10⁻¹⁰<δ_ν(M)<9.181×10⁻¹⁰ |
| Logarithmic value growth | log δ_ν₂(M)−log δ_ν₁(M)≥.02259(ν₂−ν₁) |
| Additive value growth | δ_ν₂(M)−δ_ν₁(M)>2.07×10⁻¹¹(ν₂−ν₁) |
| Minimum positive driver separation | None |
| Endpoint additive bound from R31 | >3.234375×10⁻¹³ |
| Exact algebra groups | 31 |
| Independent outward-rational decisions | 19,017 |
| Whole-u finite cells | 1,024 |
| Whole-driver inherited cells | 32 |
| mpmath diagnostic precisions | 60 and 90 decimal digits |
| Diagnostic integral/derivative/composition checks | 24 / 30 / 10 |

The two main comparison inequalities are valid simultaneously for all
pairs in the domain. They do not assert that δ is differentiable.
R30 gives a stronger endpoint lower bound; R31 supplies the missing
arbitrarily-small-separation conclusion. See [proof](../PROOF.md).
