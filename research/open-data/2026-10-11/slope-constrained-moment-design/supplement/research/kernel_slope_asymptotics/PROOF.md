# R15 — Sharp cost of a finite slope bound

21 September 2026. Analytic proof draft with verified numerical hypotheses.
This is not a proof-assistant formalization or an external referee report.
The quantity called cost is the maximum relative multiplier amplitude,
not computational effort, money, or a physical energy.

## 1. Problem and a theorem for weighted moment designs

On the half-line let dρ=w(u)du with w>0. Let p₀,…,pₘ be real
functions with ∫|pⱼ|dρ<∞. Given f>0, impose

    ∫pⱼ h dρ = 0  (j<m),       ∫pₘ h dρ = −f.

Define δ* as the infimum of ∥h∥∞ over bounded measurable h, and δ(M)
as the infimum over bounded Lipschitz h with Lip_u(h)≤M and the same
moments. The domain and original coordinate u are fixed. No additional
mass normalization is imposed. An even extension of h is permitted.

For a∈Rᵐ put rₐ=pₘ−Σaⱼpⱼ and D(a)=∫|rₐ|dρ. Assume there is a
coefficient vector a* such that D*=D(a*)>0 and

    ∫pⱼ sign(r*) dρ = 0,       j<m,       r*=rₐ*.

Then δ*=f/D*: the bound f=|∫r*h dρ|≤∥h∥∞D* applies to all feasible h,
and h*=−(f/D*)sign(r*) attains it. The sign moments also say that a*
minimizes the convex objective D when r* has a zero set of measure zero.

Assume further:

1. w and pⱼ are C² locally, r*(0)≠0, and all positive zeros zₖ of r*
   are simple. The signed set {±zₖ} is uniformly separated by d>0.
   A finite nonempty zero set is also allowed.
2. For qⱼ=w pⱼ and some b>0, with neighborhoods inside (0,∞),
   Σₖ sup_{|u−zₖ|≤b}|qⱼ^(l)(u)|<∞ for l=0,1,2 and j=0,…,m.
   In particular Γ=Σₖ w(zₖ)|r*′(zₖ)| is finite and positive.
3. There are m selected zeros for which the matrix (pⱼ(zₖ))_{j<m,k}
   is nonsingular.

The conclusion is

    δ(M) = δ* + C*/M² + o(M⁻²),       M→∞,
    C* = δ*³ Γ/(3D*) = δ*⁴ Γ/(3f) > 0.                 (1)

This is a theorem about the stated class of moment problems, subject to
the displayed hypotheses. It does not assert that every positive
integral kernel has simple switches or the required rank. Priority of
this formulation has not been established.

## 2. Sharp lower estimate

For every feasible h with δ=∥h∥∞, dual equality gives the exact identity

    (δ−δ*)D* = ∫ |r*| [δ + sign(r*)h] dρ.              (2)

The integrand is nonnegative. Take any finite collection of distinct
simple zeros and disjoint neighborhoods [zₖ−bₖ,zₖ+bₖ]. On each, let
cₖ=(inf w)(inf |r*′|)>0. For v∈[0,bₖ], |r*(zₖ±v)|w(zₖ±v)≥cₖv.
The two signs of r* are opposite, and Lipschitz continuity implies

    [δ+sign(r*(zₖ+v))h(zₖ+v)]
    +[δ+sign(r*(zₖ−v))h(zₖ−v)] ≥ 2δ−2Mv.

For sufficiently large M put ℓ=δ*/M≤min bₖ. Since δ≥δ*, the
contribution to (2) from this pair of half-neighborhoods is at least

    ∫₀^ℓ cₖ v(2δ*−2Mv)dv = cₖ δ*³/(3M²).            (3)

The estimate holds for every feasible h, hence also for the infimum.
First take liminf M²(δ(M)−δ*), then shrink the finitely many
neighborhoods so that cₖ→w(zₖ)|r*′(zₖ)|. Finally increase the finite
collection. Monotone convergence of the positive series yields

    liminf M²(δ(M)−δ*) ≥ δ*³ Γ/(3D*).                 (4)

An approximate dual residual cannot simply replace r* in (2). Its
baseline f/D(a₀) differs from δ*, and a fixed baseline error eventually
dominates M⁻². R15 explicitly localizes an exact optimizer for this reason.

