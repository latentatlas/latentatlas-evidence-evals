# R23 — Fourth-order optimal value with countably many switches

This is an analytic extension of R22. The hypotheses below are sufficient,
not claimed necessary. They are stronger in regularity than R22. We prove
the optimal **value** expansion, not existence of a differentiable infinite
vector of optimal centers or uniqueness of the finite-budget optimizer.
All parameters of the underlying integral problem are fixed.

## 1. Problem and weighted hypotheses

Let q_0,...,q_m be real L¹ densities on [0,∞), locally C³. Let f>0 and

\[
\delta(M)=\inf\{\|g\|_\infty:\operatorname{Lip}(g)\le M,
\ \int q_jg=0\ (j<m),\ \int q_mg=f\}.                 \tag{W1}
\]

For b near b*, set q_b=q_m−Σ_{j<m}b_jq_j and q*=q_{b*}.
Assume ∫q_j sign(q*)=0 for j<m. Write D=∫|q*|>0 and δ₀=f/D.
Assume q*(0)≠0. Its positive zeros z_k, in increasing order, are
simple, tend to infinity, and have a positive minimum separation.

There is a radius ρ>0 and a bounded open neighborhood U of b* such that:

1. N_k=[z_k−ρ,z_k+ρ] lie in (0,∞) and are pairwise disjoint.
   Each q_b has exactly one simple zero z_k(b) in each N_k, no other
   zeros, and the same crossing orientation σ_k as q*. The functions
   z_k(b) are C¹ and uniformly Lipschitz in b, with a common constant C.
   Shrink U so |z_k(b)−z_k|<ρ/4 for every k and b∈U.
2. There are numbers L_k>0 with

\[
 |q_b(x)|\ge L_k|x-z_k(b)|\quad(x\in N_k,\ b\in U).
                                                               \tag{W2}
\]

3. Put E_k=Σ_{j=0}^m Σ_{ℓ=0}³ sup_{N_k}|q_j^{(ℓ)}|.
   Choose a finite constant C_U≥1 with |q_b^{(ℓ)}|≤C_U E_k on N_k,
   for b∈U and ℓ≤3. Define K_k=C_U E_k/(6L_k). The weighted condition is

\[
             \sum_k E_k(1+K_k)^2<\infty.                       \tag{W3}
\]

4. Some m switch evaluation vectors (q_j(z_k))_{j<m} are independent.
   When m=0 this condition is empty.

Condition W2 is a coercive crossing condition, not monotonicity of q_b
on the whole neighborhood. For q_b=w r_b with w>0 it follows from a
uniform lower bound for |r_b'| of fixed sign and a lower bound for w.
In particular, W3 allows K_k to be unbounded.

## 2. Coefficients and theorem

