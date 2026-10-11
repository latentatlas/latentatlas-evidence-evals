# R30 review record

The accepted calculation is the 32-cell effective remainder cover in
`results/cover`, with exact algebra in `results/algebra.json`, rational
reconstruction in `results/rational_check.json`, and finite-value
consequences in `results/comparisons.json`.

| Layer | New work | Explicit prerequisites / limitations |
|---|---|---|
| Cusp and global dual identity | Check frozen R29 provenance; replay its audit | R03/R29 graph containment, uniqueness and seam arguments |
| Infinite tails | Recheck the five potential derivative inequalities at H=1/64 and all enlarged-v constants | R26 analytic active/inactive-prefix proof and weighted infinite-tail envelopes |
| Finite remainder | Fresh full sextic jets, 28 neighborhoods per cell, sign cover, repaired moments and scalar inversion | Analytic Taylor, support, contraction and compactness arguments of R25–R27 |
| Arithmetic | Independent 512-bit outward rational reconstruction on every cell | Transcendental interval jets, coefficient boxes and whole-tail bounds are explicit inputs |
| Coefficient sensitivity | Rational AD reconstructs δ₀′, C₂′ and C₄′ separately | R29 justified differentiation of root sums and validated derivative inputs |
| Actual-value comparison | Integrate coefficient derivative bounds, add both endpoint remainder allowances | Values compared at the same M; no derivative bound on the finite-M remainder |
| Figure | Exact rational formulas rendered as bounds | Pixel positions are rounded; no optimizer is plotted |

The finite moment target depends on ν and each ν permits a separate g.
The resulting amplitude comparison is meaningful for exactly this problem;
it is not evidence for financial cost, learning efficiency or physical energy.

The strongest current conclusion is a uniform remainder and pairwise
comparison at resolved separations. Full monotonicity is deliberately
left open. Taking d arbitrarily small while retaining a fixed absolute
error would be an invalid inference; the exact negative controls record
this limitation. They are inconclusive cases, not counterexamples to
monotonicity of the actual problem.

No fresh mpmath solve of the finite-M optimizer is claimed. R29's
independent integral diagnostics are checked by the prerequisite audit,
not recast as independent exact finite-budget optima. Agreement of
arithmetic implementations cannot replace review of the analytic proof.

Previous 30 manifests /1235 frozen entries are hash checked. The old
manuscripts are unchanged. No external referee, formal verification,
literature-priority conclusion, public release or submission is implied.
The mathematical result is suitable for inclusion in a new manuscript
after the full theorem chain and closest literature have been reviewed.

Two development failures were in checks around the computation. A plotting
QA assertion caught an automatic logarithmic tick outside the canvas;
explicit major ticks fixed it. The first audit incorrectly required the
Arb enclosure of 2e-5 to be an exact point. Since 1/50000 is not dyadic,
the correct assertion checks that the narrow interval contains that exact
rational. The separate rational checker already used the exact Fraction.
Both sources and failures are retained in [diagnostics](diagnostics/README.md).
Neither correction changed a producer or mathematical acceptance bound.