## 3. Linear transitions and exact moment correction

Write s*=sign(r*), extended evenly to R. Move only the m selected
positive switch centers to c=(c₁,…,cₘ), reflecting their negatives;
leave all other switches fixed. Denote the resulting bounded step
function by s_c. Its jump at zₖ is dₖ=2 sign(r*′(zₖ)). For a>0 set

    s_{c,a}(u) = (1/(2a)) ∫_{−a}^a s_c(u−v)dv.

For c sufficiently near the selected zeros and a sufficiently small,
the transition intervals are disjoint and avoid the origin. Therefore
|s_{c,a}|≤1; every transition is a linear ramp with slope magnitude
1/a; plateaus of magnitude one remain. Thus ∥s_{c,a}∥∞=1 and
Lip(s_{c,a})=1/a. Reflection introduces no boundary transition at 0.

For a single unit upward step centered at c, its smoothing error
against any C² density q is exactly

    I_q(c,a) = −(a/2) ∫₀¹(1−v)[q(c+av)−q(c−av)]dv
             = −a² q′(c)/6 + o(a²).                 (5)

The expression extends evenly and C² to negative a and a=0. The
summability assumptions justify summing the errors and their first
two a-derivatives over infinitely many switches. Indeed the second
derivative is bounded by a constant times the local supremum of
|q′|+|a q″|, with a bound independent of the switch index. The finite
center variables cause no additional infinite sum. We use local
differences of step functions, not an unjustified interchange of a
conditionally convergent infinite sum of step tails.

Define Sⱼ(c,a)=∫qⱼ s_{c,a}. At c=z_selected,a=0 the first m Sⱼ vanish.
The center Jacobian has entries

    ∂Sⱼ/∂cₖ = −dₖ qⱼ(zₖ).

It is nonsingular by assumption 3 and w(zₖ)>0. The finite-dimensional
implicit-function theorem supplies C² centers c(a) with Sⱼ(c(a),a)=0
for all j<m. Evenness in a and local uniqueness imply c(−a)=c(a), so
c(a)=z_selected+O(a²). These are exact moment identities, not numerical
residual tolerances.

Now use q_r=w r*. At every switch q_r(zₖ)=0 and
dₖ q_r′(zₖ)=2w(zₖ)|r*′(zₖ)|. The finitely many O(a²) center movements
change the unsmoothed residual moment by O(a⁴), because its first
center derivative vanishes there. Applying (5) to all switches gives

    ∫q_r s_{c(a),a} = D*−Γ a²/3+o(a²).

Since the first m moments are exactly zero, the left side is also
Sₘ(c(a),a). Thus, for all small positive a, set

    α(a)=f/Sₘ(c(a),a),       h_a=−α(a)s_{c(a),a}.

All m+1 constraints hold, ∥h_a∥∞=α(a), Lip(h_a)=α(a)/a, and

    α(a)=δ*+δ*Γ a²/(3D*)+o(a²).                      (6)

The function α is C² and α′(a)=O(a). Consequently α(a)/a is strictly
decreasing for small a>0 and tends to infinity. For every sufficiently
large M one can choose a=a(M) with α(a)/a=M; then
a(M)=δ*/M+O(M⁻³). Inserting this in (6) proves the matching limsup
inequality in (4), and therefore (1).

The constructed ramps are Lipschitz, not C∞. Formula (1) is about the
closed Lipschitz problem. For the present theta example the R13
equality of infima transfers the value to smooth positive exact-order-
four, rank-three designs; it does not give a smooth minimizer or an
exact description of any finite-M optimizer. If δ*<1, the large-M
construction itself also keeps 1+h_a positive.

## 4. Application at the original exact cusp Q

Use the exact R01 cusp Q=(τ,λ_Q,μ_Q,0), not just its printed midpoint:

    τ≈41.4003413586842508894,
    λ_Q≈−3.64569206160491909881,
    μ_Q≈8.33512049891860723771.

Here m=3,

    Φ(u)=Σ_{k≥1}(2π²k⁴e^(9u)−3πk²e^(5u)) exp(−πk²e^(4u)),
    w(u)=Φ(u) exp(λ_Q u²+μ_Q u⁴),
    pⱼ(u)=(2u)^j cos(2τu+jπ/2),      f=f₃=∫p₃dρ>0.

