# R09 — Pinned-cusp shape design and a constructed order-four zero

20 September 2026. Computer-assisted results for a specified family of
modified positive theta kernels. These results have not received external
mathematical review. Literature priority is not established.

## 1. Fixed objects and the scope of the deformation

Use the integral and the exact certified point Q from
[R01](../cusp_verified/PROOF.md):

\[
F(t;\lambda,\mu,\nu)=\int_0^\infty\Phi(u)
 e^{\lambda u^2+\mu u^4+\nu u^6}\cos(2tu)\,du,
\]
\[
\Phi(u)=\sum_{n\geq1}(2\pi^2n^4e^{9u}-3\pi n^2e^{5u})
 e^{-\pi n^2e^{4u}}.
\]

For u≥0 each summand is positive. The super-exponential tail permits
holomorphic dependence on all finite complex controls on compact sets,
and differentiation under the integral. Write F_n=∂t^n F. The identities

\[
\partial_\lambda F_n=-F_{n+2}/4,\qquad
\partial_\mu F_n=F_{n+4}/16,\qquad
\partial_\nu F_n=-F_{n+6}/64
\tag{1}
\]

also hold after multiplication of the kernel by any fixed bounded cosine
polynomial used below.

Q is the exact root of F_0=F_1=F_2=0 at ν=0 identified by
[the R01 root certificate](../cusp_verified/results/quartic_cusp_certificate.json).
Approximately Q=(41.40034135868425, −3.645692061604919,
8.335120498918607); F_3(Q)>0>F_4(Q). The word *quartic* in the old
certificate's filename refers to the u⁴ deformation, not a fourth-order
t zero. Q initially has multiplicity three. Rounded coordinates do not
define Q or any exact moment in this note.

For 1≤j≤16 and 0≤n≤8 define exact moments

\[
M_{nj}=\left.\partial_t^n\int_0^\infty\Phi(u)
e^{\lambda_Qu^2+\mu_Qu^4}\cos(2ju)\cos(2tu)\,du\right|_{t=t_Q}.
\tag{2}
\]

Let J=(10,13,15,16), A_J=(M_nj) for n=0,1,2 and j∈J. Its
four signed 3×3 minors are c_i=(−1)^(i−1)det(A_J with column i
removed). All four are nonzero. Set Z=Σ|c_i| and w_i=σc_i/Z, where
σ∈{−1,1} is the orientation recorded in the certificate, chosen below
to give S>0. Define

\[
h_*(u)=\sum_{i=1}^4w_i\cos(2J_i u),\qquad
H=\int_0^\infty\Phi(u)e^{\lambda u^2+\mu u^4+\nu u^6}
h_*(u)\cos(2tu)\,du,
\quad G_\epsilon=F+\epsilon H.
\tag{3}
\]

The cofactor identity gives A_Jw=0 **exactly**. Thus H_0(Q)=H_1(Q)
=H_2(Q)=0 and Q is a zero of order at least three for every ε.
Furthermore Σ|w_i|=1, so ||h_*||∞≤1; equality of that supremum norm
is not needed or asserted. In particular Φ_ε=Φ(1+εh_*) is positive
for |ε|<1. The approximate weights, solely for identification, are
(−0.71541683886549, 0.16731579128320, −0.07939153463132,
0.03787583521999). They must not replace the exact cofactor definition.

Define

\[
a=H_3(Q)/F_3(Q),\quad b=H_4(Q)/F_4(Q),\quad S=b-a.
\tag{4}
\]

The independently checked bounds are a∈[−53.279001512222,
−53.279001512221], b∈[30.487975048861,30.487975048862], and
S∈[83.766976561083,83.766976561084].

## 2. An exact optimum in a declared finite class

Consider all real cosine polynomials h=Σ(j=1..16)v_j cos(2ju)
such that their three Q moments vanish and Σ|v_j|≤1. Let A be
the 3×16 moment matrix with its rows divided by the positive exact
dyadic scales recorded in the certificate, and put
d_j=M_4j/F_4(Q)−M_3j/F_3(Q). The objective is

\[
\max_{Av=0,\ \|v\|_1\leq1}d^Tv.
\tag{5}
\]

It equals the maximum initial logarithmic rate of decrease of the
leading fold opening coefficient, −∂ε log C(0). This is neither an
optimization over every bounded h nor an optimization of finite W at
a nonzero λ offset.

**Theorem 1.** The oriented four-mode vector w, extended by zero outside
J, is the unique maximizer of (5), with maximum S.

**Proof.** Let (y,z) be the exact solution of the four equations
d_j−A_j^Ty=z sign(w_j), j∈J. The defining 4×4 matrix is nonsingular.
The certificate gives z>0 and |d_j−A_j^Ty|<z for every j outside J;
the smallest strict slack exceeds 10.51. Hence every feasible v obeys

