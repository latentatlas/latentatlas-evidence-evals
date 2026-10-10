# Uniform fold neighborhoods along the certified cusp curve

R04, 20 September 2026. A local computer-assisted argument. External
expert review and literature priority assessment remain outstanding.

## 1. Family, coordinates and theorem

Use the kernel, normalization, integral/tail bounds of the frozen R01
package and the analytic cusp graph of R03:

\[
F(t;\lambda,\mu,\nu)=\int_0^\infty\Phi(u)
e^{\lambda u^2+\mu u^4+\nu u^6}\cos(2tu)\,du,
\quad c(\nu)=(t_*(\nu),\lambda_*(\nu),\mu_*(\nu)),\quad -29\le\nu\le0.
\]

Write D_n=∂_t^nF. Throughout, ν is held fixed when studying a local fold
section. Coordinates are s=t−t*(ν), ℓ=λ−λ*(ν), m=μ−μ*(ν). These are
relative to the **exact** cusp, not its approximate predictor.

Set T=3/1000, L=10^-6, M=2×10^-9 and define

\[
I_\nu=t_*(\nu)+[-T,T],\qquad
P_\nu=(\lambda_*(\nu),\mu_*(\nu))+[-L,L]\times[-M,M].
\]

**Uniform local-region theorem.** For every ν∈[−29,0], Iν×Pν contains
exactly the reference cusp and two nondegenerate fold arcs attached to
it. The arcs exit Pν through ℓ=L and have no other intersections. For
0<ℓ≤L they are graphs m_low(ℓ,ν)<0<m_high(ℓ,ν). Between them there are
exactly three simple real zeros in Iν. Everywhere else off the
discriminant in Pν there is exactly one simple zero. On a fold there
are one double and one simple zero; at the cusp, one triple zero.
No zero crosses either endpoint of Iν for any control in Pν.

The fold arcs vary analytically with ν away from their cusp edge; taken
together over ν they form two fold sheets attached to the cusp curve.
The full implicit fold surface is analytic in coordinates (s,ν).

Along the auxiliary fold graph for |s|≤T, the following finite bounds
hold simultaneously for every ν:

\[
1.80s^2\le\ell(s,\nu)\le2.21s^2,\qquad
1.61|s|^3\le|m(s,\nu)|\le2.09|s|^3,
\]

\[
\operatorname{sign}m=-\operatorname{sign}s\ (s\ne0),\qquad
0.49\ell^{3/2}\le|m|\le0.86\ell^{3/2}.
\]

Consequently the three-root width Wν(ℓ)=m_high−m_low satisfies

\[
0.98\ell^{3/2}\le W_\nu(\ell)\le1.72\ell^{3/2},\qquad0<\ell\le10^{-6}. \tag{1}
\]

**Opening-coefficient theorem.** The leading width coefficient is

\[
C(\nu)=\lim_{\ell\downarrow0}\frac{W_\nu(\ell)}{\ell^{3/2}}
=-\frac{8\sqrt2}{3}\frac{D_3(c(\nu),\nu)}{D_4(c(\nu),\nu)}.
\tag{2}
\]

C is analytic and C'(ν)<0 throughout [−29,0]. The generating enclosures
give −0.0019<C'<−0.0007. A separate exact-rational implementation also
proves the strict sign, using a more conservative expanded polynomial.
At the exact quartic and sextic cusps, respectively,

\[
C_Q\simeq1.29460899168316557416,\qquad
C_S\simeq1.32690473189189066537,
\]

and 1.024<C_S/C_Q<1.026. The relative increase is approximately
2.4946327745 percent. This is a statement about the leading coefficient,
not an asserted exact percentage for Wν at a fixed nonzero ℓ. In
particular, strict monotonicity of the finite width for every ℓ in the
rectangle is not proved here.

All comparisons use the same original λ,μ coordinates in fixed-ν
sections. C is coordinate dependent. At the sextic cusp this section
permits μ perturbations; it is not the original μ=0, (λ,ν) section.

## 2. Correlated derivative enclosures on each driver cell

R03 supplies 58 intervals ν=ν_j+z, |z|≤1/4, with exact dyadic centers
x_j, predictors v_j and bounds |c(ν)−x_j−v_jz|≤r_j. These are the
certified tight radii, not estimated Newton errors. Its larger majorant
domain also contains the local neighborhoods below; this is checked
before evaluation.

For w=c(ν)−x_j−v_jz and a local offset e, define commuting operators

\[
A=v_tD_t-v_\lambda D_t^2/4+v_\mu D_t^4/16-D_t^6/64,
\quad B=(w_t+e_t)D_t-(w_\lambda+e_\lambda)D_t^2/4
 +(w_\mu+e_\mu)D_t^4/16.
\]

The directional operator is zA+B. At order K=8 expand

\[
D_n(x_j+v_jz+w+e,\nu_j+z)
=\sum_{p+q<K}\frac{z^p A^p B^q D_n(x_j,\nu_j)}{p!q!}+R_n. \tag{3}
\]

