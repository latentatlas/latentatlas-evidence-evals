# R14 — A narrow amplitude bracket at a fixed slope budget

21 September 2026. This package narrows the R13 problem at the **single**
budget M=0.00002. It does not change Q, the norm, the four target moments,
the allowed support, or the kernel normalization. Analytic arguments are
research proof drafts, not formal verification or external expert review.

## 1. Statement and scope

Use the original exact R01 cusp Q=(τ,λQ,μQ,0), the positive measure
dρ=Φ(u)exp(λQ u²+μQ u⁴)du, and

\[
p_j(u)=(2u)^j\cos(2\tau u+j\pi/2),\quad
f_j=\int_0^\infty p_j\,d\rho,\quad L_j(h)=\int_0^\infty p_jh\,d\rho.
\]

R01/R09 give f0=f1=f2=0 and f3>0. Let δ(M) be the infimum of ∥h∥∞
over real bounded Lipschitz h on [0,∞) satisfying

\[
\operatorname{Lip}_u(h)\le M,\qquad
L_0(h)=L_1(h)=L_2(h)=0,\quad L_3(h)=-f_3.
\tag{1}
\]

**Certified bound.** At M=0.00002,

\[
\boxed{0.000000000917873080<\delta(0.00002)
                  <0.000000000917876530.}
\tag{2}
\]

The displayed relative bracket width is less than 3.76×10⁻⁶. The upper
bound is supplied by a fixed even real-analytic h with positive Φ(1+h),
exactly order four at Q, and rank-three controls. Consequently (2) also
brackets the infimum in this smaller geometric class, without relying on
R13's general equality-of-infima result.

Combining (2) with the unchanged R12 bracket for the unrestricted δ* gives

\[
2.48\times10^{-6}<\frac{\delta(0.00002)}{\delta_*}-1
                    <6.25\times10^{-6}.
\tag{3}
\]

The fractions in (3) are relative increases of the **minimum amplitude**,
not absolute amplitudes, measurement error rates or physical tolerances.
We do not identify an exact optimizer, prove its uniqueness, evaluate
the full δ(M) curve, or transfer R10's finite root window to this kernel.

## 2. Summing 28 disjoint lower-bound losses

Keep the exact R12 residual r=p3−Σ(i=0..2) a_i p_i and its certified
28 simple sign-changing zeros z_k in [b_k−β,b_k+β], β=2⁻³⁶. In this
section b_k are the **unchanged old knots**, not the adjusted primal
knots below. Let a=2⁻¹⁴. The enlarged neighborhoods
[b_k−β−a,b_k+β+a] are positive and pairwise disjoint.

On each such neighborhood, interval evaluation gives

\[
\frac{d\rho}{du}\ge w_k>0,\quad |r'|\ge m_k>0,\quad c_k=w_km_k.
\]

The density bound uses the positive first theta summand

\[
\pi e^{5u}(2\pi e^{4u}-3)
    e^{-\pi e^{4u}+\lambda_Q u^2+\mu_Q u^4}.
\]

For any feasible h, write δ=∥h∥∞. Since ∫rh dρ=−f3,

\[
\delta\int|r|\,d\rho-f_3
=\int|r|\{\delta+\operatorname{sgn}(r)h\}\,d\rho.
\tag{4}
\]

The integrand is nonnegative. Pairing z_k−v and z_k+v, the two defects
have sum at least 2δ−2Mv. Their respective |r|ρ weights are at least
c_k v. Thus for 0<ℓ≤a and Mℓ≤δ, the kth pair neighborhood contributes
at least c_k(δℓ²−2Mℓ³/3). Disjointness is essential for summing these
inequalities without double counting.

Take the old universal lower bound L=0.00000000091787079603827 and
ℓ=L/M<a. Substitution of δ≥L gives the total loss

\[
P=\frac{L^3}{3M^2}\sum_{k=1}^{28}c_k>0,
\qquad \delta(M)\ge\frac{f_3+P}{B_D},
\tag{5}
\]

where B_D is the unchanged R12 upper bound for ∫|r|dρ. The independent
rational reconstruction obtains Σc_k>1.288569607526844904805296574359
and (f3+P)/B_D>0.000000000917873080978808354103.
No exact dual minimizer or enumeration of residual zeros beyond 1 is
assumed. These 28 zeros belong to the auxiliary residual, not to F.

## 3. A wider analytic smoothing with three adjusted knots

Let the old even step template be s_old. It starts at +1 and has positive
knots b_k with jumps d_k=−2(−1)^k for zero-based k=0,…,27. Choose new
positive knots c_k: c_k=b_k for k≥3; the first three are the exact binary
rationals recorded in `diagnostics/candidate_probe.json`. Their approximate
values are 0.0032703202992944284, 0.038318389081010644 and
0.07627939240616548. Floating-point optimization only selects these
constants; its convergence or residual tolerance is not used as proof.

Let s_c be the resulting even step function and choose exactly

\[
\eta=49500\,2^{-30},\quad
k_\eta(v)=\frac{\operatorname{sech}^2(v/\eta)}{2\eta},\quad
s_\eta=k_\eta*s_c.
\]

This nonnegative unit-mass convolution gives ∥sη∥∞≤1. Equivalently,
with Hη(v)=(1+tanh(v/η))/2,

