# R28 — Review of derivative claims and evidence

The central result is the uniform positive ν derivative of the exact
R27 coefficient C₄. Its scope is the same short interval [−2⁻¹⁶,0].

| Obligation | Evidence and argument |
|---|---|
| Identity of the cusp and dual | R27 exact objects and complete root cover retained. |
| Differentiate the moving target | V5/V7 use D₄,D₅,D₇,D₉ and the cusp velocity. |
| Differentiate the optimal dual | Differentiate all three sign moments; solve G b'=A with a validated inverse residual. |
| Avoid circular tail assumptions | The tail of A is bounded at fixed b before b' is solved. Only later derivative tails use the verified coarse bound on b'. |
| Include moving boundaries | Every finite root has velocity V8; sign-moment boundary terms have the factor 2 and correct sign. |
| Include higher u derivatives | Total third-jet motion includes q*'''' z'; sextic derivatives are retained. |
| Avoid unnecessary v' cancellation | Stationary quadratic representation yields P'=B'ᵀv−½vᵀG'v. |
| Differentiate infinite root sums | New uniformly summable derivative envelopes cover every root after 1. |
| Retain all theta terms | Local omitted-series bounds and new integral truncation/half-line bounds are explicit. |
| Rational arithmetic crosscheck | Forward AD reconstructs quotient/product derivatives with 512-bit outward rational intervals. |
| Independent numerical mechanism | Original integral systems are re-solved at nearby drivers and finite-differenced; C₄' formula is not used. |
| Quantified monotonicity | Integrate the strict derivative band; exact R24 anchor supplies the narrower value band. |

The following inferences would be invalid and are not made:

1. Positive C₄ at each point does not imply that C₄ increases. The new
   derivative proof is required.
2. Holding b fixed while moving the cusp omits the implicit-dual response.
   Holding the roots fixed omits their total-derivative contributions.
3. A small coefficient tail does not automatically give a small derivative
   tail. This package derives different envelopes for the latter.
4. Pointwise differentiability of summands does not alone justify
   differentiation of an infinite sum. The new uniform majorants are needed.
5. A derivative bound on this tiny arc does not establish the direction on
   [−29,0], nor does the observed change of C₄' prove convexity.
6. A bound on the value of the finite-M remainder does not bound its ν
   derivative. Monotonicity of δ_ν(M) is not asserted.
7. Direction depends on the chosen driver orientation. The theorem uses ν,
   not an unspecified coordinate or arclength.
8. A passed replay is evidence of reproducibility and the stated numerical
   inequalities. It is not a mechanical proof of the analytic chain or an
   independent referee's judgment.

All 26 exact groups and 44 rational decisions passed. The direct check
contains 26 cusp/dual re-solves (13 at each precision), 146 enclosure
comparisons and 72 cross-precision comparisons. Finite differences use
second-order one-sided endpoint stencils and a central interior stencil;
two step sizes agree. No rigorous finite-difference truncation bound is
claimed, and no continuum statement is inferred from these samples.

The rational check accepts inherited cusp/dual/velocity boxes, local
transcendental jets, sign-motion and integration-error enclosures, and
analytic infinite-tail bounds as inputs. The producer replays the new
integral and jet calculations, but the proof still depends on the frozen
R03/R09/R12/R24/R27 chain. Literature priority and external mathematical
review are open. R19/R20 manuscripts are preserved.

[Proof](PROOF.md), [numbers](results/TABLE.md), [reproduction](README.md).
