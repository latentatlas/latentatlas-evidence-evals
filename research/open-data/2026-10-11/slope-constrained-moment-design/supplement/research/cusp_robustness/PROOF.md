# R07: quantitative persistence under bounded relative kernel errors

20 September 2026. A local computer-assisted result extending the frozen
R01–R05 theorem chain. The arithmetic witnesses have a separate rational
check; external mathematical review and literature priority remain open.

## 1. Kernel class and precise statement

Use the positive Jacobi kernel and normalization of
[R01](../cusp_verified/PROOF.md). For real u≥0 let

\[
\Phi(u)=\sum_{n\ge1}(2\pi^2n^4e^{9u}-3\pi n^2e^{5u})
 e^{-\pi n^2e^{4u}},\qquad \Phi_h(u)=\Phi(u)(1+h(u)),
\]
\[
G_h(t;\lambda,\mu,\nu)=\int_0^\infty\Phi_h(u)
 e^{\lambda u^2+\mu u^4+\nu u^6}\cos(2tu)\,du.
\tag{1}
\]

The perturbation h is **one fixed real measurable function**, independent
of t,λ,μ,ν, with essential supremum norm at most ε₀=10^-18. Extend h and
Φ evenly to the real line. Positivity holds almost everywhere since
1+h≥1−ε₀>0; changes on null sets do not change the integral. Smoothness
or a complex continuation of h is not assumed. Entire dependence of
G_h on the four complex controls follows by dominated differentiation
on compact parameter sets, using the double-exponential decay of Φ.

Write D_n^h=∂t^nG_h. The three parameter identities survive unchanged:

\[
\partial_\lambda D_n^h=-D_{n+2}^h/4,\quad
\partial_\mu D_n^h=D_{n+4}^h/16,\quad
\partial_\nu D_n^h=-D_{n+6}^h/64.\tag{2}
\]

**Theorem.** For every h in this class the following hold.

1. In the 58 specified R03 continuation tubes there is a single glued
   real analytic cusp graph c_h(ν)=(t_h,λ_h,μ_h) for −29≤ν≤0.
   Each graph solves D_0^h=D_1^h=D_2^h=0 and has D_3^h>0>D_4^h.
   Uniqueness is in the specified tubes, not in the whole parameter space.
   Its displacement from the original graph satisfies
   \(\|c_h(\nu)-c(\nu)\|_\infty<4\cdot10^{-5}\).
   Coordinates here are the original numerical t,λ,μ coordinates;
   this is not a dimensionless physical norm.
2. Along this graph, 0.26<μ_h′<0.34. There is exactly one μ_h=0
   crossing in (−29,0), denoted ν_{S,h}; c_h(0) is its quartic-section
   counterpart. Relative to the original sextic crossing,
   |ν_{S,h}−ν_S|<2·10^-4.
3. Center **each perturbed section at its own exact cusp**:
   s=t−t_h(ν), ℓ=λ−λ_h(ν), m=μ−μ_h(ν). In
   |s|≤0.003, |ℓ|≤10^-6, |m|≤2·10^-9 the R04 classification persists:
   exactly the cusp and its two nondegenerate fold arms; three simple
   real roots between the arms and one elsewhere off the discriminant;
   a double and a simple root on either arm; one triple root at the cusp.
   These root counts refer only to this t window. No root crosses its
   two endpoints for any controls in the stated rectangle.
4. For 0<ℓ≤10^-6 the two fold graphs satisfy
   m_low,h<0<m_high,h and
   \(0.98\ell^{3/2}\le W_h(\ell,\nu)\le1.72\ell^{3/2}\),
   where W_h=m_high,h−m_low,h. For a **fixed h**,
   \[
   \partial_\nu m_{\mathrm{high},h}<0,
   \qquad\partial_\nu m_{\mathrm{low},h}>0,
   \qquad
   0.0003\ell^{3/2}<-\partial_\nu W_h<0.003\ell^{3/2}.
   \tag{3}
   \]
   Thus decreasing ν produces strictly nested three-root strips in
   their respective translated, unrescaled (ℓ,m) coordinates.

There is no ordering assertion between strips for two different h's.
The original Q/S percentage increase is not asserted unchanged after
perturbation. The theorem does not assert global real-root counts,
an optimal ε₀, loss of the structure beyond ε₀, or physical stability.

## 2. Absolute moments control arbitrary measurable perturbations

The frozen R03–R05 positive majorants B_n bound
\(\int_0^\infty\Phi(u)e^{\lambda u^2+\mu u^4+\nu u^6}(2u)^n du\)
on a specified larger real parameter domain, for n≤74. Consequently,

