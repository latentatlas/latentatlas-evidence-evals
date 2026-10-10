# R05 - Finite cusp width and nested three-root regions

This package proves strict motion of both folds, and therefore strict
nesting of the three-root strips, over the complete R04 window
nu in [-29,0], 0<ell<=10^-6. Coordinates are relative to each exact
cusp. See [the theorem and proof](PROOF.md),
[the Turkish research note](ARASTIRMA_NOTU.md), and the ongoing
[research notebook](../CALISMA_DEFTERI.md).

The common conservative derivative bounds are
0.0003*ell^(3/2) < -partial_nu W < 0.003*ell^(3/2).
As nu decreases, the upper fold moves upwards and the lower downwards.
This is a local parameter-space theorem, not a global root theorem or
a physical stability statement. The sextic endpoint comparison fixes
nu and permits lambda and mu perturbations, using the same control
directions as every other section.

## Reproduction

Use the pinned R01 environment: Python 3.12.14, python-flint 0.9.0,
mpmath 1.4.1, matplotlib 3.11.2. The present project provides it in
`.venv-math`. Preserve the four frozen sibling packages and their
manifests; 101 scientific files are checked before computations.

From /PROJECT, in a fresh copy:

~~~sh
.venv-math/bin/python research/cusp_width/certify_width.py
.venv-math/bin/python research/cusp_width/check_width.py
.venv-math/bin/python research/cusp_width/endpoint_folds.py
.venv-math/bin/python research/cusp_width/check_endpoints.py
.venv-math/bin/python research/cusp_width/test_width.py
.venv-math/bin/python research/cusp_width/check_independent.py
.venv-math/bin/python research/cusp_width/plot_paper.py
~~~

Dependencies in this order matter: the endpoint tests read the endpoint
certificate, and the plots check both rational reports. Do not use
Python -O/-OO. No network access is required for scientific computation.
The installed fonts used for these paper figures are Times New Roman
and STIX; font availability affects rendering, not the mathematical
certificate. The complete generating width run took about 24 seconds
on this machine. Timings can differ substantially on other machines.

Commands display their output; the supplied `.log` files record the
specific snapshot runs. Runtime fields change certificate hashes on a
rerun, so regenerate downstream reports and figures after changing an
input. `manifest.json` records the frozen snapshot, and the scientific
commands do not silently rewrite it. Work in a new copy for new runs.

For the recorded snapshot, `audit_snapshot.py` checks the manifest,
original files and report links. Its explicit `--freeze` option creates
a new snapshot manifest after all validations; it is for a deliberate
new snapshot, not a way to bypass an unexpected integrity failure.

The scientific rerun commands above do not fabricate a new visual-review
record. A fresh plot run changes PDF hashes (including creation metadata).
Before freezing a new copy, render and inspect its new PDFs and record
that review; the supplied figure_qa.json applies only to the exact PDFs
whose hashes it records. An existing manifest is never overwritten by
--freeze. The continuous research notebook is outside the frozen package
so that later entries can be appended without rewriting earlier results.

## Files and roles

- `fold_jets.py`: implicit power-series coefficient solution of F=Ft=0;
  works with Arb intervals or exact rational inputs.
- `transport_model.py`: extends the correlation-preserving R04 bounds
  through D26 and evaluates the fourth transport derivative at the cusp.
- `certify_width.py`: all 58 cells, fifth derivative, finite remainder,
  and positive normalized width-rate bounds.
- `check_width.py`: outward exact-rational arithmetic, expanded
  22-monomial fourth derivative and an independent fold-ODE recurrence.
- `endpoint_folds.py`: 128 interval contractions at the two exact cusps,
  on 32 nonzero ell sections, for quantitative paper figures.
- `check_endpoints.py`: separate rational verification of the saved
  endpoint contraction, radius, width and ratio witnesses.
- `test_width.py`: cusp cancellations, exact coefficient identities,
  ODE/implicit-jet agreement, outward arithmetic, domain rejection,
  36 correlated and 60 endpoint direct-integral comparisons.
- `check_independent.py`: 27 mpmath derivative comparisons and a separate
  expression for B4; numerical support only.
- `plot_paper.py`: two vector PDF/EPS/SVG figures and PNG previews, with
  input certificate and output hashes in `results/plot_metadata.json`.
- `paper/`: insertion guidance, English captions, theorem fragment and
  EPS/SVG/PNG figure versions. PDF masters are in `output/pdf/`.
- `results/`: complete interval witnesses, check reports and recorded logs.
- `diagnostics/`: retained development bounds and three-cell trials;
  these do not establish the whole-path theorem.

## Trust boundary and scope

The analytic arguments, frozen integral/tail estimates, Python and
FLINT/Arb execution remain trusted. Rational checkers do not import
FLINT; they assume the saved integral and correlated Taylor enclosures.
They independently rebuild the relevant downstream inequalities, not
the whole integration engine. Sampled direct-integral or mpmath tests
do not substitute for the uniform remainder proof.

External expert review and novelty assessment remain open. No interval
proof of the theorem outside the stated window is asserted. The plots
do not establish monotonicity by visual interpolation. The original
manuscript and frozen R01-R04 packages are preserved.
