# R07 diagnostic history — retained, not promoted to counterexamples

All entries refer to 20 September 2026 and the frozen R03–R05 inputs.

| Attempt | Scope | Outcome | Meaning |
|---|---|---|---|
| Relative budget 10^-19 | Cells 0, 28, 57 | Passed | Preliminary sample only |
| Relative budget 10^-18 | Cells 0, 28, 57 | Passed | Candidate for full proof |
| Relative budget 10^-17 | Cells 0, 28, 57 | Cell 0 passed; cell 28 failed semicubical bounds; cell 57 failed cubic bounds | These fixed sufficient bounds do not prove that budget; no mathematical counterexample |
| Relative budget 10^-18 | All 58 cells, 57 joins | Arb passed | Full generating certificate |
| First rational checker | First cell, radius comparison | Assertion before geometry | Artificial enclosure widening of an exact preconditioner made a very tight radius comparison fail |
| Corrected rational checker | Cells 0, 28, 57, then all 58 and 57 joins | Passed | Exact dyadic Y used as exact Fraction in the radius formulas; subsequent interval operations remain outward-rounded |
| Cosine direction | Six rigorous integrals; three direct mpmath moments | Passed | Large infinitesimal sensitivity, not a finite perturbation failure |
| Four-mode moment annihilation | Forty rigorous integrals; exact cofactor identity; rational signs; five direct moments | Passed | One exact cusp stays fixed and nondegenerate for amplitudes [-1/2,1/2]; no whole-arc assertion at that amplitude |

Sample outputs: [10^-19](probe_1e-19.json), [10^-18](probe_1e-18.json),
[10^-17](probe_1e-17.json). They intentionally use the status
`diagnostic_only`; passing three cells is not a theorem on the whole arc.

The preliminary probe required positivity of the normalized width-rate
lower bound and an upper bound 0.01. The full generator tightened these
to 0.0003 and 0.003 before the full run. All passed diagnostic cells also
meet the tighter constants. Removing a redundant exponent `**1` in a
display-rate formula did not change the mathematics.

The first checker failure occurred at
`assert all(need <= used < Ri ...)`. The initial checker computed
absolute Y entries from 192-bit outward intervals instead of their
exact stored dyadics. That extra rounding could exceed the very fine
110-decimal-digit generator radius by a tiny amount. The correction
does not weaken the comparison or add a tolerance: the input dyadics
are read as exact fractions for E and Q, and the same strict inequalities
are checked. The main Arb certificate was not edited or regenerated.

No older package was changed, and no failed inequality was relabeled
as evidence of the opposite mathematical statement.

The first figure render put the overall title too close to the panel
titles. The layout was revised and both figures were rendered and
inspected again before freezing the package. No scientific data were
changed by that layout correction.