\[
|D_n^h-D_n|\le \|h\|_\infty B_n\le\epsilon_0 B_n.\tag{4}
\]

No quadrature of h, no complex analyticity of h, and no finite sampling
of the admissible class are used. In particular, the old holomorphic
integrator is applied only to the original analytic kernel, never to an
arbitrary measurable h. Fixedness of h across the controls is essential
both in (2) and when following a single graph in ν.

## 3. Uniform contraction and gluing

At each R03 driver interval ν=ν_j+z, |z|≤1/4, retain the exact dyadic
predictor a_j(ν)=x_j+v_jz, the three radii R_i=2^-10, and invertible
preconditioner Y. Let q₀,η₀ and r_i^old be the already verified R03
scaled contraction, center residual, and tight root radii.

For J=∂(D_0,D_1,D_2)/∂(t,λ,μ), its three column shifts and absolute
factors are (1,2,4) and (1,1/4,1/16). Define

\[
E=\max_i R_i^{-1}\sum_{n=0}^2|Y_{in}|B_n,
\]
\[
Q=\max_i\sum_{j=0}^2\frac{R_j}{R_i}|f_j|
 \sum_{n=0}^2|Y_{in}|B_{n+\sigma_j}.
\]

For the perturbed cusp map its contraction and residual obey
q_ε≤q₀+ε₀Q and η_ε≤η₀+ε₀E. The computation verifies q_ε+η_ε<1
on all 58 tubes. Banach's theorem gives one root for every driver value.
Comparing its fixed point with the original one also gives

\[
|c_{h,i}(\nu)-c_i(\nu)|
\le R_i\frac{\epsilon_0 E}{1-q_\epsilon},\qquad
r_i^{\rm new}=\min\left\{
 R_i\frac{\eta_\epsilon}{1-q_\epsilon},\;
 r_i^{\rm old}+R_i\frac{\epsilon_0E}{1-q_\epsilon}\right\}.
\tag{5}
\]

At each of the 57 driver seams, the full new root enclosure from one
tube lies strictly inside the neighboring tube's uniqueness box. The
largest computed componentwise containment ratio is below 0.131.
This is root containment plus uniqueness, not geometric overlap alone.
Invertibility of the cusp Jacobian follows from contraction (also its
determinant is (D_3^h)^2D_4^h/64). The analytic implicit-function theorem
and the seam identifications give the claimed analytic graph.

Both implementations verify the derivative signs and
μ_h′=D_6^h/(4D_4^h)∈(0.26,0.34). The root tubes give μ_h(0)>0 and
μ_h(−29)<0. Existence and uniqueness of the sextic crossing follow.
At ν_S, |μ_h(ν_S)|<4·10^-5, so the derivative lower bound gives
|ν_{S,h}−ν_S|<(4·10^-5)/0.26<2·10^-4.

## 4. Enlarged original-kernel Taylor bounds and local geometry

Rebuild the R05 correlated Taylor formula on the new radii in (5).
Use the same fixed original-kernel central D_0,…,D_68 and moment
majorants B_0,…,B_74. Every enlarged tube and all auxiliary local
neighborhoods are verified to remain inside the original majorant
domain. Add (4) to every resulting derivative enclosure.

At the **proved perturbed cusp**, the first three G_h derivatives are
exactly zero. It is then valid to use the cusp-centered Taylor bounds
of R04 with these three exact zero coefficients. The complete local
argument in [R04, Sections 3–5](../cusp_geometry/PROOF.md) applies by (2).
It is rechecked numerically here, including the common implicit fold
box, signs D_3^h>0>D_4^h and Δ=D_3^h D_4^h−D_2^h D_5^h<0, and

\[
1.80s^2\le\ell(s,\nu)\le2.21s^2,\qquad
1.61|s|^3\le|m(s,\nu)|\le2.09|s|^3.
\tag{6}
\]

The sign of m is opposite to that of s. Quadratic/cubic comparison
gives 0.49ℓ^(3/2)≤|m|≤0.86ℓ^(3/2). Both fold exits, both t-boundary
signs, a three-root sign witness and a 32-subinterval one-root witness
are checked on every driver cell. Together with D_3^h>0 and Rolle's
theorem this gives the full root classification, not just existence
of three roots at selected parameter values.

## 5. Opening and finite fold transport

