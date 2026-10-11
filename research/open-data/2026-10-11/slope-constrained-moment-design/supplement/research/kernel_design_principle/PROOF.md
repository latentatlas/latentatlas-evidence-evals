# R11 — General moment control and the distance to a pinned order-four zero

21 September 2026. The general arguments below are analytic proof drafts;
their ingredients are classical finite-dimensional moment control and
L1 approximation. No claim of priority or external mathematical review
is made. The final section has separate arithmetic and quadrature checks.

## 1. Assumptions, fixed coordinates, and the admissible changes

Fix a real point Q=(τ,λ₀,μ₀,ν₀), with τ≠0. Let K≥0 be measurable and
write

\[
d\rho(u)=K(u)e^{\lambda_0u^2+\mu_0u^4+\nu_0u^6}\,du,
\qquad u\in(0,\infty).
\tag{1}
\]

Assume this measure has positive density almost everywhere on some
nonempty open interval. Assume, for some η>0,

\[
\int_0^\infty e^{\eta(u+u^2+u^4+u^6)}\,d\rho(u)<\infty.
\tag{2}
\]

This convenient sufficient assumption gives all needed moments and
analytic dependence on t and the three polynomial controls in a
neighborhood of Q. We do not assert that it is necessary. The original
theta kernel meets (2) for every finite η. For the full-support result
in Section 4 we additionally require the density to be positive almost
everywhere on all of (0,∞).

The admissible relative change is a **single fixed real bounded
measurable function h**, independent of all four moving coordinates:
K_h=K(1+h). The cost is δ=||h||∞, using essential supremum on the
integration domain. For δ<1, K_h≥(1−δ)K almost everywhere. In particular
it remains strictly positive almost everywhere that K is positive.
For continuous multipliers the amplitude bound holds pointwise.
This is an amplitude constraint;
it imposes no frequency or derivative bound on h. Even extensions to
the real line are understood when discussing cosine transforms.

Set

\[
p_j(u)=(2u)^j\cos(2\tau u+j\pi/2),\quad
f_j=\int p_j\,d\rho,\quad L_j(h)=\int p_jh\,d\rho.
\tag{3}
\]

At Q the modified integral has derivative f_j+L_j(h). Suppose the
base point is an ordinary order-three zero:

\[
f_0=f_1=f_2=0,\qquad f_3\ne0.
\tag{4}
\]

Keeping the zero at the exact same Q requires L₀=L₁=L₂=0. Turning
it into a zero of order at least four additionally requires L₃=−f₃.
No coordinate relocation or approximate moment cancellation is allowed.
Order exactly four and a rank-three control unfolding are separate
conditions, addressed below.

## 2. Local control is a general principle

**Lemma 1 (independent jets).** For every finite m, the functions
p₀,…,p_m are linearly independent on every nonempty open interval,
and also as elements of L1(ρ).

**Proof.** A linear relation has the form
P(u)cos(2τu)+Q(u)sin(2τu)=0, where P and Q are polynomials whose
coefficients encode respectively the even and odd jet coefficients.
Vanishing almost everywhere on an interval of positive density forces
this analytic function to vanish identically. The complex identity is

\[
(P-iQ)e^{2i\tau z}+(P+iQ)e^{-2i\tau z}=0.
\]

If P−iQ were nonzero, this would express e^{4iτz} as a rational
function. Its exponential growth or decay along an imaginary ray
contradicts the polynomial asymptotics of a nonzero rational function.
Thus P=Q=0, and all jet coefficients vanish. ∎

**Theorem 1 (smooth bounded right inverse).** For every finite m,
the map h↦(L₀(h),…,L_m(h)) is onto R^{m+1}, even when h is
restricted to real smooth functions compactly supported inside a fixed
interval where the density is positive. There is a bounded linear
right inverse R_m, with a finite constant C_m such that

\[
\|R_m v\|_\infty\le C_m\|v\|_\infty.
\tag{5}
\]

Consequently every sufficiently small specified jet change can be
realized while retaining K_h≥(1−C_m||v||∞)K, with a strictly positive
relative factor. The kernel is positive wherever the original K is.

**Proof.** Choose a smooth nonnegative bump χ with compact support
inside the positive-density interval and positive on a subinterval.
The Gram matrix

\[
B_{ij}=\int\chi p_i p_j\,d\rho,\qquad0\le i,j\le m
\]

is positive definite by Lemma 1. Define

\[
(R_mv)(u)=\chi(u)\sum_{j=0}^m(B^{-1}v)_j p_j(u).
\tag{6}
\]

Then L_i(R_mv)=v_i exactly. One valid constant is
C_m=Σ_j ||χp_j||∞ Σ_k |(B^{-1})_{jk}|. Compact support makes it
finite, giving (5) and the stated positivity bound. ∎

For example m=4 and v=(0,0,0,a,b) keep Q pinned while prescribing
small changes in f₃ and f₄ independently. A specific four-cosine
subspace need not have full rank; this must be checked in that
subspace. The full smooth function space has no such rank obstacle
under the stated assumptions.

