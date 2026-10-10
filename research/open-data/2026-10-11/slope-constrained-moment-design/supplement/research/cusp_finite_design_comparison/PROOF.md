# R30 — Effective comparison of optimal design values along a cusp arc

This is an analytic argument with validated numerical inequalities. It
extends R27's effective remainder to the R29 arc and derives finite-budget
comparisons from three coefficient derivative bounds. It is not a formal
proof checked by a theorem prover or an external referee report.

## 1. The exact objects being compared

Use the exact R03 cusp graph identified in [R29](../cusp_motion_continuation/PROOF.md),
with original driver and integration coordinates, and set

\[
 I=[-1/64,0],\qquad M_0=2\times10^{-5}.
 \tag{F1}
\]

At Q(ν)=(τ(ν),λ(ν),μ(ν),ν), let
Φ(u)=Σ_{n≥1}πn²e^{5u}(2πn²e^{4u}−3)e^{−πn²e^{4u}},
w_ν=Φ exp(λu²+μu⁴+νu⁶), p_j=(2u)^j cos(2τu+jπ/2),
q_{j,ν}=w_νp_j and f_ν=∫₀∞q_{3,ν}>0. The problem is

\[
 \delta_\nu(M)=\inf\{\|g\|_\infty:\operatorname{Lip}g\le M,
       \ \int q_{j,\nu}g=0\ (j<3),\ \int q_{3,\nu}g=f_\nu\}.
 \tag{F2}
\]

Every driver permits a separate function g. Both the densities and the
target f_ν depend on ν. This compares the associated moment problems,
not a fixed numerical target against different kernels. For a chosen ν,
the perturbation h=−g is fixed when differentiating its modified kernel
with respect to controls. Cost here means the minimum amplitude in F2,
not money, training time, energy, or a physical observable.

Let b*(ν) be R29's unique global minimizer of ∫|q₃−Σb_jq_j|,
q*=q₃−Σb*_jq_j, D=∫|q*| and δ₀=f/D. At all its positive roots z_k
write σ_k=sign q*'(z_k), γ_k=|q*'(z_k)| and Q_k=(q_j(z_k))_{j<3}.
The coefficient definitions are the full infinite sums of R23/R24:

\[
 \begin{split}
 \Gamma&=\sum_k\gamma_k,&G&=2\sum_k Q_kQ_k^T/\gamma_k,\\
 B_j&=\frac13\sum_k\sigma_k(q_jq^{*\prime\prime}/q^{*\prime}-q'_j),
 &v&=G^{-1}B,\\
 R&=\sum_k[(q^{*\prime\prime})^2/(36\gamma_k)-\sigma_kq^{*\prime\prime\prime}/60],
 &\Xi&=R-\tfrac12B^Tv,\\
 C_2&=\delta_0^3\Gamma/(3D),
 &C_4&=\delta_0^5[\Gamma^2/(3D^2)-\Xi/D].
 \end{split} \tag{F3}
\]

All summands are evaluated at their own roots. In particular the
coefficients below are exact functions of ν, not printed decimal centers.

## 2. Uniform effective remainder on the enlarged arc

**Theorem 1.** For every (ν,M)∈I×[M₀,∞), put
P₄,ν(M)=δ₀(ν)+C₂(ν)/M²+C₄(ν)/M⁴. Then

\[
 -\frac{K_-}{M^6}<\delta_\nu(M)-P_{4,\nu}(M)<\frac{K_+}{M^6},
 \quad K_-=1.02\times10^{-53},\quad K_+=1.64\times10^{-53}.
 \tag{F4}
\]

Thus the same published constants and onset as R27 hold on an interval
1024 times as long. R29's anchored bound C₄>2.48374879×10⁻³⁹ and
K₋/M₀²<C₄ imply δ_ν(M)>δ₀(ν)+C₂(ν)/M² everywhere in this domain.

**Proof of the extension.** The 32 closed R29 cells are
I_i=[−(i+1)/2048,−i/2048], i=0,…,31. Their exact cusp and unique
dual are already identified, including at seams; no new identification
by mere box overlap is used here. Fresh calculations on every entire
cell give the full sextic jets through order five, 28 disjoint finite
root neighborhoods, positive signed trial derivatives, a 354-leaf sign
cover of their complement in [0,1], and a positive tail gap on [1,1.001].
The trial dual path is b(a,ν)=b*(ν)+v(ν)a², with a≤a₀=2⁻¹⁴.
The new calculations verify |v|<(5,4,180) and the full expanded trial
box |b(a,ν)|<(.001,.1,.005), as required by the phase estimates.

The larger ν interval requires a new tail argument, not only finite
root jets. Write H=1/64 and P=λu²+μu⁴+νu⁶. For u≥1,

    |P'|≤44u³+6Hu⁵;       |P''|≤116u²+30Hu⁴;
    |P'''|≤216u+120Hu³;   |P''''|≤216+360Hu²;
    |P'''''|≤720Hu.

Since e^{4u}>50u³ and u⁵e^{−4u}<1/40, the exact checks give

\[
 \begin{gathered}
 (44/50+6H/40),\ (116+30H)/50^2,\ (216+120H)/50^3,\\
 (216+360H)/50^4,\ 720H/50^5\ <1.
 \end{gathered} \tag{F5}
\]

Consequently |P^(j)|<e^{4ju} for j=1,…,5. R26's Bell/product-rule
weight constants remain valid. Also ν≤0 gives the same upper envelope
w_ν≤88 exp(9u+9u⁴−πe^{4u}). The negative sextic factor is retained
in local jets; only in an upper tail bound is it replaced by 1.

For ε=2⁻¹² keep the first 28 roots and each tail root satisfying
ae^{4z_k}≤ε. The raw phase and spacing bounds need only
41<τ<42 and the expanded b bounds above. The enlarged v bounds meet
R27's rational inequalities for |κ_k|<46e^{4z_k}, the constants
550 and 2800 for the raw trial derivative/value, and the signed weighted
derivative bound 200w(z_k)z_k³. Here
κ_k=(Q_kᵀv−q*''(z_k)/6)/q*'(z_k). The active balance constant is
recomputed with V=(5,4,180); the inactive constants 188 and 2071000
still pass. No small-|ν| constant from R27 is silently assumed.

R26's whole-tail estimates therefore hold uniformly, with
S_d=88 exp(18+d−πe⁴)/(1−50⁻⁴) and
I_d=(88/500)exp(18+d−πe⁴), d=12,16,24. For inactive roots use
Σ_{ae^{4z_k}>ε}t_k≤(a/ε)^sΣt_ke^{4sz_k}, t_k≥0. The integral
cut at the first inactive root minus 3a retains the factors
(1−48a₀)⁻¹ and (1−72a₀)⁻¹. These bounds control the entire tail;
the root list is never treated as the complete infinite set.

The finite Taylor/support inequalities of
[R25](../theta_effective_remainder/PROOF.md), Sections 3–5, are recomputed
on each R29 cell, including variation of ν and of the dual. With the
tail added, a fresh dyadic preconditioner proves exact lower-moment
repair by shifting three centers by a⁴y_k. The uniform row bounds are

    contraction < (.005731,.007842,.004703),
    forcing     < (.328781,.448496,.267009),

and every row sum is <1. All repaired ramps remain in their disjoint
neighborhoods. The root prefix depends on a, not on the three correction
variables, so it is fixed during each contraction argument.

This proves the two estimates in R26 G11 for every fixed (ν,a): the
support bound applies to arbitrary competitors and the repaired primal
has exactly zero lower moments. New common sufficient constants are
K_d<655000 and K_p<4.746×10⁶. R26's auxiliary polynomial
J(A)=DA−ΓA³/(3M²)+Xi A⁵/M⁴−K_pA⁷/M⁶ has opposite endpoint
signs relative to f and positive derivative on [δ₀,U], with
U<9.181×10⁻¹⁰ and U/M₀<a₀. The upper endpoint's normalized margin
exceeds 1.7683×10⁻¹⁵. Hence its root yields an exactly feasible profile
after rescaling, for every M≥M₀. This step does not assume continuity
of the changing finite root prefix. Existence of an optimum follows
from the bounded Lipschitz sequence argument and dominated convergence
as in R26. The constructed kernel factor 1−g is positive since U<1.

Finally the scalar inversion keeps every term through polynomial
degree twelve after exact cancellation through degree two. The new
maximum computed bounds are below 1.001×10⁻⁵³ and 1.620×10⁻⁵³,
respectively, strictly below K₋ and K₊ in F4. A separate 512-bit
outward rational reconstruction verifies the inequalities, including
the moment repair and scalar inversion, on each entire cell. Taking
the union of the 32 cells proves Theorem 1. □

## 3. Three derivative bounds, not only the fourth coefficient

R29 establishes C¹ dependence of the exact coefficient functions and
justifies differentiation of their infinite sums. Its transcendental
enclosures are reused here as frozen inputs. Independently differentiating
the coefficient expressions with rational automatic differentiation gives

\[
 \begin{split}
 2.7\times10^{-11}&<\delta_0'(\nu)<3.0\times10^{-11},\\
 7.4\times10^{-26}&<C_2'(\nu)<8.7\times10^{-26},\\
 1.9\times10^{-40}&<C_4'(\nu)<5.3\times10^{-40}.
 \end{split} \tag{F6}
\]

Derivatives use the original driver ν, with one-sided endpoint values.
For example δ₀'=(f'D−fD')/D² and
C₂'=C₂(3f'/f−4D'/D+Γ'/Γ). The D' formula has no b*' term because
the sign moments vanish at the unrestricted dual minimizer. The Γ'
calculation does include root motion and the derivative of b*. R29's
tail derivative bounds and implicit Gram solve remain explicit inputs;
finite differences are not used to prove F6.

## 4. Finite-budget comparisons with a quantified separation

**Theorem 2.** Let ν₁<ν₂ be in I, d=ν₂−ν₁, M≥M₀, and
K_Σ=K₋+K₊=2.66×10⁻⁵³. Define
L(M)=2.7×10⁻¹¹+7.4×10⁻²⁶/M²+1.9×10⁻⁴⁰/M⁴ and
U(M)=3.0×10⁻¹¹+8.7×10⁻²⁶/M²+5.3×10⁻⁴⁰/M⁴. Then

\[
 L(M)d-\frac{K_\Sigma}{M^6}
 <\delta_{\nu_2}(M)-\delta_{\nu_1}(M)
 <U(M)d+\frac{K_\Sigma}{M^6}.
 \tag{F7}
\]

In particular a convenient sufficient condition for positive difference is
d≥1.54×10⁻¹⁴(M₀/M)⁶. This follows even after discarding the positive
C₂' and C₄' terms: K_Σ/(2.7×10⁻¹¹M₀⁶)<1.54×10⁻¹⁴.

To isolate the fourth-order effect in the actual optimal value, set

\[
 Z_M(\nu)=M^4[\delta_\nu(M)-\delta_0(\nu)-C_2(\nu)/M^2].
 \tag{F8}
\]

It is an expression involving the actual optimum, not just C₄. Then

\[
 1.9\times10^{-40}d-\frac{K_\Sigma}{M^2}
 <Z_M(\nu_2)-Z_M(\nu_1)
 <5.3\times10^{-40}d+\frac{K_\Sigma}{M^2}.
 \tag{F9}
\]

The sufficient positive-separation threshold in F9 is
d>3.5×10⁻⁴(M₀/M)². For the 33 exact nodes
ν_k=−1/64+k/2048, k=0,…,32, both actual optimal amplitudes and
the corresponding Z_M values are strictly increasing in k for every
M≥M₀. Indeed the adjacent Z lower bound is at least
1.9×10⁻⁴⁰/2048−K_Σ/M₀²=2.62734375×10⁻⁴⁴>0.
For amplitudes, already 2.7×10⁻¹¹/2048−K_Σ/M₀⁶>0.

**Proof.** Integrate F6 between ν₁ and ν₂ to bound the difference
of P₄. The two error terms in F4 have difference strictly between
−K_Σ/M⁶ and K_Σ/M⁶. Add these inequalities to obtain F7;
subtract the first two terms and multiply by M⁴ to obtain F9.
The node and separation conclusions follow by exact rational arithmetic.
No derivative or continuity of δ_ν(M) is needed for this comparison. □

At M=M₀ the endpoint pair has the concrete bounds

\[
 \begin{split}
 4.21877890\times10^{-13}
 &<\delta_{\nu=0}(M_0)-\delta_{\nu=-1/64}(M_0)
 <4.68753399\times10^{-13},\\
 2.90225\times10^{-42}
 &<Z_{M_0}(0)-Z_{M_0}(-1/64)
 <8.34775\times10^{-42}.
 \end{split} \tag{F10}
\]

## 5. What these bounds do and do not establish

Theorem 1 is uniform over a continuum of (ν,M), not 32 sampled solves.
Theorem 2 also applies to any pair satisfying its separation condition;
the 33-node statement is a convenient consequence, not its full scope.
The first two terms have been subtracted exactly in F8. Decimal rounding
of coefficients must be propagated separately before using that expression
in a numerical implementation.

Neither F7 nor F9 proves monotonicity for all arbitrarily close drivers:
as d→0 the fixed-budget error allowance stays nonzero. A bounded smooth
error may have rapidly varying derivative, so a value bound alone cannot
fill this gap. The negative-control cases in `compare_values.py` explicitly
leave tiny separations unresolved; they do not establish reversed ordering.
No derivative of the finite-M optimum, C₆ coefficient, maximal arc or
extension to all of [−29,0] is asserted.

These are amplitude-cost and moment results. They do not yet prove the
fourth derivative and three-control rank conditions for every resulting
modified kernel, a common perturbation throughout the arc, a physical
phase transition, or a new application in AI/LLMs. Novelty relative to
the literature and publication suitability require separate assessment.

## 6. Evidence and trust boundaries

Twelve exact algebra groups cover the enlarged tail hypotheses. The new
rational checker makes 4064 recorded decisions (32×[81 remainder +46
derivative AD]), and `compare_values.py` makes 146 exact comparison
checks. The fresh Arb producer evaluates each entire parameter box;
the rational checker independently rebuilds arithmetic from its explicit
transcendental and inherited inputs. It does not independently integrate
the kernel. The R29 audit separately reconstructs its cusp/dual/coefficient
chain, and `--with-arb` regenerates its transcendental data as well.

The analytic arguments in R23–R29 remain dependencies, particularly
support duality, root summability, exact repair, and scalar feasibility.
Fresh replay and matching hashes test provenance and reproducibility;
they do not constitute an external proof review. The plot uses F7/F9
and exact separation formulas; no finite-budget optimizer has been
numerically solved or plotted as an exact curve.