Let k_h=−D_3^h/D_4^h and C_h=(8√2/3)k_h. The polynomial identity
from R04 gives k_h′=N/(64(D_3^h)^2(D_4^h)^3), with N homogeneous of
degree five in D_3^h,…,D_10^h. R05 gives
B_h''''(0)=−2N₄/((D_3^h)^3(D_4^h)^4), where N₄ is homogeneous
of degree seven in D_3^h,…,D_11^h and

\[
B_h(s,\nu)=\frac{4\lambda_h'(\nu)D_2^h+D_6^h/4}{D_4^h}.
\tag{7}
\]

For clarity, evaluating these polynomials on the original F derivatives
at a perturbed cusp is **only an intermediate polynomial evaluation**.
That point need not be a cusp of F. The cusp identities are applied
only after replacing the derivative vector by that of G_h at its own
cusp. The original correlated polynomial enclosure is extended by the
mean-value estimate

\[
|P(d^h)-P(d)|\le\frac{\epsilon_0}{s_0}
 \sum_n B_n\sup_{\mathcal D}|\partial_n P|,
\quad d_n=D_n/s_0,\quad d_n^h=D_n^h/s_0,\tag{8}
\]

where s₀>0 is one fixed scaling constant per tube and the box
\(\mathcal D\) contains both vectors and their connecting segment.
Both nonlinear polynomials are bounded this way; their quotient
denominators use the perturbed derivative bounds. This retains the
essential cancellation in N rather than independently widening its
terms before following the driver.

As in R05, B_h(0)=μ_h′, B_h′(0)=B_h″(0)=0, and
B_h'''(0)=−32k_h′. For |s|≤S=3/4000, compute M₄≥|B_h''''(0)| and
M₅≥sup|B_h'''''(s)| on the uniform fold neighborhood. Then

