# R05: strict nesting and monotonicity of the finite three-root width

20 September 2026. Computer-assisted local result, built on the frozen
R01-R04 packages. External mathematical review and literature priority
assessment remain outstanding. The figures are explanatory artifacts;
the argument below and its recorded interval witnesses establish the claims.

## 1. Setting and theorem

Use the kernel, integral normalization and analytic estimates in
[R01](../cusp_verified/PROOF.md), the single analytic cusp graph of
[R03](../cusp_connection/PROOF.md), and the uniform local-region theorem of
[R04](../cusp_geometry/PROOF.md). Thus

\[
F(t;\lambda,\mu,\nu)=\int_0^\infty\Phi(u)
e^{\lambda u^2+\mu u^4+\nu u^6}\cos(2tu)\,du,
\qquad D_n=\partial_t^nF,
\]

\[
\partial_\lambda D_n=-D_{n+2}/4,\quad
\partial_\mu D_n=D_{n+4}/16,\quad
\partial_\nu D_n=-D_{n+6}/64.
\tag{1}
\]

For -29 <= nu <= 0 let c(nu)=(t*,lambda*,mu*) be the exact cusp from
R03. Work in the translated, unrescaled coordinates

\[
s=t-t_*(\nu),\qquad \ell=\lambda-\lambda_*(\nu),\qquad
m=\mu-\mu_*(\nu).
\]

R04 gives two folds m_low(ell,nu)<0<m_high(ell,nu) for
0<ell<=L=10^-6, in the common local window
|s|<=0.003, |ell|<=10^-6, |m|<=2*10^-9. Between the folds there are
exactly three simple real zeros in that t window. Off the discriminant
outside this strip there is one. Define W_nu(ell)=m_high-m_low.

**Finite-width and nesting theorem.** Throughout -29<=nu<=0 and
0<ell<=10^-6,

\[
\partial_\nu m_{\rm high}(\ell,\nu)<0,
\qquad \partial_\nu m_{\rm low}(\ell,\nu)>0,
\qquad \partial_\nu W_\nu(\ell)<0. \tag{2}
\]

Both implementations described below verify the conservative bounds

\[
0.0003\,\ell^{3/2}< -\partial_\nu W_\nu(\ell)
 <0.003\,\ell^{3/2}. \tag{3}
\]

In particular, for nu1<nu2, in these centered coordinates,

\[
m_{\rm low}(\ell,\nu_1)<m_{\rm low}(\ell,\nu_2)
<m_{\rm high}(\ell,\nu_2)<m_{\rm high}(\ell,\nu_1). \tag{4}
\]

The corresponding three-root strips are strictly nested. For a fixed
positive ell their widths increase as nu decreases from the quartic
point Q (nu=0) towards the sextic point S
(nu approximately -28.82453269539050), and the assertion holds on the
entire certified driver interval [-29,0]. Derivatives at driver endpoints
are interpreted using the analytic local extensions, or one-sided values.

This compares sections after translating by their respective exact cusps.
It does not assert inclusion of regions in absolute (lambda,mu)
coordinates. The t windows also move with the cusp. These are parameter
derivatives, not physical time evolution or dynamical stability.
At ell=0 the width is zero and the strict inequalities in (2)-(3)
are not asserted. There is no global real-axis root-count assertion.

## 2. A scalar transport function for both folds

At a fixed nu, R04 provides an analytic implicit fold
(ell(s,nu),m(s,nu)) for |s|<=0.003, with F=D1=0. Put

\[
\Delta=D_3D_4-D_2D_5<0.
\]

Its tangent satisfies

\[
\ell_s=4D_2D_4/\Delta,\qquad
m_s=16D_2^2/\Delta. \tag{5}
\]

All D_n in a formula along this fold are evaluated at its full point.
Define, at fixed nu,

\[
B(s,\nu)=\frac{4\lambda_*'(\nu)D_2+D_6/4}{D_4}. \tag{6}
\]

Here D4 stays strictly negative. Differentiate F=0 with respect to nu
along a fold while keeping the relative coordinate ell fixed.
The moving t term vanishes because D1=0. Using (1),

\[
0=-D_2\lambda_*'/4+D_4(\mu_*'+\partial_\nu m)/16-D_6/64.
\]

