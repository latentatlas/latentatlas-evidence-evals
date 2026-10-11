# R12 — A certified near-minimum relative change at the fixed cusp

21 September 2026. This package continues the R11 minimum-norm question.
All statements below use the original theta kernel and the exact R01
point Q. The analytic argument is a research proof draft, not a formal
proof-assistant result or an externally reviewed theorem. The numerical
inequalities have separate rational and quadrature checks.

## 1. Target, norm and exact inputs

Let dρ=Φ(u)exp(λ_Q u²+μ_Q u⁴)du on (0,∞), at the exact R01
point Q=(τ,λ_Q,μ_Q,0). Set

\[
p_j(u)=(2u)^j\cos(2\tau u+j\pi/2),\quad
f_j=\int p_j\,d\rho,\quad L_j(h)=\int p_jh\,d\rho.
\tag{1}
\]

R01/R09 certify f₀=f₁=f₂=0, f₃>0. A fixed real multiplier
Φ_h=Φ(1+h), independent of all moving controls, keeps Q at order
at least four exactly when

\[
L_0(h)=L_1(h)=L_2(h)=0,\qquad L_3(h)=-f_3.
\tag{2}
\]

Define δ_* as the infimum of ||h||∞ over all real bounded measurable
h satisfying (2). There is no frequency or derivative constraint.
The constructed feasible h below is even and real analytic, has norm
less than one, and gives order exactly four and rank-three controls.
Thus the same numerical bracket also applies to the infimum over
smooth positive nondegenerate designs, even without invoking R11's
general equality-of-infima theorem: the universal lower bound applies
to that smaller class, and our explicit feasible member gives its
upper bound. Equality of the two infima follows separately from R11.

The three approximate optimizer coefficients and the sign-template
knots were located with floating-point computation. They are then
converted to **exact binary rationals**, defining fixed candidates.
Their approximate optimality or the completeness of the floating-point
root search is not assumed in the proof.

## 2. Universal lower certificate from one residual

For any fixed real a=(a₀,a₁,a₂), set r=p₃−Σa_i p_i. For every h
satisfying (2),

\[
f_3=\left|\int r h\,d\rho\right|
\le\|h\|_\infty\int|r|\,d\rho.
\tag{3}
\]

Consequently a rigorous upper bound B_D on ∫|r|dρ gives
δ_*≥f₃/B_D. This elementary lower certificate does not require
proving that a is an exact minimizer of the three-variable L1 problem.

The fixed coefficients used here are

\[
a_0=-4326449874427607/36893488147419103232,
\]
\[
a_1=-1165166962990569/18014398509481984,
\qquad
a_2=4474338913982565/1152921504606846976.
\tag{4}
\]

There are N=28 positive binary-rational knots b₁<⋯<b_N<1, listed
exactly in `threshold_certificate.json`. Let s₀ start at +1 and change
sign at each b_k, remaining constant past b_N; extend it evenly to R.
Its moments S_j=∫p_j s₀dρ are computed by signed integration on
the 29 intervals from 0 to 1, with full-kernel and infinite-domain
tails and the exact-Q displacement included.

At exact Q, each interval [b_k−β,b_k+β], β=2⁻³⁶, is proved to
contain exactly one zero of r: the endpoint signs are opposite and
the derivative excludes zero throughout the interval. A collection
of 113 interval sign leaves proves that s₀=sign(r) on the complement
of these 28 boxes in [0,1]. Together the boxes and leaves form a
complete adjacent partition. This is the root-completeness argument
on [0,1]; a sampled plot is not used for that purpose.

If R_k bounds |r| and W_k bounds the density ρ on the kth box,
its possible contribution to the difference |r|−r s₀ is at most
4βW_kR_k. We use

\[
R_k\le |r(b_k)|+\beta\sup_{[b_k-\beta,b_k+\beta]}|r'|.
\tag{5}
\]

For u≥1 no residual-root enumeration is required. If T_j bounds
∫₁∞(2u)^j dρ, then the omitted difference is at most
2(T₃+Σ|a_i|T_i). Therefore

\[
B_D=\operatorname{up}\!\left(
S_3-\sum_{i=0}^2a_iS_i+
\sum_{k=1}^{28}4\beta W_kR_k+
2(T_3+\sum_{i=0}^2|a_i|T_i)\right)
\tag{6}
\]

is a valid objective upper bound. The finite-box correction is about
4.4524×10⁻²¹, and the infinite-domain correction is below 1.612×10⁻⁶⁷.
The independent rational checker reconstructs (6) from the enclosures;
it may round its upper endpoint slightly differently from Arb.

## 3. A quantitative smoothing lemma

The sharp sign template s₀ is not used as the final smooth design.
For η>0 define

\[
H_\eta(v)=\frac{1+\tanh(v/\eta)}2,
\qquad k_\eta(v)=\frac{\operatorname{sech}^2(v/\eta)}{2\eta},
\qquad s_\eta=k_\eta*s_0.
\tag{7}
\]

