# R29 — Recentered continuation of the fourth coefficient

23 September 2026. This is a computer-assisted result with explicit analytic
arguments and validated numerical hypotheses. It is not a formal proof or
an external referee report. Definitions of the design problem, its coefficient
and the differentiation identities are inherited from
[R23](../infinite_slope_fourth_order/PROOF.md),
[R27](../cusp_uniform_remainder/PROOF.md) and
[R28](../cusp_coefficient_motion/PROOF.md). No frozen prerequisite is edited.

## 1. Statement and normalization

Let Q(ν)=(τ(ν),λ(ν),μ(ν),ν) be the exact R03 cusp graph, with Q(0)=Q.
Use the original half-line coordinate u and original driver ν. Put
w=Φ exp(λu²+μu⁴+νu⁶), p_j=(2u)^j cos(2τu+jπ/2), q_j=wp_j and f=D₃>0,
where D_n=∂_t^nF. The design value is

\[
 \delta_\nu(M)=\inf\{\|g\|_\infty:\operatorname{Lip}g\le M,
       \ \int q_jg=0\ (j<3),\ \int q_3g=f\}.                 \tag{E1}
\]

Each ν has its own admissible g. Let b*(ν) be the unrestricted minimizer
of D_ν(b)=∫|q₃−Σb_jq_j|. For q*=q₃−b*·q, retain the full infinite root
sums Γ,G,B,R and Xi=R−½BᵀG⁻¹B from R27. Define δ₀=f/D and

\[
 C_4(\nu)=\delta_0^5\left(\frac{\Gamma^2}{3D^2}-\frac{\Xi}{D}\right),
 \qquad I=[-1/64,0].                                       \tag{E2}
\]

**Theorem.** On I, b* is uniquely defined and C₄ is C¹, with one-sided
derivatives at the endpoints. Throughout I,

\[
 1.9\times10^{-40}<C_4'(\nu)<5.3\times10^{-40},\qquad
 2.48374879\times10^{-39}<C_4(\nu)<2.49203006\times10^{-39}.
                                                               \tag{E3}
\]

For every ν₁<ν₂ in I the gain lies strictly between the two derivative
bounds times ν₂−ν₁. In particular

\[
 2.96875\times10^{-42}<C_4(0)-C_4(-1/64)
                         <8.28125\times10^{-42}.            \tag{E4}
\]

At each fixed ν the R23 asymptotic interpretation remains valid:
δ_ν(M)=δ₀(ν)+C₂(ν)M⁻²+C₄(ν)M⁻⁴+o(M⁻⁴), with
C₂=δ₀³Γ/(3D). The claim here is pointwise in ν. R27's explicit
O(M⁻⁶) constants and common onset M≥2×10⁻⁵ are **not** extended to I.
I is 1024 times longer than R28's interval; no maximality is asserted.

## 2. New anchors belong to the same exact cusp

Use h=1/4096 and centers ν_i=−(2i+1)h, i=0,…,31. The closed cells
I_i=[−(i+1)/2048,−i/2048] have no gaps and cover I exactly.
At each center, Newton iteration only proposes a dyadic x_i. Fresh Arb
quadrature encloses D₀,…,D₃₉ at (x_i,ν_i); the full theta-series and
infinite-domain errors are included by the R01/R03 integral routine.

The trial cube has radius r=2⁻¹⁶⁰. With an exact dyadic approximate
Jacobian inverse C, the computation bounds q=||I−CJ||∞ and
η=||CF||∞/r on that cube and checks q+η<1 and det C≠0. Banach's
theorem gives a unique zero and radius

\[
 r_*\le \frac{r\eta}{1-q}.                                 \tag{E5}
\]

The whole trial cube lies strictly inside the R03 uniqueness tube at ν_i.
Therefore the zero is Q(ν_i). Mere overlap of numerical boxes is not used
to identify branches. R03 already identifies the analytic graph on
[−1/2,0] with Q. Subsequent arc enclosures integrate its known velocity.

For the Taylor operator L=ΔτD_t−ΔλD_t²/4+ΔμD_t⁴/16−ΔνD_t⁶/64,
use the degree-five expansion with sixth-degree positive-moment remainder.
R09 supplies B_n through order 58. Although its original parameter box
was small, these positive moments also dominate every smaller λ and μ
and every ν≤0, pointwise in u. R03 proves λ'>0 and μ'>0 on its first
cell. Thus actual cusp points in I satisfy λ(ν)≤λ(0), μ(ν)≤μ(0).
The anchor trial cubes are checked below R09's upper controls too.
Every actual straight Taylor segment is dominated. We do not assert
that every artificial corner of a dependency-widened box is a cusp.

Starting with R03 velocities, enclose the derivatives, then use

\[
 \mu'=D_6/(4D_4),\quad
 \lambda'=(4D_5\mu'-D_7)/(16D_3),\quad
 \tau'=(D_8/64+D_4\lambda'/4-D_6\mu'/16)/D_3.                \tag{E6}