Therefore at either root s=s_-(ell,nu)<0 or s=s_+(ell,nu)>0 of
ell(s,nu)=ell,

\[
\partial_\nu m(\ell,\nu)=B(s,\nu)-\mu_*'(\nu). \tag{7}
\]

The negative s branch is the upper fold; the positive s branch is the
lower fold. This identification and the nonzero ell_s away from zero
are already part of R04.

## 3. Exact cancellations at the cusp

In this section let a=D3, b=D4, c=D5, d=D6, e=D7, f=D8, g=D9,
h=D10, i=D11 at the exact cusp; a>0 and b<0. Write
k=-a/b>0 and C=(8*sqrt(2)/3)k. Differentiating the cusp equations gives

\[
\mu_*'=\frac{d}{4b},\quad
\lambda_*'=\frac{4c\mu_*'-e}{16a},\quad
t_*'=\frac{f/64+b\lambda_*'/4-d\mu_*'/16}{a}. \tag{8}
\]

On the fold ell_s(0)=m_s(0)=0, ell_ss(0)=4, m_ss(0)=0.
For every n, (1) then gives the exact identity

\[
\left.\frac{d^2}{ds^2}D_n\right|_{s=0}
=D_{n+2}-\frac{4}{4}D_{n+2}=0.
\]

Using (8) in (6) yields

\[
B(0,\nu)=\mu_*',\qquad B_s(0,\nu)=B_{ss}(0,\nu)=0. \tag{9}
\]

To obtain the next derivatives, expand the implicit fold using (1):

\[
\ell(s,\nu)=2s^2+A_3s^3+O(s^4),\qquad
A_3=\frac43\left(\frac cb-\frac ba\right),
\]

\[
m(s,\nu)=-\frac{16}{3}ks^3-4s^4+O(s^5). \tag{10}
\]

All coefficients depend analytically on nu; notably the fourth m
coefficient is exactly -4. Derivatives at fixed ell and at fixed s obey
partial_nu m|ell = partial_nu m|s - m_s partial_nu ell|s / ell_s
away from s=0. The expansions extend the expression analytically there.
Equations (7)-(10) imply

\[
B_{sss}(0,\nu)=-32k'(\nu)=-6\sqrt2\,C'(\nu)>0,
\qquad B_{ssss}(0,\nu)=96k A_3'. \tag{11}
\]

The positivity at the cusp follows from R04. It alone would not prove
positivity on a specified finite interval. The rest of R05 supplies
explicit remainder bounds to make that step.

For a useful evaluation of the fourth derivative define

\[
T=abf+bcd-b^2e-ad^2,\quad U=cd-be,
\]
\[
P_3=bT-caU+ea^2d-ga^2b,
\]
\[
P_4=cT-daU+fa^2d-ha^2b,\quad
P_5=dT-eaU+ga^2d-ia^2b,
\]
\[
N_4=a^2(bP_5-cP_4)-b^2(aP_4-bP_3).
\]

The total cusp derivatives of D3,D4,D5 are respectively
P3/(64*a^2*b), P4/(64*a^2*b), P5/(64*a^2*b). Substitution in the
quotient derivative of A3 in (10) proves

\[
B_{ssss}(0,\nu)=-\frac{2N_4}{a^3b^4}. \tag{12}
\]

Exact Fraction tests compare (9)-(12) with implicit Taylor coefficients
for three distinct rational derivative vectors, and compare the factored
N4 with the checker's expanded 22-monomial polynomial. These tests support
the analytic derivation; finite test vectors by themselves are not a
polynomial-identity proof or a replacement for the derivation above.

## 4. Uniform derivative bounds on all 58 driver cells

The complete R01-R04 file manifests are checked before computation.
Extend R04's correlated Taylor model through D26, still at total order
K=8. The new integrals are the central orders 57,...,68 and the new
positive majorants are orders 63,...,74. The same frozen integrator and
the same larger R03 majorant domains are used.