The kernel k_η is even, nonnegative and has integral one. Thus
|s_η|≤1. It is also given by the finite real-analytic formula

\[
s_\eta(u)=1+\sum_{k=1}^{N}d_k
\{H_\eta(u-b_k)+H_\eta(-u-b_k)\},
\quad d_k=-2(-1)^{k-1}.
\tag{8}
\]

It is even and independent of all controls. Here η=2⁻³².

**Lemma.** Let q(u)=ρ(u)p_j(u), u≥0, and suppose its even extension
to R is globally Lipschitz with constant M_j. Then

\[
\left|\int_0^\infty q(u)(s_\eta(u)-s_0(u))\,du\right|
\le N M_j\eta^2.
\tag{9}
\]

**Proof.** Let E_η=H_η−H, with H the step function. E_η is odd
and integrable, its integral is zero, and
|E_η(v)|≤exp(−2|v|/η). At a jump position b, subtract q(b) and use
the Lipschitz bound to obtain

\[
\left|\int_{\mathbb R}q(b+v)E_\eta(v)\,dv\right|
\le M_j\int_{\mathbb R}|v|e^{-2|v|/\eta}\,dv
=M_j\eta^2/2.
\]

Each jump has magnitude two. There are 2N jumps on the full line.
The product q(s_η−s₀) is even, so its half-line integral is half
its full-line integral. This gives N M_jη². ∎

This quadratic smoothing-error bound uses cancellation. A bound based
only on the absolute area of each transition would be of order η,
and would be much less effective for this certificate. We do not
claim that this elementary smoothing mechanism is a new general tool.

## 4. Global Lipschitz bounds for this kernel

For u≥0 the positive majorants

\[
0<\Phi(u)\le C_0e^{9u-\pi e^{4u}},\quad C_0=4\pi^2+6\pi,
\]
\[
|\Phi'(u)|\le C_1e^{13u-\pi e^{4u}},\quad
C_1=60\pi^2+30\pi+16\pi^3
\tag{10}
\]

follow termwise from the theta series. In particular, for powers
k²,k⁴,k⁶ the ratio of successive majorant terms is at most
64 exp(−3π)<1/2, so each sum is at most twice its first term.
Differentiating the kth kernel summand gives

\[
(30\pi^2 k^4e^{9u}-15\pi k^2e^{5u}
 -8\pi^3k^6e^{13u})e^{-\pi k^2e^{4u}},
\]

which proves the second bound by the triangle inequality.
Put P=λu²+μu⁴, with all coefficients ranging over the exact-Q
enclosure. Then

\[
|\rho'|\le e^P(|\Phi'|+|P'|\Phi),
\]
\[
|q_j'|\le |\rho'|(2u)^j+
\rho\{2j(2u)^{j-1}+2|\tau|(2u)^j\}.
\tag{11}
\]

The term with j−1 is omitted when j=0. We bound (11) on 256
dyadic cells covering [0,2], using endpoint upper bounds on each
polynomial monomial and positive exponential envelopes. On [2,∞),
each envelope term decreases. A common verified logarithmic-derivative
margin is

\[
4\pi e^{4U}-13-11/U-P_+'(U)>0,\qquad U=2,
\tag{12}
\]

where P_+ keeps only positive coefficient upper bounds. The required
monotonicity of u^{d−1}e⁻⁴ᵘ holds beyond U for each polynomial degree.
The largest envelope power needed for j≤8 is j+3≤11. Thus the
maximum of the cell bounds and the envelope value at U bounds
|q_j'| on the whole positive line. The even extension is globally
Lipschitz with the same bound, whether or not its derivative at zero
is considered. Equation (9) now encloses all nine smooth moments.

The very narrow transitions are **not numerically integrated as sharp
spikes**. Their moment effects are bounded analytically by (9).

## 5. Exact correction and a smooth feasible design

Retain R11's certified nonsingular moment matrix for frequencies
J={40,41,42,43}:

\[
A_{nj}=\int p_n\cos(2ju)\,d\rho,\quad0\le n\le3.
\]

Let

\[
\alpha=8877101635207251/9671406556917033397649408,
\]
\[
A w=(0,0,0,-f_3)^T+
\alpha\bigl(L_0(s_\eta),\ldots,L_3(s_\eta)\bigr)^T,
\tag{13}
\]

and define the exact real-analytic multiplier

\[
h_c(u)=-\alpha s_\eta(u)+\sum_{j\in J}w_j\cos(2ju).
\tag{14}
\]

Equations (13) define the exact coefficients through exact moments;
the published balls enclose those coefficients. Equation (2) follows
as an exact identity. Small numerical residuals are only consistency
checks. Positivity follows from

\[
\|h_c\|_\infty\le \alpha+\sum_{j\in J}|w_j|=:U_c<1.
\tag{15}
\]

The certified upper budget uses the outward upper endpoint of (15),
not the lower endpoint or midpoint of an interval enclosure.
No equality between the supremum norm and the coefficient bound
is claimed.

