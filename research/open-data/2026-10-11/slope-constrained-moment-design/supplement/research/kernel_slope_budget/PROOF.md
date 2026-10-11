# R13 — Amplitude cost under a slope budget

21 September 2026. This continues the explicit norm limitation of R12.
The analytic results below are proof drafts subject to external review.
Compactness, convexity, moment correction and the elementary dual-loss
argument are not claimed as new general methods. The numerical witnesses
and strict finite-budget separation have separate interval/rational checks.

## 1. Problem and assumptions

Use R11's measure ρ and functions pⱼ at a fixed Q, with f₀=f₁=f₂=0,
f₃≠0, positive density almost everywhere on all of (0,∞), and the stated
exponential-moment assumption. Write Lⱼ(h)=∫pⱼh dρ. On [0,∞) define

\[
\delta(M)=\inf\{\|h\|_\infty: h\text{ bounded and Lipschitz},\quad
 \operatorname{Lip}(h)\le M,\quad
 L_0=L_1=L_2=0,\ L_3=-f_3\},\qquad M\ge0.
\tag{1}
\]

This is initially the closed moment problem for order **at least four**.
Exactly order four and rank three are separate geometric conditions.
For a smooth h, Lip(h)=sup|h′|. The derivative is with respect to the
original integration coordinate u, not t or a physical time. Changes of
u units change this budget. No kernel-mass normalization is imposed.

The admissible set in (1) includes h≡−1. That function annihilates the
entire kernel and is not a positive nondegenerate design. It is used only
to define the closed endpoint M=0 and to prove feasibility/limits. For
M>0 the minimizers shown below have cost strictly below one, hence preserve
positivity. Values at zero are well defined by Lipschitz continuity.

## 2. Attainment, strict gap and shape of the cost function

**Proposition 1.** The infimum in (1) is attained for every finite M.
Furthermore

\[
 \delta(0)=1,\qquad \delta_*<\delta(M)<1\quad(0<M<\infty),
 \qquad \lim_{M\to\infty}\delta(M)=\delta_*.
\tag{2}
\]

The function δ is convex, strictly decreasing and continuous on [0,∞).
Here δ* is the unrestricted L∞ infimum from R11/R12. These properties
do not constitute a numerical evaluation of the whole curve.

**Proof.** Constants have zero slope and h=−1 is feasible, so δ(M)≤1.
Take a minimizing sequence with uniformly bounded supremum norms. On
every [0,R] it is uniformly bounded and equicontinuous. Arzelà–Ascoli
and diagonal extraction give locally uniform convergence to h with
Lip(h)≤M and ∥h∥∞≤δ(M). Since |pⱼ| is ρ-integrable and the sequence
is globally uniformly bounded, dominated convergence preserves the four
moment equalities. This proves attainment; compactness on the entire
unbounded domain in the supremum norm is not asserted.

At M=0, h is constant and L₃(h)=hf₃=−f₃ forces h=−1. Thus δ(0)=1.
Choose a smooth feasible nondegenerate h₀ of cost d<1 supplied by R11,
with finite slope S. For any M>0 choose 0<θ≤1 with θS≤M and put

\[
 h_\theta=-1+\theta(1+h_0).
\tag{3}
\]

It is feasible, has cost at most 1−θ+θd<1, and slope at most θS.
In fact K(1+hθ)=θK(1+h₀): this construction is a uniform positive
rescaling of a feasible modified kernel, with its zeros unchanged.
The feasibility argument relies on allowing this rescaling; adding a
mass constraint would change the problem.

R11/R12 imply that no continuous multiplier attains δ* for this
full-support density. If δ(M)=δ* at finite M, attainment in (1) would
give such a continuous minimizer, a contradiction. Hence δ(M)>δ*.
R11 gives smooth compactly supported feasible designs of arbitrarily
near-δ* cost, each with some finite slope. This proves the limit at infinity.

Admissible sets are nested, so δ is nonincreasing. If h₁,h₂ are
minimizers for M₁,M₂, their convex combination is feasible with slope
≤(1−θ)M₁+θM₂ and cost ≤(1−θ)δ(M₁)+θδ(M₂). This proves convexity.
If δ took the same value at two distinct finite budgets, convexity and
nonincrease would force it to be constant thereafter. The limit and
strict gap rule that out. Finite convexity gives continuity on (0,∞).

Finally, |h(u)−h(0)|≤Mu and the last moment give

