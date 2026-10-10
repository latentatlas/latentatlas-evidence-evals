# Applying R23 to the fixed theta cusp

The exact cusp Q and exact unrestricted dual b* are the objects certified
in R12/R15, not their decimal centers. This application inherits that
localization, the zero sign-moment equations, the finite root cover, and
the nonzero three-switch determinant. It does not relabel an approximate
dual point as the optimizer.

## 1. Model and inherited topology

\[
\begin{split}
\Phi(u)&=\sum_{n\ge1}\pi n^2e^{5u}(2\pi n^2e^{4u}-3)e^{-\pi n^2e^{4u}},\\
w(u)&=\Phi(u)e^{\lambda u^2+\mu u^4},\quad
p_j(u)=(2u)^j\cos(2\tau u+j\pi/2),\quad q_j=wp_j,\quad 0\le j\le3.
\end{split}                                                     \tag{T1}
\]

Here 41<τ<42, −4<λ<0, 0<μ<9. All theta summands are positive for
u≥0, and every compact interval admits termwise derivatives of all
orders, by the Gaussian decay in n. The densities and their polynomial
moments are integrable. R15 encloses all 28 roots in [0,1] and proves
tail phase monotonicity for the whole dual coefficient cube. In that cube,
|b₀|<1/1000, |b₁|<1/10, |b₂|<1/200, and

\[
r_b=A\sin(2\tau u)+B\cos(2\tau u)=T\sin\varphi,\quad
A=8u^3+2b_1u,\ B=4b_2u^2-b_0,\ T=(A^2+B^2)^{1/2}.
                                                               \tag{T2}
\]

For u≥1, T>7u³, |T'|<25u² and 81<φ'<85. Consecutive tail zeros
are separated by more than 3/85. At a root, the absolute residual
derivative exceeds 567u³. Consequently, using the max norm on b,
the sum of absolute parameter derivatives of a root is at most
(1+2u+4u²)/(567u³)≤1/(81u)<1/80 for u≥1.

Take ρ≤1/1000. Shrink the coefficient neighborhood inside the inherited
cube so every root moves less than ρ/4. For roots z_k≥2 and x∈N_k,
|φ(x)−φ(z_k(b))|≤85·5ρ/4. Thus, after accounting for orientation,

\[
 \sigma_k r_b'(x)\ge
 \left[567\left(1-\tfrac12(425\rho/4)^2\right)
              -25(425\rho/4)\right]x^3>550x^3.                \tag{T3}
\]

There are only finitely many roots below 2. Their simplicity and the
inherited sign cover permit a further reduction of ρ and of the same
coefficient neighborhood to get the corresponding positive derivative
bounds there. Compact nonzero gaps prevent additional roots. The tail
phase labeling and finite continuity give the uniformly Lipschitz root
motion and unchanged orientations required in R23. This step asserts
existence of a smaller neighborhood, not an explicit numerical onset.

## 2. Derivatives through order three

For x=πn²e^{4u}, differentiation of πn²e^{5u−x}P(x) replaces P by
(5−4x)P+4xP'. The four polynomials are

\[
\begin{split}
P_0&=-3+2x,\\
P_1&=-15+30x-8x^2,\\
P_2&=-75+330x-224x^2+32x^3,\\
P_3&=-375+3270x-4232x^2+1440x^3-128x^4.
\end{split}                                                     \tag{T4}
\]

For each absolute monomial the successive-n ratio is at most
2¹⁰ exp(−3π)<1/2, for u≥0. Twice the n=1 term therefore bounds
each sum. All derivatives Φ^{(ℓ)}, ℓ≤3, are bounded by C_ℓ times
exp(21u−πe^{4u}), where an integer upper constant is
C_ℓ=2Σ_j |[x^j]P_ℓ|4^{j+1}, using π<4.

For P=λu²+μu⁴, bounds for e^{-P}(e^P)^{(ℓ)} are respectively
1, 44(1+u)³, 2052(1+u)⁶, 100712(1+u)⁹. Combining the product
rule with |2τ|<84 gives the following explicit common envelope for
the sum E_k of all q_j derivatives through order three:

\[
 E_k\le\overline E(z_k):=C_E(1+z_k+\rho)^{12}
 \exp\{21(z_k+\rho)+9(z_k+\rho)^4-\pi e^{4(z_k-\rho)}\},
 \qquad C_E=4980928512.                                      \tag{T5}
\]

The integer product-rule construction of C_E and all four P_ℓ are
recomputed in `check_algebra.py`; no fitted tail constants are used.

