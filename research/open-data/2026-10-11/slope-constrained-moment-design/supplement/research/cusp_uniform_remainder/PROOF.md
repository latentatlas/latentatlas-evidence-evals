# R27 — Uniform fourth-order accuracy on a short cusp arc

This proof extends the fixed-Q R26 argument to a closed subarc of the
existing R03 cusp curve. The new issues are the moving cusp, moving
unrestricted dual optimum, the negative sextic weight, and constants
uniform in both the driver and the slope budget. Analytic arguments and
validated numerical inequalities are separate evidence. Neither this
proof nor its inherited chain has been externally refereed or formalized.

## 1. Exact family, targets and statement

Let Q(ν)=(τ(ν),λ(ν),μ(ν),ν) be the exact graph of
[R03](../cusp_connection/PROOF.md), identified there with Q(0)=Q.
Restrict to the exact rational interval

\[
 I=[-2^{-16},0],\qquad h=2^{-16}=0.0000152587890625.
 \tag{U1}
\]

Use the original half-line coordinate u and theta kernel
Φ=Σ_{n≥1}πn²e^{5u}(2πn²e^{4u}−3)e^{−πn²e^{4u}}. At each driver set
w_ν=Φe^{λ(ν)u²+μ(ν)u⁴+νu⁶}, p_j=(2u)^j cos(2τ(ν)u+jπ/2),
q_{j,ν}=w_νp_j and f_ν=∫q_{3,ν}>0. The cusp identities give
∫q_{j,ν}=0 for j<3. Define the pointwise design problem

\[
 \delta_\nu(M)=\inf\{\|g\|_\infty:\operatorname{Lip}g\le M,
   \ \int q_{j,\nu}g=0\ (j<3),\ \int q_{3,\nu}g=f_\nu\}.
 \tag{U2}
\]

Each ν permits its own g; the claim is not existence of one fixed g
meeting all these problems simultaneously. The kernel perturbation is
h_ν=−g. For a chosen ν it is fixed when differentiating that kernel's
integral with respect to its controls.

Let b*(ν) be the unique unrestricted dual minimizer proved below,
q*=q₃−Σb*_j q_j, D_ν=∫|q*| and δ₀(ν)=f_ν/D_ν. At its simple
positive roots z_k let r=q*', t=q*'', u_k=q*''', γ=|r|,
σ=sign r and Q_k=(q_j(z_k))_{j<3}. Define the full infinite sums

