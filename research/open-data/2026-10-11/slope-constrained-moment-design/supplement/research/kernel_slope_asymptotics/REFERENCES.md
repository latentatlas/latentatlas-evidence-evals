# R15 — References and scope of the comparison

Checked 21 September 2026. This is a limited positioning check, not an
exhaustive novelty or priority review. No quotation is reproduced.

1. Daniel Wachsmuth, *Adaptive regularization and discretization of
   bang-bang optimal control problems*, Electronic Transactions on
   Numerical Analysis 40 (2013), 249–267.
   [Journal full text](https://etna.ricam.oeaw.ac.at/vol.40.2013/pp249-267.dir/pp249-267.pdf).
   The paper studies bounded controls in a tracking problem with
   quadratic Tikhonov regularization. Its measure condition on small
   switching-function values supports convergence-rate estimates.
   This is relevant background for rates near sign-type optimizers.
   It is not cited as proving our hard derivative-bound, minimum-L∞
   moment problem or its explicit switch-sum coefficient.

2. Nikolaus von Daniels, *Tikhonov regularization of control-constrained
   optimal control problems*, arXiv:1704.05797.
   [Author preprint abstract](https://arxiv.org/abs/1704.05797).
   Only the abstract was used for positioning: source/measure
   conditions and regularization error estimates are discussed.
   No exact theorem from this preprint is invoked in R15.

3. *Regularization and implicit Euler discretization of linear-quadratic
   optimal control problems with bang-bang solutions* (2016).
   [Publisher abstract and introduction](https://doi.org/10.1016/j.amc.2016.04.028).
   The accessed text concerns regularization, discretization error and
   switching-function growth conditions. It does not establish the
   R15 formula; it identifies a body of adjacent work that must be
   compared before making a priority claim.

The local 1/3 triangular-loss integral, convex dual equality and
implicit-function correction in R15 are written out in the proof.
The publication contribution should be assessed as a precise moment-
design theorem, verified applicability and numerical constants at the
theta cusp, together with the prior geometry. Neither a literature
search without a match nor a successful computation proves novelty.

Further comparison should target hard control-rate constraints,
minimum-amplitude moment interpolation and switch-time asymptotics.
The present package does not claim that a soft quadratic regularizer
is mathematically equivalent to Lip_u(h)≤M.
