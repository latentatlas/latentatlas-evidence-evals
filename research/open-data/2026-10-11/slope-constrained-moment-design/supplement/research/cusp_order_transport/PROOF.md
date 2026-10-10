# R31 — Moment-preserving transport and strict ordering of the actual optimum

This is an analytic proof with computer-validated inequalities, conditional
on the exact cusp graph and feasibility results of R29/R30. It is not a
formal proof checked by a theorem prover or an external referee report.
All numerical assertions below have explicit domains and error bounds.

## 1. Objects and theorem

Use the exact R03 cusp graph identified throughout
[R29](../cusp_motion_continuation/PROOF.md). Set I=[−1/64,0], M₀=2×10⁻⁵,
Q(ν)=(τ(ν),λ(ν),μ(ν),ν), and

\[
 \begin{split}
 \Phi(u)&=\sum_{n\ge1}\pi n^2e^{5u}(2\pi n^2e^{4u}-3)e^{-\pi n^2e^{4u}},\\
 P_\nu(u)&=\lambda(\nu)u^2+\mu(\nu)u^4+\nu u^6,\quad
 w_\nu(u)=\Phi(u)e^{P_\nu(u)},\\
 p_{j,\nu}(u)&=(2u)^j\cos(2\tau(\nu)u+j\pi/2),\quad q_{j,\nu}=w_\nu p_{j,\nu},\\
 f_\nu&=\int_0^\infty q_{3,\nu}(u)\,du>0.
 \end{split} \tag{T1}
\]

As in [R30](../cusp_finite_design_comparison/PROOF.md), let

\[
 \delta_\nu(M)=\inf\{\|g\|_\infty:\operatorname{Lip}(g)\le M,
 \ \int q_{j,\nu}g=0\ (0\le j<3),\quad \int q_{3,\nu}g=f_\nu\}.
 \tag{T2}
\]

The functions are real, bounded and Lipschitz on [0,∞). Every ν permits
a separate function g, and the target f_ν depends on ν. This is the
minimum amplitude for this specific moment problem, not a monetary,
training, energy or measured physical cost. Kernel perturbation is h=−g.
R30 gives attainment and 9.17×10⁻¹⁰<δ_ν(M)<U=9.181×10⁻¹⁰ for M≥M₀.
Its lower bound follows already from δ_ν(M)≥δ₀(ν)=f_ν/D_ν.

**Theorem.** For every M≥M₀ and every ν₁<ν₂ in I, put
 d=ν₂−ν₁ and η=τ(ν₁)/τ(ν₂). Then

\[
 \boxed{\delta_{\nu_2}(M)\ \ge\ \eta e^{d/50}\delta_{\nu_1}(M)
 \ >\delta_{\nu_1}(M).} \tag{T3}
\]

In particular η≥exp(0.00259d), so

\[
 \log\delta_{\nu_2}(M)-\log\delta_{\nu_1}(M)\ge0.02259d,
 \qquad
 \delta_{\nu_2}(M)-\delta_{\nu_1}(M)>2.07\times10^{-11}d.
 \tag{T4}
\]

There is no positive minimum separation between ν₁ and ν₂. No derivative
or uniqueness of the finite-M optimizer is assumed or concluded.

## 2. A sufficient transport principle

This section applies to any positive C² weight family with the moment
shape in T1, C¹ parameter dependence, τ>0, f>0 and integrable moments,
with continuous mixed derivative ∂ᵤ∂ν log w, provided the bounds stated
below hold. For a general weight, replace ∂νP by ∂ν log w in T7.
The theta formula is used only
when checking those bounds in Sections 3–5.

For ν₁<ν₂ define

\[
 T_{1\leftarrow2}(u)=\frac{f_1}{f_2}\eta^4
                     \frac{w_2(\eta u)}{w_1(u)},
 \qquad (\mathcal T_{1\leftarrow2}g)(u)=T_{1\leftarrow2}(u)g(\eta u).
 \tag{T5}
\]

The weight is strictly positive. Since p_{j,2}(ηu)=η^j p_{j,1}(u),
the substitution x=ηu, including its Jacobian, gives

