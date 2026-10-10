# R26 — A uniform fourth-order remainder for all large slope budgets

This analytic argument replaces R25's positive minimum width by a
width-dependent finite prefix of switches. It uses the exact fixed theta
Q and b* of R12/R15 and the exact coefficients of R23/R24. The numerical
hypotheses and constants are validated by Arb and separately reconstructed
with outward-rounded rational arithmetic. Neither this proof nor its
inherited analytic lemmas have been formalized in a proof assistant or
independently refereed.

## 1. Result and fixed problem

Let q_j=w p_j, p_j=(2u)^j cos(2τu+jπ/2),
w=Φ exp(λu²+μu⁴), q*=q₃−Σ_{j<3}b*_j q_j. The half-line problem is

\[
\delta(M)=\inf\{\|g\|_\infty:\operatorname{Lip}g\le M,
\ \int_0^\infty q_jg=0\ (j<3),\ \int_0^\infty q_3g=f>0\}.
\tag{G1}
\]

Here Φ=Σ_{n≥1}πn²e^{5u}(2πn²e^{4u}−3)e^{−πn²e^{4u}} and
f=∫₀^∞q₃(u)du is the fixed positive target f₃ of R12/R15. The exact
Q=(τ,λ,μ,0) and b* are the localized objects of those packages; their
input balls are carried by the [R25 certificate](../theta_effective_remainder/results/certificate.json).
The printed coordinates τ≈41.40034, λ≈−3.64569, μ≈8.33512 merely
identify this example. The constants below are not uniform over arbitrary
positive targets f or over that coarse parameter range. The coordinate
u and its Lipschitz normalization are the original ones.

Use D=∫|q*|, δ₀=f/D, Γ,G,B,v=G⁻¹B,R,P,Xi=R−P and
C₂=δ₀³Γ/(3D), C₄=δ₀⁵[Γ²/(3D²)−Xi/D] from R23/R24. All are
exact objects, including the infinite coefficient sums. Put
P₄(M)=δ₀+C₂/M²+C₄/M⁴.
Their full root-sum definitions are [R23, equation W4](../infinite_slope_fourth_order/PROOF.md).

**Theorem.** For every M≥M₀=2×10⁻⁵,

\[
-\frac{9.593\times10^{-54}}{M^6}
 <\delta(M)-P_4(M)
 <\frac{1.488\times10^{-53}}{M^6}.
\tag{G2}
\]

This is now a genuine O(M⁻⁶) remainder as M→∞. It does not prove
existence or a value of a sixth-order coefficient. No statement is made
about varying Q along the cusp curve or uniqueness of the true finite-M
optimizer. The constants refer to exact coefficients; decimal rounding
of coefficients requires a separate error allowance.

## 2. Choosing the finite prefix

Set a₀=2⁻¹⁴ and ε=2⁻¹². At a given 0<a≤a₀, always include the 28
roots in [0,1]. Among the remaining exact roots of q*, include precisely
those for which a exp(4z_k)≤ε. These are the active tail roots; they form
a finite prefix. Use the trial multiplier and centers

\[
b(a)=b^*+va^2,\quad
\kappa_k=\frac{Q_k^Tv-q^{*\prime\prime}(z_k)/6}{q^{*\prime}(z_k)},
\quad c_k=z_k+\kappa_k a^2.
\tag{G3}
\]

The normalized primal template has ramps σ_k(u−c_k)/a at all included
roots and the appropriate ±1 plateaus. It keeps the last plateau to
infinity. Let z_n be the first inactive root and put L(a)=z_n−3a.
No original root is removed from the mathematical problem: omitted
profile transitions and omitted coefficient terms are explicitly bounded.

The elementary inequality that removes a_min is, for t_k≥0 and s>0,

\[
\sum_{a e^{4z_k}>\varepsilon}t_k
 \le (a/\varepsilon)^s\sum_k t_k e^{4sz_k}.
\tag{G4}
\]

