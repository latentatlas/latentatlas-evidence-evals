# R03 — Certified connection of quartic and sextic cusps

This package extends the frozen `../cusp_verified` (R01) and
`../cusp_region` (R02) packages. Their 25 and 24 recorded files are
verified before generating the result. The mathematical conclusion and
its limits are in [the Turkish research note](ARASTIRMA_NOTU.md), with
the detailed argument in [PROOF.md](PROOF.md).

The result is one analytic cusp graph in the recorded tubes for
ν∈[−29,0], containing the two earlier exact cusp points. It has
F_ttt>8×10^-14, independent λ,μ controls, and 0.26<dμ/dν<0.34. Its
intersection with μ=0 is unique. This is not a classification of other
branches or a uniform extension of the R02 finite root-count region.

## Reproduction

The existing `.venv-math` environment uses Python 3.12.14,
python-flint 0.9.0 and mpmath 1.4.1. Plotting uses matplotlib 3.11.2.
Dependency pins are in `../cusp_verified/requirements.txt` and
`../cusp_verified/requirements-plot.txt`. Preserve both input packages
and their manifests together with this package.

From `/PROJECT`:

```sh
.venv-math/bin/python research/cusp_connection/explore.py
.venv-math/bin/python research/cusp_connection/certify_connection.py
.venv-math/bin/python research/cusp_connection/check_connection.py
.venv-math/bin/python research/cusp_connection/test_connection.py
.venv-math/bin/python research/cusp_connection/check_independent.py
.venv-math/bin/python research/cusp_connection/plot_connection.py
```

Run in this order: all checks read the complete connection certificate.
Do not use `-O` or `-OO`; the rational checker rejects disabled assertions.
The commands write only the new package's outputs and Python import
caches. They do not modify the original manuscript or the recorded
R01/R02 scientific files. A fresh copy of the complete project is
preferable when reproducing, so the supplied result snapshot is retained.

The full certifier independently refines each center and recomputes all
central integrals and derivative majorants. The discovery file supplies
candidate starting values only. No sampled candidate is itself accepted
as a path certificate. The completed discovery took about 88 seconds,
the full certification 163 seconds, the regression checks 7 seconds, and
the mpmath comparison 17 seconds in the recorded environment. Runtime
elsewhere will differ.

The optional `certify_connection.py --trial` tests the first cell only
and writes `results/trial_cell.json`. It does not establish the complete
curve, its joins, or endpoint identity. The archived development trial
is in `diagnostics/`.

Runtime metadata means a newly generated JSON file may have a different
byte hash even if the mathematical witnesses agree. After regenerating
the main certificate, regenerate every dependent check and plot. The
included `manifest.json` records this completed snapshot; it must not be
treated as a current manifest for subsequently changed files. Terminal
output from the recorded runs was captured separately in the `.log`
files; the commands above display their output rather than recreate
those logs automatically.

## Package contents

- `explore.py`: candidate continuation from both old cusps; numerical
  discovery, not a continuum proof.
- `bridge_taylor.py`: four-variable Taylor enclosures, analytic
  remainders, correlated predictors, and combined preconditioned entries.
- `certify_connection.py`: all 58 uniform contractions, 57 joins,
  identification of both exact old cusps, and derivative signs.
- `check_connection.py`: a separate exact-Fraction expansion using
  multinomial enumeration, including contractions, joins, endpoint
  identity and uniform slope bounds. It imports only the frozen R02
  rational interval helper and standard Python modules.
- `test_connection.py`: four groups covering 42 direct derivative
  comparisons, six preconditioned Jacobian comparisons, 18 predictor
  residual components, exact tangent algebra, and invalid domains.
- `check_independent.py`: 18 mpmath derivative comparisons without FLINT
  or the Taylor engine; additional numerical evidence.
- `plot_connection.py`: the PNG/SVG illustration. Plotted connecting
  lines are not proof objects.
- `results/connection_certificate.json`: exact dyadic inputs and ball
  enclosures, Taylor coefficients and majorants, matrices, signs,
  containment witnesses, settings, and input hashes.
- `results/exact_check.json`, `results/independent_check.json`, and
  `results/plot_metadata.json`: dependent outputs tied to the exact
  certificate and their generating script hashes.
- `diagnostics/`: an unsuccessful coarse interval trial, the subsequent
  successful refined trial, and their interpretation.

## Trust boundary

The analytic integral and tail arguments from R01, FLINT/Arb's enclosures,
and Python execution remain the trusted computational base. The rational
checker independently reconstructs the continuation arithmetic from the
saved central integral enclosures and derivative bounds; it does not
reintegrate them. Direct checks exercise the new expressions at selected
points and cannot replace the uniform remainder proof. The mpmath checks
are numerical, without certified truncation/rounding errors.

External expert review and literature priority assessment remain open.
There is no claim of global A4 exclusion, a Newman-constant bound,
physical dynamics, or automatic journal acceptance.