For each driver cell nu=nu_j+z, |z|<=1/4, R03 gives
c(nu)=x_j+v_j z+w with a certified tight componentwise bound on w.
For a local offset e, expand with the commuting operators

\[
\mathcal A=v_tD_t-v_\lambda D_t^2/4+v_\mu D_t^4/16-D_t^6/64,
\quad
\mathcal H=(w_t+e_t)D_t-(w_\lambda+e_\lambda)D_t^2/4
 +(w_\mu+e_\mu)D_t^4/16.
\]

Keep each combined central coefficient A^p D_n before multiplying by
z^p. Terms p+q<8 give the polynomial in z*A+H; terms p+q=8 with the
positive majorants bound the integral Taylor remainder. Central orders
up to 26+6*7=68 and remainder orders up to 26+6*8=74 suffice. All segments
must lie inside the existing majorant domains; code checks this.

Set S=3/4000=0.00075. The R04 inequalities imply on |s|<=S

\[
|\ell(s,\nu)|\le2.21S^2,\qquad |m(s,\nu)|\le2.09S^3.
\]

Use the slightly larger local derivative box
|e_t|<=2S, |e_lambda|<=2.22S^2, |e_mu|<=2.10S^3.
At fold points impose D0=D1=0 exactly. R04's bound on w_s for w=D2
also gives |D2|<=sup(w_s)*S. All these restrictions apply at every actual
fold point; they are not assumptions about arbitrary points of the box.

For (12), interval evaluation without driver correlation would be too
coarse. Normalize the derivatives by a fixed positive central scale,
expand the degree-seven N4 in the common driver z through degree 49,
then add explicit errors for central Taylor remainders and the certified
cusp displacement w, using first partial derivatives and the mean-value
theorem on the enclosing boxes. Numerator and denominator both have
degree seven, so the scale cancels. This yields M4>=|B_ssss(0,nu)|.

To bound M5>=sup_{|s|<=S}|B_sssss(s,nu)|, the generator builds local
Taylor series of the implicit controls in an increment h, by solving
F=Ft=0 coefficient by coefficient with the nonsingular control Jacobian
from R04. Substitute those series in (6) through degree five. Coefficients
are derivatives divided by factorial; hence M5=120*abs(coefficient_5),
with an outward interval upper bound. Only derivatives through D26
are required. The expansion is local at every fold point in the box,
not a truncated global approximation of the fold.

The fundamental theorem of calculus, or Taylor's formula for B_sss, gives

\[
B_{sss}(s,\nu)\in B_{sss}(0,\nu)+[-E,E],\quad
E=M_4S+\tfrac12 M_5S^2. \tag{13}
\]

Every recorded cell in results/width_certificate.json satisfies
0<beta_j<=B_sss(s,nu)<=Gamma_j throughout |s|<=S and its whole driver
interval. No inference from a grid of positive point values is used.

## 5. From the derivative bound to finite-width monotonicity

By R04, ell>=1.80*s^2 along the folds. Since

\[
1.80(3/4000)^2=1.0125\times10^{-6}>L,
\]

both folds at every 0<ell<=L lie strictly inside |s|<S. Integrating the
positive third derivative three times, using (9), gives

\[
\operatorname{sign}(B(s,\nu)-B(0,\nu))=\operatorname{sign}s,
\]

\[
\frac{\beta_j}{6}|s|^3\le |B(s,\nu)-B(0,\nu)|
\le\frac{\Gamma_j}{6}|s|^3. \tag{14}
\]

Together with (7), the branch identification proves (2). Because
1.80*s^2<=ell<=2.21*s^2 on each branch, adding the two absolute
velocities in (14) proves

\[
\frac{\beta_j}{3(2.21)^{3/2}}
\le-\ell^{-3/2}\partial_\nu W_\nu(\ell)
\le\frac{\Gamma_j}{3(1.80)^{3/2}}. \tag{15}
\]

The generating calculation verifies the stronger readable range
(0.0004,0.0025); the separate checker verifies (0.0003,0.003) using
rational squared comparisons. The theorem states the common, more
conservative range. Integrating the strict fold velocities gives (4).
The exact-cusp graph and uniform implicit folds glue at driver-cell
boundaries by R03/R04, so the result concerns a single connected family.