Each theta summand is positive for u≥0. The exact Q conditions give
f₀=f₁=f₂=0. The multiplier Φ_h=Φ(1+h) is independent of all moving
controls. In particular the design still aims at the same zero location.

### 4.1 Exact dual optimizer localization and uniqueness

The R12 central vector a₀ is exact dyadic data, approximately
(−0.00011726865882510123409,−0.06467975949223486731,
0.00388087037678106362010). Let R=2⁻⁴⁰. All checks are uniform on the
coordinate cube a₀+[-R,R]³ and the exact-Q parameter enclosure.

There are 28 disjoint zero boxes in [0,1], with opposite endpoint signs
and derivative bounded away from zero; 113 sign leaves cover the
complement. This holds for every a in that cube. Contracting the boxes
about the fixed old knots uses the real mean-value identity
z−b=−rₐ(b)/rₐ′(ξ). Only strict improvements are accepted; a proposal
equal to the current radius is discarded, retaining the proved box.
This is a radius contraction argument, not an unsupported assertion
of convergence of point Newton iterations.

Let w₁ be the positive k=1 theta term times exp(λ_Q u²+μ_Q u⁴).
Restrict ∫|rₐ|w₁ to the 28 fixed coarse zero neighborhoods. Its Hessian is

    H(a)=2 Σ_{k=1}^{28} w₁(zₖ(a)) p(zₖ(a))p(zₖ(a))ᵀ/|rₐ′(zₖ(a))|,
    p=(p₀,p₁,p₂)ᵀ.

The rest of D is convex: it is the integral outside these neighborhoods
plus the nonnegative density w−w₁ inside. The three leading principal
minors of H−(1/200)I are uniformly positive by interval enclosure and
an independent rational determinant calculation. Thus D is strongly
convex with modulus m₀=1/200 on the cube.

The gradient ∇D(a₀)=−∫p sign(rₐ₀)dρ is bounded using inherited step
moments, separately contracted central roots, and a full infinite-tail
bound. The certificate gives

    ∥∇D(a₀)∥₂ ≤ ∥∇D(a₀)∥₁ < 2.065×10⁻¹⁶,
    m₀ R−2∥∇D(a₀)∥₁ > 4.1345×10⁻¹⁵ > 0.

Therefore D(a)>D(a₀) on the Euclidean sphere |a−a₀|₂=R. The minimum
over that closed ball is interior; convexity makes it a global minimum.
Strong convexity on the ball and convexity on every segment to any
other minimizer make it the unique global minimizer a*. The first-order
sign moment equations hold there. This establishes uniqueness of a*
for this example, not uniqueness of a finite-M primal minimizer.

### 4.2 All remaining roots, separation, and convergence of the series

Write rₐ=A sin(2τu)+B cos(2τu), where A=8u³+2a₁u and B=4a₂u²−a₀.
On the entire coefficient cube, |a₀|<1/1000, |a₁|<1/10, |a₂|<1/200.
For u≥1, A>7u³ and θ=atan(B/A) is well defined. Exact differentiation gives

    AB′−BA′ = −32a₂u⁴+(8a₁a₂+24a₀)u²+2a₀a₁.

It follows that |θ′|≤1/(200u²). Because 41<τ<42, the total phase
2τu+θ(u) has derivative between 81 and 85. It tends to infinity.
Hence all tail zeros are simple, consecutive tail roots are separated
by at least π/85>3/85, and there are no other types of tail zeros.
The finite root boxes, the gap from the last one to 1, and reflection
about zero supply a uniform signed-root separation d=1/200.

For completeness, theta derivatives satisfy, for u≥0,

    |Φ| ≤ C₀ exp(9u−πe^(4u)),        C₀=4π²+6π,
    |Φ′|≤ C₁ exp(13u−πe^(4u)),       C₁=60π²+30π+16π³,
    |Φ″|≤ C₂ exp(17u−πe^(4u)),       C₂=660π²+150π+448π³+64π⁴.

To verify these, put x=πk²e^(4u) and differentiate the summand
πk²e^(5u)e^(−x)(2x−3) with the polynomial operator
T(P)=(5−4x)P+4xP′. The first two derived polynomials are
−15+30x−8x² and −75+330x−224x²+32x³. For each positive absolute
monomial, the ratio of successive k terms is at most 256e^(−3π)<1/2;
twice its first term bounds the sum. The polynomial identities are
checked separately with exact rational arithmetic.

