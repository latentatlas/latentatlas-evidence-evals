# R08 — Exact cusp pinning and two-parameter finite fold transport

20 September 2026. A computer-assisted result for the explicitly specified
integral family. This package extends the fixed-Q result of R07 to a whole
cusp sheet and a common finite root window. External mathematical review
and a claim of literature priority remain outstanding.

## 1. Exact family and the statement

Use the positive theta kernel and normalization of
[R01](../cusp_verified/PROOF.md):

\[
F(t;\lambda,\mu,\nu)=\int_0^\infty\Phi(u)
 e^{\lambda u^2+\mu u^4+\nu u^6}\cos(2tu)\,du.
\]

The exact quartic cusp \(Q=(t_Q,\lambda_Q,\mu_Q)\), at \(\nu=0\),
is the uniquely identified root in the frozen R01 certificate, approximately
\((41.40034135868425,-3.645692061604919,8.335120498918607)\).
No rounded value in this note defines Q.

Let \(A_{nj}\), \(n=0,1,2\), \(j=1,\ldots,4\), be the three t-derivative
moments at Q with the additional factor \(\cos(2ju)\). Define

\[
a_j=(-1)^{j-1}\det A_{\widehat j},\quad
Z=\sum_{j=1}^4|a_j|,\quad w_j=a_j/Z,\quad
h_0(u)=\sum_{j=1}^4w_j\cos(2ju).
\]

These are exact integrals and cofactors. The approximate weights are
(-0.61794135500488, 0.29141786021722, -0.08042267470752,
0.01021811007038). R07 proves \(Z>0\), \(\|h_0\|_\infty=1\),
and the exact three cancellations at Q. Its
[pinning certificate](../cusp_robustness/results/pinned_cusp_certificate.json)
and [proof](../cusp_robustness/PROOF.md) are frozen inputs.

Write \(H\) for the same integral with an extra factor \(h_0\), and set

\[
F_\epsilon=F+\epsilon H,\qquad
-\tfrac12\leq\epsilon\leq\tfrac12 .
\]

This is one fixed, explicitly constructed kernel direction. Its even
extension gives positive even kernels, since
\(\Phi_\epsilon=\Phi(1+\epsilon h_0)\geq\Phi/2\) on the real integration
domain. The real analytic dependence on all finite control parameters
follows from the super-exponential kernel tail. The three heat identities
remain valid for F, H and every fixed linear combination.

**Theorem (specified cusp sheet and two strict nesting directions).**
For every \((\nu,\epsilon)\in[-29,0]\times[-1/2,1/2]\), the recorded
uniqueness tubes identify a single real analytic cusp graph
\(c(\nu,\epsilon)=(t_*,\lambda_*,\mu_*)\), with

\[
F_\epsilon=(F_\epsilon)_t=(F_\epsilon)_{tt}=0,\qquad
(F_\epsilon)_{ttt}>0>(F_\epsilon)_{tttt},\qquad
0.26<\partial_\nu\mu_*<0.34.
\]

Its \(\nu=0\) edge is exactly Q, independently of \(\epsilon\).
For each amplitude there is exactly one \(\mu_*=0\) crossing on the
certified arc. Uniqueness is asserted in the specified tubes, not among
all possible cusps of the integral family.

For every section use its own exact cusp and retain the original units:

\[
s=t-t_*,\qquad \ell=\lambda-\lambda_*,\qquad m=\mu-\mu_*.
\]

The common window is
\[
|s|\leq0.003,\qquad |\ell|\leq10^{-6},\qquad |m|\leq2\,10^{-9}.
\]

For \(0<\ell\leq10^{-6}\) there are two folds
\(m_-(\ell,\nu,\epsilon)<0<m_+(\ell,\nu,\epsilon)\).
Between them there are exactly three simple real zeros in this t window.
Off the discriminant outside this strip there is exactly one simple
real zero. At a noncusp fold there are one double and one simple zero;
at the cusp there is one triple zero. No zero crosses the t-window boundary.

