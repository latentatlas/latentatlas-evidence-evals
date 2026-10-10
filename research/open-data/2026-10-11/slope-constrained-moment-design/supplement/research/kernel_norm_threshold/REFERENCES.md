# R12 — Established tools and source-reading scope

Checked 21 September 2026, Europe/Istanbul. This is targeted verification
of the tools and their contracts, not a literature-priority search for
the specific quantitative theta-kernel threshold.

1. Stephen Boyd and Lieven Vandenberghe, revised lecture slides with
   Parth Nobel, *Convex Optimization*, chapter 5, Duality.
   [Official Stanford slides](https://web.stanford.edu/class/ee364a/lectures/duality.pdf).
   The sections on the lower-bound property, equality-constrained norm
   minimization and weak duality were read. A feasible construction and
   a universal lower bound are classical ways to bound suboptimality.
   R12 supplies a self-contained integral version of the required
   inequality rather than importing finite-dimensional hypotheses
   without checking them. No general duality novelty is claimed.

2. FLINT project, `acb_calc` integration documentation.
   [Official integration contract](https://flintlib.org/doc/acb_calc.html).
   The integration section states the finite-path and holomorphic
   callback requirements and explains interval, Gauss–Legendre and
   adaptive-subdivision integration. We integrate an entire finite
   theta sum separately on the sign intervals and bound both improper
   tails analytically. Requested tolerances are not used as proof of
   accuracy; the returned enclosures are retained. This documentation
   check is not an independent validation of the FLINT library.

3. The classical moment-annihilation and L1-approximation background is
   recorded in [R11 REFERENCES](../kernel_design_principle/REFERENCES.md),
   including the distinction between smooth complex phase multipliers
   in Lazarev–Lieb and the positive real kernel changes considered here.
   The limited full-text access recorded there still applies.

The quantitative smoothing bound is proved directly in PROOF.md.
Positive convolution, cancellation of an odd transition error, exact
moment correction and equality-case nonattainment are standard tools;
they are not separately advertised as new inventions. The research
content is their explicit certified use to quantify this fixed cusp's
distance to an order-four zero in the stated relative norm.
