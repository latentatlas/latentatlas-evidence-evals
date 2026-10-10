# R25 — An effective fourth-order error bound on a finite budget interval

This is an analytic proof with computer-validated numerical inequalities.
Its inputs are the exact fixed theta cusp Q, exact unrestricted multiplier
b*, sign-moment identities and root enclosures of R12/R15, and the full
coefficient formula and enclosures in R23/R24. All parameter uncertainties
are retained. No exact finite-budget optimizer is computed or presumed.

## 1. Statement

Use the half-line moment problem, original u coordinate and separate
amplitude/Lipschitz constraints of R23. In particular q_j=w p_j,
r_b=p_3−Σ_{j<3}b_jp_j, q*=w r_{b*}, and

\[
\delta(M)=\inf\{\|g\|_\infty:\operatorname{Lip}g\le M,
\ \int q_jg=0\ (j<3),\ \int q_3g=f>0\}.
\tag{E1}
\]

Let δ₀=f/D, D=∫|q*|, and let Γ,G,B,v=G⁻¹B,R,P,Xi be the exact
infinite sums in R23. C₂=δ₀³Γ/(3D) and C₄=δ₀⁵[Γ²/(3D²)−Xi/D]
are the same exact coefficients enclosed by R24. Put

\[
P_4(M)=\delta_0+C_2M^{-2}+C_4M^{-4}.
\]

**Theorem.** For every real budget in the closed interval
2×10⁻⁵≤M≤2×10⁻³,

\[
-\frac{9.593\times10^{-54}}{M^6}
 <\delta(M)-P_4(M)
 <\frac{1.488\times10^{-53}}{M^6}.                 \tag{E2}
\]

These bounds concern exact δ₀,C₂,C₄, not their printed decimal midpoints.
This is a finite-window inequality. It is **not** an O(M⁻⁶) claim as
M→∞, a sixth-order coefficient, or an onset for all M above 2×10⁻⁵.

## 2. Finite transitions and an explicit tail

Set a_min=2⁻²², a_max=2⁻¹⁴, ρ=1/4000. For the 28 exact roots
z_k∈[0,1], write r_k=q*'(z_k), t_k=q*''(z_k), u_k=q*'''(z_k),
σ_k=sign(r_k), Q_k=(q_j(z_k))_{j<3}, and define

\[
\kappa_k=(Q_k^Tv-t_k/6)/r_k,\quad
c_k=z_k+\kappa_k a^2,\quad b(a)=b^*+v a^2.
\tag{E3}
\]

The coefficient path is a trial dual path, not the exact finite-a
minimizer. The original tiny localization cube cannot enclose this path
at a_max. We therefore evaluate a larger cube
b*±(|v_j|a_max²)_j directly. On every interval
N_k=[lower(z_k box)−ρ, upper(z_k box)+ρ], the numerical enclosures prove
σ_k q'_{b(a)}>m_k>0. The endpoint signs and a 354-leaf interval cover
of the complement in [0,1] prove that there is exactly one trial root
in each N_k and no other root in [0,1]. All neighborhoods are disjoint.

Let s_a have the original sign before the first transition, with linear
ramps σ_k(u−c_k)/a in [c_k−a,c_k+a], and the corresponding ±1 constants
between them. Keep the final constant for all u≥1. Hence |s_a|≤1,
||s_a||∞=1 and Lip(s_a)=1/a. This finite-transition profile is an
admissible trial function on the full half-line; the original residual
still has infinitely many zeros. Its difference from sign(q*) after 1
is bounded in the integrals, not declared zero.

For u≥1, R24's weight bound gives
|q_j(u)|≤88·2^j u^j exp(9u+9u⁴−πe^{4u}). The logarithmic derivative
is less than −540: j/u+9+36u³−4πe^{4u}≤48u³−600u³<−540 for j≤3.
Thus

\[
T_j:=\frac{88\,2^j}{540}e^{18-\pi e^4}
 \ge\int_1^\infty |q_j|,\qquad
T_0^{\rm obj}=2\left(T_3+\sum_{j<3}\sup|b_j(a)|T_j\right)
 <5.610\times10^{-67}.                              \tag{E4}
\]