This theorem does not give a uniform numerical C_m for all kernels,
does not guarantee a large target under a small amplitude budget,
and is not claimed as a new general method. It identifies which
part of our earlier construction is a general mechanism. The
quantitative cost of a finite target is the selected extension.

## 3. Exact reduction of the minimum relative change

First allow order at least four, without imposing smoothness or
positivity separately. Define

\[
\delta_* =\inf\{\|h\|_\infty:
L_0(h)=L_1(h)=L_2(h)=0,\ L_3(h)=-f_3\}.
\tag{7}
\]

Let V=span{p₀,p₁,p₂}, and define the weighted L1 distance

\[
D=\min_{a\in\mathbb R^3}
\int_0^\infty\left|p_3(u)-\sum_{i=0}^2a_i p_i(u)\right|d\rho(u).
\tag{8}
\]

**Theorem 2 (minimum-cost formula).** The minimum in (8) is attained,
D>0, and

\[
\boxed{\delta_* = |f_3|/D.}
\tag{9}
\]

For any minimizing a, set r_a=p₃−Σa_i p_i. A minimum-norm
measurable design is

\[
h_*(u)=-\frac{f_3}{D}\operatorname{sgn}(r_a(u)).
\tag{10}
\]

It is unique up to ρ-null sets on the support of ρ. No uniqueness
claim for the coefficient vector a is needed. Values at zeros of r_a
do not affect the integrals.

**Proof.** Finite-dimensional norm equivalence and independence of
p₀,p₁,p₂ imply coercivity of the objective in (8). Indeed its value
is at least ||Σa_i p_i||L1−||p₃||L1, and the first norm is bounded
below by a positive constant times ||a||. Thus a minimizer exists.
Since p₃ is not in the closed finite-dimensional space V, D>0.

For a fixed a the residual is a nonzero analytic function. Its zeros
are a Lebesgue null set, hence a ρ-null set. Differentiating the
objective with respect to a_i is justified by domination by |p_i|.
At a minimum,

\[
\int p_i\operatorname{sgn}(r_a)\,d\rho=0,
\quad i=0,1,2.
\tag{11}
\]

It follows that ∫p₃ sign(r_a)dρ=D, so (10) satisfies all four
constraints and has norm |f₃|/D. Conversely every feasible h obeys

\[
|f_3|=\left|\int r_a h\,d\rho\right|
\le\|h\|_\infty\int|r_a|\,d\rho=\|h\|_\infty D.
\tag{12}
\]

Equality forces h=−(f₃/D)sign(r_a) almost everywhere where ρ>0
and r_a≠0, proving uniqueness of the optimal measurable multiplier.
This is the familiar L1-approximation/L∞-moment duality specialized
to the pinned-zero target, not a claim of a new duality theorem. ∎

Equation (9) reduces an optimization over functions h to a convex
problem with **three real unknowns**, but its objective is still an
integral on an unbounded domain. The absolute value, residual zeros,
tail bounds and exact-Q uncertainty must be controlled to compute
D rigorously. A numerical optimizer alone would not settle δ_*.

Every candidate a with a rigorously computed upper bound U_a on
∫|r_a| gives the rigorous lower bound δ_*≥|f₃|/U_a. Every exact
feasible h with ||h||∞≤U_h gives δ_*≤U_h. These are different
certificate directions; an upper bound on D produces a lower bound
on the required change.

## 4. Positivity, exact order four, and smoothness

**Corollary 1.** If δ_*<1, the multiplier (10) gives a uniformly
positive relative kernel factor 1+h_*≥1−δ_*>0 almost everywhere.
If the density is
positive almost everywhere on all of (0,∞), then δ_*<1 automatically
under (4).

**Proof of the additional statement.** For the minimizing residual,
∫r_a dρ=f₃, because f₀=f₁=f₂=0. For arbitrarily large u with
cos(2τu)=0 and sin(2τu)=±1, the residual is
±((2u)³+a₁(2u)). Thus r_a takes both signs on open intervals.
Full positive density makes both positive and negative parts have
strictly positive integrals. Hence D=∫|r_a|dρ>|∫r_a dρ|=|f₃|,
which proves δ_*<1. This is not a uniform bound separated from 1
over all possible kernels. ∎

The minimum-norm design generally has jumps; it cannot simply be
called a smooth positive kernel modification. Also f₄+L₄(h_*) may
vanish. The next statement deals explicitly with both issues.

**Theorem 3 (same infimum for smooth nondegenerate designs).** If
δ_*<1, then for every sufficiently small ε>0 there exists a real
smooth compactly supported h with ||h||∞<δ_*+ε<1 such that Q is
a zero of exactly order four and its (λ,μ,ν) unfolding has rank
three. Therefore the infimum of the cost over these smooth positive
nondegenerate designs also equals δ_*. Attainment of that infimum
in the smooth class is not asserted.