For x≥L(a), z_n≤x+3a. Inactivity implies
a^{-s}<ε^{-s} exp(4sx+12s a₀). Consequently an omitted integral,
divided by a^s, is bounded by a fixed exponentially weighted integral.
The theta density decays sufficiently fast for all weights used below.

The prefix may change discontinuously with a. We do not assume that the
resulting family of profiles is continuous. Section 7 proves feasibility
at every budget using an auxiliary scalar polynomial instead.

## 3. Root geometry and active neighborhoods

The enlarged R25 trial coefficient box satisfies
|b₀|<.001, |b₁|<.1, |b₂|<.005, and the true v obeys
(|v₀|,|v₁|,|v₂|)<(4,3,168)=V. A fresh interval evaluation proves
r_b>0 on [1,1.001] over this whole enlarged box. Thus every original
or trial root after 1 is greater than 1.001.

For u≥1 write r_b=T sin φ with
A=8u³+2b₁u, B=4b₂u²−b₀, T=(A²+B²)^(1/2),
φ=2τu+atan(B/A). The coarse coefficient bounds give A>7u³,
|T'|<25u² and 81<φ'<85. For example
|φ'−2τ|≤[(8.2)(.04)+(.021)(24.2)]/(7.8²u²)<.02.
Roots have spacing >3/85 and |r'_b(z)|>567z³. Parameterize the segment
by b*+sva², 0≤s≤1. Since Σ_j V_j 2^j=682, implicit differentiation
gives |dz/ds|≤682a²/(567z)<168a²/81<3a². The initial gap prevents
a root crossing u=1. This derivative bound continues each phase-labelled
root along the whole segment without escape to infinity.

For each active tail root let N_k(a)=[z_k−3a,z_k+3a]. These
neighborhoods lie above 1 and are disjoint, since 3a₀<.001 and
6a₀<3/85. R24's raw derivative estimates and exact rational arithmetic
give, throughout N_k(a),

\[
\sigma_k r'_{b(a)}(x)>550z_k^3,\qquad
|r_{b(a)}(x)|<2800a z_k^3,\qquad
|\kappa_k|<46e^{4z_k}.
\tag{G5}
\]

For the first estimate the variation of r*' from z to x is at most
63000(1+3a₀)³(3a₀)z³<12z³; the multiplier perturbation costs <z³.
For the second, use 900(1+3a₀)³(3a)z³ plus the perturbation
682(1+3a₀)² a²z³. For the third use the root identity
κ=pᵀv/r*'−(2w'/w+r*''/r*')/6, with
|pᵀv/r*'|<2, |w'/w|<135e^{4z}, |r*''/r*'|<112 and e^{4z}>50.

On N_k, |w'/w|<136e^{4z}. Hence |log(w(x)/w(z))|<408ε<1/2,
and 1/2<w(x)/w(z)<2. Combining G5 with 550−136·2800ε>400 gives

\[
\sigma_k q'_{b(a)}(x)>200w(z_k)z_k^3=:m_k>0.
\tag{G6}
\]

The approximate center satisfies |c_k−z_k|<46εa<a. The true trial
root is within 3a² of z_k. Its balanced center lies within a of that
root, and its entire ramp lies in N_k, because 2a+3a²<3a. The
approximate ramp, the balanced ramp and their intervening center segment
are therefore in the same region of positive signed density derivative.
Existence of the balanced center follows from the integral's opposite
signs at centers z_k(b)±a; uniqueness follows from the derivative sign.

The R25 finite neighborhoods handle the first 28 roots. The tail phase
labels handle the active roots after 1 and exclude extra trial roots
before L(a). The last balanced active ramp ends before L(a), by
6a<3/85. These facts justify the same cellwise support inequality as R25.

## 4. Explicit weighted derivative bounds

