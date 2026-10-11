# R26 — Quantitative evidence

The theorem is for the exact fixed theta cusp and exact R24 coefficients.
M is a Lipschitz slope budget. All strict bounds below are rounded outward
from [certificate.json](certificate.json) and checked independently by
[rational_check.json](rational_check.json).

| Quantity | Bound / value | Role |
|---|---:|---|
| Minimum budget M₀ | 2×10⁻⁵ | Sufficient onset; no upper budget |
| Maximum width a₀ | 2⁻¹⁴ | Local estimates hold for every 0<a≤a₀ |
| Active-tail threshold ε | 2⁻¹² | A root is active if ae^{4z}≤ε |
| Roots always retained | 28 below 1 | R25 finite-root estimates |
| Positive root-free tail gap | [1,1.001] | Fresh enclosure on expanded trial box |
| Root spacing after 1 | >3/85 | Phase bound, for original and trial roots |
| Signed trial density derivative on active cell | >200w(z)z³ | Balancing/support argument |
| S₁₂, S₁₆, S₂₄ | <3.027×10⁻⁶⁰, 1.653×10⁻⁵⁸, 4.926×10⁻⁵⁵ | Weighted sums of all tail roots |
| I₁₂, I₁₆, I₂₄ | <6.053×10⁻⁶³, 3.305×10⁻⁶¹, 9.851×10⁻⁵⁸ | Entire weighted integral tails |
| Moment tail bounds H_tail | <(1.866,3.732,7.463)×10⁻⁴⁶ | Constants multiplying a⁴ |
| Target tail constant K_tail,6 | <8.411×10⁻³⁵ | Constant multiplying a⁶ |
| Added support tail constant | <3.366×10⁻⁴⁰ | Constant multiplying a⁸ |
| Three contraction rows | <(.0014891,.0020451,.0024510) | Exact moment repair |
| Three forcing rows | <(.257845,.351476,.418263) | Each forcing + contraction <1 |
| K_d | <467733 | Global normalized support error /a⁶ |
| K_p | <3963115 | Global normalized primal error /a⁶ |
| Upper amplitude U | <9.178748657×10⁻¹⁰ | Feasibility and kernel positivity |
| Scalar upper endpoint margin | >1.76868×10⁻¹⁵ | Works uniformly for all M≥M₀ |
| Auxiliary scalar derivative | >0.0003634068639 | Existence/uniqueness of auxiliary root |
| Lower-error constant K₋ | <9.593×10⁻⁵⁴ | Lower side of optimal-value enclosure |
| Upper-error constant K₊ | <1.488×10⁻⁵³ | Upper side of optimal-value enclosure |
| C₄ (R24 input) | (2.49203004,2.49203006)×10⁻³⁹ | Positive exact coefficient |

Consequently, for every M≥M₀,

    −9.593×10⁻⁵⁴/M⁶ < δ−P₄ <1.488×10⁻⁵³/M⁶,
    1−9.624×10⁻⁶(M₀/M)² < (δ−δ₀−C₂/M²)/(C₄/M⁴)
                           <1+1.493×10⁻⁵(M₀/M)².

At M₀ the absolute error is <2.325×10⁻²⁵; relative to C₄/M₀⁴,
it is <0.001493 percent. These compare exact mathematical quantities.
They are not extra known decimal digits of δ(M) computed with rounded inputs.

The exact check has 22 groups. The outward rational checker has 22
decision inequalities. The independent diagnostic uses roots with phase
indices 27,40,53,80 and widths a=εe^{-4z}/2 and a=εe^{-4z}; both
90- and 130-digit runs pass 300 local inequalities each. It stores the
normalized jets and remainders explicitly. Across the 40 residual
comparisons, the largest relative change is about 2.8072×10⁻⁶⁹.
This is numerical corroboration at central inputs, not a rigorous bound
for all parameter choices or all distant roots.

The proof of a-independent constants and budget coverage is
[G3–G13](../PROOF.md). [Review and limits](../REVIEW.md),
[figure caption](../FIGURE_CAPTIONS.md), [reproduction](../README.md).