\[
 \int_0^\infty q_{j,1}\mathcal T_{1\leftarrow2}g
 =\frac{f_1}{f_2}\eta^{3-j}\int_0^\infty q_{j,2}g
 \quad(0\le j\le3). \tag{T6}
\]

Thus all four feasibility equalities are preserved with the appropriate
new target. More generally a highest target moment m uses η^(m+1).
T6 is algebraic; it does not depend on g being an optimizer. Absolute
convergence follows from boundedness once the estimate below is proved.

Run backwards in the parameter, ν(t)=ν₂−t, 0≤t≤d. Write
η(t)=τ(ν(t))/τ(ν₂), T(t,u)=T_{ν(t)←ν₂}(u), and set

\[
 \kappa_\nu=-\tau'(\nu)/\tau(\nu),\quad L_\nu=\partial_u\log w_\nu,
 \quad r_\nu=-f'_\nu/f_\nu+4\kappa_\nu+
 \partial_\nu P_\nu+\kappa_\nu uL_\nu. \tag{T7}
\]

Assume κ≥0 and, for some a₀,c>0, the **whole-half-line bound**

\[
 r_\nu(u)+\kappa_\nu+a_0|\partial_u r_\nu(u)|\le-c
 \quad(\nu\in I,\ u\ge0). \tag{T8}
\]

Direct differentiation of T5 gives, with D=∂ₜ−κu∂ᵤ,
DT=rT, Dη=κη and D(Tᵤ)=(r+κ)Tᵤ+rᵤT. In particular the last term
has a plus sign from commuting ∂ᵤ with D. Let W=ηT+a₀|Tᵤ|.
Since η≥1 and T>0, T≤W. Along a characteristic u' = −κu,

    D W ≤ (r+κ)W + a₀ |rᵤ| T ≤ −c W,     W(0,u)=1.

The absolute value inequality holds almost everywhere along each
characteristic; |Tᵤ| is locally absolutely continuous, which suffices
for integration. Every finite (t,u) characteristic starts at the finite
point η(t)u; no boundedness of r on the entire unbounded domain is
needed. Consequently W≤exp(−ct), uniformly for all u≥0, and
T≤exp(−ct)/η. For any bounded Lipschitz g with
||g||∞≤a₀M and Lip(g)≤M, the product/chain rule holds almost everywhere
and yields

\[
 \|\mathcal T g\|_\infty\le\frac{e^{-cd}}\eta\|g\|_\infty,
 \qquad \operatorname{Lip}(\mathcal T g)\le e^{-cd}M.
 \tag{T9}
\]

The derivative bound implies a global Lipschitz bound by integration on
every finite interval. This proves the sufficient transport principle.
It also makes the transformed moment integrals absolutely convergent.

## 3. Parameter bounds from the exact cusp arc

R29's 32 closed cells cover I with their already identified exact graph.
No new gluing by overlapping approximate boxes is used. Reconstruct
f′=τ′D₄−λ′D₅/4+μ′D₇/16−D₉/64 from the integral derivative dictionary.
Both Arb and an independent 512-bit outward rational computation verify
on every whole cell

| Quantity | Strict enclosing bounds |
|---|---|
| κ=−τ′/τ | (0.00259, 0.00260) |
| f′/f | (0.0437, 0.0451) |
| λ | (−3.651, −3.645) |
| μ | (8.330, 8.336) |
| λ′ | (0.3260, 0.3264) |
| μ′ | (0.2939, 0.2942) |

The actual driver lies in [−1/64,0]; tiny representational enlargement
of R29's stored parameter balls is not a change in the exact driver
interval. Take a₀=1/16384 and c=1/50. R30's per-cell construction gives
U/M₀<a₀. Thus every attained optimal profile for M≥M₀ is in the class
required by T9.

## 4. Validated logarithmic theta derivatives on 0≤u≤1

