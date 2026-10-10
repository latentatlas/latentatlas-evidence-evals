# R24 — A positive fourth-order coefficient for the fixed theta problem

This package evaluates the coefficient whose existence was proved in R23.
It retains the exact cusp Q and exact unrestricted dual b* enclosed by
R12/R15. Decimal centers are used only in the independent numerical check.
The problem is the bounded Lipschitz moment-design problem, with the same
u coordinate and normalization as the preceding packages.

## 1. Result and inherited inputs

For the fixed Q, let q_j=w p_j, j=0,...,3, where

\[
p_j(u)=(2u)^j\cos(2\tau u+j\pi/2),\qquad
w(u)=\Phi(u)e^{\lambda u^2+\mu u^4},\qquad
r_b=p_3-\sum_{j<3}b_jp_j,\quad q^*=w r_{b^*}.                 \tag{C1}
\]

Here Q is the exact certified cusp, with 41<τ<42, −4<λ<0, 0<μ<9.
The threshold is the minimum ||g||∞ with Lip(g)≤M, ∫q_jg=0 for j<3,
and ∫q₃g=f₃>0. Thus g=−h in the original kernel perturbation notation.
R15 supplies the exact optimizer localization, all 28 root enclosures
in [0,1], the whole-tail phase description, sign-moment equations,
δ₀, f₃ and D=f₃/δ₀. R23 supplies the analytic infinite-switch expansion.

**Certified coefficient statement.** Combining those analytic results
with the new enclosures below gives

\[
\begin{split}
\delta(M)&=\delta_0+C_2M^{-2}+C_{4,\theta}M^{-4}+o(M^{-4}),\\
2.49203004\times10^{-39}&<C_{4,\theta}
                       <2.49203006\times10^{-39}.             \tag{C2}
\end{split}
\]

The displayed bounds enclose both the Arb computation and an independent
outward-rounded rational reconstruction. This is a coefficient enclosure,
not a finite-M error estimate for the expansion.

## 2. Sharper localization using existing evidence

Let b₀ be the exact dyadic dual center in R15. That package proves
Hess D≥mI on the localization region, m=1/200, and bounds
||∇D(b₀)||₁ by g₀. Since the already certified b* lies in that region
and ∇D(b*)=0, strong monotonicity gives

\[
 \|b^*-b_0\|_2\le\frac{\|\nabla D(b_0)\|_2}{m}
              \le\frac{g_0}{m}<4.130\times10^{-14}.           \tag{C3}
\]

This is smaller than the previous 2^{-40} radius. No new unvalidated
optimizer is substituted. A new coefficient cube encloses this ball
and remains inside the old cube. For each inherited root box I, a
mean-value contraction uses the point c=mid(I) and the enclosure
c−r_b(c)/r_b'(I). Only strictly contained contractions are accepted.
The root is known to exist uniquely from R15. Thirty-one accepted
contractions over the 28 boxes are recorded in the certificate.

## 3. Exact root identities remove unnecessary small denominators

At a true zero z of r=r_{b*}, write a₁=r'(z), a₂=r''(z), a₃=r'''(z)
and σ=sign(a₁). The product rule and r(z)=0 imply

\[
 q^{*\prime}=wa_1,\qquad
 q^{*\prime\prime}=2w'a_1+wa_2,\qquad
 q^{*\prime\prime\prime}=3w''a_1+3w'a_2+wa_3.                \tag{C4}
\]

These are identities **at the enclosed root**, not identities at every
point of its interval. In particular no w''' value is required for the
third root derivative. Let γ=w|a₁|, ℓ=w'/w, n=w''/w, H=a₂/a₁, J=a₃/a₁.
The contributions to the coefficient sums are

\[
\begin{split}
G_{ij,k}&=\frac{2w p_i p_j}{|a_1|},\\
B_{j,k}&=\frac{\sigma}{3}
       \left[w'p_j+w(p_j a_2/a_1-p_j')\right],\\
\mathcal R_k&=\gamma\left[\frac{(2\ell+H)^2}{36}
                         -\frac{3n+3\ell H+J}{60}\right].
\end{split}                                                     \tag{C5}
\]

The finite computation uses C4 and the equivalent formula
R_k=(q*'')²/(36γ)−σq*'''/60. C5 is also checked as an algebraic
identity and supplies convenient whole-tail bounds. The checker derives
the sums again from interval p jets and w,w',w'', using exact rational
arithmetic and outward dyadic rounding after every operation.

