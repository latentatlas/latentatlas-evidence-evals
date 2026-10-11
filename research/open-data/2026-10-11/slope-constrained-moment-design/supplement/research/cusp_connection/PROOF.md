# A certified cusp curve joining quartic and sextic deformations

R03, 20 September 2026. Local computer-assisted theorem with interval
integrals and a separate exact-rational arithmetic check. External expert
review and a literature priority assessment have not been completed.

## 1. Family and result

Use the kernel Φ, normalization and analytic/tail estimates of the frozen
[R01 proof](../cusp_verified/PROOF.md). Here all three controls are active:

\[
F(t;\lambda,\mu,\nu)=\int_0^\infty\Phi(u)
 e^{\lambda u^2+\mu u^4+\nu u^6}\cos(2tu)\,du.
\]

Let D_n=∂_t^n F and G=(D_0,D_1,D_2). Then

\[
F_\lambda=-D_2/4,\quad F_\mu=D_4/16,\quad F_\nu=-D_6/64. \tag{1}
\]

The two previously certified exact cusps, denoted Q and S, have approximate
locators in coordinates (t,λ,μ,ν):

\[
Q\simeq(41.40034135868425,-3.645692061604919,8.335120498918607,0),
\]
\[
S\simeq(44.28556344959544,-12.43702949446505,0,-28.82453269539050).
\]

These rounded locators are not the proof inputs. The original dyadic
centers and certified radius boxes are used to identify the exact points.

**Computer-assisted theorem.** There is one real analytic graph

\[
\Gamma(\nu)=(t(\nu),\lambda(\nu),\mu(\nu),\nu),
\qquad -29\le\nu\le0,
\]

in the recorded connected family of affine tubes, with G(Γ(ν))=0.
Both Q and S lie on this graph. At every point of the graph,

\[
D_3>8\cdot10^{-14},\quad D_4<0,\quad D_6<0,
\qquad 0.26<\frac{d\mu}{d\nu}<0.34. \tag{2}
\]

Each point is a nondegenerate triple zero with independent λ,μ control
directions. The graph meets μ=0 exactly once, at S. In particular Q and S
belong to the same connected component of the cusp locus, and a concrete
regular arc between them has been certified. There is no fourth-order
zero, and hence no A4 potential singularity, along this arc.

Uniqueness is only asserted inside the recorded tubes at each driver
value. Other cusp branches outside those tubes have not been classified.
No conclusion about RH, the classical Newman constant, or a physical
time evolution is made.

## 2. Cover, centers, and affine predictors

Treat ν as the driver and x=(t,λ,μ) as the unknown. For j=0,…,57 set

\[
\nu_j=-\frac{2j+1}{4},\qquad h=\frac14,\qquad
I_j=[\nu_j-h,\nu_j+h].
\]

These closed intervals cover [−29,0] without gaps, in decreasing order.
Each cell has an exact dyadic point x_j and predictor v_j, obtained from
numerical refinement, and the affine center

\[
a_j(\nu)=x_j+v_j(\nu-\nu_j).
\]

The unknown lies in X_j(ν)=a_j(ν)+S[-1,1]^3, where
S=diag(2^-10,2^-10,2^-10). The proof does not depend on Newton iteration
being successful in any global sense; its candidates are accepted only
after the following uniform tests pass.

The x-Jacobian has entries

\[
(G_x)_{ij}=f_jD_{i+s_j},\quad i=0,1,2,\quad
s=(1,2,4),\quad f=(1,-1/4,1/16). \tag{3}
\]

The stored fixed matrix Y_j is an exact dyadic approximate inverse of (3)
at the center. Its determinant excludes zero.

## 3. Taylor bounds in four variables

For displacement δ=(δt,δλ,δμ,δν), define the commuting differential operator

\[
L_\delta=\delta tD_t-\frac{\delta\lambda}{4}D_t^2
 +\frac{\delta\mu}{16}D_t^4-\frac{\delta\nu}{64}D_t^6. \tag{4}
\]

For n≤8 and K=8,

\[
D_n(x_j+\delta)=\sum_{k=0}^{K-1}\frac{L_\delta^kD_n(x_j)}{k!}+R_n.
\]

Writing L_δ^K=Σ_m A_{K,m}(δ)D_t^m, the integral remainder gives

\[
|R_n|\le\frac1{K!}\sum_m|A_{K,m}(\delta)| B_{n+m}, \tag{5}
\]

where B_r uniformly bounds |D_r| throughout every intervening segment.
Central derivatives through order 50 and positive majorants through order
56 are recorded for every cell. The R01 integrator uses a finite entire
kernel sum, adds the omitted real-axis kernel-series error, and adds a
separate infinite-domain tail bound.

For a cell let H_i≥|v_ji|h+2^-10 for i=0,1,2 and H_3=h, using outward
dyadic bounds. The derivative-majorant domain is twice this half-width
box. This slack absorbs interval representation widening. It covers all
segments used by (5), including the positive-ν part of the enlarged
majorant domain near the quartic endpoint. The tail condition for the
sextic polynomial holds at U=2.

For the Jacobian, evaluating D_r separately and then multiplying by Y
unnecessarily loses cancellations between related derivatives. Instead,
each scalar entry f_j Σ_i Y_ri D_{i+s_j} is expanded as one linear
combination: combine the central derivatives first and apply (4) second.
The remainder still uses the triangle inequality Σ_i |Y_ri|B_{i+s_j+m}.
This is an enclosure-preserving rearrangement, not an assumed cancellation
of unknown errors.

