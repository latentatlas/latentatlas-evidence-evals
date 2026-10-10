# R27 — Evidence and adversarial review

The result is uniform on I×[M₀,∞), I=[−2⁻¹⁶,0], M₀=2×10⁻⁵.
Its exact coefficients depend on ν. It permits a separate design at
each cusp; it does not identify one common design for the curve.

| Obligation | Evidence |
|---|---|
| Same exact cusp branch | R03 identity; integrate its velocity from exact Q(0), then tighten with R09 Taylor bounds. |
| Valid sextic Taylor remainders | Every segment has ν≤0 and λ,μ within the positive-moment majorant domain. |
| Moving f_ν | New four-variable Taylor expansion; the target is not held at f₀. |
| Moving exact dual | Uniform sign cover, tail phase, Hessian/gradient bounds and contraction. Convexity identifies the global optimum. |
| Tightened solution | A posteriori η/(1−q)<0.160239; root jets recomputed on the smaller box. |
| Moving D_ν | L¹ change bounds and optimality at both parameters, equation U9. |
| Positive C₄ | Full root sums, validated matrix residual, parameter uncertainty, and agreement of Arb/rational bounds. |
| Sextic weight derivatives | νu⁶ included through order five; 12 exact groups extend the tail estimates. |
| Infinite tail | Negative ν preserves the majorizing density; all active/inactive roots and integral tails retained. |
| Finite support and repair | 28 neighborhoods, 354 sign leaves, three-center repair recomputed on the full new trial box. |
| Every large M | R26 scalar feasibility/inversion with new uniform constants; no prefix continuity assumed. |
| Separate arithmetic | 116 outward-rational decision inequalities; interval inputs explicitly accepted. |
| Independent diagnostics | Original-integral solves at five drivers, 90/130 digits, 1180 enclosure checks, 90 precision comparisons. |

The initial jet code raised a TypeError by attempting `Arb // int`.
The factorial ratio is now computed as an integer first. The initial
source and failed run are preserved. The next coarse enclosure passed
dual contraction but failed the combined C₄>0/Xi>0 test. This was an
inconclusive bound, not a counterexample. A posteriori tightening and a
dyadic solve seed resolved it at the same driver width. See the
[diagnostic history](diagnostics/README.md).

Logical traps checked:

1. Nearby numerical cusps do not establish identity with Q. R03 supplies
   that exact identity, used as the anchor here.
2. Quartic derivatives cannot be reused at ν≠0 with the sextic term
   omitted. The new model includes all its product-rule terms.
3. Negative ν is essential to the reused moment majorants. A positive
   driver interval is not covered by this proof.
4. Infinitely many roots need not move a bounded distance when τ changes.
   The finite sign motion is local; every sign difference after 1 is
   covered by an entire integral-tail bound.
5. Sampled dual solutions do not prove continuum existence. The new
   contraction covers the entire parameter/coefficient box.
6. Fixed-Q δ₀,D,C₂,C₄ cannot be held constant on the curve. They are
   recomputed as interval families.
7. A changing finite prefix need not be continuous. The auxiliary scalar
   feasibility proof avoids that assumption.
8. A uniform bound for separate designs is not one shared perturbation.
9. An increasing numerical sample is not a monotonicity theorem; a common
   interval is not the exact range of C₄ or a claim of constancy.
10. Moment cancellation alone does not establish all geometric
    nondegeneracy conditions of the modified kernels. The next derivative
    and unfolding rank need separate bounds.

External mathematical review remains necessary. The rational reconstruction
accepts cusp/Taylor enclosures, transcendental jets, root/sign values,
sign-motion integral estimates and whole-tail bounds as inputs. The direct
check uses finite truncations and gives diagnostic agreement. Neither
mechanically proves the analytic chain.

This is a quantified local family version of R26; no claim is made that
continuity itself is novel. Full-arc coverage, monotonicity, C₆, a shared
design, literature priority and journal acceptance remain separate questions.
Frozen prerequisites and manuscript versions are preserved.

[Proof](PROOF.md), [numbers](results/TABLE.md), [reproduction](README.md).