\]

Integrating each newly valid velocity box from the exact anchor and
repeating gives the recorded local boxes. In every cell D₃>0, D₄<0,
D₆<0, all three velocity magnitudes are <1, 41<τ<42, −4<λ<0, 0<μ<9.

## 3. Local sign moments and better residual transport

At each dyadic cusp center, a dual Newton iteration proposes b⁰ and
28 dyadic root knots. These are candidates, not exact optimizers or zeros.
For each j=0,…,9 integrate q_j over the 29 fixed sign-template intervals
in [0,1]. The integrand is an entire finite theta sum, so its complex
quadrature callback has no branch-cut ambiguity. Add the omitted theta
series, the domain tail, and the exact-cusp displacement from E5.
Actual returned ball radii are retained; requested tolerances are not
substituted for proven errors. This usage follows the
[FLINT integration contract](https://flintlib.org/doc/acb_calc.html) and
[python-flint callback contract](https://python-flint.readthedocs.io/en/latest/acb.html#flint.acb.integral).

For current parameters and a coefficient box, each root is bracketed
and contracted. The complement in [0,1] has a complete signed interval
cover. To move a template moment to the current sign moment, add

\[
 E_j+2\sum_{k\le28}|J_k|\sup_{J_k}|q_j|
       +2\int_1^\infty|q_j|,\quad
 E_j=d_\tau B_{j+1}+d_\lambda B_{j+2}/4
                  +d_\mu B_{j+4}/16+d_\nu B_{j+6}/64.       \tag{E7}
\]

J_k contains the template knot and every enclosed current root.
Recursive sign-cover split endpoints may themselves have nonzero Arb radii.
For endpoint balls l,r, the evaluated ball (l+r)/2±upper((r−l)/2)
contains [lower(l),upper(r)]. The audit uses these outer intervals and
checks overlap of consecutive leaves and root brackets all the way from
0 to 1; it does not incorrectly require every stored split to be exact.
The last term covers all possible tail sign disagreements. Anchor
uncertainty is conservatively counted twice in one displacement bound;
this does not remove any error contribution.

The key recentering improvement concerns the **preconditioned** residual.
For fixed b⁰ let S_j(ν,b⁰)=∫sign(q_b⁰)q_j. With
T_j=τ'S_{j+1}−λ'S_{j+2}/4+μ'S_{j+4}/16−S_{j+6}/64,
R28's moving-boundary calculation gives

\[
 \partial_\nu S_j=T_j+2\sum_k q_j(z_k)h_k/\gamma_k,
 \quad h_k=w(z_k)\tau'(p_4-\textstyle\sum b_i^0p_{i+1})(z_k).
                                                               \tag{E8}
\]

The tail of E8 is bounded independently of b'. At the exact anchor,
S(ν_i,b⁰) is enclosed by the fresh integrals and root errors. For a
constant dyadic preconditioner C, integration along the already known cusp
therefore bounds the fixed-point forcing componentwise by

\[
 |CS(\nu,b^0)|_i\le |CS(\nu_i,b^0)|_i
                 +h\sup_{\nu\in I_i}|C\partial_\nu S|_i.
                                                               \tag{E9}
\]

Linear combinations are taken before absolute values. This retains
cancellation lost by transporting separate absolute moments from Q(0).
It is an inequality along the known cusp, not an assumption about b*.

## 4. Uniform dual existence and identification across cells

Take radii R_i at least four times the right side of E9. On the whole
box b⁰+diag(R)[−1,1]³, bound G=Hess D by all finite root contributions
and the complete infinite tail. For T(b)=b+C S(b)=b−C∇D(b), check

\[
 q_i=\sum_j|(I-CG)_{ij}|R_j/R_i,\quad
 \eta_i=\sup|CS(b^0)|_i/R_i,\quad q_i+\eta_i<1.             \tag{E10}
\]

With det C≠0, the fixed point has zero lower sign moments. The positive
Gram principal minors give strict local convexity. Global convexity of
D then makes it the unique global minimizer: a second minimizer would
force constancy on the joining segment, contradicting local strict
convexity. A posteriori radii R_i η_max/(1−q_max) tighten the localization.
All roots and jets are reevaluated in the tighter box.

At a shared driver, neighboring cells refer to the same cusp by Section 2.
Their dual solutions coincide by uniqueness of the global minimizer.
This proves that the cells form a single b*(ν), without relying on box
overlap. Overlap of neighboring dual boxes is only an additional recorded
consistency check. Simple roots and invertible G give local C¹ dependence;
the global uniqueness identifies these local functions on the overlaps.

## 5. The objective, coefficient, and its derivative

At ν_i, the objective at b⁰ is S₃−b⁰·S_{<3}. If d=b*(ν_i)−b⁰, Taylor's
formula for the convex objective bounds the difference from its minimum by

\[
 e_i\le\sum_j|S_j(\nu_i,b^0)|\,|d_j|
                      +\tfrac12\sum_{jk}\sup|G_{jk}|\,|d_jd_k|.
                                                               \tag{E11}
\]

The same box contains the whole joining segment. The uniform dual has
already been established; consequently its envelope derivative is
D'=T₃−Σb*_j T_j. Transport E7 first bounds this derivative without using
the yet-to-be-tightened D interval. Integration yields
D(ν)∈D_{ν_i}(b⁰)±(e_i+h sup|D'|). There is no circular existence or
objective bound.

Compute Γ,G,B,R from all 28 roots, retaining their full sextic weight
jets, and add R24's tail bounds justified below. The solve Gv=B is
validated with a dyadic seed v₀ and Neumann residual bound, then Xi and
C₄ are evaluated. For differentiation use R28 identities V5–V11:
solve Gb'=A, calculate each moving-root velocity, differentiate the
root sums, and use P'=B'ᵀv−½vᵀG'v. The complete derivative tails are
included. The resulting bounds imply E3 in all 32 closed cells.
An outward 512-bit rational checker differentiates the coefficient
formulas by forward automatic differentiation, separately from the
producer's explicit quotient formulas, and verifies the same band.

Finally integrate E3 from ν to 0 and use R24's exact endpoint bound
2.49203004×10⁻³⁹<C₄(0)<2.49203006×10⁻³⁹. This proves the sharper
common coefficient band and E4; loose raw interval coefficient bands
need not themselves fit that sharper anchored band.

## 6. Why the infinite tails and asymptotic meaning persist

For H=1/64, ν∈[−H,0] and u≥1, the upper density envelope remains
w≤88 exp(9u+9u⁴−πe^{4u}). The potential derivatives obey

    |P'|≤44u³+6Hu⁵,       |P''|≤116u²+30Hu⁴,
    |P'''|≤216u+120Hu³,   |P''''|≤216+360Hu²,
    |P'''''|≤720Hu.

Using u⁵e⁻⁴ᵘ<1/40 and e⁴ᵘ>50u³, exact rational checks give
|P^(j)|<e^{4ju}, j=1,…,5. Thus the same R26 weight constants and
R24/R28 coefficient and derivative tail estimates apply. Every actual
dual box satisfies |b|<(.001,.1,.005). The R23/R26 phase bounds give
root separation >3/85 and |r_b'(z)|>567z³ beyond 1. The computed
Gb'=A enclosure verifies |b'_j|<10 before using this in subsequent
derivative tail bounds. As in R28, |z'| may grow like z; no common
absolute displacement of infinitely many roots is assumed. All
differentiated series have uniform summable majorants on I.

For the R23 asymptotic theorem at a fixed ν, finitely many simple roots
and the tail phase bounds give a sufficiently small common neighborhood
radius ρ≤1/1000 and a coefficient neighborhood. The first three switch
evaluation columns have nonzero determinant, checked freshly in every
cell. For tail root neighborhoods one may use finite constants C with

    E_k≤C(1+z_k+ρ)^18
        exp(21(z_k+ρ)+9(z_k+ρ)^4−π exp(4(z_k−ρ))),
    L_k=exp(−4(z_k+ρ)^2−H(z_k+ρ)^6−π exp(4(z_k+ρ))).

The degree 18 allows the sextic potential's third exponential derivative
and the cubic moment factor. The phase coercivity proof from R23 is
unchanged, since the residual phase does not involve λ, μ or ν.
For the crucial weighted summability, E_k³/L_k² is bounded by a constant
times a degree-54 factor and

\[
 \exp\{63(z+\rho)+27(z+\rho)^4+8(z+\rho)^2
       +2H(z+\rho)^6-\pi c_\rho e^{4z}\},\quad
 c_\rho=3e^{-4\rho}-2e^{4\rho}>97/100.                    \tag{E12}
\]

The negative exponential-of-z term dominates all positive polynomial
terms as z→∞. Together with the uniform separation, this proves
ΣE_k(1+E_k/(6L_k))²<∞. Finitely many remaining neighborhoods contribute
finite amounts. R23 therefore supplies the pointwise coefficient
interpretation in Section 1. This existence proof does not calculate
a new finite-M onset or uniform numerical remainder.

## 7. Limits and falsifiable checks

The coarse attempt on [−1/512,0] encloses C₄' in an interval containing
zero; it is inconclusive, not negative evidence. The first four smaller
cells cover exactly that same interval and all prove positive derivative.
This isolates an interval-overestimation obstruction in that attempt.
It does not identify a mathematical endpoint of continuation.

The full R03 curve [−29,0], C₄ convexity, a sixth coefficient, monotonicity
of δ_ν(M) at fixed finite M, and a shared optimal perturbation across ν
are not claimed. The new contribution is a larger quantified continuation
and its reproducible localization method. Literature priority, external
review and publication acceptance remain separate questions.

[Review](REVIEW.md), [numbers](results/TABLE.md),
[reproduction](README.md), [Turkish findings](BULGU_NOTU_TR.md).
