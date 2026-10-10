# R26 — Evidence boundary and adversarial review

The new statement is G2 in [PROOF.md](PROOF.md): the same explicit
fourth-order error as R25 holds for **all** M≥2×10⁻⁵ at the fixed
exact cusp Q. The numerical constants have not been loosened. The new
content is the uniform active/inactive tail argument and budget coverage.

| Obligation | Evidence and dependency |
|---|---|
| Exact problem and coefficients | R12/R15 localization and sign-moment identities; R23 formulas and R24 coefficient balls. The present package does not independently rebuild that entire analytic chain. |
| Valid finite-root constants for every 0<a≤a₀ | Only R25's a_min-independent local, contraction, support and scalar-inversion bounds are inherited. Its fixed-tail/a_min terms are discarded. R25's audit and interval producer are rerun. |
| Parameter-dependent root geometry | Phase representation valid on the enlarged trial box, root motion bound, and fresh positive Arb enclosure on [1,1.001]. |
| Active tail roots have valid cells | a exp(4z)≤ε gives disjoint width-6a neighborhoods, bounded density ratios, signed derivative >200w(z)z³, and containment of approximate and balanced ramps. |
| High derivatives on cells | Exact theta polynomial recurrence and product-rule bounds through order five; omitted theta-series terms controlled by a geometric ratio. |
| All infinitely many coefficient terms | Weighted root sums S₁₂,S₁₆,S₂₄, including all roots after 1. No finite sample establishes this coverage. |
| Inactive profile transitions | The elementary weighted tail inequality G4 and the integral cut L=z_n−3a yield constants for a⁴ moments and a⁶ targets. The integral-shift factors are retained. |
| Exact lower moments | The same three-center contraction with newly bounded forcing; the root prefix is fixed while solving for those three corrections. |
| Lower bound on the optimal amplitude | Balanced-cell support estimate for arbitrary feasible competitors, not just the constructed profile. |
| Upper bound at every budget | The auxiliary scalar polynomial J_M has a root with a feasible rescaled profile. No continuity of the adaptive prefix is assumed. |
| Arithmetic | 22 exact check groups, 120-digit Arb evaluation, independent outward 512-bit rational reconstruction of 22 decision inequalities. |
| Separate corroboration | Original-density mpmath derivatives and 20/28-node ramp quadrature at 90/130 digits: 600 local diagnostic inequalities and 40 precision comparisons. |

## Failure modes examined

1. A fixed positive tail bound is not O(a⁶) as a→0. It must not be
   absorbed using R25's a_min in a theorem with no lower width. R26
   replaces that step with G4 and exponential weights.
2. The center coefficient κ grows along the tail. No uniform bound on
   κ is asserted. The bound |κ|≤46e^{4z} is combined with the active
   condition; it yields the needed cell containment at each width.
3. A neighborhood is not a root. G8 retains the product term involving
   r*(x), bounding it by 2800az³. It never sets that term to zero
   throughout the neighborhood.
4. Near the cutoff, trial roots move. The first inactive original root
   is buffered by 3a, which exceeds the <3a² root motion. All included
   balanced ramps finish before this cut. A positive gap after 1
   prevents the first tail cell from falling outside the tail bounds.
5. The integral-shift constants are 72a₀ and 48a₀ for L=z_n−3a.
   Omitting that shift would understate the normalized tail estimates.
6. Active moment coefficients do not sum to zero by themselves. The
   full infinite coefficient is B−Gv=0; the omitted part is bounded
   separately before performing exact moment repair.
7. The dual support and primal target need different estimates. Balanced
   cells bound all competitors; only the three-center repaired primal
   must obey exact moment constraints.
8. A changing finite prefix need not depend continuously on a. R25's
   continuous-width intermediate value theorem is not imported. G12
   instead uses a continuous scalar polynomial at each fixed M, then
   selects the corresponding width and rescales a feasible profile.
9. A unique auxiliary scalar root is not a unique true optimizer.
   The construction bounds the optimal value; it does not identify the
   infinite-dimensional optimizer in closed form.
10. Bounded M⁶[δ−P₄] does not imply its convergence. C₆ remains open.
    The remainder after the positive fourth-order correction has no
    asserted sign.
11. The theorem uses exact coefficients. Their printed decimal uncertainty
    can exceed this approximation error, especially for very large M.
12. A sample of distant switches does not certify an infinite tail.
    The independent diagnostic checks test for implementation/algebra
    mistakes; G4–G10 supply the uniform mathematical argument.

## Current conclusion and remaining review

The proof gives an explicit O(M⁻⁶) remainder and a sufficient onset for
positive fourth-order dominance in the **fixed-Q** theta problem.
The onset is not proved minimal. No uniform theorem along the cusp
curve, sixth-order coefficient, physical model, exact finite-M optimum,
literature priority or journal acceptance follows from this package.

This is an internally reviewed analytic argument with validated numerical
enclosures. It still requires independent mathematical review, especially
of the inherited localization, support arguments and coefficient identities.
The rational checker trusts the supplied transcendental enclosures; the
audit verifies evidence and reproduces arithmetic, not every analytic
implication. No proof-assistant formalization or external review occurred.

The earlier 26 manifests/1070 entries and both existing manuscript versions
are preserved. The plotting diagnostic and improved evidence recording
are retained in [diagnostics](diagnostics/README.md). No public upload,
submission or external message was sent.

[Reproduction](README.md), [table](results/TABLE.md),
[figure caption](FIGURE_CAPTIONS.md), [audit](audit_report.json).
