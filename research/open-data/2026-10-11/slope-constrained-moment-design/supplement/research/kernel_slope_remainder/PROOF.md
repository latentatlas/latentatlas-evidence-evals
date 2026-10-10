# R16 — A uniform quantitative remainder for the large-slope law

21 September 2026. Analytic proof draft with certified derivative
enclosures and independent arithmetic checks. No external review or
proof-assistant formalization is claimed.

## 1. Statement at the same exact Q

All objects are those of [R15](../kernel_slope_asymptotics/PROOF.md):
qⱼ=w pⱼ, j=0,…,3; q_r=w r*=q₃−Σa*ⱼqⱼ; the exact optimal
residual r*; its simple positive zeros zₖ; D*=∫|r*|dρ;
δ*=f₃/D*; and Γ=Σw(zₖ)|r*′(zₖ)|. Put

    C*=δ*³Γ/(3D*)=δ*⁴Γ/(3f₃),
    e(M)=δ(M)−δ*.

The moment target, original coordinate u, amplitude cost, and absence
of a mass-normalization constraint are unchanged. Then for **every**
M≥M₀=0.00002,

    C*/M² − (9.624×10⁻³³)/M³
       < e(M) <
    C*/M² + (2.167×10⁻³²)/M³.                         (1)

These are explicit inequalities about the true δ* and C*, not about
an approximate numerical baseline. The rounded constants have strict
slack over the computed bounds; replacing < by ≤ is also valid.

Using C*>9.20340371×10⁻²⁵ gives

    | e(M)/(C*/M²) − 1 | < 0.001178 (M₀/M).           (2)

The relative error is about the small excess e(M), not about the
whole kernel, its mass, or the total amplitude δ(M). At M₀ it is less
than 0.1178 percent. No optimality of the remainder order M⁻³ is claimed.

## 2. Quantitative data and their meaning

Let a₀=2⁻¹⁴ be a maximum transition half-width. Move only the first
three positive switch centers, writing

    cₖ=zₖ+a²vₖ,       |vₖ|≤Vₖ,       V=(512,768,384),
    0<a≤a₀.

Reflect the centers to negative u for an even step template and
convolve that template with the uniform density on [-a,a]. All
transitions are disjoint and avoid 0. On the positive half-line this
gives a bounded piecewise linear sign profile s_{c,a}, of norm one
and Lipschitz constant 1/a. Negative switches do not intersect the
positive half-line transition neighborhoods and are not counted twice.

Let Uₖ contain the exact zₖ and the radius a₀+a₀²Vₖ when k≤3,
or radius a₀ otherwise. The finite enclosures include all R15 root
uncertainty. Write

    Q_{jlk} = sup_{Uₖ}|qⱼ^(l)|,
    R_{lk}  = sup_{Uₖ}|q_r^(l)|.

The certificate bounds all finite terms and the full infinite tails.
In particular set

    B₂=Σₖ R_{2k},       A₃=B₂/12,
    A₄=Σ_{k=1}³ [R_{1k}Vₖ² + R_{2k}Vₖ/3].          (3)

Readable computed values are

    B₂ < 59.125014562,
    A₃ < 4.927084547,
    A₄ < 132801.204.

The numerical definitions in the certificate, not these abbreviated
values, are used to compute the final constants.

## 3. A uniform moment-correcting fixed point

Let dₖ=2 sign(r*′(zₖ)); for the first 28 switches dₖ=−2(−1)^(k−1).
Use Sⱼ(c,a)=∫qⱼ s_{c,a}. The exact sign optimum gives Sⱼ(z,0)=0,
j=0,1,2. For a single unit upward step and any C² q,

    I_q(c,a)=−(a/2)∫₀¹(1−t)[q(c+at)−q(c−at)]dt,
    |I_q(c,a)+a²q′(c)/6| ≤ a³ sup|q″|/24.            (4)

The last inequality follows by Taylor expansion on each side of c:
the difference from 2at q′(c) is bounded by a²t² sup|q″|, and
(1/2)∫₀¹(1−t)t²dt=1/24. All jumps have magnitude two.

Let J_{jk}=−dₖqⱼ(zₖ) for the first three switches. Define
Fⱼ=(1/6)Σₖdₖqⱼ′(zₖ). Its infinite tail is enclosed absolutely.
Then

    |Sⱼ(z,a)/a²+Fⱼ| ≤ (a/12)ΣₖQ_{j2k}.              (5)

Choose the exact dyadic 3×3 preconditioner B recorded in the
certificate, and the weighted maximum norm
∥v∥_V=maxₖ|vₖ|/Vₖ. On ∥v∥_V≤1 consider

    T_a(v)=v−B S_{0:2}(z+a²v,a)/a².                 (6)

Here S is the true infinite-half-line moment vector at exact Q and a*.
No floating-point residual is substituted for its defining identities.

The exact center derivative is

    ∂Sⱼ/∂cₖ = −dₖ (1/(2a))∫_{cₖ−a}^{cₖ+a}qⱼ(u)du.