## 4. Finite-root interval evaluation

Polynomial/trigonometric p derivatives through order three are evaluated
by the product rule, retaining the factors (2u)^j and frequency 2τ.
For the theta weight, use the first 12 terms and the derivative polynomials

\[
P_0=-3+2x,\qquad P_1=-15+30x-8x^2,\qquad
P_2=-75+330x-224x^2+32x^3,
\quad x=\pi n^2e^{4u}.                                      \tag{C6}
\]

The summand derivative is πn²e^{5u−x}P_ℓ(x). For each absolute
monomial the omitted-series ratio is at most 2⁸e^{-3π}<1/2 for u≥0;
twice the first omitted absolute term bounds the series remainder.
Mixed left/right endpoints of each root interval enclose the exponential
and polynomial factors. Derivatives of exp(λu²+μu⁴) are combined by
the product rule. All parameter boxes and all local omitted-series bounds
are retained. Evaluation is performed at 120 decimal digits with Arb.

## 5. Bounds for every remaining root

On u≥1, the inherited phase representation gives |r'(z)|>567z³
at every zero. Direct product-rule bounds, uniform over the coefficient
cube, give

\[
 |r'(u)|<900u^3,\quad |r''(u)|<63000u^3,\quad
 |r'''(u)|<5400000u^3,\quad |H|<112,\quad |J|<9524.
                                                               \tag{C7}
\]

For example each p_j^{(ℓ)} is bounded by
2^j Σ_{h≤min(j,ℓ)} binom(ℓ,h)(j)_h 84^{ℓ-h} u^j, for u≥1.
Insert |b₀|<1/1000, |b₁|<1/10, |b₂|<1/200, and use u^j≤u³.
The inequalities for H,J are used only at the roots, where the lower
bound for |r'| applies.

The first theta term is at least π²e^{9u−πe^{4u}} for u≥1, while the
R15 derivative bounds give |Φ'/Φ|<134e^{4u} and |Φ''/Φ|<3526e^{8u}.
Use |P'|≤44u³, |P''|≤116u² for P=λu²+μu⁴, and
e^{4u}>50u³ for u≥1. Then

\[
 w<88e^{9u+9u^4-\pi e^{4u}},\qquad
 |w'/w|<135e^{4u},\qquad |w''/w|<3800e^{8u}.                \tag{C8}
\]

Consequently |2ℓ+H|<273e^{4u} and |3n+3ℓH+J|<12400e^{8u}.
In C5 this gives |R_k|<2300γ_k e^{8z_k}. The following nonnegative
envelopes therefore bound the absolute contribution of every tail root:

\[
\begin{array}{c|c}
\text{quantity}&\text{envelope at a root }u\ge1\\\hline
\gamma_k&79200u^3e^{9u+9u^4-\pi e^{4u}}\\
|G_{ij,k}|&5u e^{9u+9u^4-\pi e^{4u}}\\
|B_{j,k}|&16400u^2e^{13u+9u^4-\pi e^{4u}}\\
|\mathcal R_k|&182160000u^3e^{17u+9u^4-\pi e^{4u}}
\end{array}                                                     \tag{C9}
\]

For B, use |p_j|≤2^ju^j and |p_j'|≤2^j(j+84)u^j, with j≤2.
All constants and reductions in C7–C9 are checked with exact fractions.

Each envelope has logarithmic derivative less than −540 on u≥1.
Indeed −4πe^{4u}<−600u³ and the positive logarithmic derivative
terms are bounded by respectively 48u³, 46u³, 51u³ and 56u³.
The root spacing is >3/85 and 540(3/85)>16. Since e⁴>50,
each root sum is at most its envelope at 1 divided by 1−50^{-4}.
The resulting safe upper bounds are

\[
\begin{split}
\Gamma_{\rm tail}&<1.674\times10^{-62},&
|(G_{\rm tail})_{ij}|&<1.057\times10^{-66},\\
|(B_{\rm tail})_j|&<1.892\times10^{-61},&
|\mathcal R_{\rm tail}|&<1.148\times10^{-55}.
\end{split}                                                     \tag{C10}
\]

No root after 1 is assumed absent. In particular R23's different
weighted-majorant bound beyond 2 is not reused as a C₄ error bound.

## 6. Enclosing the matrix solve

The finite sums are augmented by the signed tail intervals in C10;
Γ and the Gram diagonal receive nonnegative tail intervals. Interval
Sylvester minors certify G−I/200 positive definite. Set C to an exact
dyadic midpoint approximation to G^{-1}, and v₀ to an exact dyadic
point approximation to G^{-1}B. Compute E=I−CG and η=||E||∞. Then

\[
 \eta<9.27\times10^{-9}<1,\qquad
 \|G^{-1}B-v_0\|_\infty
 \le\frac{\|C(B-Gv_0)\|_\infty}{1-\eta}.                    \tag{C11}
\]

Thus the matrix inverse is validated by a residual inequality, not by
printing an ordinary numerical inverse. The rational checker independently
rebuilds G,B,E and this bound from the local input intervals.

Finally define

\[
\mathcal P=\tfrac12 B^TG^{-1}B,\quad\Xi=\mathcal R-\mathcal P,
\quad C_{4,\theta}=\delta_0^5
 \left(\frac{\Gamma^2}{3D^2}-\frac{\mathcal R}{D}
                         +\frac{\mathcal P}{D}\right),
\qquad D=f_3/\delta_0.                                      \tag{C12}
\]

The diagnostic central values are R≈356.5482685, P≈202.3577501,
Xi≈154.1905184. Full enclosures, rather than these decimals, are
propagated into the coefficient interval in (C2). Both computations independently lie in the strict
published C₄ interval. An exact-arithmetic negative control with the
wrong sign of P produces a disjoint interval and is rejected.

## 7. Interpretation and precise limit of the conclusion

The three contributions in C12 are approximately

\[
 C_{4,\theta}=
 \big[\underbrace{2.768449782}_{\text{amplitude normalization}}
      \underbrace{-0.639189600}_{\text{local shape}}
      \underbrace{+0.362769871}_{\text{moment correction}}\big]
      \times10^{-39}.                                      \tag{C13}
\]

This decomposes the coefficient at the same fixed b*,D,Γ. Removing
the moment constraints would change those base quantities, so the last
term is not the total difference between two unconstrained/constrained
problems.

The positive C₄ and R23's little-o statement imply that for some
uncomputed M₁,

\[
 \delta(M)>\delta_0+C_2/M^2\qquad(M\ge M_1).                 \tag{C14}
\]

For example, at M=2×10^{-5} the **formal terms** have
C₄/M⁴≈1.55752×10^{-20} and (C₄/M⁴)/(C₂/M²)≈6.76932×10^{-6}.
These are arithmetic evaluations of known terms, not enclosures of
δ(M) minus a truncated expansion at that budget. R16 remains the
available explicit finite-budget remainder theorem. Its bounds are
not sharpened by substituting a little-o statement at a fixed M.

This package establishes the fixed-theta coefficient and sign. It does
not give an effective fourth-order remainder, a numerical onset M₁,
a result uniform along the cusp curve, an exact finite-M optimizer,
or a new physical interpretation. The R19/R20 manuscript files remain
unchanged pending later integration and expert review.

[Numerical table](results/TABLE.md), [review](REVIEW.md),
[reproduction](README.md), [certificate](results/certificate.json).