\[
B_h'''(s)\in-32k_h'+[-e,e],\quad e=M_4S+M_5S^2/2.
\tag{9}
\]

Its lower endpoint is positive on every cell in both implementations.
Integrating three times shows sign(B_h(s)−μ_h′)=sign(s), and
\(\partial_\nu m|_\ell=B_h(s,\nu)-\mu_h'\).
The upper fold has s<0, the lower has s>0; hence the first two signs
in (3). Since 1.80S²>10^-6, (6) covers every ℓ of interest.
Bounds on |s|³ in terms of ℓ^(3/2), applied to both arms, give
the two constants 0.0003 and 0.003 in (3).

## 6. An explicit conditioning witness

Fix a equal to the exact dyadic t center in the R01 quartic certificate,
approximately 41.40034135868425, and set h_ε(u)=ε cos(2au).
For |ε|<1 this defines a positive even kernel, and product-to-sum gives
the exact identity

\[
G_\epsilon(t)=F(t)+\frac\epsilon2[F(t+a)+F(t-a)].\tag{10}
\]

At the exact quartic cusp Q, with ν=0 fixed, put
\(r_n=[D_n(t_*+a;\lambda_*,\mu_*,0)+D_n(t_*-a;\lambda_*,\mu_*,0)]/2\).
The cusp implicit-function theorem applies for ε near zero. Its tangent
(ṫ,λ̇,μ̇)=d c_ε(0)/dε at ε=0 satisfies J(ṫ,λ̇,μ̇)^T=−(r₀,r₁,r₂)^T,
so

\[
\dot\mu=-16r_0/D_4,\qquad
\dot\lambda=(4r_1+D_5\dot\mu/4)/D_3,\qquad
\dot t=(-r_2+D_4\dot\lambda/4-D_6\dot\mu/16)/D_3.\tag{11}
\]

Six new rigorous original-kernel integrals at frequencies 0 and 2a
enclose the r_n. Mean-value bounds over the extremely small R01 root
box transfer exact dyadic center evaluations to the exact cusp.
Both original tail bounds remain included. The verified readable
tangent intervals are

| Coordinate | Lower bound for derivative | Upper bound for derivative |
|---|---:|---:|
| t | −277750000000 | −277730000000 |
| λ | 531550000000 | 531570000000 |
| μ | 492590000000 | 492610000000 |

The μ derivative is approximately 4.926008495177408·10^11. The large
response has an explicit mechanism: near t=a the cosine modulation
mixes the high-frequency integral with its nonoscillatory value near
t−a=0. Dividing this forcing by the small D₄ in (11) produces a large
coordinate response. This is a property of this admissible direction,
not an assertion that every perturbation is damaging. A constant
relative multiplier merely rescales F and moves no zero at all.

These are **derivatives at ε=0**, not validated finite-ε displacements.
They show real coordinate sensitivity but do not prove that 10^-18 is
the optimal robustness radius, explain its exact magnitude, or prove
breakdown at 10^-17. The radius in the theorem is a sufficient bound.

## 7. Verification boundary and diagnostic history

The Arb generator uses 110 decimal digits. The separate checker imports
neither FLINT nor the R07 generator. It reconstructs all new correlated
Taylor bounds by multinomial formulas; the degree-five and degree-seven
polynomials by their 11 and 22 expanded monomials; the fifth transport
derivative by the fold ODE rather than implicit coefficient solving;
and the contraction, root-count and seam inequalities by outward
rational interval arithmetic on a 192-bit dyadic grid. Exact dyadic
input preconditioners are retained as exact fractions for the tight
radius comparisons. It checks all 58 cells and all 57 joins.

Frozen original integral enclosures, positive majorants and R03
contraction/tight-root estimates remain trusted numerical inputs.
They were checked in earlier packages, but this is not a formal proof
assistant or an independent mathematical referee. Three direct
cos-modulated integrals computed separately with mpmath agree with the
shifted-frequency result within 10^-80; this is numerical support.

Three-cell diagnostics passed at 10^-19 and 10^-18. At 10^-17, two
cells failed the fixed readable geometric bounds. This is failure of
these sufficient estimates, not a counterexample. An initial rational
checker attempt introduced extra rounding into an exact radius
comparison; retaining those particular dyadics as exact fractions fixed
the checker. The generating certificate and old results were unchanged.
The details are retained in [DIAGNOSTICS.md](DIAGNOSTICS.md).

## 8. A structured finite-amplitude direction that fixes the exact cusp

Kernel linearity gives a stronger conclusion for specially selected
directions than a first-order sensitivity statement. At the exact
quartic cusp Q define, for j=1,2,3,4 and n=0,…,4,

\[
M_{nj}=\int_0^\infty\Phi(u)e^{\lambda_Qu^2+\mu_Qu^4}
 \cos(2ju)(2u)^n\cos(2t_Qu+n\pi/2)\,du.
\]

Let A be the first three rows of M. Define α_j=(-1)^(j−1)det A_{omit j},
Z=Σ|α_j|, and

\[
w_j=\alpha_j/Z,\qquad h_0(u)=\sum_{j=1}^4w_j\cos(2ju).\tag{12}
\]

These are definitions using **exact integral values at the exact cusp**.
Rounded printed coefficients do not define an exactly pinned cusp.
The alternating-minor identity Aα=0 proves that the first three
moments of h₀ vanish exactly. Therefore for Φ_ε=Φ(1+εh₀), the point Q
satisfies G_ε=D_1G_ε=D_2G_ε=0 for every real ε, with no expansion or
finite-ε remainder needed.

Forty new shifted-frequency integrals at t_Q±j enclose M, using (10)
with a=j and the same center-to-root correction as above. All four
cofactors have nonzero sign, in order (−,+,−,+), so Z>0 and the
direction is nontrivial. The approximate coefficients are

\[
(w_1,w_2,w_3,w_4)\simeq
(-0.6179413550,\;0.2914178602,\;-0.0804226747,\;0.0102181101).
\]

By definition Σ|w_j|=1; in fact h₀(π/2)=1 by these signs, so its
supremum norm is exactly one. Both the generating and the separate
rational computation verify

\[
\left|\sum_j w_j M_{3j}\right|<0.401D_3(Q),\qquad
\left|\sum_j w_j M_{4j}\right|<0.401|D_4(Q)|.\tag{13}
\]

**Pinned-cusp proposition.** For every −1/2≤ε≤1/2 this explicit
nonconstant, smooth, even perturbation leaves Φ_ε positive and leaves
the exact Q a nondegenerate cusp in the ν=0 section. Indeed Φ_ε≥Φ/2,
D_3G_ε(Q)>0 and D_4G_ε(Q)<0, with magnitudes at least 0.7995 times
the original ones by (13). The (λ,μ) unfolding determinant is
D_3G_ε D_4G_ε/64≠0. A local cusp geometry follows, but neither the
entire ν arc nor the previous explicit finite window or width-motion
direction has been validated at these larger amplitudes.

The cofactor identity is also checked as an exact symbolic polynomial
identity by integer monomial cancellation. Five direct h₀-modulated
mpmath integrals agree within 10^-75, with the first three numerically
zero to that tolerance. This supports, but does not replace, exact
annihilation by the definition (12). Coefficients rounded for plotting
or ordinary software lose the exact annihilation and must instead be
treated with error bounds.

This construction uses elementary linearity and a nullspace; no new
general nullspace method is claimed. Its extra family-specific content
is an explicit normalized direction with certified nondegeneracy over
the specified finite amplitude interval. It sharpens the distinction
between a tiny guarantee for arbitrary directions and a much larger
guarantee for one selected direction and one fixed cusp.

All conclusions use the stated h classes, coordinates and windows.
Optimized tolerances, large-amplitude arc geometry, global root counts
and physical models remain separate questions.
