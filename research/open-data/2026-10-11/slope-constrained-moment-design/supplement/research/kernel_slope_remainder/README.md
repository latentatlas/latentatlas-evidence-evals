# R16 — Explicit uniform remainder for the slope-cost law

For every M≥0.00002, at the same exact Q and four moment target,

    C*/M² − 9.624e-33/M³ < δ(M)−δ* < C*/M² + 2.167e-32/M³.

Thus the relative error of the leading excess C*/M² is less than
0.001178·0.00002/M. At M=0.00002 the total threshold is enclosed by

    (0.00000000091787309568619750, 0.00000000091787309964331750).

- [Research note](ARASTIRMA_NOTU.md), [proof](PROOF.md).
- [Arb certificate](results/remainder_certificate.json).
- [Rational reconstruction](results/remainder_check.json).
- [Separate derivative samples](results/derivative_crosscheck.json).
- [Numerical ramp reconstruction](results/design_crosscheck.json).
- [Exact remainder factors](results/algebra_check.json).
- [Figure captions](FIGURE_CAPTIONS.md), [development diagnosis](diagnostics/NOTES.md).
- [Closure audit](audit_report.json), [frozen identities](manifest.json).

This is a rigorous-arithmetic-backed analytic proof draft, not an
external referee report or formal proof. The numerical ramp run is
corroboration and does not define the certified exact family.
Literature positioning remains the limited comparison recorded in
[R15 references](../kernel_slope_asymptotics/REFERENCES.md).

## Read-only verification

Using the recorded runtime from the project or publication-copy root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_remainder/audit_snapshot.py
```

The audit checks 16 prior manifests and 780 frozen file entries. It
checks the evidence chain, not a formalization of the analytic proof.
Do not run Python with `-O`.

## Rebuild calculations

Choose a fresh output directory; these commands refuse overwrites:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_remainder/certify_remainder.py --output /tmp/r16-new/certificate.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_remainder/check_remainder.py --output /tmp/r16-new/check.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_remainder/crosscheck_derivatives.py --output /tmp/r16-new/derivatives.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_remainder/crosscheck_design.py --output /tmp/r16-new/design.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_remainder/check_algebra.py --output /tmp/r16-new/algebra.json
```

The checker and crosschecks read the recorded certificate in their
package tree. To check a regenerated certificate, use a disposable
copy of the whole research tree and install the new certificate at
its expected path there. Compare numerical enclosures separately
from variable runtime metadata.

The producer requires python-flint. The rational/algebra checkers use
the standard library and the frozen R11 rational-interval helper.
Crosschecks use mpmath; plots use numpy/matplotlib. See
[runtime.json](runtime.json) for versions. Run `plot_results.py` in a
disposable copy when frozen figure bytes must remain unchanged.
