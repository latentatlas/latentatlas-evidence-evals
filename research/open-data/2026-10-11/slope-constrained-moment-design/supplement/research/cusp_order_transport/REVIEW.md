# R31 evidence and review boundary

The analytic chain in [PROOF.md](PROOF.md) has five distinct obligations:

1. **Identity.** The exact cusp graph is inherited from R29, including
   seam identification, and its 32 cells are hash checked. τ decreases
   and f is positive. The driver domain is the exact closed interval.
2. **Feasible transport.** The weight η⁴(f₁/f₂)w₂(ηu)/w₁(u) has the
   correct Jacobian and powers for all four moment constraints. Exact
   symbolic checks and independent finite-integral diagnostics support
   the analytic change-of-variables argument.
3. **Whole-domain norm bound.** Cusp caps, the fresh Arb log-theta
   interval cover, its omitted theta-series tails, and an analytic
   infinite-u estimate prove r+κ+a₀|rᵤ|<−1/50. A 512-bit outward
   rational checker reconstructs all operations from the explicit
   transcendental inputs. No finite sample set replaces this condition.
4. **Comparison.** The characteristic inequality controls
   ηT+a₀|Tᵤ|; the exact optimizer exists by R30 and has amplitude/M<a₀.
   This gives feasible transfer and hence actual-value ordering, with
   no differentiation of the optimizer or remainder.
5. **Preservation.** All 31 prior manifests and 1,298 frozen file entries
   are checked. R31 freezes separately; publication-preparation export
   retains prior releases and verifies a copied replay.

The 60/90-digit mpmath diagnostics test 24 matched-domain integral
comparisons, 30 spatial derivative checks and 10 semigroup comparisons.
They use rounded R29 points and 12 theta summands. They are not an
independent interval certificate or a solution of the finite-M optimizer.

Four development failures are preserved in [diagnostics](diagnostics/README.md).
The mathematical bound −1/50 and all old inputs stayed fixed. The
independent rational computation has 19,017 successful decisions; the
exact algebra has 31 groups. A missing-Jacobian negative control is
included. These counts measure recorded checks, not independent theorems
or a probability that the manuscript is correct.

The fresh audit regenerates exact/rational outputs and diagnostics. With
`--with-arb`, it also regenerates the new transcendental cover and the
R30/R29 prerequisite chain. Successful numerical outputs are compared
byte for byte. Shared helper code and explicit inherited inputs are
listed by hash; this is not complete implementation independence.

No claim here of finite-M differentiability, uniqueness of optimizer,
Z_M ordering at arbitrarily close drivers, C₆, a larger arc, smaller M,
a common g or common target, a physical application, optimal constants,
literature priority, formal verification, external review or acceptance.
The theorem's analytic steps still warrant specialist review before
submission. The standard tools are identified in [LITERATURE.md](LITERATURE.md).