The theta derivative polynomials satisfy P₀=−3+2x and
P_{l+1}=(5−4x)P_l+4xP'_l, for l≤4. For u≥1, each absolute
theta-series monomial has successive-n ratio at most
2¹⁴ exp(−3πe^{4u})<1/2. The first summand lower bound
Φ≥π²exp(9u−πe^{4u}) yields
|Φ^(l)/Φ|≤K_l exp(4lu), with K₀=1 and
K_l=2[|P_l(0)|/3+Σ_{i≥1}|[x^i]P_l|4^{i−1}].

The potential derivatives satisfy |(λu²+μu⁴)^(j)|≤exp(4ju)
for j≥1 through order five. The Bell numbers (1,1,2,5,15,52)
therefore give relative weight constants W_l by the product rule.
In particular W₁=135 and W₂<3800.

Let P_jl=2^j Σ_h binom(l,h)(j)_h84^{l−h}. Define

\[
E_{jl}=\sum_{k=0}^l {l\choose k}W_k P_{j,l-k}/50^{l-k},
\quad C_l=P_{3l}+.001P_{0l}+.1P_{1l}+.005P_{2l}.
\tag{G7}
\]

For x≥1, |q_j^(l)(x)|≤E_jl w(x)x^j exp(4lx). On an active
N_k the bound becomes 8E_jl w(z)z^j exp(4lz): the factors for
w, x^j and the exponential each cost less than 2. The factor 8 is
deliberately conservative. The exact-root bounds used below are
|q*''(z)|≤T w(z)z³e^{4z}, T=900·273,
and |q*'''(z)|≤U w(z)z³e^{8z}, U=900·12400.

To avoid an unnecessary extra exponential power, use r*(z)=0 also
for the neighborhood remainder. The raw value is ≤2800a z³, and
a≤εe^{-4z}. Thus for n=4,5,

\[
\sup_{N_k}|q^{*(n)}|
 \le A_n w(z)z^3 e^{4(n-1)z},\quad
A_n=8\left[2800\varepsilon W_n+
 \sum_{k=0}^{n-1}{n\choose k}W_k C_{n-k}/50^{n-1-k}\right].
\tag{G8}
\]

This is a neighborhood estimate using a bound on r*(x), not the false
claim that r*(x)=0 away from z.

Insert these estimates and |κ|≤K e^{4z}, K=46, into R25's exact
local Taylor formulas. Since a e^{4z}≤ε on active roots, the constants
are independent of a. The local moment remainder divided by a⁴ is
bounded by H_j w(z)z^j e^{12z}, where

    H_j = E_j1 K² + E_j2(K+K³ε²)/3
          +8E_j3(1/5+2K²ε²+K⁴ε⁴)/12.

The local q* target remainder divided by a⁶ is bounded by
C_* w(z)z³ e^{16z}, where

    C_* = T K³/3 + U(2K²+K⁴ε²)/12
        + A₄[K+(10/3)K³ε²+K⁵ε⁴]/60
        + A₅[1/7+3K²ε²+5K⁴ε⁴+K⁶ε⁶]/360.

The local balance defect |E q_b(c+ay)|/a⁴ is bounded by
C_h w(z)z³ e^{12z}, where

    C_h = T K²/2 + U(K+K³ε²)/6
        + A₄(1/5+2K²ε²+K⁴ε⁴)/24
        + (1/50) Σ_j V_j[E_j1 K+4E_j2(1/3+K²ε²)].

All these rational constants are generated exactly in `check_algebra.py`.
Strong concavity as in R25 bounds the support gain on balancing a tail
cell by a⁸(C_h²/200) w(z)z³ e^{24z}, using G6.

## 5. Whole-tail sums and inactive contributions

For 0≤p≤3 and d≤24, the envelope
88u^p exp((9+d)u+9u⁴−πe^{4u}) has logarithmic derivative <−500
on u≥1. Indeed its positive part is at most (p+9+d+36)u³≤72u³,
while the negative part is less than −600u³. Consequently

\[
\begin{split}
\sum_{z_k>1}w(z_k)z_k^p e^{d z_k}
 &\le S_d:=\frac{88e^{18+d-\pi e^4}}{1-50^{-4}},\\
\int_1^\infty w(u)u^p e^{du}\,du
 &\le I_d:=\frac{88}{500}e^{18+d-\pi e^4}.
\end{split}                                                   \tag{G9}
\]

The root sum uses spacing >3/85 and 500(3/85)>16. Both formulas
include all roots or the entire integral, not a finite numerical cutoff.

At every original tail root, R24's root identities and coarse constants
give the following convenient bounds:

    γ ≤900wz³;  |G_jl,k| ≤(32/567)wz;
    |B_j,k| ≤187wz²e^{4z};  |R_k| ≤2070000wz³e^{8z};
    |(B−Gv)_j,k| ≤188wz³e^{4z};
    |R_k+(1/2)vᵀG_kv−B_kᵀv| ≤2071000wz³e^{8z}.

G4 now bounds the inactive Gamma contribution to the sixth-order
error by 300ε⁻⁴ S₁₆, and the inactive fourth coefficient by
2071000ε⁻² S₁₆. The inactive quadratic lower-moment coefficient,
divided by a², is at most 188ε⁻²S₁₂.

The gap gives L(a)>1. On the remaining integral tail |q_b|<9wu³,
and |q_j|≤2^jwu^j. Using the integral version of G4 gives

\[
\begin{split}
2a^{-6}\int_{L(a)}^\infty |q_b|
 &\le 18\varepsilon^{-6}\frac{I_{24}}{1-72a_0},\\
2a^{-4}\int_{L(a)}^\infty |q_j|
 &\le 2^{j+1}\varepsilon^{-4}\frac{I_{16}}{1-48a_0}.
\end{split}                                                   \tag{G10}
\]

We used exp(t)≤1/(1−t) for 0≤t<1. The factors 72a₀ and 48a₀
come from L=z_n−3a; their shift is retained.

Combining active and inactive errors gives the a-independent moment
tail constants

    H_tail,j = H_j S₁₂ +188ε⁻² S₁₂
                   +2^{j+1}ε⁻⁴ I₁₆/(1−48a₀),

and the target sixth-order tail constant

    K_tail,6 = C_* S₁₆ +Σ_j V_j H_j S₁₂
       +300ε⁻⁴ S₁₆ +2071000ε⁻² S₁₆
       +18ε⁻⁶ I₂₄/(1−72a₀) <8.411×10⁻³⁵.

The added support eighth-order constant is
(C_h²/200) S₂₄ <3.366×10⁻⁴⁰. These are constants in normalized
target/support estimates, not direct errors in δ(M).

## 6. Moment repair and global support inequalities

The 28 finite-root Taylor/support constants of R25 use a₀ only;
its a_min-dependent tail terms are discarded. Add H_tail,j to the
finite moment bounds. The same dyadic preconditioner C and repair box
W=(2²⁶,2²⁶,2²⁴) still satisfy each contraction-plus-forcing bound <1.
For every fixed a>0, the prefix is finite and three center corrections
e_k=a⁴y_k therefore make the lower moments exactly zero. The root
selection is independent of y, so its discontinuities in a do not
affect this contraction in y. The finite repair and its objective-cost
bound are unchanged.

Let H_v(a) be the full support of q_{b(a)} over |s|≤1, Lip(s)≤1/a,
and S(a) the target of the repaired normalized primal. We obtain, for
every 0<a≤a₀,

\[
\begin{split}
H_v(a)&\le D-\Gamma a^2/3+\Xi a^4+K_d a^6,\\
|S(a)-(D-\Gamma a^2/3+\Xi a^4)|&\le K_p a^6,
\end{split}                                                   \tag{G11}
\]

where K_d<467733 and K_p<3963115. Specifically,

    K_d = K₆^finite +K_tail,6
                     +a₀²[K₈^finite,dual+(C_h²/200)S₂₄],
    K_p = K₆^finite +K_tail,6 +a₀²K₈^finite,primal.

The baseline D is exact because all sign moments at b* vanish. The
quadratic and fourth coefficients are the full infinite sums; G4/G10
pay for omitted terms. The balanced-cell support bound applies to
arbitrary competitors, whereas the repaired primal supplies feasibility.

## 7. Every budget without assuming continuity of the prefix

Use U from R25, U<9.178748657×10⁻¹⁰, and define

\[
F_M(A)=DA-\Gamma A^3/(3M^2)+\Xi A^5/M^4,\qquad
J_M(A)=F_M(A)-K_p A^7/M^6.
\tag{G12}
\]

For all M≥M₀, a= A/M≤U/M₀<a₀ when δ₀≤A≤U. Fresh interval
inequalities prove J_M(δ₀)<f<J_M(U). The lower endpoint follows from
Γ/3−Xi δ₀²/M₀²>0. At the upper endpoint we drop the positive Xi
term and obtain the uniform positive normalized margin

    U−δ₀−ΓU³/(3DM₀²)−K_pU⁷/(DM₀⁶) >1.76868×10⁻¹⁵.

Also J'_M≥D−ΓU²/M₀²−7K_pU⁶/M₀⁶>0. Therefore the scalar
polynomial has a unique root A_+(M) in [δ₀,U] with J_M(A_+)=f.
At a=A_+/M, G11 gives S(a)≥f/A_+>0. Scaling the repaired profile
by A=f/S(a)≤A_+ gives exact target f and Lipschitz constant
A/a≤M. This proves δ(M)≤A_+≤U for every M≥M₀, despite any
discontinuity of the prefix as a changes. No continuity of S is invoked.

The lower bound δ(M)≥δ₀ and an Arzelà–Ascoli diagonal subsequence give
an optimizer in this amplitude interval. Local uniform convergence of
uniformly bounded M-Lipschitz functions preserves the moments by dominated
convergence, since every q_j is in L¹. For the optimizer use a=δ(M)/M in G11:
F_M(δ(M))≥f−K_dU⁷/M⁶.

R25's exact scalar polynomial calculation bounds
|F_M(P₄)−f|≤K_poly/M⁶ for all M≥M₀; it uses only the upper
bound on w=(δ₀/M)² and has no dependence on a_min. Also P₄∈[δ₀,U]
and F'_M≥d_min=D_lower−Γ_upper U²/M₀²>0. The inverse bound gives

\[
K_-=(K_{\rm poly}+K_dU^7)/d_{\min}<9.593\times10^{-54},\qquad
K_+=(K_{\rm poly}+K_pU^7)/d_{\min}<1.488\times10^{-53}.
\tag{G13}
\]

This proves G2. The auxiliary root's uniqueness is not uniqueness of
the true optimal multiplier or of the infinite-dimensional optimizer.
The feasible perturbation h=−A s remains positive as a kernel factor
because A≤U<1.

## 8. Consequences and evidence boundary

Since C₄>2.49203004×10⁻³⁹, G2 gives for every M≥M₀

\[
1-9.624\times10^{-6}(M_0/M)^2
 <\frac{\delta(M)-\delta_0-C_2/M^2}{C_4/M^4}
 <1+1.493\times10^{-5}(M_0/M)^2.
\tag{G14}
\]

Thus δ(M)>δ₀+C₂/M² from the explicit onset M₀ onward. M₀ is a
sufficient onset, not asserted minimal. The remainder after adding
C₄/M⁴ has no determined sign. Existence of lim M⁶[δ−P₄] remains open.

The newly computed quantities validate the analytic estimates above.
The rational checker accepts the transcendental tail enclosures and
inherited finite bounds as inputs. Independent direct differentiation
and ramp quadrature at four distant switches corroborate, but do not
prove, the uniform tail estimates. No external approval, formal proof,
literature priority or publication acceptance is implied.

[Evidence table](results/TABLE.md), [review](REVIEW.md), [reproduction](README.md),
[terminology](../theta_effective_remainder/CERTIFICATION_TERMINOLOGY_TR.md).