Put x=πe^{4u}≥π>3.14 and let φₙ denote the nth positive theta summand.
For n≥2 write

    Rₙ=φₙ/φ₁=n²(2n²x−3)/(2x−3) exp[−(n²−1)x],
    ℓₙ=∂ᵤ log φₙ=9+12/(2n²x−3)−4n²x,
    ℓₙ′=−16n²x−96n²x/(2n²x−3)².

For R=Σ_{n≥2}Rₙ, differentiate the positive ratio series:
R′=ΣRₙ(ℓₙ−ℓ₁), R″=ΣRₙ[(ℓₙ−ℓ₁)²+ℓₙ′−ℓ₁′]. Hence

\[
 L_\Phi=\ell_1+\frac{R'}{1+R},\qquad
 L'_\Phi=\ell'_1+\frac{R''}{1+R}-\left(\frac{R'}{1+R}\right)^2.
 \tag{T10}
\]

For x≥3,n≥2, elementary inequalities give

    0<Rₙ≤2n⁴ exp[−(n²−1)x],
    |Rₙ′|≤10n⁶ x exp[−(n²−1)x],
    |Rₙ″|≤100n⁸ x² exp[−(n²−1)x].

For completeness, (2n²x−3)/(2x−3)≤2n²; also
ℓₙ−ℓ₁=−4(n²−1)x[1+6/((2n²x−3)(2x−3))], whose absolute value
is at most 5n²x. The two curvature corrections are respectively <3
and ≤32, so |ℓₙ′−ℓ₁′|≤20n²x since 35<4n²x. Combining them gives
2n⁴(25n⁴x²+20n²x)≤100n⁸x². These bounds justify differentiation
by uniform convergence on compact intervals (indeed their majorants
are summable uniformly for all u≥0).

For p≤2, x^p exp[−(n²−1)x] decreases on x≥3. Successive n-majorants
have ratio ≤(3/2)^8 exp(−15)<1/2. The omitted n≥13 terms therefore
have absolute errors bounded by

    E₀=4·13⁴ exp(−504),
    E₁=60·13⁶ exp(−504),
    E₂=1800·13⁸ exp(−504).

The zeroth error is nonnegative; the other two may be enclosed
symmetrically. Arb at 120 decimal digits encloses n=2,…,12 and these
tails on 1024 entire dyadic cells [i/1024,(i+1)/1024]. All parameter
caps from Section 3 are used simultaneously on every u cell. Compute

    Lν=LΦ+2λu+4μu³+6νu⁵,
    Lν′=LΦ′+2λ+12μu²+30νu⁴,
    r=−f′/f+4κ+λ′u²+μ′u⁴+u⁶+κuLν,
    rᵤ=2λ′u+4μ′u³+6u⁵+κ(Lν+uLν′).

The largest recorded Arb upper endpoint of r+κ+a₀|rᵤ| is
−0.0217069792118474299… (cell 461). A separate dyadic rational checker
reconstructs the operations using the recorded transcendental
intervals as explicit inputs and proves an upper bound <−0.0217
on every cell. Its entire outward rounding error is retained, including
tiny exponential errors enlarged to the 2⁻⁵¹² grid. These are interval
covers, not point samples. This proves T8 for 0≤u≤1.

## 5. The full infinite tail u≥1

Here x≥πe⁴>150. The preceding summand bounds and ratio estimate give

    R<64e⁻⁴⁵⁰,   |R′|<192000e⁻⁴⁵⁰,
    |R″|<1152000000e⁻⁴⁵⁰.

All three are <1/4, as checked by a positive finite Taylor lower bound
for exp(450). Therefore |(log(1+R))″|<1. Also ℓ₁<10−4x,
|ℓ₁|<4x, and 96x/(2x−3)²<1. Each Rₙ′<0, so R′<0 and

    LΦ≤10−4x,  |LΦ|≤4x+1,  |LΦ′|≤16x+2.

Set H=1/64. Since −4<λ<0, 0<μ<9, −H≤ν≤0,

    Lν≤10−4x+36u³<0,
    |Lν|≤4x+1+8u+36u³+6Hu⁵,
    |Lν′|≤16x+10+108u²+30Hu⁴.

The strict negative sign follows from e^{4u}>50u³ for u≥1
(the ratio increases there and e⁴>50), so x>150u³.
Let k₋=.00259,k₊=.00260, l=.3264,m=.2942,F=.0437 and
k̄=k₋−5a₀k₊>0. Using the negative sign of Lν with the lower κ bound,
and the absolute derivative estimate with the upper κ bound, gives

\[
 r+\kappa+a_0|r_u|\le P_6(u)-4\bar k\,\pi u e^{4u}=:Q(u),
 \tag{T11}
\]

where the coefficients of P₆, in increasing degree, are exactly

    [−F+5k₊+a₀k₊,
      10k₋+a₀(2l+18k₊),
      l,
      a₀(4m+144k₊),
      m+36k₋,
      a₀(6+36Hk₊),
      1].

For example the exponential derivative terms use
−4k₋ux+a₀k₊(4+16u)x≤−4k̄ux for u≥1. All positive-degree
coefficients are positive. If S=Σ_{j=1}⁶jPⱼ, then P₆′(u)≤Su⁵.
To verify (1+4u)e^{4u}>270u⁵ for u≥1, set z=u−1≥0 and use
e⁴>109/2 and the first six Taylor terms of exp(4z). The polynomial

    (109/2)(5+4z) Σ_{j=0}⁵(4z)^j/j! − 270(1+z)⁵

has its first three coefficients 5/2,−42,352. Their quadratic is
strictly positive because 4(5/2)352−42²>0; all higher coefficients
are positive. These inequalities are checked in exact rational
arithmetic. Consequently

    Q′(u) < [S−4k̄·3·270]u⁵ < 0.

Finally π>157/50 and e⁴>109/2 imply πe⁴>170, and

    Q(1) < ΣPⱼ−4k̄·170 = −0.051116612396240234375 < −1/50.

Thus Q(u)<−1/50 on the entire u≥1 half-line, completing T8.
No numerical cutoff replaces the infinite tail.

## 6. From feasible transport to the actual value

Choose an attained minimizer g₂ in T2 at ν₂. R30 supplies attainment,
its amplitude bound U, and integrability; no differentiable selection
of optimizers is required. By T6, the transported g₁ is feasible at
ν₁. By T9 its Lipschitz constant is at most e^{−cd}M<M and
its amplitude is at most e^{−cd}δ_{ν₂}(M)/η. Therefore
δ_{ν₁}(M)≤e^{−cd}δ_{ν₂}(M)/η, which is T3. Positivity of
δ_{ν₁} and κ makes the ordering strict.

Integrating −τ′/τ≥.00259 proves η≥exp(.00259d). Use
exp(x)−1≥x, δ_{ν₁}>9.17×10⁻¹⁰, and
9.17×10⁻¹⁰·.02259=2.071503×10⁻¹¹>2.07×10⁻¹¹ to obtain T4.
The transformed amplitude remains below one, so 1−g₁ remains positive.
This does not by itself certify any additional rank condition for an
A₄ singularity of every modified kernel.

## 7. What was and was not resolved

R30's value comparison lost resolution at very small d because it
subtracted two endpoint remainder bounds. T3 resolves actual-value
ordering for every d>0 on the stated arc and budget range. It neither
computes δ_ν(M) exactly nor differentiates its remainder. The earlier
R30 two-sided quantitative comparisons remain valid and can be sharper
for a fixed nonzero separation.

Still open here: monotonicity at arbitrarily close drivers of
Z_M(ν)=M⁴[δ_ν(M)−δ₀(ν)−C₂(ν)/M²]; differentiability of δ_ν(M);
uniqueness/smoothness of its optimizer; a ν-derivative of the M⁻⁶
remainder; C₆; extension to M<M₀ or the whole [−29,0] arc; a single
common profile or fixed target for all ν; physical measurements.

Weighted composition and characteristic comparison are existing tools.
The current contribution under investigation is their explicit use to
preserve these moments and certify ordering in this particular family.
No priority, optimality of constants, publication acceptance, formal
verification or independent expert approval is claimed. See
[LITERATURE.md](LITERATURE.md) for the limited background check.