\[
 \begin{split}
 \Gamma&=\sum_k\gamma_k,&G&=2\sum_k Q_kQ_k^T/\gamma_k,\\
 B_j&=\frac13\sum_k\sigma_k(q_jt_k/r_k-q'_j),&v&=G^{-1}B,\\
 R&=\sum_k(t_k^2/(36\gamma_k)-\sigma_ku_k/60),&
 \Xi&=R-\tfrac12 B^Tv,\\
 C_2(\nu)&=\frac{\delta_0(\nu)^3\Gamma}{3D_\nu},&
 C_4(\nu)&=\delta_0(\nu)^5\left(\frac{\Gamma^2}{3D_\nu^2}-\frac{\Xi}{D_\nu}\right).
 \end{split} \tag{U3}
\]

All quantities on the right depend on ν. These are not the fixed
coefficients at Q(0) substituted at another point.

**Theorem.** For every ν∈I,

\[
 2.47\times10^{-39}<C_4(\nu)<2.52\times10^{-39}.
 \tag{U4}
\]

For every pair (ν,M)∈I×[2×10⁻⁵,∞), put
P₄,ν(M)=δ₀(ν)+C₂(ν)/M²+C₄(ν)/M⁴. Then

\[
 -\frac{1.02\times10^{-53}}{M^6}
 <\delta_\nu(M)-P_{4,\nu}(M)
 <\frac{1.64\times10^{-53}}{M^6}.
 \tag{U5}
\]

In particular δ_ν(M)>δ₀(ν)+C₂(ν)/M² throughout this product domain.
This is a uniform O(M⁻⁶) remainder on this subarc. The onset and arc
length are sufficient bounds, not asserted optimal. A C₆ coefficient,
monotonicity of C₄, or extension to the full R03 interval [−29,0]
does not follow.

## 2. Transporting the exact cusp and its moment target

The first R03 cell covers [−1/2,0] and gives a uniform velocity box V⁰
for (τ',λ',μ'). Because the exact Q(0) is already identified,
Q_i(ν)−Q_i(0)∈νV⁰_i. This anchors the new arc to the original exact
point; there is no identification by nearby floating-point coordinates.

The R09 original-kernel data enclose D_n=∂_t^nF at exact Q(0) through
order 54 and positive absolute moments B_n through order 58. The latter
hold for |Δλ|≤2⁻¹⁰ and |Δμ|≤2⁻¹⁷ at ν=0. They also hold at
ν≤0, since e^{νu⁶}≤1. Every straight parameter segment below stays
inside these λ,μ bounds and in the negative ν half-space.

For offsets Δ=(Δτ,Δλ,Δμ,ν) use the commuting operator

\[
 L_\Delta=\Delta\tau D_t-\Delta\lambda D_t^2/4
                  +\Delta\mu D_t^4/16-\nu D_t^6/64.
 \tag{U6}
\]

Taylor expansion through total degree five has remainder at order six
bounded by Σ_m |[D_t^m]L_Δ⁶| B_{n+m}/6!. Coarse offsets νV⁰ enclose
D₀,…,D₈. At actual cusp points, the exact cusp identities yield

    μ'=D₆/(4D₄),
    λ'=(4D₅μ'−D₇)/(16D₃),
    τ'=(D₈/64+D₄λ'/4−D₆μ'/16)/D₃.

These give a tighter velocity box V¹. Integrating it on the same whole
subarc gives new offsets νV¹. Applying U6 again encloses D₀,…,D₉,
including f_ν=D₃. Recorded numerical enclosures imply, uniformly,

    −0.107402<τ'<−0.107375,
     0.326200<λ'< 0.326224,
     0.294035<μ'< 0.294042,
     3.335610×10⁻¹³<f_ν<3.335649×10⁻¹³.

The velocity formulas are applied only on the proved cusp, where the
first three moments vanish exactly. Taylor boxes also contain noncusps;
no exact-zero identity is imposed on those other points.

## 3. Uniform L¹ perturbation and moving sign moments

Let E_j bound the L¹ difference q_{j,ν}−q_{j,0}. With componentwise
offset bounds d_t,d_λ,d_μ,d_ν, the integral mean-value estimate gives

\[
 E_j=d_tB_{j+1}+d_\lambda B_{j+2}/4
                   +d_\mu B_{j+4}/16+d_\nu B_{j+6}/64.
 \tag{U7}
\]

This includes the whole half-line; no oscillatory cancellation is
assumed in these absolute estimates.

Keep the exact dyadic dual center b⁰ from R15. The raw residual
r_b=p₃−Σb_jp_j depends on τ and b, while its positive weight depends
on λ,μ,ν. For current τ and b=b⁰, bracket its 28 roots near the old
ones, verify signed derivatives, and contract each bracket by the
mean-value formula. Let J_k contain both the old and current k-th
roots. The complete sign cover and the tail phase description below
show that the only finite-domain sign differences occur in these J_k.
Thus the j-th component of the dual gradient at b⁰ satisfies

    |∂_j D_ν(b⁰)| ≤ g_j^old + E_j
                 +2Σ_{k≤28}|J_k| sup_{J_k}|q_{j,ν}|
                 +2∫₁^∞|q_{j,ν}|.

The old gradient bounds are those at the exact Q(0), not at its decimal
center. The last integral covers every possible sign difference beyond
1, even when the phase shift accumulates over infinitely many roots.

## 4. Uniform continuation of the exact unrestricted dual

Use R24's exact dyadic approximate Gram inverse C. The initial coefficient
box is b⁰+diag(R_b)[−1,1]³ with

    R_b=(2⁻²²,2⁻¹⁸,2⁻¹⁶).

For every cusp parameter in the enclosing box, bracket and contract
all 28 roots uniformly over this whole coefficient box. A 354-leaf
interval partition covers their complement in [0,1]. The signs alternate
with the same orientations. After 1 the R26 phase representation applies:
T>7u³, 81<φ'<85, separation >3/85, and |r'_b(z)|>567z³. Its validity
depends on 41<τ<42 and |b|<(.001,.1,.005), verified here.

The exact Hessian of the convex dual objective D_ν(b)=∫|q_b| is
G_ν(b)=2ΣQ_kQ_k^T/γ_k. Its finite part is evaluated over all root
and parameter boxes; the whole infinite tail is retained. Differentiation
is justified by simple roots, phase control and the uniform summable
theta envelopes. The new signed weight remains strictly positive.

For T_ν(b)=b−C∇D_ν(b), in the scaled max norm the computation gives

\[
 q_i<(.025586,.038809,.026084)_i,\qquad
 \eta_i<(.131538,.154021,.134816)_i,
 \quad q_i+\eta_i<1.
 \tag{U8}
\]

Hence every T_ν maps the box into itself and is a contraction, with
invertible C. Its fixed point b*(ν) has zero sign moments. Positive
Gram principal minors give strict local convexity; global convexity
then makes this the unique global dual minimizer. If another minimizer
existed, the connecting segment would contradict strict convexity near
the first one. The old b*(0) lies in this box and is the same object
by uniqueness.

The fixed point lies in the smaller box with radii
R_b·η_max/(1−q_max), whose factor is <0.160239. Roots and coefficient
jets are freshly recomputed on this smaller box. The first three
evaluation vectors also remain independent, as verified in the moment
repair below. Uniform contraction and dominated convergence imply
continuous dependence on ν; no derivatives of an infinite vector of
optimal transition centers are presumed.

## 5. The dual objective and coefficient enclosures

L¹ perturbation gives a useful estimate without numerically subtracting
two oscillatory objective integrals. Optimality at each endpoint implies

\[
 |D_\nu-D_0|\le E_3+\sum_{j<3}
       \max\{|b_j^*(0)|,|b_j^*(\nu)|\}E_j.
 \tag{U9}
\]

For the upper inequality evaluate the new objective at b*(0); for the
lower evaluate the old one at b*(ν). The b-box bounds both choices.
U9 and U6 enclose D_ν and f_ν, hence δ₀(ν)=f_ν/D_ν.

The 28 finite root contributions to Γ,G,B,R use full derivatives of
w_ν through the required order. The potential derivatives include νu⁶.
At exact roots, r_b(z)=0 removes the appropriate product terms; it is
not imposed away from a root. Gram solve error is validated with the
residual bound

    ||v−v⁰||∞ ≤ ||C(B−Gv⁰)||∞/(1−||I−CG||∞),

where v⁰ and C are recorded exact dyadic candidates. The calculation
gives |v|<(5,4,180). All infinite root contributions are included as
in Section 6. Interval evaluation of U3 gives U4. A separate outward
rational reconstruction also lies strictly inside the published U4 bounds.

## 6. Why the sextic term preserves the required tail estimates

For u≥1 and ν∈I, w_ν≤88 exp(9u+9u⁴−πe^{4u}), just as in R26.
Absolute derivatives of the potential satisfy

    |P'|≤44u³+6hu⁵,          |P''|≤116u²+30hu⁴,
    |P'''|≤216u+120hu³,      |P''''|≤216+360hu²,
    |P'''''|≤720hu.

The maximum of u⁵e^{−4u} on u≥1 is (5/4)⁵e^{−5}<1/40.
Together with e^{4u}>50u³ this gives |P^(j)|<e^{4ju} for j=1,…,5.
Thus the same Bell/product-rule constants W_j as R26 remain valid;
in particular |w'/w|<135e^{4u}, |w''/w|<3800e^{8u}. This also
justifies reusing R24's Gamma/G/B/R tail bounds.

Set a₀=2⁻¹⁴, ε=2⁻¹². Always keep the first 28 roots and keep a
tail root only if ae^{4z}≤ε. Use b(a,ν)=b*(ν)+v(ν)a² and
c_k=z_k+κ_k a², κ=(Q_k^Tv−q*''/6)/q*'. The slightly enlarged bound
V=(5,4,180) has Σ2^jV_j=733. Exact rational checks show that the
R26 raw derivative/residual constants 550 and 2800, |κ|<46e^{4z},
and signed density derivative >200w(z)z³ still hold on [z−3a,z+3a].
A fresh interval check gives r_b>0 on [1,1.001] for the full expanded
trial box. This handles the first tail root and the junction to the
finite-domain proof.

For inactive roots the R26 elementary estimate remains valid:

\[
 \sum_{ae^{4z_k}>\varepsilon} t_k
 \le(a/\varepsilon)^s\sum_k t_ke^{4sz_k}\quad(t_k\ge0).
 \tag{U10}
\]

Its integral analogue uses the first inactive root and cut L=z_n−3a.
All weighted root and integral envelopes S₁₂,S₁₆,S₂₄ and I₁₂,I₁₆,I₂₄
are uniform in ν. The local target constant is unchanged except for
the new V-weighted moment term; the balance/support constant is enlarged
explicitly. The bounds 188 and 2071000 for inactive coefficient
combinations still suffice with ΣV_j=189. All shift factors from L,
including 1/(1−48a₀) and 1/(1−72a₀), are retained.

## 7. Uniform finite cells, exact repair, and all budgets

The R25 local Taylor and support inequalities are recomputed over the
whole cusp/dual boxes using the sextic jets. The expanded trial-dual box,
28 derivative-positive neighborhoods, 354-leaf sign cover and balanced
ramp containment are checked anew. No old fixed-Q derivative margin is
assumed unchanged.

The same first three centers permit exact lower-moment repair. With
the new dyadic preconditioner and scaled correction box, row contraction
bounds are <(.010534,.014440,.008662), forcing bounds are
<(.358977,.489798,.291664), and their sums are <1. The proof applies
for each fixed (ν,a); the selected finite root list is independent of
the three correction variables.

Combining finite cells with U10 proves, uniformly for ν∈I and 0<a≤a₀,

\[
 H_{v,\nu}(a)\le D_\nu-\Gamma_\nu a^2/3+\Xi_\nu a^4+K_da^6,
 \quad
 |S_\nu(a)-(D_\nu-\Gamma_\nu a^2/3+\Xi_\nu a^4)|\le K_pa^6,
 \tag{U11}
\]

with K_d<739740 and K_p<4831937. The first inequality bounds arbitrary
admissible competitors; the second concerns the exactly repaired primal.

R26's auxiliary scalar argument now uses the parameter-dependent
F_{ν,M}(A)=D_νA−Γ_νA³/(3M²)+Xi_νA⁵/M⁴ and
J_{ν,M}=F_{ν,M}−K_pA⁷/M⁶. A common U<9.178959760×10⁻¹⁰ satisfies
U/M₀<a₀, J(δ₀)<f_ν<J(U), and J'>0 for all ν∈I, M≥M₀.
The upper endpoint margin exceeds 1.76885×10⁻¹⁵. Its root yields a
feasible profile after rescaling, without assuming continuity of the
changing root prefix in a or ν. Amplitudes are <1, so each constructed
kernel multiplier remains positive. Existence of the true optimum follows
by Arzelà–Ascoli and dominated convergence against the L¹ densities.

The scalar inversion polynomial of R25 has its coefficients through
degree two cancel exactly and retains all remaining terms through
degree twelve. Recomputed interval bounds give

\[
 K_-<1.016671\times10^{-53}<1.02\times10^{-53},\qquad
 K_+<1.634865\times10^{-53}<1.64\times10^{-53}.
 \tag{U12}
\]

This proves U5. Since 1.02×10⁻⁵³/M₀²<2.47×10⁻³⁹, U4 gives the
strict positive correction claimed after U5.

## 8. Scope and independent checks

This quantifies local persistence of the optimal-value structure at
the quartic endpoint of the known cusp arc. It does not claim that a
continuity principle itself is new. It does not prove global classification,
a common perturbation for the whole arc, a C₆ limit, or monotonic C₄.
Nor does this moment-cost theorem check the fourth derivative and the
three-control rank of every resulting modified kernel; those geometric
nondegeneracy questions require their own bounds.

Twelve new exact algebra groups extend the R26 tail estimates. A separate
512-bit outward rational calculation reconstructs 116 decision inequalities,
including the moving dual, coefficient and remainder bounds. It accepts
the cusp/Taylor enclosures, transcendental jets, root/sign values and
infinite-tail inputs explicitly. The audit cannot mechanically prove
all analytic implications above.

Direct mpmath calculations at five driver values independently solve the
original cusp and sign-moment equations, then evaluate the coefficient
and selected root derivatives. They use 90/130 digits, twelve theta terms
and a finite integral cutoff. Their agreement is diagnostic corroboration;
the continuum and infinite-tail claims come from the analytic bounds and
interval calculation. The sampled increasing trend in C₄ is not promoted
to a monotonicity theorem. Exact coefficients are used in U5; decimal
rounding errors must be added separately in applications.

[Numbers](results/TABLE.md), [review](REVIEW.md), [reproduction](README.md),
[Turkish findings](BULGU_NOTU_TR.md).