Use Q_k=(q_j(z_k))_{j<m}, r_k=q*'(z_k), t_k=q*''(z_k),
u_k=q*'''(z_k), γ_k=|r_k|, σ_k=sign(r_k). Define

\[
\begin{split}
\Gamma&=\sum_k\gamma_k,&
G&=2\sum_k Q_kQ_k^T/\gamma_k,\\
B_j&=\frac13\sum_k\sigma_k
     \left(q_j(z_k)t_k/r_k-q_j'(z_k)\right),&v&=G^{-1}B,\\
\mathcal R&=\sum_k\left(t_k^2/(36\gamma_k)-\sigma_ku_k/60\right),&
\mathcal P&=\tfrac12 B^TG^{-1}B,\qquad\Xi=\mathcal R-\mathcal P.
\end{split}                                                     \tag{W4}
\]

All series converge absolutely and G is positive definite. Indeed
γ_k≥L_k, |t_k|,γ_k,|u_k|≤C_U E_k. Implicit differentiation at b*
gives ∂_{b_j}z_k=q_j(z_k)/r_k; uniform root motion bounds these ratios.
It follows that entries of G and B are bounded by constant multiples
of E_k, and t_k²/γ_k≤6E_k K_k after increasing fixed constants.
The rank assumption makes the Gram form strictly positive.

**Theorem.** Under W1–W3 and the rank hypothesis,

\[
\delta(M)=\delta_0+\frac{C_2}{M^2}+\frac{C_4}{M^4}+o(M^{-4}),\quad
C_2=\frac{\delta_0^3\Gamma}{3D},\quad
C_4=\delta_0^5\left(\frac{\Gamma^2}{3D^2}-\frac{\Xi}{D}\right).
                                                               \tag{W5}
\]

Consequently M³[δ(M)−δ₀−C₂/M²]→0. This is not a computable uniform
error bound, and does not assert that all odd powers at higher orders
vanish. The moment penalty P≥0 remains invariant under an invertible
change of lower-moment basis, by the same Gram identity as R22.

## 3. Balanced cells exist without uniformly bounded center coefficients

For b∈U and 0<a<ρ/4, consider the equation

\[
 \frac12\int_{-1}^1q_b(c+ay)\,dy=0.                            \tag{W6}
\]

At c=z_k(b)−a and c=z_k(b)+a the integrals have opposite strict
signs. For c between them, q_b(c−a) and q_b(c+a) have opposite
signs and
∂_c∫_{c−a}^{c+a}q_b=q_b(c+a)−q_b(c−a) has sign σ_k.
Thus there is a unique balanced center c_k(b,a) in this interval.
The cells lie inside N_k, are disjoint, and straddle the respective root.
Their centers are continuous in (b,a) for a>0 by the ordinary scalar IFT.

Taylor's formula about c, symmetric averaging, and W2 imply

\[
 |c_k(b,a)-z_k(b)|\le\min\{a,K_ka^2\}.                       \tag{W7}
\]

In fact the averaged remainder is at most C_U E_k a²/6, and the
absolute value of q_b(c) is at least L_k|c−z_k(b)|. No lower bound
for q_b' throughout the cell was used.

Set b(a)=b*+v a². This is an explicit trial dual path; it is not asserted
to be the exact finite-a dual minimizer. For every fixed k, ordinary local
Taylor expansion of W6 gives, with Δ_k=c_k(b(a),a)−z_k,

\[
 \frac{\Delta_k}{a^2}\longrightarrow
 \kappa_k=\frac{Q_k^Tv-t_k/6}{r_k},\qquad
 |\Delta_k|\le a+Ca^2|v|,\quad
 |\Delta_k|/a^2\le K_k+C|v|.                                  \tag{W8}
\]

This is pointwise convergence in k with a summable weighted bound.
It is not convergence in the unweighted supremum norm of center vectors.

## 4. Exact support of the trial residual

Let s_a be sign(q_{b(a)}) outside the balanced cells and
σ_k(x−c_k)/a inside cell k. It is continuous, |s_a|≤1, and
Lip(s_a)≤1/a. On cell [c−a,c+a], put P(x)=∫_{c−a}^x q_{b(a)}.
Balance gives P=0 at both endpoints and σ_k P<0 in its interior.
Every absolutely continuous |s|≤1 with |s'|≤1/a satisfies

\[
 \int_{c-a}^{c+a}q_{b(a)}(s-s_a)
       =-\int_{c-a}^{c+a}P(x)(s'(x)-\sigma_k/a)\,dx\le0.
                                                               \tag{W9}
\]

The same inequality follows pointwise outside the cells. Summing is
legitimate: |q_b(s−s_a)|≤2|q_b|∈L¹. Consequently

\[
 H_v(a):=\sup_{|s|\le1,\ \operatorname{Lip}(s)\le1/a}\int q_{b(a)}s
                     =\int q_{b(a)}s_a.                        \tag{W10}
\]

This support maximizer need not satisfy the lower moments exactly.
The distinction is essential for the later upper bound.

## 5. Termwise expansions justified by weighted domination

For H_j(t)=∫_t^∞q_j, the difference of the smoothed and original signed
moments is the sum of local differences

\[
 \int q_j(s_a-\operatorname{sign}q^*)
 =\sum_k2\sigma_k\left[\frac12\int_{-1}^1
 H_j(z_k+\Delta_k+ay)\,dy-H_j(z_k)\right].                      \tag{W11}
\]

Only these **differences** are summed. No absolute convergence of the
individual infinite tail-primitive series is assumed. Their supports
lie in the disjoint N_k and the sum is absolutely integrable.

For lower moments, expand H_j to degree two. The average of
(Δ+ay)² is Δ²+a²/3. W8, ΣE_k(1+K_k)²<∞, and dominated convergence
give

\[
 \int q_js_a
 =a^2\left[-2\sum_k\sigma_kq_j(z_k)\kappa_k
                     -\frac13\sum_k\sigma_kq_j'(z_k)\right]+o(a^2)
 =a^2(B-Gv)_j+o(a^2)=o(a^2).                                 \tag{W12}
\]

For clarity, the terms q_j'Δ²/a² are dominated by a fixed multiple
of E_k(1+K_k)² and tend to zero individually; the third-order Taylor
bound after division by a² is ≤constant·aE_k for all small a, since
|Δ_k|≤2a. These bounds cover the entire infinite sum.

For q*, H*'(z_k)=−q*(z_k)=0. The degree-four Taylor expansion gives

\[
 \int q^*s_a
 =D-\frac{\Gamma}{3}a^2
   -a^4\sum_k\sigma_k
       (r_k\kappa_k^2+t_k\kappa_k/3+u_k/60)+o(a^4)
 =D-\frac{\Gamma}{3}a^2+
       (\mathcal R-\tfrac12v^TGv)a^4+o(a^4).                  \tag{W13}
\]

Here the averages of h²,h³,h⁴, for h=Δ+ay, are respectively
Δ²+a²/3, Δ³+Δa², Δ⁴+2Δ²a²+a⁴/5. After subtracting the quadratic
term, the normalized r_kΔ², t_kΔa² and t_kΔ³ contributions are
dominated by constants times E_k(1+K_k)². The remaining quartic
terms and Taylor remainders are dominated by constants times E_k.
Continuity of q*''' gives a pointwise little-o remainder at each root.
Dominated convergence turns its sum into o(a⁴); no common unweighted
Taylor radius for the center coefficient is needed.

