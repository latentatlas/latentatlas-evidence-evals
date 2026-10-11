# R10 — A finite swallowtail window in original control coordinates

20 September 2026. Computer-assisted statements for the fixed modified
positive kernel constructed in R09. External mathematical review and
literature priority remain open.

## 1. Exact function and the physical box

Let Q=(t_Q,λ_Q,μ_Q), ν=0, be the exact point identified in R01,
and let h_* and ε_4=−F_3(Q)/H_3(Q) be the exact R09 cofactor direction
and order-four amplitude. Fix that amplitude throughout this package:

\[
G(t;\lambda,\mu,\nu)=\int_0^\infty
\Phi(u)(1+\epsilon_4h_*(u))e^{\lambda u^2+\mu u^4+\nu u^6}
\cos(2tu)\,du.
\]

R09 proves positivity of this modified kernel, G_0(Q)=⋯=G_3(Q)=0,
G_4(Q)<0 and rank three for the parameter jets. Subscripts denote
t derivatives. Use exact translations
s=t−t_Q, ℓ=λ−λ_Q, m=μ−μ_Q, n=ν and the constant normalization

\[
g(s;\ell,m,n)=\frac{24}{G_4(Q)}
G(t_Q+s;\lambda_Q+\ell,\mu_Q+m,n).
\tag{1}
\]

The multiplier is negative and nonzero; all zeros and their
multiplicities are unchanged. At the exact origin g_0=⋯=g_3=0,
g_4=24. No rounded coordinates define Q, h_* or ε_4.

The heat identities persist:

\[
\partial_\ell g_j=-g_{j+2}/4,\qquad
\partial_m g_j=g_{j+4}/16,\qquad
\partial_n g_j=-g_{j+6}/64.
\tag{2}
\]

Let

\[
T=2^{-7},\quad P_\ell=2^{-17},\quad P_m=P_n=2^{-34},
\quad I=[-T,T],\quad
P=[-P_\ell,P_\ell]\times[-P_m,P_m]\times[-P_n,P_n].
\tag{3}
\]

These are original control offsets, without a hidden normal-form
coordinate change. The function is real analytic on this box and on
the larger auxiliary boxes below, by the integral's super-exponential
tail and the fixed bounded cosine multiplier.

**Theorem 1 (finite root count).** Throughout I×P,
22<g_4<26. At both ends g(±T)>10⁻⁹, and
g_1(−T)<−10⁻⁶<0<10⁻⁶<g_1(T). Thus no root crosses the t-window
boundary, and g has at most four real zeros in I, counting multiplicity.
Off its root discriminant, it has exactly 0, 2 or 4 simple real zeros.

More explicitly, let r_1<⋯<r_k be all distinct zeros of g_1 in I.
There are at most three. Provided g(r_i)≠0, the exact root count is
the number of sign changes in

\[
g(-T),\quad g(r_1),\ldots,g(r_k),\quad g(T).
\tag{4}
\]

The rule also applies when a stationary point is degenerate but is
not a zero of g. It is not restricted to simple stationary points.

**Proof.** The uniform inequalities are checked by two separate Taylor
and arithmetic implementations. Rolle's theorem, with multiplicities,
and g_4>0 give the bound of four roots and the bound of three stationary
points. Between consecutive distinct stationary points the derivative
has constant nonzero sign, so the function is strictly monotone and
crosses zero exactly when its endpoint values have opposite signs.
The positive outer endpoint values give even parity. ∎

For three simple stationary points r_1<r_2<r_3, put v_i=g(r_i).
The outer two are minima and the middle one is a maximum. Off the
root discriminant, four roots occur precisely when v_1<0<v_2 and
v_3<0; zero roots occur when both minima are positive; the other
possibilities give two. For a single stationary point, a positive
minimum gives zero roots and a negative minimum gives two.

## 2. Every multiple root belongs to one certified surface

Set auxiliary control radii

\[
R_\ell=4T^2=2^{-12},\qquad R_m=R_n=32T^3=2^{-16}.
\tag{5}
\]

These bounds are larger than the physical P box. They are used for
uniform existence and uniqueness, not as an asserted root-count window.