The integral Taylor remainder is bounded by the p+q=K terms with
|z|^p, absolute operator coefficients, and the positive derivative
majorants at the corresponding orders. The combinations A^pD_n are
formed before applying z or the w intervals; the same z is retained
in all four coordinate displacements. Interval arithmetic otherwise
overestimates this small oscillatory quantity too severely.

The original central derivatives D_0,…,D_50 and majorants B_0,…,B_56
are reused only after their complete package hashes are checked. Six
extra central derivatives and six extra majorants extend (3) through
D_14: central orders through 56 and remainder orders through 62.
Their integrator, normalization and majorant domain are unchanged.

For the exact-cusp derivative vector take e=0. For the local derivative
box take |e_t|≤2^-8, |e_λ|≤2^-12, |e_μ|≤2^-19. This is larger than
the auxiliary region |s|≤T, |ℓ|≤2^-13, |m|≤2^-20, and absorbs interval
representation widening. Every real segment in the following Taylor
and mean-value arguments lies in the appropriate box.

## 3. Taylor formulas about the exact cusp

At the exact cusp D_0=D_1=D_2=0 identically. Setting these coefficients
to zero is justified by R03, even though its numerical predictor has
a nonzero residual. The remaining central derivatives are enclosed by
(3). Let b_n be the derivative enclosure over the local box.

For n≤5, first expand in t through derivative order five:

\[
D_n(t_*+s;\lambda_*,\mu_*,\nu)
\in\sum_{k=0}^{5-n}\frac{s^kD_{n+k}(c)}{k!}
 +\frac{s^{6-n}}{(6-n)!}\,b_6. \tag{4}
\]

The signed remainder is valid because the weighted average of the
sixth derivative lies in b6, for either sign of s. For n=0,1 then
expand to first order in (ℓ,m). The additional symmetric error is
bounded by

\[
\frac12\left[\frac{|\ell|^2}{16}|b_{n+4}|
 +\frac{2|\ell m|}{64}|b_{n+6}|
 +\frac{|m|^2}{256}|b_{n+8}|\right]. \tag{5}
\]

The linear terms are −ℓ D_(n+2)/4+m D_(n+4)/16, evaluated with (4).
For n=2 the simpler integral mean-value enclosure

\[
D_2\in s b_3-\ell b_4/4+m b_6/16 \tag{6}
\]

suffices. Higher derivatives are taken directly from their b_n boxes.
These formulas provide small residual bounds relative to the actual
cusp uniformly in ν; its approximate absolute coordinates never
replace the exact center.

## 4. Uniform implicit fold surface and finite geometry

For every (s,ν), solve H=(F,F_t)=0 for the offsets (ℓ,m) in the same
auxiliary rectangle Q=[−2^-13,2^-13]×[−2^-20,2^-20]. Its Jacobian is

\[
H_{(\ell,m)}=\begin{pmatrix}-D_2/4&D_4/16\\-D_3/4&D_5/16\end{pmatrix},
\quad\det H_{(\ell,m)}=\Delta/64,\quad\Delta=D_3D_4-D_2D_5.
\]

Every R03 cell has a fixed invertible dyadic preconditioner Y. The
certificate checks in the scaled max norm that q<0.59 and η+q<0.74<1
for the map p↦p−YH. Hence it has one fixed point in Q for every
|s|≤T and every ν in that cell. The saved bounds also give
D_3>0, D_4<0, Δ<0. The analytic implicit-function theorem applies.
At shared driver boundaries the exact cusp is the same R03 object
and Q is the same offset rectangle. Uniqueness therefore identifies
the fold graphs; no new inference from overlapping boxes is needed.

For fixed ν, let w(s)=D_2 along this fold. Direct differentiation gives

\[
\ell_s=4wD_4/\Delta,\qquad m_s=16w^2/\Delta,\qquad
w_s=D_3-D_4\ell_s/4+D_6m_s/16>0. \tag{7}
\]

Since w(0)=0, this is its only zero. Thus ℓ decreases to its unique
minimum zero at s=0 and increases afterwards; m strictly decreases
through zero. Integrating (7), with uniform positive bounds on w_s,
4D4/Δ and −16/Δ, yields the quadratic and cubic inequalities in §1.
The sharper interval values imply the stated 0.49 and 0.86 bounds
by comparing squares, without numerical square-root assumptions.

At |s|=T, ℓ≥1.80T²>L. Each arm therefore reaches ℓ=L exactly once.
Before that crossing, |m|≤0.86L^(3/2)<M. Neither arm can exit through
a μ edge or the negative λ edge. This proves the asserted complete
discriminant inside the control rectangle.

## 5. Root counts

For every control in Pν, (4)–(5) prove F(t*−T)<0 and F(t*+T)>0.
There is no boundary crossing. D3>0 on Iν×Q implies at most three
real zeros counting multiplicities, by repeated Rolle's theorem.

