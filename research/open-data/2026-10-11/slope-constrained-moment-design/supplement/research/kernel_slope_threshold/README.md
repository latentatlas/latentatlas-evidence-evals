# R14 — Finite slope threshold

Same exact Q and moment target as R11–R13. This package narrows δ(M)
at M=0.00002 to

`0.000000000917873080 < δ(M) < 0.000000000917876530`.

The lower bound applies to all feasible bounded Lipschitz h. The upper
bound has an explicit even real-analytic positive exact-order-four,
rank-three witness. No whole optimal curve or exact minimizer is claimed.

- [Research note](ARASTIRMA_NOTU.md), [proof draft](PROOF.md).
- [Certificate](results/slope_threshold_certificate.json).
- [Independent rational check](results/slope_threshold_check.json).
- [Separate original-coordinate quadratures](results/moment_crosscheck.json).
- [Figure captions](FIGURE_CAPTIONS.md), [references and scope](REFERENCES.md).
- [Closure audit](audit_report.json), [frozen file identities](manifest.json).

## Read-only closure

From the project or publication-copy root, with the recorded environment:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_threshold/audit_snapshot.py
```

The prior 14 manifests and their frozen file hashes are checked. The
closure validates identities and existing evidence; it is not a new
analytic proof. Use Python assertions normally; do not run with `-O`.

## Reconstruct calculations

Do not overwrite frozen outputs. The following commands use explicit
new paths; choose a fresh directory if these paths already exist:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_threshold/check_threshold.py --output /tmp/r14-new/check.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_threshold/certify_threshold.py --output /tmp/r14-new/certificate.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_slope_threshold/crosscheck_moments.py --output /tmp/r14-new/crosscheck.json
```

The checker and crosscheck read the **recorded certificate in their
package tree**. To audit a fresh producer output, copy the complete
research tree to a disposable location and install the fresh certificate
at its expected path there before invoking the checker. A rebuilt output
will have different runtime metadata and is not expected to have the same
whole-file hash. Compare numerical enclosures and statuses.

`probe_candidate.py` is the nonrigorous floating-point design search; its
constants become exact binary rationals in the certificate. The proof
does not assume the probe found any exact optimizer or exact root.
`plot_results.py` renders illustrations from the recorded results; run it
only in a disposable copy if preserving the frozen figure bytes matters.

The producer uses python-flint. The independent checker needs only the
standard library and the frozen R11 rational interval helper. The separate
quadrature uses mpmath. numpy is used only for the candidate probe and
plotting, and matplotlib only for figures. Versions are in `runtime.json`.

The analytic arguments and local transcendental/integral bounds have
explicit trust boundaries in the proof and reports. No external reviewer
or formal proof assistant has approved this package.