\[
 |h(0)+1|\le\frac{M}{|f_3|}\int u|p_3|\,d\rho,
 \qquad
 \delta(M)\ge1-\kappa M,\quad
 \kappa=\frac{\int(2u)^4d\rho}{2|f_3|}.
\tag{4}
\]

Together with δ(M)≤1 this proves continuity at zero. ∎

Attainment in (1) is in the Lipschitz class, not necessarily in C∞,
and the minimizer may have higher zero order or deficient unfolding rank.
We make no uniqueness or bang-bang description of that minimizer.

## 3. The geometric smooth infimum at a fixed positive budget

**Proposition 2.** For every M>0, the infimum over real smooth bounded
h with sup|h′|≤M, positive modified kernel, exactly order four at Q and
rank-three controls is also δ(M). Attainment in that smaller class is
not claimed.

**Proof.** Start with a minimizing Lipschitz h and a smooth positive
nondegenerate feasible h_b with Lip(h_b)<M, obtained from (3) with strict
inequality. For ε>0 mix (1−ε)h+εh_b. This remains feasible, has slope
strictly below M and cost approaching δ(M)<1. Its even extension to R
has the same Lipschitz bound. Convolve with an even nonnegative compact
smooth kernel of small support. Supremum norm and slope do not increase,
and uniform convergence implies convergence of the first eight moments.

Correct the first four errors exactly using the R11 smooth right inverse
R₃. That fixed finite-dimensional map is bounded in both supremum and
first-derivative norm, since its basis functions are smooth and compactly
supported. Thus the correction can fit inside the strict slope and
positivity margins. Use R₇ for an arbitrarily small adjustment of jets
4–7, keeping jets 0–3 unchanged and avoiding the zero polynomial locus
g₄(g₄g₇−g₅g₆)=0. Its first-derivative cost also tends to zero. The
result has the stated geometry, with cost arbitrarily close to δ(M).
The reverse infimum inequality is set inclusion. ∎

This uses the original u slope norm. A bound on a second derivative,
a Fourier cutoff or a fixed integral of the kernel has not been added.

## 4. Two certified smooth anchors and their interpolations

For the original theta kernel and exact R01 Q, retain the *exact* R11
four-cosine design h₁ and R12 smoothed design h₂. Their enclosures give

| Design | Certified slope budget Mᵢ | Certified amplitude budget Uᵢ |
|---|---:|---:|
| R11 h₁ | 0.00002 | 0.00000023803280902557 |
| R12 h₂ | 4 | 0.00000000091787079608363 |

Both bounds are strict for the respective functions. The R11 slope
bound is Σ2j|wⱼ|<1.975806172549×10⁻⁵. For R12, let d be the minimum
spacing among its 56 signed transition locations ±bₖ. The exact knots
give d≥32η. At most one transition can be within d/2 of any u; all
others contribute at most 4exp(−d/η) to sech². Consequently

\[
 \|s_\eta'\|_\infty
 \le\eta^{-1}\{1+4(2N-1)e^{-d/\eta}\}
 <\eta^{-1}\{1+4(2N-1)50^{-8}\}.
\tag{5}
\]

The rational Taylor bound Σₖ₌₀⁷4ᵏ/k!>50 proves e⁴>50 and hence
e⁻³²<50⁻⁸. Thus this exponential bound does not depend on a decimal
approximation. Combining (5) with the cosine correction gives

\[
 \|h_2'\|_\infty\le
 \alpha\eta^{-1}\{1+4(2N-1)50^{-8}\}
       +\sum 2j|w_j|<3.942225050961<4.
\tag{6}
\]

This is a global upper bound, not an exact derivative norm. It does not
make h₂ small in a derivative norm comparable to its 10⁻⁹ amplitude.

For the interpolation hθ=(1−θ)h₁+θh₂, both endpoint g₄ values are
negative. The three degree-two Bernstein coefficients of
g₄(θ)g₇(θ)−g₅(θ)g₆(θ) are all certified positive: the two endpoint
values and

\[
 \tfrac12(g_{1,4}g_{2,7}+g_{2,4}g_{1,7}
                  -g_{1,5}g_{2,6}-g_{2,5}g_{1,6}).
\tag{7}
\]

Hence every convex interpolation has g₄<0 and determinant
g₄(g₄g₇−g₅g₆)/4096<0. The jets here use the same original integral
normalization. Exact moment constraints and positivity are preserved.

With M₁=2×10⁻⁵, M₂=4, the explicit feasible upper curve is