At ℓ=−L/2,m=0, D1>0 on a 32-piece cover of the entire t interval;
this gives one simple root. At ℓ=L/2,m=0, the values at
s=(−.0015,−.0003,.0003,.0015) have signs (−,+,−,+), giving exactly
three simple roots. All these inequalities hold for every ν in
each cell, not just its center.

The complement of the discriminant in Pν has the region between
the arms and its connected exterior. Simplicity, compactness and
the nonzero window boundary imply constant root count on each.
The two witnesses identify these counts. A fold has a double zero
and one simple zero; the cusp has its single triple zero, by the
same multiplicity bound. This establishes the uniform region theorem.

## 6. The opening coefficient and its change along the curve

From (7), or Taylor differentiation at s=0,

\[
\ell(s,\nu)=2s^2+O_\nu(s^3),\qquad
m(s,\nu)=\frac{16D_3}{3D_4}s^3+O_\nu(s^4). \tag{8}
\]

The two solutions of ℓ(s,ν)=ℓ give
Wν(ℓ)=C(ν)ℓ^(3/2)+Oν(ℓ²), with C as in (2).
The 3/2 exponent and the quadratic coefficient 2 follow from the
local cusp structure and the heat identity; they are not novelty
claims. The new family-specific result is the certified behavior
of C along the entire previously identified arc.

To differentiate along ν, the exact cusp tangent is

\[
\mu_*'=D_6/(4D_4),\quad
\lambda_*'=(4D_5\mu_*'-D_7)/(16D_3),\quad
t_*'=(D_8/64+D_4\lambda_*'/4-D_6\mu_*'/16)/D_3.
\]

For k=−D3/D4, substitution into its total derivative gives

\[
k'=\frac{N}{64a^2b^3},\quad (a,b,c,d,e,f,g,h)=(D_3,D_4,D_5,D_6,D_7,D_8,D_9,D_{10}),
\]

\[
N=(ac-b^2)(abf+bcd-b^2e-ad^2)
 +(bc-ad)(cd-be)a+(af-be)da^2+(bg-ah)a^2b. \tag{9}
\]

Because a>0 and b<0, N>0 implies k'<0 and C'<0. Direct independent
interval substitutions lose too much cancellation to settle this sign.
Instead use a fixed positive scale a_j and expand each normalized
derivative on the affine predictor as the degree-seven polynomial
P_n(z)=Σ_(p<8) z^p A^pD_n/(p!a_j), with a certified remainder e_n.
Substitute these polynomials into N and multiply them exactly as
polynomials with interval coefficients. Its degree is at most 35.
The constant term plus a symmetric bound Σ_(p≥1)|coefficient_p|h^p
encloses its value for the full driver interval.

The jet remainder changes N by at most Σ|∂N/∂D_n|e_n, evaluated
over enlarged derivative intervals containing both vectors and their
connecting segment. Finally move from the affine predictor to the
actual cusp, |w_i|≤r_ji. The additional error is at most

\[
\sum_{i\in\{t,\lambda,\mu\}} r_{ji}
 \sup\left|\sum_{n=3}^{10}\frac{\partial N}{\partial (D_n/a_j)}
                        \frac{\partial_iD_n}{a_j}\right|. \tag{10}
\]

Here ∂tDn=D_(n+1), ∂λDn=−D_(n+2)/4, ∂μDn=D_(n+4)/16,
so the enclosures through D14 suffice. The derivative box used
in (10) covers the whole segment between predictor and cusp.
N is homogeneous of degree five; scaling all D_n by the same
fixed a_j does not change the quotient (9).

The resulting lower bound for N is strictly positive in all 58 cells.
The endpoint values in (2) are calculated from the exact-root derivative
enclosures in the original Q and S certificates, not from R03 cell
centers or a rounded value of the sextic driver.

## 7. Checks and limits

The separate Fraction checker repeats all contraction, growth, boundary,
and root-witness inequalities. It expands (9) into eleven monomials,
forms its partial derivatives by monomial differentiation, and builds
the A^p coefficients by multinomial enumeration. It independently
reconstructs a positive N bound. Saved oscillatory derivative
enclosures and local Taylor values remain trusted inputs; it does
not provide independent integral certification.

Four regression groups cover 54 correlated derivative comparisons
against finer direct integrals, 18 cusp-centered comparisons, domain
and zero-crossing tests, and exact algebra for (9) and its partial
derivatives. A separate mpmath implementation gives 24 numerical
derivative comparisons and opening/slope checks at three candidate
centers. Those checks support the calculation; they do not certify
quadrature errors or replace the uniform arguments.

R01/R02/R03 are unchanged. R04 supplies a uniform neighborhood theorem,
not a larger absolute t window or a global root classification. Its
common constants are more conservative than the sharper R02 constants
at ν=0; the latter remain valid. No claim is made that the finite width
Wν(ℓ) is monotone for every nonzero ℓ in the entire rectangle, that its
increase is exactly 2.4946 percent there, or that another control
coordinate system must yield the same coefficient.
