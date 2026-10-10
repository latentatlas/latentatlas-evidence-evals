# A quantitative cusp region for the quartic deformation

Research result R02, 20 September 2026. This is a local computer-assisted
mathematical argument with a reproducible implementation. It is not an
external expert review or a proof-assistant verification. No priority claim
is made for the general identities or for the example.

## 1. Object, domains, and statement

Use exactly the quartic family and kernel in the frozen
[baseline proof](../cusp_verified/PROOF.md):

\[
F(t;\lambda,\mu)=\int_0^\infty\Phi(u)e^{\lambda u^2+\mu u^4}
                 \cos(2tu)\,du.
\]

Write D_n = ∂_t^n F. Then F_λ = −D_2/4 and F_μ = D_4/16.
The family is real analytic on all real finite parameter boxes.

Let x0=(t0,λ0,μ0) be the **exact dyadic center**, not the rounded decimal
display, in the baseline quartic certificate. For orientation only,
x0≈(41.40034135868425, −3.645692061604919, 8.335120498918607).
Set

\[
I=[t_0-3/1000,t_0+3/1000],\qquad
P=[\lambda_0-10^{-6},\lambda_0+10^{-6}]
  \times[\mu_0-2\cdot10^{-9},\mu_0+2\cdot10^{-9}].
\]

For an auxiliary uniqueness domain use

\[
Q=[\lambda_0-2^{-13},\lambda_0+2^{-13}]
  \times[\mu_0-2^{-20},\mu_0+2^{-20}].
\]

**Computer-assisted theorem.** In I × P there is exactly one cusp
c=(t*,λ*,μ*), namely the cusp already certified in the baseline.
The discriminant, defined here as the controls for which F has a multiple
real zero **in I**, consists of this cusp and two nondegenerate fold arcs.
The arcs meet only at the cusp and each exits P through λ=λ0+10^-6.
There are no other multiple real zeros in I × P.

For λ*<λ≤λ0+10^-6, write the arcs as μ_low(λ)<μ*<μ_high(λ).
Between them F has exactly three simple real zeros in I. At every other
control in P off the discriminant it has exactly one simple real zero in I.
On either fold arc there is one double and one simple zero; at the cusp
there is one triple zero. No root crosses either endpoint of I anywhere in P.

All the counts concern I only. There is no claim about all real zeros, RH,
the classical Newman constant, or a physical time evolution.

## 2. A uniform two-control Taylor enclosure

For a displacement (h,l,m), differentiation along its straight segment is

\[
L=hD_t-\frac{l}{4}D_t^2+\frac{m}{16}D_t^4.
\]

The operators commute. For any n≤6 the total-degree Taylor polynomial of
order k−1, k=8, is

\[
T_n(h,l,m)=\sum_{p+q+r<k}
 \frac{h^p(-l/4)^q(m/16)^r}{p!q!r!}
 D_{n+p+2q+4r}(x_0).
\]

Suppose B_j bounds |D_j| on every intervening real segment. The ordinary
one-variable integral remainder along the segment, followed by the
multinomial expansion of L^k, gives

\[
|D_n(x_0+(h,l,m))-T_n(h,l,m)|\le
\sum_{p+q+r=k}
\frac{|h|^p(|l|/4)^q(|m|/16)^r}{p!q!r!} B_{n+p+2q+4r}. \tag{1}
\]

The identity includes the quartic-control factor 1/16 and both parameter
directions. The polynomial uses central derivatives through order 34,
and (1) uses bounds through order 38. The B_j bounds are obtained from the
baseline's real positive majorants on the larger domain
|h|≤2^-8, |l|≤2^-12, |m|≤2^-19. Thus the straight segments used for I × Q
are covered. Central derivatives are enclosed by the baseline finite-sum
complex quadrature with its two analytic real-axis tails.

All arithmetic is outward ball arithmetic. Signed interval powers in the
polynomial are formed by repeated multiplication; a nonfinite value is
rejected. Cache provenance includes the exact input center, integrator hash,
quadrature settings, precision and library version. The frozen baseline's
25 file hashes are checked before use.

## 3. One analytic fold curve for every t in I

Let H=(F,F_t) and let A be its two-control Jacobian. Then

\[
A=\begin{pmatrix}-D_2/4&D_4/16\\-D_3/4&D_5/16\end{pmatrix},
\quad \det A=\frac{\Delta}{64},\quad
\Delta=D_3D_4-D_2D_5. \tag{2}
\]