For G(a_j(ν),ν), the displacement is correlated: δ=(v_j z,z), z=ν−ν_j.
Use L_δ=zA_j with constant operator

\[
A_j=v_{jt}D_t-v_{j\lambda}D_t^2/4+v_{j\mu}D_t^4/16-D_t^6/64.
\]

The powers of A_j act on the central derivatives before multiplication by
the interval z^k. Thus the shared driver is not split into four independent
intervals. Remainders are again bounded by (5).

## 4. Uniform existence and uniqueness

For each fixed ν∈I_j consider T_ν(x)=x−Y_j G(x,ν). The saved Taylor
enclosures imply, uniformly on the whole tube,

\[
q_j=\sup\|S^{-1}(I-Y_jG_x)S\|_\infty<0.502,
\]

\[
\eta_j=\sup_{\nu\in I_j}\|S^{-1}Y_jG(a_j(\nu),\nu)\|_\infty,
\qquad \eta_j+q_j<0.560<1. \tag{6}
\]

Consequently T_ν maps X_j(ν) strictly into itself and is a contraction.
Nonsingularity of Y_j makes its unique fixed point equivalent to G=0.
The root also satisfies, in each coordinate,

\[
|x_i(\nu)-a_{ji}(\nu)|
\le R_{ji}\frac{\eta_j}{1-q_j}. \tag{7}
\]

Since ||I−Y_jG_x|| in the scaled norm is less than one, G_x is invertible
on the tube. The analytic implicit-function theorem provides a locally
analytic graph in ν, uniquely identified within this tube.

## 5. Connecting all 58 graphs

Adjacent cells share exactly one endpoint ν_b. The proof checks that the
entire smaller root box (7) of the preceding cell at ν_b lies strictly
inside the next cell's full uniqueness box:

\[
|a_{ji}(\nu_b)-a_{j+1,i}(\nu_b)|
 +R_{ji}\frac{\eta_j}{1-q_j}<R_{j+1,i},\quad i=0,1,2. \tag{8}
\]

This is a root containment test; overlap of two arbitrary boxes would not
suffice. All 57 tests pass. The separate exact-rational calculation proves
that the left side of (8), divided by the right side, is less than 0.117.
The previous root is therefore a root in the next cell's uniqueness box,
so the two roots coincide. The local analytic graphs agree near the seam
by the implicit-function theorem. Induction glues all cells into Γ.

## 6. Identifying the previously certified points

At ν=0, the entire original quartic cusp box in (t,λ,μ) lies strictly
inside X_0(0). Its proved root must be Γ(0) by uniqueness.

The original sextic certificate gives an exact root with μ=0 and
(t,λ,ν) in its recorded box. Its ν interval lies strictly inside the last
cell. For every ν in that small interval, the original possible t,λ
coordinates together with μ=0 lie in X_57(ν). Hence the original exact
sextic root lies on Γ, at its own certified ν value. We do not replace
that unknown exact ν by its printed approximation or the dyadic center.

These two containment arguments identify the old mathematical objects,
not just nearby numerical candidates from a new Newton run.

## 7. Regularity and the unique sextic intersection

The uniform derivative tests give D_3>8×10^-14, D_4<0 and D_6<0 on the
relevant boxes. At a root of G, the two-control determinant is

\[
\det D_{(\lambda,\mu)}(F,F_t)=D_3D_4/64\ne0.
\]

Thus every point of Γ is a nondegenerate cusp with those control
directions. In particular its third t-derivative never vanishes.

Differentiate G(Γ(ν))=0 and use D_1=D_2=0 exactly at its cusp points.
The triangular equations give

\[
\mu'=\frac{D_6}{4D_4},\qquad
\lambda'=\frac{4D_5\mu'-D_7}{16D_3},\qquad
t'=\frac{D_8/64+D_4\lambda'/4-D_6\mu'/16}{D_3}. \tag{9}
\]

The signs in (1) are essential here. Exact-rational substitution tests
check (9) against the full Jacobian equation G_x x'=−G_ν.
The uniform boxes prove 0.26<μ'<0.34. Hence μ is strictly increasing with ν,
and the μ=0 intersection already identified as S is unique on this arc.
The present proof does not require a sign conclusion about t'.

## 8. Independent arithmetic and integral checks

The generating code builds differential-operator powers by polynomial
multiplication in ball arithmetic. `check_connection.py` instead expands
all four-variable multinomial coefficients with Python exact fractions.
It rebuilds the preconditioned Taylor bounds, predictor residuals, all
58 contractions, all 57 joins, the derivative sign bounds, and the two
endpoint identifications. Its positive remainders may be more conservative.
Nevertheless it independently checks the rational thresholds in (2), (6)
and (8). Its central derivative balls and B_r bounds remain input
assumptions: it does not independently certify the integrals themselves.

`test_connection.py` compares the new four-variable enclosures with
42 direct derivative integrals at three separated cells, checks the
preconditioned Jacobian at six mixed-displacement points, and compares
18 correlated predictor residual components with direct integration.
It also verifies domain rejection and the exact tangent identities.
The direct checks use more kernel terms and finer quadrature subdivision.

`check_independent.py` uses mpmath, not FLINT or the Taylor implementation,
at three interior cell centers for 18 derivative comparisons. It is
additional numerical support, not a second rigorous integration theorem.

All original R01/R02 files are checked against their frozen manifests.
Neither the original manuscript nor those packages are modified by this
new calculation. No claim of literature priority, global classification,
or automatic journal acceptance follows from this result.