\[
d^Tv=(d-A^Ty)^Tv\leq z\|v\|_1\leq z.
\]

For w the active equalities and exact moment cancellation give
d^Tw=zΣ|w_j|=z, so it attains the bound. Strict slack forces any
maximizer to vanish outside J. Rank(A_J)=3 leaves a one-dimensional
nullspace, and the required orientation and norm give precisely w.
No conclusion is inferred from a merely small residual: active
equalities follow from the exact linear-system definition and moment
cancellation follows from the exact cofactor identity. The rational
checker uses permutation determinants and Cramer's rule, independently
of the generator's Arb matrix solve. This is an application of standard
[linear-programming weak duality](https://web.stanford.edu/class/ee364a/lectures/duality.pdf),
not a new optimization method. ∎

## 3. Prescribing any positive leading opening coefficient

At a cusp with G_3>0>G_4, in translated but unrescaled coordinates
s=t−t_Q, ℓ=λ−λ_Q, m=μ−μ_Q, the local fold equations give

\[
\ell(s)=2s^2+O(s^3),\quad
m(s)=-\tfrac{16}{3}k s^3+O(s^4),\quad k=-G_3/G_4>0,
\]
\[
W(\ell,\epsilon)=m_+-m_-=C(\epsilon)\ell^{3/2}+O(\ell^2),
\qquad C(\epsilon)=\tfrac{8\sqrt2}{3}k.
\tag{6}
\]

Since Q is fixed exactly, (4) gives the **exact** identity

\[
\frac{C(\epsilon)}{C(0)}=\frac{1+a\epsilon}{1+b\epsilon}.
\tag{7}
\]

**Theorem 2.** For every prescribed r>0, the amplitude

\[
\epsilon(r)=\frac{1-r}{rb-a}
\tag{8}
\]

defines a positive smooth modified kernel, keeps the exact Q cusp
nondegenerate in the (λ,μ) controls, and gives C(ε(r))=rC(0).
For all these kernels Φ_ε>0.9672Φ on the integration domain.

**Proof.** Let ε_μ=−1/b and ε_4=−1/a. The verified bounds are

\[
\epsilon_\mu\in[-0.032799816925,-0.032799816924],\qquad
\epsilon_4\in[0.018769120509,0.018769120510].
\tag{9}
\]

For r>0, rb−a>0. Substitution of (8) gives
1+aε=r(b−a)/(rb−a)>0 and 1+bε=(b−a)/(rb−a)>0.
Thus ε_μ<ε(r)<ε_4 and G_3(Q)>0>G_4(Q). The (λ,μ) unfolding
matrix for (G_0,G_1) has determinant G_3G_4/64≠0. Also |ε|<0.0328
implies 1+εh_*>0.9672. Equation (7) proves the assertion. ∎

On this open interval C is strictly decreasing, tending to +∞ at the
left boundary and to 0 at the right boundary. This is a statement
about the *leading local coefficient in the original control units*.
It does not assert a common finite root window across this entire
interval or an unbounded W at a fixed ℓ. Near the left boundary the
control unfolding becomes ill-conditioned; control rescaling would
alter C. Positivity, exact pinning and pointwise nondegeneracy alone
therefore provide no finite upper bound for this particular C. A
uniform transversality margin is necessary for such a bound.

## 4. A common finite window, not only an asymptotic coefficient

Set τ=1/128. For |ε|≤τ, every kernel differs pointwise from Φ by
at most 0.78125% relative to Φ. This is a bound on each kernel's
distance from the base kernel, not on the distance between endpoints.
The latter can be as large as 1.5625% of Φ under this bound.

**Theorem 3.** For every |ε|≤τ at ν=0, in

\[
|s|\leq0.003,\qquad |\ell|\leq10^{-6},\qquad |m|\leq2\,10^{-9},
\tag{10}
\]

there is just the exact cusp Q and two fold branches
m_−(ℓ,ε)<0<m_+(ℓ,ε) for 0<ℓ≤10⁻⁶. Between the folds there are
exactly three simple real zeros in the stated s window. Off the
discriminant outside that strip there is exactly one simple zero.
A noncusp fold has one double and one simple zero; Q has one triple
zero. No zero crosses the s-window endpoints. Moreover

\[
\partial_\epsilon m_+<0<\partial_\epsilon m_-,\qquad
10\ell^{3/2}<-\partial_\epsilon W<500\ell^{3/2}.
\tag{11}
\]

Consequently the actual three-root strips are strictly nested as ε
increases. This R09 theorem is only at the fixed ν=0 section. The R08
whole-ν-arc theorem uses a different direction and remains a separate
result; it cannot be transferred to h_* without further proof.

**Proof and validated bounds.** Partition [−τ,τ] into sixteen adjacent
closed intervals of length 1/1024. On each interval the stored exact-Q
F and H jets are combined as G_n=F_n+εH_n before spatial variation
is enclosed. Taylor expansion through total order seven in
δt D−δλ D²/4+δμ D⁴/16 is used. The terms of total order eight are
bounded by positive absolute derivative majorants. The retained
central derivatives run through order 54, and the majorants through
order 58. The entire segment lies in the recorded majorant domain.

For each s∈[−0.003,0.003], the equations G=G_1=0 in (ℓ,m) admit
a uniform contraction on the common auxiliary box
|ℓ|≤2⁻¹³, |m|≤2⁻¹⁹. Its preconditioner is the dyadic midpoint
inverse at the cusp. The weighted derivative defect q and residual
η satisfy q+η<1. Existence and uniqueness therefore apply to the
whole fold curve, not just sampled fold points. In that box
G_3>0>G_4 and Δ=G_3G_4−G_2G_5<0. Differentiating along the fold gives

\[
\ell_s=4G_2G_4/\Delta,\qquad m_s=16G_2^2/\Delta,
\quad (G_2)_s=G_3-G_4\ell_s/4+G_6m_s/16>0.
\tag{12}
\]

Integrating the recorded per-cell bounds yields positive quadratic
and cubic bounds for ℓ(s) and |m(s)|. These prove both branches exist
up to ℓ=10⁻⁶ and remain strictly inside |m|≤2×10⁻⁹. The saved
endpoint signs prevent roots crossing |s|=0.003. G_3>0 bounds the
number of zeros by three (with multiplicity). Alternating signs at
four interior points and a positive-G_1 interval cover provide one
three-root and one one-root witness in the respective components.
Together with the complete discriminant parametrization, these give
the claimed root count throughout the window. Adjacent ε cells have
the same exact Q and the same fold uniqueness box; uniqueness
identifies their curves at all fifteen interfaces. Mere box overlap
is not used to identify solutions.

For the transport sign, Q is constant, so at fixed ℓ the fold velocity is

\[
B(s)=\partial_\epsilon m|_\ell=-16H_0/G_4.
\tag{13}
\]

Let k=−G_3/G_4 and A_3=(4/3)(G_5/G_4−G_4/G_3), evaluated at Q.
The exact [R08 transport calculation](../cusp_pinned_family/PROOF.md)
gives B(0)=B′(0)=B″(0)=0, B‴(0)=−32k_ε and B⁽⁴⁾(0)=96k(A_3)_ε.
Here k_ε=(F_3H_4−F_4H_3)/G_4²<0, whose numerator is independent
of ε; it is enclosed before interval division. If M_4 bounds the
fourth derivative at Q and M_5 bounds the fifth derivative along
the fold, then

\[
B'''(s)\in -32k_\epsilon+
[-M_4S_0-M_5S_0^2/2,\ M_4S_0+M_5S_0^2/2]
\quad (|s|\leq S_0=0.001).
\tag{14}
\]

Every cell makes the lower bound positive. Its quadratic growth
bound gives ℓ(S_0)>10⁻⁶, so (14) covers every fold needed in (10).
Three integrations give B(s)<0 for s<0 and B(s)>0 for s>0.
The negative-s branch is the upper fold. Combining these integrations
with the quadratic bounds yields (11). The rational checker rebuilds
all new spatial Taylor bounds and evaluates M_5 by a fold ODE,
independently of the generator's implicit-series elimination. ∎

At ℓ=10⁻⁶, separate finite fold contractions give

\[
100\left[\frac{W(+\tau)}{W(-\tau)}-1\right]
\in[-74.63952481,-74.63952480]\ \text{percent}.
\tag{15}
\]

For the old R07 direction at the **same** amplitudes this lies in
[−0.00078034,−0.00078033] percent. The leading-C change for h_* is
[−74.6395459500,−74.6395459499] percent; it is not substituted for
the finite-W result. The direct finite widths W×10⁹ at −τ, 0, +τ
are respectively enclosed by [2.4067339885,2.4067339886],
[1.2946095162,1.2946095163], [0.6103591760,0.6103591762].

## 5. Different endpoint mechanisms; a local quartic unfolding

At ε_μ=−1/b, G_4(Q)=0 but G_3(Q)/F_3(Q)=1−a/b>2.74. The
zero remains of order three, while the two-control (λ,μ) cusp
unfolding loses rank. This is not a fourth-order zero.

**Theorem 4.** At ε_4=−1/a, Q is an exact zero of order four of
the modified integral G=F+ε_4H, and its three-control (λ,μ,ν)
unfolding has local zero equation equivalent to

\[
x^4+u x^2+v x+w=0.
\tag{16}
\]

**Proof.** Exact moment identities give G_0=G_1=G_2=0, and the
exact definition of ε_4 gives G_3=0. The independent rational
certificate gives

\[
10^{12}G_4(Q)\in[-1.527706119921,-1.527706119920].
\tag{17}
\]

At this point the parameter derivative matrix for (G_0,G_1,G_2) is

\[
J_p=\begin{pmatrix}
0&G_4/16&-G_6/64\\
0&G_5/16&-G_7/64\\
-G_4/4&G_6/16&-G_8/64
\end{pmatrix},\qquad
\det J_p=\frac{G_4(G_4G_7-G_5G_6)}{4096},
\]
\[
10^{38}\det J_p\in[-1.247577850654,-1.247577850653].
\tag{18}
\]

In particular the zero order is exactly four and rank(J_p)=3.
Let p=(λ−λ_Q,μ−μ_Q,ν) and s=t−t_Q. Holomorphic dependence and
G_4≠0 permit Weierstrass preparation:
G(s,p)=U(s,p)[s⁴+c_3(p)s³+c_2(p)s²+c_1(p)s+c_0(p)], where U
is nonzero and c_i(0)=0. For a statement of the preparation theorem
see [Ngô, section 3](https://math.uchicago.edu/~ngo/Weierstrass.pdf).

The derivatives in p of (G_0,G_1,G_2) at s=p=0 are an invertible
triangular matrix, with diagonal U(0), U(0), 2U(0), times the
derivatives of (c_0,c_1,c_2). Terms involving ∂p U times s⁴
vanish in these three jets. Thus (c_0,c_1,c_2) has rank three.
The substitution s=x−c_3(p)/4 removes the cubic term. The changes
to the lower coefficients have zero first derivative at p=0, so
their rank remains three. The inverse function theorem now gives
analytic control coordinates (u,v,w), proving (16). For real p all
changes can be chosen real; multiplication by the nonvanishing U
preserves zeros and their multiplicities. ∎

The antiderivative x⁵/5+ux³/3+vx²/2+wx is the usual swallowtail
potential with three controls, consistent with
[NIST DLMF §36.2(i)](https://dlmf.nist.gov/36.2#i). In a potential
convention this is called A4; the scalar function germ x⁴ is often
indexed A3. We use “order-four zero with a three-control unfolding”
to avoid that convention ambiguity. No claim is made that the
original integral itself is a canonical catastrophe integral.

This construction gives a positive kernel (indeed Φ_ε4>0.98123Φ),
but **it changes the original kernel**. It does not establish an A4
point in the original fixed-Φ polynomial deformation family. Also,
(16) is a local germ result: no explicit common physical-coordinate
swallowtail neighborhood or global discriminant has been certified.

## 6. Evidence, reproducibility and limits

The [dictionary](results/dictionary_16.json) uses 288 rigorous
frequency-shift integrals for 16 modes and 9 orders. Exact-Q uncertainty
is included using the frozen root radius and positive majorants.
The [local jets](results/local_jets.json) add 55 direct F and 55
direct H integrals, with 9 H comparisons against the shifted dictionary
and 9 F comparisons against the old Q certificate. A separate old-direction
comparison adds 34 H integrals. The primary integrations use Arb with
explicit series and infinite-domain tail bounds. Their parameters and
source hashes are recorded. Nine direct H moments were also evaluated
with mpmath at both 90 and 115 decimal digits; these precision checks
are supplementary numerical evidence, not rigorous integration.

The independent [design checker](results/design_check.json) uses
rational endpoints, exact cofactor identities and Cramer determinants.
The [local checker](results/local_check.json) rebuilds every new
Taylor bound and all sixteen geometry and transport cells with
outward 512-bit rational endpoints; its fifth derivative comes from
the fold ODE. The [sample checker](results/sample_check.json) verifies
176 finite fold contractions and sixteen endpoint width comparisons.
The [boundary corollary](results/boundary_certificate.json) records
the exact prescription and the two distinct degeneration mechanisms.

Trust boundary: saved rigorous integral enclosures and absolute
majorants are inputs to the rational checkers. The sample checker
also assumes its saved point Taylor enclosures. These programs are
different arithmetic/derivation implementations within this project,
not an external independent peer review or a formal proof-assistant
verification. The analytic arguments in this note also need review.

The exploratory support search is not the optimality proof. The first
auxiliary fold box failed a sufficient contraction inequality at one
sampled amplitude; its report is retained. The successful v2 enlarges
only that auxiliary μ radius, and the full proof is then checked. Two
initial rational-checker type errors are retained in diagnostic notes.
See [DIAGNOSTICS.md](DIAGNOSTICS.md); no failed result is promoted.

The original manuscript and all R01–R08 packages remain unmodified.
This stage establishes no novelty priority, physical time evolution,
physical stability, global root count, or Riemann-hypothesis consequence.
It also does not make the full original manuscript submission-ready.
