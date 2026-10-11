# R18 — Exact formulation map for the literature comparison

21 September 2026. This note rewrites the existing R13–R16 problem in
standard convex-duality terminology. It is **not a new contribution
claim**, a new kernel family, or a new asymptotic theorem. The source
register and limits of the comparison are in [LITERATURE.md](LITERATURE.md).

## 1. The original optimization stays fixed

Use the half-line X=[0,∞) with its original Euclidean coordinate u.
Write q_j=w p_j, where q_j∈L¹(X), j=0,…,m. The original constraints are

    ∫q_j h=0 (j<m),     ∫q_m h=−f,     f>0.

The objective is δ(M)=inf ∥h∥∞ subject also to Lip_u(h)≤M.
There is no kernel-mass normalization or endpoint value imposed on h.
For the theta example m=3 and the underlying exact point is the R01
cusp Q. The root-order/rank conditions belong to the additional
geometric interpretation; they are not part of the following convex
support problem. The equality of infima for the smooth geometric class
is the separate R13 result.

Set g=−h, and for fixed A,M>0 let

    K(A,M)={g∈C(X): ∥g∥∞≤A, Lip_u(g)≤M},
    V(A,M)=max{∫q_m g: g∈K(A,M), ∫q_j g=0 for j<m}.

Then, exactly,

    δ(M)=inf{A>0: V(A,M)≥f}.                         (E1)

Indeed, an original feasible h gives V≥f. Conversely a maximizer g
with value V≥f>0 can be multiplied by f/V, preserving both bounds
and the zero moments, to attain the target f. Maximum existence is
justified below. The infimum of the empty set is +∞; R13 already
establishes feasibility for our particular family.

## 2. The auxiliary norm is already known

For a finite signed measure μ on X define

    H(A,M;μ)=sup{∫g dμ: g∈K(A,M)}.

This is precisely the two-parameter Kantorovich–Rubinstein norm with
parameters (λ₁,λ₂)=(A,M) in Lellmann–Lorenz–Schönlieb–Valkonen [L07,
equation (2)]. The absolute value of the integral gives the same supremum
because the admissible set is symmetric. For our residual,

    r_a=p_m−Σ_{j<m}a_j p_j,
    dμ_a=(q_m−Σ_{j<m}a_j q_j)du=w r_a du.            (E2)

All μ_a are finite signed measures by the L¹ assumptions. In particular
their total mass need not be zero. Ordinary balanced W₁ is therefore
not automatically the appropriate norm.

The literal test-function definition in (E2) applies on our half-line.
It does not import the bounded-domain divergence/minimizer theorem
from [L07, Lemma 3.1/Theorem 3.4] to an unbounded domain. To compare
definitions on R, extend g constantly as g(0) for u<0 and extend μ_a
by zero. This preserves amplitude, Lipschitz constant and the integral;
restriction supplies the reverse direction.

## 3. Restoring the moments requires a further infimum

The exact value identity is

    V(A,M)=inf_{a∈R^m} H(A,M;μ_a).                   (E3)

Here is the standard minimax justification, including its topology.
Equip C(X) with uniform convergence on compact sets. K(A,M) is compact
by Arzelà–Ascoli on [0,n] and a diagonal subsequence, and it is convex.
The Lipschitz and amplitude bounds persist in the limit. On K(A,M),
the moment maps are continuous: for R>0 split the integral at R;
local uniform convergence controls [0,R] and the tail is at most
2A∫_R^∞|q_j|, uniformly in the sequence.

For

    L(g,a)=∫q_m g−Σ_{j<m}a_j∫q_j g,

the function is continuous and affine in each variable. Apply the
one-compact-set minimax corollary on p.174 of Sion [L12], with K(A,M)
as the compact set and R^m as the other convex set. Thus

    sup_g inf_a L(g,a)=inf_a sup_g L(g,a).

The inner infimum on the left is ∫q_m g when all zero moments hold,
and −∞ otherwise. The zero function is admissible, so the left side
is the finite value V(A,M). The right side is (E3). The constrained
set is closed in K(A,M), which also proves existence of its maximum.
No attainment or uniqueness of the infimum over a is asserted here.

Combining (E1) and (E3) identifies the moment problem with a level-set
problem for an infimum of known KR norms over an affine residual
family. This duality is classical background, not a proposed novelty.

In particular,

    V(A,M)≤H(A,M;μ_{a*})                            (E4)

for the *unlimited-slope* optimizer a*. Replacing the infimum in (E3)
by a* would require an additional argument at finite M. R15's proof
does not make that replacement: its upper bound constructs designs
that restore the moments exactly.