Let Y be the fixed exact dyadic approximate inverse recorded in the
certificate. Its determinant excludes zero. In control offsets, define

T_t(p)=p−Y H(t,(λ0,μ0)+p).

Use the scaled max norm with S=diag(2^-13,2^-20). Formula (1) encloses A on
I × Q and H(t,λ0,μ0) for every t∈I. The certificate verifies

\[
q=\sup_{I\times Q}\|S^{-1}(I-YA)S\|_\infty<0.550,
\qquad
\eta=\sup_I\|S^{-1}YH(t,\lambda_0,\mu_0)\|_\infty<0.149,
\]

and, more tightly, η+q<0.698<1. Thus T_t is a self-map and contraction of
the same closed Q for **every** t∈I. Its unique fixed point is equivalent
to H=0 since Y is nonsingular. This proves a unique control pair p(t)
throughout I. There is no unstated inference from overlapping boxes.

The calculation also gives D_3>0, D_4<0 and Δ<0 throughout I × Q.
By (2) and the analytic implicit-function theorem, p(t) is locally
analytic; uniqueness identifies all these local graphs as one curve.
Write it as (Λ(t),M(t)) in absolute controls.

## 4. Exact tangent identities, a single cusp, and finite growth bounds

Along H=0, differentiating with respect to t gives A p'=−(0,D_2).
Solving this 2×2 system yields the exact identities

\[
\Lambda'=\frac{4D_2D_4}{\Delta},\qquad
M'=\frac{16D_2^2}{\Delta}. \tag{3}
\]

These formulas hold on any regular fold graph of a family satisfying both
heat-hierarchy identities. In particular, on a connected segment where
Δ≠0, its constant sign fixes the sign of M' away from triple zeros.
This algebraic observation is not claimed to be new in the literature.

Set w(t)=D_2(t,Λ(t),M(t)). The chain rule gives

\[
w'=D_3-\frac{D_4}{4}\Lambda'+\frac{D_6}{16}M'. \tag{4}
\]

Substituting the interval bounds in (3)–(4) proves w'>0 on the entire curve.
Also D_2(t0−3/1000,λ,μ)<0 and D_2(t0+3/1000,λ,μ)>0 throughout Q.
Thus w has exactly one zero. The old certified cusp lies in I × P and is
on this curve by uniqueness, so it is that zero. At it D_3>0 and
det A=D_3D_4/64≠0, giving the nondegenerate cusp. All other points on the
curve have D_2≠0 and hence are nondegenerate double zeros.

Because D_4/Δ>0, Λ'<0 before t* and Λ'>0 after t*. Because Δ<0, M'<0
except at t*, where it vanishes. Therefore Λ has a unique minimum and
M is strictly decreasing on the entire curve. In particular the control
curve has no self-intersection.

There are also **finite-neighborhood inequalities**, not just formal jets.
Let s=t−t*, a(t)=4D_4/Δ>0, b(t)=−16/Δ>0, and let g_min,g_max be positive
lower/upper bounds for (4). Since w(t*)=0,

g_min |s|≤|w(t)|≤g_max |s|.

Integrating Λ'=a w and M'=−b w² gives two-sided quadratic and cubic bounds.
The recorded intervals for a[w']/2 and b[w']²/3 are respectively contained
in [1.91856,2.08307] and [1.72999,1.93291]. Here bracketed products denote
interval products of uniform bounds, not an equality between an integral
coefficient and its value at a single point. In particular the program
checks the convenient rational inequalities

\[
1.91s^2\le\Lambda(t)-\lambda_*\le2.09s^2,
\qquad
1.72|s|^3\le|M(t)-\mu_*|\le1.94|s|^3. \tag{5}
\]

Moreover sign(M(t)−μ*)=−sign(s) for s≠0. Eliminating |s| with the sharper
stored interval bounds proves

\[
0.57(\Lambda(t)-\lambda_*)^{3/2}
\le |M(t)-\mu_*|
\le0.73(\Lambda(t)-\lambda_*)^{3/2}. \tag{6}
\]

These statements hold along the entire auxiliary curve t∈I. The differences
are relative to the actual cusp c, whose tiny box is certified, rather than
silently equating c with x0.

## 5. Restricting the curve to P