Put \(W=m_+-m_-\). Throughout the stated positive-\(\ell\) window,

\[
\partial_\nu m_+<0<\partial_\nu m_-,
\qquad
\partial_\epsilon m_+<0<\partial_\epsilon m_-,
\tag{1}
\]
\[
0.0003\ell^{3/2}<-\partial_\nu W<0.003\ell^{3/2},
\qquad
0.0002\ell^{3/2}<-\partial_\epsilon W<0.005\ell^{3/2}.
\tag{2}
\]

Consequently decreasing \(\nu\) strictly widens the centered three-root
strip, and increasing \(\epsilon\) strictly narrows it, with both fold
boundaries moving in the appropriate direction. Width monotonicity alone
would not imply this nesting; both inequalities in (1) are established.
At the parameter endpoints derivatives mean those of the analytic local
extension, equivalently the relevant one-sided derivatives.

The common geometric bounds are
\[
1.80s^2<\ell(s)<2.21s^2,\quad
1.61|s|^3<|m(s)|<2.09|s|^3
\quad(s\ne0),
\]
\[
0.49\ell^{3/2}<|m_\pm(\ell)|<0.86\ell^{3/2},
\qquad
0.98\ell^{3/2}<W<1.72\ell^{3/2}.
\]

## 2. Remove the irrelevant common amplitude

At the exact Q define
\[
\alpha=H_{ttt}(Q)/F_{ttt}(Q)
\simeq-0.40092694736584545,\quad
K=H-\alpha F,\quad
\rho=\frac{\epsilon}{1+\alpha\epsilon},\quad G=F+\rho K .
\]
Then \(F_\epsilon=(1+\alpha\epsilon)G\).
The prefactor is positive on the physical amplitude interval, so all
zeros, multiplicities, folds and cusp locations are unchanged.
Moreover \(\rho_\epsilon=(1+\alpha\epsilon)^{-2}>0\).
The endpoint rho values lie near -0.4165058004 and 0.6253622987.

We prove the uniform statements on the slightly larger rho interval
[-1/2,3/4], using four adjacent slabs of width 5/16. This normalization
retains the actual shape change while removing a large nearly common
change in the function's amplitude. No control coordinates are rescaled.
It is not an approximation or a discarded perturbation term.

## 3. Two-variable continuation with explicit gluing

Read the 58 R03 centers \(x_j\), \(\nu_j=-(2j+1)/4\), predictors \(v_j\),
and uniqueness radii \(R_i=2^{-10}\). Each driver half-width is 1/4.
At each center let Y be an exact dyadic midpoint inverse of the cusp
Jacobian of F, and let \(u_j\) be the dyadic midpoint of \(-Y(K_0,K_1,K_2)\).
The two-variable predictor is
\[
a_j(z,\rho)=x_j+v_jz+u_j\rho,\qquad |z|\leq1/4.
\]

For the cusp equations \(G_0=G_1=G_2=0\) use the map
\(x\mapsto x-Y(G_0,G_1,G_2)\). For each of 58 times 4 parameter cells,
the saved Taylor models bound the preconditioned derivative defect and
the residual at \(a_j\). In the weighted max norm let these bounds be q
and eta. All 232 cells satisfy \(q+\eta<1\); the largest sum is below
0.258. Banach's theorem gives existence and uniqueness in the whole
radius-R box and the componentwise tighter enclosure
\(r_i=R_i\eta/(1-q)\). The largest recorded r is below 0.000236.
At an exact cusp the Jacobian determinant is \(G_3^2G_4/64\ne0\),
so the identified graph is real analytic locally.

There are 228 joins in the nu direction. At a common driver boundary,
the correlated predictor difference is bounded as
\[
(x_j+v_jz_j)-(x_{j+1}+v_{j+1}z_{j+1})
 +(u_j-u_{j+1})\rho .
\]
The left solution's entire tight enclosure is contained strictly in the
right uniqueness box for every rho on that slab. Thus uniqueness
identifies the two roots; mere overlap of their boxes is not used.