\[
s_\eta(u)=1+\sum_{k=0}^{27}d_k
             \{H_\eta(u-c_k)+H_\eta(-u-c_k)\}.
\tag{6}
\]

It is even and real analytic. Choose the exact positive binary rational
α recorded in the probe; α≈9.17876525682397×10⁻¹⁰. With the same
certified R11 moment matrix A for J={40,41,42,43}, define w **exactly** by

\[
A w=(0,0,0,-f_3)^T+\alpha
       (L_0(s_\eta),L_1(s_\eta),L_2(s_\eta),L_3(s_\eta))^T,
\quad h=-\alpha s_\eta+\sum_{j\in J}w_j\cos(2ju).
\tag{7}
\]

Nonsingularity of A guarantees the exact moment equations (1).
Every coefficient and knot is fixed independently of moving controls.

## 4. Rigorous evaluation of the new smooth moments

Write q_n(u)=(dρ/du)p_n(u) for u≥0 and extend q_n evenly to R. Denote
the old certified signed moments by S_old,n. Moving the first three
step positions changes a moment by

\[
S_{c,n}=S_{\mathrm{old},n}
               -\sum_{k=0}^{2}d_k\int_{b_k}^{c_k}q_n(u)\,du,
\tag{8}
\]

where integrals are oriented. For Eη=Hη−H, oddness gives the exact
smoothing identity

\[
S_{\eta,n}-S_{c,n}
=-\sum_{k=0}^{27}d_k\eta\int_0^\infty
 \frac{q_n(c_k+\eta v)-q_n(c_k-\eta v)}{1+e^{2v}}\,dv.
\tag{9}
\]

The even extension is used in (9) when an argument is negative. For the
computed part 0≤v≤V=32, all arguments are positive. The 28 integration
neighborhoods are disjoint and lie in [0,1]. The producer computes 27
oriented integrals in (8) and 252 rescaled integrals in (9), for n=0,…,8,
using Arb at 110 decimal digits and eight theta terms. **Every new
integral uses the full exact-Q enclosure as its parameter input**, not
only an approximate Q center.

For the infinite tail, the old global Lipschitz constants M_n of the
even q_n give |q_n(c+ηv)−q_n(c−ηv)|≤2M_nηv. Since |d_k|=2,

\[
|\text{smoothing tail}|\le
2\cdot28 M_n\eta^2(V+1/2)e^{-2V}.
\tag{10}
\]

This bound includes the part where c−ηv<0 and every contribution past
the last knot. There is no extra unaccounted domain truncation.

Let T_n be the integrated theta-series remainder bound on [0,1].
The difference of two step functions has magnitude at most two.
The truncated smoothing discrepancy has magnitude at most one, because
its supports are disjoint and 2|Eη|≤1. Thus 3T_n bounds the combined
finite-series error in (8)–(9). The old moments already contain their
own infinite-domain, series and exact-Q errors.

The rational checker reconstructs the moments using a slightly larger
tail: e⁻⁶⁴<50⁻¹⁶, obtained from Σ(j=0..7)4^j/j!>50. It independently
solves (7) by permutation determinants and Cramer's rule.

## 5. Global slope, positivity and unfolding rank

Let d be the minimum spacing among the 56 signed knots ±c_k. The
certificate verifies d≥32η. At most one transition is within d/2 of a
given u, so the R13 separation bound gives

\[
\|h'\|_\infty\le
\frac{\alpha}{\eta}\{1+4(56-1)50^{-8}\}
                      +\sum_{j\in J}2j|w_j|
 <0.000019910351817<0.00002.
\tag{11}
\]

Also

\[
\|h\|_\infty\le\alpha+\sum|w_j|
 <0.000000000917876530<1.
\tag{12}
\]

These are global upper bounds, not computed exact supremum norms.
Equation (12) ensures positivity of Φ(1+h). The corrected jets satisfy

\[
g_0=g_1=g_2=g_3=0,\quad g_4\approx-9.721188231640924\times10^{-13},
\quad \det J=\frac{g_4(g_4g_7-g_5g_6)}{4096}
       \approx-4.249937650878922\times10^{-40}.
\]

Both displayed nonzero quantities have certified negative enclosures.
The rational checker also forms the full 3×3 control determinant from
the moment dictionary, so the rank check is not only a restatement of
the reduced formula. This establishes exact order four and rank three.

## 6. What is established and what remains open

The lower bound applies to every bounded Lipschitz h satisfying (1);
the upper bound has an explicit real-analytic positive nondegenerate
witness. R13's older wider bracket remains valid. Its width was largely
a limitation of the earlier feasible witness, not evidence of a large
true penalty for this M.

The improvement uses analytic smoothing, moment corrections and additive
local loss inequalities; no novelty is claimed for these general tools.
The quantitative result in this family still requires literature-priority
assessment and external mathematical review. A different kernel, Q,
mass normalization, slope coordinate or finite-frequency restriction
defines a different numerical problem. Physical or industrial use has
not been inferred from this calculation.

[Certificate](results/slope_threshold_certificate.json),
[independent arithmetic](results/slope_threshold_check.json),
[separate quadratures](results/moment_crosscheck.json),
[R13 proof](../kernel_slope_budget/PROOF.md),
[R12 proof](../kernel_norm_threshold/PROOF.md).