At Q, g_j=f_j+L_j(h_c). The full three-control matrix has rows
(-g_{n+2}/4,g_{n+4}/16,-g_{n+6}/64), n=0,1,2. At g₀=⋯=g₃=0,

\[
\det J=\frac{g_4(g_4g_7-g_5g_6)}{4096}.
\tag{16}
\]

Both the full determinant and (16) are checked independently with
rational interval arithmetic. Their signs and the fourth derivative
are certified as

\[
10^{13}g_4\in[-9.721188538,-9.721188537],
\quad 10^{40}\det J\in[-4.249937772,-4.249937771].
\tag{17}
\]

Thus h_c realizes an exact order-four zero with a rank-three
(λ,μ,ν) unfolding, at the original Q, while Φ(1+h_c)>0.

## 6. Certified near-minimum theorem

Combining the universal lower certificate (3)–(6) with the smooth
feasible upper certificate (13)–(15), and taking common outward
endpoints from Arb and the rational reconstruction, gives

\[
\boxed{
0.00000000091787079603827<\delta_*
<0.00000000091787079608363.
}
\tag{18}
\]

Equivalently, the endpoints are 9.1787079603827×10⁻¹⁰ and
9.1787079608363×10⁻¹⁰. For these displayed endpoints L,U,

\[
\frac{U-L}{L}<5\times10^{-11}.
\tag{19}
\]

The same outward interval contains the infimum over smooth positive
nondegenerate designs. In particular the explicit h_c satisfies
||h_c||∞/δ_*−1<5×10⁻¹¹. This is a certified near-minimum result,
not a closed-form evaluation of δ_*, an exactly optimal smooth
multiplier, or a uniqueness proof for the three coefficients a.

**Corollary (nonattainment in the continuous class).** For this
full-support positive theta density, no continuous multiplier attains
δ_*. Smooth positive nondegenerate multipliers have infimum δ_*, but
there is no exactly minimum-norm smooth member.

**Proof.** R11's L1-distance argument gives a minimizing coefficient
vector a_* and forces every measurable minimum-norm multiplier to
equal −(f₃/D)sign(r_{a_*}) almost everywhere. The nonzero analytic
residual r_{a_*} takes both signs: at arbitrarily large sine peaks it
equals ±((2u)³+2a_{*,1}u). Hence it has a sign-changing isolated zero.
The density is positive almost everywhere on every interval. A
continuous multiplier equal almost everywhere to a constant on either
side of that zero must equal it everywhere on each side. The two
constants are opposite and nonzero, contradicting continuity at the
zero. Equality of the smooth infimum with δ_* is R11 Theorem 3. ∎

This qualitative statement uses the general analytic proof from R11;
it does not follow merely from the computed decimal endpoints. It is
a consequence of the classical equality condition in the dual bound,
not a claim of a new general nonattainment principle.

The floating-point optimizer merely suggested a and the knots. The
universal lower bound and exact feasible upper bound establish the
near-minimum claim without trusting the optimizer's stopping rule.

## 7. Scope, validation and retained failures

There are 261 new finite-interval Arb evaluations: nine moments on
29 sign intervals. The 113 sign leaves, 28 root boxes and global
derivative envelopes address the analytic bounds surrounding those
integrals. The separate rational checker uses the frozen R11 rational
interval primitives, but imports no FLINT. It reconstructs the sign
partition, signed moments, smoothing-error arithmetic, adjugate solve,
full control determinant and common norm bracket.

It trusts the recorded integral enclosures, trigonometric interval
evaluations, positive envelopes, exact Q and analytic tails. It does
not reprove those analytic inputs. Three step moments are separately
checked with mpmath Gauss–Legendre quadrature at 50 and 80 digits, with
12 theta terms instead of the generator's eight. These are numerical
crosschecks, not a second rigorous integration or a direct evaluation
of the smooth transitions.

Two implementation issues were caught before issuing the respective
certificates and retained in `diagnostics/`: a strict comparison of
entire overlapping cost balls was replaced by the correct outward
upper endpoint; and a rational point decoder was corrected to retain
exact dyadics finer than its interval grid. Neither issue invalidated
the mathematical inequalities; failed versions and explanations are
kept rather than silently overwritten.

The admissible norm measures amplitude only. The smoothing width is
η=2⁻³²≈2.3283×10⁻¹⁰ in the original u coordinate. Smoothness does
not imply a small derivative norm: the transition derivative scale
α/η is approximately 3.94. That scale is explanatory, not a separately
certified sharp derivative norm. A bandwidth, Lipschitz budget, or
physical regularity constraint would change the optimization problem.

This is a new modified kernel. R10's finite 0/2/4 root window and
plots have not been transferred. No global root count, physical
stability, or statement about order-four zeros of the original fixed
Φ family follows. Classical dual bounds, smoothing and moment
correction are not claimed as new methods. Quantitative priority and
external expert review remain open; see [REFERENCES.md](REFERENCES.md).