The symmetric average differs from qⱼ(cₖ) by at most a²Q_{j2k}/6;
qⱼ(cₖ) differs from qⱼ(zₖ) by at most a²VₖQ_{j1k}. Thus on the
entire box, uniformly in 0<a≤a₀,

    |∂Sⱼ/∂cₖ−J_{jk}|
        ≤ 2a₀²[VₖQ_{j1k}+Q_{j2k}/6] = Δ_{jk}.      (7)

Let E=I−BJ and

    κᵢ = Σₖ (|Eᵢₖ|+Σⱼ|Bᵢⱼ|Δⱼₖ)Vₖ/Vᵢ,
    ηᵢ = [|(BF)ᵢ|+(a₀/12)Σⱼ|Bᵢⱼ|ΣₖQ_{j2k}]/Vᵢ.

The separate rational reconstruction verifies

    κ < (0.129747, 0.118233, 0.071040),
    η < (0.397772, 0.406040, 0.324017).

Each κᵢ+ηᵢ<1, so T_a maps the weighted box strictly into itself.
Its Lipschitz constant is at most max κᵢ<1. The contraction theorem
therefore gives, for every 0<a≤a₀, a unique fixed point within this
box, hence centers satisfying S₀=S₁=S₂=0 exactly. This uniqueness
is restricted to this three-center construction and box; it is not
uniqueness of a finite-M optimal multiplier.

The moment maps depend continuously on a. Formula (4) and the
summable derivative bounds extend (6) continuously to a=0. Uniform
contraction implies continuous fixed points v(a): the usual estimate
for two fixed points divides the parameter change in T by 1−max κᵢ.
This supplies a continuous family on [0,a₀].

## 4. Explicit upper loss and budget coverage

Put S_r(c,a)=∫q_r s_{c,a}. For the corrected centers it equals S₃,
because the first three moments vanish. Let L(a)=D*−S_r(c(a),a).
Since |s_{c,a}|≤1, L(a)≥0.

At a switch q_r(zₖ)=0. Moving its center by a²vₖ changes the
unsmoothed residual moment by at most R_{1k}a⁴Vₖ². The smoothing
leading term in (4) at that moved center differs from the one at zₖ
by at most R_{2k}Vₖa⁴/3. Summing (4) over all switches, using
dₖq_r′(zₖ)=2w(zₖ)|r*′(zₖ)|, gives

    0≤L(a)≤Γa²/3+A₃a³+A₄a⁴.                        (8)

Every term in (3) includes its infinite tail. This is a quantitative
inequality for all 0<a≤a₀, not an asymptotic Taylor equality.

Let L_δ,U_δ be the inherited R12 bounds on δ*, and put

    D_min=f₃_lower/U_δ,
    E₀=Γ_upper a₀²/3+A₃a₀³+A₄a₀⁴,
    U_bar=U_δ/(1−E₀/D_min).

The recorded outward-rounded constants verify E₀<D_min,
U_bar<1 and U_bar/a₀<M₀. Hence

    α(a)=f₃/S₃(c(a),a),       h_a=−α(a)s_{c(a),a}

is well defined, satisfies all four moments exactly, and has

    δ*≤α(a)≤U_bar,
    ∥h_a∥∞=α(a),       Lip(h_a)=α(a)/a,
    1+h_a>0.

The function α(a)/a is continuous, tends to infinity as a→0, and at
a₀ is less than M₀. The intermediate value theorem therefore supplies
at least one a∈(0,a₀) for **each** M≥M₀ with α(a)/a=M. Monotonicity
of this function is not needed for this coverage argument.

Fix such a design and let e_a=α(a)−δ*. The identity
D*e_a=α(a)L(a), together with a=α/M, yields

    D*e_a≤Γα³/(3M²)+A₃α⁴/M³+A₄α⁵/M⁴.

Use α³−δ*³=e_a(α²+αδ*+δ*²)≤3U_bar²e_a and C*=Γδ*³/(3D*).
The positive denominator D*−ΓU_bar²/M² can be absorbed. It follows that

    e_a−C*/M² ≤
      [A₃U_bar⁴/M³ + A₄U_bar⁵/M⁴
       + ΓU_bar²C*/M⁴] / [D*−ΓU_bar²/M²].            (9)

Since δ(M)≤α(a), the same upper bound applies to e(M). Replacing
positive quantities by certified upper bounds, D* by D_min, and
1/M by 1/M₀ gives an explicit K₊:

    K₊ = [A₃U_bar⁴+(A₄U_bar⁵+Γ_upper U_bar²C_upper)/M₀]
          /[D_min−Γ_upper U_bar²/M₀²]
       < 2.167×10⁻³².                               (10)

The exact computed denominator is positive. The printed constants in
(1) are conservative bounds on this expression.

## 5. Explicit lower remainder, including all tail switches

For any feasible h of norm δ, set the nonnegative defect
b(u)=δ+sign(r*(u))h(u). As in R15,

    (δ−δ*)D* = ∫|q_r(u)| b(u)du.