\[
 U(M)=\begin{cases}
 1-(M/M_1)(1-U_1),&0\le M\le M_1,\\
 U_1+\dfrac{M-M_1}{M_2-M_1}(U_2-U_1),&M_1\le M\le M_2,\\
 U_2,&M\ge M_2.
 \end{cases}
\tag{8}
\]

For every M>0 these budgets are realized within the bound by smooth,
positive, nondegenerate designs: use (3), then the interpolation, then
h₂. The point M=0 is the degenerate closed endpoint. U(M) is an upper
bound and must not be drawn or quoted as the exact optimum curve.

## 5. A quantitative penalty at one residual sign change

Use the fixed R12 residual r=p₃−Σaᵢpᵢ, its exact zero z in the first
certified root box [b−β,b+β], and a=2⁻¹². On the whole interval
[b−β−a,b+β+a], the new interval calculation proves |r′|≥m>0 and
dρ/du≥w>0. The density lower bound uses only the positive first theta
summand. Put c=wm>0; this notation is unrelated to the residual's
coefficient vector. The interval is inside (0,∞).

For any feasible h with norm δ and slope ≤M,

\[
 \delta\int|r|d\rho-f_3
   =\int |r|(\delta+\operatorname{sgn}(r)h)d\rho.
\tag{9}
\]

Each integrand defect is nonnegative. Pair u=z−v and z+v. Monotonicity
gives |r(z±v)|≥mv, the signs are opposite, and Lipschitz continuity gives
a sum of the two unweighted defects at least 2δ−2Mv. For any
0<ℓ≤a with Mℓ≤δ, the pair therefore contributes at least

\[
 c\int_0^\ell v(2\delta-2Mv)dv
   =c(\delta\ell^2-\tfrac23M\ell^3).
\tag{10}
\]

Let L=0.00000000091787079603827 be the existing universal lower bound,
and take ℓ=min(a,L/M) for M>0. Then Mℓ≤L<δ. If B_D is the R12
upper bound on ∫|r|dρ, (9)–(10) imply

\[
 \delta(M)\ge
 \frac{f_3+c(L\ell^2-\tfrac23M\ell^3)}{B_D}.
\tag{11}
\]

The fixed residual need not be the exactly optimal dual residual.
This inequality uses its independently certified sign-changing zero,
not an unproved exact optimizer. The root center b itself is not assumed
to be the exact zero. The extra radius β is included in both majorants.

For M=2×10⁻⁵ the interval and separate rational computations give

\[
 \boxed{0.000000000917870847<\delta(0.00002)
             <0.00000023803280902557.}
\tag{12}
\]

The lower bound is greater than R12's *upper* bound on δ*. Thus finite
slope has a certified strictly positive cost in this numerical example,
in addition to the qualitative strict-gap theorem. The separation is
small; the bracket (12) is wide. It does not say the optimum cost rises
to the R11 witness's upper budget.

One new positive moment A₄=∫(2u)⁴dρ, recomputed at higher precision,
also yields the convenient global bound

\[
 \delta(M)\ge1-476270901\,M.
\tag{13}
\]

For example δ(10⁻¹⁰)>0.9523729099. This is a bound on maximum relative
amplitude deviation in the stated norm, not a claim that the entire
kernel is uniformly reduced by that fraction. The particular feasibility
construction (3) does uniformly rescale its modified kernel.

## 6. Verification and limits

The generator uses frozen exact-Q and R11/R12 coefficient/moment data.
It verifies both global slope upper bounds, the interpolation Bernstein
signs, a new local residual/density enclosure, and A₄ by 8 integrals at
110 digits plus 12 at 135 digits, with 16/24 theta terms and explicit
tails/Q displacement. A standard-library rational checker rederives
the budget inequalities, Bernstein signs, dual-loss penalty, outward
displayed bounds and sample envelope consistency. It trusts the local
transcendental enclosures and integral values as inputs. A separate
mpmath 90/115-digit computation corroborates the new positive moment;
it is not an interval proof.

The analytic compactness and smoothing arguments have not been formally
verified or reviewed by an external mathematician. The exact finite-M
optimizer, its uniqueness/regularity and a sharp quantitative δ(M)
curve are not established. A minimizer in the Lipschitz class need not
be a smooth nondegenerate design; Proposition 2 states equality of
infima, not attainment there. No Fourier cutoff, mass normalization,
new finite root-count window, or physical interpretation is supplied.