The last notation is an objective-tail bound, not the j=0 moment tail.
The two uses have separate JSON keys. Both the primal tail difference
and an upper estimate for the arbitrary support tail are bounded by
T₀^obj relative to ∫q_b sign(q*).

## 3. Local Taylor estimates with explicit constants

For H_j(t)=∫_t^∞q_j and h=κ_k a²+ay, averaging y uniformly over [−1,1]
gives the exact local moment change

\[
\Delta_{j,k}=-2\sigma_k\,\mathbb E\int_0^h q_j(z_k+x)\,dx.
\tag{E5}
\]

Write K=|κ_k|, Q_{j,l,k}=sup_{N_k}|q_j^(l)|,
R_{l,k}=sup_{N_k}|q*^(l)|. All local constants below are bounds using
the root and neighborhood intervals, not approximate root centers.
Taylor expansion to degree three of H_j gives

\[
\left|\Delta_{j,k}-a^2\left[-2\sigma_k q_j(z_k)\kappa_k
                          -\sigma_k q_j'(z_k)/3\right]\right|
 \le H_{j,k}a^4,
\tag{E6}
\]

where

    H_jk = |q_j'| K² + |q_j''|(K+K³ a_max²)/3
           + Q_j3k (1/5+2K² a_max²+K⁴ a_max⁴)/12.

For q*, its value at z_k is exactly zero. Expanding its primitive
through degree five and bounding the sixth-degree remainder yields

\[
\Delta_{*,k}=-\sigma_k r_k a^2/3
 -\sigma_k(r_k\kappa_k^2+t_k\kappa_k/3+u_k/60)a^4
 +\varepsilon_k,\quad |\varepsilon_k|\le K_{*,k}a^6,
\tag{E7}
\]

with

    K_*k = |t_k|K³/3 + |u_k|(2K²+K⁴ a_max²)/12
       + |q*^(4)(z_k)|(K+(10/3)K³ a_max²+K⁵ a_max⁴)/60
       + R_5k(1/7+3K² a_max²+5K⁴ a_max⁴+K⁶ a_max⁶)/360.

The moments of h through degree six are checked by exact rational
polynomial integration. In particular E h⁵=κa⁶+(10/3)κ³a⁸+κ⁵a¹⁰.
Replacing this odd average by an absolute fifth-power remainder would
lose the needed power. The sixth-power Taylor bound is nonnegative.

Set L_j=Σ_k[−2σ_k q_j κ_k−σ_k q_j'/3]. Over all roots L=B−Gv=0.
The finite sum therefore has magnitude at most
L_tail=|B_tail|+max|G_tail entry| Σ|v_j|, using the R24 whole-tail bounds.
Combining E4 and E6 proves

\[
\left|\int q_j s_a\right|\le H_j a^4,\quad
H_j=\sum_{k\le28}H_{j,k}+L_{\rm tail}/a_{\min}^2
                                  +2T_j/a_{\min}^4.
\tag{E8}
\]

For the finite part of the trial residual, the fourth coefficient is
R_fin+(1/2)vᵀG_fin v−B_finᵀv. This follows by substituting E3 in E7
and subtracting a²vᵀ times E6. The corresponding full coefficient is
Xi=R−P. The absolute error between these fourth coefficients is bounded
by

    Xi_tail = R_tail + (G_tail entry bound)(Σ|v|)²/2
                        + (B_tail entry bound)Σ|v|.

The finite sixth-order error is
K₆^fin=ΣK_*k+Σ_j |v_j|Σ_k H_jk <467724.
No independent rounding of D followed by subtraction of two large
integrals is used; the exact sign-moment identities give the baseline D.

## 4. Upper support bound from almost balanced centers

Let F_k(c)=E q_{b(a)}(c+ay). The quadratic part of F_k(c_k) vanishes
identically: r_kκ_k+t_k/6−Q_kᵀv=0. Taylor's formula gives
|F_k(c_k)|≤h_k a⁴, where

    h_k = |t_k|K²/2 + |u_k|(K+K³ a_max²)/6
          + R_4k(1/5+2K² a_max²+K⁴ a_max⁴)/24
          + Σ_j |v_j|[|q_j'|K+Q_j2k(1/3+K² a_max²)/2].

Since σ_k F'_k≥m_k on the relevant center interval, a unique balanced
center c_bar exists with |c_bar−c_k|≤h_k a⁴/m_k. The entire ramp
at both centers remains in N_k; these containments are verified.

The local objective as a function of c has derivative −2σ_k F_k(c)
and second derivative at most −2m_k. Its increase on moving to the
balanced center is at most F_k(c_k)²/m_k. At a balanced center, the
primitive of q_b from the left ramp endpoint vanishes at both ends
and has sign −σ_k inside. Integration by parts proves that the ramp
maximizes the support integral on that cell. Outside the cells the
profile equals sign(q_b) on [0,1], by the sign cover.

Consequently the support gain beyond the trial finite profile is at most

\[
K_8^{\rm dual}a^8,\qquad K_8^{\rm dual}=\sum_{k\le28}h_k^2/m_k
 <2.565\times10^9.
\tag{E9}
\]

This is a bound valid for every admissible function in the support
supremum. It does not identify the support maximizer on the infinite tail.

## 5. Exact primal moment repair

Move only the first three centers by e_k=a⁴ y_k with
|y_k|≤W_k, W=(2²⁶,2²⁶,2²⁴). Let J_jk=−2σ_k q_j(z_k) and C be
the exact dyadic preconditioner recorded in the certificate. The map
y↦y−C S_lower(c+a⁴y,a)/a⁴ has a uniform weighted contraction bound.
The Jacobian perturbation relative to J is bounded entrywise by

\[
\Delta J_{jk}=2\left[Q_{j,1,k}(K_k a_{\max}^2+W_k a_{\max}^4)
                         +Q_{j,2,k}a_{\max}^2/6\right].
\tag{E10}
\]

E8 bounds the forcing at y=0. In the norm max_k|y_k|/W_k, the three
row contraction bounds are below (0.0014891,0.0020451,0.0024510),
and the forcing bounds below (0.257845,0.351476,0.418263).
Each sum is <1, so the box maps strictly into itself and the contraction
theorem gives a unique repaired vector within this construction. The
same bounds imply invertibility of C, hence the fixed point has all
three lower moments exactly zero. Uniform contraction gives continuity
in a on the closed interval [a_min,a_max]. These are continuous interval
arguments, not numerical samples of a.

The repaired ramps remain in their disjoint N_k. At a trial center the
q_b objective derivative is bounded by 2h_k a⁴, and its second derivative
in absolute value by 2L_k, where L_k=sup_{N_k}|q_b'|. Thus repair costs at
most

\[
K_8^{\rm primal}a^8,\qquad
K_8^{\rm primal}=\sum_{k=1}^3(2h_kW_k+L_kW_k^2)
 <9.383\times10^{14}.
\tag{E11}
\]

Using q_b here is essential: at these almost balanced centers its
objective derivative is order a⁴. The repaired q_b target equals the
repaired q₃ target because the lower moments vanish exactly.

## 6. Quantified support and feasible target

Let H_v(a) be the full half-line support of q_{b(a)} with |s|≤1,
Lip(s)≤1/a, and let S(a)=∫q₃ s_repaired. Put

    K_tail,6 = Gamma_tail/(3 a_min⁴) + Xi_tail/a_min²
               + T₀^obj/a_min⁶ <3.054×10⁻²⁷,
    K_dual = K₆^fin + K₈^dual a_max² + K_tail,6 <467733,
    K_primal = K₆^fin + K₈^primal a_max² + K_tail,6 <3963115.

Every tail term is retained before the final inequality. Then

\[
\begin{split}
H_v(a)&\le D-\Gamma a^2/3+\Xi a^4+K_{\rm dual}a^6,\\
\left|S(a)-(D-\Gamma a^2/3+\Xi a^4)\right|
 &\le K_{\rm primal}a^6.
\end{split}                                                  \tag{E12}
\]

The constants' dependence on a_min is why E12 is not a sixth-order
asymptotic theorem on an interval ending at a=0.

## 7. Covering every budget and inverting the amplitude

The feasible target S is positive. Its loss from D is at most
E_max=Γ_upper a_max²/3+|Xi|_upper a_max⁴+K_primal a_max⁶.
With U=δ₀_upper/(1−E_max/D_lower), the interval computation gives

    E_max <1.611243×10⁻⁹,
    U <9.178748657×10⁻¹⁰ <1,
    U/a_max <2×10⁻⁵,        δ₀_lower/a_min >2×10⁻³.

The feasible amplitude A(a)=f/S(a) lies in [δ₀,U]. Its associated
budget A(a)/a is continuous. The endpoint inequalities and the intermediate
value theorem cover every M in E2; no monotonicity is assumed. The
resulting perturbation h=−A s_repaired preserves kernel positivity because
A≤U<1. At any such M, δ(M)∈[δ₀,U], so a=δ(M)/M also lies in
[a_min,a_max]. Existence of a minimizing function follows from the usual
Arzelà–Ascoli/diagonal and L¹ dominated-convergence argument of R23.

For fixed M let

\[
F_M(A)=D A-\Gamma A^3/(3M^2)+\Xi A^5/M^4.
\tag{E13}
\]

The dual bound gives F_M(δ(M))≥f−K_dual U⁷/M⁶. The feasible construction
gives |F_M(A)−f|≤K_primal U⁷/M⁶. Since Xi>0, F'_M is at least
d_min=D_lower−Γ_upper U²/M_min²>0.0003634068639 on [δ₀,U].
The approximation P₄ also lies in this interval.

Set t=Γ/(3D), e=Xi/D, c=3t²−e, w=(δ₀/M)² and p(w)=1+tw+cw².
Then F_M(P₄)/f−1=p−tw p³+e w² p⁵−1. Its coefficients through degree
two vanish identically; the remaining polynomial has degree twelve.
Bounding the absolute coefficients at w_max=(δ₀_upper/M_min)² gives
|F_M(P₄)−f|≤K_poly/M⁶, with K_poly<3.229371×10⁻⁵⁷.
The inverse derivative bound yields

\[
K_-=(K_{\rm poly}+K_{\rm dual}U^7)/d_{\min}
 <9.593\times10^{-54},\qquad
K_+=(K_{\rm poly}+K_{\rm primal}U^7)/d_{\min}
 <1.488\times10^{-53}.
\tag{E14}
\]

This proves E2. All abbreviated constants above have strict slack;
the certificate uses their full enclosing values, not these abbreviations.

## 8. Consequences and limits

R24 gives C₄>2.49203004×10⁻³⁹. Throughout this finite budget interval,

\[
1-9.624\times10^{-6}(M_{\min}/M)^2
 <\frac{\delta(M)-\delta_0-C_2/M^2}{C_4/M^4}
 <1+1.493\times10^{-5}(M_{\min}/M)^2.               \tag{E15}
\]

In particular δ(M)>δ₀+C₂/M² throughout the interval. At M_min the
error in the fourth-order expression is between −1.49890625×10⁻²⁵
and 2.325×10⁻²⁵. The upper absolute bound is less than 0.001493 percent
of the fourth-order term. These comparisons concern the exact coefficients;
the current uncertainty in a printed δ₀ can be larger than that error.

No cusp-curve uniformity, proof of an all-large-M sixth-order remainder,
exact finite-M optimizer, independent expert approval, formal proof-assistant
verification, physical realization or novelty priority is asserted.

[Numerical evidence](results/TABLE.md), [review](REVIEW.md),
[terminology](CERTIFICATION_TERMINOLOGY_TR.md), [reproduction](README.md).
