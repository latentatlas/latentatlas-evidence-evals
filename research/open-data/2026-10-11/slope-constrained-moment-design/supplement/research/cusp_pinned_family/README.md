# R08 — Pinned cusp family and finite fold nesting

Read [the Turkish research note](ARASTIRMA_NOTU.md) for the result and
its significance; [PROOF.md](PROOF.md) gives the derivation, analytic
assumptions, computer-assisted argument and exact trust boundary.
The [English TeX appendix](THEOREM_APPENDIX.tex) is a draft inclusion
for a future manuscript, not a compiled/submitted paper.

This package continues R07's exact cofactor-defined four-cosine
direction. It proves one connected cusp sheet for nu in [-29,0] and
physical epsilon in [-1/2,1/2], with exact fixed Q edge and two strict
finite fold nesting directions in the common centered root window.

## Evidence entry points

| Artifact | Role |
|---|---|
| [Family certificate](results/family_certificate.json) | 232 continuum cells, 402 explicit branch joins |
| [Rational continuum check](results/rational_check.json) | Separate downstream arithmetic and fold ODE verification |
| [H cache index](cache/index.json) | 58 hashed files, 69 rigorous H moments each |
| [Integral cross-check](results/integral_crosscheck.json) | 21 rigorous frequency-shift and nine mpmath comparisons |
| [Point certificates](results/point_certificates.json) | 21 narrow cusp roots identified with the sheet |
| [Finite fold samples](results/fold_samples.json) | 144 contractions at nine cusps and eight positive offsets |
| [Sample check](results/sample_check.json) | Separate rational point/fold checks |
| [Readable numbers](results/key_results.json) | Outward decimal values derived from certificates |
| [Figure metadata](figures/metadata.json) | Inputs and hashes for the two PNG/SVG figures |
| [Diagnostic history](DIAGNOSTICS.md) | Failed coarse bounds retained with their meaning |

## Verification without changing frozen results

From the project root, use its existing virtual environment:

    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/audit_snapshot.py

The audit checks preserved sources and evidence links. It does not run
all mathematics again. To rerun the rational continuum checker, choose
a fresh output path outside the frozen package:

    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/check_family.py --output /tmp/r08-new-rational-check.json

Similarly, run check_samples.py with a fresh --output path. Both reject
overwriting an existing report. The continuum checker imports no FLINT
or R08 generating modules. Its saved integral/Taylor range assumptions
remain explicit.

## Full rebuilding

Use a separate copy of the project with unchanged R01–R07 inputs and
an empty R08 cache, results and figures directory. Do not erase data
from this frozen evidence package. In that copy run, in dependency order:

    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/build_moment_cache.py --workers 2
    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/certify_family.py --output research/cusp_pinned_family/results/family_certificate.json
    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/check_family.py --output research/cusp_pinned_family/results/rational_check.json
    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/crosscheck_integrals.py --output research/cusp_pinned_family/results/integral_crosscheck.json
    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/certify_points.py --output research/cusp_pinned_family/results/point_certificates.json
    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/certify_fold_samples.py --output research/cusp_pinned_family/results/fold_samples.json
    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/check_samples.py --output research/cusp_pinned_family/results/sample_check.json
    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/summarize_results.py
    PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_pinned_family/plot_results.py

Runtime used: Python 3.12, python-flint 0.9.0, mpmath 1.4.1 and
matplotlib 3.11.2. Core quadrature uses 100 decimal digits; the shifted
integral check uses 110. The independent rational grids are 192 bits
for dimensionless continuum checks and 512 bits for very small point
residuals. Timings are recorded in outputs; runtime fields mean a new
run need not have byte-identical JSON hashes.

Figures have been visually checked. LaTeX compilation, external expert
review and a complete manuscript revision are not part of this package.