The last equality in W13 is the completed-square identity of R22,
now applied to absolutely convergent sums. Since b(a)−b*=v a² and
W12 holds, W10 yields

\[
             H_v(a)=D-\Gamma a^2/3+\Xi a^4+o(a^4).             \tag{W14}
\]

For a general fixed vector v the fourth coefficient of H_v is
R+(1/2)vᵀGv−Bᵀv. Its minimum over v is R−P, attained at G⁻¹B.
This is a finite-dimensional quadratic minimization of a coefficient,
not an assertion that b*+v a² is the exact optimizer at positive a.

## 6. Feasible primal profiles with the matching fourth coefficient

Choose the m independent switch columns in hypothesis 4. Move only
their centers by a vector e while preserving widths a. The derivative
of lower moments with respect to e tends, as a→0, to the invertible
matrix whose selected columns are −2σ_k Q_k.

W12 says the forcing at e=0 is o(a²). There is therefore a continuous
choice e(a)=o(a²) which makes all lower moments exactly zero. A
continuous-parameter implicit argument suffices: multiply the moment
equations by the inverse limiting matrix; on a fixed small e-ball,
the resulting fixed-point derivative has norm below 1/2 for small a.
The center correction is bounded by twice that inverse norm times
the forcing. Continuity follows from the contraction estimate.
No differentiability of the whole infinite-center map in a is invoked.

At each of these finitely many centers, the derivative of the q* target
is −σ_k∫_{−1}¹q*(c_k+ay)dy=O(a²). The correction therefore changes
the target by O(a²|e|+|e|²)=o(a⁴). Disjointness and positive distance
from 0 persist. Denote the repaired profile by ŝ_a. Then

\[
 \int q_j\widehat s_a=0\ (j<m),\qquad
 S(a):=\int q_m\widehat s_a=\int q^*\widehat s_a
       =D-\Gamma a^2/3+\Xi a^4+o(a^4).                        \tag{W15}
\]

Both S(a) and A(a)=f/S(a) are continuous for small a>0, with
S→D>0, A→δ₀. The profile g_a=A(a)ŝ_a is feasible at M(a)=A(a)/a.
Continuity and M(a)→∞ show that every sufficiently large M is
attained, by the intermediate value theorem. Strict monotonicity of
this repaired path is unnecessary and is not claimed.

## 7. Matching lower bound and amplitude inversion

For any feasible g with amplitude A, the zero lower moments give
f=∫q_{b(a)}g, with a=A/M. Thus, whenever a is small,

\[
                          f\le A H_v(A/M).                    \tag{W16}
\]

Existence of a minimum can also be used here: at a fixed feasible M,
a minimizing sequence with bounded amplitude has a locally uniformly
convergent subsequence by Arzelà–Ascoli and a diagonal argument.
The limit has the same Lipschitz bound and all moments by L¹ dominated
convergence; its norm is at most the liminf. The upper construction
and the elementary bound A≥δ₀ show δ(M)→δ₀.

Put t=Γ/(3D), e=Ξ/D. In both matching bounds, the formal equality is
A/δ₀=1+t a²+(t²−e)a⁴+o(a⁴), a=A/M. Substitution yields

\[
 C_2=\delta_0^3t,\qquad C_4=\delta_0^5(3t^2-e).              \tag{W17}
\]

For the lower inequality, the polynomial
D A−(Γ/3)A³/M²+ΞA⁵/M⁴ has positive derivative near δ₀ for large M.
W16 and its uniform little-o term for A in a fixed compact neighborhood
of δ₀ bound A below by its root up to o(M⁻⁴). W15 gives the identical
expansion from above. This proves W5 without a finite-M dual IFT.

## 8. Scope

The tails are retained throughout. This theorem supplies a convergent
infinite-series coefficient for a fixed admissible family and an
asymptotically matching feasible construction. It does not supply a
numerical value or sign of theta C₄, an effective onset M₀, an explicit
fourth-order error bound, uniformity along a cusp curve, an exact
finite-M formula, external validation, or a literature-priority claim.

[Theta application](THETA.md), [infinite-switch control example](EXAMPLE.md),
[claim review](REVIEW.md), [reproduction](README.md).