Derivatives of w pⱼ through order two are therefore bounded by a
polynomial times exp(17u+μ_Q u⁴−πe^(4u)). Uniform root separation and
this eventual superexponential decay imply the local-supremum
summability in assumption 2. This handles infinitely many switches;
we have not replaced the half-line problem by a cutoff problem.

For a quantitative tail, |rₐ′(u)|<900u³ on u≥1. Thus each contribution
to Γ is at most W(u)=900 C₀ u³ exp(9u+μ_+u⁴−πe^(4u)). The logarithmic
derivative is ≤−c, c=4πe⁴−12−4μ_+>0. One uses e^(4u)≥e⁴u³ for
u≥1. Since c(3/85)>16 and e⁴>50,

    Γ_{u≥1} ≤ W(1)/(1−50⁻⁴) < 5.705×10⁻⁶³.

Full densities at the finite roots use 12 theta terms and an explicit
pointwise omitted-series enclosure. For k≥13 the absolute summand
ratio is less than 1/2; the error is bounded by twice the first omitted
absolute term, using left/right interval endpoints in each exponent.

### 4.3 Switch rank, coefficient and geometric interpretation

The first three switch evaluations have determinant approximately
5.30861×10⁻⁶, with a certified enclosure excluding zero. Thus the
moment-correcting implicit function in section 3 applies. Using the
R12 rigorous bracket

    0.00000000091787079603827 < δ* < 0.00000000091787079608363

and the exact-Q f₃ enclosure yields the independent rational bounds

    1.297542117 < Γ < 1.297542121,
    9.20340371×10⁻²⁵ < C* < 9.20340375×10⁻²⁵,
    1.002690547×10⁻¹⁵ < C*/δ* < 1.002690552×10⁻¹⁵.

The sign-optimal limiting kernel also has g₄<0 and control determinant
g₄(g₄g₇−g₅g₆)/4096<0, approximately −4.249937771×10⁻⁴⁰. These are
obtained from inherited moments with new root-displacement and tail
error enclosures. As a→0 the constructed h_a converge to h* except at
the switches and are uniformly bounded. Dominated convergence for
moments through order eight preserves both nonzero quantities for all
sufficiently small a. This gives exact fourth order and control rank
three for the eventual ramp designs. No explicit onset is calculated.

The switches zₖ are zeros of a dual residual used in optimization. They
are not new zeros of the original integral F. The R10 finite 0/2/4-root
window belongs to another fixed kernel and is not transferred here.

## 5. A finite-M inequality independent of a remainder estimate

The true a* is enclosed, so the loss bound (3) can also be applied on
fixed expanded neighborhoods about all 28 finite switches. Each covers
the root uncertainty plus radius 2⁻¹⁴. Let L be the displayed lower
bound for δ*. For every M≥0.00002, ℓ=L/M<2⁻¹⁴ and the neighborhoods
remain disjoint. Summing positive lower density/derivative products
and using 1/D*=δ*/f₃ gives

    δ(M)−δ* > (9.13976214×10⁻²⁵)/M²,      M≥0.00002.   (7)

This is a genuine finite-budget lower inequality about δ*, not a use
of o(M⁻²) as an error bound. It does not supply a matching finite-budget
upper remainder. In particular (1) predicts an excess near
2.30085×10⁻¹⁵ at M=0.00002, but that number is not certified as the
actual excess at that budget. The unchanged R14 two-sided interval
remains the finite-M result there.

## 6. Evidence and limits

[Arb certificate](results/asymptotic_certificate.json),
[rational reconstruction](results/asymptotic_check.json),
[separate roots/quadrature](results/coefficient_crosscheck.json), and
[exact algebra](results/algebra_check.json) accompany the proof.

The rational checker trusts local transcendental and inherited integral
enclosures and verifies the arithmetic implications independently.
The mpmath check is numerical corroboration at central parameters and
two precisions, not a rigorous optimizer enclosure. The analytic
argument above, the applicability assumptions, and the interpretation
of prior certificates remain explicit parts of the proof to review.

No explicit finite-M remainder, optimal finite-M shape, physical
realization, mass-conserving variant, universal higher-order exponent,
or literature priority has been established in this package.