**Proof.** Approximate (10) by bounded smooth compactly supported
functions with supremum norm at most δ_*, converging in the weighted
L1 norm with weight 1+Σ_{j=0}^7|p_j| against ρ. Such approximation
follows from cutoff and smooth approximation for a finite absolutely
continuous weighted measure; the supremum bound can be preserved.
All moment errors through order seven tend to zero. Correct the
first four moment errors exactly with R₃ from Theorem 1. The
correction norm tends to zero, so the cost stays arbitrarily close
to δ_* and the first four required equalities are now exact.

Write g_j=f_j+L_j(h). At g₀=⋯=g₃=0 the determinant of the
three-control jet matrix is

\[
\det\partial_{(\lambda,\mu,\nu)}(g_0,g_1,g_2)
=\frac{g_4(g_4g_7-g_5g_6)}{4096}.
\tag{13}
\]

Use R₇ to make a further arbitrarily small change in jets 4–7
while leaving jets 0–3 exactly unchanged. The polynomial
g₄(g₄g₇−g₅g₆) is not identically zero as a function of those
four jets, so its complement is dense. Choose the adjustment there.
Its norm can be made arbitrarily small; positivity and the desired
cost bound remain. Now g₄≠0 and (13)≠0, proving the assertion. ∎

If K itself is smooth, these constructions keep K_h smooth. General
measurable K is not made smooth merely by a smooth h. Compactly
supported h away from zero extends smoothly and evenly to the real
line. No frequency cutoff or bound on derivatives of h has been
included; adding those changes the optimization problem.

## 5. First rigorous bracket for the original theta example

Return to the frozen R01 point Q at ν₀=0 and the original theta
kernel Φ. A **new** candidate is

\[
h_c(u)=\sum_{j\in\{40,41,42,43\}}w_j\cos(2ju).
\tag{14}
\]

Let A_nj=∫p_n cos(2ju)dρ for n=0,…,3. The exact weights are
defined by the exact nonsingular system

\[
Aw=(0,0,0,-f_3)^T.
\tag{15}
\]

Their interval approximations only identify these exact weights.
Seventy-two new shifted integrals enclose the moments of orders
0–8 at exact Q, including all tails and root displacement. The
Arb solve and a separate rational Cramer calculation both prove
that A is nonsingular, and that (14) has

\[
\|h_c\|_\infty\le\sum|w_j|<2.381\times10^{-7}.
\tag{16}
\]

The sum is an upper bound, not a computed exact supremum norm and
not an asserted optimum. In particular Φ(1+h_c)>(1−2.381×10⁻⁷)Φ.
For the modified integral the separately checked bounds include

\[
10^{13}g_4\in[-9.7629645301,-9.7629645300],
\]
\[
10^{40}\det\partial_{(\lambda,\mu,\nu)}(g_0,g_1,g_2)
\in[-4.4646224041,-4.4646224040].
\tag{17}
\]

Thus this is an exact order-four zero with a nondegenerate
three-control unfolding. It is a different modified kernel from
R09/R10, so the old finite-window constants and root-region plots
have not been transferred to it.

For a universal lower bound, every feasible h has
|f₃|=|L₃(h)|≤||h||∞ A₃, where A₃=∫(2u)³dρ. One new positive
integral, with the exact-Q displacement included, bounds A₃.
This gives the first bracket

\[
\boxed{3.96\times10^{-10}<\delta_*<2.381\times10^{-7}.}
\tag{18}
\]

More precise outward endpoints are
[0.00000000039603640200, 0.00000023803280902557]. The ratio of
the unrounded upper and lower bounds is about 601.04. The numerical
minimum has **not** been identified or tightly localized. The lower
bound uses only |sin|≤1; exploiting all three pinning constraints
in (8) is a concrete path to strengthening it.

The bracket applies to all real bounded measurable relative changes,
and, by Theorem 3, to the infimum over smooth positive rank-three
order-four designs at the same Q. It does not impose a bandwidth
constraint. The R09 optimum over sixteen modes concerns a different
objective and budget; it is not contradicted by (16).

## 6. Verification and selected continuation

The exact moment equations supply exact pinning. A small residual
or a quadrature value containing zero is not used as a proof of an
exact identity. The rational checker redoes the solve by permutation
determinants, checks the full 3×3 control determinant and its reduced
formula, and computes the lower and upper norm bounds from intervals.

Nine further direct product-form Arb integrals of the new kernel
agree with the shifted-integral construction. Three values have
separate mpmath checks at 90 and 115 digits. These midpoint numerical
checks are corroboration, not rigorous proofs. The rational checker
trusts the integral enclosures and exact-Q input; the analytic proofs
in Sections 1–4 have not received external expert review.

The general local mechanism is now explicit. The chosen next
mathematical extension is **the minimum relative kernel change at
fixed Q**, using (8) to obtain a sharper certified lower bound and
a correspondingly efficient feasible smooth design. The current
bracket is its first quantified result. No additional kernel family,
finite-root atlas, physical model, or higher singularity is required
to state this question.

The closest standard background and the limited scope of the source
reading are recorded in [REFERENCES.md](REFERENCES.md). Generic moment
annihilation, smooth correction, and L1/L∞ duality must not be presented
as newly invented tools. The special quantitative result and any future
sharp bound need their own literature-priority assessment.