An elementary diagnostic illustrates why (E4) need not be equality.
On X={0,1}, require g(0)=0 and maximize g(1), with A=1,M=1/4.
The constrained value is 1/4. The unlimited-slope dual objective
for μ_a=δ₁−aδ₀ is 1+|a|, whose unique minimum is a*=0. Yet
H(1,1/4;μ_0)=1. Taking a=1 gives H=1/4 and recovers (E3).
This discrete example is a check on an invalid general substitution;
it is not an example satisfying the smooth R15 hypotheses.

## 4. Normalizations that cannot be silently interchanged

These changes of variables are exact:

    H(A,M;μ)=A H(1,M/A;μ)=M H(A/M,1;μ).             (E5)

Thus the unit-amplitude Lipschitz parameter is M/A, not M. At the
minimum, A itself is δ(M); (E1) remains an implicit level relation.
In the finite-support p=1 convention of Heinemann–Klatt–Munk [L11,
definition (2) and the dual following Theorem 2.2],

    H(A,M;μ−ν)=M UOT_{1,C}(μ,ν),   C=2A/M.          (E6)

The factor 2 comes from their amplitude cap C/2. The published HTML
and the inspected preprint contain an inconsistent total-variation
factor in Theorem 2.2(ii); (E6) uses their definition and displayed
dual, not that factor. See [the normalization note](NORMALIZATION_CHECK.md).

The convention here is

    ∥μ∥TV=|μ|(X),     ∥q du∥TV=∫|q|du.

It has no prefactor 1/2. Also max(∥g∥∞,Lip(g))≤1 describes our two
separate unit caps. The alternative ∥g∥∞+Lip(g)≤1 gives an equivalent
norm but a different optimization problem and different sharp constants.
With x=c u and G(x)=g(x/c), Lip_x(G)=Lip_u(g)/c; a coordinate rescaling
cannot preserve M without compensation. We keep u fixed throughout.

## 5. What the existing R15 result adds to this formulation

At infinite slope, H(A,∞;μ_a)=A∫|r_a|dρ. R15 has the exact sign
moment identities at a*, D*=∫|r*|dρ, δ*=f/D*. Its existing conclusion is

    δ(M)−δ*=C*/M²+o(M⁻²),
    C*=δ*³ Γ/(3D*)=δ*⁴ Γ/(3f),
    Γ=Σ_k w(z_k)|r*′(z_k)|.                         (E7)

The important comparison is with asymptotics of this *moment-constrained
level value*, not only with convergence of H to a total-variation norm.
The R15 upper construction shifts m switch centers by O(a²) to enforce
the first m moments. Because q_r(z_k)=0, these shifts change the
residual integral only by O(a⁴). The same leading transition loss can
therefore be achieved with the moments exactly satisfied. The lower
bound applies to all feasible designs. Infinite switches require the
summability and separation hypotheses; they are not a finite-grid sum.

The constant 1/3 arises from an elementary linear transition integral.
That integral, norm duality, and smoothing alone are not claimed new.
Whether the combined conditional theorem (E7) has an earlier equivalent
formulation remains open after this focused search. Neither [L07]'s
definition nor [L08]'s flat/transport duality supplies (E7) by itself.
This last statement compares the identified results, not every possible
consequence of all literature.

R16 adds an explicit two-sided remainder for the theta example, valid
for every M≥0.00002, including its infinite tail. Its constants and
the R15 certificates are unchanged in R18.

## 6. Why a fixed atomic grid is not an asymptotic substitute

This is a diagnostic comparison, not a new research theorem. For
μ=Σ_i b_i δ_{x_i} on finitely many distinct nodes with minimum spacing
d>0, once Md≥2A, assigning g(x_i)=A sign(b_i) is feasible; piecewise
linear interpolation preserves both bounds in one dimension. Hence
H(A,M;μ)=AΣ_i|b_i| exactly. Cancel coincident opposite atoms first.

For comparison, for μ=x dx on [−1,1], the paired-point Lipschitz
inequality and g(x)=clip(Mx,−A,A) give, for M≥A,

    H(A,M;μ)=2M∫₀^{A/M}x²dx+2A∫_{A/M}¹x dx
            =A−A³/(3M²).                            (E8)

The continuous loss remains positive at every finite M. Fixed-grid
saturation therefore cannot establish the continuous leading coefficient.
This does not invalidate discretization methods: it requires a
discretization error bound on the scale of the quantity being studied.
The existing R15/R16 chain controls continuous integrals and infinite
tails explicitly; R18 has introduced no discretized replacement.

## Review boundary

Equations (E1)–(E6) have been checked as applications of definitions and
classical minimax; (E7) references the existing R15 proof, and (E8) is an
elementary normalization diagnostic. The accompanying rational script
checks small examples and factors. It does not formalize the minimax
argument, prove absence of prior art, or replace external review.
