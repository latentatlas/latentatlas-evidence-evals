# R25 — Claims, dependencies and adversarial review

The new mathematical statement is E2 in [PROOF.md](PROOF.md):

    −9.593×10⁻⁵⁴/M⁶ < δ(M)−δ₀−C₂/M²−C₄/M⁴ <1.488×10⁻⁵³/M⁶
    for every 2×10⁻⁵≤M≤2×10⁻³.

The exact coefficients, fixed Q, coordinate u and moment targets are
unchanged. This is a finite-window theorem about the optimal value.
The infinite kernel and the true moment equations are retained.

## Why the numerical certificate supports this particular claim

| Obligation | Evidence |
|---|---|
| Unknown exact Q and b* | R24 input balls, whose R12/R15 analytic localization is inherited. |
| Trial dual leaves the old tiny cube | New enlarged trial cube is evaluated explicitly, rather than treating the old root certificate as uniform on it. |
| Finite-domain root topology | Positive signed density derivatives in 28 disjoint neighborhoods, endpoint signs, and 354 interval leaves on their full complement. |
| All omitted theta terms | Sixth-degree derivative polynomials through the fifth derivative; a uniform ratio bound encloses the omitted series. |
| Analytic local cancellation | 15 exact rational-polynomial/inequality groups, including a wrong amplitude-feedback negative control. |
| Exact feasibility | A three-center contraction with row bounds below 0.002452 and forcing below 0.418264 proves exact lower moments for every width in the interval. |
| Arbitrary feasible competitors | Balanced-cell integration by parts and strong concavity bound the dual support. A trial profile alone would not prove a lower bound for the optimum. |
| Whole infinite tail | Integrated absolute density tails, plus R24 Gamma/G/B/R root tails; both are included before inverting the amplitude. |
| Continuous budget range | Uniform contraction gives continuous centers, and endpoint bounds give interval coverage by the intermediate value theorem. No sampling or unproved monotonicity. |
| Numerical arithmetic | 120-digit Arb bounds and independent outward 512-bit rational reconstruction; both fit strictly inside the published constants. |
| Independent corroboration | 80/110-digit direct differentiation and 20/28-node piecewise Gauss integration at three widths. Diagnostic, not a proof of the uniform claims. |

## Failure modes reviewed

1. The support and primal constructions are different. Only the repaired
   primal is required to satisfy the lower moments; the trial multiplier
   is usable for a lower bound because every feasible competitor has zero
   lower moments.
2. The infinite sign pattern is not truncated without compensation.
   The primal is constant past 1; its moment difference there is bounded
   by 2∫|q_j|. The support tail has its own objective bound.
3. Root identities are used only at true roots. In derivative bounds
   on neighborhoods, all product-rule terms, including those containing
   the nonzero residual value away from the root, are retained.
4. Fifth-order odd terms are averaged exactly. Taylor's residual is
   bounded using an even sixth power, which avoids a false cancellation
   or an unexplained sixth-order estimate.
5. Finite sums of the quadratic lower-moment coefficient do not equal
   zero. Their full infinite sum is zero; the missing coefficient tail
   is explicitly bounded.
6. Objective stationarity is taken for q_b, not q*. At the chosen centers
   the q_b average is order a⁴, so an order-a⁴ repair has an order-a⁸ cost.
7. Preconditioner entries are exact dyadic numbers; the contraction
   verifies their adequacy. A printed inverse is not used as an exact inverse.
8. The residual polynomial from amplitude inversion retains all terms
   through degree twelve. Only the first three coefficients are set aside,
   with their exact cancellations checked separately.
9. The endpoint interval a_min≤a≤a_max is essential. Tail constants
   divided by powers of a_min cannot be carried unchanged to a→0.
10. The displayed δ₀ uncertainty can exceed the proved error in P₄
    with exact coefficients. Extra decimal digits of δ(M) are not claimed.

## Interpretation

The fourth-order coefficient now has a useful, rigorously bounded error
on a concrete continuous budget interval. The leading approximation
δ₀+C₂/M² underestimates the true value throughout that interval.
The sign of the remaining error after adding C₄/M⁴ is not determined.

This is not a sixth-order coefficient or a global O(M⁻⁶) asymptotic
theorem. It does not establish the smallest valid M, cover all M above
2×10⁻⁵, prove uniqueness of the true finite-M optimizer, or prove
uniformity along the cusp curve. The next mathematical extension would
need a width-dependent tail strategy or uniform higher weighted estimates.

The proof is an analytic manuscript supported by validated computations.
The audit does not mechanically prove the analytic lemmas, and no external
expert review or proof-assistant formalization has occurred. The terminology
is made explicit in [the user's terminology note](CERTIFICATION_TERMINOLOGY_TR.md).
No claim of literature priority, physical applicability or journal acceptance
is added. No manuscript was submitted or published.

[Reproduction](README.md), [numbers](results/TABLE.md),
[figure caption](FIGURE_CAPTIONS.md), [audit](audit_report.json).