**Theorem 2 (fold surface and cusp curve).** For every
(s,ℓ)∈[−T,T]×[−R_ℓ,R_ℓ] there is exactly one pair
(m,n) in the closed radius-(R_m,R_n) box satisfying g=g_1=0.
It lies in the box's interior and defines a real analytic graph
(m,n)=f(s,ℓ). All multiple roots with controls in P occur on this
surface, after restricting its parameter values to P.

For every s∈[−T,T], there is exactly one control triple
p_c(s)=(ℓ_c,m_c,n_c) in the closed radius-R box satisfying
g=g_1=g_2=0. This graph is real analytic, p_c(0)=0, and along it

\[
16<\frac{d}{ds}g_3(s,p_c(s))<32,
\quad
0.8s^2<\ell_c(s)<4s^2\quad(s\ne0).
\tag{6}
\]

The branch s<0 has g_3<0 and the branch s>0 has g_3>0. Both consist
of ordinary triple zeros; s=0 gives the unique order-four zero among
all cusps in this auxiliary box. In particular Q is the only order-four
zero in I×P. The function ℓ_c decreases on the negative branch and
increases on the positive branch. Every 0<ℓ≤P_ℓ meets each auxiliary
cusp branch exactly once. Their m,n coordinates must still be checked
against P if a statement specifically inside P is required.

**Proof.** For the fold equations in (m,n), use the fixed exact dyadic
preconditioner Y_2 recorded in the certificate. The Jacobian is

\[
J_{mn}=\begin{pmatrix}g_4/16&-g_6/64\\g_5/16&-g_7/64\end{pmatrix}.
\]

The map z↦z−Y_2(g,g_1) has weighted derivative norm q and normalized
central residual η with q+η<1, uniformly over the whole (s,ℓ)
rectangle. Banach's theorem therefore gives existence and uniqueness
in the same box for every driver value. Its derivative is nonsingular;
the implicit function theorem supplies the analytic graph. Since P is
contained in the auxiliary control box, every physical multiple root
is captured. This is a uniform graph proof, not gluing unrelated
sampled solutions by mere box overlap.

For the cusp equations let

\[
J_p=\partial_{(\ell,m,n)}(g_0,g_1,g_2),\qquad
v=J_p^{-1}e_3.
\]

A separate three-dimensional contraction with the fixed exact dyadic
preconditioner Y_3 satisfies q+η<1 uniformly for |s|≤T. The exact
origin satisfies the equations, so uniqueness identifies p_c(0)=0.
Implicit differentiation on the cusp graph gives

\[
p_c'(s)=-g_3v,\qquad
\rho(s):=\frac{d}{ds}g_3(s,p_c(s))
=g_4-g_3\,\partial_p g_3\cdot v.
\tag{7}
\]

Direct interval inversion on the whole auxiliary box, and separately
cofactor inversion in rational arithmetic, establish
16<ρ<32 and −0.24<v_ℓ<−0.1. The checked interval product
−v_ℓρ/2 lies strictly between 0.8 and 4. Integrate ρ from 0 to s
to obtain the sign and magnitude of g_3; integrate ℓ_c′=−g_3v_ℓ
to obtain (6). The same estimates work on both sides of zero. This
also proves branch monotonicity and uniqueness of the order-four
point. Since 0.8T²>P_ℓ, each positive physical λ slice meets both
auxiliary branches. ∎

The surface can have self-intersections in control space: two distinct
s values may give the same controls. Uniqueness of (m,n) for fixed
(s,ℓ) does not exclude that phenomenon. Away from g_2=0 the surface
projection is an ordinary fold. On p_c(s), s≠0, the zero is triple
and its two-control (m,n) unfolding is nondegenerate. This follows
from g_3≠0 and the nonsingularity of J_mn.

## 3. Positive-volume boxes realizing all three root counts

Let L=2⁻²⁴ and take the common open control radii

\[
r_\ell=L/128=2^{-31},\qquad r_m=r_n=L^2/256=2^{-56}.
\tag{8}
\]

**Theorem 3 (open witnesses).** The open boxes with these radii and
the following centers all lie inside P. Every control in the respective
box has the indicated number of simple real zeros in I:

| Center (ℓ,m,n) | Root count |
|---|---:|
| (−L,0,0) | 0 |
| (−L,−L²,0) | 2 |
| (+L,0,0) | 4 |

The inequalities were in fact proved on enclosing closed boxes, so
these are genuinely open regions rather than isolated examples.