At each of the 174 rho joins the predictors and the uniqueness radii
are exactly the same for the full common nu cell. The two constructions
therefore coincide by uniqueness. This yields one cusp graph, not a
collection of unrelated pointwise roots. The frozen exact Q is contained
in the first tube for all rho; its exact pinning identifies the whole
nu=0 edge. The last tube gives \(\mu_*(-29,\rho)<0\), while
\(\mu_*(0,\rho)=\mu_Q>0\). The strictly positive nu derivative proves
the unique \(\mu=0\) crossing.

## 4. Integral enclosures and the correlated Taylor model

The old central F jets through order 68 and positive absolute derivative
majorants through order 74 are reused with their exact recorded domains.
New H jets of orders 0 through 68 are integrated at each of the 58
centers: 4002 rigorous enclosures. The finite analytic integrand uses
16 kernel terms, cutoff 2, eight subintervals, and requested quadrature
tolerances \(10^{-70}\), at 100 decimal digits. The omitted real-axis
kernel series and the infinite-domain tail are bounded separately as in
R01. Since \(\|h_0\|_\infty=1\), the corresponding absolute H bounds do
not exceed the old F majorants. For K a valid multiplier is
\(\beta=1+|\alpha|\).

The commuting directional operators are
\[
A=v_tD-v_\lambda D^2/4+v_\mu D^4/16-D^6/64,\quad
T=u_tD-u_\lambda D^2/4+u_\mu D^4/16,\quad
U=w_tD-w_\lambda D^2/4+w_\mu D^4/16 .
\]
Expand in \(zA+\rho T+U\) through total order seven. Terms with
p+q+r=8, absolute coefficients, and the old positive majorants bound
the Taylor remainder. Every segment is checked to stay in the old
majorant domain. For \(G_n\) the worst derivative order is
26+6*8=74; retained central orders need at most 26+6*7=68.

For linear combinations such as a row of Y times the Jacobian, combine
central derivative coefficients before taking interval absolute values.
Keep the joint polynomial in z and rho. For \(P(z,\rho)=\sum_pP_p(\rho)z^p\),
bound \(P_0(\rho)\) and add the symmetric radius
\(\sum_{p>0}\sup|P_p(\rho)|(1/4)^p\).
The implementation encodes a monomial as degree p+64q; it rejects every
product that might reach p=64. The largest needed p is 49, so no
two-variable coefficients alias. After constructing K's polynomial,
G is obtained as F+rho*K, including the corresponding remainder factors.

## 5. A transport identity for an arbitrary analytic driver

This is the analytic step that extends R05's nu calculation to rho.
Fix a driver sigma and put \(R=G_\sigma\), where sigma is independent
of t, lambda and mu. Write \(R_n=\partial_t^nR\).
Both G and R satisfy the lambda and mu heat identities.
At the cusp,
\[
\mu_\sigma=-16R_0/G_4,\qquad
\lambda_\sigma=(4R_1+G_5\mu_\sigma/4)/G_3,\qquad
t_\sigma=(-R_2+G_4\lambda_\sigma/4-G_6\mu_\sigma/16)/G_3.
\tag{3}
\]
For sigma=nu use \(R_n=-G_{n+6}/64\); for sigma=rho use \(R_n=K_n\).

Along the implicit fold set \(\Delta=G_3G_4-G_2G_5<0\). As in R04,
\[
\ell_s=4G_2G_4/\Delta,\qquad m_s=16G_2^2/\Delta .
\]
Differentiating G=0 on a fold at fixed relative ell, the moving-t term
vanishes because \(G_1=0\), and gives
\[
\partial_\sigma m|_\ell=B_\sigma(s)-\mu_\sigma,\qquad
B_\sigma(s)=\frac{4\lambda_\sigma G_2-16R_0}{G_4}.
\tag{4}
\]
All derivatives in (4) are evaluated at the full fold point except the
cusp tangent \(\lambda_\sigma,\mu_\sigma\), which is constant as s varies.

