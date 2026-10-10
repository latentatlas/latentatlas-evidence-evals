# R13 — Classical background and reading scope

Checked 21 September 2026. The proofs are written in PROOF.md; this is
targeted verification of established tools, not a priority search.

1. Richard Melrose, MIT 18.100B, *Ascoli–Arzelà theorem*,
   [official lecture PDF](https://math.mit.edu/~rbm/18.100B/Ascoli-Arzela.pdf).
   The statement and compactness argument on pages 1–2 were read.
   R13 applies the theorem on successive compact intervals and then
   uses diagonal extraction and dominated convergence. Compactness in
   global uniform norm on the half-line is not assumed.
2. Stephen Boyd and Lieven Vandenberghe, *Convex Optimization*, §5.6.1,
   [authors' book PDF](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf).
   The discussion of perturbed optimal values and their convexity was
   read (book pp. 249–250). This finite-dimensional discussion supplies
   classical context. R13 proves convexity directly by mixing feasible
   functions instead of importing a finite-dimensional duality theorem
   into the infinite-dimensional problem.
3. [R11 proof](../kernel_design_principle/PROOF.md) and
   [R12 proof](../kernel_norm_threshold/PROOF.md): moment right inverses,
   unrestricted infimum, full-support nonattainment and exact theta inputs.
   Their prior audit is [recorded separately](../full_chain_audit/DENETIM_RAPORU.md).

No novelty claim is made for compactness, convexity of a resource-value
function, smoothing/moment correction, or the basic fact that a slope
constraint obstructs an instantaneous sign transition. The specific
quantitative theta bounds and their relation to the fixed-Q geometry
still need external mathematical and literature-priority assessment.
