# R15 figure captions and interpretation

## Figure 1 — Local transition mechanism

[PNG](figures/linear_transition_loss.png),
[SVG](figures/linear_transition_loss.svg).

Uniform-box smoothing turns an isolated sign jump into a linear ramp.
In the normalized coordinate x=(u−z)/a its dual-loss profile near a
simple residual zero is |x|(1−|x|) on [-1,1], with integral 1/3. With
a∼δ*/M, the weighted local loss is proportional to M⁻². Exact moment
correction and summation over switches are required for the theorem;
the picture alone does not prove it. The ramp is an asymptotic
construction, not a computed exact finite-M optimizer.

## Figure 2 — Distribution of the leading-coefficient weights

[PNG](figures/switch_contributions.png),
[SVG](figures/switch_contributions.svg).

The 28 certified residual switches in [0,1] contribute positive weights
w(zₖ)|r*′(zₖ)| to Γ. Bars and the cumulative curve use midpoints of
enclosures uniform over the localized exact dual optimizer. Interval
widths are too small to resolve at this plotting scale. The infinite
tail beyond 1 is bounded separately by 5.705×10⁻⁶³. These switches
are optimization data, not an assertion that the integral has 28 roots.

Source: `results/asymptotic_certificate.json`. Neither figure plots an
unverified optimal value curve, empirical data, or a physical system.
