# R28 — Strict motion of the fourth coefficient along the exact cusp arc

The object is the exact coefficient C₄(ν) of R27, in the original u
coordinate and original driver ν. This is a sensitivity theorem for that
coefficient. It does not differentiate the finite-M remainder or establish
monotonicity of the true finite-M optimum. The analytic proof below and
the validated numerical hypotheses remain subject to external review.

## 1. Statement and identification of the objects

Keep the exact R03/R27 cusp Q(ν), the unique unrestricted dual b*(ν),
the positive density w_ν, moment densities q_j, target f_ν, objective D_ν,
and root sums Γ,G,B,R. The definitions and exact identity Q(0)=Q are
in [R27](../cusp_uniform_remainder/PROOF.md). Let

\[
 I=[-2^{-16},0],\quad
 \Xi=R-\tfrac12B^TG^{-1}B,\quad
 \delta_0=f/D,\quad
 C_4=\delta_0^5\left(\frac{\Gamma^2}{3D^2}-\frac{\Xi}{D}\right).
 \tag{V1}
\]

**Theorem.** The function C₄ is continuously differentiable on the
interior of I with continuous one-sided derivatives at its endpoints.
Throughout I, interpreting endpoint derivatives one-sided,

\[
 2.82\times10^{-40}<C_4'(\nu)<4.35\times10^{-40}.
 \tag{V2}
\]

Consequently it is strictly increasing. For any ν₁<ν₂ in I,

\[
 2.82\times10^{-40}(\nu_2-\nu_1)
 <C_4(\nu_2)-C_4(\nu_1)
 <4.35\times10^{-40}(\nu_2-\nu_1).
 \tag{V3}
\]

Combining this with R24's exact endpoint enclosure gives the stronger
common value enclosure

\[
 2.49202340\times10^{-39}<C_4(\nu)<2.49203006\times10^{-39}.
 \tag{V4}
\]

V4 sharpens R27's common value band without changing its frozen files or
recomputing its remainder constants. No statement about the whole R03
curve [−29,0], C₄ convexity, or a C₆ coefficient follows.

## 2. Moment derivatives and sign moments

A dot denotes differentiation along the exact cusp at fixed u. Its
velocity (τ',λ',μ') is uniformly enclosed by R27. Since q_j=w p_j,
the parameter derivative identity is

\[
 \dot q_j=\tau' q_{j+1}-\frac{\lambda'}4q_{j+2}
          +\frac{\mu'}{16}q_{j+4}-\frac1{64}q_{j+6}.
 \tag{V5}
\]

It commutes with u derivatives. The signs follow from the phase shifts
in p_j=(2u)^j cos(2τu+jπ/2). The last term is the derivative of the
sextic weight; it is not omitted. Positive moments from R09 and ν≤0
give uniform L¹ dominators for all densities in V5.

Set S_j=∫sign(q*)q_j. At the exact dual optimum, S₀=S₁=S₂=0 and
S₃=D. For j≤3 define T_j by applying the right side of V5 to S.
This T_j is the fixed-sign integral ∫sign(q*) dot(q_j); it is not
the full derivative S_j'.

To enclose S₄,…,S₉, start from the fixed dyadic sign template of R12.
Its moments through order eight were already bounded at exact Q(0).
The new ninth moment is integrated at the original dyadic center over
the same 29 sign intervals using Arb's finite entire-function quadrature.
The omitted theta series, the half-line tail, and the center-to-exact-Q
uncertainty are added separately. It is approximately
−5.6028695980503848888×10⁻⁶. This is a template moment, not an
unqualified optimal sign moment.

Transport from Q(0) to Q(ν) contributes

    E_j=|Δτ|B_{j+1}+|Δλ|B_{j+2}/4+|Δμ|B_{j+4}/16+|ν|B_{j+6}/64.

In [0,1], the current root box and old template knot bound every
possible sign disagreement. For each such interval J add
2|J| sup_J|q_j|. Beyond 1 add 2∫₁∞|q_j|, allowing all possible
tail sign differences. R27 supplies a complete sign cover and no
unaccounted finite roots. The derivative of the positive envelope for
orders j≤9 is less than −540, so the last term is bounded by
2·88·2^j exp(18−πe⁴)/540. No global small displacement of infinitely
many roots is assumed.

## 3. Differentiating the exact dual, before using its velocity

For a fixed b near the R27 dual box, sign moments are continuously
differentiable in b and ν. On each finite set of simple roots this
follows by differentiating the moving integral endpoints. The tails
are uniformly summable, as explained below; this justifies the limit.
The b Jacobian is −G, invertible by R27's positive Gram bounds.
The implicit-function theorem therefore yields a C¹ b*(ν), including
the one-sided extension at the endpoints by the same uniform bounds.

At a root z put q*=q₃−Σb_jq_j, γ=|∂_u q*| and Q_j=q_j(z).
Differentiating S_j=0 gives

\[
 G b'=A,\qquad
 A_j=T_j+2\sum_k\frac{Q_{j,k}\,h_k}{\gamma_k},\qquad
 h_k=\dot q_3(z_k)-\sum_{i<3}b_i\dot q_i(z_k).
 \tag{V6}
\]

Here h excludes b'. At a true root, the weight derivative multiplies
the vanishing raw residual. Thus h=w τ' (p₄−Σb_jp_{j+1}). This
root identity is used only at the enclosed true root.

There is no circular assumption on b' in this step. For u≥1 the fixed-b
parameter boundary term is at most w u³: |τ'|<1,
|p₄−Σb_jp_{j+1}|<17u⁴, |∂_u r_b(z)|>567u³ and |p_j|≤4u²
give 2·4·17/567<1. The Hessian tail is already bounded in R27.
The integral part T is dominated by positive moments. These bounds
justify V6 independently of any prior bound on b'.

We solve V6 using a recorded exact dyadic approximate inverse C and
seed v₀. If η=||I−CG||∞<1, then

    ||b'−v₀||∞≤||C(A−Gv₀)||∞/(1−η).

The interval and separate rational evaluations verify this and give
|b'_j|<10 for all three components, with much smaller actual boxes
in the certificate. This coarse bound is used only for tail estimates.

Envelope differentiation also yields

\[
 D'=T_3-\sum_{j<3}b_jT_j,\qquad
 f'=\tau'D_4-\lambda'D_5/4+\mu'D_7/16-D_9/64,
 \tag{V7}
\]

where D_n=∂_t^nF at the exact cusp, not the dual objective D.
The b' contribution to D' vanishes because S₀,S₁,S₂=0. The moving
boundary contributes zero to D' because q*=0 at each boundary.

## 4. Root velocities and total derivatives of the coefficient sums

The root equation gives

\[
 z_k'=\frac{\sum_{j<3}b'_jp_j(z_k)
       -\tau'(p_4(z_k)-\sum_{j<3}b_jp_{j+1}(z_k))}{r_b'(z_k)}.
 \tag{V8}
\]