**Proof.** For the first two boxes let δ=2⁻²⁰. The checks prove
g_3(−δ)<0<g_3(δ), g_2>0 on [−δ,δ], and
g_1(−δ)<0<g_1(δ), uniformly in the control box. Since g_4>0 on I,
g_3 is strictly increasing and the minimum of g_2 lies in [−δ,δ].
Hence g_2>0 throughout I and g has exactly one minimum, within that
strip. In the first box g>0 throughout the strip, proving zero roots.
In the second g(0)<0; the positive outer endpoint values and strict
convexity give exactly two simple roots.

For the four-root box evaluate g at
s=√L·(−3,−1,0,1,3). The uniform signs are (+,−,+,−,+).
The four disjoint sign-change intervals yield at least four roots;
Theorem 1 permits at most four counted with multiplicity. Thus all
four are simple and there are no others in I. ∎

For orientation only, the leading heat expansion along m=n=0 is
g(s;ℓ,0,0)=s⁴−3ℓs²+3ℓ²/4 plus higher weighted-order terms.
It motivates these witnesses. The rigorous counts use the interval
inequalities above, not just this truncated polynomial.

## 4. A certified finite section with two cusps and two double roots

Fix ℓ=L. The two cusp points are certified inside P. The rational
root boxes give the following outward decimal enclosures for s:

\[
s_c^-\in[-0.00017264472909,-0.00017264472907],\qquad
s_c^+\in[0.00017262225524,0.00017262225525].
\tag{9}
\]

Their original m,n coordinates are in
[the readable result file](results/key_results.json). The signs of
g_3 are separately checked and identify them with the two branches
from Theorem 2. That theorem also proves they are the only cusps in
this slice within the auxiliary control box.

At the same ℓ=L, a four-equation contraction in (s_1,s_2,m,n)
proves g(s_1)=g_1(s_1)=g(s_2)=g_1(s_2)=0, with s_1<s_2,
g_2(s_1)>0 and g_2(s_2)>0. Thus these are two distinct double
zeros at precisely the same controls, not two unrelated fold samples.
No other zeros lie in I, since their multiplicities already total four.
The independently derived enclosures are

\[
s_1\in[-0.00029903062777,-0.00029903025317],\qquad
s_2\in[0.00029898933163,0.00029898970623].
\tag{10}
\]

The contraction's Jacobian is nonsingular. At the true double zeros,
its determinant factors, up to sign, as g_2(s_1)g_2(s_2) times the
determinant of the two parameter gradients of the critical values.
Their gradients are therefore independent: the two fold branches
intersect transversely in this section. We do not assert a global
uniqueness result for all double-fold intersections.

