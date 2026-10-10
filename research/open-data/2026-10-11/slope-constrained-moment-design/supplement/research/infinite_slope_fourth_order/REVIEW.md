# R23 — Claims, proof obligations, and limits

## What has been established in this package

| Claim | Evidence and qualification |
|---|---|
| Countably many switches admit the W5 fourth-order optimal-value formula under W2–W3 and the stated rank/topology assumptions. | Analytic proof W6–W17. All infinite exchanges use a displayed summable majorant. This is a human-readable proof, not proof-assistant verification. |
| The fixed theta family at the inherited exact Q and b* satisfies the new weighted hypotheses. | T1–T7 plus unchanged R12/R15 exact localization, root topology and rank certificates. Finite neighborhoods are reduced by continuity; a numerical value of the reduced radius is not claimed. |
| Theta has a finite fourth-order coefficient given by W4–W5. | Analytic corollary T8. No numerical enclosure or sign of that coefficient is supplied here. |
| A uniform unweighted quadratic center-motion bound is unsuitable for theta. | T9 proves the fixed-root coefficient grows like (4π/3)e^{4z_k}. Actual balanced shifts still stay smaller than a. |
| The independent exponential/trigonometric example has an exact geometric tail. | E1–E6; separate complex-primitives and direct piecewise-integral calculations. It is not the theta family. |
| Six implicit budgets in that example have certified exact optimum enclosures. | Arb endpoint signs, derivative signs, balanced residual, and periodic support proof. The budget and amplitude are jointly enclosed, not rounded and substituted back. |
| The fourth-order term improves the example's approximation at all six certified budgets. | Positive leading and fourth-order error enclosures and ratio strictly between 0 and 1. This is not an all-budget improvement theorem. |
| The theta weighted-majorant tail beyond root position 2 is <10^{-3500}. | Conservative T7 envelope, analytic decay/separation, Arb evaluation. This bounds the hypothesis sum; it is not the error in C₄ or in δ(M). |

## Adversarial checks of the proof chain

1. **Tiny tail denominators.** Pointwise simplicity alone does not control
   center motion. W2 and the square-weight condition W3 explicitly include
   the inverse crossing constants. T7 checks the sign of the resulting
   exponential coefficient rather than assuming rapid decay is enough.
2. **Infinite center IFT.** None is invoked. Scalar balanced cells exist
   individually, and a finite set of centers repairs the lower moments.
   The theorem is about the optimal value. Exact finite-M dual uniqueness
   and a smooth infinite-center optimum map are left open.
3. **Trial dual versus true dual.** b*+G⁻¹B a² is a trial path. W12 records
   its moment defect; W13 and W14 are different quantities before that
   defect is used. The exact algebra includes a general nonoptimal vector
   v as a negative guard against silently identifying those quantities.
4. **Termwise integration and limits.** W11 sums local differences, not a
   possibly divergent series of primitive values. Every normalized Taylor
   contribution is dominated in W12–W13; the per-root coefficient need not
   converge uniformly in k.
5. **Moment repair at fourth order.** The forcing is o(a²); the selected
   target derivatives are O(a²) because q*(z)=0. Hence the repair costs
   o(a⁴). An O(a²) moment defect without the choice v=G⁻¹B would not suffice.
6. **Coverage of budgets.** Continuity and divergence of A(a)/a give every
   sufficiently large M by the intermediate value theorem. No unsupported
   monotonicity of the repaired path is assumed.
7. **Implicit width.** a=A/M is retained during inversion. The coefficient
   is δ₀⁵(3t²−e), not δ₀⁵(t²−e). The R22 algebra is preserved and the
   infinite example supplies a separate integral check.
8. **Exact theta identity.** The finite parameter centers are not used as
   exact optimizers. All analytic bounds hold on a neighborhood inside the
   existing certified box; b* and Q remain the exact enclosed objects.
9. **Finite samples versus asymptotics.** The general theorem supplies a
   little-o statement, not a certified finite-budget accuracy percentage.
   The example's six pointwise certificates supply only their stated values.
10. **Prior explicit remainder.** R16's M^{-3} envelope remains valid.
    A smaller true asymptotic order does not invalidate a conservative
    explicit upper bound. Its existing numerical constants were untouched.

## Remaining work

The next numerical task is to enclose G, B and R at the **exact theta dual**,
including infinite tails and cancellation, then enclose C_{4,θ} and test
whether its sign is determined. An effective fourth-order remainder needs
additional quantified regularity and center-repair bounds; it is a separate
task after the coefficient. Uniformity along the cusp curve is also open.

The current theorem concerns bounded Lipschitz profiles. This package does
not independently transfer the fourth-order statement to a smoother class
or supply a new finite root-window statement for the modified kernel.
There is no new physical realization or LLM application claim.

The R19/R20 manuscript files were preserved. R23 is a research note for
possible later integration, subject to a separate expert proof and novelty
review. The closest-literature work in R18/R20 remains relevant, but the
limited contextual source check in this round establishes no priority.

## Checks and caught problems

Twelve exact algebra/inequality groups pass. Six Arb sample budgets supply
54 sample-value enclosures; separate 80/120-digit runs compare those 54
values and 78 coefficient values (132 comparisons in total). Three plots
were visually inspected. These diagnostics corroborate explicit parts of
the argument and do not prove the analytic theorem automatically.

The third theta derivative's manually entered expected x coefficient was
initially 2970. The exact recurrence rejected it; the correct coefficient
3270 was used before any successful output was written. The first figure's
legend/footer collision was also corrected. See
[development notes](results/DEVELOPMENT_NOTES.md). No frozen earlier
package was altered to conceal these issues.

[Proof](PROOF.md), [theta](THETA.md), [example](EXAMPLE.md),
[audit](audit_report.json), [manifest](manifest.json).