Let r=∂_u q*, t=∂_u²q*, s=∂_u³q*, σ=sign r and γ=σr.
For each l=1,2,3 the total root derivative is

    r_l' = dot(q₃^(l))−Σ[b_j dot(q_j^(l))+b'_j q_j^(l)]
           +q*^(l+1) z',
    Q_j'=dot(q_j)+q_j^(1)z',
    (q_j^(1))'=dot(q_j^(1))+q_j^(2)z'.

In these formulas r₁=r, r₂=t, r₃=s. Thus fourth u derivatives,
the sextic weight derivatives, and the moving dual are all included.
Primes on Q_j and r_l here mean total derivatives along the moving root.

Termwise differentiation gives

\[
\begin{split}
 \Gamma'&=\sum\sigma r',\\
 G_{ij}'&=2\sum\left[\frac{Q_i'Q_j+Q_iQ_j'}\gamma
                    -\frac{Q_iQ_j\gamma'}{\gamma^2}\right],\\
 B_j'&=\frac13\sum\sigma\left[
        \frac{Q_j't+Q_jt'}r-\frac{Q_jtr'}{r^2}-(q_j^{(1)})'\right],\\
 R'&=\sum\left[\frac{tt'}{18\gamma}
              -\frac{t^2\gamma'}{36\gamma^2}-\frac{\sigma s'}{60}\right].
\end{split} \tag{V9}
\]

All 28 finite root contributions are interval-evaluated over the entire
R27 parameter and exact-dual boxes. The root-dependent σ is locally
constant and fixed by the validated orientations.

## 5. Every infinite derivative tail

The R27 negative-sextic extension supplies |w^(l)|≤w W_l e^{4lu}
through order four. For u≥1, define exact rational constants

    P_{jl}=2^j Σ_{h≤min(j,l)} binom(l,h)(j)_h 84^(l−h),
    K_{jl}=Σ_{k≤l} binom(l,k) W_k P_{j,l−k}.

Then |q_j^(l)|≤w K_{jl}u^j e^{4lu}. Combining V5 with |τ'|,|λ'|,
|μ'|<1 gives constants H_{jl} for
|dot(q_j^(l))|≤w H_{jl}u^{j+6}e^{4lu}. Their exact formula is
K_{j+1,l}+K_{j+2,l}/4+K_{j+4,l}/16+K_{j+6,l}/64.

V8 and |b'|<10 yield |z'|≤(70+17)u/567<u. Therefore the total
root derivative of q_j^(l) is bounded by
w(H_{jl}+K_{j,l+1})u^{j+6}e^{4(l+1)u}. For the residual, insert
the componentwise bounds |b|<(.001,.1,.005) and |b'|<10. This gives
the recorded rational L_l in

    |(q*^(l))'|≤w L_l u^9 e^{4(l+1)u}.

