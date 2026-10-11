# An independent example with genuinely infinitely many switches

This exponential/trigonometric control problem is separate from the theta
family. Its infinite tail can be summed exactly, which tests the R23
formulas without replacing a half-line problem by a compact one.

## 1. Exact setup

On u≥0, define

\[
 L=\frac{e^{-1/2}}{1-e^{-1}},\quad
 D=\frac{1+2\pi L}{1+\pi^2},\quad c=\frac{1-D}{\pi D},\quad
 q_1=e^{-u}\cos(\pi u),\quad q_0=e^{-u}[\sin(\pi u)-c\cos(\pi u)],
 \quad f=D/4.                                                \tag{E1}
\]

Let b*=0, so q*=q₁ and z_k=k+1/2 for k≥0. Direct integration yields
∫|q₁|=D, and integration of q₁' sign(q₁) gives
∫e^{-u}sin(πu)sign(q₁)=(1−D)/π. Consequently ∫q₀ sign(q₁)=0,
and δ₀=1/4. The root evaluation q₀(z₀) is nonzero. In fixed root
neighborhoods all densities/derivatives and coercivity constants scale
as e^{-k}; K_k stays bounded and W3 is a convergent geometric series.

The coefficients reduce exactly to

\[
 \Gamma=\pi L,\quad G=2L/\pi,\quad B=L/(3D),\quad
 v=\pi/(6D),\quad\kappa=\tfrac13-\frac1{6D},\quad
 \mathcal R=\Gamma(11+3\pi^2)/180,\quad
 \mathcal P=\Gamma/(36D^2),\quad\Xi=\mathcal R-\mathcal P.
                                                               \tag{E2}
\]

Here q*''/q*'=−2 and q*'''/q*'=3−π² at every zero. C₂ and C₄ follow
from W5. These are coefficients for E1 only, not theta coefficients.

## 2. Exact whole-tail moments and balanced residual

Place ramp centers at k+1/2+d, all with half-width a. The profile starts
at +1, descends at its first ramp, and alternates. For |d|+a<1/2,
it obeys s(u+1)=−s(u). With s₀=−1+iπ, put

\[
 E(d,a)=e^{s_0d}\frac{\sinh(s_0a)}{s_0a},\qquad
 Z(d,a)=-\frac1{s_0}+\frac{2iL}{s_0}E(d,a).
                                                               \tag{E3}
\]

Integrating exponential primitives on all plateaus and ramps gives
∫q₁s=Re Z and ∫q₀s=Im Z−c Re Z. Equivalently, either integral is
its direct [0,1] integral divided by 1−e^{-1}; the latter form is
used by the independent quadrature check.

The lower moment determines the local root d(a) of

\[
 F(d,a)=\operatorname{Im}Z-c\operatorname{Re}Z=0,\qquad
 b(a)=-\frac{\operatorname{Im}E}{\operatorname{Re}E+c\operatorname{Im}E}.
                                                               \tag{E4}
\]

The second formula makes every ramp balanced for q_b=q₁−bq₀,
because its cell integral is proportional to
Im[(1+bc+ib)E]. The moment derivative at (0,0) is 2L>0,
so the local branch exists. For each certified sample below, Arb
separately checks a bracket for d, positivity of F_d throughout the
bracket, nonzero denominator in E4, and strict opposite residual signs
at the first cell endpoints. Trigonometric periodicity then supplies
all later cells, with no omitted roots, and q_b(0)=1+bc>0 fixes the
initial sign. The support argument W9 proves the sampled profile is
the true global amplitude optimum at

\[
        A(a)=\frac{f}{\operatorname{Re}Z(d(a),a)},\qquad
        M(a)=A(a)/a,\qquad \delta(M(a))=A(a).                 \tag{E5}
\]

This is a pointwise certification of six implicit budgets, with their
enclosures. It does not assign a finite-budget optimum to an arbitrarily
rounded decimal M, and it does not certify every width in an interval.

## 3. Independent fourth-order calculation and the tail

Expanding E3 directly with d=κa²+νa⁴+o(a⁴) gives

\[
 \operatorname{Re}Z=D-\Gamma a^2/3+
 \Gamma\left[-\kappa^2+2\kappa/3-(3-\pi^2)/60\right]a^4+o(a^4)
 =D-\Gamma a^2/3+\Xi a^4+o(a^4).                            \tag{E6}
\]

The unknown ν cancels from the real part. `check_algebra.py` verifies
this exact complex-polynomial identity independently of the local-jet
formula, and checks the leading moment equation. The coefficient
series for Γ,G,B,R each retain exactly a fraction e^{-N} of their
total after the first N roots. When all these series are truncated
together, P also scales by 1−e^{-N}, whereas the Γ² part of C₄ scales
by (1−e^{-N})². Thus one must not simply scale the whole C₄ linearly
with the omitted fraction.

`certify_example.py` uses Arb at 100 decimal digits and 220 bisection
steps. Output intervals are exact dyadic endpoints. Separately,
`crosscheck_integrals.py` solves the original piecewise [0,1] moment
integral and integrates the target at 80/120 digits, using the exact
geometric tail factor. It does not use E3 to solve the moments.

The plotted fourth-order residual is M⁴[A−δ₀−C₂/M²]. Its limiting
value is C₄; a smooth plotted curve is numerical illustration, while
the marked budgets refer to certified interval records.

[Table](results/TABLE.md), [certificates](results/certificate.json),
[independent integrals](results/integrals.json), [figure](figures/infinite_switches.png).
