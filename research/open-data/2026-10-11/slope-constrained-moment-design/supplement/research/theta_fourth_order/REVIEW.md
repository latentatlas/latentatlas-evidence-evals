# R24 — Evidence and claim review

## The new claim

For the exact fixed theta cusp Q and exact unrestricted dual b* already
certified in R12/R15, the fourth-order coefficient of R23 satisfies

    2.49203004×10⁻³⁹ < C₄,θ < 2.49203006×10⁻³⁹.

In particular it is positive. Combined with R23, this implies eventual
underestimation by δ₀+C₂/M². The numerical onset and an effective
fourth-order remainder remain open. This is the theta family itself,
not the separate periodic control example in R23.

## Evidence chain

| Input or step | Role and check |
|---|---|
| Frozen R12/R15 exact Q and b* localization | Establishes which mathematical object is being evaluated. Its parameter uncertainty is propagated, not replaced by a midpoint. |
| R15 strong convexity and gradient bound | Tightens the exact-dual radius to <4.130×10⁻¹⁴ by an analytic inequality; does not introduce a new optimizer guess. |
| Inherited finite root topology | Gives existence and uniqueness in each of 28 root boxes; 31 accepted mean-value contractions tighten the boxes. |
| Root product identities | q*''' at a root uses w,w',w'' and residual derivatives through order three; the vanished w'''r term is not omitted away from roots. |
| Fresh Arb local jets | Includes twelve theta terms and explicit bounds for all omitted terms, at 120 decimal digits. |
| Tail envelopes for Γ,G,B,R | Covers every root after 1 by phase separation and decreasing positive envelopes. The R23 weighted-majorant bound is not misused as a C₄ error. |
| Gram solve | Positive principal minors and a Neumann residual estimate enclose G⁻¹B. The computed inverse's midpoint is only a preconditioner. |
| Independent rational reconstruction | Rebuilds local coefficients, all sums and the residual solve with outward 512-bit dyadic rounding. Its final C₄ interval lies inside the same published bounds. |
| Independent numerical calculation | At 80/120 digits, uses the original kernel, numerical differentiation at newly solved roots, LU solution and 72/96-point Gauss quadrature. It is corroboration at central inputs, not the exact-optimizer proof. |

## Specific failure modes checked

1. The factors 2u and 2τ are retained in the p-derivative product rule.
2. Both switch orientations are tested in the G, B and R algebra.
3. The exact zero identity is applied only to jets at a certified root.
4. Tail division by a small density is reduced analytically; explicit
   bounds for w'/w and w''/w retain the necessary exponential factors.
5. Tails for G and B are added before solving for the moment penalty P.
   Computing P first and adding only an R tail would be insufficient.
6. Matrix error is propagated into P and hence into Xi=R−P and C₄.
7. A deliberately wrong minus/plus choice for P gives a disjoint
   coefficient interval in the rational negative control.
8. The independent check computes D and f₃ by quadrature, rather than
   copying their displayed coefficient values. Its truncated numerical
   integral is identified as diagnostic; rigorous tails are elsewhere.
9. The two-term ratio plotted at finite M is not labeled an optimum
   approximation error. No numerical M₁ is inferred from a little-o term.
10. The new leading coefficient agrees with the existing R15 enclosure.
    The existing explicit R16 remainder and all earlier results are preserved.

## What the counts mean

Fifteen exact algebra/inequality groups pass. The rational checker verifies
31 contractions and compares 588 reconstructed local quantities with the
Arb records, then independently encloses the final coefficient. The local
overlap checks are diagnostics; the final published interval is justified
by the complete reconstructed interval, not by overlap alone.

Each numerical precision run compares 504 root/jet/local-coefficient values,
12 final coefficient values and 15 matrix/vector values with the certificate:
531 comparisons per run, 1062 over the two precisions. This count includes
each root position once. The computed f₃ at the central Q is not required
to fit the much tighter exact-Q f₃ input interval and is not included in
those 12 coefficient comparisons. Relative precision differences of all
13 computed scalar values, including f₃, are <10⁻⁵⁵.

These checks do not prove the analytic R23 theorem mechanically, establish
literature priority, or replace external expert review.

## Interpretation and remaining question

The result turns the previous existence/formula statement into a signed,
validated coefficient for the original base example. It refines the
large-M cost law. The normalization, local-shape and moment contributions
are about the same base problem; they are not costs of independently
removing or adding constraints to a different optimization problem.

Next, an effective fourth-order remainder is needed to determine a
concrete budget range where the refined expansion is provably accurate.
This requires quantified higher derivatives and moment-repair bounds.
Uniform variation along the cusp curve is a separate question. No new
physical realization, smooth-class equivalence at fourth order, or
finite root-window result is asserted here. The R19/R20 paper is not
rewritten in this package, and no public release or submission occurred.

[Proof](PROOF.md), [table](results/TABLE.md), [audit](audit_report.json),
[reproduction](README.md), [diagnostic context](diagnostics/README.md).