Substituting these bounds and γ≥567wu³ into V9 yields envelopes
of the form w C u^p e^{du}. The exact constants C are recorded in
`algebra.json`, and recomputed independently in the Arb producer:

| Tail | p | d |
|---|---:|---:|
| boundary part of A_j | 3 | 0 |
| Γ' | 9 | 8 |
| each G_ij' | 7 | 8 |
| each B_j' | 8 | 16 |
| R' | 9 | 24 |

Use w≤88 exp(9u+9u⁴−πe^{4u}). Every resulting envelope has
logarithmic derivative at most
(p+9+d+36−600)u³<−500. The roots are separated by more than 3/85,
and 500·3/85>16. Thus each sum is bounded by its value at u=1
divided by 1−50⁻⁴. Bounds before outward rounding for display are:

    |A_boundary,tail| <1.860×10⁻⁶⁵,
    |Γ'_tail|         <1.724×10⁻⁵⁶,
    |G'_ij,tail|      <3.130×10⁻⁶⁰,
    |B'_j,tail|       <1.109×10⁻⁵²,
    |R'_tail|         <1.734×10⁻⁴⁵.

These uniform summable derivative majorants justify differentiating the
infinite root sums. In particular |z'| is allowed to grow with z; no
uniform bounded displacement of the whole root sequence is required.

The finite theta jet calculation uses 12 terms. For omitted terms
n≥13 and derivatives up to four, the absolute monomial ratios are
at most (14/13)^12 exp(−27π)<1/2, so twice the first omitted term
is retained. Neither an omitted root nor an omitted theta term is
treated as zero.

## 6. The coefficient derivative and strict increase

Set v=G⁻¹B. The quadratic correction P=½BᵀG⁻¹B satisfies

\[
 P'=B'^Tv-\tfrac12v^TG'v,\quad \Xi'=R'-P',\quad
 L=\frac{f'}f-\frac{D'}D,\quad H=\frac{\Gamma^2}{3D^2}-\frac\Xi D.
 \tag{V10}
\]

This avoids enclosing v' unnecessarily. One way to verify the identity
is to write P=Bᵀv−½vᵀGv and use stationarity Gv=B; the v' terms
cancel. The exact checker verifies the polynomial cancellation.

Finally

\[
 C_4'=\delta_0^5\left[
 5LH+\frac{2\Gamma\Gamma'}{3D^2}
 -\frac{2\Gamma^2D'}{3D^3}-\frac{\Xi'}D+\frac{\Xi D'}{D^2}
 \right]. \tag{V11}
\]

The producer and separate outward-rational calculation both place V11
strictly inside V2. The latter uses forward automatic differentiation
of the root formulas and the stationary quadratic expression, instead
of copying the producer's explicit quotient derivatives.

Integrating V2 yields V3. At the endpoints this follows by continuity.
Using R24's 2.49203004×10⁻³⁹<C₄(0)<2.49203006×10⁻³⁹ gives

\[
 C_4(0)+\nu(4.35\times10^{-40})
 <C_4(\nu)
 <C_4(0)+\nu(2.82\times10^{-40})\quad(\nu<0),
 \tag{V12}
\]

and hence V4. At ν=0, V12 is an equality at the anchor; the strict
statement V4 still follows from R24. Over the full short arc the gain
is between (2.82×10⁻⁴⁰)/65536 and (4.35×10⁻⁴⁰)/65536.

## 7. Checks and limits

The 26 exact check groups verify derivative identities, moving-boundary
signs on exact examples, a missing-target-motion negative control, the
stationary quadratic cancellation, and tail inequalities. The 44
outward-rational decisions verify the transported moments, simple roots,
implicit solve and positive derivative band. The checker accepts explicitly
the inherited cusp/dual boxes, transcendental jets, sign-motion estimates,
and analytic tail inputs. It is not a new integration of every input.

Independent finite differences re-solve the original cusp and optimal
sign moments at nearby driver values. Two step sizes, two precisions,
and one-sided second-order stencils at the endpoints test V11 without
using that formula. They retain twelve theta terms and a finite cutoff;
their role is diagnostic. The continuum assertion comes from V5–V11
with uniform interval bounds, not the finite-difference samples.

V2 concerns C₄. Even though some other derivative enclosures are also
positive, no derivative bound for R27's finite-M remainder is supplied.
Thus this package does not claim that δ_ν(M) increases with ν. The
positive direction is with respect to the specified ν coordinate;
reversing that coordinate reverses the sign. Uniform geometric
nondegeneracy of modified kernels and novelty priority remain separate.

[Numbers](results/TABLE.md), [review](REVIEW.md), [reproduction](README.md).
