# Development history

All 32 first-pass remainder cells passed without changing the old
published constants. The separate rational remainder/AD checker and the
exact comparison checks passed on their first executions.

The first figure QA failed because Matplotlib's automatic logarithmic
major ticks included an off-axis 10³ label. No figure was accepted at
that stage. `plot_before_tick_fix.py` preserves the source, and
`plot_tick_failure.json` records its hash and cause. The final source
sets its intended major ticks explicitly and retains the canvas check.
A later visual inspection moved the legend into the empty gap between
the two separation curves. Neither layout change altered a mathematical
input or inequality.

The first closure audit also failed an invalid representation assertion:
it required the Arb enclosure of M₀=2e-5 to have exact endpoints equal to
1/50000. That rational is not dyadic. The corrected audit checks containment
of the exact rational and an interval width <10⁻¹²⁰. The separate outward
rational checker had used the exact Fraction from its first successful
run. The failed audit source, JSON explanation and log are retained as
`audit_before_rational_budget_fix.py` and `rational_budget_audit_failure.*`.
No mathematical producer, bound, or certificate was changed.

The tiny-separation cases in `results/comparisons.json` are deliberate
negative controls: the sufficient comparison inequality cannot resolve
those pairs. This is a limit of the bound, not evidence of reversed
ordering for the actual optimum.