The two cusp arms and self-intersection are standard features of a
swallowtail discriminant; see [NIST DLMF §36.4, equations 36.4.7–9](https://dlmf.nist.gov/36.4).
Here their locations and root multiplicities have been established
for this particular integral with finite bounds. The standard picture
or its terminology is not claimed as a new discovery.

The package also certifies 81 fold-curve points in this slice and six
simple roots at the two nonzero-root witness centers. All geometric
samples are independently re-evaluated in rational arithmetic. The
generator's and rational checker's tight boxes may differ; both use
the same larger uniqueness boxes. The explicitly stated decimal
enclosures above come from the rational checker.

## 5. A finite region map with explicit unknown cells

To display the narrow control geometry, define an **explicit affine**
chart of the original (m,n) plane:

\[
\binom{m}{n}=E\binom{L^2(\beta-3/4)}{L^{3/2}\alpha},
\qquad -4\leq\alpha\leq4,\quad-3/2\leq\beta\leq11/2.
\tag{11}
\]

Here E is exactly the dyadic 2×2 preconditioner Y_2 recorded in the
window certificate. Its matrix is nonsingular and its full entries
are serialized exactly. It approximates the inverse of the (g_0,g_1)
parameter matrix at Q, but the chart itself is defined by the dyadic
matrix, not by pretending that approximation is equality. All chart
controls belong to P. This is a known invertible linear transformation
with a translation, not an unspecified Weierstrass coordinate system
and not a claim that g is exactly a quartic polynomial.

The rectangle is partitioned into 64×56 closed cells of side 1/8.
Stationary-point graphs are first enclosed for each α stripe over
the full β range. Three disjoint monotone derivative brackets give
all three stationary points when they exist. For a single stationary
point, two uniform inflection brackets and the signs of g_1 at them
exclude the other two. The exact sign-change rule (4) then proves
the root count on each cell with resolved critical-value signs.

The result, checked with separate rational arithmetic, is:

| Status of a closed cell | Number of cells |
|---|---:|
| Exactly 0 simple real roots | 430 |
| Exactly 2 simple real roots | 2184 |
| Exactly 4 simple real roots | 190 |
| Unresolved by this grid certificate | 780 |

Thus 2804 colored cells have a proof for **every** parameter in that
cell. The remaining cells are gray. They are not asserted to contain
only multiple roots, nor assigned any root count by interpolation.
Some are unresolved because a stationary-point graph changes type;
others because critical-value enclosures meet zero. The global
theorems and exact criterion still apply there. A complete numerical
tessellation of all of P is not claimed.

The chart evaluation keeps the two affine directions correlated. At
fixed s and ℓ=L, expand to first order in (m,n), combining each
direction against (g_{j+4}/16,−g_{j+6}/64) **before** interval
evaluation. The second-order error is bounded by

\[
\frac12\left[
(|m|/16)^2 B_{j+8}
+2(|m|/16)(|n|/64)B_{j+10}
+(|n|/64)^2B_{j+12}\right].
\tag{12}
\]

In (12), B means local derivative magnitudes on the whole chart
segment. Orders through 12 use the full Taylor model; orders 13 and
14 use first-order mean-value bounds from the exact Q jets and the
positive majorants. This preserves the strong cancellation of the
original m,n coefficients without dropping any error terms.

## 6. Taylor model and verification boundary

The fifty-five F/H jets of orders 0–54 from R09 are reused at the
exact Q with their source hashes and root-uncertainty bounds. They
give the normalized g jets, with orders 0–3 set to zero and order 4
set to 24 by the exact identities, not by small numerical residuals.

**New** positive absolute majorants through order 60 include all
three control variations on
|s|≤0.02, |ℓ|≤0.001, |m|,|n|≤0.0001, with the Q displacement
included in the original λ,μ bounds. Old ν=0 majorants are not used
for nonzero ν. The constant multiplier has magnitude
|24/G_4(Q)|; kernel magnitudes are bounded by (1+|ε_4|)Φ.

Apply Taylor's theorem in the commuting operator
sD−ℓD²/4+mD⁴/16−nD⁶/64. Terms of total order at most seven use
the exact-Q jets; total order eight is bounded using positive
majorants. For derivatives up to order 12 the largest retained
order is 12+7·6=54 and the largest remainder order is 12+8·6=60.
Every displacement segment remains inside the stated majorant box.
Integer interval powers explicitly handle intervals crossing zero.

The generator uses a multi-index expansion. The independent checker
rebuilds the normalized jets from the R09 integral inputs, forms
exponential-operator coefficients by polynomial convolution and uses
outward 512-bit rational endpoints. Matrix inverses are checked by
cofactor determinants. It rebuilds the finite window, both uniform
graph contractions, cusp derivative bounds, three open witnesses,
all 2804 colored cells and all 90 geometric sample contractions.

There are also 27 new direct rigorous integral comparisons at nine
points, including nonzero ν, cusp samples and both double roots.
Exact-Q displacement and analytic series/infinite-domain tails are
included. Nine values are checked by a separate mpmath implementation
at 90 and 115 digits. Those midpoint, finite-truncation checks are
numerical support, not rigorous integration.

Trust boundary: R09 integral enclosures and the new unnormalized
positive majorants are inputs to the rational checkers. This is not
a proof-assistant formalization or an external peer review. The
analytic arguments in this note also need independent expert review.

The initial interval-power implementation failed with a nonfinite
value before a window certificate was produced; v2 corrects that
evaluation issue. The failed code and diagnostic are retained.
See [DIAGNOSTICS.md](DIAGNOSTICS.md). Earlier R01–R09 packages
and the original manuscript are unchanged.

All root counts are confined to I and to the modified kernel fixed
at ε_4. There is no global root count, no original fixed-Φ order-four
claim, and no dynamical or physical stability interpretation. The
scope of the numerical grid is explicitly smaller than the scope
of the continuous finite-window theorems.