On each switch pair zₖ±v, 0≤v≤ℓ=δ*/M<a₀,

    |q_r(zₖ±v)| ≥ γₖv−R_{2k}v²/2,
    b(zₖ+v)+b(zₖ−v) ≥ 2δ*−2Mv ≥ 0,
    γₖ=w(zₖ)|r*′(zₖ)|.

The polynomial weight lower bound may be negative at very remote
tail switches. This causes no sign error: the weighted defect is
nonnegative, hence it is at least

    max(0,γₖv−R_{2k}v²/2)(2δ*−2Mv)
      ≥ (γₖv−R_{2k}v²/2)(2δ*−2Mv).

Integrating the last expression gives

    γₖδ*³/(3M²)−R_{2k}δ*⁴/(12M³).

All neighborhoods are disjoint. The sums of γₖ and R_{2k} converge
absolutely, so summing finite sets and passing to the limit is valid.
Taking the infimum over h and dividing by D*=f₃/δ* gives

    e(M) ≥ C*/M² − δ*⁵B₂/(12f₃M³)
         ≥ C*/M² − K₋/M³,
    K₋=U_δ⁵B₂/(12f₃_lower)<9.624×10⁻³³.             (11)

This step uses the exact optimal residual throughout. There is no
fixed approximate-dual-baseline error that would spoil very large M.

## 6. Derivative and infinite-tail enclosures

The finite computations use 12 theta terms and the first two analytic
u derivatives of the density, enclosed with Arb at 110 digits. With
x=πk²e^(4u), the kernel summand and its first two derivatives are
πk²e^(5u−x)P_l(x), where

    P₀=−3+2x,
    P₁=−15+30x−8x²,
    P₂=−75+330x−224x²+32x³.

The identities were checked in R15. For omitted k≥13, absolute
monomial ratios are less than 1/2 on u≥0, so twice the first omitted
absolute term bounds each derivative tail. Mixed interval endpoints
are used for all positive and negative exponential factors.

For P=λ_Q u²+μ_Q u⁴, -4<λ_Q<0 and 0<μ_Q<9 imply

    |P′|≤44(1+u)³,       |P″|≤116(1+u)².

Let C₀,C₁,C₂ be the R15 kernel derivative-envelope constants. With
E(u)=exp(17u+μ_+u⁴−πe^(4u)), one obtains

    |w|   ≤ W₀ E(u),
    |w′|  ≤ W₁(1+u)³ E(u),
    |w″|  ≤ W₂(1+u)⁶ E(u),
    W₀=C₀, W₁=C₁+44C₀, W₂=C₂+88C₁+2052C₀.

Using 2τ<84, the resulting qⱼ derivative constants are

    T_{j0}=2^j W₀,
    T_{j1}=2^j[W₁+(j+84)W₀],
    T_{j2}=2^j[W₂+2(j+84)W₁+(j(j−1)+168j+7056)W₀].

For j≤3 and l≤2, |qⱼ^(l)(u)|≤T_{jl}(1+u)⁹E(u). Put u₀=1−a₀.
For u≥u₀>3/4 the common envelope has logarithmic derivative at most

    −c = −4πe^(4u₀)+4μ_+u₀³+17+9/(1+u₀).

Indeed e^(4u)/u³ increases there. The certificate checks c(3/85)>16.
The R15 tail switches have spacing at least 3/85, so the sums of
local suprema about every root zₖ≥1 are bounded by

    T_{jl}(1+u₀)⁹E(u₀)/(1−50⁻⁴),

where e⁴>50 supplies e⁻¹⁶<50⁻⁴. The bound for q_r″ combines these
with |a*₀|<1/1000, |a*₁|<1/10, |a*₂|<1/200. These tails enter B₂,
the forcing F and the fixed-point residual; none is discarded.

## 7. Numerical consequence and exact scope

At M₀, independent rational reconstruction of (1), the R12 δ* bounds
and R15 C* bounds gives

    0.00000000091787309568619750
       < δ(0.00002) <
    0.00000000091787309964331750.                      (12)

The displayed interval is over 870 times narrower than the R14
displayed interval. This measures enclosure width, not computational
speed or an improvement to the true mathematical optimum.

The upper construction is an exact, positive, Lipschitz moment design
defined through a rigorously enclosed family of three-center fixed
points. R13 gives the same infimum in the smooth positive exact-order-
four/rank-three class. We do not assert that this ramp is the finite-M
minimizer, that it is C∞, or that its entire finite root window is the
R10 window. The separate numerical ramp reconstruction has numerical
residuals and is only corroboration of the analytic construction.

No second asymptotic coefficient, sharp remainder exponent, finite-M
minimizer uniqueness, new physical application or literature priority
is established here. The manuscript still needs external mathematical
review and a focused comparison with adjacent control-rate literature.

[Certificate](results/remainder_certificate.json),
[independent rational check](results/remainder_check.json),
[separate differentiation](results/derivative_crosscheck.json),
[numerical ramp reconstruction](results/design_crosscheck.json),
[exact remainder factors](results/algebra_check.json).