Separate fixed-t contractions at t=t0±1/1000 produce points on the same
curve: their root boxes lie inside Q, where uniqueness has already been
proved. They verify Λ>λ0+10^-6 and |M−μ0|<2×10^-9 at both points.
For orientation, their control offsets are approximately

| t−t0 | Λ−λ0 | M−μ0 |
|---|---:|---:|
| −0.001 | 1.99809298839×10^-6 | 1.82686021×10^-9 |
| +0.001 | 2.00190975607×10^-6 | −1.83486023×10^-9 |

The cusp is strictly inside P. The strict monotonicity on either side of t*
therefore gives exactly one intersection of each arm with λ=λ0+10^-6.
The monotonicity of M and the fixed-t bounds keep both arcs inside the μ
boundaries until those intersections. No earlier exit through the left
λ boundary is possible because Λ≥λ*. Points further along either arm have
Λ>λ0+10^-6 and hence are outside P.

Optional narrow 2D contractions with unknowns (t,μ) at λ=λ0+10^-6 enclose
the boundary intersections in the certificate; they are not inferred from
a plot. Their approximate offsets are

| t−t0 | μ−μ0 |
|---:|---:|
| −0.0007073454091 | +6.469598777×10^-10 |
| +0.0007068683131 | −6.476496386×10^-10 |

Λ's strict monotonicity gives the graphs μ_high(λ), μ_low(λ).
Their derivatives, away from the cusp, satisfy

\[
\frac{dM}{d\Lambda}=\frac{4D_2}{D_4}.
\]

Thus the upper graph increases and the lower graph decreases with λ.
The discriminant splits the interior of P into exactly two components:
the open region between the two graphs, and its connected exterior.

## 6. All real-root counts in I × P

The calculation verifies F(t0−3/1000;λ,μ)<0 and
F(t0+3/1000;λ,μ)>0 for every control in P. Thus there is at least one root
in the interior of I and none at its endpoints. D_3>0 on I × Q implies
there are at most three zeros counting multiplicity, by Rolle's theorem.

Off the discriminant all roots are simple, and their count is locally
constant: the implicit-function theorem continues the roots, while
compactness and the nonzero endpoint values exclude entry of other roots.
Hence the count is constant on each of the two components above.

At (λ0−5×10^-7,μ0), the function has opposite endpoint signs and F_t>0
on a recorded 32-piece closed cover of I; it has exactly one simple root.
This witness is in the exterior because its λ coordinate is below λ*.
At (λ0+5×10^-7,μ0), the signs at t offsets
(−0.0015,−0.0003,0.0003,0.0015) are (−,+,−,+); hence there are exactly
three simple roots. This witness must be in the other component, since
it cannot lie on the discriminant and the exterior count is already one.
The same conclusions extend to regular portions of the boundary of P by
local continuation and the same nonzero endpoint bounds.

At a fold the double zero has D_2≠0. Opposite signs at the endpoints of I
require an additional odd-multiplicity zero, which must be simple because
the total multiplicity is at most three. At the cusp its triple root uses
the entire allowed multiplicity. This proves the stated classification.

**Width consequence.** For λ*<λ≤λ0+10^-6, (6) applies to both arcs and gives

\[
1.14(\lambda-\lambda_*)^{3/2}
\le\mu_{high}(\lambda)-\mu_{low}(\lambda)
\le1.46(\lambda-\lambda_*)^{3/2}. \tag{7}
\]

The exponent 3/2 is the familiar cusp scaling. The result here is an
explicit finite region, numerical constants with certified errors, and a
complete root count for this specified integral family.

## 7. Verification and limits

`certify_region.py` evaluates the stated strict inequalities and emits all
relevant intervals and contraction matrices. `test_region.py` checks
zero-crossing interval behavior, domain rejection, the tangent identities
in exact rational arithmetic, 24 two-control Taylor enclosures against
direct finer quadrature, and boundary-fold residuals via direct integrals.
`check_witnesses.py` also rechecks the saved contraction, sign, finite-growth,
and containment inequalities using exact rational interval arithmetic,
without importing FLINT or the generating Taylor code. This additional
checker trusts the saved derivative enclosures; it does not re-integrate or
formalize the analytic argument. Independent mpmath checks are additional
numerical support only.

The baseline code and its previous conclusions are preserved. R02 does not
certify the original manuscript's long continuation runs or establish that
quartic and sextic cusp examples lie on a common cusp curve. The literature
comparison and an external expert review remain separate requirements.