## 6. Independent arithmetic and supporting checks

check_width.py imports neither FLINT nor the generator. It uses exact
Fraction endpoints, rounded outwards to a 192-bit dyadic grid after each
operation. It reconstructs N4 from 22 expanded monomials and predictor
coefficients from the multinomial formula. For the fifth derivative it
uses a different recurrence, namely the fold differential equations
(5) and

\[
\frac{dD_n}{ds}=D_{n+1}-\ell_sD_{n+2}/4+m_sD_{n+4}/16.
\]

It verifies (13)-(15) for all 58 cells. Its smallest third-derivative
lower bound is approximately 0.00544601417, strictly positive. That
number is a display summary; exact endpoint fractions are recorded.
The separate implementation obtains different, in this case narrower,
intermediate bounds; agreement means the sign and stated theorem, not
identical interval endpoints.

test_width.py checks exact cusp identities, the ODE-versus-implicit
fifth derivative for exact inputs, outward arithmetic and rejection of
invalid domains. It also compares 36 selected extended enclosures with
direct integrals at three cells, both signed driver endpoints, using
20 kernel terms and 16 quadrature panels. check_independent.py performs
27 additional derivative comparisons with mpmath and obtains B4 from
the derivative of A3 along the cusp tangent. These are useful numerical
checks; the mpmath calculations are not rigorous integral enclosures.
An additional endpoint Taylor test makes 60 direct-integral comparisons
at three sampled sections, both folds and both endpoints. The five
test groups and all 96 direct-integral comparisons are linked to their
current source files and input certificates in results/test_report.json.

The rational checker trusts the saved integral and correlated derivative
enclosures. It does not independently prove the integration/tail bounds,
the analytic argument, or the correctness of every line of the software
stack. This remains a computer-assisted proof package with stated
trusted components, not a formal proof-assistant verification.

## 7. Finite endpoint widths used in Figure 2

endpoint_folds.py encloses the derivatives at the exact Q and S from
their R01 radius-10^-24 boxes, then sets D0=D1=D2=0 by those cusp
theorems. The uncertainty in t,lambda,mu for Q or t,lambda,nu for S
is propagated by the hierarchy and positive majorants. At fixed exact
driver it uses an order-eight Taylor formula in (s,ell,m), with positive
majorants for the complete total-degree-eight remainder.

For each ell=10^-6*(k/32)^2, k=1,...,32, and each of Q,S, solve (F,Ft)=0
in (s,m) for both signs of s. The Jacobian is

\[
J_{(s,m)}=\begin{pmatrix}D_1&D_4/16\\D_2&D_5/16\end{pmatrix}.
\]

A fixed invertible point preconditioner Y, a rectangular ball of radii r,
q=||I-YJ||_r<1 and eta=||YH(center)||_r with eta+q<1 establish one
root and a refined radius r*eta/(1-q). All 128 contractions pass. Their
boxes lie in the corresponding R04 window, on the specified s sign,
with D2 nonzero, which identifies the intended fold. check_endpoints.py
independently recomputes all contraction inequalities, refined containments,
width differences and endpoint ratios using outward rational arithmetic.
It too assumes the saved integral/Taylor enclosures.

At ell=10^-6 the interval witnesses imply

\[
1.2946095162\times10^{-9}<W_Q<1.2946095164\times10^{-9},
\]
\[
1.3269052468\times10^{-9}<W_S<1.3269052470\times10^{-9},
\]
\[
2.49463101<100(W_S/W_Q-1)<2.49463103.
\tag{16}
\]

This is a finite-width comparison at one specified ell. It is distinct
from the approximately 2.4946327745 percent increase of C in R04.
No constant percentage for every ell or every pair of driver values is
claimed. Connecting the 32 samples produces explanatory lines; the
uniform theorem (2), not that interpolation, establishes nesting between
samples. The S section here fixes nu=nu_S and permits mu perturbations;
it is not the original mu=0 section in the (lambda,nu) plane.