## 3. A positive crossing bound, even in the tiny-density tail

For u≥1 the first theta summand is at least
π²e^{9u}e^{-πe^{4u}}>e^{-πe^{4u}}. Since λ>−4 and μ>0,
w(u)>exp(−4u²−πe^{4u}). T3 and the mean value theorem therefore give
the R23 coercivity bound with

\[
 L_k=\exp\{-4(z_k+\rho)^2-\pi e^{4(z_k+\rho)}\},
 \quad z_k\ge2.                                             \tag{T6}
\]

All |b_j|<1, so C_U=1 is valid when E_k includes q₀,...,q₃.
With K_k=E_k/(6L_k),

\[
 E_k(1+K_k)^2\le 2\overline E(z_k)+
 \frac{C_E^3}{18}(1+z_k+\rho)^{36}
 e^{63(z_k+\rho)+27(z_k+\rho)^4+8(z_k+\rho)^2
                    -\pi c_\rho e^{4z_k}},\quad
 c_\rho=3e^{-4\rho}-2e^{4\rho}>97/100.                       \tag{T7}
\]

The sign of c_ρ is the crucial check: the inverse-density factors in
the center bound must not overwhelm the density decay. Its rational
lower bound follows from e^{-4ρ}≥1−4ρ and e^{4ρ}≤1/(1−4ρ).
Both envelopes in T7 have logarithmic derivative below −1 for z≥2.
For example the positive terms in the logarithmic derivative of the second envelope are at most
223(z+ρ)³, while its negative term exceeds 1000(z+ρ)³. Use
e⁸>2500, z+ρ<3 at z=2, and monotonicity of e^{4z}/(z+ρ)³.
The first envelope has the weaker positive bound 69(z+ρ)³ and the
same argument applies. This estimate concerns logarithmic derivatives
with respect to z, not a second derivative of a density.

Uniform root separation now gives a geometric summation bound:
the sum of either envelope over roots z_k≥2 is at most its value
at 2 divided by 1−exp(−3/85). `certify_example.py` also evaluates
this conservative whole-tail bound with Arb. Finitely many remaining
neighborhoods contribute finite amounts. Hence W3 holds for the
entire half-line; roots beyond a cutoff have not been discarded.

The rank and sign-moment hypotheses are inherited from R15. Therefore
R23 gives the **fixed-Q theta corollary**

\[
 \delta_\theta(M)=\delta_*+C_2M^{-2}+C_{4,\theta}M^{-4}
                         +o(M^{-4}),                         \tag{T8}
\]

where C₂ is the previously certified R15 constant, and C_{4,θ} is the
absolutely convergent series/matrix expression W4–W5 at the exact b*.
This establishes existence and the formula, not a numerical enclosure
or sign of C_{4,θ}. It is compatible with the older, weaker explicit
R16 M^{-3} remainder bound, which remains unchanged.

## 4. Why an unweighted center hypothesis would fail

At a fixed residual zero, the fixed-b balanced-center coefficient is
κ_k^0=−q*''(z_k)/(6q*'(z_k)). The first theta term and its derivative
dominate at infinity, giving

\[
 \frac{w'}w=-4\pi e^{4u}+4\mu u^3+2\lambda u+9+O(e^{-4u}),
 \quad \frac{r_*''(z_k)}{r_*'(z_k)}=O(1/z_k),\quad
 \frac{\kappa_k^0}{e^{4z_k}}\longrightarrow\frac{4\pi}{3}.
                                                               \tag{T9}
\]

The O(1/z_k) residual ratio follows by differentiating T sin φ at
its zeros: 2T'/T+φ''/φ'. T∼8u³ and θ=atan(B/A)=O(1/u).
The finite-dimensional correction Q_kᵀv/r_k is O(1/z_k), so the
same leading divergence occurs for κ_k in W8. A common bound
|c_k−z_k|≤C a² for all k and all small a cannot hold: its pointwise
a→0 limit would bound every κ_k. Nevertheless the actual balanced
center always obeys |c_k−z_k(b)|<a. The limits k→∞ and a→0 must
not be interchanged without weights.

## 5. Evidence boundary

This is an analytic corollary using frozen R12/R15 hypotheses. It is
not a fresh validated theta C₄ computation, an effective fourth-order
error estimate, or a theorem uniform along the cusp curve. The new
Arb tail certificate covers T7's weighted majorant and its auxiliary
constants; it does not mechanically verify the proof of W5.

[General proof](PROOF.md), [review](REVIEW.md),
[infinite-switch example](EXAMPLE.md).