Let \(a=G_3,b=G_4,c=G_5,\ldots,g=G_9\) at the cusp and \(k=-a/b>0\).
The heat identities imply the exact local expansions
\[
\ell(s)=2s^2+A_3s^3+O(s^4),\quad
A_3=\tfrac43(c/b-b/a),\qquad
m(s)=-\tfrac{16}{3}ks^3-4s^4+O(s^5).
\]
Applying the chain rule at fixed ell establishes
\[
B_\sigma(0)=\mu_\sigma,\quad B_\sigma'(0)=B_\sigma''(0)=0,\quad
B_\sigma'''(0)=-32k_\sigma,\quad
B_\sigma''''(0)=96k(A_3)_\sigma .
\tag{5}
\]
The invariant fourth coefficient -4 in m(s) is needed for the last
identity. Finite sampled derivative tests are not the basis for (5).

For the rho implementation put \(r_n=K_n\) and define
\[
U=br_1-cr_0,\qquad V=-abr_2+b^2r_1+(ad-bc)r_0,
\]
\[
P_3=a^2br_3+bV-acU-a^2er_0,\quad
P_4=a^2br_4+cV-adU-a^2fr_0,\quad
P_5=a^2br_5+dV-aeU-a^2gr_0.
\]
Equation (3) shows that the total cusp derivatives of a,b,c are
\(P_3/(a^2b),P_4/(a^2b),P_5/(a^2b)\). Quotient differentiation gives
\[
N_\rho=aP_4-bP_3,\quad
(k)_\rho=\frac{N_\rho}{a^2b^3},
\]
\[
N_{4,\rho}=a^2(bP_5-cP_4)-b^2(aP_4-bP_3),\qquad
B_\rho''''(0)=-\frac{128N_{4,\rho}}{a^3b^4}.
\tag{6}
\]
The rational checker constructs expanded monomials from these quotient
identities. Substitution \(r_n=-G_{n+6}/64\) gives exactly the two frozen
R05 nu polynomials with their 1/64 factor. These two reductions are
verified as exact polynomial identities over the rationals.

Correlated polynomial evaluation, a jet remainder bound, and a spatial
mean-value correction from the predictor to the true cusp enclose
\(k_\nu,k_\rho\) and both fourth derivatives. Both k derivatives are
strictly negative on every parameter cell.

## 6. From the cusp identities to the entire finite window

The local geometry calculation is repeated in every new cell; it is not
inferred solely from persistence of a cusp. It verifies a uniform
two-equation fold contraction, derivative signs, quadratic/cubic bounds,
t-boundary signs, three-root witness signs and a one-root reference
cover. The classification argument of
[R04](../cusp_geometry/PROOF.md) then applies on the same window.

Set \(S=3/4000\). The quadratic bound gives
\(1.80S^2>10^{-6}\), so all folds used in the theorem have |s|<S.
Enclose G and K through order 26 in the larger offset box
\[
|e_t|\leq2S,\quad |e_\lambda|\leq2.22S^2,\quad
|e_\mu|\leq2.10S^3.
\]
At fold points impose the exact \(G_0=G_1=0\), and bound G2 using the
certified positive derivative along the fold. The generator obtains the
fifth derivative of (4) by solving the implicit fold power series.
The separate rational checker instead differentiates the fold ODE:
\[
\frac{d}{ds}G_n=G_{n+1}-\ell_sG_{n+2}/4+m_sG_{n+4}/16,
\]
with the same equation for K. No R08 generating module or FLINT is
imported by that checker.

If M4 bounds \(|B_\sigma''''(0)|\) and M5 bounds
\(|B_\sigma'''''(s)|\) on |s|<=S, then
\[
B_\sigma'''(s)\in -32k_\sigma+
[-M_4S-M_5S^2/2,\ M_4S+M_5S^2/2].
\]
All these intervals are strictly positive for both drivers.
Equation (5) and integration three times give that
\(B_\sigma(s)-\mu_\sigma\) has the sign of s. The negative-s branch is
the upper fold; the positive-s branch is the lower fold. This proves
(1) first for nu and rho. If [b0,b1] is the positive third-derivative
interval, the width rate lies between
\[
\frac{b_0}{3(2.21)^{3/2}}\ell^{3/2}
\quad\hbox{and}\quad
\frac{b_1}{3(1.80)^{3/2}}\ell^{3/2}.
\]
The recorded bounds are inside (0.0003,0.003) for both nu and rho.
Finally multiply the rho rates by \((1+\alpha\epsilon)^{-2}\).
The rational checker verifies the conservative physical epsilon bounds
in (2) without using floating-point proof comparisons.

## 7. Quantitative finite comparisons and checks

There are 21 further narrow cusp contractions at nu=0,-5,-10,-15,-20,-25,-29
and epsilon=-1/2,0,1/2. Each is contained in the appropriate sheet
uniqueness tube. At nine of these cusps, 144 more contractions identify
both finite folds at eight positive offsets
\(\ell=j^2/(64\,10^6)\), j=1,...,8. Cusp uncertainty is propagated into
the centered Taylor jets before imposing the three exact cusp zeros.
Their 21+144 contraction inequalities and width comparisons are checked
separately using rational intervals on a 512-bit outward dyadic grid.

At ell=10^-6, the following are outward percentage intervals for
\(100[W(\nu,+1/2)/W(\nu,-1/2)-1]\):

| nu | Finite W percentage change |
|---|---|
| 0 | [-0.05201561, -0.05201560] |
| -15 | [-0.04707662, -0.04707661] |
| -29 | [-0.04254131, -0.04254130] |

These are finite-width values, not substitutions of the leading
coefficient \(C=(8\sqrt2/3)k\). For comparison, the leading-coefficient
percentage at Q lies in [-0.0520157034,-0.0520157033].
At Q one can also use the exact closed formula
\[
C(0,\epsilon)=C(0,0)
\frac{1+\alpha\epsilon}{1+\gamma\epsilon},\qquad
\gamma=H_{tttt}(Q)/F_{tttt}(Q).
\]
The cusp position is exactly fixed, while this coefficient changes.

For selected new H moments, 21 rigorous comparisons use the independent
integrand representation
\[
H_n(t)=\tfrac12\sum_{j=1}^4w_j\{F_n(t+j)+F_n(t-j)\}.
\]
They use 18 terms, 16 integration pieces, tolerance 10^-85 and 110 digits.
Nine additional direct mpmath comparisons at 90/115 digits agree and lie
in the cached rigorous balls. These numerical checks are sampling checks,
not additional continuum proofs.

## 8. Trust boundary and limits

The separate continuum checker verifies every contraction inequality,
228+174 joins, local root classification conditions, expanded transport
polynomials and both fifth-derivative ODEs with rational arithmetic.
It assumes the saved integral/majorant enclosures and the new correlated
two-variable Taylor/predictor polynomial ranges; it does not independently
rebuild that entire upstream stage. The analytic derivation in this note
and the Arb implementation supply that stage. This is a deliberately
explicit trust boundary, not a claim of two wholly independent proofs.

Results concern the selected h0, the stated parameter rectangle and
moving cusp-centered root windows. They do not establish universal
monotonicity for all kernel perturbations, an optimal admissible amplitude,
a global count of real zeros, a property of the Riemann hypothesis, a
physical time evolution or physical stability. They do not assert
inclusion in fixed absolute (lambda,mu) coordinates. Exact pinning by
itself is elementary linear algebra; the family-specific content here is
the whole connected sheet with two uniform strict finite nesting laws.

The figures connect certified point values for explanation. Lines between
points are not used as proof. The original manuscript and all R01-R07
packages are preserved.
