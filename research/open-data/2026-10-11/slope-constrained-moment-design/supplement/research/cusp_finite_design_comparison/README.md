# R30 — Finite-budget design comparisons on a cusp arc

For the exact cusp driver −1/64≤ν≤0 and every M≥2×10⁻⁵, the effective
remainder of R27 now holds on the entire R29 arc with the same constants:

    −1.02×10⁻⁵³/M⁶ < δ_ν(M)−δ₀(ν)−C₂(ν)/M²−C₄(ν)/M⁴ <1.64×10⁻⁵³/M⁶.

Together with positive derivative bounds for all three coefficients,
this gives strict comparisons of actual optimal values at quantitatively
separated drivers. In particular the 33 nodes −1/64+k/2048 are strictly
ordered for every allowed budget, both for δ and for the normalized
fourth-order contribution Z_M. Monotonicity at arbitrarily close drivers
is not proved. Each driver has its own moment target and allows its own g.

- [Türkçe bulgu notu](BULGU_NOTU_TR.md)
- [Analytic proof and precise scope](PROOF.md)
- [Numerical table](results/TABLE.md)
- [Review and trust boundaries](REVIEW.md)
- [Scientific figure](figures/finite_design_comparison.png) and [caption](FIGURE_CAPTIONS.md)
- [Audit record](audit_report.json) and [manifest](manifest.json)
- [Diagnostic history](diagnostics/README.md)

Keep the full research tree, the runtime in [requirements.txt](requirements.txt),
and assertions enabled. From any working directory:

```sh
python3 /path/to/research/cusp_finite_design_comparison/audit_snapshot.py
python3 /path/to/research/cusp_finite_design_comparison/audit_snapshot.py --with-arb
```

The default audit checks all previous frozen bytes, freshly reconstructs
exact algebra, rational remainders/AD, and exact value comparisons, and
runs the R29 prerequisite audit. `--with-arb` also regenerates this
package's 32-cell remainder cover and the R29 prerequisite chain, comparing
output bytes. It does not rerun the old mpmath diagnostics or formally
prove the analytic text.

Separate producers require fresh output paths:

```sh
python3 check_algebra.py --output /tmp/r30-algebra-new.json
python3 certify_remainder.py --output-dir /tmp/r30-cover-new
python3 check_bounds.py --cover-dir /tmp/r30-cover-new --output /tmp/r30-rational-new.json
python3 compare_values.py --output /tmp/r30-comparisons-new.json
```

The producer uses the recorded R30 algebra and frozen R29 cusp, dual and
coefficient cells; the comparison script uses the recorded rational check.
Modify only a disposable copy after freezing. No old manuscript or frozen
package is modified. This is a private research package, not a journal
submission or public release. The precise
[certification terminology](../theta_effective_remainder/CERTIFICATION_TERMINOLOGY_TR.md)
continues to apply to validated numerical enclosures, not to a blanket
claim that every analytic argument has been independently certified.
