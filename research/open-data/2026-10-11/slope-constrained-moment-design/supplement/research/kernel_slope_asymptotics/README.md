# R15 — Sharp large-slope cost law

At the same original exact Q and four moment target as R11–R14,

    δ(M)=δ*+C*/M²+o(M⁻²),
    9.20340371e-25 < C* < 9.20340375e-25.

The general analytic theorem assumes simple separated switches,
summable density derivatives, and an invertible selected-switch
moment matrix. A new certificate validates those hypotheses for the
theta example, including a unique exact dual optimizer neighborhood.

- [Research note](ARASTIRMA_NOTU.md), [proof draft](PROOF.md).
- [Certificate](results/asymptotic_certificate.json).
- [Independent rational reconstruction](results/asymptotic_check.json).
- [Separate root and quadrature check](results/coefficient_crosscheck.json).
- [Exact algebra checks](results/algebra_check.json).
- [Figures and captions](FIGURE_CAPTIONS.md), [reference scope](REFERENCES.md).
- [Diagnostics](diagnostics/NOTES.md), [closure audit](audit_report.json),
  [frozen identities](manifest.json).

The asymptotic formula has no explicit finite-M remainder here. The
separate lower excess inequality holds for all M≥0.00002. The finite-M
two-sided interval remains the R14 result. No exact finite-M optimizer,
new physical model or literature priority is asserted.

## Read-only closure

From the project or Desktop publication-copy root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_asymptotics/audit_snapshot.py
```

The audit checks all 15 prior manifests and their frozen file hashes.
It validates evidence identities and status, not the analytic proof.
Do not disable Python assertions with `-O`.

## Rebuild into new paths

Use a fresh output directory. These commands refuse to overwrite output:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_asymptotics/certify_asymptotics.py --output /tmp/r15-new/certificate.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_asymptotics/check_asymptotics.py --output /tmp/r15-new/check.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_asymptotics/crosscheck_coefficient.py --output /tmp/r15-new/crosscheck.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_asymptotics/check_algebra.py --output /tmp/r15-new/algebra.json
```

The checker and crosscheck read the recorded certificate in their own
package tree. To check a regenerated producer output, use a disposable
copy of the full research tree and put the new certificate at its
expected path there. Runtime metadata changes whole-file hashes;
compare numerical enclosures separately.

The producer uses python-flint/Arb. The rational and algebra checkers
use only the standard library and, for intervals, the frozen R11
helper. The independent numerical comparison uses mpmath. Figures
use numpy/matplotlib. Versions are in [runtime.json](runtime.json).
Run `plot_results.py` only in a disposable copy if frozen image bytes
must remain unchanged.
