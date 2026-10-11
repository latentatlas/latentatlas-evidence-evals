# R17 — R15–R16 proof clarifications

21 September 2026. This is a review addendum, not a new theorem or a
change of certified constants. The frozen R15/R16 texts remain intact.
This text makes two proof implications explicit and corrects one sentence
about the extent of a sum. External mathematical review is still pending.

## 1. Regularity of the infinite switch correction

In [R15 section 3](../kernel_slope_asymptotics/PROOF.md), choose one
fixed b smaller than the separation and boundary margins. Let
Q_lk=sup_{|u-z_k|≤b}|q^(l)(u)|, with the summability assumed there.
For one upward unit step define

    I_k(a)=−a/2 ∫₀¹(1−v)[q(z_k+av)−q(z_k−av)]dv.

The same formula defines an even function for |a|≤b, including zero.
Direct differentiation gives

    I_k''(a)=−∫₀¹v(1−v)[q'(z_k+av)+q'(z_k−av)]dv
             −a/2 ∫₀¹v²(1−v)[q''(z_k+av)−q''(z_k−av)]dv.

Consequently

    |I_k(a)| ≤ a²Q_1k/6,
    |I_k'(a)| ≤ |a|Q_1k/3,
    |I_k''(a)| ≤ Q_1k/3 + |a|Q_2k/12,
    I_k''(0)=−q'(z_k)/3.

The sums of these majorants converge. With jump factors |d_k|=2,
uniform convergence of the series and its first two derivatives proves
the asserted C² regularity and permits the second-order coefficient
to be summed. These are sums of local smoothing differences, not of
nonintegrable individual step tails. Only finitely many centers move;
their center and mixed derivatives are ordinary local derivatives.
No C³ hypothesis is being assumed. This supplies the detailed estimate
behind R15 lines 101–109 without changing its assumptions.

## 2. Why the R16 fixed point solves the moments and varies continuously

Write S=S_{0:2}, J=∂_cS(z,0), and use the exact dyadic B in R16.
The weighted row estimates imply

    ||I−BJ||_V ≤ max_i κ_i < 1.

The Neumann series makes BJ invertible. Since B and J are square,
B is invertible as well. Thus T_a(v)=v is equivalent to S(z+a²v,a)=0,
not merely to BS=0. The exact rational determinant calculation in
[the targeted check](results/review_algebra.json) independently checks
that this particular B is nonsingular. This is an explicit missing
sentence in the exposition, not a missing numerical hypothesis.

For bounded v the local shift integrals and the smoothing estimates give

    S(z+a²v,a)/a² = Jv−F+O(a),

uniformly on the recorded box. To see uniformity, the unsmoothed shift
remainder is O(a⁴) before division by a², while the smoothing remainder
is at most a³ ΣQ_2k/12. Moving finitely many smoothing centers contributes
O(a⁴). All constants have summable or finite bounds in R16. Therefore

    T_0(v)=(I−BJ)v+BF

is the continuous extension of T_a to zero. Uniform contraction yields
continuous fixed points v(a) on [0,a₀]. The parameter continuity estimate
uses the denominator 1−max κ_i; it is strictly positive. Positivity of
S₃ gives continuous α(a), and α(a)/a tends to infinity. Its value at a₀
is smaller than M₀. The intermediate value theorem covers every M≥M₀,
without assuming monotonicity or checking only finitely many budgets.

## 3. Correction to the wording about infinite tails

R16 section 4, line 150, says that every term in equation (3) includes
its infinite tail. Read literally, that is inaccurate for A₄. The
replacement sentence for a new manuscript is:

> B₂ and A₃ include all switches, with explicit infinite-tail bounds.
> A₄ contains only the three moved centers, since every other center is
> fixed. The forcing and the sums of moment second derivatives also
> include their infinite tails.

This corrects the description, not the formula or implementation.
Equation (3), the producer and the checker already use precisely these
index sets. No coefficient or downstream inequality changes.

## 4. Review of the two delicate sign and normalization points

For the lower remainder let P_k(v)=γ_kv−R_2k v²/2 and let b_±≥0 be
the two defects. Since both true weights are nonnegative and at least
P_k, the weighted pair is bounded below by

    max(0,P_k(v))(b_++b_−)
      ≥ max(0,P_k(v))(2δ*−2Mv)
      ≥ P_k(v)(2δ*−2Mv),      0≤v≤δ*/M.

Thus a negative Taylor lower bound at a far tail switch causes no
reversal of an inequality. Summing finite sets and then passing to
the absolutely convergent series is legitimate. R16 already includes
this positive-part argument; the review found no omitted tail loss.

For the upper remainder, the exact moment relation gives
D*e_a=αL(a), not δ*L(a). This α factor is retained throughout R16.
Substituting a=α/M and then absorbing the difference α³−δ*³ produces
the denominator D*−Γ U_bar²/M². Both this denominator and the final
rounded constants were checked with separate rational arithmetic.
The audit's polynomial check independently verifies the absorption
identity. In particular the factors 1/3, 1/6 and 1/12 have not been
confused with the magnitude-two jumps.

## 5. What this review does not upgrade

The unique dual coefficient vector a*, the three-center fixed point,
and a minimizer of the finite-M Lipschitz problem are different objects.
Only the first two have uniqueness assertions here. The constructed
ramp supplies an upper bound, not a characterization of the finite-M
minimizer. R13 proves equality of infima with smooth positive
fourth-order/rank-three designs, not existence of a smooth minimizer.
The original coordinate u and absence of mass normalization remain
part of the problem. None of the proofs transfers R10's root window
to the optimized kernels, proves a physical application, or settles
priority in the literature.
